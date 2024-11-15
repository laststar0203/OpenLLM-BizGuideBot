# app/chat_app.py

import logging

import streamlit as st
from processor.file_processor import FileProcessor
from processor.text_processor import TextProcessor
from processor.vector_store import VectorStoreManager
from processor.custom_runnable import PromptConsoleOutput

from langchain_core.messages import ChatMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langserve import RemoteRunnable

from langchain_core.prompts import MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, ChatPromptTemplate

from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain


# 로그 레벨 설정
# logging.basicConfig(level=logging.DEBUG)

RAG_SYSTEM_PROMPT_TEMPLATE = """당신은 라임에스엔씨 안내 AI 챗봇 라임봇입니다.
검색된 문맥을 사용하여 질문에 맞는 답변을 하세요.
답을 모른다면 모른다고 답변하세요.
Context: {context}
"""

UNRAG_SYSTEM_PROMPT_TEMPLATE = """
당신은 라임에스엔씨 안내 AI 챗봇 라임봇입니다.
질문에 맞는 답변을 하세요.
답을 모른다면 모른다고 답변하세요.
"""

HUMAN_PROMPT_TEMPLATE = """
Question: {input}
Answer:"""


def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    if session_ids not in st.session_state['history']:
        st.session_state['history'][session_ids] = ChatMessageHistory()
    return st.session_state['history'][session_ids]


class ChatApp:

    def __init__(self, config):


        self.file_processor = FileProcessor()
        self.text_processor = TextProcessor()
        self.vector_store_manager = VectorStoreManager()

        #self.llm_url = "https://incredibly-mature-vulture.ngrok-free.app/llm/"
        
        self.DOCUMENT_DIR = config['document_dir']
        
        self.llm = RemoteRunnable(config['llm_url'])
        self.setup_session_state()
        self.setup_page()

    def setup_session_state(self):

        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        if "history" not in st.session_state:
            st.session_state["history"] = {}
        
        if "retriever" not in st.session_state:
            st.session_state["retriever"] = None
        
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant",
                                             "content": "안녕하세요! 저는 라임에스엔씨의 AI 안내 챗봇 라임봇입니다. 무엇을 도와드릴까요?"}]                              
    
    def setup_page(self):

        st.set_page_config(
            page_title="라임에스엔씨 안내 챗봇",
            #page_icon=":books:"
        )

        st.title("라임에스엔씨 안내 챗봇")

    def print_history(self):
        for msg in st.session_state.messages:
            st.chat_message(msg.role).write(msg.content)

    def add_history(self, role, content):
        st.session_state.messages.append(ChatMessage(role=role, content=content))

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # streamlit은 상호작용이 발생할 때마다 전체 코드가 재실행됨.
    def run(self):

        # run() 재실행되므로 이전 메모리 저장 삭제 
        self.file_processor.clear()
        self.file_processor.add_directory(self.DOCUMENT_DIR)
        #self.file_processor.add_streamlit_upload_files(uploaded_files)
        files_text = self.file_processor.get_text()
        
        print("files_text : ", files_text)
        
        if len(files_text) > 0:
            text_chunks = self.text_processor.get_text_chunks(files_text)            
            vectorestore = self.vector_store_manager.get_vectorstore(text_chunks)            
            retriever = vectorestore.as_retriever(search_type='mmr', verbose=True)

            
            st.session_state['retriever'] = retriever
            st.session_state['ragActive'] = True
        else:
            st.session_state['ragActive'] = False
        

        self.print_history()

        if user_input := st.chat_input("메시지를 입력해 주세요."):
            self.add_history("user", user_input)
            st.chat_message("user").write(f"{user_input}")
            with st.chat_message("assistant"):
                
                chat_container = st.empty()

                if st.session_state['ragActive']:
                
                    # Contextulize question
                    
                    contextualize_q_prompt = ChatPromptTemplate.from_messages(
                        [
                            SystemMessagePromptTemplate.from_template("""채팅 기록과 최근 사용자 질문이 주어졌을 때, 채팅 기록의 맥락을 참조할 수 있는 최근 질문을, 채팅 기록 없이도 이해할 수 있는 독립적인 질문으로 재구성하세요. 질문에 답하지 말고, 필요하다면 질문을 재구성하고 그렇지 않으면 그대로 반환하세요."""),
                            MessagesPlaceholder(variable_name="history"),
                            HumanMessagePromptTemplate.from_template("{input}")
                        ]
                    )                   
                    
                    # LLM 도움을 받아 적합한 document를 찾음
                    history_aware_retriever = create_history_aware_retriever(
                        self.llm, retriever, contextualize_q_prompt
                    )
                    
                    qa_prompt = ChatPromptTemplate.from_messages(
                        [
                            SystemMessagePromptTemplate.from_template(RAG_SYSTEM_PROMPT_TEMPLATE),
                            MessagesPlaceholder(variable_name="history"),
                            HumanMessagePromptTemplate.from_template(HUMAN_PROMPT_TEMPLATE)
                        ]
                    )
                    
                    question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
                    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
                    
                    chain = RunnableWithMessageHistory(
                        rag_chain,
                        get_session_history,
                        input_messages_key="input",
                        history_messages_key="history",
                        output_messages_key="answer"
                    )
                                        
                else:
                    """
                    prompt = ChatPromptTemplate.from_template(UNRAG_PROMPT_TEMPLATE)
                    chain = prompt | PromptConsoleOutput() | self.llm | StrOutputParser()
                    """
                
                answer = chain.stream(
                    input={"input": user_input},
                    config={"configurable": {"session_id": "abc124"}}
                )
                
                self.display_answer(answer, chat_container)

    def display_answer(self, answer_stream, chat_container):
        chunks = []
        for chunk in answer_stream:
            if 'answer' in chunk:
                chunks.append(chunk['answer'])
                chat_container.markdown("".join(chunks))
                
        self.add_history("assistant", "".join(chunks))

# 파이프라인에서 문제가 발생시 체인 단계하나하나씩 확인 필요
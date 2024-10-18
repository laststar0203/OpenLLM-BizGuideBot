# app/chat_app.py

import streamlit as st
from processor.file_processor import FileProcessor
from processor.text_processor import TextProcessor
from processor.vector_store import VectorStoreManager

from langchain_core.messages import ChatMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langserve import RemoteRunnable


RAG_PROMPT_TEMPLATE = """당신은 라임에스엔씨 안내 챗봇 라임봇입니다.
검색된 문맥을 사용하여 질문에 맞는 답변을 하세요.
답을 모른다면 모른다고 답변하세요.
Question: {question}
Context: {context}
Answer:"""


class ChatApp:

    def __init__(self, config):


        self.file_processor = FileProcessor()
        self.text_processor = TextProcessor()
        self.vector_store_manager = VectorStoreManager()

        #self.llm_url = "https://incredibly-mature-vulture.ngrok-free.app/llm/"
        
        
        self.llm = RemoteRunnable(self.llm_url)
        self.setup_session_state()
        self.setup_page()

    def setup_session_state(self):

        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        if "store" not in st.session_state:
            st.session_state["store"] = dict()

        if "processComplete" not in st.session_state:
            st.session_state.setdefault("processComplete", None)
        
        if "retriever" not in st.session_state:
            st.session_state.setdefault("retriever", None)
        
        if "messages" not in st.session_state or not st.session_state["messages"]:
            st.session_state["messages"] = [{"role": "assistant",
                                             "content": "안녕하세요! 주어진 문서에 대해 궁금하신 것이 있으면 언제든 물어봐주세요!"}]

    def setup_page(self):

        st.set_page_config(
            page_title="라임에스엔씨 안내 챗봇",
            #page_icon=":books:"
        )

        st.title("라임에스엔씨 안내 챗봇")

    def print_history(self):
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

    def add_history(self, role, content):
        st.session_state["messages"].append({"role": role, "content": content})

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # streamlit은 상호작용이 발생할 때마다 전체 코드가 재실행됨.
    def run(self):
        
        with st.sidebar:
            uploaded_files = st.file_uploader("Upload your file", type=["pdf", "docx", "pptx"], accept_multiple_files=True)
            process = st.button("Process")

        if process:
            files_text = self.file_processor.get_text(uploaded_files)
            text_chunks = self.text_processor.get_text_chunks(files_text)
            vectorestore = self.vector_store_manager.get_vectorstore(text_chunks)
            retriever = vectorestore.as_retriever(search_type='mmr', verbose=True)
            st.session_state['retriever'] = retriever
            st.session_state['processComplete'] = True


        self.print_history()

        if user_input := st.chat_input("메시지를 입력해 주세요."):
            self.add_history("user", user_input)
            st.chat_message("user").write(f"{user_input}")
            with st.chat_message("assistant"):
                chat_container = st.empty()

                if st.session_state['processComplete']:
                    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
                    retriever = st.session_state['retriever']
                    rag_chain = ({
                        "context": retriever | self.format_docs,
                        "question": RunnablePassthrough(),
                    } | prompt | self.llm | StrOutputParser())

                    answer = rag_chain.stream(user_input)
                    self.display_answer(answer, chat_container)
                else:
                    prompt = ChatPromptTemplate.from_template(
                        "다음의 질문에 간결하게 답변해 주세요:\n{input}"
                    )
                    chain = prompt | self.llm | StrOutputParser()
                    answer = chain.stream(user_input)
                    self.display_answer(answer, chat_container)

    def display_answer(self, answer_stream, chat_container):
        chunks = []
        for chunk in answer_stream:
            chunks.append(chunk)
            chat_container.markdown("".join(chunks))
        self.add_history("assistant", "".join(chunks))

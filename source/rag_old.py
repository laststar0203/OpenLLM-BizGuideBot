import streamlit as st
import tiktoken
from loguru import logger

from langchain_core.messages import ChatMessage
from langchain_community.chat_models import ChatOllama

from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import UnstructuredPowerPointLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser

from langchain.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langserve import RemoteRunnable


def tiktoken_len(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)

def get_text(docs):
    
    doc_list = []
    
    for doc in docs:
        
        file_name = doc.name 

        with open(file_name, 'wb') as file:
            file.write(doc.getvalue())
            logger.info(f"Uploaded {file_name}")
        
        if ".pdf" in doc.name:
            loader = PyPDFLoader(file_name)
            documents = loader.load_and_split()
        elif '.docx' in doc.name:
            loader = Docx2txtLoader(file_name)
            documents = loader.load_and_split()
        elif 'pptx' in doc.name:
            loader = UnstructuredPowerPointLoader(file_name)
            documents = loader.load_and_split()
        
        doc_list.extend(documents)

    return doc_list

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=100,
        length_function=tiktoken_len
    )
    chunks = text_splitter.split_documents(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    vectordb = FAISS.from_documents(text_chunks, embeddings)
    
    return vectordb


def main():
    
    global retriever
    
    st.set_page_config(
        page_title="Stremlit_remote_Rag",
        page_icon=":books:"
    )

    st.title("_Private Data :red[Q/A Chat]_ :books:")
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        
    # 채팅 대화기록을 점검
    if "store" not in st.session_state:
        st.session_state["store"] = dict()
        
        
    def print_history():
        for msg in st.session_state.messages:
            st.chat_message(msg.role).write(msg.content)
    
    def add_history(role, content):
        st.session_state.messages.append(ChatMessage(role=role, content=content))
        
    if "processComplete" not in st.session_state:
        st.session_state.processComplete = None
        
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
        
    with st.sidebar:
        uploaded_files = st.file_uploader("Upload your file", type=["pdf", "docx"], accept_multiple_files=True)
        process = st.button("Process")
        
    if process:

        files_text = get_text(uploaded_files)
        text_chunks = get_text_chunks(files_text)
        vectorestore = get_vectorstore(text_chunks)
        retriever = vectorestore.as_retriever(search_type = 'mmr', vervose=True)
        st.session_state['retriever'] = retriever
        
        st.session_state.processComplete = True
        
    
    if 'message' not in st.session_state:
        st.session_state['messages'] = [{"role": "assistant",
                                         "content": "안녕하세요! 주어진 문서에 대해 궁금하신 것이 있으면 언제든 물어봐주세요!"}]
    
    def format_docs(docs):
        # 검색한 문서 결과를 하나의 문단으로 합쳐줍니다.
        return "\n\n".join(doc.page_content for doc in docs)
    
    RAG_PROMPT_TEMPLATE = """당신은 동서울대학교 컴퓨터소프트웨어과 안내 AI 입니다.
                             검색된 문맥을 사용하여 질문에 맞는 답변을 30단어 이내로 하세요.
                             답을 모른다면 모른다고 답변하세요.
                             Question: {question}
                             Context: {context}
                             Answer:"""
                             
    
    print_history()
    
    if user_input := st.chat_input("메시지를 입력해 주세요."):
        # 사용자가 입력한 내용
        add_history("user", user_input)
        st.chat_message("user").write(f"{user_input}")
        with st.chat_message("assistant"):
            #llm = RemoteRunnable("http://localhost:8000/llm")
            llm = RemoteRunnable("https://incredibly-mature-vulture.ngrok-free.app/llm/")
            chat_container = st.empty()
            
            
            if st.session_state.processComplete==True:
                prompt1 = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
                
                retriever = st.session_state['retriever']
                # 체인을 생성합니다.
                rag_chain = ({
                        "context": retriever | format_docs,
                        "question": RunnablePassthrough(),
                    }
                    | prompt1
                    | llm
                    | StrOutputParser()
                )
                
                answer = rag_chain.stream(user_input)
                chunks = []
                
                for chunk in answer:
                    chunks.append(chunk)
                    chat_container.markdown("".join(chunks))
                add_history("ai", "".join(chunks))
        
            else:
                prompt2 = ChatPromptTemplate.from_template(
                    "다음의 질문에 간결하게 답변해 주세요:\n{input}"
                )
                
                # 체인을 생성합니다.
                chain = prompt2 | llm | StrOutputParser()
                
                answer = chain.stream(user_input)
                chunks = []
                for chunk in answer:
                    chunks.append(chunk)
                    chat_container.markdown("".join(chunks))
                add_history("ai", "".join(chunks))



if __name__ == "__main__":
    main()
            
            
            
                
            
            
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

class VectorStoreManager:
    def get_vectorstore(self, text_chunks):
        embeddings = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-multitask",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        vectordb = FAISS.from_documents(text_chunks, embeddings)
        return vectordb

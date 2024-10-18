import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextProcessor:

    @staticmethod
    def tiktoken_len(text):
        tokenizer = tiktoken.get_encoding("cl100k_base")
        tokens = tokenizer.encode(text)
        return len(tokens)

    def get_text_chunks(self, text):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=900,
            chunk_overlap=100,
            length_function=self.tiktoken_len
        )
        chunks = text_splitter.split_documents(text)
        return chunks

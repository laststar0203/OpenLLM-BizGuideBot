import os
from loguru import logger
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader, TextLoader

class FileProcessor:
    
    def __init__(self) -> None:
        self._doc_list = []
    
    def add_file(self, doc_path: str):
        self._doc_list.append(doc_path)

    
    def add_directory(self, dir_path: str):
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            
            if os.path.isfile(file_path):
                self._doc_list.append(file_path)
            
    def clear(self):
        self._doc_list.clear()
    
    def get_text(self):
        
        result = []
        
        for doc_name in self._doc_list:
            file_name = doc_name

            if ".pdf" in doc_name:
                loader = PyPDFLoader(file_name)
            elif '.docx' in doc_name:
                loader = Docx2txtLoader(file_name)
            elif '.pptx' in doc_name:
                loader = UnstructuredPowerPointLoader(file_name)
            elif '.txt' in doc_name:
                loader = TextLoader(file_name)
            else:
                continue  # 지원하지 않는 파일 형식은 무시

            documents = loader.load_and_split()
            result.extend(documents)
        
        return result

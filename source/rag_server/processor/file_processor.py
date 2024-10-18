from loguru import logger

from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader

class FileProcessor:
    
    def get_text(self, docs):
        doc_list = []

        for doc in docs:
            file_name = doc.name

            with open(file_name, 'wb') as file:
                file.write(doc.getvalue())
                logger.info(f"Uploaded {file_name}")

            if ".pdf" in doc.name:
                loader = PyPDFLoader(file_name)
            elif '.docx' in doc.name:
                loader = Docx2txtLoader(file_name)
            elif '.pptx' in doc.name:
                loader = UnstructuredPowerPointLoader(file_name)
            else:
                continue  # 지원하지 않는 파일 형식은 무시

            documents = loader.load_and_split()
            doc_list.extend(documents)

        return doc_list

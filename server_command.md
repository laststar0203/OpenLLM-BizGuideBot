## 구동 절차 (windows)

1. Langchain Serve 구동
2. ngrok 구동

### Langchain Serve 구동 절차

1. cd를 통해 /rag-serice 디렉토리 내부로 이동
2. poetry run lanchain serve

### ngrok 구동 절차

1. cd를 통해 ngrok.exe 가 존재하는 디렉토리 내부로 이동
2. ngrok.exe http --domain https://incredibly-mature-vulture.ngrok-free.app 8000

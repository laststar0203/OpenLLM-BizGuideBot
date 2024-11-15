from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes

from langchain_community.chat_models import ChatOllama

import logging

logging.basicConfig(level=logging.INFO)

# Langchain이 지원하는 다른 채팅 모델을 사용합니다. 여기서는 Ollama를 사용합니다.
llm = ChatOllama(model="lime-bot-8b:latest", temperature=0) 

app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

@app.middleware("http")
async def log_prompt_request(request, call_next):
    body = await request.json()
    logging.info(f"Received prompt request: {body}")
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Edit this to add the chain you want to add
add_routes(app,
           llm,
           path="/llm")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=58888)


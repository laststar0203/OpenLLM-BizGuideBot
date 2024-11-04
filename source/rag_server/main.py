from app.chat_app import ChatApp

def main():
    app = ChatApp({
        "llm_url": "http://localhost:58888/llm/"
    })
    app.run()

if __name__ == "__main__":
    main()

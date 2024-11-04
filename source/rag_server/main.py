from app.chat_app import ChatApp

def main():
    app = ChatApp({
        "llm_url": "https://incredibly-mature-vulture.ngrok-free.app/llm/"
    })
    app.run()

if __name__ == "__main__":
    main()

import os
from app.chat_app import ChatApp

def main():

    current_dir = os.getcwd()
    document_dir = os.path.abspath(os.path.join(current_dir, "../../document"))
    
    app = ChatApp({
        "llm_url": "https://incredibly-mature-vulture.ngrok-free.app/llm/",
        "document_dir": document_dir,
        "show_prompt" : True,
    })
    app.run()

if __name__ == "__main__":
    main()

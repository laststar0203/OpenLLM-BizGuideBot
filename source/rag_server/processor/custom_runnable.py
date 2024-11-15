from langchain_core.runnables import Runnable

class PromptConsoleOutput(Runnable):
    def invoke(self, input, config, **kwargs):
        print("Prompt sent to llm:", input)
        return input
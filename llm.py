from openai import OpenAI
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_anthropic import ChatAnthropic

class OpenAIEmbedding:
    def __init__(self, model="text-embedding-3-small"):
        self.client = OpenAI()
        self.model = model
    
    def get_embedding(self, text):
        text = text.replace("\n", " ")
        return self.client.embeddings.create(input=[text], model=self.model).data[0].embedding

langchain_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Game of Thrones themed chat model
got_chat_model = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0.7,  # Increased for more creative responses
    max_tokens=2048,  # Increased for longer responses
    timeout=None,
    max_retries=2,
    api_key=os.getenv('CLAUDE_KEY')
)

# For backwards compatibility, also define chat_model
chat_model = got_chat_model

# System message for Game of Thrones theme
got_system_message = """
You are a wise maester from the Citadel, deeply knowledgeable about the history, 
lore, and current events of the Seven Kingdoms and beyond. Your task is to answer 
questions about the world of Game of Thrones, its characters, houses, events, and 
legends. Provide detailed and engaging responses, as if recounting tales from the 
great books of Westeros. If you're unsure about specific details, you may speculate 
based on your vast knowledge, but indicate when you're doing so.
"""

def get_got_response(user_query):
    messages = [
        ("system", got_system_message),
        ("human", user_query),
    ]
    ai_msg = got_chat_model.invoke(messages)
    return ai_msg.content

# OpenAI's GPT-4 model as a backup or for specific tasks
gpt4 = ChatOpenAI(temperature=0, model_name="gpt-4")

# Example usage
if __name__ == "__main__":
    print(get_got_response("Tell me about the Targaryen dynasty."))

# Export all necessary components
__all__ = ['OpenAIEmbedding', 'langchain_embeddings', 'got_chat_model', 'chat_model', 
           'got_system_message', 'get_got_response', 'gpt4']
from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
from vector_store import FlowerShopVectorStore
from tools import ChatHistory

load_dotenv()

class ProductChatbot:
    def __init__(self):
        self.chat_history = ChatHistory()
        self.vector_store = FlowerShopVectorStore()
        self.llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            api_key=os.environ['GROQ_API_KEY']
        )
        
        self.prompt = """#Purpose
You are a customer service chatbot for an online products store. You can help customers achieve the goals listed below.

#Goals
1.⁠ ⁠Answer questions users might have about our products and services using the knowledge base.
2.⁠ ⁠Recommend relevant products based on customer preferences and needs.
3.⁠ ⁠Provide helpful product information and comparisons.

#Tone
Helpful and friendly. Use Gen-Z emojis to keep things lighthearted.

#Available Tools
- query_knowledge_base: Look up information about products and services
- search_for_product_recommendations: Get product recommendations based on customer needs

#Current Conversation:
{chat_history}

#Human Message:
{input}

#Response:
"""

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        self.chat_prompt = ChatPromptTemplate.from_template(self.prompt)
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.chat_prompt,
            memory=self.memory,
            verbose=True
        )

        # Register tools with vector store integration
        self.tools = {
            "query_knowledge_base": self.vector_store.query_faqs,
            "search_for_product_recommendations": self.vector_store.query_inventories
        }
        
        self.llm = self.llm.bind_tools(list(self.tools.values()))

    def process_message(self, user_id: str, message: str) -> str:
        # Load user history
        history = self.chat_history.get_user_history(user_id)
        
        # Update memory with historical context
        if history:
            for msg in history:
                if msg['type'] == 'human':
                    self.memory.chat_memory.add_user_message(msg['content'])
                else:
                    self.memory.chat_memory.add_ai_message(msg['content'])

        # Process the message
        response = self.chain.invoke({
            "input": message
        })

        # Update history
        new_messages = [
            {"type": "human", "content": message},
            {"type": "ai", "content": response['text']}
        ]
        
        current_history = history + new_messages
        self.chat_history.update_user_history(user_id, current_history)

        return response['text']

    def clear_history(self, user_id: str):
        self.chat_history.clear_user_history(user_id)
        self.memory.clear()

# def main():
#     # Example usage
#     chatbot = ProductChatbot()
    
#     # Test interaction
#     user_id = "user123"
#     questions = [
#         "hi"
#     ]
    
#     for question in questions:
#         print(f"\nUser: {question}")
#         response = chatbot.process_message(user_id, question)
#         print(f"Bot: {response}")

# if __name__ == "__main__":
#     main()
from typing import TypedDict
from langgraph.graph import StateGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.prebuilt import ToolNode
from tools import query_knowledge_base, search_for_product_reccommendations
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

# MongoDB setup
mongo_client = MongoClient(os.environ['MONGODB_URI'])
db = mongo_client['chat_history_db']
chat_history_collection = db['chat_histories']


prompt = """#Purpose
You are a customer service chatbot for an online products store. You can help customers achieve the goals listed below.

#Goals
1.⁠ ⁠Answer questions users might have relating to the services offered.
2.⁠ ⁠Recommend products to users based on their preferences.
3.⁠ ⁠Help customers check on an existing order or place a new order.

#Tone
Helpful and friendly. Use Gen-Z emojis to keep things lighthearted.

#
"""

chat_template = ChatPromptTemplate.from_messages([
    ('system', prompt),
    ('placeholder', "{messages}")
])

tools = [query_knowledge_base, search_for_product_reccommendations]

llm = ChatGroq(model="llama-3.1-70b-versatile", api_key=os.environ['GROQ_API_KEY'])
llm_with_prompt = chat_template | llm.bind_tools(tools)

def filter_messages(messages: list, max_messages: int = 5):
    """Keep only the last 'max_messages' messages."""
    return messages[-max_messages:]

class CustomState(TypedDict):
    messages: list
    user_id: str

def call_agent(state: CustomState):
    user_id = state['user_id']
    
    # Retrieve chat history from MongoDB
    user_history = get_user_history(user_id)
    if user_history:
        all_messages = user_history + state['messages']
    else:
        all_messages = state['messages']
    
    # Filter messages to prevent context window from growing too large
    filtered_messages = filter_messages(all_messages)
    
    response = llm_with_prompt.invoke({'messages': filtered_messages})
    
    # Update chat history in MongoDB
    update_user_history(user_id, filtered_messages + [response])
    
    return {
        'messages': state['messages'] + [response],
        'user_id': user_id
    }

def is_there_tool_calls(state: CustomState):
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return 'tool_node'
    else:
        return '__end__'

graph = StateGraph(CustomState)
tool_node = ToolNode(tools)

graph.add_node('agent', call_agent)
graph.add_node('tool_node', tool_node)

graph.add_conditional_edges(
    "agent",
    is_there_tool_calls
)
graph.add_edge('tool_node', 'agent')

graph.set_entry_point('agent')

app = graph.compile()

# Database operations
def get_user_history(user_id: str):
    user_history = chat_history_collection.find_one({'user_id': user_id})
    if user_history:
        return [HumanMessage(content=msg['content']) if msg['type'] == 'human' else AIMessage(content=msg['content']) for msg in user_history['messages']]
    return None

def update_user_history(user_id: str, messages: list):
    chat_history_collection.update_one(
        {'user_id': user_id},
        {'$set': {'messages': [{'type': 'human' if isinstance(msg, HumanMessage) else 'ai', 'content': msg.content} for msg in messages]}},
        upsert=True
    )

def clear_user_history(user_id: str):
    chat_history_collection.delete_one({'user_id': user_id})

# Example usage (for testing)
def process_user_message(user_id: str, message: str):
    input_message = HumanMessage(content=message)
    state = CustomState(messages=[input_message], user_id=user_id)
    
    for event in app.stream(state, {}, stream_mode="values"):
        event['messages'][-1].pretty_print()
        print("********************")
        
def sender_user_massage(user_id: str, message: str):
    input_message = HumanMessage(content=message)
    state = CustomState(messages=[input_message], user_id=user_id)
    
    final_message_content = None  # To store the content of the last message
    for event in app.stream(state, {}, stream_mode="values"):
        final_message = event['messages'][-1]  # Store the last message in the sequence
        final_message_content = final_message.content  # Extract the content of the last message

    return final_message_content  # Return the final output message content

        

print(sender_user_massage("chat1","what are product is presnet"))

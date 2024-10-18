from chromadb import PersistentClient, EmbeddingFunction, Embeddings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import List
import json
from pymongo import MongoClient
import os

MODEL_NAME = 'all-MiniLM-L6-v2'
DB_PATH = './.chroma_db'

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['business_db']
faq_collection_mongo = db['faqs']
inventory_collection_mongo = db['products']

class Product:
    def __init__(self, name: str, id: str, description: str, type: str, price: float, quantity: int):
        self.name = name
        self.id = id
        self.description = description
        self.type = type
        self.price = price
        self.quantity = quantity

class QuestionAnswerPairs:
    def __init__(self, question: str, answer: str):
        self.question = question
        self.answer = answer

class CustomEmbeddingClass(EmbeddingFunction):
    def __init__(self, model_name):
        self.embedding_model = HuggingFaceEmbedding(model_name=MODEL_NAME)

    def __call__(self, input_texts: List[str]) -> Embeddings:
        return [self.embedding_model.get_text_embedding(text) for text in input_texts]

class FlowerShopVectorStore:
    def __init__(self):
        db = PersistentClient(path=DB_PATH)
        custom_embedding_function = CustomEmbeddingClass(MODEL_NAME)

        self.faq_collection = db.get_or_create_collection(name='FAQ', embedding_function=custom_embedding_function)
        self.inventory_collection = db.get_or_create_collection(name='inventory', embedding_function=custom_embedding_function)

        if self.faq_collection.count() == 0:
            self._load_faq_collection_from_mongo()

        if self.inventory_collection.count() == 0:
            self._load_inventory_collection_from_mongo()

    def _load_faq_collection_from_mongo(self):
        faqs = list(faq_collection_mongo.find({}, {"_id": 0}))

        self.faq_collection.add(
            documents=[faq['question'] for faq in faqs] + [faq['answer'] for faq in faqs],
            ids=[str(i) for i in range(0, 2 * len(faqs))],
            metadatas=faqs + faqs
        )

    def _load_inventory_collection_from_mongo(self):
        inventories = list(inventory_collection_mongo.find({}, {"_id": 0}))

        self.inventory_collection.add(
            documents=[inventory['description'] for inventory in inventories],
            ids=[str(i) for i in range(0, len(inventories))],
            metadatas=inventories
        )

    def query_faqs(self, query: str):
        return self.faq_collection.query(query_texts=[query], n_results=5)
    
    def query_inventories(self, query: str):
        return self.inventory_collection.query(query_texts=[query], n_results=5)

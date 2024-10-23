from typing import List, Dict
import json
import os

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

import json
import os
from typing import List, Dict
from datetime import datetime

class ChatHistory:
    def __init__(self, file_path='chat_history.json'):
        self.file_path = file_path
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Create the history file with empty dict if it doesn't exist"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f)
    
    def get_user_history(self, user_id: str) -> List[Dict]:
        """Get chat history for a specific user"""
        try:
            with open(self.file_path, 'r') as f:
                histories = json.load(f)
                if not isinstance(histories, dict):
                    histories = {}
                return histories.get(user_id, [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def append_message(self, user_id: str, message: str, is_user: bool):
        """Append a new message to the user's chat history"""
        try:
            # Read existing histories
            with open(self.file_path, 'r') as f:
                try:
                    histories = json.load(f)
                    if not isinstance(histories, dict):
                        histories = {}
                except json.JSONDecodeError:
                    histories = {}
            
            # Get existing messages for user or initialize empty list
            user_messages = histories.get(user_id, [])
            
            # Create new message entry
            new_message = {
                "timestamp": datetime.now().isoformat(),
                "sender": "user" if is_user else "assistant",
                "message": message
            }
            
            # Append new message to user's history
            user_messages.append(new_message)
            
            # Update histories with modified user messages
            histories[user_id] = user_messages
            
            # Write back to file
            with open(self.file_path, 'w') as f:
                json.dump(histories, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error appending message: {e}")
            return False
    
    def update_user_history(self, user_id: str, messages: List[Dict]):
        """Update entire chat history for a specific user"""
        try:
            # Read existing histories
            with open(self.file_path, 'r') as f:
                try:
                    histories = json.load(f)
                    if not isinstance(histories, dict):
                        histories = {}
                except json.JSONDecodeError:
                    histories = {}
            
            # Get existing messages
            existing_messages = histories.get(user_id, [])
            
            # Append new messages to existing ones
            existing_messages.extend(messages)
            
            # Update histories
            histories[user_id] = existing_messages
            
            # Write back to file
            with open(self.file_path, 'w') as f:
                json.dump(histories, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error updating history: {e}")
            return False
    
    def clear_user_history(self, user_id: str):
        """Clear chat history for a specific user"""
        try:
            with open(self.file_path, 'r') as f:
                try:
                    histories = json.load(f)
                    if not isinstance(histories, dict):
                        histories = {}
                except json.JSONDecodeError:
                    histories = {}
                    
            if user_id in histories:
                del histories[user_id]
                
            with open(self.file_path, 'w') as f:
                json.dump(histories, f, indent=2)
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False
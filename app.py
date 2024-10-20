from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from twilio.rest import Client
import json
from uuid import uuid4
import random
from datetime import datetime, timedelta
import os
import subprocess
from chatbot import sender_user_massage

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

# File paths
BUSINESS_INFO_FILE = 'business_info.json'
PRODUCTS_FILE = 'inventory.json'
FAQS_FILE = 'FAQ.json'
USERS_FILE = 'users.json'

def load_json(file_path, default=None):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default if default is not None else {}

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f)

# Load data
business_info = load_json(BUSINESS_INFO_FILE)
products = load_json(PRODUCTS_FILE, [])
faqs = load_json(FAQS_FILE, [])
users = load_json(USERS_FILE, {})

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    user_data = users.get(user_id)
    if user_data:
        return User(user_id, user_data['username'], user_data['password'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((User(id, data['username'], data['password']) for id, data in users.items() if data['username'] == username), None)
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if any(data['username'] == username for data in users.values()):
            flash('Username already exists.', 'error')
        else:
            user_id = str(uuid4())
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            users[user_id] = {'username': username, 'password': hashed_password}
            save_json(USERS_FILE, users)
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html', business_info=business_info, products=products, faqs=faqs)

@app.route('/get_business_info')
def get_business_info():
    return jsonify(business_info)

@app.route('/save_business_info', methods=['POST'])
def save_business_info():
    global business_info
    business_info = request.json
    save_json(BUSINESS_INFO_FILE, business_info)
    return jsonify({"status": "success"})

@app.route('/add_product', methods=['POST'])
def add_product():
    product = request.json
    product['id'] = str(uuid4())[:8].upper()
    products.append(product)
    save_json(PRODUCTS_FILE, products)
    return jsonify({"status": "success", "id": product['id']})

@app.route('/add_faq', methods=['POST'])
def add_faq():
    faq = request.json
    faqs.append(faq)
    save_json(FAQS_FILE, faqs)
    return jsonify({"status": "success"})

@app.route('/metrics_dashboard')
def metrics_dashboard():
    return render_template('metrics_dashboard.html')

@app.route('/get_products')
def get_products():
    return jsonify(products)

@app.route('/update_product', methods=['POST'])
def update_product():
    updated_product = request.json
    for product in products:
        if product['id'] == updated_product['id']:
            product.update(updated_product)
            break
    save_json(PRODUCTS_FILE, products)
    return jsonify({"status": "success"})

@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_id = request.json['id']
    global products
    products = [p for p in products if p['id'] != product_id]
    save_json(PRODUCTS_FILE, products)
    return jsonify({"status": "success"})

@app.route('/update_faq', methods=['POST'])
def update_faq():
    updated_faq = request.json
    for faq in faqs:
        if faq['question'] == updated_faq['oldQuestion']:
            faq['question'] = updated_faq['question']
            faq['answer'] = updated_faq['answer']
            break
    save_json(FAQS_FILE, faqs)
    return jsonify({"status": "success"})

@app.route('/delete_faq', methods=['POST'])
def delete_faq():
    question = request.json['question']
    global faqs
    faqs = [f for f in faqs if f['question'] != question]
    save_json(FAQS_FILE, faqs)
    return jsonify({"status": "success"})

@app.route('/get_faqs')
def get_faqs():
    return jsonify(faqs)

# @app.route('/get_metrics')
# def get_metrics():
#     total_conversations = random.randint(100, 1000)
#     avg_response_time = round(random.uniform(5, 60), 2)
#     lead_conversion_rate = round(random.uniform(0.1, 0.5), 2)
#     csat_score = round(random.uniform(3.5, 5), 1)

#     dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7, 0, -1)]
#     conversations_data = [random.randint(10, 100) for _ in range(7)]
#     resolved_queries_data = [int(x * random.uniform(0.7, 0.9)) for x in conversations_data]
#     csat_data = [round(random.uniform(3, 5), 1) for _ in range(7)]

#     sentiment_data = {
#         'Positive': random.randint(40, 60),
#         'Neutral': random.randint(20, 40),
#         'Negative': random.randint(10, 20)
#     }

#     return jsonify({
#         'total_conversations': total_conversations,
#         'avg_response_time': avg_response_time,
#         'lead_conversion_rate': lead_conversion_rate,
#         'csat_score': csat_score,
        # 'chart_data': {
        #     'dates': dates,
        #     'conversations': conversations_data,
        #     'resolved_queries': resolved_queries_data,
        #     'csat': csat_data
        # },
#         'sentiment_data': sentiment_data
#     })

# # Example chat history
# chat_history = [
#     {"user_id": 1, "timestamp": "2024-10-01T10:00:00", "sender": "user", "message": "Hello!"},
#     {"user_id": 1, "timestamp": "2024-10-01T10:01:00", "sender": "assistant", "message": "Hi! How can I help you today?"},
#     {"user_id": 1, "timestamp": "2024-10-01T10:02:00", "sender": "user", "message": "I want to buy a laptop."},
#     {"user_id": 1, "timestamp": "2024-10-01T10:03:00", "sender": "assistant", "message": "Sure! Which one are you interested in?"},
#     {"user_id": 1, "timestamp": "2024-10-01T10:04:00", "sender": "user", "message": "On a scale of 1 to 5, how satisfied are you with our service?"},
#     {"user_id": 1, "timestamp": "2024-10-01T10:05:00", "sender": "assistant", "message": "I would rate it a 5."},
# ]

from datetime import datetime

from datetime import datetime, timedelta
from collections import defaultdict

def analyze_sentiment(message):
    """Simple sentiment analysis based on keywords."""
    positive_keywords = ['good', 'great', 'happy', 'love', 'satisfied']
    negative_keywords = ['bad', 'poor', 'hate', 'unsatisfied', 'disappointed']

    message_lower = message.lower()

    if any(word in message_lower for word in positive_keywords):
        return 'Positive'
    elif any(word in message_lower for word in negative_keywords):
        return 'Negative'
    else:
        return 'Neutral'

def process_chat_history(chat_history):
    total_conversations = len(set(entry['user_id'] for entry in chat_history))
    response_times = []
    conversions = 0
    resolved_queries = 0
    total_score = 0
    feedback_count = 0
    conversations_data = defaultdict(int)
    csat_data = defaultdict(list)
    sentiment_data = {
        'Positive': 0,
        'Neutral': 0,
        'Negative': 0
    }

    last_assistant_timestamp = {}

    for entry in chat_history:
        entry_date = datetime.fromisoformat(entry['timestamp']).date()
        conversations_data[entry_date] += 1

        if entry['sender'] == 'user':
            if entry['user_id'] in last_assistant_timestamp:
                response_time = (datetime.fromisoformat(entry['timestamp']) - last_assistant_timestamp[entry['user_id']]).total_seconds()
                response_times.append(response_time)

            if 'buy' in entry['message'].lower() or 'purchase' in entry['message'].lower():
                conversions += 1

            sentiment = analyze_sentiment(entry['message'])
            sentiment_data[sentiment] += 1

        elif entry['sender'] == 'assistant':
            last_assistant_timestamp[entry['user_id']] = datetime.fromisoformat(entry['timestamp'])

            if 'resolved' in entry['message'].lower():
                resolved_queries += 1

            if 'satisfied' in entry['message'].lower():
                next_entry_index = chat_history.index(entry) + 1
                if next_entry_index < len(chat_history) and chat_history[next_entry_index]['sender'] == 'user':
                    try:
                        rating = int(chat_history[next_entry_index]['message'])
                        if 1 <= rating <= 5:
                            total_score += rating
                            feedback_count += 1
                            csat_data[entry_date].append(rating)
                    except ValueError:
                        continue

    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    lead_conversion_rate = (conversions / total_conversations) if total_conversations > 0 else 0
    csat_score = (total_score / (feedback_count * 5)) if feedback_count > 0 else 0

    # Get the last 7 days
    end_date = max(conversations_data.keys())
    start_date = end_date - timedelta(days=6)
    dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

    conversations_last_7_days = [conversations_data[start_date + timedelta(days=i)] for i in range(7)]
    resolved_queries_last_7_days = [int(conversations_data[start_date + timedelta(days=i)] * 0.8) for i in range(7)]  # Assuming 80% resolution rate
    csat_last_7_days = [sum(csat_data[start_date + timedelta(days=i)]) / len(csat_data[start_date + timedelta(days=i)]) if csat_data[start_date + timedelta(days=i)] else 0 for i in range(7)]

    return {
        'total_conversations': total_conversations,
        'avg_response_time': round(avg_response_time, 2),
        'lead_conversion_rate': round(lead_conversion_rate, 2),
        'csat_score': round(csat_score, 2),
        'chart_data': {
            'dates': dates,
            'conversations': conversations_last_7_days,
            'resolved_queries': resolved_queries_last_7_days,
            'csat': csat_last_7_days
        },
        'sentiment_data': sentiment_data
    }

@app.route('/get_metrics')
def get_metrics():
    metrics = process_chat_history(chat_history)
    return jsonify(metrics) 

# Example chat history
chat_history = [
    {"user_id": 1, "timestamp": "2024-10-01T10:00:00", "sender": "user", "message": "Hello!"},
    {"user_id": 1, "timestamp": "2024-10-01T10:01:00", "sender": "assistant", "message": "Hi! How can I help you today?"},
    {"user_id": 1, "timestamp": "2024-10-01T10:02:00", "sender": "user", "message": "I want to buy a laptop."},
    {"user_id": 1, "timestamp": "2024-10-01T10:03:00", "sender": "assistant", "message": "Sure! Which one are you interested in?"},
    {"user_id": 1, "timestamp": "2024-10-01T10:04:00", "sender": "user", "message": "On a scale of 1 to 5, how satisfied are you with our service?"},
    {"user_id": 1, "timestamp": "2024-10-01T10:05:00", "sender": "assistant", "message": "I would rate it a 5."},
    {"user_id": 2, "timestamp": "2024-10-01T10:00:00", "sender": "user", "message": "Hello!"},
    {"user_id": 2, "timestamp": "2024-10-01T10:01:00", "sender": "assistant", "message": "Hi! How can I help you today?"},
]

# Process the chat history and print metrics
metrics = process_chat_history(chat_history)
print(metrics)


    # return jsonify({
    #     'total_conversations': metricstotal_conversations,
    #     'avg_response_time': avg_response_time,
    #     'lead_conversion_rate': lead_conversion_rate,
    #     'csat_score': csat_score,
    #     'chart_data': {
    #         'dates': dates,
    #         'conversations': conversations_data,
    #         'resolved_queries': resolved_queries_data,
    #         'csat': csat_data
    #     },
    #     'sentiment_data': sentiment_data
    # })


# def get_total_conversations():

#     total_conv = chat_history_collection.find()
#     print(total_conv)
#     return total_conv

def get_avg_response_time():

    return

@app.route('/twilio/receiveMessage', methods=['POST'])
def receive_message():
    try:
        print("triggered whstapp")
        # Extract incoming parameters from Twilio
        print("triggered whstapp")
        message = request.form['Body']
        sender_id = request.form['From']

        print(message,sender_id)
        response_message=sender_user_massage(sender_id,message)


        # response_message=f"you said:{message}"
        # Echo the received message back to the sender
        twilio_client.messages.create(
            body=response_message,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=sender_id
        )
    except Exception as e:
        print(f"Error: {e}")
    return 'OK', 200

def run_streamlit():
    subprocess.Popen(["streamlit", "run", "streamlit_frontend.py"])

@app.route('/streamlit')
def streamlit():
    return '''
        <iframe src="http://localhost:8501" width="100%" height="1000px" frameborder="0"></iframe>
    '''

if __name__ == '__main__':
    #run_streamlit()
    app.run(debug=True,port=5000,use_reloader=False)

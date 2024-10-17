from twilio.rest import Client
import json
from flask import Flask, render_template, request, jsonify
from uuid import uuid4
import random
from datetime import datetime, timedelta
import os
import subprocess
from chatbot import app, sender_user_massage
app = Flask(__name__)
twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

# File paths
BUSINESS_INFO_FILE = 'business_info.json'
PRODUCTS_FILE = 'inventory.json'
FAQS_FILE = 'FAQ.json'

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

@app.route('/get_metrics')
def get_metrics():
    total_conversations = random.randint(100, 1000)
    avg_response_time = round(random.uniform(5, 60), 2)
    lead_conversion_rate = round(random.uniform(0.1, 0.5), 2)
    csat_score = round(random.uniform(3.5, 5), 1)
    
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7, 0, -1)]
    conversations_data = [random.randint(10, 100) for _ in range(7)]
    resolved_queries_data = [int(x * random.uniform(0.7, 0.9)) for x in conversations_data]
    csat_data = [round(random.uniform(3, 5), 1) for _ in range(7)]
    
    sentiment_data = {
        'Positive': random.randint(40, 60),
        'Neutral': random.randint(20, 40),
        'Negative': random.randint(10, 20)
    }
    
    return jsonify({
        'total_conversations': total_conversations,
        'avg_response_time': avg_response_time,
        'lead_conversion_rate': lead_conversion_rate,
        'csat_score': csat_score,
        'chart_data': {
            'dates': dates,
            'conversations': conversations_data,
            'resolved_queries': resolved_queries_data,
            'csat': csat_data
        },
        'sentiment_data': sentiment_data
    })

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
    # run_streamlit()
    app.run(debug=True,port=5000)
# from chatbot import app
# respose=app.invoke({
#             'messages': "hi"
#         })
# print(respose['messages'])

from flask import Flask, request
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Twilio client
twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),~~
    os.getenv('TWILIO_AUTH_TOKEN')
)

@app.route('/')
def home():
    return 'All is well...'

@app.route('/twilio/receiveMessage', methods=['POST'])
def receive_message():
    try:
        # Extract incoming parameters from Twilio
        message = request.form['Body']
        sender_id = request.form['From']

        # Echo the received message back to the sender
        response_message = f"You said: {message}"
        twilio_client.messages.create(
            body=response_message,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=sender_id
        )
    except Exception as e:
        print(f"Error: {e}")
    
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)

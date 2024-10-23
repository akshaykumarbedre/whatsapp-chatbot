# WhatsApp Business Chatbot 🤖

A powerful WhatsApp chatbot solution that helps business owners automate customer interactions by leveraging AI to handle product inquiries, FAQs, and customer support.

## Features

### 1. Automated Customer Service
- 24/7 automated responses to customer inquiries
- Natural language processing for understanding customer intent
- Personalized conversations based on customer history
- Multi-language support for global customers

### 2. Product Management
- Easy product catalog management through web interface
- Real-time inventory updates
- Product recommendation engine
- Detailed product information storage and retrieval
- Search functionality for products

### 3. FAQ Management
- Dynamic FAQ database management
- Automated responses to common questions
- Easy addition and updating of FAQs through web interface
- Smart matching of customer questions to FAQ database

### 4. Business Information Management
- Customizable business profile
- Operating hours
- Contact information
- Location details
- Service descriptions

### 5. User Authentication & Security
- Secure login system for business owners
- Password encryption using bcrypt
- Session management
- User registration system
- Protected admin routes

### 6. Analytics Dashboard
- Real-time conversation metrics
- Customer satisfaction scores
- Response time analytics
- Conversion tracking
- Sentiment analysis
- Visual data representation
  - Conversation trends
  - Query resolution rates
  - Customer satisfaction trends

### 7. Chat History & Management
- Complete conversation logging
- Searchable chat history
- User interaction tracking
- Message timestamp recording
- Conversation context maintenance

### 8. Vector Store Integration
- Efficient storage and retrieval of product information
- Semantic search capabilities
- FAQ matching using embeddings
- Improved response accuracy

### 9. Integration with External Services
- Twilio WhatsApp Business API integration
- Groq AI integration for natural language processing
- Streamlit integration for additional visualization

## Technical Stack

### Backend
- Flask (Python web framework)
- LangChain for LLM integration
- ChromaDB for vector storage
- SQLite for data persistence
- Bcrypt for password hashing

### Frontend
- HTML/CSS/JavaScript
- Streamlit for analytics visualization
- Bootstrap for responsive design

### AI/ML
- Groq LLM for natural language processing
- Custom embedding model (all-MiniLM-L6-v2)
- Sentiment analysis
- Product recommendation system

### External APIs
- Twilio WhatsApp Business API
- Groq API

## Setup & Installation

1. Clone the repository
```bash
git clone [repository-url]
```

2. Install required packages
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_whatsapp_number
GROQ_API_KEY=your_groq_api_key
```

4. Initialize the database
```bash
python init_db.py
```

5. Run the application
```bash
python app.py
```

## Usage

1. **Business Owner Portal**
   - Register/Login at `/login`
   - Add/update business information
   - Manage product catalog
   - Update FAQs
   - View analytics dashboard

2. **WhatsApp Integration**
   - Connect your business WhatsApp number through Twilio
   - Test the chatbot using the provided WhatsApp number
   - Monitor conversations in real-time

3. **Analytics**
   - Access the metrics dashboard at `/metrics_dashboard`
   - View conversation analytics
   - Track customer satisfaction
   - Monitor response times

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Demo Video

![Video showing Demo whatsapp chatbot](preview.gif)
[https://www.youtube.com/watch?v=OMXWGkL5X_o](url)

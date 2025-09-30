# Chat with Files

A FastAPI application that allows you to chat with your documents using LLMs and vector databases. Upload your files, and the system will process them to enable intelligent Q&A conversations.

## Features

- 📄 Support for PDF, TXT, and DOCX files
- 🤖 Powered by Google Gemini LLM
- 💾 Vector storage using Pinecone
- 💬 Real-time chat via WebSocket
- 📝 Conversation history management
- 🔍 Context-aware responses using RAG (Retrieval Augmented Generation)

## Prerequisites

- Python 3.11+
- Conda (Anaconda or Miniconda)
- API keys for:
  - Google Gemini API
  - Pinecone
  - HuggingFace

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd chat-with-files
```

### 2. Create Conda environment
```bash
conda create -n chatfiles python=3.10
conda activate chatfiles
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory with the following variables:

```env
GOOGLE_API_KEY = "your_google_api_key_here"
HF_TOKEN = "your_huggingface_token_here"
PINECONE_API_KEY = "your_pinecone_api_key_here"
APP_NAME = "Chat with Files"
INDEX_NAME = "chat-with-files"
VERSION = "1.0.0"
LOG_LEVEL = "INFO"
WS_HOST = "0.0.0.0"
WS_PORT = "8765"
```

## Usage

### 1. Start the server
```bash
python main.py
```
The server will start on `http://0.0.0.0:8765`

### 2. Access the API documentation
Visit `http://0.0.0.0:8765/docs` for interactive API documentation

### 3. Process a file
First, preprocess your document to create embeddings:

```bash
curl -X POST "http://0.0.0.0:8765/preprocess" \
     -H "Content-Type: application/json" \
     -d '{"file_url": "path/to/your/file.pdf"}'
```

### 4. Start chatting
Connect to the WebSocket endpoint to start a conversation:

```javascript
// Example WebSocket connection
const ws = new WebSocket('ws://localhost:8765/api/ws/chat');

ws.onopen = () => {
    // Send a message
    ws.send(JSON.stringify({
        message: "What is this document about?"
    }));
};

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log('Reply:', response.reply);
};
```

## API Endpoints

- `GET /` - Root endpoint, welcome message
- `GET /health` - Health check
- `POST /preprocess` - Process and embed a document
- `WS /api/ws/chat` - WebSocket endpoint for real-time chat

## Project Structure

```
chat-with-files/
├── api/               # API route handlers
├────  config/            # Configuration settings
├────  services/          # Business logic services
├────  models/            # Data models and schemas
├────   utils/             # Utility functions
├────   history/           # Conversation history storage
├────  logs/              # Application logs
├── .env               # Environment variables (create this)
├── requirements.txt   # Python dependencies
└──── main.py           # Application entry point
```

## Key Components

- **Preprocessing**: Loads documents, chunks them, and creates embeddings stored in Pinecone
- **Conversation**: Handles Q&A with context retrieval and conversation memory
- **Vector Store**: Uses Pinecone for efficient similarity search
- **LLM**: Google Gemini for generating responses
- **Embeddings**: HuggingFace BGE model for text embeddings

## Notes

- Maximum 10 conversation sessions are maintained (configurable)
- Supports similarity search with top 5 relevant chunks
- Conversation history is persisted to JSON files
- WebSocket connections maintain session state

## License

[Apache License Version 2.0]

## Support

For issues or questions, please open an issue in the repository.

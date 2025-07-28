# SCU Provost Academic Advisor Chatbot

An intelligent chatbot designed to assist students with questions related to the Santa Clara University (SCU) Provost's office, academic policies, and course information. This project leverages OpenAI's GPT-4o with a Retrieval-Augmented Generation (RAG) architecture to provide accurate answers based on a dedicated knowledge base.

## ✨ Key Features

* **AI-Powered Responses:** Utilizes the OpenAI GPT-4o model for natural and context-aware conversations.
* **Retrieval-Augmented Generation (RAG):** Answers are grounded in a specific set of university documents, ensuring accuracy and relevance through an OpenAI vector store.
* **Relevancy Guardrails:** A preliminary check classifies user queries to ensure the chatbot only answers questions related to its purpose.
* **Scalable API Backend:** Built with Flask, making it lightweight and ready for serverless deployment on platforms like Vercel.

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **AI & NLP:** OpenAI API (GPT-4o, GPT-3.5-Turbo for guardrails)
* **Data Store:** OpenAI Vector Store
* **Environment Management:** `python-dotenv`

## 🚀 Getting Started

### Prerequisites

* Python 3.8+
* An OpenAI API Key

### 1. Clone the Repository

```
git clone <your-repository-url>
cd <your-project-directory>
```

### 2. Install Dependencies

```
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory and add your credentials:

```
# Your OpenAI API Key
OPENAI_API_KEY="sk-..."

# The ID of your OpenAI Vector Store
VECTORDBID="vs_..."
```

### 4. Run the Application Locally

```
python api/index.py
```

The server will start, typically on `http://127.0.0.1:5000`.

## 📡 API Endpoints

### Main Endpoint

* **`POST /`**: Accepts a user query and returns a synthesized answer.
    * **Request Body:** `{ "query": "Your question here..." }`
    * **Success Response:** `{"response": "The assistant's answer..."}`

### Health Check

* **`GET /check`**: A simple endpoint to confirm the API is running.
    * **Success Response:** `{"status": "ok", "message": "API is running."}`

## ⚙️ How It Works

1.  A frontend client sends a `POST` request with a JSON payload to the Flask server.
2.  The server first sends the query to a **Guardrail Model** (GPT-3.5-Turbo) to classify its relevance.
3.  If the query is relevant, the server calls the main **Generation Model** (GPT-4o).
4.  The model uses the `file_search` tool to query the pre-configured OpenAI Vector Store for relevant context.
5.  The model generates a complete response, which the server returns to the client.

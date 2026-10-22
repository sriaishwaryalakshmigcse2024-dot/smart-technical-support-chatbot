Smart Technical Support Chatbot with RAG

1. Project Overview

The Smart Technical Support Chatbot is an AI-powered technical support
application that uses Retrieval-Augmented Generation (RAG) to answer
questions using a technical knowledge base.

It retrieves relevant document passages and uses the Ollama language
model to generate answers grounded in the retrieved information.

2. Features

- Technical document loading
- Text chunking and semantic retrieval
- RAG-based answer generation using Ollama
- Source filename and location references
- Fallback responses for questions without relevant information
- Streamlit chat interface
- Helpful and not-helpful feedback collection
- CSV-based feedback storage
- Feedback analytics dashboard
- Automated retrieval tests

3. Technologies Used

- Python
- Streamlit
- Ollama
- Llama 3.2
- Sentence Transformers
- FAISS
- Pandas
- Pytest

4. Project Structure

smart-technical-support-chatbot/
├── app.py
├── analytics.py
├── feedback.py
├── document_loader.py
├── chunking.py
├── retriever.py
├── rag_chatbot.py
├── requirements.txt
├── data/
│   ├── knowledge_base/
│   │   └── wifi_troubleshooting.txt
│   └── feedback.csv
└── tests/
    └── test_retriever.py

5. How It Works

1. Load technical documents from the knowledge base.
2. Extract and split document text into chunks.
3. Convert chunks into semantic embeddings.
4. Retrieve relevant chunks for a user question.
5. Send the question and retrieved context to Ollama.
6. Generate an answer and list source references.
7. Display the answer in the Streamlit interface.
8. Save user feedback and display analytics.

6. Setup Instructions

Create and activate a virtual environment on Windows:

    py -m venv .venv
    .\.venv\Scripts\Activate.ps1

Install project dependencies:

    python -m pip install -r requirements.txt

Ensure Ollama is installed and running, and download the model:

    ollama pull llama3.2

7. Run the Application

From the project root, with the virtual environment activated:

    python -m streamlit run app.py

Open the local URL shown in the terminal, usually:

    http://localhost:8501

8. Run Tests

    python -m pytest -v

9. Feedback Analytics

User ratings are saved to:

    data/feedback.csv

The dashboard displays feedback totals, helpful ratings, the helpful
rate, and recent feedback records.

10. Limitations

- Answers depend on the quality and coverage of the knowledge base.
- Retrieved sources should be checked to verify answer accuracy.
- The current application is a local prototype.
- Authentication, role-based access controls, and production deployment
  require additional implementation before organizational use.

11. Future Improvements

- Add PDF and DOCX knowledge-base documents.
- Add document versioning and re-indexing.
- Improve source citations and confidence handling.
- Add authentication and access controls.
- Expand automated tests.
- Add escalation workflows and usage analytics.

# local_retriever.py

import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

store_path = "E:/ResQ/FirstResQ/data/faiss_index"

# Load Gemini API Key
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_KEY
)

# Load FAISS vector index
faiss_path = store_path
vector_store = FAISS.load_local(
    folder_path=faiss_path,
    embeddings=embeddings,
    allow_dangerous_deserialization=True
)


def retrieve_local_relevant_sentences(query: str, k: int = 5):
    """Retrieve top-k relevant sentences from local FAISS index."""
    results = vector_store.similarity_search(query, k=k)

    return [
        {
            "text": doc.page_content,
            "source": "local"
        }
        for doc in results
    ]


# Test it
if __name__ == "__main__":
    user_query = "I'm shaky, sweaty, and my sugar is 55 — what should I do?"
    results = retrieve_local_relevant_sentences(user_query)
    print(results)
    # print("🔍 Top Local Matches:\n")
    # for i, r in enumerate(results, 1):
    #     print(f"{i}. ({r['id']}) {r['sentence']}\n")

import os
import pandas as pd
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document

# Load environment variables
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Path setup
store_path = "E:/ResQ/FirstResQ/data/faiss_index"
corpus_path = "E:/ResQ/FirstResQ/data/local_corpus.csv"
index_file = os.path.join(store_path, "index.faiss")

# Initialize Gemini Embeddings (LangChain wrapper)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", google_api_key=GEMINI_KEY
)

# Ensure storage path exists
os.makedirs(store_path, exist_ok=True)

# Load or create FAISS vector store
if os.path.exists(index_file):
    print("🔁 Loading existing FAISS index...")
    vector_store = FAISS.load_local(
        folder_path=store_path,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )
else:
    print("📄 Reading corpus and creating new FAISS index...")

    # Load the corpus CSV
    df = pd.read_csv(corpus_path, encoding="utf-8", encoding_errors="replace")


    # Convert each row into a LangChain Document
    documents = [
        Document(page_content=row["Sentence"], metadata={"id": row["s"]})
        for _, row in df.iterrows()
    ]

    # Embed and build the FAISS index
    vector_store = FAISS.from_documents(documents, embeddings)

    # Save the index to disk
    vector_store.save_local(store_path)
    print("✅ FAISS index saved to:", store_path)

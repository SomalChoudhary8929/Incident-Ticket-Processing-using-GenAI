import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


PDF_PATH = "vector_database/jci standards.pdf"
VECTORSTORE_PATH = "vector_database/vectorstore/jci_index"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def build_vectorstore():
    loader = PyMuPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"[✓] Loaded {len(documents)} pages from PDF")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"[✓] Split into {len(chunks)} chunks")

    embeddings = HuggingFaceEmbeddings(model_name=MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"[✓] FAISS vectorstore saved to {VECTORSTORE_PATH}")

if __name__ == "__main__":
    build_vectorstore()

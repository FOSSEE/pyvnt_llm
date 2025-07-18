import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# Path to your renamed .txt files
DATA_DIR = "C:\Users\Vedan\OneDrive\Desktop\data\data"

file_paths = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".txt")]

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

all_docs = []

for path in file_paths:
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()
        chunks = splitter.create_documents([text], metadatas=[{"source": os.path.basename(path)}])
        all_docs.extend(chunks)

print(all_docs)
# print(f"Total chunks created: {len(all_docs)}")

embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
vectorstore = FAISS.from_documents(all_docs, embedding)
vectorstore.save_local("openfoam_vectorstore")
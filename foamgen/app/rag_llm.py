from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from together import Together

def run_rag_pipeline(query: str, api_key: str, model: str):
    # Initialize Together client
    client = Together(api_key=api_key)

    # Load embedding and vector store
    # embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
    # vectorstore = FAISS.load_local(
    #     "openfoam_vectorstore",
    #     embedding,
    #     allow_dangerous_deserialization=True
    # )

    # Retrieve relevant docs
    # retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    # docs = retriever.get_relevant_documents(query)
    # context = "\n".join([doc.page_content for doc in docs])

    # If not using vectorstore, set context to empty and docs to empty list
    context = ""
    docs = []

    # Construct chat messages
    messages = [
        {
            "role": "system",
            "content": f"You are an expert OpenFOAM engineer. Use this context to answer the user's question: {context}"
        },
        {
            "role": "user",
            "content": query
        }
    ]

    # Call Together API using the new client method
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0
    )

    # Extract and return answer + docs
    return response.choices[0].message.content, docs
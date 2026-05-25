from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from config import CHROMA_DB_PATH, EMBEDDING_MODEL
from dotenv import load_dotenv
import os

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vectorstore = Chroma(
    persist_directory=CHROMA_DB_PATH,
    embedding_function=embeddings
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=200
)

prompt_template = """
    You are a news assistant. Answer the question using ONLY the news articles provided below.
    If the answer is not in the articles, say "I don't have recent news on that topic."
    Always mention which source the information came from. Have a slight sense of humour too

    News Context:
    {context}

    Question:
    {question}
    Answer:
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

qa_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

def ask(question : str) -> dict:
    docs = retriever.invoke(question)

    result = qa_chain.invoke(question)

    sources = list(set([
        doc.metadata.get("source", "Unknown")
        for doc in docs
    ]))


    return{
        "answer" : result,
        "sources" : sources
    }

if __name__ == "__main__":
    response = ask("What is up in Japan ?")
    print(f"\nAnswer : {response["answer"]}")
    print(f"\nSources : {response["sources"]}")
    

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from faqmanager import faq_manager_container

import time
import os

# Load Streamlist app
st.set_page_config(page_title="Customer Support Agent", page_icon="💬")
st.title("💬 SaaS Customer Support Service")

# Set and Load Gimini API Key
api_key = st.text_input("🔑 Enter your Google API Key", type="password")
load_apikey_button = st.button("🔄 Load API Key")

# Store init state
if "assistant_loaded" not in st.session_state:
    st.session_state.assistant_loaded = False

# Load assistant after button is clicked
if load_apikey_button:
    if not api_key:
        st.error("Please enter your API key before loading the assistant.")
        st.stop()
    os.environ["GOOGLE_API_KEY"] = api_key
    st.session_state.assistant_loaded = True

# Prevent loading before API key is set
if not st.session_state.assistant_loaded:
    st.info("Enter your API key and click 'Load Assistant' to begin.")
    st.stop()


# Load FAQ content
faq_path, faq_content = faq_manager_container()


# Define the system prompt for the FAQ agent
FAQ_SYSTEM_PROMPT = """
You are a friendly technical customer support assistant.

Answer the user’s question using the context below.
If the answer is unclear or missing, respond with:
"I'm going to escalate this to a human support agent."

{context}
"""


# Initialize Google Generative AI
google_genai = GoogleGenerativeAI(
    api_key=api_key,
    model="gemini-2.5-flash",
    temperature=0.1,
    max_output_tokens=512,
    top_p=0.95,
    top_k=40,
    system_prompt=FAQ_SYSTEM_PROMPT
    )


# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


# Split Document into Chunks and load into VectorStore
# chunk_size=500: Processes text in chunks of 500 tokens
# chunk_overlap : Ensures there is no overlap between consecutive chunks
@st.cache_resource
def load_faq_chain():
    # docs = load_faq_content(faq_path)
    # Wrap in Document list
    docs = TextLoader(faq_path).load()
    # docs = [Document(page_content=faq_path)]
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    vector_store = FAISS.from_documents(chunks, embeddings)
    retriever = vector_store.as_retriever()
    chain = RetrievalQA.from_chain_type(
        llm=google_genai,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        verbose=False
    )
    return chain

agent_response_chain = load_faq_chain()

# Streamlit App
st.subheader("Ask your question below:")
# st.caption("Hit Enter to submit your question")
user_question = st.chat_input("How do I reset my password?", key="user_question_input")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# If the user has entered a question, process it
if user_question:
    with st.spinner("Processing your question..."):
        # Get response from the agent
        output = agent_response_chain.invoke(user_question)
        response = output["result"]

    # Store chat history
    st.session_state.chat_history.append({"user": user_question, "assistant": response})


# Display Chat History
if st.session_state.chat_history:
    st.badge("📚 Chat History", color="blue")
    for chat in st.session_state.chat_history:
        st.write(f"**User:** {chat['user']}")
        st.write(f"**Assistant:** {chat['assistant']}")

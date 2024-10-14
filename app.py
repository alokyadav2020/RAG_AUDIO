import streamlit as st
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
# from langchain.vectorstores import Pinecone

from langchain_pinecone import PineconeVectorStore

import os
from dotenv import load_dotenv


load_dotenv()

OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
os.environ["OPENAI_API_KEY"] = OPEN_AI_KEY

llm = ChatOpenAI(model="gpt-4o",temperature=1)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
# pc = Pinecone(api_key=PINECONE_API_KEY)
# index = pc.Index("langchain-test-index")

def login_page():
    st.title("Login Page")
    # Create login input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Login button
    if st.button("Login"):
        # Check if the credentials match
        if PASSWORD == password and USER == username:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.rerun()
            # st.experimental_user()  # Refresh the page to move to the home page
        else:
            st.error("Invalid username or password")

def pinecone_retreiver():
    pc = Pinecone(api_key=PINECONE_API_KEY)

    index_name = "langchain-test-index"  # change if desired

    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=3072,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        # while not pc.describe_index(index_name).status["ready"]:
        #    pass

    index = pc.Index(index_name)    
    vector_store = PineconeVectorStore(index=index,embedding=OpenAIEmbeddings(model='text-embedding-3-large',api_key=OPEN_AI_KEY)) 
    retriever_pincone =vector_store.as_retriever(search_kwargs={'k': 25})

    return retriever_pincone       


def respone_script(user_query:str):
    system_prompt = (
                        """ 
                    You are a certified Hypnosis Expert with deep knowledge of hypnosis techniques and principles, extracted from multiple authoritative books on the subject. 
                    Your goal is to provide users with a personalized and soothing hypnosis 
                    session that helps them achieve their desired outcome, 
                    whether it’s relaxation, stress relief, sleep improvement, or 
                    positive behavioral change.

                    Your responses should be professional, calming, and precise, drawing on established hypnosis practices. 
                    You will guide the user into a state of deep relaxation, using clear, 
                    gentle language that fosters trust, calmness, and a sense of well-being. 
                    
                    You will get context from {context} to gerate hypnosis.
                    make sure hypnosis will be from this {context} only.
                    And hypnosis lenth should be more than 4000 words.
                
                    """
                    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    
    # retriever_pincone = PineconeVectorStore(index_name='langchain-test-index',embedding=embeddings,pinecone_api_key=PINECONE_API_KEY)
    retriever_pincone= pinecone_retreiver()
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever_pincone, question_answer_chain)

    results = rag_chain.invoke({"input": user_query})

    return results["answer"]


def home_page():

    with st.form("my_form"):
        text = st.text_area("Enter text:")
        submitted = st.form_submit_button("Submit")
        if submitted:
            if text:
                tst_res = respone_script(text)
                st.write(tst_res)
 






if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    login_page()  # Show the login page if not logged in
else:
    home_page()    


             

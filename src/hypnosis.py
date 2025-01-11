from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
# from langchain_community.chat_models import ChatOpenAI
# from langchain.vectorstores import Pinecone

from langchain_pinecone import PineconeVectorStore
from src.promt import system_prompt



class HypnosisGeneration:
    def __init__(self,OPEN_AI_KEY,PINECONE_API_KEY ):
        self._OPEN_AI_KEY = OPEN_AI_KEY
        self._PINECONE_API_KEY = PINECONE_API_KEY
        self._llm = ChatOpenAI(model="gpt-4o-mini",temperature=1, max_tokens=10000,api_key=OPEN_AI_KEY)
        self._embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self._system_prompt = system_prompt




    def pinecone_retreiver(self):
        pc = Pinecone(api_key=self._PINECONE_API_KEY)

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
        vector_store = PineconeVectorStore(index=index,embedding=OpenAIEmbeddings(model='text-embedding-3-large',api_key=self._OPEN_AI_KEY)) 
        retriever_pincone =vector_store.as_retriever(search_kwargs={'k': 20})

        return retriever_pincone     





    
    def respone_script(self,user_query:str):
        

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._system_prompt),
                ("human", "{input}"),
            ]
        )
        
        # retriever_pincone = PineconeVectorStore(index_name='langchain-test-index',embedding=embeddings,pinecone_api_key=PINECONE_API_KEY)
        retriever_pincone= self.pinecone_retreiver()
        question_answer_chain = create_stuff_documents_chain(self._llm, prompt)
        rag_chain = create_retrieval_chain(retriever_pincone, question_answer_chain)

        results = rag_chain.invoke({"input": user_query})

        return results["answer"]     

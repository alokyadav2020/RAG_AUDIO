from src.hypnosis import HypnosisGeneration
import os
from dotenv import load_dotenv




class GenerationPipeline:
    def __init__(self,OPEN_AI_KEY,PINECONE_API_KEY):
        self._OPEN_AI_KEY = OPEN_AI_KEY
        self._PINECONE_API_KEY = PINECONE_API_KEY

    def respone(self,query):
        obj = HypnosisGeneration(OPEN_AI_KEY=self._OPEN_AI_KEY,PINECONE_API_KEY=self._PINECONE_API_KEY)
        result = obj.respone_script(user_query=query)
        return result
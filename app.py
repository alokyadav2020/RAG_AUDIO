from flask import Flask, request, jsonify,send_file
from functools import wraps
import streamlit as st
from src.pipline import GenerationPipeline
import os
from dotenv import load_dotenv

load_dotenv()
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
os.environ["OPENAI_API_KEY"] = OPEN_AI_KEY




app = Flask(__name__)
# CORS(app)
app.config['API_KEY'] =   os.getenv('hypnosis-api-key')

@app.route("/")
def home():
    return 'BEV'



def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
            api_key = request.headers.get('hypnosis-api-key')  # Frontend sends the key in headers

            if api_key and api_key == app.config['API_KEY']:
                return f(*args, **kwargs)
            else:
                return jsonify({"message": "Invalid or missing API key"}), 401
        
    return decorated_function



@app.route("/hypnosisresponse", methods = ['POST'])
@require_api_key
def predict():
    try:
        if request.method == "POST":

            

            data =request.get_json()
            if not data:
               return jsonify({"error": "Empty or invalid JSON provided"}), 400



            all_params = data.get('params', {})
            param = all_params['query']

            obj = GenerationPipeline(OPEN_AI_KEY=OPEN_AI_KEY,PINECONE_API_KEY=PINECONE_API_KEY)
            result = obj.respone(query=param)
            
           
            
            return jsonify({"result":result})
    except Exception as e:
        # Handle the OperationalError and return a valid response
        app.logger.error(f"Error {e}")
       
        return jsonify({"error": str(e)})
    



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080,threaded =True,debug=True)    



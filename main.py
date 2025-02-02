from pymongo import MongoClient
import google.generativeai as genai
from dotenv import load_dotenv
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.embeddings import VertexAIEmbeddings
import os
load_dotenv()
GENAI_API_KEY = os.environ["GOOGLE_API_KEY"]
MONGO_URI = "mongodb+srv://stackgpt:admin@cluster0.9p9ck.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
import streamlit as st
st.title("StackGPT_POC")
query = st.text_area("Enter your querry")
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
INDEX_NAME = "vector_index"
def get_gemini_embedding(text):
  embedding = genai.embed_content(
        model="models/text-embedding-004",content=text)
  return  embedding['embedding']


try:
      # Establish connection
      client = MongoClient(MONGO_URI)

      # Access database
      db = client["StackGPT"]

      # Access or create collection
      collection = db.get_collection("POC")
except Exception as e:
    print(f"An error occurred: {e}")
    print(f"MONGO_URI: {MONGO_URI}")  # Print the URI for debugging

def find_relevant_documents(query_text, top_k):
        # Get embedding for the query
        indexes = collection.list_indexes()
        for index in indexes:
            print(index)
        query_embedding = get_gemini_embedding(query_text)

        # Perform vector search in MongoDB
        results = collection.aggregate([
            {
                "$vectorSearch": {
                    "index": INDEX_NAME,
                    "path": "embeddings",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": top_k
                }
            }
        ])

        return list(results)

def store_query_embedding_in_mongodb(query, embedding):
  """
  Stores the query and its embedding in the MongoDB database.

  Args:
    query: The query string.
    embedding: The embedding vector for the query.
  """
  try:
      document = {
          "embeddings": str(embedding),
          "query": query,
          "hit": 0
      }
      result = collection.insert_one(document)
  except Exception as e :
      print("insertion failed", e)

  finally:
      # Close the connection
      client.close()
      print(f"Document inserted with ID: {result.inserted_id}")

def store_query_embedding_and_result_in_mongodb(query, embedding):
    response = model.generate_content(query)
    result = response.text
    try:
        document = {
            "embeddings": embedding,
            "query": query,
            "result":result,
            "hit": 0
        }
        result = collection.insert_one(document)
    except Exception as e:
        print("insertion failed", e)

    finally:
        # Close the connection
        client.close()
        print(f"Document inserted with ID: {result.inserted_id}")
    return response.text
def update_hit_count(collection, query):
  """
  Updates the hit count of a document in the collection.

  Args:
    collection: The MongoDB collection object.
    query: The user's question.
  """
  try:
    result = collection.update_one({"query": query}, {"$inc": {"hit": 1}})
    if result.modified_count > 0:
      print(f"Hit count updated for query: {query}")
    else:
      print(f"No document found for query: {query}")
  except Exception as e:
    print(f"Error updating hit count: {e}")


# Update hit count (example)
#update_hit_count("POC", query)
if query:
 embedding = get_gemini_embedding(query)
 # response = store_query_embedding_and_result_in_mongodb(query, embedding)
 # st.write(embedding)
 relevent_docs = find_relevant_documents(query,1)
 st.write(relevent_docs)
 # st.write(response)
 print("succesfully executed")
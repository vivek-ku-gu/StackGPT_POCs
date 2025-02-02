from pymongo import MongoClient
import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()
GENAI_API_KEY = os.environ["GOOGLE_API_KEY"]
MONGO_URI = "mongodb+srv://stackgpt:admin@cluster0.9p9ck.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
import streamlit as st
st.title("StackGPT_POC")
query = st.text_area("Enter your querry")

def get_gemini_embedding(text):
  """
  Generates an embedding for the given text using the Gemini model.

  Args:
    text: The text to generate an embedding for.

  Returns:
    A list of floats representing the embedding vector.
  """
  genai.configure(api_key=GENAI_API_KEY)
  model = genai.GenerativeModel("text-embedding-004")
  embedding = genai.embed_content(
        model="models/text-embedding-004",content=text)
  return str( embedding['embedding'])

def store_query_embedding_in_mongodb(query, embedding):
  """
  Stores the query and its embedding in the MongoDB database.

  Args:
    query: The query string.
    embedding: The embedding vector for the query.
  """
  try:
      # Establish connection
      client = MongoClient(MONGO_URI)

      # Access database
      db = client["StackGPT"]

      # Access or create collection
      collection = db.get_collection("POC")

      # Insert document
      document = {
          "embeddings": embedding,
          "query": query,
          "hit": 0
      }
      result = collection.insert_one(document)
  except Exception as e:
      print(f"An error occurred: {e}")
      print(f"MONGO_URI: {MONGO_URI}")  # Print the URI for debugging

  finally:
      # Close the connection
      client.close()
      print(f"Document inserted with ID: {result.inserted_id}")

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
 store_query_embedding_in_mongodb(query, embedding)
 st.write(embedding)
 print("succesfully executed")
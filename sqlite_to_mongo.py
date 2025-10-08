import sqlite3
from pymongo import MongoClient

# --- SQLite connection ---
sqlite_conn = sqlite3.connect("db_backup.sqlite3")
cursor = sqlite_conn.cursor()

# --- MongoDB connection ---
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["qa_collection"]

# --- Fetch QA data from SQLite ---
cursor.execute("SELECT question, answer FROM chatbot_qa")
rows = cursor.fetchall()

# --- Insert into MongoDB ---
for row in rows:
    doc = {
        "question": row[0],
        "answer": row[1]
    }
    collection.insert_one(doc)

print(f"✅ Successfully imported {len(rows)} QA entries to MongoDB")

# --- Close connections ---
cursor.close()
sqlite_conn.close()
client.close()

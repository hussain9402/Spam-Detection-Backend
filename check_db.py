import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Check all messages in database
messages = db.collection("messages").stream()

count = 0
for msg in messages:
    count += 1
    data = msg.to_dict()
    print(f"\nMessage {count}:")
    print(f"ID: {msg.id}")
    print(f"Text: {data.get('text')}")
    print(f"Processed: {data.get('processed')}")

if count == 0:
    print("✅ Database is empty - no messages yet")
else:
    print(f"\nTotal messages: {count}")
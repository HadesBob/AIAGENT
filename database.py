from google.cloud import firestore

# Initialize Firestore client globally
# It connects to your specific project and database
db = firestore.Client(project="aibot-505317", database="appdb")
import os
import time

import resend
from pymongo import MongoClient

resend.api_key = os.environ["RESEND_API_KEY"]
AUDIENCE_ID = os.environ["RESEND_AUDIENCE_ID"]

client = MongoClient(os.environ["MONGO_URI"])
signups = client["pythonsv"]["signups"].find({}, {"name": 1, "email": 1, "_id": 0})

for doc in signups:
    name_parts = doc["name"].split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    try:
        result = resend.Contacts.create(
            {
                "audience_id": AUDIENCE_ID,
                "email": doc["email"],
                "first_name": first_name,
                "last_name": last_name,
            }
        )
        print(f"OK: {doc['name']} <{doc['email']}> -> {result['id']}")
    except Exception as e:
        print(f"FAILED: {doc['name']} <{doc['email']}> -> {e}")

    time.sleep(1)

import os

from pymongo import MongoClient

client = MongoClient(os.environ["MONGO_URI"])

result = client["pythonsv"]["signups"].find({"role": "organize"})
for doc in result:
    print(doc)

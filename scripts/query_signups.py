import os

from pymongo import MongoClient


def main() -> None:
    client = MongoClient(os.environ["MONGO_URI"])

    result = client["pythonsv"]["signups"].find({"role": "organize"})
    for doc in result:
        print(doc)


if __name__ == "__main__":
    main()

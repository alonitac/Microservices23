import os
from flask import Flask, request
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongo:27017")
db = client['myDatabase']
collection = db['requests']


@app.route('/')
def home():
    try:
        request_data = {
            'endpoint': request.endpoint,
            'method': request.method,
            'url': request.url,
            'headers': dict(request.headers),
            'data': request.get_data(as_text=True)
        }

        request_id = collection.insert_one(request_data).inserted_id

    except:
        return "Mongo is not available"
    return f"Request information stored successfully: {request_id}\n"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9090)


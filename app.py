from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from pymongo import MongoClient
import os
from bson import ObjectId

app = Flask(__name__)
CORS(app)  


MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://admin:admin@cluster1-ghosh.5kvtg.mongodb.net/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'internships_db')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'internships')


client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def serialize_document(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

def serialize_documents(docs):
    return [serialize_document(doc) for doc in docs]

@app.route('/api/search', methods=['GET'])
def search_internships():
    try:
        
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                "error": "Search query 'q' is required",
                "status": "error"
            }), 400
        
        
        total_docs = collection.count_documents({})
        
        if total_docs == 0:
            return jsonify({
                "results": [],
                "total": 0,
                "query": query,
                "status": "success"
            })
        
        
        sample_doc = collection.find_one({})
        search_fields = []
        
        
        possible_fields = ['title', 'description', 'company', 'category', 'location', 'name', 'role', 'organization']
        
        if sample_doc:
            for field in possible_fields:
                if field in sample_doc:
                    search_fields.append({field: {"$regex": query, "$options": "i"}})
        
        if not search_fields:
            
            if sample_doc:
                for key, value in sample_doc.items():
                    if isinstance(value, str) and key != '_id':
                        search_fields.append({key: {"$regex": query, "$options": "i"}})
        
        if search_fields:
            results = list(collection.find({"$or": search_fields}).limit(6))
        else:
            
            all_docs = list(collection.find({}).limit(20))  
            results = []
            for doc in all_docs:
                if len(results) >= 6:
                    break
                for value in doc.values():
                    if isinstance(value, str) and query.lower() in value.lower():
                        results.append(doc)
                        break
        
        return jsonify({
            "results": serialize_documents(results),
            "total": len(results),
            "query": query,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Search failed: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/filter', methods=['GET'])
def filter_internships():
    
    filters = {}
    
    try:
        
        filters = {}
        if request.args.get('category'):
            filters['category'] = {"$regex": request.args.get('category').strip(), "$options": "i"}
        if request.args.get('location'):
            filters['location'] = {"$regex": request.args.get('location').strip(), "$options": "i"}
        if request.args.get('duration'):
            filters['duration'] = {"$regex": request.args.get('duration').strip(), "$options": "i"}
        if request.args.get('company'):
            filters['company'] = {"$regex": request.args.get('company').strip(), "$options": "i"}
        
        
        if filters:
            results = list(collection.find(filters).limit(6))
        else:
            results = list(collection.find({}).limit(6))
        
        return jsonify({
            "results": serialize_documents(results),
            "total": len(results),
            "filters": {k: v["$regex"] if isinstance(v, dict) and "$regex" in v else v for k, v in filters.items()},
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Filter failed: {str(e)}",
            "status": "error"
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Internship Search API...")
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 API will be available at: http://localhost:{port}")
    
    app.run(debug=False, host='0.0.0.0', port=port) 
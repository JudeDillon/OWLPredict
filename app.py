from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.OWLPredict      #select the database
matchMapStats = db.match_map_stats   #select the collection

@app.route("/", methods=["GET"])
def index():
    return make_response("<h1>Hello world</h1>", 200)

@app.route("/api/mapStats", methods=["GET"])
def show_all_map_stats():
    page_num, page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))
    page_start = (page_size * (page_num -1))

    data_to_return = []
    for map in matchMapStats.find().skip(page_start).limit(page_size):
        map['_id'] = str(map['_id'])
        data_to_return.append(map)

    return make_response( jsonify(data_to_return), 200 )

@app.route("/api/mapStats/matches", methods=["GET"])
def show_all_matches():
    page_num, page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))
    page_start = (page_size * (page_num -1))

    data_to_return = []
    
    for matchID in matchMapStats.find().distinct('match_id'):
        map = matchMapStats.find_one({'match_id':matchID})
        map['_id'] = str(map['_id'])
        data_to_return.append(map)
    
    return make_response( jsonify(data_to_return), 200 )

if __name__ == "__main__":
    app.run(debug=True)

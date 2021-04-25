from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from flask_cors import CORS
from bson import ObjectId
from math import sqrt
import re

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.OWLPredict      #select the database
matchMapStats = db.match_map_stats   #select the collection
games = db.games

def get_round_start_key(match):
    return match.get('round_start_time')

def get_winrate_difference_key(game):
    return game.get('winrate_difference')

@app.route("/", methods=["GET"])
def index():
    return make_response( jsonify("Hello world"), 200)

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
    data_to_return = []
    
    for matchID in matchMapStats.find().distinct('match_id'):
        map = matchMapStats.find_one({'match_id':matchID})
        map['_id'] = str(map['_id'])
        data_to_return.append(map)

    data_to_return.sort(key=get_round_start_key)
    return make_response( jsonify(data_to_return), 200 )

@app.route("/api/mapStats/matches/<string:team>", methods=["GET"])
def show_all_matches_for_team(team):
    data_to_return = []
    
    for matchID in matchMapStats.find({"$or":[{"team_one_name":team}, {"team_two_name":team}]}).sort("match_id",1).distinct('match_id'):
        map = matchMapStats.find_one({'match_id':matchID})
        map['_id'] = str(map['_id'])
        data_to_return.append(map)
    
    data_to_return.sort(key=get_round_start_key)
    return make_response( jsonify(data_to_return), 200 )

@app.route("/api/mapStats/matches/wins/<string:team>", methods=["GET"])
def show_all_wins_for_team(team):
    data_to_return = []
    
    for matchID in matchMapStats.find({"match_winner":team}).sort("match_id",1).distinct('match_id'):
        map = matchMapStats.find_one({'match_id':matchID})
        map['_id'] = str(map['_id'])
        data_to_return.append(map)
    
    data_to_return.sort(key=get_round_start_key)
    return make_response( jsonify(data_to_return), 200 )

def winrate_dif_calc(team_one, team_two, season):
    team_one_winrate = calc_winrate(team_one, None, season)
    team_two_winrate = calc_winrate(team_two, None, season)

    winrate_dif = team_one_winrate - team_two_winrate

    return winrate_dif

def calc_winrate(team, round_start_time, season):
    total_games = 0
    total_wins = 0

    if(round_start_time is None):
        total_wins = games.find({"$and":[{"match_winner":team}, {"stage": season}]}).count()
        total_games = games.find({"$and":[{"$or":[{"team_one_name":team}, {"team_two_name":team}]}, {"stage": season}]}).count()
    else:
        for game in games.find({"$and":[
            {"$and":[
                {"$or":[
                    {"team_one_name":team}, 
                    {"team_two_name":team}]}, 
                {"stage": season}]},
            {"round_start_time":{"$lt":round_start_time}}]}):
                total_games+=1
                if((game["team_one_win_status"]==1 and game["team_one_name"]==team) or (game["team_one_win_status"]==0 and game["team_two_name"]==team)):
                    total_wins+=1

    try:
        winrate = total_wins / total_games
        #if total games is 0 then winrate is 0
    except ZeroDivisionError:
        winrate = 0
        
    return winrate

def get_distance(winrate_difference, game):
    distance = (winrate_difference - game["winrate_difference"])**2
    return sqrt(distance)

def get_neighbours(winrate_difference, num_neighbours, season):
    distances = list()
    for game in games.find({"stage": season}):
        distance = get_distance(winrate_difference, game)
        distances.append((game, distance))
    
    distances.sort(key=lambda tup: tup[1])

    neighbours = list()
    for i in range(num_neighbours):
        neighbours.append(distances[i][0])
    return neighbours

def update_predictors(season):
    winrate_list = []

    for game in games.find({"stage": season}):
        team_one = game["team_one_name"]
        team_two = game["team_two_name"]
        round_start_time = game["round_start_time"]

        team_one_winrate = calc_winrate(team_one, round_start_time, season)
        team_two_winrate = calc_winrate(team_two, round_start_time, season)

        winrate_diff = team_one_winrate - team_two_winrate
        winrate_list.append(winrate_diff)

    i = 0
    for game in games.find({"stage": season}):
        games.update_one(
            {"match_id":game["match_id"]},
            {"$set" :{"winrate_difference": winrate_list[i]}}
        )
        i = i + 1

@app.route("/predict/<string:team_one>/<string:team_two>", methods=["GET"])
def make_prediction(team_one, team_two):
    num_neighbours = 33
    season = ""

    if request.args.get('neighbours'):
        num_neighbours = int(request.args.get('neighbours'))
    if request.args.get('season'):
        season = str(request.args.get('season'))
    seasonrgx = re.compile('.*' + season + '.*')

    update_predictors(seasonrgx)

    winrate_difference = winrate_dif_calc(team_one, team_two, seasonrgx)
    
    neighbours = get_neighbours(winrate_difference, num_neighbours, seasonrgx)

    neighbors_votes = [neighbour["team_one_win_status"] for neighbour in neighbours]

    team_one_win_votes = 0
    team_two_win_votes = 0
    for vote in neighbors_votes:
        if(vote == 1):
            team_one_win_votes+=1
        else:
            team_two_win_votes+=1

    if(team_one_win_votes > team_two_win_votes):
        prediction = "I predict that " + team_one + " wins by " + str(team_one_win_votes/len(neighbors_votes)*100) + "% of the neighbours votes"
    else:
        prediction = "I predict that " + team_two + " wins by " + str(team_two_win_votes/len(neighbors_votes)*100) + "% of the neighbours votes"

    return make_response(jsonify(prediction), 200)

if __name__ == "__main__":
    app.run(debug=True)

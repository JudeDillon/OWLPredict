from flask import Flask, request, jsonify, make_response
from dotenv import load_dotenv
import os
import pymongo
from pymongo import MongoClient
from flask_cors import CORS
from bson import ObjectId
from math import sqrt
import re

load_dotenv()
app = Flask(__name__)
CORS(app)

#DATABASE_URL=f'mongodb+srv://dbUserPog:{os.environ.get("password")}@owlpredict-ire.mo4hm.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
#client = pymongo.MongoClient(DATABASE_URL, ssl=True,ssl_cert_reqs='CERT_NONE')
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.OWLPredict      #select the database
games = db.games

@app.route("/", methods=["GET"])
def index():
    return make_response( jsonify("Hello world"), 200)

@app.route("/sample_launch/", methods=["GET"])
def sample():
	results=games.find_one()
	return make_response( jsonify(str(results)), 200)

def winrate_dif_calc(team_one, team_two, season):
    team_one_winrate = calc_winrate(team_one, None, season)
    team_two_winrate = calc_winrate(team_two, None, season)

    winrate_dif = team_one_winrate - team_two_winrate

    return winrate_dif

def calc_winrate(team, round_start_time, season):
    chosen_season_games = 0
    chosen_season_wins = 0

    if(round_start_time is None):
        if(season == 0):
            chosen_season_wins = games.find({"match_winner":team}).count()
            chosen_season_games = games.find({"$or":[{"team_one_name":team}, {"team_two_name":team}]}).count()
        else:
            chosen_season_wins = games.find({"$and":
                [{"match_winner":team}, 
                {"$and":
                    [{"match_id":{"$lt":(season + 1) * 10000}}, 
                    {"match_id":{"$gt":season * 10000}}]
                }]
            }).count()
            chosen_season_games = games.find({"$and":[{"$or":[{"team_one_name":team}, {"team_two_name":team}]}, {"$and":[{"match_id":{"$lt":(season + 1) * 10000}}, {"match_id":{"$gt":season * 10000}}]}]}).count()

    else:
        if(season == 0):
            for game in games.find({"$and":[
                    {"$or":[
                        {"team_one_name":team}, 
                        {"team_two_name":team}]},
                {"round_start_time":{"$lt":round_start_time}}]}):
                    chosen_season_games+=1
                    if((game["team_one_win_status"]==1 and game["team_one_name"]==team) or (game["team_one_win_status"]==0 and game["team_two_name"]==team)):
                        chosen_season_wins+=1
        else:
            for game in games.find({"$and":[
                {"$and":[
                    {"$or":[
                        {"team_one_name":team}, 
                        {"team_two_name":team}]}, 
                    {"$and":[{"match_id":{"$lt":(season + 1) * 10000}}, {"match_id":{"$gt":season * 10000}}]}]},
                {"round_start_time":{"$lt":round_start_time}}]}):
                    chosen_season_games+=1
                    if((game["team_one_win_status"]==1 and game["team_one_name"]==team) or (game["team_one_win_status"]==0 and game["team_two_name"]==team)):
                        chosen_season_wins+=1

    try:
        winrate = chosen_season_wins / chosen_season_games
        #if total games is 0 then winrate is 0
    except ZeroDivisionError:
        winrate = 0
        
    return winrate

def get_distance(inputvalue, game):
    distance = 0.0
    row2 = [(game["winrate_difference"]), (game["average_final_score_difference"])]
    for i in range(len(inputvalue)-1):
        distance += (inputvalue[i] - row2[i])**2
    return sqrt(distance)

def get_neighbours(inputvalue, num_neighbours, season):
    distances = list()
    if(season == 0):
        chosen_season = games.find()
    else:
        chosen_season = games.find({"$and":[{"match_id":{"$lt":(season + 1) * 10000}}, {"match_id":{"$gt":season * 10000}}]})

    for game in chosen_season:
        distance = get_distance(inputvalue, game)
        distances.append((game, distance))
    
    distances.sort(key=lambda tup: tup[1])

    neighbours = list()
    for i in range(num_neighbours):
        neighbours.append(distances[i][0])
    return neighbours

def calc_average_final_score(team, round_start_time, season):
    total_games = 0
    total_score = 0

    if(round_start_time is None):
        if(season == 0):
            for game in games.find({"$or":[{"team_one_name":team}, {"team_two_name":team}]}):
                if((game["team_one_win_status"]==1 and game["team_one_name"]==team) or (game["team_one_win_status"]==0 and game["team_two_name"]==team)):
                    total_score = total_score + game["winning_team_final_map_score"]
                else:
                    total_score = total_score + game["losing_team_final_map_score"]
            total_games = games.find({"$or":[{"team_one_name":team}, {"team_two_name":team}]}).count()
        else:
            for game in games.find({"$and":[{"$or":[{"team_one_name":team}, {"team_two_name":team}]}, {"$and":[{"match_id":{"$lt":(season + 1) * 10000}}, {"match_id":{"$gt":season * 10000}}]}]}):
                if((game["team_one_win_status"]==1 and game["team_one_name"]==team) or (game["team_one_win_status"]==0 and game["team_two_name"]==team)):
                    total_score = total_score + game["winning_team_final_map_score"]
                else:
                    total_score = total_score + game["losing_team_final_map_score"]
            total_games = games.find({"$and":[{"$or":[{"team_one_name":team}, {"team_two_name":team}]}, {"$and":[{"match_id":{"$lt":(season + 1) * 10000}}, {"match_id":{"$gt":season * 10000}}]}]}).count()
    else:
        if(season == 0):
            for game in games.find({"$and":[
                        {"$or":[
                            {"team_one_name":team}, 
                            {"team_two_name":team}]},
                    {"round_start_time":{"$lt":round_start_time}}]}):
                        total_games += 1
                        if((game["team_one_win_status"]==1 and game["team_one_name"]==team) or (game["team_one_win_status"]==0 and game["team_two_name"]==team)):
                            total_score = total_score + game["winning_team_final_map_score"]
                        else:
                            total_score = total_score + game["losing_team_final_map_score"]
        else:
            for game in games.find({"$and":[
                    {"$and":[
                        {"$or":[
                            {"team_one_name":team}, 
                            {"team_two_name":team}]}, 
                        {"$and":[{"match_id":{"$lt":(season + 1) * 10000}}, {"match_id":{"$gt":season * 10000}}]}]},
                    {"round_start_time":{"$lt":round_start_time}}]}):
                        total_games += 1
                        if((game["team_one_win_status"]==1 and game["team_one_name"]==team) or (game["team_one_win_status"]==0 and game["team_two_name"]==team)):
                            total_score = total_score + game["winning_team_final_map_score"]
                        else:
                            total_score = total_score + game["losing_team_final_map_score"]

    try:
        average_score = total_score / total_games
        #if total games is 0 then winrate is 0
    except ZeroDivisionError:
        average_score = 0
        
    return average_score


def update_predictors(season):
    winrate_list = []
    total_average_damage_done_list = []
    average_final_score_difference_list = []

    if(season == 0):
        chosen_season = games.find()
    else:
        chosen_season = games.find({"$and":[{"match_id":{"$lt":(season + 1) * 10000}}, {"match_id":{"$gt":season * 10000}}]})

    for game in chosen_season:
        team_one = game["team_one_name"]
        team_two = game["team_two_name"]
        round_start_time = game["round_start_time"]
        match_id = game["match_id"]

        team_one_winrate = calc_winrate(team_one, round_start_time, season)
        team_two_winrate = calc_winrate(team_two, round_start_time, season)
        winrate_diff = team_one_winrate - team_two_winrate
        winrate_list.append(winrate_diff)

        team_one_average_final_score = calc_average_final_score(team_one, round_start_time, season)
        team_two_average_final_score = calc_average_final_score(team_two, round_start_time, season)
        average_final_score_diff = team_one_average_final_score - team_two_average_final_score
        average_final_score_difference_list.append(average_final_score_diff)

    winrateminmax = list()
    for i in range(len(winrate_list)):
        value_min = min(winrate_list)
        value_max = max(winrate_list)
        winrateminmax.append([value_min, value_max])

    for i in range(len(winrate_list)):
        winrate_list[i] = (winrate_list[i] - winrateminmax[i][0]) / (winrateminmax[i][1] - winrateminmax[i][0])

    scoreminmax = list()
    for i in range(len(average_final_score_difference_list)):
        value_min = min(average_final_score_difference_list)
        value_max = max(average_final_score_difference_list)
        scoreminmax.append([value_min, value_max])

    for i in range(len(average_final_score_difference_list)):
        average_final_score_difference_list[i] = (average_final_score_difference_list[i] - scoreminmax[i][0]) / (scoreminmax[i][1] - scoreminmax[i][0])
    
    if(season == 0):
        chosen_season = games.find()
    else:
        chosen_season = games.find({"$and":[{"match_id":{"$lt":(season + 1) * 10000}}, {"match_id":{"$gt":season * 10000}}]})

    i = 0
    for game in chosen_season:
        games.update_one(
            {"match_id":game["match_id"]},
            {"$set" :{
                "winrate_difference": winrate_list[i],
                "average_final_score_difference": average_final_score_difference_list[i]
            }}
        )
        i = i + 1

@app.route("/predict/<string:team_one>/<string:team_two>/<string:accuracy>", methods=["GET"])
def make_prediction(team_one, team_two, accuracy):
    num_neighbours = 33
    season = 0

    if request.args.get('neighbours'):
        num_neighbours = int(request.args.get('neighbours'))
    if request.args.get('season'):
        if(request.args.get('season') == ""):
            season = 0
        else:
            season = int(request.args.get('season'))

    update_predictors(season)

    winrate_difference = winrate_dif_calc(team_one, team_two, season)

    team_one_average_final_score = calc_average_final_score(team_one, None, season)
    team_two_average_final_score = calc_average_final_score(team_two, None, season)
    average_final_score_difference = team_one_average_final_score - team_two_average_final_score

    inputvalue = [winrate_difference, average_final_score_difference]
    
    neighbours = get_neighbours(inputvalue, num_neighbours, season)

    neighbors_votes = [neighbour["team_one_win_status"] for neighbour in neighbours]

    team_one_win_votes = 0
    team_two_win_votes = 0
    for vote in neighbors_votes:
        if(vote == 1):
            team_one_win_votes+=1
        else:
            team_two_win_votes+=1

    if(team_one_win_votes > team_two_win_votes):
        if(accuracy == "accuracy"):
            prediction = [team_one, str(team_one_win_votes/len(neighbors_votes)*100)]
        else:
            prediction = "I predict that " + team_one + " is " + str(team_one_win_votes/len(neighbors_votes)*100) + "% likely to win"
    else:
        if(accuracy == "accuracy"):
            prediction = [team_two, str(team_two_win_votes/len(neighbors_votes)*100)]
        else:
            prediction = "I predict that " + team_two + " is " + str(team_two_win_votes/len(neighbors_votes)*100) + "% likely to win"

    if(accuracy == "accuracy"):
        return prediction
    else:
        return make_response(jsonify(prediction), 200)
    
@app.route("/predict/accuracy", methods=["GET"])
def get_accuracy():
    test_amount = games.find().count()//5
    correct_amount = 0
    test_games = list()

    for game in games.find().sort("$natural", -1).limit(test_amount):
        test_games.append((game["team_one_name"], game["team_two_name"], game["match_winner"]))
    
    for game in test_games:
        prediction = make_prediction(game[0], game[1], "accuracy")
        if(prediction[0] == game[2]):
            correct_amount += 1
            print((correct_amount/test_amount)*100)

    accuracy = (correct_amount/test_amount)*100
    print("accuracyfinal")
    return make_response( jsonify(accuracy), 200)

if __name__ == "__main__":
    app.run()

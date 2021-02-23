from math import sqrt
from csv import reader

def load_csv(filename):
    dataset = list()
    with open(filename, 'r') as file:
        csv_reader = reader(file)
        for row in csv_reader:
            if not row:
                continue
            dataset.append(row)
    return dataset

def filter_dataset(dataset, stage):
    #only include data where the stage column is equal to the chosen stage
    dataset = [row for row in dataset if row[2] == stage]
    return dataset

def get_unique_match_ids(dataset):
    unique_matches_dataset = []
    match_id_set = set()

    for item in dataset:
        #if match id has already been seen in the dataset then don't add it to this set
        if item[3] not in match_id_set:
            match_id_set.add(item[3])
            unique_matches_dataset.append(item)
        else:
            pass
    return unique_matches_dataset

def add_team_one_win_status(proto_dataset):
    team_one_win = proto_dataset
    for row in range(0,len(team_one_win)):
        #if the winning team is the team one then status is 1
        #otherwise it is 0
        if(team_one_win[row][5] == team_one_win[row][15]):
            team_one_win[row].append(1)
        else:
            team_one_win[row].append(0)
    return team_one_win

def get_winrate(team_name, dataset, match_id):
    total_games = 0
    total_wins = 0

    for match in range(0,len(dataset)):
        old_match_id = dataset[match][3]
        #if the match has already occured before the selected match or selected match has no match id
        #then include it as a match to check
        if((match_id is None) or (int(match_id) > int(old_match_id))):
            old_game_team_one = dataset[match][15]
            old_game_team_two = dataset[match][16]
            old_game_winner = dataset[match][5]

            #if the team was in the game increase the total games it has played counter
            if((team_name == old_game_team_one) or (team_name == old_game_team_two)):
                total_games+=1
                #if the team won increase the total wins it has counter
                if(team_name == old_game_winner):
                    total_wins+=1
    
    #calculate the winrate
    try:
            winrate = total_wins / total_games
    #if total games is 0 then winrate is 0
    except ZeroDivisionError:
            winrate = 0 
    return winrate

def get_winrate_differences(dataset):
    winrate_list = []
    winrate_difference_column_dataset = dataset

    #for each row in dataset calculate difference between team one and team two winrate then add it to the dataset
    for row in range(0,len(dataset)):
        team_one = dataset[row][15]
        team_two = dataset[row][16]
        match_id = dataset[row][3]

        #get team one and team two  winrate
        team_one_winrate = get_winrate(team_one, dataset, match_id)
        team_two_winrate = get_winrate(team_two, dataset, match_id)
        
        #calculate winrate difference and add to list of winrate differences
        winrate_diff = team_one_winrate - team_two_winrate
        winrate_list.append(winrate_diff)

    #add winrate differences list to the dataset
    i = 0
    for row in winrate_difference_column_dataset:
        row.append(winrate_list[i])
        i = i + 1
    return winrate_difference_column_dataset

def get_distance(prediction_row, data_row):
    #get distance squared and then square root of it to avoid negative numbers
    distance = (prediction_row - data_row[26])**2
    return sqrt(distance)

def get_neighbors(data, prediction_data, num_neighbors):
    distances = list()
    #get dataset with distances
    for data_row in data:
        dist = get_distance(prediction_data, data_row)
        distances.append((data_row, dist))
    #sort distances from smallest to biggest
    distances.sort(key=lambda tup: tup[1])
    #create list of the shortest neighbours for selected amount of nearest neighbours
    neighbors = list()
    for i in range(num_neighbors):
        neighbors.append(distances[i][0])
    return neighbors

def predict_classification(data, prediction_data, num_neighbors):
    #get list of the shortest neighbours for selected amount of nearest neighbours
    neighbors = get_neighbors(data, prediction_data, num_neighbors)
    #create list of the team one win statuses for each of the nearest neighbours
    neighbors_votes = [row[25] for row in neighbors]

    #count nearest neighbours votes
    team_one_win_votes = 0
    team_two_win_votes = 0
    for vote in neighbors_votes:
        if(vote == 1):
            team_one_win_votes+=1
        else:
            team_two_win_votes+=1
    #choose prediction based on which team had more votes and output percentage of votes that predict this outcome
    if(team_one_win_votes > team_two_win_votes):
        prediction = "I predict that team one wins by " + str(team_one_win_votes/len(neighbors_votes)*100) + "% of the neighbours votes"
    else:
        prediction = "I predict that team two wins by " + str(team_two_win_votes/len(neighbors_votes)*100) + "% of the neighbours votes"
    return prediction

def switch(id):
    #created a dictionary to use as a switch case
    switcher = {
        1:"Atlanta Reign",
        2:"Boston Uprising",
        3:"Chengdu Hunters",
        4:"Dallas Fuel",
        5:"Florida Mayhem",
        6:"Guangzhou Charge",
        7:"Hangzhou Spark",
        8:"Houston Outlaws",
        9:"London Spitfire",
        10:"Los Angeles Gladiators",
        11:"Los Angeles Valiant",
        12:"New York Excelsior",
        13:"Paris Eternal",
        14:"Philadelphia Fusion",
        15:"San Francisco Shock",
        16:"Seoul Dynasty",
        17:"Shanghai Dragons",
        18:"Toronto Defiant",
        19:"Vancouver Titans",
        20:"Washington Justice"
    }
    return switcher.get(id, "Invalid team")

#this is the filename of the OWL match map stats csv file
filename = 'match_map_stats.csv'
#makes a 2D list from the map stats file
dataset = load_csv(filename)
#removes data from matches outside of the 2020 Season of OWL
dataset = filter_dataset(dataset, "OWL 2020 Regular Season")
#removes rows with duplicate matchIDs
dataset = get_unique_match_ids(dataset)
#adds a column that states if team 1 won or lost the game
dataset = add_team_one_win_status(dataset)
#adds a column that includes the difference between the winrate of team 1 and team 2
dataset_with_winrate_difference = get_winrate_differences(dataset)

#The value of K to be used in K Nearest Neighbours 
num_neighbors = 9

print("Atlanta Reign          [1]\nBoston Uprising        [2]\nChengdu Hunters        [3]\nDallas Fuel            [4]\nFlorida Mayhem         [5]\nGuangzhou Charge       [6]\
        \nHangzhou Spark         [7]\nHouston Outlaws        [8]\nLondon Spitfire        [9]\nLos Angeles Gladiators [10]\nLos Angeles Valiant    [11]\
        \nNew York Excelsior     [12]\nParis Eternal          [13]\nPhiladelphia Fusion    [14]\nSan Francisco Shock    [15]\nSeoul Dynasty          [16]\
        \nShanghai Dragons       [17]\nToronto Defiant        [18]\nVancouver Titans       [19]\nWashington Justice     [20]")

#get user team choices
team_one_input = input("Choose team 1: ")
team_two_input = input("Choose team 2: ")
team_one_name = switch(int(team_one_input))
team_two_name = switch(int(team_two_input))

#get winrates for each team and calculate difference
team_one_win_rate = get_winrate(team_one_name, dataset_with_winrate_difference, None)
team_two_win_rate = get_winrate(team_two_name, dataset_with_winrate_difference, None)
winrate_difference = team_one_win_rate - team_two_win_rate
print("Winrate Difference = " + str(winrate_difference))

#predict which team will win and display it to the user
prediction = predict_classification(dataset_with_winrate_difference, winrate_difference, num_neighbors)
print(prediction)

#uncomment these lines to create csv of the final state of the dataset
# with open('finalDataset.csv', 'w') as f:
#     for item in dataset_with_winrate_difference:
#         f.write(','.join(map(str, item)))
#         f.write("\n")

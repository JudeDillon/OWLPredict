from math import sqrt
from csv import reader

# Load CSV file
def load_csv(filename):
	dataset = list()
	with open(filename, 'r') as file:
		csv_reader = reader(file)
		for row in csv_reader:
			if not row:
				continue
			dataset.append(row)
	return dataset

def filter_dataset(dataset):
    proto_dataset = [x for x in dataset if x[2] == "OWL 2020 Regular Season"]
    return proto_dataset

def unique_match_ids(proto_dataset):
    unique_matches_dataset = []
    match_id_set = set()

    for item in proto_dataset:
        if item[3] not in match_id_set:
            match_id_set.add(item[3])
            unique_matches_dataset.append(item)
        else:
            pass
    return unique_matches_dataset

def does_team_one_win_column(proto_dataset):
    team_one_win = proto_dataset
    for row in range(0,len(team_one_win)):
        if(team_one_win[row][5] == team_one_win[row][15]):
            team_one_win[row].append(1)
        else:
            team_one_win[row].append(0)
    return team_one_win

def get_win_rate(team_name, dataset, match_id):
    total_games = 0
    total_wins = 0

    for match in range(0,len(dataset)):
        old_match_id = dataset[match][3]
        if(((match_id is None) or (int(match_id) > int(old_match_id)))and int(old_match_id) > 30991):
            old_game_team_one = dataset[match][15]
            old_game_team_two = dataset[match][16]
            old_game_winner = dataset[match][5]

            if((team_name == old_game_team_one) or (team_name == old_game_team_two)):
                total_games+=1
                if(team_name == old_game_winner):
                    total_wins+=1
    
    try:
            winrate = total_wins / total_games
    except ZeroDivisionError:
            winrate = 0 
    return winrate

def get_winrate_difference(does_team_one_win, dataset):
    winrate_list = []
    winrate_difference_column_dataset = does_team_one_win
    for row in range(0,len(does_team_one_win)):
        team_one = does_team_one_win[row][15]
        team_two = does_team_one_win[row][16]
        match_id = does_team_one_win[row][3]

        team_one_winrate = get_win_rate(team_one, dataset, match_id)
        team_two_winrate = get_win_rate(team_two, dataset, match_id)
        
        winrate_diff = team_one_winrate - team_two_winrate
        winrate_list.append(winrate_diff)

    i = 0
    for row in winrate_difference_column_dataset:
        row.append(winrate_list[i])
        i = i + 1
    return winrate_difference_column_dataset

def get_distance(prediction_row, data_row):
    distance = 0.0
    distance = (prediction_row - data_row[26])**2
    # for i in range(len(data_row)-1):
    #     distance += (data_row[i] - prediction_row[i])**2
    return sqrt(distance)

def get_neighbors(data, prediction_data, num_neighbors):
	distances = list()
	for data_row in data:
		dist = get_distance(prediction_data, data_row)
		distances.append((data_row, dist))
	distances.sort(key=lambda tup: tup[1])
	neighbors = list()
	for i in range(num_neighbors):
		neighbors.append(distances[i][0])
	return neighbors

def predict_classification(data, prediction_data, num_neighbors):
    neighbors = get_neighbors(data, prediction_data, num_neighbors)
    output_values = [row[25] for row in neighbors]
    print(output_values)

    team_one_win_votes = 0
    team_two_win_votes = 0
    for value in output_values:
        if(value == 1):
            team_one_win_votes+=1
        else:
            team_two_win_votes+=1

    if(team_one_win_votes > team_two_win_votes):
        prediction = "I predict that team one wins            " + str(team_one_win_votes/len(output_values)*100) + "% of votes"
    else:
        prediction = "I predict that team two wins            " + str(team_two_win_votes/len(output_values)*100) + "% of votes"
    return prediction

def switch(id):
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

filename = 'match_map_stats.csv'
original_dataset = load_csv(filename)
dataset = original_dataset
dataset = filter_dataset(dataset)
unique_match_ids_dataset = unique_match_ids(dataset)

does_team_one_win = does_team_one_win_column(unique_match_ids_dataset)
dataset_with_winrate_difference = get_winrate_difference(does_team_one_win, dataset)

num_neighbors = 9

print("Atlanta Reign          [1]\nBoston Uprising        [2]\nChengdu Hunters        [3]\nDallas Fuel            [4]\nFlorida Mayhem         [5]\nGuangzhou Charge       [6]\
        \nHangzhou Spark         [7]\nHouston Outlaws        [8]\nLondon Spitfire        [9]\nLos Angeles Gladiators [10]\nLos Angeles Valiant    [11]\
        \nNew York Excelsior     [12]\nParis Eternal          [13]\nPhiladelphia Fusion    [14]\nSan Francisco Shock    [15]\nSeoul Dynasty          [16]\
        \nShanghai Dragons       [17]\nToronto Defiant        [18]\nVancouver Titans       [19]\nWashington Justice     [20]")

team_one_input = input("Choose team 1:")
team_two_input = input("Choose team 2:")
team_one_name = switch(int(team_one_input))
team_two_name = switch(int(team_two_input))

team_one_win_rate = get_win_rate(team_one_name, dataset_with_winrate_difference, None)
team_two_win_rate = get_win_rate(team_two_name, dataset_with_winrate_difference, None)
winrate_difference = team_one_win_rate - team_two_win_rate

prediction = predict_classification(dataset_with_winrate_difference, winrate_difference, num_neighbors)
print(prediction)

# with open('your_file.txt', 'w') as f:
#     for item in dataset_with_winrate_difference:
#         f.write("%s\n" % item)

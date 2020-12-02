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

def remove_columns(proto_dataset):
    match_winners = proto_dataset
    columns = 24
    for row in match_winners:
        for column in range(columns, -1, -1):
            if((column == 16) or (column == 15) or (column == 5) or (column == 3)):
                pass
            else:
                del row[column]
    return match_winners

def does_team_one_win_column(proto_dataset):
    team_one_win = proto_dataset
    for row in range(0,len(team_one_win)):
        if(team_one_win[row][1] == team_one_win[row][2]):
            team_one_win[row][1] = 1
        else:
            team_one_win[row][1] = 0
    return team_one_win

def get_winrate_difference(does_team_one_win, dataset):
    winrate_list = []
    winrate_difference_column_dataset = does_team_one_win
    for row in range(0,len(does_team_one_win)):
        team_one_games_before = 0
        team_one_wins_before = 0
        team_one = does_team_one_win[row][2]

        team_two_games_before = 0
        team_two_wins_before = 0
        team_two = does_team_one_win[row][3]

        match_id = does_team_one_win[row][0]

        for match in range(0,len(dataset)):
            if(match_id>dataset[match][3]):
                old_game_team_one = dataset[match][15]
                old_game_team_two = dataset[match][16]
                old_game_winner = dataset[match][5]

                if((team_one == old_game_team_one) or (team_one == old_game_team_two)):
                    team_one_games_before = team_one_games_before + 1
                    if(team_one == old_game_winner):
                        team_one_wins_before = team_one_wins_before + 1

                if((team_two == old_game_team_one) or (team_two == old_game_team_two)):
                    team_two_games_before = team_two_games_before + 1
                    if(team_two == old_game_winner):
                        team_two_wins_before = team_two_wins_before + 1
        try:
            team_one_winrate = team_one_wins_before / team_one_games_before
        except ZeroDivisionError:
            team_one_winrate = 0
        try:
            team_two_winrate = team_two_wins_before / team_two_games_before
        except ZeroDivisionError:
            team_two_winrate = 0
        
        winrate_diff = team_one_winrate - team_two_winrate
        winrate_list.append(winrate_diff)

    i = 0
    for row in winrate_difference_column_dataset:
        row.append(winrate_list[i])
        i = i + 1
    return winrate_difference_column_dataset

def get_distance(prediction_row, data_row):
    distance = 0.0
    distance = (prediction_row - data_row[4])**2
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
	print(neighbors)
	output_values = [row[1] for row in neighbors]
	prediction = max(set(output_values), key=output_values.count)
	return prediction

filename = 'match_map_stats.csv'
dataset = load_csv(filename)
#proto_dataset = filter_dataset(dataset)
proto_dataset = unique_match_ids(dataset)
proto_dataset = remove_columns(proto_dataset)

does_team_one_win = does_team_one_win_column(proto_dataset)
dataset_with_winrate_difference = get_winrate_difference(does_team_one_win, dataset)

num_neighbors = 5
new_game = 0.7
prediction = predict_classification(dataset_with_winrate_difference, new_game, num_neighbors)
print(prediction)
#print('Data=%s, Predicted: %s' % (row, label))

# with open('your_file.txt', 'w') as f:
#     for item in dataset_with_winrate_difference:
#         f.write("%s\n" % item)

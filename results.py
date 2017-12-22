import yaml
import json
import os
import sys
from tabulate import tabulate

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def score_to_points(score):
    if score[0] == None or score[1] == None or score[0] == 'x' or score[1] == 'x':
        return None
    else:
        diff = abs(score[0] - score[1])
        if score[0] > score[1]:
            return diff
        else:
            return -diff

# Takes an array of points and returns an array of confidence picks
# [-3, 5, 1] -> [-2, 3, 1]
# In both arrays, positive numbers mean team1 is favored while negative mean team2 is favored
# The absolute value represents the true point value, negative only indicates which team is favored
def points_to_picks(points):
    # Assign index to all point values (so we can maintain the index after sorting)
    vals = [(p, i) for i, p in enumerate(points)]

    # Sort by values 
    vals.sort(key=lambda x: -1 if x[0] is None else abs(x[0]))
    vals.reverse()

    # Assign confidence values based on sorted values
    picks = [-1] * len(vals)
    confidence = len(vals)
    for val in vals:
        picks[val[1]] = confidence if val[0] is None or val[0] >= 0 else -confidence
        confidence -= 1
    return picks

base_dir = './data/2017'
bowls = yaml.load(open(os.path.join(base_dir, 'bowls.yaml')))
params = yaml.load(open(os.path.join(base_dir, 'params.yaml')))

score_files = [f[0:-7] for f in os.listdir(base_dir) if f.endswith('.scores')]
points_files = [f[0:-7] for f in os.listdir(base_dir) if f.endswith('.points')]
groups = list(params['groups'].keys())

entry_map = {}
entries = []

# Order the entries so that all members are next to the group
for group in groups:
    for name in params['groups'][group]:
        entries.append(name)
    entries.append(group)

# Determine picks for all .score files
for f in score_files:
    score_data = json.load(open(os.path.join(base_dir, f + '.scores')))
    points = [score_to_points(s) for s in score_data]
    picks = points_to_picks(points)
    entry_map[f] = picks

# Determine picks for all .points files
for f in points_files:
    points_data = json.load(open(os.path.join(base_dir, f + '.points')))
    points = [None if v[0] == 0 else v[1] if v[0] == 1 else -v[1] for v in points_data]
    picks = points_to_picks(points)
    entry_map[f] = picks

# Determine picks for all groups
for group in groups:
    points = []
    for idx in range(0, len(bowls)):
        total = 0
        count = 0
        for name in params['groups'][group]:
            pick = entry_map[name][idx]
            if pick is not None:
                total += pick
                count += 1
        if count > 0:
            points.append(total / count)
        else:
            points.append(None)
    entry_map[group] = points_to_picks(points)

# Calculate predictions
points = []
for idx in range(0, len(bowls)):
    total = 0
    for group in groups:
        pick = entry_map[group][idx]
        if pick is not None:
            weighted = pick * params['group_weights'][group]
            total += weighted
            count += 1
    points.append(total)

entry_map['calc'] = points_to_picks(points)
entries.append('calc')

table_data = []
headers = ['Bowl', 'Winner'] + [entry[0:4] for entry in entries]
for idx, bowl in enumerate(bowls):
    row = [bowl['name']]
    if 'winner' in bowl:
        team1Win = bowl['winner'] == 1
        row.append(bowl['team1'] if team1Win else bowl['team2'])
        for name in entries:
            pick = entry_map[name][idx]
            correct = pick > 0 and team1Win or pick < 0 and not team1Win
            color = bcolors.OKGREEN if correct else bcolors.FAIL
            row += ['{}{}{}'.format(color, abs(pick), bcolors.ENDC)]
    table_data.append(row)

print('Results')
print(tabulate(table_data, headers=headers, stralign='right'))
print()

table_data = []
for name in entries:
    won = 0
    lost = 0
    row = [name]
    for idx, bowl in enumerate(bowls):
        if 'winner' in bowl:
            pick = entry_map[name][idx]
            team1Win = bowl['winner'] == 1
            correct = pick > 0 and team1Win or pick < 0 and not team1Win
            if correct:
                won += abs(pick)
            else:
                lost += abs(pick)
    row += [won, 903 - won - lost]
    table_data.append(row)

table_data.sort(key=lambda x: -abs(x[1]))

table_data[0].insert(2, '')
table_data[0].append('')
table_data[0].append('')
for i in range(1, len(table_data)):
    down = table_data[i][1] - table_data[0][1]
    table_data[i].insert(2, '{}{}{}'.format(bcolors.OKGREEN if down >= 0 else bcolors.FAIL, down, bcolors.ENDC))
    plus = table_data[i][3] - table_data[0][3]
    table_data[i].append('{}{}{}{}'.format(bcolors.OKGREEN if plus >= 0 else bcolors.FAIL, '+' if plus > 0 else '', plus, bcolors.ENDC))
    power = down + plus
    table_data[i].append('{}{}{}{}'.format(bcolors.OKGREEN if power >= 0 else bcolors.FAIL, '+' if power > 0 else '', power, bcolors.ENDC))

print('Results')
print(tabulate(table_data, headers=['Entry', 'Score', 'Down', 'PPR', 'Plus', 'Power'], stralign='right'))
print()

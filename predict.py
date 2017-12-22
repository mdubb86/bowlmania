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
        picks[val[1]] = None if val[0] is None else confidence if val[0] >= 0 else -confidence
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
    print(points_data)
    points = [None if v[0] == 0 else v[1] if v[0] == 1 else -v[1] for v in points_data]
    picks = points_to_picks(points)
    print(picks)
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
headers = ['Bowl', 'Team 1', 'Team 2'] + [entry[0:4] for entry in entries]

for idx, bowl in enumerate(bowls):
    row = [bowl['name'], bowl['team1'], bowl['team2']]
    for name in entries:
        pick = entry_map[name][idx]
        color = bcolors.ENDC if pick is None else bcolors.OKBLUE if pick > 0 else bcolors.OKGREEN
        pick = abs(pick) if pick is not None else ''
        row += ['{}{}{}'.format(color, pick, bcolors.ENDC)]
    table_data.append(row)

print('Overview')
print(tabulate(table_data, headers=headers, stralign='right'))
print()

table_data = [[bowl['name'], bowl['team1'] if entry_map['calc'][idx] >= 0 else bowl['team2'], abs(entry_map['calc'][idx])] for idx, bowl in enumerate(bowls)]
headers = ['Bowl', 'Pick', 'Confidence']
print('Picks')
print(tabulate(table_data, headers=headers, stralign='right'))
print()

print('Picks (sorted by confidence)')
table_data.sort(key=lambda row: row[2])
print(tabulate(table_data, headers=headers, stralign='right'))


import argparse
import json
import os
import yaml
from time import sleep
import curses
import curses.ascii as KEYS

def main(stdscr):
    curses.echo()
    current = 0
    while True:
        stdscr.clear()
        header = '{} ({} / {})'.format(bowls[current]['name'], current + 1, len(bowls))
        stdscr.addstr(0, 0, header)
        str1 = bowls[current]['team1']
        str2 = bowls[current]['team2']
        if vals[current][0] == 1:
            str1 += ' <--'
        elif vals[current][0] == 2:
            str2 += ' <--'
        str3 = 'Points: {}'.format(vals[current][1])
        stdscr.addstr(1, 0, str1)
        stdscr.addstr(2, 0, str2)
        stdscr.addstr(3, 0, str3)
        stdscr.move(3, len(str3))

        key = stdscr.getch()
        if key == 258:
            t1 = True
            current = min(len(bowls) - 1, current + 1)
        elif key == 259:
            t1 = True
            current = max(0, current - 1)
        elif key == KEYS.TAB:
            vals[current][0] = vals[current][0] + 1 if vals[current][0] <= 1 else 0
        elif key == KEYS.LF:
            current = min(len(bowls) - 1, current + 1)
        elif key == KEYS.BS or key == KEYS.DEL:
            vals[current][1] = vals[current][1][0:-1]
        elif KEYS.isdigit(key):
            vals[current][1] += chr(key)
        elif key == 45:
            vals[current][1] += '.'
        elif key == 46:
            vals[current][1] += '.'
        elif key == KEYS.ESC:
             data = [[v1, to_file(v2)] for v1, v2 in vals]
             with open(data_file, 'w') as outfile:
                 json.dump(data, outfile)
             break

        stdscr.refresh()

def to_file(val):
    if val == '':
        return None
    else:
        return float(val)

def from_file(val):
    s = str(val)
    if s == 'None':
        return ''
    else:
        return s


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='name')
    args = parser.parse_args()

    base_dir = './data/2017'
    bowls = yaml.load(open(os.path.join(base_dir, 'bowls.yaml')))
    data_file = os.path.join(base_dir, args.name + '.points')

    if os.path.exists(data_file):
        with open(data_file, 'r') as infile:
            data = json.load(infile)
            vals = [[v[0], from_file(v[1])] for v in data]
    else:
        vals = [[0, ''] for i in range(0, len(bowls))]

    #print(data)
    #print(vals)
    curses.wrapper(main)

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
    t1 = True
    while True:
        stdscr.clear()
        header = '{} ({} / {})'.format(bowls[current]['name'], current + 1, len(bowls))
        stdscr.addstr(0, 0, header)
        str1 = '{}: {}'.format(bowls[current]['team1'], vals[current][0])
        stdscr.addstr(1, 0, str1)
        str2 = '{}: {}'.format(bowls[current]['team2'], vals[current][1])
        stdscr.addstr(2, 0, str2)
        if t1:
            stdscr.move(1, len(str1))
        else:
            stdscr.move(2, len(str2))

        key = stdscr.getch()
        if key == 258:
            t1 = True
            current = min(len(bowls) - 1, current + 1)
        elif key == 259:
            t1 = True
            current = max(0, current - 1)
        elif key == KEYS.TAB:
            t1 = not t1
        elif key == KEYS.LF:
            if t1:
                t1 = False
            else:
                t1 = True
                current = min(len(bowls) - 1, current + 1)
        elif key == KEYS.BS or key == KEYS.DEL:
            if t1:
                vals[current][0] = vals[current][0][0:-1]
            else:
                vals[current][1] = vals[current][1][0:-1]
        elif key == 45:
            if t1:
                vals[current][0] += '-'
            else:
                vals[current][1] += '-'
        elif key == 46:
            if t1:
                vals[current][0] += '.'
            else:
                vals[current][1] += '.'
        elif key == 120:
            if t1:
                vals[current][0] = 'x'
            else:
                vals[current][1] = 'x'
        elif KEYS.isdigit(key):
            if t1:
                vals[current][0] += chr(key)
            else:
                vals[current][1] += chr(key)
        elif key == KEYS.ESC:
             data = [[to_file(v1), to_file(v2)] for v1, v2 in vals]
             with open(data_file, 'w') as outfile:
                 json.dump(data, outfile)
             break

        stdscr.refresh()

def to_file(val):
    if val == '':
        return None
    elif val == 'x':
        return 'x'
    else:
        return float(val)

def from_file(val):
    s = str(val)
    if s.endswith('.0'):
        return s[0:-2]
    elif s == 'None':
        return ''
    else:
        return s

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='name')
    args = parser.parse_args()

    base_dir = './data/2017'

    bowls = yaml.load(open(os.path.join(base_dir, 'bowls.yaml')))
    data_file = os.path.join(base_dir, args.name + '.scores')

    if os.path.exists(data_file):
        with open(data_file, 'r') as infile:
            data = json.load(infile)
            vals = [[from_file(v[0]), from_file(v[1])] for v in data]
    else:
        vals = [['', ''] for i in range(0, len(bowls))]

    #print(data)
    #print(vals)
    curses.wrapper(main)

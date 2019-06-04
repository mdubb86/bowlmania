import argparse
import json
import os
import yaml
from time import sleep
import curses
import curses.ascii as KEYS
import pyperclip
import queue
import threading
import sys

def mark_dirty():
    global dirty
    dirty = True

def set_val(val):
    global vals, current, t1
    vals[current][0 if t1 else 1] = val
    mark_dirty()
    
def append_val(val):
    global vals, current, t1
    set_val(vals[current][0 if t1 else 1] + val)

def backspace():
    global vals, current, t1
    set_val(vals[current][0 if t1 else 1][0:-1])

def set_t1(val):
    global t1, clipboard, current
    t1 = val
    clipboard = bowls[current]['team' + ('1' if t1 else '2')]
    pyperclip.copy(clipboard)
    os.system("say '" + clipboard + "' &")
    mark_dirty()

def swap_teams():
    global t1
    set_t1(not t1)

def set_bowl(idx):
    global current
    current = idx
    set_t1(True)

def next_bowl():
    global bowls, current
    set_bowl(min(len(bowls) - 1, current + 1))

def prev_bowl():
    global bowls, current
    set_bowl(max(0, current - 1))

def advance():
    global vals, current
    if '' in vals[current]:
        swap_teams()
    else:
        next_bowl()

def is_float(val):
    try:
        float(val)
        return True
    except ValueError:
        return False

def log(msg):
    global log_file
    print(msg, file=log_file, flush=True)

def main(stdscr):
    global bowls, vals, t1, clipboard, current, dirty, alias_sets, log_file

    alias_sets = []
    curses.halfdelay(1)

    current = 0
    t1 = True
    clipboard=None
    dirty = True
    log_file = open("/tmp/keys", "w")

    while True:
        try:
            key = stdscr.getkey()
        except curses.error:
            key = None
            clipped = pyperclip.paste()
            log("Clipboard: {}".format(clipboard))
            if clipboard == None:
                clipboard = clipped
                continue
            elif clipped != clipboard:
                clipboard = clipped
                log("Clipboard changed: {}")
                if is_float(clipboard):
                    set_val(clipboard)
                    advance()
                else:
                    if match(clipboard, bowls[current]['team1']):
                        set_t1(True)
                    elif match(clipboard, bowls[current]['team2']):
                        set_t1(False)

        if key == None:
            pass
        elif key == 'KEY_DOWN':
            next_bowl()
        elif key == 'KEY_UP':
            prev_bowl()
        elif len(key) > 1:
            continue
        elif ord(key) == KEYS.TAB:
            swap_teams()
        elif ord(key) == KEYS.LF:
            advance()
        elif ord(key) == 127:
            backspace()
        elif ord(key) == 45:
            append_val('-')
        elif ord(key) == 46:
            append_val('.')
        elif ord(key) == 120:
            set_val('x')
        elif KEYS.isdigit(key):
            append_val(key)
        elif ord(key) == KEYS.ESC:
             data = [[to_file(v1), to_file(v2)] for v1, v2 in vals]
             with open(data_file, 'w') as outfile:
                 json.dump(data, outfile)
             log_file.close()
             break
        if dirty:
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
            stdscr.refresh()
            dirty = False

def match(str1, str2):
    global alias_sets
    if str1 == str2:
        return True
    for alias_set in alias_sets:
        if str1 in alias_set:
            return str2 in alias_set
    return False

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

    base_dir = './data/2018'

    bowls = yaml.load(open(os.path.join(base_dir, 'bowls.yaml')))
    data_file = os.path.join(base_dir, args.name + '.scores')

    if os.path.exists(data_file):
        with open(data_file, 'r') as infile:
            data = json.load(infile)
            vals = [[from_file(v[0]), from_file(v[1])] for v in data]
    else:
        vals = [['', ''] for i in range(0, len(bowls))]
    
    curses.wrapper(main)

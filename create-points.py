import argparse
import json
import os
import yaml
from time import sleep
import curses
import curses.ascii as KEYS
import pyperclip

def mark_dirty():
    global dirty
    dirty = True

def get_val():
    global vals, current
    return vals[current][1]

def set_val(val):
    global vals, current
    vals[current][1] = val
    mark_dirty()
    
def append_val(val):
    global vals, current
    set_val(vals[current][1] + val)

def backspace():
    global vals, current
    set_val(vals[current][1][0:-1])

def pick(val):
    global vals, current
    vals[current][0] = val
    name = 'no pick' if val == 0 else bowls[current]['team1'] if val == 1 else bowls[current]['team2']
    os.system("say '" + name + "' &")
    mark_dirty()

def advance():
    global vals, current
    p = vals[current][0]
    if p == 0:
        pick(1)
    elif p == 1:
        pick(2)
    elif p == 2:
        pick(0)

def set_bowl(idx):
    global current, dirty
    current = idx
    val = vals[current][0]
    name = None if val == 0 else bowls[current]['team1'] if val == 1 else  bowls[current]['team2']
    if name is not None:
        os.system("say '" + name + "' &")
    dirty = True

def next_bowl():
    global bowls, current
    set_bowl(min(len(bowls) - 1, current + 1))

def prev_bowl():
    global bowls, current
    set_bowl(max(0, current - 1))

def is_float(val):
    try:
        float(val)
        return True
    except ValueError:
        return False

def main(stdscr):
    global bowls, vals, t1, current, dirty, alias_sets

    log_file = open("/tmp/bowls.log", "w")
    def log(msg):
        nonlocal log_file
        print(msg, file=log_file, flush=True)

    curses.halfdelay(1)
    current = 0
    clipboard=None
    dirty = True
    
    alias_sets = []
    while True:
        try:
            key = stdscr.getkey()
        except curses.error:
            key = None
            clipped=pyperclip.paste()
            log("Clipped: {}".format(clipped))
            if clipboard == None:
                clipboard = clipped
                continue
            elif clipped != clipboard:
                clipboard = clipped
                log("Clipboard changed: {}".format(clipboard))
                if is_float(clipboard):
                    set_val(clipboard)
                    #clipboard=''
                    #pyperclip.copy('')
                    sleep(.1)
        
        if key == None:
            pass
        elif key == 'KEY_DOWN':
            next_bowl()
        elif key == 'KEY_UP':
            prev_bowl()
        elif KEYS.isdigit(key):
            append_val(key)
        elif key == 'q':
            pick(1)
        elif key == 'a':
            pick(2)
        elif len(key) > 1:
            continue
        elif ord(key) == KEYS.TAB:
            advance()
        elif ord(key) == KEYS.LF:
            next_bowl()
        elif ord(key) == KEYS.BS or ord(key) == KEYS.DEL:
            backspace()
        elif ord(key) == 45:
            append_val('-')
        elif ord(key) == 46:
            append_val('.')
        elif ord(key) == KEYS.ESC:
             data = [[v1, to_file(v2)] for v1, v2 in vals]
             with open(data_file, 'w') as outfile:
                 json.dump(data, outfile)
             break

        if dirty:
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

    base_dir = './data/2019'
    bowls = yaml.load(open(os.path.join(base_dir, 'bowls.yaml')))
    data_file = os.path.join(base_dir, args.name + '.points')

    if os.path.exists(data_file):
        with open(data_file, 'r') as infile:
            data = json.load(infile)
            vals = [[v[0], from_file(v[1])] for v in data]
    else:
        vals = [[0, ''] for i in range(0, len(bowls))]

    curses.wrapper(main)

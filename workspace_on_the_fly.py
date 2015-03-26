#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# daanmathot@gmail.com

'''
  i3 workspace helper functions

  # this will (try) to send the focused window to the workspace matching users input
  bindsym Mod1+Shift+w exec python /path/to/workspaces_on_the_fly.py move_to_workspace

  # this will first create a new workspace using the focused window's instance name
  bindsym Mod1+Shift+t exec python /path/to/workspaces_on_the_fly.py move_to_temp_workspace

  # this will (try) to go to the workspace matching user input
  bindsym Mod1+Shift+g exec python /path/to/workspaces_on_the_fly.py go_to_workspace
'''

import argparse
import sys
import commands
import os

import i3

def _get_all_workspaces():
    with open(os.path.expanduser('~/.config/i3/config')) as f:
        config = f.read()
        variables = dict((k, v) for k, v in re.findall(r'set.*(\$[^ ]+)[ "]*([a-z]+)', config, re.M))
        workspaces = [variables[variable] for variable in 
                        re.findall(r'^\s*workspace.*(\$[^ ]+)', config, re.M)
                        if variables.find(variable)]

    all_workspaces = workspaces + filter(
        lambda w: w not in workspaces,
        [w['name'] for w in i3.get_workspaces()])

    return all_workspaces



def _i3input_getch(getKey=None):
    output = commands.getoutput('i3-input -l 1 -F "%s"')
    getch_info = dict((k.strip(), v.strip()) for k, v in
                      [line.split('=') for line in output.split('\n')
                      if len(line.split()) == 3 and '=' in line])

    if not getKey:
        return getch_info
    return getch_info.get(getKey)


def _get_target_workspace():
    workspaces = _get_all_workspaces()
    input_string = ''
    while True:
        c = _i3input_getch('command')

        if c == '\x03':
            # end of line (^C), abort.
            return
        if c == '\x08' or c == '\x7f':
            # backspace, remove last c from input string
            input_string = input_string[:-1]
        else:
            input_string += c

        # get workspaces matching input_string
        target_workspaces = filter(
            lambda w: w[:len(input_string)] == input_string,
            workspaces)

        if not target_workspaces:
            return

        if len(target_workspaces) == 1:
            return target_workspaces[0]


def _move_to_workspace(is_temp_workspace=False):
    # get focused window
    active_window = i3.filter(nodes=[], focused=True)
    instance = active_window[0]['window_properties']['instance']
    if is_temp_workspace:
        workspace = instance.lower()
    else:
        workspace = _get_target_workspace()
    i3.workspace(workspace)
    i3.command('[instance="{0}"] move workspace {1}'.format(instance, workspace))


def move_to_temp_workspace():
    _move_to_workspace(True)


def move_to_workspace():
    _move_to_workspace()


def go_to_workspace():
    target_workspace = _get_target_workspace()
    if target_workspace:
        i3.workspace(target_workspace)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('task')
    parser.add_argument('--arg', dest='args', action='append')
    parsed_args = parser.parse_args()
    task = globals().get(parsed_args.task)

    if not task:
        sys.exit(-1)

    args = parsed_args.args if parsed_args.args else []

    task(*args)

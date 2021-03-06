from __future__ import print_function
import sys
import json
# from dolfin import MPI
import os
import mpi4py.MPI as MPI

MPI_rank = MPI.COMM_WORLD.Get_rank()
MPI_size = MPI.COMM_WORLD.Get_size()

RED = "\033[1;37;31m{s}\033[0m"
BLUE = "\033[1;37;34m{s}\033[0m"
GREEN = "\033[1;37;32m{s}\033[0m"
YELLOW = "\033[1;37;33m{s}\033[0m"
CYAN = "\033[1;37;36m{s}\033[0m"
NORMAL = "{s}"
ON_RED = "\033[41m{s}\033[0m"


__all__ = ["convert", "str2list", "parseval", "parse_command_line",
           "info_style", "info_red", "info_blue", "info_yellow",
           "info_green", "info_cyan", "info", "info_on_red",
           "info_split_style", "info_split", "info_warning",
           "info_error",
           "print_dir", "print_recipe", "help_menu"]


# Stolen from Oasis
def convert(data):
    if isinstance(data, dict):
        return {convert(key): convert(value)
                for key, value in data.iteritems()}
    elif isinstance(data, list):
        return [convert(element) for element in data]
    # elif isinstance(data, unicode):
    #     return data.encode('utf-8')
    else:
        return data


def str2list(string):
    if bool(string[0] == "[" and string[-1] == "]" and
            "--" not in string):
        # Avoid parsing line specification as list.
        li = string[1:-1].split(",")
        for i in range(len(li)):
            li[i] = str2list(li[i])
        return li
    else:
        return parseval(string)


def parseval(value):
    try:
        value = json.loads(value)
    except ValueError:
        # json understands true/false, not True/False
        if value in ["True", "False"]:
            value = eval(value)
        elif "True" in value or "False" in value:
            value = eval(value)

    if isinstance(value, dict):
        value = convert(value)
    elif isinstance(value, list):
        value = convert(value)
    return value


def parse_command_line():
    cmd_kwargs = dict()
    for s in sys.argv[1:]:
        if s in ["-h", "--help", "help"]:
            key, value = "help", "true"
        elif s.count('=') == 0:
            key, value = s, "true"
        elif s.count('=') == 1:
            key, value = s.split('=', 1)
        else:
            raise TypeError(
                "Only kwargs separated with at the most a single '=' allowed.")

        value = parseval(value)
        if isinstance(value, str):
            value = str2list(value)

        cmd_kwargs[key] = value
    return cmd_kwargs


def info_style(message, check=True, style=NORMAL):
    if MPI_rank == 0 and check:
        print(style.format(s=message))


def info_red(message, check=True):
    info_style(message, check, RED)


def info_blue(message, check=True):
    info_style(message, check, BLUE)


def info_yellow(message, check=True):
    info_style(message, check, YELLOW)


def info_green(message, check=True):
    info_style(message, check, GREEN)


def info_cyan(message, check=True):
    info_style(message, check, CYAN)


def info(message, check=True):
    info_style(message, check)


def info_on_red(message, check=True):
    info_style(message, check, ON_RED)


def info_split_style(msg_1, msg_2, style_1=BLUE, style_2=NORMAL, check=True):
    if MPI_rank == 0 and check:
        print(style_1.format(s=msg_1) + " " + style_2.format(s=msg_2))


def info_split(msg_1, msg_2, check=True):
    info_split_style(msg_1, msg_2, check=check)


def info_warning(message, check=True):
    info_split_style("Warning:", message, style_1=ON_RED, check=check)


def info_error(message, check=True):
    info_split_style("Error:", message, style_1=ON_RED, check=check)
    exit("")


def print_dir(folder):
    for path in sorted(os.listdir(folder), key=str.lower):
        filename, ext = os.path.splitext(path)
        if ext == ".py" and filename[0].isalpha():
            info("   " + filename)


def print_recipe(lines, len_max=80):
    for i, line in enumerate(lines):
        if len(line) > len_max:
            words = line.split(" ")
            part_line = ""
            for word in words:
                part_line += word
                if len(part_line) > len_max:
                    info(part_line)
                    part_line = ""
                else:
                    part_line += " "
            if len(part_line) > 1:
                info(part_line)
        else:
            info(line)


def help_menu():
    info_yellow("BERNAISE (Binary ElectRohydrodyNAmIc SolvEr)")
    info_red("You called for help! And here are your options:\n")

    info_cyan("Usage:")
    info("   python sauce.py problem=[...] solver=[...] ...")

    info_cyan("\nImplemented problems:")

    print_dir("problems")

    info_cyan("\nImplemented solvers:")

    print_dir("solvers")

    info("\n...or were you looking for the recipe "
         "for Bearnaise sauce? [y/N] ")
    q = str(input("")).lower()

    if MPI_rank == 0:
        if q in ["y", "yes"]:
            with open("common/recipe.txt") as f:
                lines = f.read().splitlines()

                print_recipe(lines)

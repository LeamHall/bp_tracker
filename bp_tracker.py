#!/usr/bin/env python3

# name:     bp_tracker.py
# version:  0.0.1
# date:     20220509
# authors:  Leam Hall, Alex Kleider
# desc:     Track and report on blood pressure numbers.

# Notes:
#  Datafile expects three ints and one float, in order.

# TODO
#   Add statistical analysis for standard deviation.
#   Report based on time of day (early, midmorning, afternoon, evening)
#   (?) Add current distance from goal?
#   Add more tests.

import argparse
from datetime import datetime
from operator import attrgetter
import os
import sys

data_file = "data/bp_numbers.txt"

systolic_labels = (
    (0, 0, "dead"),
    (1, 49, "low: medication required"),
    (50, 69, "low: at risk"),
    (70, 85, "low"),
    (86, 120, "good"),
    (121, 129, "elevated"),
    (130, 139, "high: stage 1"),
    (140, 179, "high: stage 2"),
    (180, 300, "high: crisis"),
)

diastolic_labels = (
    (0, 0, "dead"),
    (1, 45, "low: medication required"),
    (46, 55, "low: at risk"),
    (56, 65, "low"),
    (66, 79, "good"),
    (80, 89, "high: stage 1"),
    (90, 119, "high: stage 2"),
    (120, 300, "high: crisis"),
)


class Result:
    def __init__(self, line=""):
        line_data = line.strip().split()
        self.systolic = int(line_data[0])
        self.diastolic = int(line_data[1])
        self.pulse = int(line_data[2])
        if len(line_data) == 3:
            self.timestamp = datetime.now().strftime("%Y%m%d.%H%M")
        else:
            self.timestamp = line_data[3]

    def before_date(self, date):
        day = int(self.timestamp.split(".")[0])
        return day <= date

    def after_date(self, date):
        day = int(self.timestamp.split(".")[0])
        return day >= date

    def in_date_range(self, begin, end):
        return self.after_date(begin) and self.before_date(end)


def add(args):
    """Append arguments to datafile"""
    if check_file(args.file, "w"):
        timestamp = datetime.now().strftime("%Y%m%d.%H%M")
        this_report = args.add
        this_report.append(timestamp)
        with open(args.file, "a") as file:
            file.write("{} {} {} {}\n".format(*this_report))
    else:
        print("Unable to write to", args.file)
        sys.exit(1)


def results_from_file(report_file):
    """
    Input is the report file: four (string) values per line.
    Output is [int, int, int, str], systolic, diastolic, pulse, time stamp.
    [1] Each of the 4 strings represents a number: first three are integers,
    last (the fourth) is a YYYYmmdd.hhmm string representation of a timestamp
    """
    res = []
    with open(report_file, "r") as f:
        for line in useful_lines(f):
            res.append(Result(line))
    return res


def average(lst):
    """Takes a list of numerics and returns an integer average"""
    return sum(lst) // len(lst)


def check_file(file, mode):
    """
    Mode (must be 'r' or 'w') specifies if we need to
    r)ead or w)rite to the file.
    """
    if mode == "r" and os.access(file, os.R_OK):
        return True
    if mode == "w":
        if os.access(file, os.W_OK):
            return True
        if not os.path.exists(file) and os.access(
            os.path.dirname(file), os.W_OK
        ):
            return True
    return False


def format_report(systolics, diastolics):
    """
    Takes the numeric lists of systolics, diastolics, and pulses, and
    return a string for printing.
    """
    systolic = get_last(systolics)
    sys_low, sys_upper, sys_label = get_labels(systolic, systolic_labels)
    diastolic = get_last(diastolics)
    dia_low, dia_upper, dia_label = get_labels(diastolic, diastolic_labels)
    result = "Systolic {} ({} [{}-{}])\n".format(
        systolic,
        sys_label,
        sys_low,
        sys_upper,
    )
    result += "Diastolic {} ({} [{}-{}])\n".format(
        diastolic,
        dia_label,
        dia_low,
        dia_upper,
    )
    result += "Average {}/{} \n".format(
        average(systolics), average(diastolics)
    )
    return result


def get_args():
    """Gets args"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        help="Report FILE (default bp_numbers.txt)",
        default=data_file,
    )
    parser.add_argument(
        "-a",
        "--add",
        nargs=3,
        help="Add in the order of systolic, diastolic, pulse",
    )
    parser.add_argument(
        "-t",
        "--times",
        nargs=2,
        type=int,
        help="Only consider readings within TIMES span",
    )
    parser.add_argument(
        "-r",
        "--range",
        nargs="+",
        type=int,
        help="""Begin and end dates are in YYYYMMDD format.
            Default today for end. For example:
            20230809 20230824
            or
            20230809""",
    )
    parser.add_argument(
        "-n",
        "--number",
        nargs=1,
        type=int,
        help="Only consider the last NUMBER valid readings",
    )
    return parser.parse_args()


def get_label(num, scale):
    """
    Takes a number and a tuple of (min, max, lable) tuples,
    returns the label for the range the number falls into.
    """
    for group in scale:
        lower, upper, label = group
        if num in range(lower, upper + 1):
            # The 'upper + 1' is required because range doesn't include upper
            return label
    return None


def get_labels(num, scale):
    """
    Takes a number and a tuple of (min, max, lable) tuples,
    returns the min, max, and label for the range the number falls into.
    """
    for group in scale:
        lower, upper, label = group
        if num in range(lower, upper + 1):
            # The 'upper + 1' is required because range doesn't include upper
            return lower, upper, label
    return None


def get_last(val):
    """Returns last element of a list."""
    return val[-1]


def list_of_attr(data, attr):
    """Takes a list of results and returns a list of the specific attribute"""
    result = []
    for element in data:
        result.append(getattr(element, attr))
    return result


def sort_by_attr(data, _attr):
    """Sorts lists of lists by specified index in sub-lists."""
    get_on_attr = attrgetter(_attr)
    return sorted(data, key=get_on_attr)


def time_of_day_filter(datum, begin, end):
    time = datum[3].split(".")[-1]
    if time >= begin and time <= end:
        return True
    return False


def useful_lines(stream, comment="#"):
    """
    Blank lines and leading and/or trailing white space are ignored.
    If <comment> resolves to true, lines beginning with <comment>
    (after being stripped of leading spaces) are also ignored.
    <comment> can be set to <None> if don't want this functionality.
    Other lines are returned ("yield"ed) stripped of leading and
    trailing white space.
    """
    for line in stream:
        line = line.strip()
        if comment and line.startswith(comment):
            continue
        if line:
            yield line


if __name__ == "__main__":
    args = get_args()

    try:
        data = results_from_file(args.file)
    except FileNotFoundError:
        print("Unable to find {}, exiting.".format(args.file))
        sys.exit(1)

    if args.add:
        add(args)
    elif args.range:
        print("In results")
        begin = args.range[0]
        if len(args.range) > 1:
            end = args.range[1]
        else:
            end = int(datetime.now().strftime("%Y%m%d"))
        if begin > end:
            print("The begin date is greater than the end date")
            sys.exit(1)
        results = [
            result for result in data if result.in_date_range(begin, end)
        ]
    else:
        results = data

    sys_list = list_of_attr(results, "systolic")
    dia_list = list_of_attr(results, "diastolic")

    print(format_report(sys_list, dia_list))

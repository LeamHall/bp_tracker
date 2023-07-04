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
from operator import itemgetter
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


invalid_lines = []  # still to decide: -v or -i --invalid option?
# option might collect a file name into which to dump invalid_lines


class NoValidData(ValueError):
    pass


def add(args):
    # This format allows sequencing now and parsing later.
    if check_file(args.file, "w"):
        timestamp = datetime.now().strftime("%Y%m%d.%H%M")
        this_report = args.add
        this_report.append(timestamp)
        with open(args.file, "a") as file:
            file.write("{} {} {} {}\n".format(*this_report))
    else:
        print("Unable to write to", args.file)
        sys.exit(1)


def array_from_file(report_file, invalid_lines=None):
    """
    Input is the report file: four (string) values per line.
    Output is [int, int, int, str], systolic, diastolic, pulse, time stamp.
    [1] Each of the 4 strings represents a number: first three are integers,
    last (the fourth) is a YYYYmmdd.hhmm string representation of a timestamp
    """
    res = []
    with open(report_file, "r") as f:
        for line in useful_lines(f):
            numbers = valid_data(line, invalid_lines=invalid_lines)
            if numbers:
                res.append(numbers)
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


def date_range_filter(datum, begin, end):
    if no_date_stamp(datum):
        return
    day = datum[3].split(".")[0]
    if day >= begin and day <= end:
        return True


def filter_data(data, args):
    """
    Although the decision is perhaps arbitrary,
    we do the filtration first and only consider
    the -n --number2consider argument on what ever
    passes the filters rather than starting with
    -n readings and applying filters afterwards
    which could result in less than n values being
    considered.
    """
    ret = []
    for item in data:
        if args.times and not time_of_day_filter(
            item, args.times[0], args.times[1]
        ):
            continue
        if args.range and not date_range_filter(
            item, args.range[0], args.range[1]
        ):
            continue
        if args.date and not not_before_filter(item, args.date[0]):
            continue
        ret.append(item)
    if args.number:
        n = args.number[0]
        ln = len(ret)
        if (n > ln) or (n < 1):
            n = ln
        ret = ret[-n:]
    if len(ret) == 0:
        raise NoValidData("No data to report on")
    return ret


def format_report(systolics, diastolics):
    """
    Takes the numeric lists of systolics, diastolics, and pulses, and
    return a string for printing.
    """
    systolic = get_last(systolics)
    diastolic = get_last(diastolics)
    result = "Systolic {} ({}) \n".format(
        systolic, get_label(systolic, systolic_labels)
    )
    result += "Diastolic {} ({}) \n".format(
        diastolic, get_label(diastolic, diastolic_labels)
    )
    result += "Average {}/{} \n".format(
        average(systolics), average(diastolics)
    )
    return result


def get_args():
    """ """
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
        nargs=2,
        type=int,
        help="Only consider readings taken within date RANGE.",
    )
    parser.add_argument(
        "-d",
        "--date",
        nargs=1,
        type=int,
        help="Ignore readings prior to DATE",
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


def get_last(val):
    """Returns last element of a list."""
    return val[-1]


def list_from_index(data, index):
    """Takes a list of lists and returns a list of the specific index"""
    result = []
    for element in data:
        result.append(element[index])
    return result


def no_date_stamp(data):
    if data[3] == 0:
        return True


def not_before_filter(data, date):
    if no_date_stamp(data):
        return
    day = data[3].split(".")[0]
    if day >= date:
        return True


def sort_by_index(data, index):
    """Sorts lists of lists by specified index in sub-lists."""
    get_on_index = itemgetter(index)
    return sorted(data, key=get_on_index)


def time_of_day_filter(datum, begin, end):
    if no_date_stamp(datum):
        return
    time = datum[3].split(".")[-1]
    if time >= begin and time <= end:
        return True


def useful_lines(stream, comment="#"):
    """
    A generator which accepts a stream of lines (strings.)
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


def valid_data(line, invalid_lines=None):
    """
    Accepts what is assumed to be a valid line.
    If valid, returns a list of int, int, int, string.
    If not valid and if <invalid_lines> is not None,
    assumes errors is a list to which the invalid line is added.
    """
    data = line.split()
    if len(data) == 4:
        try:
            for i in range(3):
                data[i] = int(data[i])
            data[3] = str(data[3])
        except ValueError:
            if invalid_lines is not None:
                invalid_lines.append(line)
            return
    else:
        if invalid_lines is not None:
            invalid_lines.append(line)
        return
    return data


if __name__ == "__main__":
    args = get_args()

    if args.add:
        add(args)

    try:
        data = filter_data(array_from_file(args.file, invalid_lines), args)
        data = sort_by_index(data, -1)
    except FileNotFoundError:
        print("Unable to find {}, exiting.".format(args.file))
        sys.exit(1)
    except NoValidData:
        print("No viable data in {}, exiting.".format(args.file))
        sys.exit(1)

    for element in data:
        sys_list = list_from_index(data, 0)
        dia_list = list_from_index(data, 1)

    print(format_report(sys_list, dia_list))

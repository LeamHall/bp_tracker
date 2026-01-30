# bp_tracker

Tool to track and evaluate blood pressure recordings.

## Overview

bp_tracker is a command-line utility for recording and analyzing blood pressure readings. It stores readings in a simple text file format and provides health classifications based on standard blood pressure ranges.

## Usage

```
usage: bp_tracker.py [-h] [-f FILE] [-a ADD ADD ADD] [-r RANGE [RANGE ...]]

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Report FILE (default bp_numbers.txt)
  -a ADD ADD ADD, --add ADD ADD ADD
                        Add in the order of systolic, diastolic, pulse
  -r RANGE [RANGE ...], --range RANGE [RANGE ...]
                        Begin and end dates are in YYYYMMDD format. Default today
                        for end. For example: 20230809 20230824 or 20230809
```

### Examples

Report all readings:
```
./bp_tracker.py
```

Add a new reading (systolic 120, diastolic 80, pulse 60):
```
./bp_tracker.py -a 120 80 60
```

Report readings for a specific date range:
```
./bp_tracker.py -r 20230809 20230824
```

Report readings from a date to today:
```
./bp_tracker.py -r 20230809
```

Use a different data file:
```
./bp_tracker.py -f /path/to/mydata.txt
```

## Data Format

The data file uses space-separated values with one reading per line:

```
systolic diastolic pulse timestamp
```

Example:
```
# Comments start with #
120 80 60 20220914.1407
130 85 65 20220915.1008
```

Fields:
- systolic: Systolic blood pressure (integer)
- diastolic: Diastolic blood pressure (integer)
- pulse: Pulse rate (integer)
- timestamp: Date and time in YYYYmmdd.HHMM format (auto-generated when adding)

Lines starting with # are treated as comments. Blank lines are ignored.

## Health Classifications

The tool classifies blood pressure readings according to standard medical ranges:

SYSTOLIC:
- 0-49: Low, medication required
- 50-69: Low, at risk
- 70-85: Low
- 86-120: Good
- 121-129: Elevated
- 130-139: High, stage 1
- 140-179: High, stage 2
- 180+: High, crisis

DIASTOLIC:
- 0-45: Low, medication required
- 46-55: Low, at risk
- 56-65: Low
- 66-79: Good
- 80-89: High, stage 1
- 90-119: High, stage 2
- 120+: High, crisis

## Report Output

The report shows:
- Latest systolic reading with classification and range
- Latest diastolic reading with classification and range
- Average systolic with classification and range
- Average diastolic with classification and range

Example output:
```
Systolic 130 (elevated [121-129])
Diastolic 85 (high: stage 1 [80-89])
Systolic Average 125 (elevated [121-129])
Diastolic Average 82 (high: stage 1 [80-89])
```

## Testing

The project includes comprehensive test coverage using Python's unittest framework.

Run all tests:
```
make test
```

Run tests manually:
```
python -m unittest discover -s test -p "test_*.py" -v
```

Run specific test file:
```
python -m unittest test.test_bp_tracker -v
python -m unittest test.test_bp_tracker_exhaustive -v
```

Run a single test:
```
python -m unittest test.test_bp_tracker.TestBpTracker.test_average
```

Test coverage:
- test/test_bp_tracker.py: 13 tests (original test suite)
- test/test_bp_tracker_exhaustive.py: 81 tests (comprehensive test suite)
- Total: 94 tests

## Development

Code formatting:
```
python -m black . -l79
```

Code linting:
```
flake8
```

Test coverage report:
```
coverage run -m unittest discover -s test -p "test_*.py"
coverage report -m
```

Run full quality suite:
```
make all
```

Clean generated files:
```
make clean
```

## Code Review

A comprehensive code review has been performed on this codebase. See the following documents for details:

- CODE_REVIEW.txt: Detailed analysis of bugs, robustness issues, and improvements
- REVIEW_SUMMARY.txt: Executive summary with prioritized recommendations
- QUICK_REFERENCE.txt: Quick command reference and key points

CRITICAL BUGS IDENTIFIED:
1. Line 297: sys.exit() called with incorrect arguments
2. Lines 317-320: Crash when no results match date range
3. Lines 131-133: Unpacking None causes TypeError

See CODE_REVIEW.txt for complete details and recommended fixes.

## Dependencies

REQUIRED: None (uses Python Standard Library only)

OPTIONAL (for development):
- coverage: Test coverage reporting
- black: Code formatting
- flake8: Code linting

Install optional dependencies:
```
pip install coverage black flake8
```

## Project Structure

```
bp_tracker/
├── bp_tracker.py                        Main application
├── data/
│   └── bp_numbers.txt                   Default data file
├── test/
│   ├── test_bp_tracker.py              Original tests (13 tests)
│   └── test_bp_tracker_exhaustive.py   Comprehensive tests (81 tests)
├── Makefile                             Build and test automation
├── README.md                            This file
├── CLAUDE.md                            Project documentation for Claude Code
├── CODE_REVIEW.txt                      Detailed code review
├── REVIEW_SUMMARY.txt                   Executive summary
└── QUICK_REFERENCE.txt                  Quick reference guide
```

## License

See LICENSE file for details.

## Authors

Leam Hall, Alex Kleider

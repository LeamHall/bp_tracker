# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

bp_tracker.py is a command-line tool for tracking and evaluating blood pressure recordings. It stores blood pressure readings with timestamps and provides analysis including latest readings, averages, and health classifications based on medical ranges.

## Architecture

### Single-File Design
The entire application is contained in bp_tracker.py (approximately 320 lines). Core components:

- Result class: Represents a single BP reading with systolic, diastolic, pulse, and timestamp. Provides date filtering methods (before_date, after_date, in_date_range).
- Health classification system: Two tuples (systolic_labels and diastolic_labels) define medical ranges from "dead" through "good" to "high: crisis". The get_label() and get_labels() functions map readings to these ranges.
- Data persistence: Plain text format in data/bp_numbers.txt with four values per line: systolic diastolic pulse timestamp (format: YYYYmmdd.HHMM). Comments allowed with # prefix.
- Report generation: format_report() produces multi-line output showing latest reading and averages with their health classifications and ranges.

### Key Design Patterns

- The useful_lines() generator filters blank lines and comments when reading the data file.
- Results are stored as Result objects and can be filtered by date range before analysis.
- The application uses argparse for CLI interface with three main operations: default report (all data), add new reading (-a), and date-range report (-r).

## Commands

### Running the Application

```
./bp_tracker.py                                    # Report all readings
./bp_tracker.py -f data/bp_numbers.txt            # Specify data file
./bp_tracker.py -a 120 65 55                      # Add new reading (systolic diastolic pulse)
./bp_tracker.py -r 20230809                       # Report from date to today
./bp_tracker.py -r 20230809 20230824              # Report for date range
```

### Testing

```
make test              # Run unittest with verbose output
python -m unittest discover -s test -p "test_*.py" -v  # Same as make test
python -m unittest test.test_bp_tracker.TestBpTracker.test_average  # Run single test
python -m unittest test.test_bp_tracker  # Run all tests in one file
```

### Code Quality

```
make all               # Clean, test, format with black (79 char line length), coverage report, flake8
make clean             # Remove .pyc and .swp files
python -m black . -l79 # Format code with 79-character line limit
coverage run -m unittest discover -s test -p "test_*.py"  # Generate coverage data
coverage report -m     # Show coverage report with missing lines
flake8                 # Lint code (may fail, prefixed with - in Makefile)
```

## Data Format

The data file (data/bp_numbers.txt) uses space-separated values:
- Line format: systolic diastolic pulse timestamp
- Example: 120 65 55 20220914.1407
- Comments start with #
- Timestamp format: YYYYmmdd.HHMM
- When adding readings via -a, timestamp is auto-generated

## Test Structure

Tests are in test/test_bp_tracker.py using unittest framework. Key test patterns:
- setUp() creates temporary directory and test files
- tearDown() cleans up temporary resources
- Tests use self.good_file (valid test data) and self.bad_file (permission testing)
- File permission testing uses os.chmod(file, 0o000) to create unreadable/unwriteable files

## Commented-Out Features

The code includes commented-out argument parser options for future features:
- -t/--times: Filter readings by time of day span
- -n/--number: Consider only last N readings

These features are partially implemented (time_of_day_filter function exists) but not exposed in the CLI.

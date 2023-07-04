# conftest.py

import os
import pytest


@pytest.fixture
def input_file(tmp_path):
    in_file = os.path.join(tmp_path, "bp_data.txt")
    with open(in_file, "w") as in_f:
        in_f.write("150 80 60 20230404.1000\n")
        in_f.write("160 85 65 20230405.1000\n")
        in_f.write("170 90 70 20230406.1000\n")
    return in_file


@pytest.fixture
def output_file(tmp_path):
    out_file = os.path.join(tmp_path, "bp_data.txt")
    return out_file


@pytest.fixture
def input_args():
    class Args:
        pass

    input_args = Args
    return input_args

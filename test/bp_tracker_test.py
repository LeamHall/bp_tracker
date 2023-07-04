# tests/bp_tracker_tests.py

import bp_tracker as bpt


def test_array_from_file(input_file):
    data = bpt.array_from_file(input_file)
    assert len(data) >= 3


def test_add(output_file, input_args):
    in_args = input_args()
    in_args.file = output_file
    in_args.add = ["150", "80", "60"]
    bpt.add(in_args)
    data = bpt.array_from_file(output_file)
    result = data[0]
    assert len(result) == 4
    assert result[0] == 150
    assert result[1] == 80
    assert result[2] == 60
    assert type(result[3]) is str

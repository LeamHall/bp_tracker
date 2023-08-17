# tests/bp_tracker_tests.py

import bp_tracker as bpt


def test_add(output_file, input_args):
    in_args = input_args()
    in_args.file = output_file
    in_args.add = ["150", "80", "60"]
    bpt.add(in_args)
    data = bpt.results_from_file(output_file)
    result = data[0]
    assert result.systolic == 150
    assert result.diastolic == 80
    assert result.pulse == 60
    assert type(result.timestamp) is str


def test_get_data(input_file):
    data = bpt.get_data(input_file)
    result = data[-1]
    assert result.systolic == 170
    assert result.diastolic == 90
    assert result.pulse == 70
    assert type(result.timestamp) is str


def test_get_data_no_file(output_file):
    data = bpt.get_data("bad_file_name.txt")
    assert data is None


def test_after_date():
    line = "150 80 60 20230404.1234"
    result = bpt.Result(line)
    assert result.after_date(20000101)
    assert not result.after_date(30231231)


def test_before_date():
    line = "150 80 60 20230404.1234"
    result = bpt.Result(line)
    assert result.before_date(20231231)
    assert not result.before_date(20000101)


def test_date_range_single():
    line = "150 80 60 20230404.1234"
    result = bpt.Result(line)
    assert result.in_date_range(20230101, 20231231)
    assert not result.in_date_range(20220101, 20221231)
    assert not result.in_date_range(20230501, 20231231)


def test_get_labels():
    lower, upper, label = bpt.get_labels(70, bpt.systolic_labels)
    assert lower == 70
    assert upper == 85
    assert label == "low"


def test_list_of_attr():
    data = [
        bpt.Result("110 59 68 20220809.1640"),
        bpt.Result("124 62 62 20220810.0840"),
        bpt.Result("134 63 57 20220812.0758"),
        bpt.Result("134 62 57 20220812.1128"),
        bpt.Result("100 59 62 20220812.1323"),
    ]
    expected_sys = [110, 124, 134, 134, 100]
    expected_dia = [59, 62, 63, 62, 59]
    expected_pul = [68, 62, 57, 57, 62]
    assert bpt.list_of_attr(data, "systolic") == expected_sys
    assert bpt.list_of_attr(data, "diastolic") == expected_dia
    assert bpt.list_of_attr(data, "pulse") == expected_pul


def test_make_result():
    line = "150 80 60 20230404.1234"
    result = bpt.Result(line)
    assert result.systolic == 150
    assert result.diastolic == 80
    assert result.pulse == 60
    assert result.timestamp == "20230404.1234"


def test_results_from_file(input_file):
    data = bpt.results_from_file(input_file)
    assert len(data) >= 3


def test_date_range_generator():
    data = [
        bpt.Result("110 59 68 20220809.1640"),
        bpt.Result("124 62 62 20220810.0840"),
        bpt.Result("134 63 57 20220812.0758"),
        bpt.Result("134 62 57 20220812.1128"),
        bpt.Result("100 59 62 20220812.1323"),
    ]
    results = [
        result for result in data if result.in_date_range(20220808, 20220811)
    ]
    assert len(results) == 2
    assert results[0].systolic == 110

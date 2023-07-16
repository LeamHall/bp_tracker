import os
import os.path
import tempfile
import unittest

import bp_tracker


class TestBpTracker(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.good_file = os.path.join(self.test_dir.name, "good_data.txt")
        with open(self.good_file, "w") as f:
            f.write("# A comment, just to keep us honest.\n")
            f.write("120 65 55 20220914.1407\n")
            f.write("120 64 60 20220914.1753\n")
            f.write("140 64 65 20220915.1408\n")
            f.write("140 62 60 20220915.1714\n")
        self.good_data = bp_tracker.results_from_file(self.good_file)
        self.bad_file = os.path.join(self.test_dir.name, "bad_data.txt")
        with open(self.bad_file, "w") as b:
            b.write("This is trash")
        os.chmod(self.bad_file, 0o000)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_average(self):
        self.assertTrue(bp_tracker.average([120, 130, 140]) == 130)
        self.assertTrue(bp_tracker.average([121, 130, 140]) == 130)
        self.assertTrue(bp_tracker.average([123, 130, 140]) == 131)

    def test_bad_file(self):
        self.assertFalse(bp_tracker.check_file(self.bad_file, "w"))
        self.assertFalse(bp_tracker.check_file(self.bad_file, "r"))

    def test_check_file_readable_file(self):
        self.assertTrue(bp_tracker.check_file(self.good_file, "r"))

    def test_check_file_writeable_file(self):
        self.assertTrue(bp_tracker.check_file(self.good_file, "w"))

    def test_check_file_writeable_dir(self):
        test_dir_writeable = os.path.join(self.test_dir.name, "writeable")
        os.mkdir(test_dir_writeable)
        os.chmod(test_dir_writeable, 0o777)
        self.assertTrue(bp_tracker.check_file(self.test_dir.name, "w"))

    def test_check_file_read_missing_file(self):
        test_dir_unwriteable = os.path.join(self.test_dir.name, "unwriteable")
        os.mkdir(test_dir_unwriteable)
        os.chmod(test_dir_unwriteable, 0o000)
        test_file = os.path.join(test_dir_unwriteable, "missing.file")
        self.assertFalse(bp_tracker.check_file(test_file, "w"))

    def test_check_file_write_unwriteable_file(self):
        test_file = os.path.join(self.test_dir.name, "bad_file.txt")
        with open(test_file, "w") as f:
            f.write("bleagh")
        os.chmod(test_file, 0o000)
        self.assertFalse(bp_tracker.check_file(test_file, "w"))

    def test_check_file_write_unwriteable_dir(self):
        test_dir_unwriteable = os.path.join(self.test_dir.name, "unwriteable")
        os.mkdir(test_dir_unwriteable)
        os.chmod(test_dir_unwriteable, 0o00)
        test_file = os.path.join(test_dir_unwriteable, "bad_dir.file")
        self.assertFalse(bp_tracker.check_file(test_file, "w"))

    def test_useful_lines(self):
        self.assertEqual(len(self.good_data), 4)

    def test_results_from_file(self):
        data = (
            "110 59 68 20220809.1640",
            "124 62 62 20220810.0840",
            "134 63 57 20220812.0758",
            "134 62 57 20220812.1128",
            "100 59 62 20220812.1323",
        )
        report_file = os.path.join(self.test_dir.name, "test_write_data.txt")
        with open(report_file, "w") as f:
            for line in data:
                f.write(line + "\n")
        res = bp_tracker.results_from_file(report_file)
        self.assertEqual(5, len(res))
        for element in res:
            self.assertTrue(type(element) is bp_tracker.Result)

    def test_time_of_day_filter(self):
        self.assertEqual(
            bp_tracker.time_of_day_filter(
                (115, 67, 66, "20220914.0800"), "0800", "0900"
            ),
            True,
        )
        self.assertEqual(
            bp_tracker.time_of_day_filter(
                (115, 67, 66, "20220914.0839"), "0800", "0900"
            ),
            True,
        )
        self.assertEqual(
            bp_tracker.time_of_day_filter(
                (115, 67, 66, "20220914.0839"), "0900", "1000"
            ),
            None,
        )
        self.assertEqual(
            bp_tracker.time_of_day_filter(
                (115, 67, 66, "0.0"), "0800", "0900"
            ),
            None,
        )

    def test_get_label(self):
        # Test at lower boundry
        self.assertTrue(
            bp_tracker.get_label(70, bp_tracker.systolic_labels) == "low"
        )
        self.assertTrue(
            bp_tracker.get_label(56, bp_tracker.diastolic_labels) == "low"
        )

        # Test at upper boundry
        self.assertTrue(
            bp_tracker.get_label(179, bp_tracker.systolic_labels)
            == "high: stage 2"
        )
        self.assertTrue(
            bp_tracker.get_label(119, bp_tracker.diastolic_labels)
            == "high: stage 2"
        )

        # Test out of bounds
        self.assertTrue(
            bp_tracker.get_label(-1, bp_tracker.systolic_labels) is None
        )
        self.assertTrue(
            bp_tracker.get_label(301, bp_tracker.diastolic_labels) is None
        )

    def test_format_report(self):
        expected = [
            "Systolic 165 (high: stage 2 [140-179])",
            "Diastolic 89 (high: stage 1 [80-89])",
            "Average 160/88 ",
        ]
        systolics = [155, 165]
        diastolics = [87, 89]
        result = bp_tracker.format_report(systolics, diastolics).split("\n")
        print(result[0])
        print(expected[0])
        self.assertTrue(result[0] == expected[0])
        self.assertTrue(result[1] == expected[1])
        self.assertTrue(result[2] == expected[2])

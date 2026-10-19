import unittest
from simulator import Tag, scan, trial_batch

class RFIDTests(unittest.TestCase):
    def test_all_detected(self):
        result = scan([Tag(f"X{i}", 100, True, 1) for i in range(20)], cycles=1)
        self.assertTrue(result.correct)
        self.assertEqual(result.total_paise, 2000)
    def test_duplicate_reads_count_once(self):
        self.assertEqual(scan([Tag("X", 499, True, 1)], cycles=20).total_paise, 499)
    def test_missing_tag(self):
        self.assertEqual(scan([Tag("X", 100, True, 0)]).missing, {"X"})
    def test_outside_false_inclusion(self):
        r = scan([Tag("X", 100, True, 1), Tag("Y", 200, False)],
                 outside_leak_probability=1)
        self.assertEqual(r.unexpected, {"Y"})
    def test_outside_exclusion(self):
        r = scan([Tag("X", 100, True, 1), Tag("Y", 200, False)],
                 outside_leak_probability=0)
        self.assertTrue(r.correct)
    def test_duplicate_epc_rejected(self):
        with self.assertRaises(ValueError):
            scan([Tag("X", 100), Tag("X", 200)])
    def test_reproducible_batch(self):
        self.assertEqual(trial_batch(trials=100), trial_batch(trials=100))

if __name__ == "__main__":
    unittest.main()

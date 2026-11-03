import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from analyze_frame_times import analyze

class FrameTimingTests(unittest.TestCase):
    def test_stable_sixty(self):
        result = analyze([i / 60 for i in range(121)])
        self.assertAlmostEqual(result['average_fps'], 60)
        self.assertEqual(result['intervals_over_budget'], 0)
        self.assertEqual(result['frames'], 121)

    def test_one_late_frame(self):
        result = analyze([0, 1/60, 2/60, 5/60])
        self.assertEqual(result['intervals_over_budget'], 1)
        self.assertAlmostEqual(result['frame_ms_max'], 50)
        self.assertAlmostEqual(result['average_fps'], 36)

    def test_invalid_values(self):
        for times in ([], [1], [0, 0], [1, 0], [0, math.nan], [0, math.inf]):
            with self.subTest(times=times):
                with self.assertRaises(ValueError): analyze(times)
        for target in (0, -1, math.nan, math.inf):
            with self.subTest(target=target):
                with self.assertRaises(ValueError): analyze([0, 1], target)

if __name__ == '__main__': unittest.main()

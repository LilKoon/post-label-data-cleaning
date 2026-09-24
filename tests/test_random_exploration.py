import unittest

import numpy as np

from explore_random import draw_random_trials


class RandomExplorationTests(unittest.TestCase):
    def test_explicit_seed_reproduces_draws(self):
        errors = np.array([0, 1] * 50, dtype=np.uint8)
        first = draw_random_trials(errors, budget=5, runs=3, seed=12)
        second = draw_random_trials(errors, budget=5, runs=3, seed=12)
        self.assertEqual(first, second)

    def test_different_seeds_select_different_rows(self):
        errors = np.array([0, 1] * 50, dtype=np.uint8)
        first = draw_random_trials(errors, budget=5, runs=3, seed=12)
        second = draw_random_trials(errors, budget=5, runs=3, seed=13)
        self.assertNotEqual(first[0]["selected_rows"], second[0]["selected_rows"])


if __name__ == "__main__":
    unittest.main()

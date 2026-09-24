import unittest

import numpy as np

from make_scenario_demo import scenario_record


class ScenarioDemoTests(unittest.TestCase):
    def setUp(self):
        self.labels = np.repeat(np.arange(10, dtype=np.uint8), 200)
        self.probabilities = np.full((2000, 10), 0.025, dtype=np.float32)
        self.probabilities[np.arange(2000), self.labels] = 0.775

    def test_same_seeds_reproduce_both_queues(self):
        first = scenario_record(self.labels, self.probabilities, noise_seed=2000, random_seed=5000)
        again = scenario_record(self.labels, self.probabilities, noise_seed=2000, random_seed=5000)
        self.assertEqual(first, again)
        self.assertEqual(sum(kind != 0 for kind in first["error_types"]), 200)
        self.assertEqual(len(first["model_rows"]), 100)
        self.assertEqual(len(set(first["model_rows"])), 100)
        self.assertEqual(len(first["random_rows"]), 100)
        self.assertEqual(len(set(first["random_rows"])), 100)

    def test_new_seed_changes_noisy_labels_without_changing_budget(self):
        first = scenario_record(self.labels, self.probabilities, noise_seed=2000, random_seed=5000)
        second = scenario_record(self.labels, self.probabilities, noise_seed=2001, random_seed=5001)
        self.assertNotEqual(first["current_labels"], second["current_labels"])
        self.assertEqual(first["model_metrics"]["total_errors"], 200)
        self.assertEqual(second["model_metrics"]["total_errors"], 200)
        self.assertEqual(first["model_metrics"]["reviewed"], second["random_metrics"]["reviewed"])


if __name__ == "__main__":
    unittest.main()

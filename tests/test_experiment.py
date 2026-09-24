import unittest

import numpy as np

from experiment import inject_noise, evaluate_top_k, rank_suspicion


class ExperimentTests(unittest.TestCase):
    def test_noise_types_are_disjoint_and_labels_change(self):
        labels = np.tile(np.arange(10, dtype=np.uint8), 100)
        noisy, error_type, batch_id = inject_noise(labels, seed=7, rate=0.10)

        self.assertEqual(len(labels), len(noisy))
        self.assertEqual(np.count_nonzero(error_type == 1), 40)
        self.assertEqual(np.count_nonzero(error_type == 2), 40)
        self.assertEqual(np.count_nonzero(error_type == 3), 20)
        np.testing.assert_array_equal(labels != noisy, error_type != 0)
        self.assertEqual(len(batch_id), len(labels))

    def test_evaluation_uses_exact_budget_and_true_error_count(self):
        error_type = np.array([0, 1, 2, 3, 0, 1, 0, 0, 0, 0])
        ranking = np.array([3, 1, 0, 2, 4, 5, 6, 7, 8, 9])
        result = evaluate_top_k(ranking, error_type, budget_count=2)

        self.assertEqual(result["reviewed"], 2)
        self.assertEqual(result["errors_found"], 2)
        self.assertEqual(result["total_errors"], 4)
        self.assertEqual(result["error_recall"], 0.5)
        self.assertEqual(result["precision"], 1.0)
        self.assertEqual(result["found_by_type"], {"random": 1, "systematic": 0, "batch": 1})

    def test_ranking_is_stable_for_ties(self):
        scores = np.array([0.4, 0.9, 0.9, 0.1])
        np.testing.assert_array_equal(rank_suspicion(scores), np.array([1, 2, 0, 3]))


if __name__ == "__main__":
    unittest.main()

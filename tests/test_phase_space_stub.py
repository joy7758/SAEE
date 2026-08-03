import unittest
from public_abstraction.abstraction_layer.phase_space_stub import summarize_phase_space

class PhaseSpaceStubTest(unittest.TestCase):
    def test_empty_input(self) -> None:
        result = summarize_phase_space([])
        self.assertEqual(result, {"regime": "unobserved", "basin": "unobserved", "count": 0})

    def test_stable_majority(self) -> None:
        rows = [
            {"stability_proxy": 0.8},
            {"stability_proxy": 0.6},
            {"stability_proxy": 0.1},
        ]
        result = summarize_phase_space(rows)
        self.assertEqual(result, {"regime": "stable_regime", "basin": "stable_lineage_basin", "count": 3})

    def test_exploratory_majority(self) -> None:
        rows = [
            {"stability_proxy": 0.1},
            {"stability_proxy": 0.2},
            {"stability_proxy": 0.3},
        ]
        result = summarize_phase_space(rows)
        self.assertEqual(result, {"regime": "exploratory_regime", "basin": "exploration_basin", "count": 3})

    def test_exact_half_stable(self) -> None:
        rows = [
            {"stability_proxy": 0.7},
            {"stability_proxy": 0.2},
        ]
        result = summarize_phase_space(rows)
        self.assertEqual(result, {"regime": "stable_regime", "basin": "stable_lineage_basin", "count": 2})

if __name__ == "__main__":
    unittest.main()

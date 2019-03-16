import unittest

from gamebuilder import PlayerSpecification


class PlayerSpecificationTest(unittest.TestCase):

    def test_pure_strategies(self):
        player_specification = PlayerSpecification(player_types=[1, 2], player_actions=["U", "D"])
        expected_strategies = {("U", "U"), ("U", "D"), ("D", "U"), ("D", "D")};
        actual_strategies = set()
        for pure_strategy in player_specification.get_pure_strategies():
            actual_strategies.add(pure_strategy)

        self.assertEqual(actual_strategies, expected_strategies)

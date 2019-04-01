import unittest
from fractions import Fraction

from auctions import FirstPriceAuction, GnuthPlayerSpecification


class GnuthAuctionTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(GnuthAuctionTest, self).__init__(*args, **kwargs)
        player_specification = GnuthPlayerSpecification(player_valuations=[50, 51, 52])
        opponent_specification = GnuthPlayerSpecification(player_valuations=[50, 51])

        self.sample_auction = FirstPriceAuction(game_name="toy_auction", player_specification=player_specification,
                                                opponent_specification=opponent_specification)

    def test_no_jumpy_strategies(self):
        player_specification = GnuthPlayerSpecification(player_valuations=[50, 51, 52, 53])
        opponent_specification = GnuthPlayerSpecification(player_valuations=[50, 51, 52])
        another_auction = FirstPriceAuction(game_name="another_toy_auction", player_specification=player_specification,
                                            opponent_specification=opponent_specification)

        expected_player_strategies = [(50, 50, 50, 50), (50, 50, 50, 51), (50, 50, 51, 51), (50, 50, 51, 52),
                                      (50, 51, 51, 51), (50, 51, 51, 52), (50, 51, 52, 52), (50, 51, 52, 53)]
        actual_player_strategies = another_auction.player_specification.get_pure_strategies()

        self.assertEqual(sorted(actual_player_strategies), sorted(expected_player_strategies))

        expected_oponent_strategies = [(50, 50, 50), (50, 50, 51), (50, 51, 51), (50, 51, 52)]
        actual_opponent_strategies = another_auction.opponent_specification.get_pure_strategies()
        self.assertEqual(sorted(actual_opponent_strategies), sorted(expected_oponent_strategies))

    def test_pure_strategies(self):
        expected_strategies = [(50, 50, 50), (50, 50, 51), (50, 51, 51), (50, 51, 52)]
        actual_strategies = list(self.sample_auction.player_specification.get_pure_strategies())
        self.assertEqual(actual_strategies, expected_strategies)

        expected_strategies = [(50, 50), (50, 51)]
        actual_strategies = list(self.sample_auction.opponent_specification.get_pure_strategies())
        self.assertEqual(actual_strategies, expected_strategies)

    def test_auction_utilities(self):
        expected_strong_utility = Fraction(1, 2)
        expected_weak_utility = Fraction(1, 4)
        strong_bidder_strategy = (50, 50, 50)
        weak_bidder_strategy = (50, 50)

        actual_strong_utility, actual_weak_utility = self.sample_auction.get_expected_utilities(
            (strong_bidder_strategy, weak_bidder_strategy))

        self.assertAlmostEqual(actual_strong_utility, expected_strong_utility)
        self.assertAlmostEqual(actual_weak_utility, expected_weak_utility)

        expected_strong_utility = Fraction(1 / 12)
        expected_weak_utility = 0
        strong_bidder_strategy = (50, 50, 52)
        weak_bidder_strategy = (50, 51)

        actual_strong_utility, actual_weak_utility = self.sample_auction.get_expected_utilities(
            (strong_bidder_strategy, weak_bidder_strategy))

        self.assertAlmostEqual(actual_strong_utility, expected_strong_utility)
        self.assertAlmostEqual(actual_weak_utility, expected_weak_utility)

    def test_calculate_equilibria(self):
        actual_equilibria = self.sample_auction.calculate_equilibria()
        self.assertEqual(len(actual_equilibria), 2)

        for equilibrium in actual_equilibria:
            weak_bidder_strategy = self.sample_auction.opponent_specification.get_strategy_index((50, 50))
            weak_bidder_index = 1
            self.assertEqual(equilibrium[(weak_bidder_index, weak_bidder_strategy)], "1")

            strong_bidder_index = 0
            strong_bidder_strategy = self.sample_auction.player_specification.get_strategy_index((50, 50, 50))
            other_strong_bidder_strategy = self.sample_auction.player_specification.get_strategy_index((50, 50, 51))

            strong_equilibrium = equilibrium[(strong_bidder_index, strong_bidder_strategy)] == "1" or equilibrium[
                (strong_bidder_index, other_strong_bidder_strategy)] == "1"
            self.assertTrue(strong_equilibrium)

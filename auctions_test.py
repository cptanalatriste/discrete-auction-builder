import unittest
from fractions import Fraction

from auctions import FirstPriceAuction


class FirstPriceAuctionTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FirstPriceAuctionTest, self).__init__(*args, **kwargs)
        self.sample_auction = FirstPriceAuction(game_name="toy_auction", player_valuations=[0, 1, 2],
                                                opponent_valuations=[0, 1])

    def test_pure_strategies(self):
        expected_strategies = {(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 0), (0, 1, 1), (0, 1, 2)}
        actual_strategies = self.sample_auction.player_specification.get_pure_strategies()
        self.assertEqual(actual_strategies, expected_strategies)

        expected_strategies = {(0, 0), (0, 1)}
        actual_strategies = self.sample_auction.opponent_specification.get_pure_strategies()
        self.assertEqual(actual_strategies, expected_strategies)

    def test_auction_utilities(self):
        expected_strong_utility = Fraction(1, 2)
        expected_weak_utility = Fraction(1, 4)
        strong_bidder_strategy = (0, 0, 0)
        weak_bidder_strategy = (0, 0)

        actual_strong_utility, actual_weak_utility = self.sample_auction.get_expected_utilities(
            (strong_bidder_strategy, weak_bidder_strategy))

        self.assertAlmostEqual(actual_strong_utility, expected_strong_utility)
        self.assertAlmostEqual(actual_weak_utility, expected_weak_utility)

        expected_strong_utility = Fraction(1 / 12)
        expected_weak_utility = 0
        strong_bidder_strategy = (0, 0, 2)
        weak_bidder_strategy = (0, 1)

        actual_strong_utility, actual_weak_utility = self.sample_auction.get_expected_utilities(
            (strong_bidder_strategy, weak_bidder_strategy))

        self.assertAlmostEqual(actual_strong_utility, expected_strong_utility)
        self.assertAlmostEqual(actual_weak_utility, expected_weak_utility)

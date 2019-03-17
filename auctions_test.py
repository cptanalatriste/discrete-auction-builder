import unittest

from auctions import FirstPriceAuction


class FirstPriceAuctionTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FirstPriceAuctionTest, self).__init__(*args, **kwargs)
        self.sample_auction = FirstPriceAuction(game_name="toy_auction", player_valuations=[0.0, 1.0, 2.0],
                                                opponent_valuations=[0.0, 1.0])

    def test_auction_utilities(self):
        expected_strong_utility = 0.5
        expected_weak_utility = 0.25
        strong_bidder_strategy = (0.0, 0.0, 0.0)
        weak_bidder_strategy = (0.0, 0.0)

        actual_strong_utility, actual_weak_utility = self.sample_auction.get_expected_utilities(
            (strong_bidder_strategy, weak_bidder_strategy))

        self.assertAlmostEqual(actual_strong_utility, expected_strong_utility)
        self.assertAlmostEqual(actual_weak_utility, expected_weak_utility)

        expected_strong_utility = 1.0 / 12
        expected_weak_utility = 0.0
        strong_bidder_strategy = (0.0, 0.0, 2.0)
        weak_bidder_strategy = (0.0, 1.0)

        actual_strong_utility, actual_weak_utility = self.sample_auction.get_expected_utilities(
            (strong_bidder_strategy, weak_bidder_strategy))

        self.assertAlmostEqual(actual_strong_utility, expected_strong_utility)
        self.assertAlmostEqual(actual_weak_utility, expected_weak_utility)

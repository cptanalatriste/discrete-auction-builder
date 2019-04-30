import unittest
from fractions import Fraction

from auctions import FirstPriceAuction, GnuthPlayerSpecification, PezanisAuction, AuctionPlayerSpecification


class GnuthAuctionTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(GnuthAuctionTest, self).__init__(*args, **kwargs)
        player_specification = GnuthPlayerSpecification(player_valuations=[50, 51, 52])
        opponent_specification = GnuthPlayerSpecification(player_valuations=[50, 51])

        self.sample_auction = FirstPriceAuction(game_name="gnuth_auction", player_specification=player_specification,
                                                opponent_specification=opponent_specification)

    def test_no_jumpy_strategies(self):
        player_specification = GnuthPlayerSpecification(player_valuations=[50, 51, 52, 53])
        opponent_specification = GnuthPlayerSpecification(player_valuations=[50, 51, 52])
        another_auction = FirstPriceAuction(game_name="another_gnuth_auction",
                                            player_specification=player_specification,
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


class AllPayAuctionTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(AllPayAuctionTest, self).__init__(*args, **kwargs)

        player_valuations = [0, 1, 2]
        self.player_specification = AuctionPlayerSpecification(player_actions=player_valuations,
                                                               player_types=player_valuations, no_jumps=False)
        self.opponent_specification = AuctionPlayerSpecification(player_actions=player_valuations,
                                                                 player_types=player_valuations, no_jumps=False)

        self.sample_auction = FirstPriceAuction(game_name="allpay_auction",
                                                player_specification=self.player_specification,
                                                opponent_specification=self.opponent_specification, all_pay=True,
                                                no_ties=False)

    def test_pure_strategies(self):
        expected_strategies = [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 1), (0, 1, 2)]
        player_strategies = list(self.sample_auction.player_specification.get_pure_strategies())
        self.assertEqual(sorted(expected_strategies), sorted(player_strategies))

        opponent_strategies = list(self.sample_auction.opponent_specification.get_pure_strategies())
        self.assertEqual(sorted(opponent_strategies), sorted(player_strategies))

    def test_auction_utilities(self):
        expected_player_utility = Fraction(1, 2)
        expected_opponent_utility = Fraction(1, 2)
        player_strategy = (0, 0, 0)
        opponent_strategy = (0, 0, 0)

        actual_player_utility, actual_opponent_utility = self.sample_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        expected_player_utility = Fraction(1, 18)
        expected_opponent_utility = Fraction(-1, 18)
        player_strategy = (0, 0, 1)
        opponent_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility = self.sample_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        expected_player_utility = Fraction(1, 9)
        expected_opponent_utility = Fraction(2, 9)
        player_strategy = (0, 0, 2)
        opponent_strategy = (0, 0, 1)

        actual_player_utility, actual_opponent_utility = self.sample_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        expected_player_utility = Fraction(-5, 18)
        expected_opponent_utility = Fraction(-5, 18)
        player_strategy = (0, 1, 2)
        opponent_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility = self.sample_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

    def test_noties_utilities(self):
        another_sample_auction = FirstPriceAuction(game_name="noties_auction",
                                                   player_specification=self.player_specification,
                                                   opponent_specification=self.opponent_specification, all_pay=True,
                                                   no_ties=True)

        expected_player_utility = 0
        expected_opponent_utility = 0
        player_strategy = (0, 0, 0)
        opponent_strategy = (0, 0, 0)

        actual_player_utility, actual_opponent_utility = another_sample_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        # expected_player_utility = Fraction(-1, 9)
        # expected_opponent_utility = Fraction(-1, 9)
        # player_strategy = (0, 0, 1)
        # opponent_strategy = (0, 1, 2)
        #
        # actual_player_utility, actual_opponent_utility = self.sample_auction.get_expected_utilities(
        #     (player_strategy, opponent_strategy))
        # self.assertEqual(actual_player_utility, expected_player_utility)
        # self.assertEqual(actual_opponent_utility, expected_opponent_utility)


class PezanisAuctionTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(PezanisAuctionTest, self).__init__(*args, **kwargs)

        self.sample_auction = PezanisAuction(game_name="pezanis_auction", player_valuations=[0, 1, 2],
                                             opponent_valuations=[-6, -5, -4, -3, -2, -1, 0, 1, 2])

    def test_no_jumpy_strategies(self):
        another_sample_auction = PezanisAuction(game_name="pezanis_auction", player_valuations=[0, 1, 2],
                                                opponent_valuations=[-6, -5, -4, -3, -2, -1, 0, 1, 2],
                                                no_jumps=True)

        expected_strategies = [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 2)]
        player_strategies = list(another_sample_auction.player_specification.get_pure_strategies())
        self.assertEqual(sorted(expected_strategies), sorted(player_strategies))

        opponent_strategies = list(another_sample_auction.opponent_specification.get_pure_strategies())
        self.assertEqual(sorted(opponent_strategies), sorted(player_strategies))

    def test_auction_utilities(self):
        expected_strong_utility = Fraction(5, 6)
        expected_weak_utility = Fraction(1, 6)
        strong_bidder_strategy = (0, 0, 0)
        weak_bidder_strategy = (0, 0, 0)

        actual_strong_utility, actual_weak_utility = self.sample_auction.get_expected_utilities(
            (strong_bidder_strategy, weak_bidder_strategy))

        self.assertEqual(actual_strong_utility, expected_strong_utility)
        self.assertEqual(actual_weak_utility, expected_weak_utility)

        expected_strong_utility = Fraction(5, 18)
        expected_weak_utility = Fraction(0, 1)
        strong_bidder_strategy = (0, 1, 1)
        weak_bidder_strategy = (0, 1, 2)

        actual_strong_utility, actual_weak_utility = self.sample_auction.get_expected_utilities(
            (strong_bidder_strategy, weak_bidder_strategy))

        self.assertAlmostEqual(actual_strong_utility, expected_strong_utility)
        self.assertAlmostEqual(actual_weak_utility, expected_weak_utility)

        expected_strong_utility = Fraction(13, 54)
        expected_weak_utility = Fraction(2, 27)
        strong_bidder_strategy = (0, 0, 2)
        weak_bidder_strategy = (0, 1, 1)

        actual_strong_utility, actual_weak_utility = self.sample_auction.get_expected_utilities(
            (strong_bidder_strategy, weak_bidder_strategy))

        self.assertAlmostEqual(actual_strong_utility, expected_strong_utility)
        self.assertAlmostEqual(actual_weak_utility, expected_weak_utility)

    def test_pure_strategies(self):
        expected_strategies = [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 1), (0, 1, 2)]
        player_strategies = list(self.sample_auction.player_specification.get_pure_strategies())
        self.assertEqual(sorted(expected_strategies), sorted(player_strategies))

        opponent_strategies = list(self.sample_auction.opponent_specification.get_pure_strategies())
        self.assertEqual(sorted(opponent_strategies), sorted(player_strategies))

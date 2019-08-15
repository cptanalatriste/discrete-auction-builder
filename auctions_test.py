import unittest
from fractions import Fraction

from auctions import FirstPriceAuction, GnuthPlayerSpecification, PezanisAuction, AuctionPlayerSpecification


class GnuthAuctionTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(GnuthAuctionTest, self).__init__(*args, **kwargs)
        self.player_specification = GnuthPlayerSpecification(player_valuations=[50, 51, 52])
        self.opponent_specification = GnuthPlayerSpecification(player_valuations=[50, 51])

        self.sample_auction = FirstPriceAuction(game_name="gnuth_auction",
                                                player_specifications=[self.player_specification,
                                                                       self.opponent_specification])

    def test_no_jumpy_strategies(self):
        another_player_specification = GnuthPlayerSpecification(player_valuations=[50, 51, 52, 53])
        another_opponent_specification = GnuthPlayerSpecification(player_valuations=[50, 51, 52])

        expected_player_strategies = [(50, 50, 50, 50), (50, 50, 50, 51), (50, 50, 51, 51), (50, 50, 51, 52),
                                      (50, 51, 51, 51), (50, 51, 51, 52), (50, 51, 52, 52), (50, 51, 52, 53)]
        actual_player_strategies = another_player_specification.get_pure_strategies()

        self.assertEqual(sorted(actual_player_strategies), sorted(expected_player_strategies))

        expected_oponent_strategies = [(50, 50, 50), (50, 50, 51), (50, 51, 51), (50, 51, 52)]
        actual_opponent_strategies = another_opponent_specification.get_pure_strategies()
        self.assertEqual(sorted(actual_opponent_strategies), sorted(expected_oponent_strategies))

    def test_pure_strategies(self):
        expected_strategies = [(50, 50, 50), (50, 50, 51), (50, 51, 51), (50, 51, 52)]
        actual_strategies = list(self.player_specification.get_pure_strategies())
        self.assertEqual(actual_strategies, expected_strategies)

        expected_strategies = [(50, 50), (50, 51)]
        actual_strategies = list(self.opponent_specification.get_pure_strategies())
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
        actual_equilibria = self.sample_auction.calculate_equilibria(only_pure=True)
        self.assertEqual(len(actual_equilibria), 2)

        for equilibrium in actual_equilibria:
            weak_bidder_strategy = self.opponent_specification.get_strategy_index((50, 50))
            weak_bidder_index = 1
            self.assertEqual(equilibrium[(weak_bidder_index, weak_bidder_strategy)], "1")

            strong_bidder_index = 0
            strong_bidder_strategy = self.player_specification.get_strategy_index((50, 50, 50))
            other_strong_bidder_strategy = self.player_specification.get_strategy_index((50, 50, 51))

            strong_equilibrium = equilibrium[(strong_bidder_index, strong_bidder_strategy)] == "1" or equilibrium[
                (strong_bidder_index, other_strong_bidder_strategy)] == "1"
            self.assertTrue(strong_equilibrium)


class FirstPriceThreeBiddersTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FirstPriceThreeBiddersTest, self).__init__(*args, **kwargs)

        player_valuations = [0, 1, 2]
        self.player_specification = AuctionPlayerSpecification(player_actions=player_valuations,
                                                               player_types=player_valuations, no_jumps=False)
        self.opponent_specification = AuctionPlayerSpecification.from_specification(self.player_specification)
        self.third_player_specification = AuctionPlayerSpecification.from_specification(self.player_specification)

        self.auction_no_ties = FirstPriceAuction(game_name="3-bidders-no-ties",
                                                 player_specifications=[self.player_specification,
                                                                        self.opponent_specification,
                                                                        self.third_player_specification], all_pay=False,
                                                 no_ties=True)

        self.auction_with_ties = FirstPriceAuction(game_name="3-bidders-with-ties",
                                                   player_specifications=[self.player_specification,
                                                                          self.opponent_specification,
                                                                          self.third_player_specification],
                                                   all_pay=False,
                                                   no_ties=False)
        self.allpay_with_ties = FirstPriceAuction(game_name="3-bidders-allpay-ties",
                                                  player_specifications=[self.player_specification,
                                                                         self.opponent_specification,
                                                                         self.third_player_specification],
                                                  all_pay=True,
                                                  no_ties=False)

    def test_allpay_ties_auction(self):
        expected_player_utility = Fraction(1, 3)
        expected_opponent_utility = Fraction(1, 3)
        expected_tnird_utility = Fraction(1, 3)
        player_strategy = (0, 0, 0)
        opponent_strategy = (0, 0, 0)
        third_strategy = (0, 0, 0)

        actual_player_utility, actual_opponent_utility, actual_third_utility = self.allpay_with_ties.get_expected_utilities(
            (player_strategy, opponent_strategy, third_strategy))

        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)
        self.assertEqual(actual_third_utility, expected_tnird_utility)

        expected_player_utility = Fraction(-11, 27)
        expected_opponent_utility = Fraction(-53, 162)
        expected_tnird_utility = Fraction(-53, 162)
        player_strategy = (0, 1, 1)
        opponent_strategy = (0, 1, 2)
        third_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility, actual_third_utility = self.allpay_with_ties.get_expected_utilities(
            (player_strategy, opponent_strategy, third_strategy))

        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)
        self.assertEqual(actual_third_utility, expected_tnird_utility)

        expected_player_utility = Fraction(-7, 81)
        expected_opponent_utility = Fraction(-7, 81)
        expected_tnird_utility = Fraction(-7 / 27)
        player_strategy = (0, 0, 1)
        opponent_strategy = (0, 0, 2)
        third_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility, actual_third_utility = self.allpay_with_ties.get_expected_utilities(
            (player_strategy, opponent_strategy, third_strategy))

        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        # Temporary workaround, due to Excel fraction rounding
        # self.assertEqual(actual_third_utility, expected_tnird_utility)
        self.assertAlmostEqual(actual_third_utility, expected_tnird_utility)


    def test_withties_auction(self):
        expected_player_utility = Fraction(1, 3)
        expected_opponent_utility = Fraction(1, 3)
        expected_tnird_utility = Fraction(1, 3)
        player_strategy = (0, 0, 0)
        opponent_strategy = (0, 0, 0)
        third_strategy = (0, 0, 0)

        actual_player_utility, actual_opponent_utility, actual_third_utility = self.auction_with_ties.get_expected_utilities(
            (player_strategy, opponent_strategy, third_strategy))

        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)
        self.assertEqual(actual_third_utility, expected_tnird_utility)

        expected_player_utility = Fraction(7, 81)
        expected_opponent_utility = Fraction(0)
        expected_tnird_utility = Fraction(0)
        player_strategy = (0, 1, 1)
        opponent_strategy = (0, 1, 2)
        third_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility, actual_third_utility = self.auction_with_ties.get_expected_utilities(
            (player_strategy, opponent_strategy, third_strategy))

        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)
        self.assertEqual(actual_third_utility, expected_tnird_utility)

        expected_player_utility = Fraction(11, 81)
        expected_opponent_utility = Fraction(2, 81)
        expected_tnird_utility = Fraction(0)
        player_strategy = (0, 0, 1)
        opponent_strategy = (0, 0, 2)
        third_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility, actual_third_utility = self.auction_with_ties.get_expected_utilities(
            (player_strategy, opponent_strategy, third_strategy))

        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)
        self.assertEqual(actual_third_utility, expected_tnird_utility)

    def test_noties_auction(self):
        expected_player_utility = Fraction(0)
        expected_opponent_utility = Fraction(0)
        expected_tnird_utility = Fraction(0)
        player_strategy = (0, 0, 0)
        opponent_strategy = (0, 0, 0)
        third_strategy = (0, 0, 0)

        actual_player_utility, actual_opponent_utility, actual_third_utility = self.auction_no_ties.get_expected_utilities(
            (player_strategy, opponent_strategy, third_strategy))

        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)
        self.assertEqual(actual_third_utility, expected_tnird_utility)

        expected_player_utility = Fraction(1, 27)
        expected_opponent_utility = Fraction(0)
        expected_tnird_utility = Fraction(0)
        player_strategy = (0, 1, 1)
        opponent_strategy = (0, 1, 2)
        third_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility, actual_third_utility = self.auction_no_ties.get_expected_utilities(
            (player_strategy, opponent_strategy, third_strategy))

        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)
        self.assertEqual(actual_third_utility, expected_tnird_utility)

        expected_player_utility = Fraction(2, 27)
        expected_opponent_utility = Fraction(0)
        expected_tnird_utility = Fraction(0)
        player_strategy = (0, 0, 1)
        opponent_strategy = (0, 0, 2)
        third_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility, actual_third_utility = self.auction_no_ties.get_expected_utilities(
            (player_strategy, opponent_strategy, third_strategy))

        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)
        self.assertEqual(actual_third_utility, expected_tnird_utility)


class FirstPriceAuctionTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FirstPriceAuctionTest, self).__init__(*args, **kwargs)

        player_valuations = [0, 1, 2]
        self.player_specification = AuctionPlayerSpecification(player_actions=player_valuations,
                                                               player_types=player_valuations, no_jumps=False)
        self.opponent_specification = AuctionPlayerSpecification.from_specification(self.player_specification)

        self.all_pay_auction = FirstPriceAuction(game_name="allpay_auction",
                                                 player_specifications=[self.player_specification,
                                                                        self.opponent_specification], all_pay=True,
                                                 no_ties=False)

        self.first_price_auction = FirstPriceAuction(game_name="first_price_auction",
                                                     player_specifications=[self.player_specification,
                                                                            self.opponent_specification], all_pay=False,
                                                     no_ties=False)

    def test_pure_strategies(self):
        expected_strategies = [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 1), (0, 1, 2)]
        player_strategies = list(self.player_specification.get_pure_strategies())
        self.assertEqual(sorted(expected_strategies), sorted(player_strategies))

        opponent_strategies = list(self.opponent_specification.get_pure_strategies())
        self.assertEqual(sorted(opponent_strategies), sorted(player_strategies))

    def test_first_price_utilities(self):
        expected_player_utility = Fraction(1, 2)
        expected_opponent_utility = Fraction(1, 2)
        player_strategy = (0, 0, 0)
        opponent_strategy = (0, 0, 0)

        actual_player_utility, actual_opponent_utility = self.first_price_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        expected_player_utility = Fraction(2, 9)
        expected_opponent_utility = Fraction(0)
        player_strategy = (0, 0, 1)
        opponent_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility = self.first_price_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        expected_player_utility = Fraction(1, 9)
        expected_opponent_utility = Fraction(1, 3)
        player_strategy = (0, 0, 2)
        opponent_strategy = (0, 0, 1)

        actual_player_utility, actual_opponent_utility = self.first_price_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        expected_player_utility = Fraction(0)
        expected_opponent_utility = Fraction(0)
        player_strategy = (0, 1, 2)
        opponent_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility = self.first_price_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

    def test_all_pay_utilities(self):
        expected_player_utility = Fraction(1, 2)
        expected_opponent_utility = Fraction(1, 2)
        player_strategy = (0, 0, 0)
        opponent_strategy = (0, 0, 0)

        actual_player_utility, actual_opponent_utility = self.all_pay_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        expected_player_utility = Fraction(1, 18)
        expected_opponent_utility = Fraction(-1, 18)
        player_strategy = (0, 0, 1)
        opponent_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility = self.all_pay_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        expected_player_utility = Fraction(1, 9)
        expected_opponent_utility = Fraction(2, 9)
        player_strategy = (0, 0, 2)
        opponent_strategy = (0, 0, 1)

        actual_player_utility, actual_opponent_utility = self.all_pay_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        expected_player_utility = Fraction(-5, 18)
        expected_opponent_utility = Fraction(-5, 18)
        player_strategy = (0, 1, 2)
        opponent_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility = self.all_pay_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

    def test_noties_utilities(self):
        another_sample_auction = FirstPriceAuction(game_name="noties_auction",
                                                   player_specifications=[self.player_specification,
                                                                          self.opponent_specification], all_pay=True,
                                                   no_ties=True)

        expected_player_utility = 0
        expected_opponent_utility = 0
        player_strategy = (0, 0, 0)
        opponent_strategy = (0, 0, 0)

        actual_player_utility, actual_opponent_utility = another_sample_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        expected_player_utility = Fraction(-1, 9)
        expected_opponent_utility = Fraction(-1, 9)
        player_strategy = (0, 0, 1)
        opponent_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility = another_sample_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        expected_player_utility = 0
        expected_opponent_utility = Fraction(1, 9)
        player_strategy = (0, 0, 2)
        opponent_strategy = (0, 0, 1)

        actual_player_utility, actual_opponent_utility = another_sample_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)

        expected_player_utility = Fraction(-4, 9)
        expected_opponent_utility = Fraction(-4, 9)
        player_strategy = (0, 1, 2)
        opponent_strategy = (0, 1, 2)

        actual_player_utility, actual_opponent_utility = another_sample_auction.get_expected_utilities(
            (player_strategy, opponent_strategy))
        self.assertEqual(actual_player_utility, expected_player_utility)
        self.assertEqual(actual_opponent_utility, expected_opponent_utility)


class PezanisAuctionTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(PezanisAuctionTest, self).__init__(*args, **kwargs)

        self.sample_auction = PezanisAuction(game_name="pezanis_auction", player_valuations=[[0, 1, 2],
                                                                                             [-6, -5, -4, -3, -2, -1, 0,
                                                                                              1, 2]])
        self.player_specification = self.sample_auction.player_specifications[0]
        self.opponent_specification = self.sample_auction.player_specifications[1]

    def test_no_jumpy_strategies(self):
        another_sample_auction = PezanisAuction(game_name="pezanis_auction", player_valuations=[[0, 1, 2],
                                                                                                [-6, -5, -4, -3, -2, -1,
                                                                                                 0, 1, 2]],
                                                no_jumps=True)

        expected_strategies = [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 2)]
        player_strategies = list(another_sample_auction.player_specifications[0].get_pure_strategies())
        self.assertEqual(sorted(expected_strategies), sorted(player_strategies))

        opponent_strategies = list(another_sample_auction.player_specifications[1].get_pure_strategies())
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
        player_strategies = list(self.player_specification.get_pure_strategies())
        self.assertEqual(sorted(expected_strategies), sorted(player_strategies))

        opponent_strategies = list(self.opponent_specification.get_pure_strategies())
        self.assertEqual(sorted(opponent_strategies), sorted(player_strategies))

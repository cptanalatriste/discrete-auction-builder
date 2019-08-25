import logging
import time

from auctions import GnuthPlayerSpecification, FirstPriceAuction, PezanisAuction, AuctionPlayerSpecification


class FivePlayerSpecification(AuctionPlayerSpecification):
    player_valuations = range(0, 5)

    def __init__(self, no_jumps):
        super(FivePlayerSpecification, self).__init__(player_types=FivePlayerSpecification.player_valuations,
                                                      player_actions=FivePlayerSpecification.player_valuations,
                                                      no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = max(valuation - 1, 0)

        return min_bid, max_bid


class WeaklyIncreasing6PlayerSpecification(AuctionPlayerSpecification):
    player_valuations = range(0, 6)

    def __init__(self, no_jumps):
        super(WeaklyIncreasing6PlayerSpecification, self).__init__(
            player_types=SixPlayerSpecification.player_valuations,
            player_actions=SixPlayerSpecification.player_valuations,
            no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = max(valuation - 1, 0)

        return min_bid, max_bid


class SevenPlayerSpecification(AuctionPlayerSpecification):
    player_valuations = range(0, 7)

    def __init__(self, no_jumps):
        super(SevenPlayerSpecification, self).__init__(player_types=SevenPlayerSpecification.player_valuations,
                                                       player_actions=SevenPlayerSpecification.player_valuations,
                                                       no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = max(valuation - 1, 0)

        if valuation >= 2 and min_bid == 0:
            min_bid = 1

        return min_bid, max_bid


class SixPlayerSpecification(AuctionPlayerSpecification):
    player_valuations = range(0, 6)

    def __init__(self, no_jumps):
        super(SixPlayerSpecification, self).__init__(player_types=SixPlayerSpecification.player_valuations,
                                                     player_actions=SixPlayerSpecification.player_valuations,
                                                     no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = max(valuation - 1, 0)

        if valuation >= 2 and min_bid == 0:
            min_bid = 1

        return min_bid, max_bid


class ElevenPlayerSpecification(AuctionPlayerSpecification):
    player_valuations = range(0, 11)

    def __init__(self, no_jumps):

        super(ElevenPlayerSpecification, self).__init__(player_types=ElevenPlayerSpecification.player_valuations,
                                                        player_actions=ElevenPlayerSpecification.player_valuations,
                                                        no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = min(valuation - 1, 6)

        if valuation >= 3 and min_bid == 0:
            min_bid = 1

        if valuation == 5:
            max_bid = 3
        elif valuation == 6:
            max_bid = 4
        elif 7 <= valuation <= 8:
            max_bid = 5

        return min_bid, max_bid


class ThirteenPlayerSpecification(AuctionPlayerSpecification):
    player_valuations = range(0, 13)

    def __init__(self, no_jumps):

        super(ThirteenPlayerSpecification, self).__init__(player_types=ThirteenPlayerSpecification.player_valuations,
                                                          player_actions=ThirteenPlayerSpecification.player_valuations,
                                                          no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = valuation - 1

        if valuation >= 3 and min_bid == 0:
            min_bid = 1

        if 6 <= valuation <= 8:
            max_bid = valuation - 2
        elif 9 <= valuation <= 10:
            max_bid = valuation - 3
        elif 11 <= valuation <= 12:
            max_bid = valuation - 4

        return min_bid, max_bid


def do_pezanis_experiments():
    player_valuations = range(0, 3)
    opponent_valuations = range(-6, 3)

    # player_valuations = range(0, 11)
    # opponent_valuations = range(-30, 11)

    game_name = "pezanis_" + str(len(player_valuations)) + "_strong_" + str(len(opponent_valuations)) + "_weak_auction"

    start_time = time.time()
    sample_auction = PezanisAuction(game_name=game_name, player_valuations=player_valuations,
                                    opponent_valuations=opponent_valuations,
                                    no_jumps=True)

    sample_auction.calculate_equilibria()
    logging.info("--- %s seconds ---" % (time.time() - start_time))


def do_allpay_experiments():
    # player_valuations = range(0, 3)
    # player_valuations = range(0, 5)
    # player_valuations = range(0, 6)
    player_valuations = range(0, 7)
    # player_valuations = range(0, 8)

    all_pay = True
    only_pure = True
    start_time = time.time()

    for no_jumps in [False]:
        for no_ties in [True, False]:
            run_first_price(player_valuations=player_valuations, no_jumps=no_jumps,
                            no_ties=no_ties, all_pay=all_pay, only_pure=only_pure)

    logging.info("--- %s seconds ---" % (time.time() - start_time))


def do_three_bidders_experiments():
    # player_valuations = range(0, 3)
    # player_valuations = range(0, 4)
    player_valuations = range(0, 6)
    # player_valuations = range(0, 7)

    start_time = time.time()

    no_jumps = False
    # no_ties = True
    no_ties = False

    all_pay = False
    num_players = 3

    run_first_price(num_players=num_players, player_valuations=player_valuations, no_jumps=no_jumps, no_ties=no_ties,
                    all_pay=all_pay)
    logging.info("--- %s seconds ---" % (time.time() - start_time))


def do_first_price_experiments():
    # player_valuations = range(0, 3)
    # player_valuations = range(0, 5)
    # player_valuations = range(0, 7)
    player_valuations = range(0, 9)
    # player_valuations = range(0, 11)

    start_time = time.time()

    # no_jumps = True
    no_jumps = False
    no_ties = False
    all_pay = False

    run_first_price(player_valuations=player_valuations, no_jumps=no_jumps, no_ties=no_ties, all_pay=all_pay)

    logging.info("--- %s seconds ---" % (time.time() - start_time))


def do_custom_valuations(specification_class, num_players=2, no_jumps=False, no_ties=False, all_pay=False):
    start_time = time.time()

    run_first_price(no_jumps=no_jumps, no_ties=no_ties, all_pay=all_pay, specification_class=specification_class,
                    num_players=num_players)

    logging.info("--- %s seconds ---" % (time.time() - start_time))


def run_first_price(no_jumps, no_ties, all_pay, player_valuations=[], only_pure=True, num_players=2,
                    specification_class=AuctionPlayerSpecification):
    valuations = len(player_valuations)
    if valuations == 0:
        valuations = len(specification_class.player_valuations)

    game_name = "num_players_" + str(num_players) + "_allpay_" + str(all_pay) + "_noties_" + str(
        no_ties) + "_nojumps_" + str(no_jumps) + "_" + str(valuations) + "_valuations_auction"

    if len(player_valuations) != 0:
        player_specifications = [
            specification_class(player_actions=player_valuations, player_types=player_valuations,
                                no_jumps=no_jumps) for _ in range(num_players)]
    else:
        player_specifications = [
            specification_class(no_jumps=no_jumps) for _ in range(num_players)]

    another_sample_auction = FirstPriceAuction(game_name=game_name,
                                               player_specifications=player_specifications, all_pay=all_pay,
                                               no_ties=no_ties)

    logging.info("Running: " + game_name)
    another_sample_auction.calculate_equilibria(only_pure)


def do_gnuth_experiments():
    # player_valuations = range(50, 53)
    # opponent_valuations = range(50, 52)

    player_valuations = range(50, 56)
    opponent_valuations = range(50, 54)
    #
    # player_valuations = range(50, 59)
    # opponent_valuations = range(50, 56)
    #
    # player_valuations = range(50, 62)
    # opponent_valuations = range(50, 58)

    # player_valuations = range(50, 65)
    # opponent_valuations = range(50, 60)

    # player_valuations = range(50, 200 + 1)
    # opponent_valuations = range(50, 150 + 1)

    game_name = str(len(player_valuations)) + "_strong_" + str(len(opponent_valuations)) + "_weak_auction"

    start_time = time.time()
    player_specification = GnuthPlayerSpecification(player_valuations=player_valuations)
    opponent_specification = GnuthPlayerSpecification(player_valuations=opponent_valuations)

    sample_auction = FirstPriceAuction(game_name=game_name, player_specification=player_specification,
                                       opponent_specification=opponent_specification)

    sample_auction.calculate_equilibria()
    logging.info("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    # do_allpay_experiments()
    # do_first_price_experiments()
    # do_three_bidders_experiments()

    # do_custom_valuations(specification_class=ThirteenPlayerSpecification)

    # Trello card: https://trello.com/c/YQss546H/11-first-price-with-ties-and-3-bidders
    # do_custom_valuations(specification_class=SixPlayerSpecification, num_players=3)
    do_custom_valuations(specification_class=SevenPlayerSpecification, num_players=3)

    # Trello card: https://trello.com/c/7avj9H5M/12-all-pay-with-ties-and-3-bidders
    # do_custom_valuations(specification_class=FivePlayerSpecification, num_players=3, no_ties=False, all_pay=True)
    # do_custom_valuations(specification_class=WeaklyIncreasing6PlayerSpecification, num_players=3, no_ties=False,
    #                      all_pay=True)

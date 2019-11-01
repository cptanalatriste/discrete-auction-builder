import logging
import time

from auctions import GnuthPlayerSpecification, FirstPriceAuction, PezanisAuction, AuctionPlayerSpecification
from customspec import SevenPlayerSpecification, ThreePlayersFirsPriceTiesSpec, CustomWeaklyIncreasing


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


def do_custom_valuations(num_players=2, no_jumps=False, no_ties=False, all_pay=False, range_list=[]):
    start_time = time.time()

    player_specifications = [
        CustomWeaklyIncreasing(range_list=range_list,
                               no_jumps=no_jumps) for _ in range(num_players)]

    valuations = len(range_list)
    run_first_price(no_jumps=no_jumps, no_ties=no_ties, all_pay=all_pay, player_specifications=player_specifications,
                    num_players=num_players, valuations=valuations)

    logging.info("--- %s seconds ---" % (time.time() - start_time))


def run_first_price(no_jumps, no_ties, all_pay, player_valuations=[], only_pure=True, num_players=2,
                    specification_class=AuctionPlayerSpecification, player_specifications=None, valuations=0):
    if player_specifications is None:
        valuations = len(specification_class.player_valuations)

    game_name = "num_players_" + str(num_players) + "_allpay_" + str(all_pay) + "_noties_" + str(
        no_ties) + "_nojumps_" + str(no_jumps) + "_" + str(valuations) + "_valuations_auction"

    if player_specifications is None:
        player_specifications = [
            AuctionPlayerSpecification(player_actions=player_valuations, player_types=player_valuations,
                                       no_jumps=no_jumps) for _ in range(num_players)]

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
    # do_custom_valuations(specification_class=SevenPlayerSpecification, num_players=3)

    # ThreePlayersFirsPriceTiesSpec.player_valuations = range(0, 8)
    # do_custom_valuations(specification_class=ThreePlayersFirsPriceTiesSpec, num_players=3)

    # Trello card: https://trello.com/c/7avj9H5M/12-all-pay-with-ties-and-3-bidders
    # do_custom_valuations(specification_class=FivePlayerSpecification, num_players=3, no_ties=False, all_pay=True)
    # do_custom_valuations(specification_class=WeaklyIncreasing6PlayerSpecification, num_players=3, no_ties=False,
    #                      all_pay=True)

    # Trello card: https://trello.com/c/3GAsAFSE/4-first-price-without-ties-and-3-bidders
    # range_list = [(0, 0), (0, 1), (1, 1), (2, 2), (2, 3), (3, 4), (3, 4)]
    # do_custom_valuations(num_players=3, no_jumps=False, no_ties=True, all_pay=False, range_list=range_list)
    # range_list = [(0, 0), (0, 1), (1, 1), (2, 2), (2, 3), (3, 4), (3, 5), (3, 5)]
    # do_custom_valuations(num_players=3, no_jumps=False, no_ties=True, all_pay=False, range_list=range_list)

    # Trello card: https://trello.com/c/EzwXJ3E6/9-all-pay-2-bidders
    # range_list = [(0, 0), (0, 0), (0, 1), (0, 2), (0, 3), (1, 4), (1, 4)]
    # do_custom_valuations(num_players=2, no_jumps=False, no_ties=False, all_pay=True, range_list=range_list)
    # range_list = [(0, 0), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 5), (1, 5)]
    # do_custom_valuations(num_players=2, no_jumps=False, no_ties=False, all_pay=True, range_list=range_list)
    # range_list = [(0, 0), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 6), (1, 6)]
    # do_custom_valuations(num_players=2, no_jumps=False, no_ties=False, all_pay=True, range_list=range_list)
    range_list = [(0, 0), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 6), (1, 7), (1, 7)]
    do_custom_valuations(num_players=2, no_jumps=False, no_ties=False, all_pay=True, range_list=range_list)


    # Starting no-ties
    # range_list = [(0, 0), (0, 0), (0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (1, 6)]
    # do_custom_valuations(num_players=2, no_jumps=False, no_ties=True, all_pay=True, range_list=range_list)
    # range_list = [(0, 0), (0, 0), (0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (1, 6), (1, 7)]
    # do_custom_valuations(num_players=2, no_jumps=False, no_ties=True, all_pay=True, range_list=range_list)

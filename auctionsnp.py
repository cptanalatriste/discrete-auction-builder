import logging
from fractions import Fraction
import time
import numpy as np

import gamebuildernp
from gamebuildernp import BayesianGame, PlayerSpecification

logging.basicConfig(level=logging.INFO)


class AuctionPlayerSpecification(PlayerSpecification):

    def __init__(self, player_valuations):
        super(AuctionPlayerSpecification, self).__init__(player_types=player_valuations,
                                                         player_actions=player_valuations)

    def initialize_pure_strategies(self):
        pure_strategies = []

        for valuation in self.player_types:
            pure_strategies.append([bid for bid in self.player_actions if bid <= valuation])

        product = gamebuildernp.get_cartesian_product(*pure_strategies)
        valid_filter = np.array([self.is_valid_strategy(row) for row in product])
        return product[valid_filter]

    @staticmethod
    def is_valid_strategy(strategy):
        for index, current_bid in enumerate(strategy):
            if index > 0:
                previous_bid = strategy[index - 1]

                if previous_bid > current_bid:
                    return False

        return True


class FirstPriceAuction(BayesianGame):

    def __init__(self, game_name, player_valuations, opponent_valuations):
        super(FirstPriceAuction, self).__init__(
            game_name=game_name,
            player_specification=AuctionPlayerSpecification(player_valuations=player_valuations),
            opponent_specification=AuctionPlayerSpecification(player_valuations=opponent_valuations))

    def get_types_probability(self, player_type, opponent_type):
        return Fraction(1, len(self.player_specification.player_types) * len(self.opponent_specification.player_types))

    def get_utility(self, player_type, player_strategy, opponent_type, opponnet_strategy):
        player_bid = player_strategy.get_action_by_type(player_type)
        opponent_bid = opponnet_strategy.get_action_by_type(opponent_type)

        if player_bid > opponent_bid:
            return player_type - player_bid, 0
        elif opponent_bid > player_bid:
            return 0, opponent_type - opponent_bid
        else:
            return Fraction(player_type - player_bid, 2), Fraction(opponent_type - opponent_bid, 2)


if __name__ == "__main__":
    # player_valuations = range(50, 53)
    # opponent_valuations = range(50, 52)

    # player_valuations = range(50, 56)
    # opponent_valuations = range(50, 54)

    player_valuations = range(50, 59)
    opponent_valuations = range(50, 56)

    # player_valuations = range(50, 62)
    # opponent_valuations = range(50, 58)

    # player_valuations = range(50, 200 + 1)
    # opponent_valuations = range(50, 150 + 1)

    game_name = str(len(player_valuations)) + "_strong_" + str(len(opponent_valuations)) + "_weak_auction"

    start_time = time.time()
    sample_auction = FirstPriceAuction(game_name=game_name, player_valuations=player_valuations,
                                       opponent_valuations=opponent_valuations)

    sample_auction.calculate_equilibria()

    logging.info("--- %s seconds ---" % (time.time() - start_time))

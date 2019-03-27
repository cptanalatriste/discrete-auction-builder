import itertools
import logging
from fractions import Fraction
import time
import networkx as nx

from gamebuilder import BayesianGame, PlayerSpecification

logging.basicConfig(level=logging.INFO)


class AuctionPlayerSpecification(PlayerSpecification):

    def __init__(self, player_valuations):
        super(AuctionPlayerSpecification, self).__init__(player_types=player_valuations,
                                                         player_actions=player_valuations)

    def get_num_strategies(self):
        return pow(2, len(self.player_types) - 1)

    def initialize_pure_strategies(self):
        bidding_graph = nx.DiGraph()
        parent_node = (self.player_types[0], self.player_actions[0])
        bidding_graph.add_node(parent_node)

        pure_strategies = []
        self.add_bids(type_index=1, bidding_graph=bidding_graph, parent_node=parent_node)

        logging.debug("bidding_graph: ", bidding_graph.edges)

        for node in bidding_graph:
            logging.debug("node", node, "bidding_graph.out_degree(node)", bidding_graph.out_degree(node))

            if bidding_graph.out_degree(node) == 0:
                pure_strategies.append(map(lambda path: tuple(bid for _, bid in path),
                                           nx.all_simple_paths(bidding_graph, source=parent_node, target=node)))

        return itertools.chain.from_iterable(pure_strategies)

    def add_bids(self, type_index, bidding_graph, parent_node):
        if type_index == len(self.player_types):
            return

        valuation = self.player_types[type_index]
        previous_bid = parent_node[1]
        valid_bids = [bid for bid in self.player_actions if previous_bid <= bid <= (previous_bid + 1)]

        for bid in valid_bids:
            bid_per_valuation = (valuation, bid)
            bidding_graph.add_edge(parent_node, bid_per_valuation)
            self.add_bids(type_index=type_index + 1, bidding_graph=bidding_graph, parent_node=bid_per_valuation)

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
        player_type_index = self.player_specification.get_type_index(player_type)
        player_bid = player_strategy[player_type_index]

        opponent_type_index = self.opponent_specification.get_type_index(opponent_type)
        opponent_bid = opponnet_strategy[opponent_type_index]

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
    #
    # player_valuations = range(50, 59)
    # opponent_valuations = range(50, 56)

    player_valuations = range(50, 62)
    opponent_valuations = range(50, 58)
    #
    # player_valuations = range(50, 65)
    # opponent_valuations = range(50, 60)

    # player_valuations = range(50, 200 + 1)
    # opponent_valuations = range(50, 150 + 1)

    game_name = str(len(player_valuations)) + "_strong_" + str(len(opponent_valuations)) + "_weak_auction"

    start_time = time.time()
    sample_auction = FirstPriceAuction(game_name=game_name, player_valuations=player_valuations,
                                       opponent_valuations=opponent_valuations)

    sample_auction.calculate_equilibria()

    logging.info("--- %s seconds ---" % (time.time() - start_time))

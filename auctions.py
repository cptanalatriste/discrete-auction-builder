import itertools
import logging
from fractions import Fraction
import networkx as nx

from gamebuilder import BayesianGame, PlayerSpecification

logging.basicConfig(level=logging.INFO)


class GnuthPlayerSpecification(PlayerSpecification):

    def __init__(self, player_valuations):
        super(GnuthPlayerSpecification, self).__init__(player_types=player_valuations,
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


class FirstPriceAuction(BayesianGame):

    def __init__(self, game_name, player_specification, opponent_specification):
        super(FirstPriceAuction, self).__init__(
            game_name=game_name,
            player_specification=player_specification,
            opponent_specification=opponent_specification)

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


class PezanisPlayerSpecification(PlayerSpecification):

    def __init__(self, player_valuations):
        player_actions = [action for action in player_valuations if action >= 0]
        super(PezanisPlayerSpecification, self).__init__(player_types=player_valuations,
                                                         player_actions=player_actions)

    def initialize_pure_strategies(self):
        bidding_graph = nx.DiGraph()
        parent_node = (self.player_actions[0], self.player_actions[0])
        bidding_graph.add_node(parent_node)

        pure_strategies = []
        self.add_bids(action_index=1, bidding_graph=bidding_graph, parent_node=parent_node)

        logging.debug("bidding_graph: ", bidding_graph.edges)

        for node in bidding_graph:
            logging.debug("node", node, "bidding_graph.out_degree(node)", bidding_graph.out_degree(node))

            if bidding_graph.out_degree(node) == 0:
                pure_strategies.append(map(lambda path: tuple(bid for _, bid in path),
                                           nx.all_simple_paths(bidding_graph, source=parent_node, target=node)))

        return itertools.chain.from_iterable(pure_strategies)

    def get_strategy_description(self, strategy):
        strategy_description = ""

        for type_index, action in enumerate(strategy):
            strategy_description += "Type_" + str(self.player_actions[type_index]) + "_action_" + str(action) + "_"
        return strategy_description[:-1]

    def add_bids(self, action_index, bidding_graph, parent_node):
        if action_index == len(self.player_actions):
            return

        valuation = self.get_action_index(action_index)
        previous_bid = parent_node[1]
        valid_bids = [bid for bid in self.player_actions if bid >= previous_bid and bid <= valuation]

        for bid in valid_bids:
            bid_per_valuation = (valuation, bid)
            bidding_graph.add_edge(parent_node, bid_per_valuation)
            self.add_bids(action_index=action_index + 1, bidding_graph=bidding_graph, parent_node=bid_per_valuation)


class PezanisAuction(FirstPriceAuction):
    def __init__(self, game_name, player_valuations, opponent_valuations):
        player_specification = PezanisPlayerSpecification(player_valuations=player_valuations)
        opponent_specification = PezanisPlayerSpecification(player_valuations=opponent_valuations)

        super(PezanisAuction, self).__init__(
            game_name=game_name,
            player_specification=player_specification,
            opponent_specification=opponent_specification)

    def get_number_of_entries(self):
        pass

    def get_utility(self, player_type, player_strategy, opponent_type, opponnet_strategy):

        player_bid = None
        if player_type >= 0:
            player_type_index = self.player_specification.get_action_index(player_type)
            player_bid = player_strategy[player_type_index]
            player_wins = player_type - player_bid, 0

        opponent_bid = None
        if opponent_type >= 0:
            opponent_type_index = self.opponent_specification.get_action_index(opponent_type)

            opponent_bid = opponnet_strategy[opponent_type_index]
            opponent_wins = 0, opponent_type - opponent_bid

        if player_bid is None and opponent_bid is not None:
            return opponent_wins
        elif player_bid is not None and opponent_bid is None:
            return player_wins
        elif player_bid > opponent_bid:
            return player_wins
        elif opponent_bid > player_bid:
            return opponent_wins
        else:
            return Fraction(player_type - player_bid, 2), Fraction(opponent_type - opponent_bid, 2)

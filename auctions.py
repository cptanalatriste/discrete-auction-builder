import itertools
import logging
from fractions import Fraction
import networkx as nx
from functools import reduce
import operator

from gamebuilder import BayesianGame, PlayerSpecification

logging.basicConfig(level=logging.INFO)


class FirstPriceAuction(BayesianGame):

    def __init__(self, game_name, player_specifications, all_pay=False, no_ties=False):

        self.all_pay = all_pay
        self.no_ties = no_ties

        super(FirstPriceAuction, self).__init__(
            game_name=game_name,
            player_specifications=player_specifications)

    def get_types_probability(self, player_types):
        return Fraction(1, reduce(operator.mul, [len(player_specification.player_types) for player_specification in
                                                 self.player_specifications]))

    def get_player_bids(self, player_types, strategy_profile):
        return [player_strategy[player_specification.get_type_index(player_type)] for
                player_type, player_strategy, player_specification in
                zip(player_types, strategy_profile, self.player_specifications)]

    def get_utility(self, player_types, strategy_profile):

        player_bids = self.get_player_bids(player_types, strategy_profile)

        max_bid = max([bid for bid in player_bids if bid is not None])
        winners = [player_index for player_index, player_bid in enumerate(player_bids) if player_bid == max_bid]

        utilities = [0.0 for _ in range(self.num_players)]
        num_winners = len(winners)
        for player_index, player_type, player_bid in zip(range(self.num_players), player_types, player_bids):

            if num_winners == 1 and player_index in winners:
                utilities[player_index] = self.get_winning_utility(player_type, player_bid)
            elif num_winners > 1 and player_index in winners:
                utilities[player_index] = self.get_tie_utility(player_type, player_bid, num_winners)
            else:
                utilities[player_index] = self.get_losing_utility(player_bid)

        return utilities

    @staticmethod
    def get_winning_utility(player_type, player_bid):
        return player_type - player_bid

    def get_losing_utility(self, player_bid):

        loser_utility = 0

        if self.all_pay:
            loser_utility = -player_bid

        return loser_utility

    def get_tie_utility(self, player_type, player_bid, num_winners):

        if self.no_ties:
            return self.get_losing_utility(player_bid)
        else:

            return Fraction((num_winners - 1) * self.get_losing_utility(player_bid),
                            num_winners) + Fraction(
                self.get_winning_utility(player_type, player_bid), num_winners)


class AuctionPlayerSpecification(PlayerSpecification):

    def __init__(self, player_types, player_actions, no_jumps):
        self.no_jumps = no_jumps
        super(AuctionPlayerSpecification, self).__init__(player_types=player_types,
                                                         player_actions=player_actions)

    @classmethod
    def from_specification(cls, player_specification):
        return cls(player_types=player_specification.player_types,
                   player_actions=player_specification.player_actions,
                   no_jumps=player_specification.no_jumps)

    def get_num_strategies(self):
        pass

    def initialize_pure_strategies(self):
        if self.no_jumps:
            logging.info("Jumpy strategies are excluded!")

        bidding_graph = nx.DiGraph()
        parent_node = (self.player_types[0], self.player_actions[0])
        bidding_graph.add_node(parent_node)

        self.add_bids(type_index=1, bidding_graph=bidding_graph, parent_node=parent_node)
        return self.get_strategies_from_graph(parent_node, bidding_graph)

    def get_bid_range(self, valuation, previous_bid):
        max_bid = valuation
        if self.no_jumps:
            max_bid = previous_bid + 1

        return previous_bid, max_bid

    def get_bid_options(self, valuation, previous_bid):

        min_bid, max_bid = self.get_bid_range(valuation, previous_bid)

        return [bid for bid in self.player_actions if min_bid <= bid <= max_bid]

    def add_bids(self, type_index, bidding_graph, parent_node):
        if type_index == len(self.player_types):
            return

        valuation = self.player_types[type_index]
        previous_bid = parent_node[1]
        valid_bids = self.get_bid_options(valuation=valuation, previous_bid=previous_bid)

        for bid in valid_bids:
            bid_per_valuation = (valuation, bid)
            bidding_graph.add_edge(parent_node, bid_per_valuation)
            self.add_bids(type_index=type_index + 1, bidding_graph=bidding_graph, parent_node=bid_per_valuation)

    @staticmethod
    def get_strategies_from_graph(parent_node, bidding_graph):
        pure_strategies = []
        logging.debug("bidding_graph: ", bidding_graph.edges)

        for node in bidding_graph:
            logging.debug("node", node, "bidding_graph.out_degree(node)", bidding_graph.out_degree(node))

            if bidding_graph.out_degree(node) == 0:
                pure_strategies.append(map(lambda path: tuple(bid for _, bid in path),
                                           nx.all_simple_paths(bidding_graph, source=parent_node, target=node)))

        return itertools.chain.from_iterable(pure_strategies)


class GnuthPlayerSpecification(AuctionPlayerSpecification):

    def __init__(self, player_valuations):
        super(GnuthPlayerSpecification, self).__init__(player_types=player_valuations,
                                                       player_actions=player_valuations,
                                                       no_jumps=True)

    def get_num_strategies(self):
        return pow(2, len(self.player_types) - 1)


class PezanisPlayerSpecification(AuctionPlayerSpecification):

    def __init__(self, player_valuations, no_jumps=False):
        player_actions = [action for action in player_valuations if action >= 0]
        super(PezanisPlayerSpecification, self).__init__(player_types=player_valuations,
                                                         player_actions=player_actions,
                                                         no_jumps=no_jumps)

    def initialize_pure_strategies(self):
        if self.no_jumps:
            logging.info("Jumpy strategies are excluded!")

        bidding_graph = nx.DiGraph()

        parent_node = (self.player_actions[0], self.player_actions[0])
        bidding_graph.add_node(parent_node)
        self.add_bids(action_index=1, bidding_graph=bidding_graph, parent_node=parent_node)

        return self.get_strategies_from_graph(parent_node, bidding_graph)

    def add_bids(self, action_index, bidding_graph, parent_node):
        if action_index == len(self.player_actions):
            return

        valuation = self.get_action_index(action_index)
        previous_bid = parent_node[1]
        max_bid = valuation
        if self.no_jumps:
            max_bid = previous_bid + 1

        valid_bids = [bid for bid in self.player_actions if previous_bid <= bid <= max_bid]

        for bid in valid_bids:
            bid_per_valuation = (valuation, bid)
            bidding_graph.add_edge(parent_node, bid_per_valuation)
            self.add_bids(action_index=action_index + 1, bidding_graph=bidding_graph, parent_node=bid_per_valuation)

    def get_strategy_description(self, strategy):
        strategy_description = ""

        for type_index, action in enumerate(strategy):
            strategy_description += "Type_" + str(self.player_actions[type_index]) + "_action_" + str(action) + "_"
        return strategy_description[:-1]


class PezanisAuction(FirstPriceAuction):
    def __init__(self, game_name, player_valuations, no_jumps=False):

        player_specifications = [PezanisPlayerSpecification(player_valuations=valuations, no_jumps=no_jumps) for
                                 valuations in player_valuations]

        super(PezanisAuction, self).__init__(
            game_name=game_name,
            player_specifications=player_specifications)

    def get_number_of_entries(self):
        pass

    def get_player_bids(self, player_types, strategy_profile):

        bids = [None for _ in range(self.num_players)]

        for player_index, player_type, player_strategy, player_specification in zip(range(self.num_players),
                                                                                    player_types, strategy_profile,
                                                                                    self.player_specifications):
            if player_type >= 0:
                bids[player_index] = player_strategy[player_specification.get_action_index(player_type)]

        return bids

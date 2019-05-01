import itertools
import logging
from fractions import Fraction
import networkx as nx

from gamebuilder import BayesianGame, PlayerSpecification

logging.basicConfig(level=logging.INFO)


class FirstPriceAuction(BayesianGame):

    def __init__(self, game_name, player_specification, opponent_specification, all_pay=False, no_ties=False):

        self.all_pay = all_pay
        self.no_ties = no_ties

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
            return self.player_victory_utilities(player_type=player_type, player_bid=player_bid,
                                                 opponent_bid=opponent_bid)
        elif opponent_bid > player_bid:
            return self.opponent_victory_utilities(player_bid=player_bid, opponent_type=opponent_type,
                                                   opponent_bid=opponent_bid)
        else:
            return self.get_tie_utilities(player_type=player_type, player_bid=player_bid, opponent_type=opponent_type,
                                          opponent_bid=opponent_bid)

    @staticmethod
    def get_winning_utility(player_type, player_bid):
        return player_type - player_bid

    def get_losing_utility(self, player_bid):

        loser_utility = 0

        if self.all_pay:
            loser_utility = -player_bid

        return loser_utility

    def player_victory_utilities(self, player_type, player_bid, opponent_bid):
        return self.get_winning_utility(player_type, player_bid), self.get_losing_utility(opponent_bid)

    def opponent_victory_utilities(self, player_bid, opponent_type, opponent_bid):
        return self.get_losing_utility(player_bid), self.get_winning_utility(opponent_type, opponent_bid)

    def get_tie_utilities(self, player_type, player_bid, opponent_type, opponent_bid):

        if self.no_ties:
            return self.get_losing_utility(player_bid), self.get_losing_utility(opponent_bid)
        else:
            return Fraction(self.get_losing_utility(player_bid) + self.get_winning_utility(player_type, player_bid),
                            2), Fraction(
                self.get_losing_utility(opponent_bid) + self.get_winning_utility(opponent_type, opponent_bid), 2)


class AuctionPlayerSpecification(PlayerSpecification):

    def __init__(self, player_types, player_actions, no_jumps):
        self.no_jumps = no_jumps
        super(AuctionPlayerSpecification, self).__init__(player_types=player_types,
                                                         player_actions=player_actions)

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

    def add_bids(self, type_index, bidding_graph, parent_node):
        if type_index == len(self.player_types):
            return

        valuation = self.player_types[type_index]
        previous_bid = parent_node[1]
        max_bid = valuation
        if self.no_jumps:
            max_bid = previous_bid + 1

        valid_bids = [bid for bid in self.player_actions if previous_bid <= bid <= max_bid]

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
    def __init__(self, game_name, player_valuations, opponent_valuations, no_jumps=False):
        player_specification = PezanisPlayerSpecification(player_valuations=player_valuations, no_jumps=no_jumps)
        opponent_specification = PezanisPlayerSpecification(player_valuations=opponent_valuations, no_jumps=no_jumps)

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

        opponent_bid = None
        if opponent_type >= 0:
            opponent_type_index = self.opponent_specification.get_action_index(opponent_type)
            opponent_bid = opponnet_strategy[opponent_type_index]

        if player_bid is None and opponent_bid is not None:
            return self.opponent_victory_utilities(player_bid=player_bid, opponent_type=opponent_type,
                                                   opponent_bid=opponent_bid)
        elif player_bid is not None and opponent_bid is None:
            return self.player_victory_utilities(player_type=player_type, player_bid=player_bid,
                                                 opponent_bid=opponent_bid)
        elif player_bid > opponent_bid:
            return self.player_victory_utilities(player_type=player_type, player_bid=player_bid,
                                                 opponent_bid=opponent_bid)
        elif opponent_bid > player_bid:
            return self.opponent_victory_utilities(player_bid=player_bid, opponent_type=opponent_type,
                                                   opponent_bid=opponent_bid)
        else:
            return self.get_tie_utilities(player_type=player_type, player_bid=player_bid, opponent_type=opponent_type,
                                          opponent_bid=opponent_bid)

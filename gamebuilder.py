import itertools
import logging
from abc import ABC, abstractmethod

import gambitutils


class PlayerSpecification(object):

    def __init__(self, player_types, player_actions):
        self.player_types = player_types
        self.player_actions = player_actions

        self.pure_strategies = self.initialize_pure_strategies()

    def initialize_pure_strategies(self):
        return [strategy for strategy in itertools.product(self.player_actions, repeat=len(self.player_types))]

    def get_pure_strategies(self):
        return self.pure_strategies

    def get_strategy_description(self, strategy):
        strategy_description = ""

        for type_index, action in enumerate(strategy):
            strategy_description += "Type_" + str(self.player_types[type_index]) + "_action_" + str(action) + "_"
        return strategy_description[:-1]

    def get_type_index(self, player_type):
        return self.player_types.index(player_type)

    def get_strategy_index(self, player_strategy):
        return self.pure_strategies.index(player_strategy)

    def get_strategy_catalogue(self):
        return [self.get_strategy_description(strategy) for strategy in self.get_pure_strategies()]


class BayesianGame(ABC):

    def __init__(self, game_name, player_specification, opponent_specification):
        self.game_name = game_name
        self.player_specification = player_specification
        self.opponent_specification = opponent_specification
        self.num_players = 2

    def get_expected_utilities(self, strategy_profile):
        player_strategy, opponent_strategy = strategy_profile
        types_iterator = itertools.product(self.player_specification.player_types,
                                           self.opponent_specification.player_types)

        expected_player_utility, expected_opponent_utility = 0, 0
        for player_type, opponent_type in types_iterator:
            probability = self.get_types_probability(player_type, opponent_type)
            player_utility, opponent_utility = self.get_utility(player_type, player_strategy, opponent_type,
                                                                opponent_strategy)

            expected_player_utility += probability * player_utility
            expected_opponent_utility += probability * opponent_utility

        return expected_player_utility, expected_opponent_utility

    @abstractmethod
    def get_types_probability(self, player_type, opponent_type):
        pass

    @abstractmethod
    def get_utility(self, player_type, player_strategy, opponent_type, opponnet_strategy):
        pass

    def get_strategy_catalogues(self):
        strategies_catalogues = [self.player_specification.get_strategy_catalogue(),
                                 self.opponent_specification.get_strategy_catalogue()]

        return strategies_catalogues

    def get_strategic_game_format(self):
        player_strategies = self.player_specification.get_pure_strategies()
        opponent_strategies = self.opponent_specification.get_pure_strategies()

        logging.info(
            "Pure strategies for player 1: " + str(len(player_strategies)) + " . Pure strategies for player 2: " + str(
                len(opponent_strategies)))

        profile_payoffs = []

        logging.info(
            "Calculating payoffs for " + str(
                len(player_strategies) * len(opponent_strategies)) + " strategy profiles...")
        for opponent_strategy, player_strategy in itertools.product(opponent_strategies, player_strategies):
            payoffs = self.get_expected_utilities((player_strategy, opponent_strategy))
            profile_name = "P1_" + self.player_specification.get_strategy_description(
                player_strategy) + "_P2_" + self.opponent_specification.get_strategy_description(opponent_strategy)

            profile_payoffs.append((profile_name, payoffs))

        strategies_catalogues = self.get_strategy_catalogues()
        return gambitutils.get_strategic_game_format(self.game_name, strategies_catalogues, profile_payoffs)

    def calculate_equilibria(self):
        nfg_file = self.get_strategic_game_format()
        logging.info("Gambit file generated at " + nfg_file)

        strategies_catalogues = self.get_strategy_catalogues()

        return gambitutils.calculate_equilibrium(gambit_file=nfg_file,
                                                 strategy_catalogues=strategies_catalogues)

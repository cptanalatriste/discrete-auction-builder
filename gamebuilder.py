import itertools
from abc import ABC, abstractmethod


class PlayerSpecification(object):

    def __init__(self, player_types, player_actions):
        self.player_types = player_types
        self.player_actions = player_actions

    def get_pure_strategies(self):
        return itertools.product(self.player_actions, repeat=len(self.player_types))


class BayesianGame(ABC):

    def __init__(self, player_specification, opponent_specification):
        self.player_specification = player_specification
        self.opponent_specification = opponent_specification

    def get_expected_utilities(self, strategy_profile):
        player_strategy, opponent_strategy = strategy_profile
        types_iterator = itertools.product(self.player_specification.player_types,
                                           self.opponent_specification.player_types)

        expected_player_utility, expected_opponent_utility = 0.0, 0.0
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


if __name__ == "__main__":
    print("Holitas")

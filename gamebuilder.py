import itertools
import logging
from abc import ABC, abstractmethod
from tqdm import tqdm

import gambitutils


class PlayerSpecification(object):

    def __init__(self, player_types, player_actions):
        self.player_types = player_types
        self.player_actions = player_actions

        self.pure_strategies = self.initialize_pure_strategies()
        self.strategy_catalogue = []
        self.strategy_descriptions = []

    def initialize_pure_strategies(self):
        return itertools.product(self.player_actions, repeat=len(self.player_types))

    def get_num_strategies(self):
        return pow(len(self.player_actions), len(self.player_types))

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
        return self.strategy_catalogue.index(player_strategy)

    def add_to_strategy_catalogue(self, player_strategy, strategy_description):
        if player_strategy not in self.strategy_catalogue:
            self.strategy_catalogue.append(player_strategy)
            self.strategy_descriptions.append(strategy_description)

    def get_strategy_catalogue(self):
        return self.strategy_descriptions


class BayesianGame(ABC):

    def __init__(self, game_name, player_specification, opponent_specification):
        self.game_name = game_name
        self.player_specification = player_specification
        self.opponent_specification = opponent_specification
        self.num_players = 2

    def get_expected_utilities(self, strategy_profile):
        player_strategy, opponent_strategy = strategy_profile
        types_iterator = ((player_type, opponent_type) for player_type in self.player_specification.player_types for
                          opponent_type in self.opponent_specification.player_types)

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

    def register_action_profile(self, player_strategy, player_strategy_desc, opponent_strategy, opponent_strategy_desc):
        self.player_specification.add_to_strategy_catalogue(player_strategy, player_strategy_desc)
        self.opponent_specification.add_to_strategy_catalogue(opponent_strategy, opponent_strategy_desc)

    def get_number_of_entries(self):
        return self.player_specification.get_num_strategies() * self.opponent_specification.get_num_strategies()

    def get_payoffs_per_profile(self):
        logging.info("Obtaining strategies for the strong bidder")
        player_strategies = self.player_specification.get_pure_strategies()

        logging.info("Obtaining strategies for the weak bidder")
        opponent_strategies = self.opponent_specification.get_pure_strategies()

        profile_payoffs = []
        cell_entries = self.get_number_of_entries()

        logging.info(
            "Calculating payoff values for " + str(cell_entries) + " entries ..")

        with tqdm(total=cell_entries) as progress_bar:
            cell_iterator = itertools.product(opponent_strategies, player_strategies)
            for opponent_strategy, player_strategy in cell_iterator:
                payoffs = self.get_expected_utilities((player_strategy, opponent_strategy))

                player_strategy_desc = self.player_specification.get_strategy_description(
                    player_strategy)
                opponent_strategy_desc = self.opponent_specification.get_strategy_description(opponent_strategy)
                self.register_action_profile(player_strategy, player_strategy_desc, opponent_strategy,
                                             opponent_strategy_desc)

                profile_name = "P1_" + player_strategy_desc + "_P2_" + opponent_strategy_desc

                logging.debug("Profile: " + profile_name + " Payoffs: " + str(payoffs))
                profile_payoffs.append((profile_name, payoffs))

                progress_bar.update(1)

        payoffs_obtained = len(profile_payoffs)
        if payoffs_obtained != cell_entries:
            raise Exception("The number of payoffs obtained doesn't match the estimate. Calculated: " + str(
                payoffs_obtained) + " .Estimated: " + str(cell_entries))

        strategies_catalogues = self.get_strategy_catalogues()
        return strategies_catalogues, profile_payoffs

    def calculate_equilibria(self):
        logging.info("Starting equilibrium calculation ...")
        strategies_catalogues, profile_payoffs = self.get_payoffs_per_profile()

        nfg_file = gambitutils.get_strategic_game_format(self.game_name, strategies_catalogues, profile_payoffs)
        logging.info("Gambit file generated at " + nfg_file)

        strategies_catalogues = self.get_strategy_catalogues()

        return gambitutils.calculate_equilibrium(gambit_file=nfg_file,
                                                 strategy_catalogues=strategies_catalogues)

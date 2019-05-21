import itertools
import logging
from abc import ABC, abstractmethod
from tqdm import tqdm

import gambitutils


class PlayerSpecification(object):

    def __init__(self, player_types, player_actions):
        self.player_types = player_types
        self.player_actions = player_actions
        self.strategy_catalogue = None

        self.pure_strategies = self.initialize_pure_strategies()

    def initialize_pure_strategies(self):
        return itertools.product(self.player_actions, repeat=len(self.player_types))

    def get_num_strategies(self):
        return pow(len(self.player_actions), len(self.player_types))

    def get_pure_strategies(self):
        return self.pure_strategies

    def get_strategy_catalogue(self):
        if self.strategy_catalogue is None:
            self.strategy_catalogue = list(self.get_pure_strategies())
        return self.strategy_catalogue

    def get_strategy_description(self, strategy):
        strategy_description = ""

        for type_index, action in enumerate(strategy):
            strategy_description += "Type_" + str(self.player_types[type_index]) + "_action_" + str(action) + "_"
        return strategy_description[:-1]

    def get_type_index(self, player_type):
        return self.player_types.index(player_type)

    def get_action_index(self, player_action):
        return self.player_actions.index(player_action)

    def get_strategy_index(self, player_strategy):
        return self.strategy_catalogue.index(player_strategy)


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

    def get_number_of_entries(self):
        if self.player_specification.get_num_strategies() and self.opponent_specification.get_num_strategies():
            return self.player_specification.get_num_strategies() * self.opponent_specification.get_num_strategies()

    def to_nfg_file(self):
        logging.info("Obtaining strategies for the strong bidder")
        player_strategies = self.player_specification.get_strategy_catalogue()

        logging.info("Obtaining strategies for the weak bidder")
        opponent_strategies = self.opponent_specification.get_strategy_catalogue()

        profile_ordering = []

        player_strategy_catalogue = [self.player_specification.get_strategy_description(player_strategy) for
                                     player_strategy in player_strategies]
        opponent_strategy_catalogue = [self.opponent_specification.get_strategy_description(opponent_strategy) for
                                       opponent_strategy in opponent_strategies]

        strategy_catalogues = [player_strategy_catalogue, opponent_strategy_catalogue]
        file_name = gambitutils.start_nfg_file(self.game_name, strategy_catalogues)

        cell_entries = self.get_number_of_entries()
        if cell_entries is None:
            cell_entries = len(player_strategies) * len(opponent_strategies)

        logging.info("File " + file_name + " created. Starting appending payoff values ...")
        logging.info("Writing payoff values for " + str(cell_entries) + " entries ...")
        with tqdm(total=cell_entries) as progress_bar, open(file_name, "a") as nfg_file:

            gambitutils.start_nfg_section(nfg_file)

            cell_iterator = itertools.product(opponent_strategies, player_strategies)
            for index, profile in enumerate(cell_iterator):
                opponent_strategy, player_strategy = profile
                payoffs = self.get_expected_utilities((player_strategy, opponent_strategy))

                player_strategy_desc = player_strategy_catalogue[player_strategies.index(player_strategy)]
                opponent_strategy_desc = opponent_strategy_catalogue[opponent_strategies.index(opponent_strategy)]

                profile_name = "P1_" + player_strategy_desc + "_P2_" + opponent_strategy_desc
                logging.debug("Profile: " + profile_name + " Payoffs: " + str(payoffs))
                gambitutils.register_profile_payoff(nfg_file, profile_name, payoffs)

                profile_ordering.append(str(index + 1))
                progress_bar.update(1)

            gambitutils.close_nfg_section(nfg_file)
            gambitutils.write_profile_ordering(nfg_file, profile_ordering)

        payoffs_obtained = len(profile_ordering)
        if payoffs_obtained != cell_entries:
            raise Exception("The number of payoffs obtained doesn't match the estimate. Calculated: " + str(
                payoffs_obtained) + " .Estimated: " + str(cell_entries))

        return file_name, strategy_catalogues

    def calculate_equilibria(self, only_pure=True):
        logging.info("Starting equilibrium calculation ...")
        nfg_file, strategy_catalogues = self.to_nfg_file()
        logging.info("Gambit file generated at " + nfg_file)

        tool = gambitutils.PURE_EQUILIBRIA

        if not only_pure:
            tool = gambitutils.ALL_EQUILIBRIA

        return gambitutils.calculate_equilibrium(gambit_file=nfg_file,
                                                 strategy_catalogues=strategy_catalogues,
                                                 tool=tool)

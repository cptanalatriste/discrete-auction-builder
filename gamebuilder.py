import itertools
import operator
import logging
from functools import reduce
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

    def __init__(self, game_name, player_specifications):
        self.game_name = game_name
        self.player_specifications = player_specifications
        self.num_players = len(player_specifications)

    def get_expected_utilities(self, strategy_profile):

        types_iterator = itertools.product(
            *[player_specification.player_types for player_specification in self.player_specifications])

        expected_player_utilities = [0 for _ in range(self.num_players)]

        for player_types in types_iterator:
            probability = self.get_types_probability(player_types)
            player_utilities = self.get_utility(player_types, strategy_profile)

            expected_player_utilities = [previous_value + probability * current_value for previous_value, current_value
                                         in
                                         zip(expected_player_utilities, player_utilities)]

        return expected_player_utilities

    @abstractmethod
    def get_types_probability(self, player_types):
        pass

    @abstractmethod
    def get_utility(self, player_types, strategy_profile):
        pass

    def get_strategy_catalogues(self):
        strategies_catalogues = [player_specification.get_strategy_catalogue() for player_specification in
                                 self.player_specifications]

        return strategies_catalogues

    def get_number_of_entries(self):

        num_strategies = [player_specification.get_num_strategies() for player_specification in
                          self.player_specifications if player_specification.get_num_strategies()]

        if len(num_strategies) > 0:
            return reduce(operator.mul, num_strategies)

    def to_nfg_file(self):
        logging.info("Obtaining strategies for all players")
        player_strategies = [player_specification.get_strategy_catalogue() for player_specification in
                             self.player_specifications]

        profile_ordering = []

        strategy_catalogues = [
            [player_specification.get_strategy_description(player_strategy) for player_strategy in strategy_list] for
            strategy_list, player_specification in zip(player_strategies, self.player_specifications)]

        file_name = gambitutils.start_nfg_file(self.game_name, strategy_catalogues)

        cell_entries = self.get_number_of_entries()
        if cell_entries is None:
            cell_entries = reduce(operator.mul, [len(strategy_list) for strategy_list in player_strategies])

        logging.info("File " + file_name + " created. Starting appending payoff values ...")
        logging.info("Writing payoff values for " + str(cell_entries) + " entries ...")
        with tqdm(total=cell_entries) as progress_bar, open(file_name, "a") as nfg_file:

            gambitutils.start_nfg_section(nfg_file)

            cell_iterator = itertools.product(*player_strategies)
            for index, profile in enumerate(cell_iterator):
                payoffs = self.get_expected_utilities(profile)

                profile_name = ""

                for player_index in range(self.num_players):
                    player_strategy = profile[player_index]
                    strategy_catalogue = strategy_catalogues[player_index]
                    strategy_list = player_strategies[player_index]

                    profile_name += "P" + str(player_index) + strategy_catalogue[strategy_list.index(player_strategy)]

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

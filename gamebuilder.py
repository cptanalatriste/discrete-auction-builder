import itertools
import subprocess
from abc import ABC, abstractmethod
from collections import defaultdict
from string import Template
import logging


class PlayerSpecification(object):

    def __init__(self, player_types, player_actions):
        self.player_types = player_types
        self.player_actions = player_actions

        self.pure_strategies = self.initialize_pure_strategies()

    def initialize_pure_strategies(self):
        return {strategy for strategy in itertools.product(self.player_actions, repeat=len(self.player_types))}

    def get_pure_strategies(self):
        return self.pure_strategies

    def get_strategy_description(self, strategy):
        strategy_description = ""

        for type_index, action in enumerate(strategy):
            strategy_description += "Type_" + str(self.player_types[type_index]) + "_action_" + str(action) + "_"
        return strategy_description[:-1]

    def get_type_index(self, player_type):
        return self.player_types.index(player_type)

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
        player_strategies = [strategy for strategy in self.player_specification.get_pure_strategies()]
        opponent_strategies = [strategy for strategy in self.opponent_specification.get_pure_strategies()]

        logging.info(
            "Pure strategies for player 1: " + str(len(player_strategies)) + " .Pure strategies for player 2: " + str(
                len(opponent_strategies)))

        profile_payoffs = []

        for opponent_strategy, player_strategy in itertools.product(opponent_strategies, player_strategies):
            payoffs = self.get_expected_utilities((player_strategy, opponent_strategy))
            profile_name = "P1_" + self.player_specification.get_strategy_description(
                player_strategy) + "_P2_" + self.opponent_specification.get_strategy_description(opponent_strategy)

            profile_payoffs.append((profile_name, payoffs))

        strategies_catalogues = self.get_strategy_catalogues()
        return get_strategic_game_format(self.game_name, strategies_catalogues, profile_payoffs)


def get_strategic_game_format(game_desc, strategies_catalogues, profile_payoffs):
    """
    Generates the content of a Gambit NFG file.
    :return: Name of the generated file.
    """

    template = 'NFG 1 R "$game_desc" { $player_catalog } \n\n ' \
               '{ $actions_per_player \n}\n""\n\n' \
               '{\n$payoff_per_profile\n}\n$profile_ordering'

    nfg_template = Template(template)
    teams = set(['"Player_' + str(team_number) + '"' for team_number in range(len(strategies_catalogues))])

    action_list = []
    for strategies_catalog in strategies_catalogues:
        actions = " ".join(['"' + strategy + '"' for strategy in strategies_catalog])
        action_list.append("{ " + actions + " }")

    profile_lines = []
    profile_ordering = []

    for index, profile_info in enumerate(profile_payoffs):
        profile_name, payoffs = profile_info
        payoff_strings = [str(payoff) for payoff in payoffs]
        payoff_line = '{ "' + profile_name + '" ' + ",".join(payoff_strings) + " }"

        profile_lines.append(payoff_line)
        profile_ordering.append(str(index + 1))

    player_catalog = " ".join(teams)
    actions_per_player = "\n".join(action_list)
    payoff_per_profile = "\n".join(profile_lines)
    profile_ordering = " ".join(profile_ordering)

    file_content = nfg_template.substitute({
        'game_desc': game_desc,
        'player_catalog': player_catalog,
        'actions_per_player': actions_per_player,
        'payoff_per_profile': payoff_per_profile,
        'profile_ordering': profile_ordering})

    file_name = game_desc + ".nfg"
    with open(file_name, "w") as gambit_file:
        gambit_file.write(file_content)

    return file_name


def calculate_equilibrium(gambit_process, strategy_catalogues, gambit_file):
    """
    Executes Gambit for equilibrium calculation.
    :param gambit_process: Gambit solver to use
    :param strategy_catalogues: Catalog of available strategies.
    :param gambit_file:
    :return: List of equilibrium profiles.
    """

    no_banner_option = "-q"
    command_line = [gambit_process, no_banner_option, gambit_file]
    solver_process = subprocess.Popen(command_line, stdout=subprocess.PIPE)

    nash_equilibrium_strings = []
    while True:
        line = solver_process.stdout.readline().decode()
        if line != '':
            nash_equilibrium_strings.append(line)
        else:
            break

    start_index = 3

    equilibrium_list = []
    for index, nash_equilibrium in enumerate(nash_equilibrium_strings):

        logging.info("Equilibrium " + str(index + 1) + " of " + str(len(nash_equilibrium_strings)))

        nash_equilibrium = nash_equilibrium.strip()
        nash_equilibrium = nash_equilibrium[start_index:].split(",")

        player_index = 0
        strategy_index = 0

        equilibrium_profile = defaultdict(defaultdict)
        for probability in nash_equilibrium:

            strategies_catalog = strategy_catalogues[player_index]
            strategy_name = strategies_catalog[strategy_index]

            if float(probability) > 0.0:
                logging.info(
                    "Player " + str(player_index) + "-> Strategy: " + str(strategy_name) + " \t\tProbability " + str(
                        probability))

            equilibrium_profile[player_index][strategy_name] = probability

            if strategy_index < len(strategies_catalog) - 1:
                strategy_index += 1
            else:
                player_index += 1
                strategy_index = 0

        equilibrium_list.append(equilibrium_profile)

    return equilibrium_list

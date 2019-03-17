import itertools
from abc import ABC, abstractmethod
from string import Template


class PlayerSpecification(object):

    def __init__(self, player_types, player_actions):
        self.player_types = player_types
        self.player_actions = player_actions

    def get_pure_strategies(self):
        return itertools.product(self.player_actions, repeat=len(self.player_types))

    def get_strategy_description(self, strategy):
        strategy_description = ""

        for type_index, action in enumerate(strategy):
            strategy_description += "Type_" + str(self.player_types[type_index]) + "_action_" + str(action) + "_"
        return strategy_description[:-1]


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

    def get_strategic_game_format(self):
        player_strategies = [strategy for strategy in self.player_specification.get_pure_strategies()]
        opponent_strategies = [strategy for strategy in self.opponent_specification.get_pure_strategies()]

        strategies_catalogues = []
        profile_payoffs = []

        for opponent_strategy, player_strategy in itertools.product(opponent_strategies, player_strategies):
            payoffs = self.get_expected_utilities((player_strategy, opponent_strategy))
            profile_name = "P1_" + self.player_specification.get_strategy_description(
                player_strategy) + "_P2_" + self.opponent_specification.get_strategy_description(opponent_strategy)

            profile_payoffs.append((profile_name, payoffs))

        strategies_catalogues.append(
            [self.player_specification.get_strategy_description(strategy) for strategy in player_strategies])

        strategies_catalogues.append(
            [self.opponent_specification.get_strategy_description(strategy) for strategy in opponent_strategies])

        get_strategic_game_format(self.game_name, strategies_catalogues, profile_payoffs)


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

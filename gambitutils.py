import logging
import subprocess
from string import Template

DEFAULT_PROCESS = "/Applications/Gambit.app/Contents/MacOS/gambit-enumpure"


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


def calculate_equilibrium(strategy_catalogues, gambit_file, gambit_process=DEFAULT_PROCESS):
    """
    Executes Gambit for equilibrium calculation.
    :param gambit_process: Gambit solver to use
    :param strategy_catalogues: Catalog of available strategies.
    :param gambit_file:
    :return: List of equilibrium profiles.
    """

    no_banner_option = "-q"
    command_line = [gambit_process, no_banner_option, gambit_file]
    logging.info("Starting equilibrium calculation using: " + gambit_process)

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

        equilibrium_profile = {}
        for probability in nash_equilibrium:

            strategies_catalog = strategy_catalogues[player_index]
            strategy_name = strategies_catalog[strategy_index]

            if float(probability) > 0.0:
                logging.info(
                    "Player " + str(player_index) + "-> Strategy: " + str(strategy_name) + " \t\tProbability " + str(
                        probability))

            equilibrium_profile[(player_index, strategy_index)] = probability

            if strategy_index < len(strategies_catalog) - 1:
                strategy_index += 1
            else:
                player_index += 1
                strategy_index = 0

        equilibrium_list.append(equilibrium_profile)

    return equilibrium_list

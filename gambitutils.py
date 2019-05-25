import logging
import subprocess
import time
from string import Template

GAMBIT_DIR = "/Applications/Gambit.app/Contents/MacOS/"

ALL_EQUILIBRIA = "gambit-enumpoly"
PURE_EQUILIBRIA = "gambit-enumpure"


def start_nfg_section(nfg_file):
    nfg_file.write("\n{")


def close_nfg_section(nfg_file):
    nfg_file.write("}")


def register_profile_payoff(nfg_file, profile_name, payoffs):
    payoff_strings = [str(payoff) for payoff in payoffs]
    payoff_line = '{ "' + profile_name + '" ' + ",".join(payoff_strings) + " }"
    nfg_file.write(payoff_line + "\n")


def write_profile_ordering(nfg_file, profile_ordering):
    profile_ordering = " ".join(profile_ordering)
    nfg_file.write("\n" + profile_ordering)


def start_nfg_file(game_description, strategies_catalogues):
    first_line = 'NFG 1 R "$game_desc" { $player_catalog }'
    first_line_template = Template(first_line)

    players = set(['"Player_' + str(player_number) + '"' for player_number in range(len(strategies_catalogues))])
    player_catalog = " ".join(players)
    file_name = game_description + ".nfg"

    with open(file_name, "w") as nfg_file:
        nfg_file.write(first_line_template.substitute({
            'game_desc': game_description,
            'player_catalog': player_catalog}))

        start_nfg_section(nfg_file)

        for strategy_catalogue in strategies_catalogues:
            actions = " ".join(['"' + strategy + '"' for strategy in strategy_catalogue])
            nfg_file.write("{ " + actions + " }\n")

        close_nfg_section(nfg_file)

    return file_name


def get_strategic_game_format(game_desc, strategies_catalogues, profile_payoffs):
    """
    Generates the content of a Gambit NFG file.
    :return: Name of the generated file.
    """

    template = 'NFG 1 R "$game_desc" { $player_catalog } \n\n ' \
               '{ $actions_per_player \n}\n""\n\n' \
               '{\n$payoff_per_profile\n}\n$profile_ordering'

    nfg_template = Template(template)
    players = set(['"Player_' + str(player_number) + '"' for player_number in range(len(strategies_catalogues))])

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

    player_catalog = " ".join(players)
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


def calculate_equilibrium(strategy_catalogues, gambit_file, tool=PURE_EQUILIBRIA):
    """
    Executes Gambit for equilibrium calculation.
    :param tool: Gambit solver to use
    :param strategy_catalogues: Catalog of available strategies.
    :param gambit_file:
    :return: List of equilibrium profiles.
    """

    no_banner_option = "-q"
    gambit_process = GAMBIT_DIR + tool

    command_line = [gambit_process, no_banner_option, gambit_file]
    logging.info("Starting equilibrium calculation using: " + gambit_process)

    solver_process = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = solver_process.communicate()

    logging.info("Command-line output: Return Code " + str(solver_process.returncode))
    if solver_process.returncode == 0:
        logging.info("Command-line output: " + str(out))

        nash_equilibrium_strings = str(out.decode()).splitlines()
        if len(nash_equilibrium_strings) == 0:
            logging.warning("NO EQUILIBRIA WAS FOUND FOR GAME " + gambit_file)

        equilibrium_list = []

        start_index = 3
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
                        "Player " + str(player_index) + "-> Strategy: " + str(
                            strategy_name) + " \t\tProbability " + str(
                            probability))

                equilibrium_profile[(player_index, strategy_index)] = probability

                if strategy_index < len(strategies_catalog) - 1:
                    strategy_index += 1
                else:
                    player_index += 1
                    strategy_index = 0

            equilibrium_list.append(equilibrium_profile)

    else:
        logging.error("ERROR WHILE PROCESSING FILE: " + gambit_file + " . Error: " + str(err))
        return

    return equilibrium_list

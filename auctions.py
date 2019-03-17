import gamebuilder
from gamebuilder import BayesianGame, PlayerSpecification


class FirstPriceAuction(BayesianGame):

    def __init__(self, game_name, player_valuations, opponent_valuations):
        super(FirstPriceAuction, self).__init__(
            game_name=game_name,
            player_specification=PlayerSpecification(player_types=player_valuations, player_actions=player_valuations),
            opponent_specification=PlayerSpecification(player_types=opponent_valuations,
                                                       player_actions=opponent_valuations))

    def get_types_probability(self, player_type, opponent_type):
        return 1.0 / (len(self.player_specification.player_types) * len(self.opponent_specification.player_types))

    def get_utility(self, player_type, player_strategy, opponent_type, opponnet_strategy):
        player_type_index = self.player_specification.get_type_index(player_type)
        player_bid = player_strategy[player_type_index]

        opponent_type_index = self.opponent_specification.get_type_index(opponent_type)
        opponent_bid = opponnet_strategy[opponent_type_index]

        if player_bid > opponent_bid:
            return player_type - player_bid, 0
        elif opponent_bid > player_bid:
            return 0, opponent_type - opponent_bid
        else:
            return 0.5 * (player_type - player_bid), 0.5 * (opponent_type - opponent_bid)


if __name__ == "__main__":
    sample_auction = FirstPriceAuction(game_name="toy_auction", player_valuations=[0.0, 1.0, 2.0],
                                       opponent_valuations=[0.0, 1.0])

    nfg_file = sample_auction.get_strategic_game_format()
    print("Gambit file generated at " + nfg_file)

    gambit_process = "C:\Program Files (x86)\Gambit\gambit-enumpure.exe"
    strategies_catalogues = sample_auction.get_strategy_catalogues()

    print("Starting equilibrium calculation using: " + gambit_process)
    gamebuilder.calculate_equilibrium(gambit_process=gambit_process, gambit_file=nfg_file,
                                      strategy_catalogues=strategies_catalogues)

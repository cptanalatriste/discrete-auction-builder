import itertools


class PlayerSpecification(object):

    def __init__(self, player_types, player_actions):
        self.player_types = player_types
        self.player_actions = player_actions

    def get_pure_strategies(self):
        return itertools.product(self.player_actions, repeat=len(self.player_types))


if __name__ == "__main__":
    print("Holitas")

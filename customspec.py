from auctions import AuctionPlayerSpecification


class ThreePlayersFirsPriceTiesSpec(AuctionPlayerSpecification):
    player_valuations = None

    def __init__(self, no_jumps):

        super(ThreePlayersFirsPriceTiesSpec, self).__init__(
            player_types=ThreePlayersFirsPriceTiesSpec.player_valuations,
            player_actions=ThreePlayersFirsPriceTiesSpec.player_valuations,
            no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = max(valuation - 1, 0)

        if 2 <= valuation <= 4:
            min_bid = 1
        elif valuation >= 5:
            min_bid = 2

        return min_bid, max_bid


class FivePlayerSpecification(AuctionPlayerSpecification):
    player_valuations = range(0, 5)

    def __init__(self, no_jumps):
        super(FivePlayerSpecification, self).__init__(player_types=FivePlayerSpecification.player_valuations,
                                                      player_actions=FivePlayerSpecification.player_valuations,
                                                      no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = max(valuation - 1, 0)

        return min_bid, max_bid


class WeaklyIncreasing6PlayerSpecification(AuctionPlayerSpecification):
    player_valuations = range(0, 6)

    def __init__(self, no_jumps):
        super(WeaklyIncreasing6PlayerSpecification, self).__init__(
            player_types=SixPlayerSpecification.player_valuations,
            player_actions=SixPlayerSpecification.player_valuations,
            no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = max(valuation - 1, 0)

        return min_bid, max_bid


class SevenPlayerSpecification(AuctionPlayerSpecification):
    player_valuations = range(0, 7)

    def __init__(self, no_jumps):
        super(SevenPlayerSpecification, self).__init__(player_types=SevenPlayerSpecification.player_valuations,
                                                       player_actions=SevenPlayerSpecification.player_valuations,
                                                       no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = max(valuation - 1, 0)

        if valuation >= 2 and min_bid == 0:
            min_bid = 1

        return min_bid, max_bid


class SixPlayerSpecification(AuctionPlayerSpecification):
    player_valuations = range(0, 6)

    def __init__(self, no_jumps):
        super(SixPlayerSpecification, self).__init__(player_types=SixPlayerSpecification.player_valuations,
                                                     player_actions=SixPlayerSpecification.player_valuations,
                                                     no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = max(valuation - 1, 0)

        if valuation >= 2 and min_bid == 0:
            min_bid = 1

        return min_bid, max_bid


class ElevenPlayerSpecification(AuctionPlayerSpecification):
    player_valuations = range(0, 11)

    def __init__(self, no_jumps):

        super(ElevenPlayerSpecification, self).__init__(player_types=ElevenPlayerSpecification.player_valuations,
                                                        player_actions=ElevenPlayerSpecification.player_valuations,
                                                        no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = min(valuation - 1, 6)

        if valuation >= 3 and min_bid == 0:
            min_bid = 1

        if valuation == 5:
            max_bid = 3
        elif valuation == 6:
            max_bid = 4
        elif 7 <= valuation <= 8:
            max_bid = 5

        return min_bid, max_bid


class ThirteenPlayerSpecification(AuctionPlayerSpecification):
    player_valuations = range(0, 13)

    def __init__(self, no_jumps):

        super(ThirteenPlayerSpecification, self).__init__(player_types=ThirteenPlayerSpecification.player_valuations,
                                                          player_actions=ThirteenPlayerSpecification.player_valuations,
                                                          no_jumps=no_jumps)

    def get_bid_range(self, valuation, previous_bid):
        min_bid = previous_bid
        max_bid = valuation - 1

        if valuation >= 3 and min_bid == 0:
            min_bid = 1

        if 6 <= valuation <= 8:
            max_bid = valuation - 2
        elif 9 <= valuation <= 10:
            max_bid = valuation - 3
        elif 11 <= valuation <= 12:
            max_bid = valuation - 4

        return min_bid, max_bid

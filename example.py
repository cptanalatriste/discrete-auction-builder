from auctions import AuctionPlayerSpecification, FirstPriceAuction


def main():
    player_valuations = [0, 1, 2]
    player_specification = AuctionPlayerSpecification(player_actions=player_valuations,
                                                      player_types=player_valuations, no_jumps=False)
    opponent_specification = AuctionPlayerSpecification.from_specification(player_specification)
    third_player_specification = AuctionPlayerSpecification.from_specification(player_specification)

    auction_with_ties = FirstPriceAuction(game_name="3-bidders-with-ties",
                                          player_specifications=[player_specification,
                                                                 opponent_specification,
                                                                 third_player_specification],
                                          all_pay=False,
                                          no_ties=False)
    auction_with_ties.calculate_equilibria(only_pure=True)


if __name__ == "__main__":
    main()

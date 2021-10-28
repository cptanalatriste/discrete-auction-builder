# Discrete Auction Builder

Supporting code for the paper 
["The importance of being discrete: on the inaccuracy of continuous approximations in auction theory"](https://arxiv.org/abs/2006.03016#).
It is a Python library for obtaining equilibria of discrete-auction game-theoretic models.

## Installation

This code was tested using on MacOS using Anaconda Python 3.9 and Gambit 15.1.1.
However, there's no reason why it shouldn't work in Linux and Windows.

Our Python scripts internally use [Gambit's command line tools for equilibrium calculation](https://gambitproject.readthedocs.io/en/latest/tools.html).
Hence, you need to [download and install Gambit](http://www.gambit-project.org/gambit16/16.0.0/intro.html#section-downloading) first.
After installation, please update the global variable `GAMBIT_DIR` on the `gambitutils.py` file with 
your installation directory.

To install Python dependencies, execute the following

```bash
pip install -r requirements.txt
```

After that, you should be able to use this library. 
To check everything went smoothly, 
[install Pytest](https://docs.pytest.org/en/6.2.x/getting-started.html) and run the test suite using:

```bash
pytest -v
```

## Usage

The experiments developed for [the paper](https://arxiv.org/abs/2006.03016#) are contained in the file `experiments.py`.
**Be aware some of them take several hours to complete.**

For demonstration purposes, in `example.py` we  included how to calculate pure-strategy equilibria for a 
3-valuation-3-bidder auction supporting ties.
The following code:

```python
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
```

Produces the following output:

```bash
INFO:root:Starting equilibrium calculation ...
INFO:root:Obtaining strategies for all players
INFO:root:Pure strategies obtained: 5
INFO:root:Pure strategies obtained: 5
INFO:root:Pure strategies obtained: 5
INFO:root:File 3-bidders-with-ties.nfg created. Starting appending payoff values ...
INFO:root:Writing payoff values for 125 entries ...
100%|██████████| 125/125 [00:00<00:00, 1454.23it/s]
INFO:root:Gambit file generated at 3-bidders-with-ties.nfg
INFO:root:Starting equilibrium calculation using: /Applications/Gambit.app/Contents/MacOS/gambit-enumpure
INFO:root:Command-line output: Return Code 0
INFO:root:Command-line output: b'NE,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0\n'
INFO:root:Equilibrium 1 of 1
INFO:root:Player 0-> Strategy: Type_0_action_0_Type_1_action_0_Type_2_action_1 		Probability 1
INFO:root:Player 1-> Strategy: Type_0_action_0_Type_1_action_0_Type_2_action_1 		Probability 1
INFO:root:Player 2-> Strategy: Type_0_action_0_Type_1_action_0_Type_2_action_1 		Probability 1
```

The file `3-bidders-with-ties.nfg` was also written to disk. This [NFG file](http://www.gambit-project.org/gambit14/formats.html)
is compatible with Gambit, and contains the normal-form model of the auction.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
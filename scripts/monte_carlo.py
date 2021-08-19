"""Performing Monte Carlo test. Useful to validate performance."""

# Note: Remember to change simulation to False

import test_swarm as swarm
from tqdm import tqdm

iterations = 10000

if __name__ == "__main__":

    performance = 0.0
    for i in tqdm(range(iterations)):
        performance += swarm.main(prints=False)
    print(performance/iterations)
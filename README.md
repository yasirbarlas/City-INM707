# INM707: Deep Reinforcement Learning

Note: This repository and its contents support the coursework of the INM707 module at City, University of London.

## Basic Tasks

We create a Gridworld-like environment using NumPy and Matplotlib. The environment specifically looks at an agent traversing a single-story house (or apartment), with the aim of cleaning the carpets of the house. We refer to the agent as a robot vacuum cleaner. The agent receives a positive reward for cleaning carpets, a negative reward for bumping into walls/furniture or trying to escape the grid, a negative reward for moving onto states with cables/wires, and lastly a positive reward for entering the terminal state (a charging station).

The relevant Jupyter Notebook can be found in the [basic-tasks](../main/basic-tasks) folder.

## Advanced Tasks

We investigate the [(Target Network + Experience Replay) Deep Q-Network (DQN)](https://www.nature.com/articles/nature14236), the [Prioritised Experience Replay DQN](https://arxiv.org/abs/1511.05952v4), the [Noisy Network DQN](https://arxiv.org/abs/1706.10295), and the [N-Step Return DQN](https://link.springer.com/article/10.1007/BF00115009) algorithms on the ViZDoom 'Defend The Center' environment. Each algorithm utilises the previous ones sequentially, similar to what is done in [Rainbow DQN](https://arxiv.org/abs/1710.02298). In other words, we look at a Target Network + Experience Replay DQN, a Target Network + Prioritised Experience Replay DQN, a Target Network + Prioritised Experience Replay + Noisy Network DQN, and lastly a Target Network + Prioritised Experience Replay + Noisy Network + N-Step Return DQN. We provide the code in standard .py form and as Jupyter Notebooks, and neither of these depend on each other to run.

We use Python 3.10.13, PyTorch (with CUDA 12.1), Gymnasium 0.29.0, ViZDoom 1.2.3, and for recording the agent in the testing phase, MoviePy 1.0.3. Instructions for installing ViZDoom (through Github or pip) can be found [here](https://vizdoom.farama.org/).

Much work on reinforcement learning seems to be built using the old versions of PyTorch and Gym. Here, we ensure that our code runs well on the latest versions of these libraries.

The relevant Jupyter Notebooks and code can be found in the [advanced-tasks](../main/advanced-tasks) folder.

The following is information regarding the ViZDoom environment we use:

```
DEFEND THE CENTER
The purpose of this scenario is to teach the agent that killing the monsters is GOOD and when monsters kill you is BAD. In addition, wasting ammunition is not very good either. Agent is rewarded only for killing monsters so he has to figure out the rest for himself.

The map is a large circle. A player is spawned in the exact center. 5 melee-only, monsters are spawned along the wall. Monsters are killed after a single shot. After dying, each monster is respawned after some time. The episode ends when the player dies (it’s inevitable because of limited ammo).

REWARDS:

+1 for killing a monster

-1 for death

CONFIGURATION:

3 available buttons: turn left, turn right, shoot (attack)

2 available game variables: player’s health and ammo

timeout = 2100

difficulty level (doom_skill) = 3

Gymnasium/Gym id: "VizdoomDefendCenter-v0"
```

We note that our code is inspired by the [Rainbow is all you need!](https://github.com/Curt-Park/rainbow-is-all-you-need) repository, and that while much of our code is similar, we make certain adjustments to be suited for the ViZDoom environment, and we make the sequential improvements to each algorithm we examine as mentioned previously.

## Individual Advanced Tasks

## Extra Tasks

The soft actor-critic algorithm is considered a state-of-the-art algorithm, notably in continuous control tasks. It combines actor-critic methods with maximum entropy reinforcement learning, encouraging exploration while simultaneously optimising for both policy improvement and entropy maximisation. We provide code to work on many of the continuous control tasks found on [Gymnasium](https://gymnasium.farama.org/index.html).

We use Python 3.10.13, PyTorch (with CUDA 12.1), Gymnasium 0.29.0, and for recording the agent in the testing phase, MoviePy 1.0.3.

Much work on reinforcement learning seems to be built using the old versions of PyTorch and Gym. Here, we ensure that our code runs well on the latest versions of these libraries.

The relevant Jupyter Notebooks and code can be found in the [extra-tasks](../main/extra-tasks) folder.

We note that our Agent class is inspired by the [PG is all you need!](https://github.com/MrSyee/pg-is-all-you-need) repository, and much of the code is adapted from the [pytorch-soft-actor-critic](https://github.com/pranz24/pytorch-soft-actor-critic) repository.

import os
import pickle
import numpy as np
from matplotlib import pyplot as plt

import torch
import torch.optim as optim
import torch.nn.functional as F

from gymnasium.wrappers import RecordVideo

from buffers import *
from models import *
from utils import *

## As found in https://github.com/Curt-Park/rainbow-is-all-you-need/blob/master/01.dqn.ipynb ##
## With some changes ##

class SimpleAgent:
    """
    Simple DQN Agent
    """
    def __init__(self, env, memory_size, batch_size, target_update, seed, gamma = 0.99, max_epsilon = 1.0, min_epsilon = 0.01, epsilon_decay = 0.00001, learning_rate = 0.0000625, optimizer = "adam"):
        """
        Initialise the DQN agent with the provided parameters.

        Args:
            env (gymnasium.Env): Gymnasium environment
            memory_size (int): Size of the replay memory
            batch_size (int): Batch size for sampling from the replay memory
            target_update (int): Frequency (in steps) at which to update the target network
            seed (int): Seed for random number generation
            gamma (float): Discount factor (default: 0.99)
            max_epsilon (float): Initial epsilon value for epsilon-greedy exploration (default: 1.0)
            min_epsilon (float): Minimum epsilon value (default: 0.01)
            epsilon_decay (float): Decay rate for epsilon (default: 0.00001)
            learning_rate (float): Learning rate for the optimizer (default: 0.0000625)
            optimizer (str): Name of the optimizer to use ("adam", "rmsprop", or "sgd") (default: "adam")
        """
        obs_dim = env.observation_space.shape
        action_dim = env.action_space.n

        self.env = env
        self.batch_size = batch_size
        self.target_update = target_update
        self.seed = seed
        self.gamma = gamma
        self.epsilon = max_epsilon
        self.max_epsilon = max_epsilon
        self.min_epsilon = min_epsilon
        self.epsilon_decay = epsilon_decay
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(self.device)
        
        self.memory = ReplayBuffer(obs_dim, memory_size, batch_size)
        
        # Action space seed
        self.env.action_space.seed(seed)

        # Neural network models setup
        self.dqn = SimpleDQN(obs_dim, action_dim).to(self.device)
        self.dqn_target = SimpleDQN(obs_dim, action_dim).to(self.device)
        self.dqn_target.load_state_dict(self.dqn.state_dict())
        self.dqn_target.eval()
        
        # Optimizer setup
        optimizer.lower()
        if optimizer == "adam":
            self.optimizer = optim.Adam(self.dqn.parameters(), lr = learning_rate)
        if optimizer == "rmsprop":
            self.optimizer = optim.RMSprop(self.dqn.parameters(), lr = learning_rate)
        if optimizer == "sgd":
            self.optimizer = optim.SGD(self.dqn.parameters(), lr = learning_rate)

        # Transition to store in memory
        self.transition = list()
        
        # Mode: train / test
        self.is_test = False

    def select_action(self, state):
        """
        Select an action from the input state.
        """
        selected_action = self.dqn.act(state, self.epsilon)
        
        if not self.is_test:
            self.transition = [state, selected_action]
        
        return selected_action

    def step(self, action):
        """
        Take an action and return the response of the environment.
        """
        next_state, reward, terminated, truncated, _ = self.env.step(action)
        done = terminated or truncated

        if not self.is_test:
            self.transition += [reward, next_state, done]
            self.memory.store(*self.transition)
    
        return next_state, reward, done

    def update_model(self):
        """
        Update the model by gradient descent.
        """
        samples = self.memory.sample_batch()

        loss = self._compute_dqn_loss(samples)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()
        
    def train(self, num_frames, plotting_interval = 1000):
        """
        Train the agent.
        """
        self.is_test = False
        
        state, _ = self.env.reset(seed = self.seed)
        update_cnt = 0
        epsilons = []
        losses = []
        scores = []
        score = 0

        for frame_idx in range(1, num_frames + 1):
            # At the halfway point, reduce learning rate by a tenth
            if frame_idx == int(num_frames // 2):
                adjust_learning_rate(self.optimizer, 0.1)

            action = self.select_action(state)
            next_state, reward, done = self.step(action)

            state = next_state
            score += reward

            # Exponentially decrease epsilon
            self.epsilon = self.min_epsilon + (self.max_epsilon - self.min_epsilon) * np.exp(- self.epsilon_decay * frame_idx)
            epsilons.append(self.epsilon)

            # If episode ends
            if done:
                state, _ = self.env.reset(seed = self.seed)
                scores.append(score)
                score = 0

            # If training is ready
            if len(self.memory) >= self.batch_size:
                loss = self.update_model()
                losses.append(loss)
                update_cnt += 1

                # If hard update is needed
                if update_cnt % self.target_update == 0:
                    self._target_hard_update()

            # Plot and save results, and save models
            if frame_idx % plotting_interval == 0:
                self._plot(scores, losses, epsilons)
                self._save(scores, losses, epsilons)

                print(f"Frame: {frame_idx}, Mean of last 10 rewards: {np.mean(scores[-10:])}")

                # Create checkpoint folder
                if not os.path.exists("checkpoints"):
                    os.makedirs("checkpoints")

                # Save the model checkpoint
                checkpoint_name = f"checkpoint_simple_dqn_latest.pth.tar"
                checkpoint_path = os.path.join("checkpoints", checkpoint_name)
                torch.save({"current_model": self.dqn.state_dict(), "target_model": self.dqn_target.state_dict(), "optimizer": self.optimizer.state_dict(), "losses": losses, "rewards": scores, "frame": frame_idx}, checkpoint_path)

        print("Training successfully completed.")

        self.env.close()

    def test(self, video_folder = "dqn_agent_video"):
        """
        Test the agent.
        """
        self.is_test = True
        old_epsilon = self.epsilon
        self.epsilon = 0
        
        # Create checkpoint folder
        if not os.path.exists(video_folder):
            os.makedirs(video_folder)
        
        # For recording a video of agent
        naive_env = self.env
        self.env = RecordVideo(self.env, video_folder = video_folder)
        
        state, _ = self.env.reset(seed = self.seed)
        done = False
        score = 0
        
        while not done:
            action = self.select_action(state)
            next_state, reward, done = self.step(action)

            state = next_state
            score += reward
        
        print("Score: ", score)
        self.env.close()
        
        # Reset
        self.env = naive_env
        self.epsilon = old_epsilon

    def _compute_dqn_loss(self, samples):
        """
        Return DQN loss.
        """
        state = torch.tensor(samples["obs"], dtype = torch.float, device = self.device).to(self.device)
        next_state = torch.tensor(samples["next_obs"], dtype = torch.float, device = self.device).to(self.device)
        action = torch.tensor(samples["acts"].reshape(-1, 1), dtype = torch.long, device = self.device).to(self.device)
        reward = torch.tensor(samples["rews"].reshape(-1, 1), dtype = torch.float, device = self.device).to(self.device)
        done = torch.tensor(samples["done"].reshape(-1, 1), dtype = torch.float, device = self.device).to(self.device)

        curr_q_value = self.dqn(state).gather(1, action)
        next_q_value = self.dqn_target(next_state).max(dim = 1, keepdim = True)[0].detach()
        mask = 1 - done
        target = (reward + self.gamma * next_q_value * mask).to(self.device)

        # Calculate DQN loss
        loss = F.smooth_l1_loss(curr_q_value, target)

        return loss

    def _target_hard_update(self):
        """
        Hard update: target <- local.
        """
        self.dqn_target.load_state_dict(self.dqn.state_dict())

    def _save(self, rewards, losses, epsilons):
        """
        Save training results to a pickle file.
        """
        # Save results to a file
        with open("simple-dqn-results.pkl", "wb") as f:
            pickle.dump(rewards, f)
            pickle.dump(losses, f)
            pickle.dump(epsilons, f)

    def _plot(self, rewards, losses, epsilons, moving_average_window = 100):
        """
        Plot training curves.
        """
        plt.figure(figsize = (40, 6))
        
        # Combined plot of rewards, moving average, loss, and epsilons
        plt.subplot(131)
        plt.title("DQN Rewards Per Episode")
        plt.plot(rewards, label = "Reward")
        if len(rewards) >= moving_average_window:
            plt.plot(moving_average(rewards, moving_average_window), label = "Moving Average", color = "red")
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.legend()
        
        plt.subplot(132)
        plt.title("DQN Loss and Epsilon Per Frame")
        plt.plot(losses, label = "DQN Loss", color = "tab:blue")
        plt.xlabel("Frame")
        plt.ylabel("Loss", color = "tab:blue")
        plt.tick_params(axis = "y", labelcolor = "tab:blue")
        plt.legend(loc = "upper left")
        
        ax2 = plt.gca().twinx()
        ax2.plot(epsilons, label = "Epsilon", color = "tab:red")
        ax2.set_ylabel("Epsilon", color = "tab:red")
        ax2.tick_params(axis = "y", labelcolor = "tab:red")
        ax2.legend(loc = "upper right")
        
        plt.savefig("simple_dqn_plot.pdf")
        plt.close()

    def _load_checkpoint(self, checkpoint_path, include_optimiser = True):
        """
        Load the models from a checkpoint.
        """
        model = torch.load(checkpoint_path, map_location = self.device)
        self.dqn.load_state_dict(model["current_model"])
        self.dqn_target.load_state_dict(model["target_model"])
        
        if include_optimiser == True:
            self.optimizer.load_state_dict(model["optimizer"])

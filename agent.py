import torch
import random
import numpy as np
from collections import deque
from game import DinoGame
from model import Linear_QNet, QTrainer
from helper import plot


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(6, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):
        try:
            i=0
            
            for obstacle in game.obstacles:
                if obstacle.rect.x > 160:
                    if i==0:
                        min = game.obstacles[0].rect.x
                        min_obstacle = game.obstacles[0]
                    if obstacle.rect.x < min:
                        min = obstacle.rect.x
                        min_obstacle=game.obstacles[0]
                    i+=1

            state = [
                min_obstacle.rect.x<500 and min_obstacle.rect.x>450,
                min_obstacle.rect.x<450 and min_obstacle.rect.x>400,
                min_obstacle.rect.x<400,


                #min_obstacle.type==0,
                min_obstacle.family==0,
                min_obstacle.family==1,
                min_obstacle.family==2
                ]

        except:
            state = [
                False,
                False,
                False,
                False,
                False,
                False
                ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 100 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move



def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = DinoGame()
    reward=0
    while True:
        state_old = agent.get_state(game)
        action = agent.get_action(state_old)
        collision,score,reward0 = game.play_step(action)
        reward+=game.check_reward(collision)
        if bool(action[2]):
            reward -= 0.001
        print(state_old, collision, "Score:",score, "Reward", reward)
        state_new = agent.get_state(game)
        agent.train_short_memory(state_old, action, reward, state_new, collision)
        agent.remember(state_old, action, reward, state_new, collision)
        if collision:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            reward=0

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

train()


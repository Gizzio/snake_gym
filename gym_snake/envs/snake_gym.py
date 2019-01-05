import gym
from gym_snake.envs.snake import Game, Renderer, Input
from gym import spaces
H = 30
W = 30
dim = 2
# TODO: add observation space and action space


class SnakeEnv(gym.Env):
    def __init__(self):
        self.game = Game(h=H, w=W)
        self.renderer = Renderer(self.game)
        self.input = Input()
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=1, shape=(H, W, dim))

    def step(self, action: int):
        self._take_action(action)
        reward = self._get_reward()
        observation = self._get_state()
        episode_over = self._is_over()

        return observation, reward, episode_over, {}

    def reset(self):
        self.game = Game(h=H, w=W)
        self.renderer.set_game(self.game)
        return self._get_state()

    def _render(self, mode, close):
        # TODO: change mode
        self.renderer.render_frame()
        # return self._get_state()

    def _take_action(self, action):
        d = self.input.translate(action)
        self.game.input(d)
        pass

    def _is_over(self):
        self.game.has_ended()
        pass

    def _get_state(self):
        self.game.get_state()

    def _get_reward(self):
        return self.game.snake.has_eaten

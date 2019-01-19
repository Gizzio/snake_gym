import gym
from gym_snake.envs.snake import Game, Renderer, Input, KeyboardInput
from gym import spaces

dim = 1
H = 10
W = 10


class SnakeEnv(gym.Env):
    def __init__(self, human_mode=False):
        self.game = Game(h=H, w=W)
        self.human_mode = human_mode
        if human_mode:
            self.renderer = Renderer(self.game)
            self.keyboard_input=KeyboardInput(self.renderer.window)
        self.input = Input()
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0, high=4, shape=(dim, H, W), dtype=int)

    def step(self, action: int):
        self._take_action(action)
        self.game.update()
        reward = self._get_reward()
        observation = self._get_state()
        episode_over = self._is_over()
        if self.human_mode:
            self._refresh_board()

        return observation, reward, episode_over, {}

    def reset(self):
        self.game = Game(h=H, w=W)
        if self.human_mode:
            self.renderer.set_game(self.game)
        return self._get_state()

    def _refresh_board(self):
        #clearing input buffer
        _ = self.keyboard_input.get_input()
        self.renderer.render_frame()
        if self.game.has_ended():
            self.renderer.close_window()
                   
    def _take_action(self, action):
        d = self.input.translate(action)
        self.game.input(d)

    def _is_over(self):
        return self.game.has_ended()

    def _get_state(self):
        return self.game.get_state()

    def _get_reward(self):
        return self.game.snake.has_eaten

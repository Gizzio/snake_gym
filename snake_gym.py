import gym
from snake import Game, Renderer, Input


class SnakeEnv(gym.Env):
    def __init__(self):
        self.renderer = Renderer()
        self.input = Input()
        pass

    def _step(self, action):
        self._take_action(action)
        reward = self._get_reward()
        observation = self._get_state()
        episode_over = self._is_over()

        return observation, reward, episode_over, {}

    def _reset(self):
        self.game = Game()
        return self._get_state()

    def _render(self, mode, close):
        # TODO: change mode
        self.renderer.render(self.game.changed_tiles)
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

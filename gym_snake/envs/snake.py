from typing import NamedTuple
import random

import numpy as np
import curses

X_START = 4
Y_START = 4

WALL = '#'
SNAKE = 'S'
HEAD = 'h'
FOOD = '@'

state_representation = {
    WALL: 1,
    SNAKE: 2,
    HEAD: 3,
    FOOD: 4
}


def trans_dir(i):
    # TODO: change to constants
    return {
        'U': (0, -1),
        'R': (1, 0),
        'D': (0, 1),
        'L': (-1, 0)
    }[i]


class Point(NamedTuple):
    x: int
    y: int


class Tile(NamedTuple):
    position: Point
    kind: str


class Food(NamedTuple):
    tile: Tile


class Game():
    def __init__(self, h, w):
        self.objects = []
        self.snake = Snake(X_START, Y_START)
        self.boardH = h
        self.boardW = w
        self.food = Tile(self._random_empty_position(), FOOD)
        self.newfood = [self.food]

    @property
    def changed_tiles(self) -> list:
        tiles = self.snake.changed_tiles
        return tiles+self.newfood

    @property
    def tiles(self) -> list:
        tiles = []
        for tile in self.snake.tiles:
            tiles.append(tile)
        tiles.append(self.food)

        return tiles

    def get_observation(self) -> np.array:
        observation = np.zeros((self.boardW, self.boardH))
        if self.has_ended():
            return observation

        for i in range(0, self.boardH):
            observation[0][i] = state_representation[WALL]
            observation[-1][i] = state_representation[WALL]

        for i in range(0, self.boardW):
            observation[i][0] = state_representation[WALL]
            observation[i][-1] = state_representation[WALL]

        for point in self.snake.get_points():
            observation[point.x][point.y] = state_representation[SNAKE]

        head_x, head_y = self.snake.head
        observation[head_x][head_y] = state_representation[HEAD]
        observation[self.food.position.x][self.food.position.y] = state_representation[FOOD]

        return observation

    def has_ended(self):
        return not self.snake.is_alive

    def input(self, input: str):
        self.snake.change_direction(trans_dir(input))

    def update(self):
        self.newfood = []
        self.snake.update()
        self._check_for_eating()
        self._check_colisions()

    def _check_for_eating(self):
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            del self.food
            new_position = self._random_empty_position()
            self.spawn_food(new_position)

    def _check_colisions(self):
        head = self.snake.head
        if self._wall_collision(head) or self._snake_collision(head):
            self.snake.die()

    def _wall_collision(self, head):
        if head.x == 0 or head.x == self.boardH-1 or head.y == 0 or head.y == self.boardW-1:
            return True
        else:
            return False

    def _snake_collision(self, head):
        for body_part in self.snake.body[1:]:
            if body_part.x ==head.x and body_part.y == head.y:
                return True
        return False

    def spawn_food(self, position):
        self.food = Tile(position, FOOD)
        self.newfood = [self.food]

    def _random_empty_position(self):
        snake_points = self.snake.get_points()
        not_empty = True
        while not_empty:
            x = np.random.randint(1,self.boardW-1)
            y = np.random.randint(1,self.boardH-1)
            not_empty = False
            for point in snake_points:
                if point.x == x and point.y == y:
                    not_empty = True

        return Point(x, y)


class Snake():
    def __init__(self, x, y):
        self.has_eaten = 0
        self.is_alive = True
        self.body = self._new_body(x, y)
        self.direction = (0, -1)
        self.changed_tiles = []

    @property
    def tiles(self) -> list:
        tiles = []

        for point in self.body:
            tiles.append(Tile(point, SNAKE))

        return tiles

    def _new_body(self, x, y):
        return [Point(x, y),
                Point(x, y+1),
                Point(x, y+2)]

    def change_direction(self, new_dir):
        #change direction only when not trying to go backward
        if self.direction != (-new_dir[0], -new_dir[1]):
            self.direction = new_dir

    def update(self):
        self.changed_tiles = []
        self._move()

    def _move(self):
        direction_x, direction_y = self.direction
        # adding direction point-wise
        new_head = Point(self.head.x + direction_x,
                         self.head.y + direction_y)
        self.body.insert(0, new_head)
        self.changed_tiles.append(Tile(new_head, SNAKE))
        if not self.has_eaten:
            self.changed_tiles.append(Tile(self.body[-1], ' ')) #removing last element of body from screen
            del self.body[-1] 

        self.has_eaten = 0

    def grow(self):
        self.has_eaten = 1

    def die(self):
        self.is_alive = False

    def get_points(self):
        return self.body

    @property
    def head(self):
        return self.body[0]


class Renderer():
    def __init__(self, game: Game):
        h = game.boardH
        w = game.boardW
        self.game = game
        self.screen = self._init_screen()
        self.window = self._init_window(h, w)
        self._render_first_frame()
    
    def set_game(self, game):
        self.game=game

    def close_window(self):
        curses.endwin()

    def _init_screen(self):
        screen = curses.initscr()
        curses.curs_set(0)
        return screen

    def _init_window(self, h, w):
        window = curses.newwin(h, w, 0, 0)
        window.keypad(1)
        window.timeout(100)
        return window

    def render_frame(self):
        changed_tiles = self.game.changed_tiles
        self._display_tiles(changed_tiles)

    def _display_tiles(self, tiles):
        for tile in tiles:
            # print symbol on given position (also ' ' for removing symbols)
            self.window.addch(tile.position.y,
                              tile.position.x,
                              tile.kind)

    def _render_first_frame(self):
        tiles = self.game.tiles
        walls = self._walls()
        self._display_tiles(tiles+walls)

    def _walls(self):
        borders = []
        h = self.game.boardH
        w = self.game.boardW
        # borders.append(Point(29, 29)) not working, curses bug
        for i in range(h-1):
            borders.append(Point(0, i))
            borders.append(Point(w-1, i))
        for j in range(w-1):
            borders.append(Point(j, 0))
            borders.append(Point(j, h-1))
        wall_tiles = [Tile(border, WALL) for border in borders]
        return wall_tiles


class KeyboardInput():
    def __init__(self, window):
        self.window = window

    def get_input(self):
        direction = self.translate_input(self.window.getch())
        return direction

    def translate_input(self, i):
        return {
            curses.KEY_UP: 'U',
            curses.KEY_RIGHT: 'R',
            curses.KEY_DOWN: 'D',
            curses.KEY_LEFT: 'L',
            -1: None
        }[i]


class Input():
    def __init__(self):
        pass
    
    def translate(self, action: int):
        return {
        0: 'U',
        1: 'R',
        2: 'D',
        3: 'L'
    }[action]


from typing import NamedTuple
import random

import numpy as np
import curses


class Point(NamedTuple):
    x: int
    y: int


class Tile(NamedTuple):
    position: Point
    kind: str


class Food(NamedTuple):
    tile: Tile


WALL = '#'
SNAKE = 'S'
HEAD = 'h'
FOOD = '@'
state_representation = {
    WALL: 1,
    SNAKE: 10,
    HEAD: 50
}

X_START = 4
Y_START = 4

# przenieść do Input


def trans_dir(i):
    # TODO: change to constants
    return {
        'U': (0, -1),
        'R': (1, 0),
        'D': (0, 1),
        'L': (-1, 0)
    }[i]


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

    def get_state(self) -> np.array:
        sstate = np.zeros((self.boardW, self.boardH))
        hstate = np.zeros_like(sstate)
        head_x, head_y = self.snake.get_points()[0]

        if self.has_ended():
            return np.array((sstate, sstate))

        for i in range(0, self.boardH):
            sstate[0][i] = state_representation[WALL]
            sstate[-1][i] = state_representation[WALL]

        for i in range(0, self.boardW):
            sstate[i][0] = state_representation[WALL]
            sstate[i][-1] = state_representation[WALL]

        for point in self.snake.get_points():
            sstate[point.x][point.y] = state_representation[SNAKE]

        sstate[head_x][head_y] = state_representation[HEAD]
        fstate = np.zeros_like(sstate)
        fstate[self.food.position.x][self.food.position.y] = 1

        return np.array((sstate, fstate))

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
        head = self.snake.body[0]
        if self._wall_collision(head) or self._snake_collision(head):
            self.snake.die()

    def _wall_collision(self, head):
        if head.x == 0 or head.x == self.boardH-1 or head.y == 0 or head.y == self.boardW-1:
            return True
        else:
            return False

    def _snake_collision(self, head):
        # TODO
        for body_part in self.snake.body[1:]:
            if body_part.x ==head.x and body_part.y == head.y:
                return True
        return False

    def spawn_food(self, position):
        self.food = Tile(position, FOOD)
        self.newfood = [self.food]

    def _random_empty_position(self):
        # TODO: checking if point is empty
        x = random.randrange(self.boardW-2)+1
        y = random.randrange(self.boardH-2)+1
        return Point(y, x)


class Snake():
    def __init__(self, x, y):
        self.has_eaten = 0
        self.is_alive = True
        self.body = self._new_body(x, y)
        self.direction = (1, 0)
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
        self.direction = new_dir

    def update(self):
        self.changed_tiles = []
        self._move()

    def _move(self):
        d = self.direction
        # adding direction point-wise
        new_head = Point(self.body[0].x + d[0], self.body[0].y + d[1])
        self.body.insert(0, new_head)
        self.changed_tiles.append(Tile(new_head, SNAKE))
        if not self.has_eaten:
            self.changed_tiles.append(Tile(self.body[-1], ' '))
            del self.body[-1]

        self.has_eaten = 0

    def grow(self):
        self.has_eaten = 1

    def die(self):
        self.is_alive = False

    def get_points(self):
        return self.body


class Renderer():
    def __init__(self, game: Game):
        h = game.boardH
        w = game.boardW
        self.game = game
        self.screen = self.init_screen()
        self.window = self.init_window(h, w)
        self._render_first_frame()
    
    def set_game(self, game):
        self.game=game

    def close_window(self):
        curses.endwin()

    def init_screen(self):
        screen = curses.initscr()
        curses.curs_set(0)
        return screen

    def init_window(self, h, w):
        window = curses.newwin(h, w, 0, 0)
        window.keypad(1)
        window.timeout(100)
        return window

    def render_frame(self):
        changed_tiles = self.game.changed_tiles
        self.add_tiles(changed_tiles)

    def add_tiles(self, tiles):
        for tile in tiles:
            position = tile.position
            # print symbol on given position (also ' ' for removing symbols)
            self.window.addch(position.y, position.x, tile.kind)

    def _render_first_frame(self):
        tiles = self.game.tiles
        walls = self._walls()
        self.add_tiles(tiles+walls)

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


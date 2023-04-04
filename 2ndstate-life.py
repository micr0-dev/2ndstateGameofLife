import pygame
import numpy as np
import random
import math
from multiprocessing import Process, Queue


# Reused code from From MiraslauKavaliou/SimuPy/physics.py
class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def one():
        return Vector2(1, 1)

    def zero():
        return Vector2()

    def up():
        return Vector2(0, 1)

    def down():
        return Vector2(0, -1)

    def left():
        return Vector2(1, 0)

    def right():
        return Vector2(-1, 0)

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, num: int):
        return Vector2(self.x * num, self.y * num)

    def __truediv__(self, num: int):
        return Vector2(self.x / num, self.y / num)

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __pow__(self, num: int):
        return Vector2(self.x**num, self.y**num)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def sqrMagnitude(self):
        return self.x**2 + self.y**2

    def dist(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def normalized(self):
        magTemp = self.magnitude()
        return Vector2(self.x / magTemp, self.y / magTemp)

    def angle(self):
        if self.x == 0:
            if self.y > 0:
                return math.pi / 2
            elif self.y < 0:
                return -math.pi / 2
            else:
                return 0
        else:
            return math.atan(self.y / self.x)

    def rotate_ip(self, angle):
        # Rotate this vector by the given angle (in degrees) in place.
        angle_radians = math.radians(angle)
        cos_theta = math.cos(angle_radians)
        sin_theta = math.sin(angle_radians)
        x = self.x * cos_theta - self.y * sin_theta
        y = self.x * sin_theta + self.y * cos_theta
        self.x = x
        self.y = y

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def tuple(self):
        return (self.x, self.y)


# Initialize Pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 200, 200
CELL_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Create the grid
grid = np.zeros((ROWS, COLS))

boxPos = -Vector2.one()
boxSize = Vector2.zero()


def whiteNoise(grid, percent=0.5):
    for y in range(ROWS):
        for x in range(COLS):
            if random.random() < percent:
                grid[y][x] = 1
            else:
                grid[y][x] = 0


def draw(window, grid):
    window.fill(WHITE)

    for i in range(ROWS):
        for j in range(COLS):
            rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE,
                               CELL_SIZE, CELL_SIZE)
            if grid[i][j] == 1:
                pygame.draw.rect(window, BLACK, rect)
            if grid[i][j] == 2:
                pygame.draw.rect(window, RED, rect)
            # pygame.draw.rect(window, WHITE, rect, 1)


def rules(new_grid, grid, i, j):
    # total = np.sum(
    #     grid[(i - 1): (i + 2), (j - 1): (j + 2)]) - grid[i, j]
    total = 0
    for r in range(-1, 2):
        for c in range(-1, 2):
            b = i+r
            v = j+c
            if b < 0 or v < 0 or b > len(grid)-1 or v > len(grid[0])-1:
                continue
            # elif grid[b][v] != 0:
            #     total += 1
            else:
                total += grid[b][v]
    total -= grid[i, j]
    if grid[i, j] == 1 and (total < 2 or total > 3):
        new_grid[i, j] = 0
    elif grid[i, j] == 1 and total == 2:
        new_grid[i, j] = 2
    elif grid[i, j] == 0 and total == 3:
        new_grid[i, j] = 1


def update_grid(grid):
    new_grid = grid.copy()

    threads = []

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            rules(new_grid, grid, i, j)
            # p.start()
            # threads.append(p)

    # print(len(threads))
    # for t in threads:
    #     t.join()
    return new_grid


def trim_grid(grid):
    new_grid = np.zeros(boxSize.tuple())

    for y in range(len(new_grid)):
        for x in range(len(new_grid[0])):
            try:
                new_grid[y][x] = grid[y+boxPos.y][x+boxPos.x]
            except IndexError:
                pass
    return new_grid


def rescale_grid(grid):
    new_grid = np.zeros((ROWS, COLS))

    for y in range(len(grid)):
        for x in range(len(grid[0])):

            try:
                new_grid[y+boxPos.y][x+boxPos.x] = grid[y][x]
            except IndexError:
                pass

    return new_grid


def set(grid, x, y, value):
    global boxPos, boxSize
    grid[x, y] = value

    return grid


def flip(grid, x, y):
    set(grid, x, y, not grid[x, y])


def compute_box_size(grid):
    global boxPos, boxSize
    min_x, min_y, max_x, max_y = ROWS, COLS, 0, 0

    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] != 0:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    boxPos = Vector2(min_x - 1, min_y - 1)
    boxSize = Vector2(max_x - min_x + 3, max_y - min_y + 3)

    if boxPos.x > COLS:
        boxPos.x = COLS
    if boxPos.y > ROWS:
        boxPos.y = ROWS
    if boxPos.x < 0:
        boxPos.x = 0
    if boxPos.y < 0:
        boxPos.y = 0

    if boxSize.x+boxPos.x > COLS:
        boxSize.x = COLS-boxPos.x
    if boxSize.y+boxPos.y > ROWS:
        boxSize.y = ROWS-boxPos.y
    if boxSize.x < 0:
        boxSize.x = 0
    if boxSize.y < 0:
        boxSize.y = 0


def main():
    global grid, boxPos, boxSize
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2nd State Game of Life")
    clock = pygame.time.Clock()

    running = True
    paused = True

    showBoundingBox = False

    while running:
        clock.tick(6000)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_r:
                    paused = True
                    grid = np.zeros((ROWS, COLS))
                if event.key == pygame.K_w:
                    whiteNoise(grid, 0.5)
                    compute_box_size(grid)
                if event.key == pygame.K_b:
                    showBoundingBox = not showBoundingBox

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                row, col = y // CELL_SIZE, x // CELL_SIZE
                flip(grid, row, col)

                compute_box_size(grid)

        if not paused:
            trimmed_grid = trim_grid(grid)
            updated_trimmed_grid = update_grid(trimmed_grid)
            grid = rescale_grid(updated_trimmed_grid)
            compute_box_size(grid)

        draw(window, grid)

        # Draw Calculation Box
        if showBoundingBox:
            rect = pygame.Rect(boxPos.x * CELL_SIZE, boxPos.y *
                               CELL_SIZE, boxSize.x * CELL_SIZE, boxSize.y * CELL_SIZE)
            pygame.draw.rect(window, GREEN, rect, 1)

        pygame.display.flip()
        print("Iterations Per Second:", clock.get_fps())

    pygame.quit()


if __name__ == "__main__":
    main()

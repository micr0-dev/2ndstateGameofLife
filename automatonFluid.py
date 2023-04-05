import pygame
import numpy as np
import random
import math
import imageio
import os


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
ROWS, COLS = 80, 80
CELL_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
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
            # Clip the value to the range of [-1, 1]
            value = np.clip(grid[i, j], -1, 1)
            # Map the value from [-1, 1] to [0, 255]
            color_value = int(127.5 * (value + 1))
            pygame.draw.rect(
                window, (color_value, color_value, color_value), rect)


def save_frame(window, frame_number):
    pygame.image.save(window, f"frame_{frame_number:04d}.png")


def update_grid(grid, prev_grid, dt=0.1, speed=1):
    new_grid = np.zeros_like(grid)
    rows, cols = grid.shape

    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            laplacian = (
                grid[i - 1, j] + grid[i + 1, j] +
                grid[i, j - 1] + grid[i, j + 1]
                - 4 * grid[i, j]
            )
            acceleration = speed ** 2 * laplacian
            new_grid[i, j] = 2 * grid[i, j] - \
                prev_grid[i, j] + dt ** 2 * acceleration

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
    margin = 2

    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] != 0:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    boxPos = Vector2(min_x - margin, min_y - margin)
    boxSize = Vector2(max_x - min_x + 1 + 2 * margin,
                      max_y - min_y + 1 + 2 * margin)

    boxPos.x = max(0, min(boxPos.x, COLS))
    boxPos.y = max(0, min(boxPos.y, ROWS))

    boxSize.x = max(0, min(boxSize.x, COLS - boxPos.x))
    boxSize.y = max(0, min(boxSize.y, ROWS - boxPos.y))


def main():
    global grid
    prev_grid = np.zeros_like(grid)

    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fluid Automaton")
    clock = pygame.time.Clock()

    running = True
    paused = True

    showBoundingBox = False

    runCount = 0

    frame_number = 0
    gif_mode = False

    while running:
        clock.tick(6000)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    if not paused and gif_mode:
                        print("Recording...")
                if event.key == pygame.K_r:
                    paused = True
                    grid = np.zeros((ROWS, COLS))
                    prev_grid = np.zeros_like(grid)
                    for i in range(frame_number):
                        os.remove(f"frame_{i:04d}.png")
                    frame_number = 0
                if event.key == pygame.K_w:
                    whiteNoise(grid, 0.5)
                    compute_box_size(grid)
                if event.key == pygame.K_b:
                    showBoundingBox = not showBoundingBox
                if event.key == pygame.K_g:  # Press 'g' to toggle gif_mode
                    gif_mode = not gif_mode
                    if gif_mode:
                        print("GIF mode ENABLED!")
                    else:
                        print("GIF mode DISABLED!")

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                row, col = y // CELL_SIZE, x // CELL_SIZE
                set(grid, row, col, 1)

                compute_box_size(grid)

        if not paused:
            temp_grid = grid.copy()
            grid = update_grid(grid, prev_grid, speed=3)
            prev_grid = temp_grid
            compute_box_size(grid)

            if gif_mode:
                save_frame(window, frame_number)
                frame_number += 1

        draw(window, grid)

        # Draw Calculation Box
        if showBoundingBox:
            rect = pygame.Rect(boxPos.x * CELL_SIZE, boxPos.y *
                               CELL_SIZE, boxSize.x * CELL_SIZE, boxSize.y * CELL_SIZE)
            pygame.draw.rect(window, GREEN, rect, 1)

        pygame.display.flip()

        if runCount % 20 == 0:
            print("Iterations Per Second:", clock.get_fps())
        runCount += 1

    # Create the gif
    if frame_number > 0:
        images = []
        print("Saving gif...")
        for i in range(frame_number):
            images.append(imageio.imread(f"frame_{i:04d}.png"))
            print(str(round((i/frame_number)*100, 2))+"%")

        print("Creating GIF...")
        imageio.mimsave("simulation.gif", images, fps=24)
        print("GIF created!")

        print("Deleting temp files...")
        # Remove the individual frames
        for i in range(frame_number):
            os.remove(f"frame_{i:04d}.png")
            print(str(round((i/frame_number)*100, 2))+"%")

    pygame.quit()


if __name__ == "__main__":
    main()

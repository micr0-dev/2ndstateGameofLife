import pygame
import numpy as np
import random

# Initialize Pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 160, 160
CELL_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Create the grid
grid = np.zeros((ROWS, COLS))


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
                               CELL_SIZE*1.5, CELL_SIZE*1.5)
            if grid[i][j] == 1:
                pygame.draw.rect(window, BLACK, rect)
            if grid[i][j] == 2:
                pygame.draw.rect(window, RED, rect)
            pygame.draw.rect(window, WHITE, rect, 1)


def update_grid(grid):
    new_grid = grid.copy()
    for i in range(ROWS):
        for j in range(COLS):
            total = np.sum(grid[i - 1: i + 2, j - 1: j + 2]) - grid[i, j]
            if grid[i, j] == 1 and (total < 2 or total > 3):
                new_grid[i, j] = 0
            elif grid[i, j] == 1 and total == 2:
                new_grid[i, j] = 2
            elif grid[i, j] == 0 and total == 3:
                new_grid[i, j] = 1
    return new_grid


def main():
    global grid
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Conway's Game of Life")
    clock = pygame.time.Clock()

    running = True
    paused = True

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

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                row, col = y // CELL_SIZE, x // CELL_SIZE
                grid[row, col] = not grid[row, col]

        if not paused:
            grid = update_grid(grid)

        draw(window, grid)
        pygame.display.flip()
        print("Iterations Per Second:", clock.get_fps())

    pygame.quit()


if __name__ == "__main__":
    main()

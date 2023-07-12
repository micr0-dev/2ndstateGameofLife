# 2ndstateGameofLife

2ndstateGameofLife is a unique simulation project that combines the classic game of cellular automaton known as "Conway's Game of Life" with fluid dynamics. 

The game is implemented using Pygame and numpy, and utilizes a 2D grid to represent the game state, where each cell can either be 'alive' (1) or 'dead' (0). The simulation can also be visualized as grayscale values on a Pygame window, with black representing dead cells and white representing living cells. 

Additionally, it provides the feature to save simulation frames and create a GIF, providing a dynamic visualization of how the system evolves over time.

## Features

- **Vector2 class**: Represents a 2D vector with multiple utility functions to manipulate and operate on vectors.
- **Grid system**: The simulation uses a 2D numpy array as a grid, with each cell representing an organism in the game of life. 
- **White noise**: A function to randomize the initial state of the grid.
- **Fluid Dynamics**: The project incorporates fluid dynamics into the simulation.
- **Bounding box**: Displays a bounding box around the calculation area.
- **Gif mode**: In this mode, the project saves each frame of the simulation as an image file, and then uses these frames to create a GIF of the entire simulation.

## How to use

This project uses the Pygame library to display a graphical representation of the simulation. You interact with it by using the following commands:

- **Spacebar**: Toggles the pause and play of the simulation.
- **'r' key**: Resets the simulation to an empty grid.
- **'w' key**: Fills the grid with a random noise.
- **'b' key**: Toggles the bounding box on/off.
- **'g' key**: Toggles the gif mode on/off.
- **Mouse click**: Revives a dead cell on the clicked location.

## Installation and running

This project requires `pygame`, `numpy`, and `imageio` to run. If not installed, they can be installed via pip.

```bash
pip install pygame numpy imageio
```

To run the program, navigate to the directory containing the Python scripts and execute:

```bash
python main.py
```

## License

This project is licensed under the terms of the MIT license.

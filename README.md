# Cell Evolution Simulation

This script simulates "cells", each containing its own "genetic code". It observes how these cells learn movement patterns and behaviors based on interactions with threats and homes in their environment.

## Simulation Mechanics





https://github.com/user-attachments/assets/9cb8aca7-36a0-41de-b025-b8a510828a7e







- **Cells**: Each cell has a "genetic code" that dictates its behavior.
- **Genetic Code**: Cover size, lifespan, reproduction cycle, mutation rate, movement, adherence to walls - all this is reflected in the color of the cell.
- **Mutation**: For each replication iteration, the genetic code can mutate according to a mutation rate.
- **Nests (Blue Box)**:
  - Extends the cell's life span.
  - Promotes one duplication cycle.
- **Threats (Red Box)**: Kills the cells upon contact.
- **Walls (Black Box)**: Inverts cell direction.

## How to Launch

This project is managed with `uv`. To run the simulation, execute the following command in your terminal:

```bash
uv run UI_V0.1.py
```

*Note: `uv` will automatically handle the installation of dependencies (`pygame`, `numpy`) defined in `pyproject.toml`.*

## Interacting with the Simulation

- **Add Cells, Threats, Nests and Walls**: Right-click on the "+" button (i.e. +Cells) and left-click anywhere within the env. 
- **Remove Objects**:
  1. Click the **"Edit"** button to enable editing mode. Once in editing mode, right-click on item to remove it (not applicable to cells).
  2. Click **"Edit Env"** again to disable editing mode.

# Cell Evolution Simulation

This script simulates "cells", each containing its own "genetic code". It observes how these cells learn movement patterns and behaviors based on interactions with threats and homes in their environment.

## Simulation Mechanics


https://github.com/user-attachments/assets/43305f8a-85a0-44b4-af71-301df68678a2



- **Cells**: Each cell has a "genetic code" that dictates its behavior.
- **Mutation**: For each replication iteration, the genetic code can mutate according to a mutation rate.
- **Homes (Blue Box)**:
  - Lowers the mutation rate.
  - Extends the cell's life span.
  - Promotes one duplication cycle.
- **Threats (Red Box)**: Kills the cells upon contact.

## How to Launch

This project is managed with `uv`. To run the simulation, execute the following command in your terminal:

```bash
uv run UI_V0.1.py
```

*Note: `uv` will automatically handle the installation of dependencies (`pygame`, `numpy`) defined in `pyproject.toml`.*

## Interacting with the Simulation

- **Add Threats & Homes**: Right-click anywhere in the environment to create a threat (Red Box) and a home (Blue Box).
- **Add Cells**: Click the **"Add Cell"** button to generate random cells throughout the environment.
- **Remove Objects**:
  1. Click the **"Edit Env"** button to enable editing mode.
  2. Left-click on any Home or Threat you wish to eliminate.
  3. Click **"Edit Env"** again to disable editing mode.

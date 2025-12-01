# UG Dissertation  
**Topic:** Agent-Based Modelling of Microorganism Dynamics in Regenerative Environments using Boids Algorithm and Cellular Automata.

## Overview  
A hybrid ecosystem modelling framework that combines the emergent flocking behaviour of boids with the cellular automata dynamics of Conway’s Game of Life. Each boid follows the standard alignment, separation and cohesion rules of the Boids Algorithm, along with reproduction, hunger and age rules, to produce emergent behaviours for different types of food distributions as they move, forage, reproduce, and die within a continuously changing GoL environment.

## Possible applications  
- Synthetic biology-inspired behavioral modeling  
- Chemotaxis & gradient-based navigation  
- Swarm intelligence  
- Population ecology  
- Pattern-driven drug/nutrient delivery optimization  

## Food distribution types  
- Random – evenly scattered  
- Linear – edge/diagonal gradient  
- Clustered – Gaussian clusters  
- Gaussian – dense centre, sparse edges  

## Tech Stack  
- Python 3  
- Pygame  
- Matplotlib  
- CSV  

## Repository Structure  
```
/project-root/
├── Core/
│   ├── bacterium.py
│   ├── food.py
│   ├── simulation.py
│   ├── engine.py
│   └── utils/
│       ├── vector.py
│       └── constants.py
├── data/
│   ├── bacteria_stats.csv
│   └── visuals.png
└── ui/
    ├── ui.py
    └── slider.py
```

## How it works  

### Movement (Agents)  
Each agent updates its velocity using:

$$
\vec{v}_{\text{new}} =
w_a \cdot \vec{v}_{\text{alignment}} +
w_c \cdot \vec{v}_{\text{cohesion}} +
w_s \cdot \vec{v}_{\text{separation}} +
w_f \cdot \vec{v}_{food\\_attraction}
$$

### Environment (GoL)  
Food distributions evolve every N steps according to standard GoL rules.

### Lifecycle of Agents  
- Agents lose energy over time  
- Gain energy when consuming food  
- Die if starved or too old  
- Reproduce when conditions are favourable  

## How to run  
`python3 engine.py`

Prompts will appear to set:  
- Number of agents  
- Food distribution type  

On-screen sliders can be used to modify real-time behaviour.  
CSV logs will allow long-run analysis and graph generation.

## Contributors  
`Sayan Saha` `Shubhamita Banerjee`

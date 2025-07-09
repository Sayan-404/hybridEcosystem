# simulation.py

import pygame
import random
from datetime import datetime

from utils.constants import *
from utils.vector import Vector2D
from core.food import FoodCell
from core.bacterium import Bacterium
from utils.slider import Slider

import math 
import csv 
import os 

class EcosystemSimulation:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bacteria Ecosystem Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.show_grid = True  # Add this line to control grid visibility

        # Simulation state
        self.step_count = 1
        self.bacteria_list = []
        self.food_grid = []
        self.food_distribution = "cluster"  # "random" or "cluster"
        
        self.food_distribution_modes = ["random", "cluster", "gaussian", "linear"]
        self.food_distribution_index = FOOD_INDEX
        self.food_distribution = self.food_distribution_modes[self.food_distribution_index]

        # Statistics
        self.total_births = 0
        self.total_deaths = 0
        self.food_births = 0
        self.food_deaths = 0
        self.population_history = []
        self.food_history = []
        
        # Initialize food grid
        self.init_food_grid()
        
        # Initialize bacteria
        self.init_bacteria()
        
        # Initialize UI
        self.init_ui()
        
        # Font for UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    
    def  init_food_grid(self):
        # print(self.food_distribution)
        grid_width = SIM_WIDTH // GRID_SIZE     # Number of columns
        grid_height = SCREEN_HEIGHT // GRID_SIZE  # Number of rows

        # Initialize grid with dead food cells
        self.food_grid = [[FoodCell(x, y) for y in range(grid_height)]
                        for x in range(grid_width)]


        for x in range(grid_width):
            for y in range(grid_height):
                self.food_grid[x][y].alive = False
                self.food_grid[x][y].age = 0
        if self.food_distribution == "random":

            for x in range(grid_width):
                for y in range(grid_height):
                    if random.random() < 0.3:
                        self.food_grid[x][y].alive = True
                        self.food_grid[x][y].age = random.randint(0, 50)
                    else:
                        self.food_grid[x][y].alive = False

        elif self.food_distribution == "cluster":
            num_clusters = 10
            cluster_radius = 3
            
            for i in range(num_clusters):
                # print(i)
                # Ensure cluster center is far enough from edges to fit the entire cluster
                center_x = random.randint(cluster_radius, grid_width - cluster_radius - 1)
                center_y = random.randint(cluster_radius, grid_height - cluster_radius - 1)

                # Create the center cell
                self.food_grid[center_x][center_y].alive = True
                self.food_grid[center_x][center_y].age = random.randint(50, 100)
                
                # print(self.food_grid[center_x][center_y].alive)
                # Create cluster around center
                for _ in range(20):  # Increased attempts for better cluster density
                    # Generate random offset within cluster radius
                    dx = random.randint(-cluster_radius, cluster_radius)
                    dy = random.randint(-cluster_radius, cluster_radius)
                    
                    x = center_x + dx
                    y = center_y + dy
                    
                    # Double-check bounds (should be safe with our center selection)
                    if 0 <= x < grid_width and 0 <= y < grid_height:
                        self.food_grid[x][y].alive = True
                        self.food_grid[x][y].age = random.randint(0, 50)
                # print(self.food_grid)
        
        elif self.food_distribution == "gaussian":
            center_x = grid_width // 2
            center_y = grid_height // 2
            sigma = min(grid_width, grid_height) / 4  # standard deviation

            for x in range(grid_width):
                for y in range(grid_height):
                    # Gaussian function
                    dx = x - center_x
                    dy = y - center_y
                    exponent = -(dx ** 2 + dy ** 2) / (2 * sigma ** 2)
                    probability = math.exp(exponent)

                    if random.random() < probability:
                        self.food_grid[x][y].alive = True
                        self.food_grid[x][y].age = int(probability * 100)

        elif self.food_distribution == "linear":
            for x in range(grid_width):
                for y in range(grid_height):
                    # Food more likely near the top-left, decreasing diagonally
                    probability = 1 - ((x + y) / (grid_width + grid_height))
                    if random.random() < probability:
                        self.food_grid[x][y].alive = True
                        self.food_grid[x][y].age = int(probability * 100)
                    
    def init_bacteria(self):
        self.bacteria_list = []
        for _ in range(BOIDS):  # Initial population
            x = random.randint(0, SIM_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            self.bacteria_list.append(Bacterium(x, y))
    
    def init_ui(self):
        slider_x = SIM_WIDTH + 10
        slider_y = 50
        slider_height = 20
        slider_width = 200
        spacing = 60
        
        self.sliders = {
            'alignment': Slider(slider_x, slider_y, slider_width, slider_height, 
                              0.0, 3.0, 0.5, "Alignment"),
            'cohesion': Slider(slider_x, slider_y + spacing, slider_width, slider_height, 
                             0.0, 3.0, 1.0, "Cohesion"),
            'separation': Slider(slider_x, slider_y + 2*spacing, slider_width, slider_height, 
                               0.0, 3.0, 1.0, "Separation"),
            'food_attraction': Slider(slider_x, slider_y + 3*spacing, slider_width, slider_height, 
                                    0.0, 3.0, 1.5, "Food Attraction"),
            'max_speed': Slider(slider_x, slider_y + 4*spacing, slider_width, slider_height, 
                              0.5, 5.0, 2.0, "Max Speed")
            
        }
    
    def update_food_grid(self):
        # Conway's Game of Life every 20 steps
        if self.step_count % 500 == 0:
            self.apply_conway_rules()
        
        # Age all food cells
        for row in self.food_grid:
            for cell in row:
                if cell.alive:
                    cell.age += 0.5

    def apply_conway_rules(self):
        grid_width = len(self.food_grid)
        grid_height = len(self.food_grid[0])
        
        # Calculate next state for each cell
        for x in range(grid_width):
            for y in range(grid_height):
                neighbors = self.count_neighbors(x, y)
                
                if self.food_grid[x][y].alive:
                    # Living cell rules
                    if neighbors < 2 or neighbors > 3:
                        self.food_grid[x][y].next_state = False
                    else:
                        self.food_grid[x][y].next_state = True
                else:
                    # Dead cell rules
                    if neighbors == 3:
                        self.food_grid[x][y].next_state = True
                    else:
                        self.food_grid[x][y].next_state = False
        
        # Apply next state
        for x in range(grid_width):
            for y in range(grid_height):
                if self.food_grid[x][y].alive != self.food_grid[x][y].next_state:
                    if self.food_grid[x][y].next_state:
                        self.food_births += 1
                        self.food_grid[x][y].density = 100.0
                        self.food_grid[x][y].age = 0
                    else:
                        self.food_deaths += 1
                
                self.food_grid[x][y].alive = self.food_grid[x][y].next_state
    
    def count_neighbors(self, x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = x + dx, y + dy
                if (0 <= nx < len(self.food_grid) and 
                    0 <= ny < len(self.food_grid[0]) and
                    self.food_grid[nx][ny].alive):
                    count += 1
        return count
    
    def update_bacteria(self):
        # Get boids parameters from sliders
        boids_params = {
            'alignment': self.sliders['alignment'].val,
            'cohesion': self.sliders['cohesion'].val,
            'separation': self.sliders['separation'].val,
            'food_attraction': self.sliders['food_attraction'].val
        }
        
        # Update max speed for all bacteria
        max_speed = self.sliders['max_speed'].val
        for bacterium in self.bacteria_list:
            bacterium.max_speed = max_speed
        
        # Update bacteria
        for bacterium in self.bacteria_list:
            bacterium.update(self.bacteria_list, self.food_grid, boids_params)
        
        # Handle reproduction
        new_bacteria = []
        for bacterium in self.bacteria_list:
            if bacterium.should_reproduce():
                # Binary fission
                new_x = bacterium.position.x + random.uniform(-20, 20)
                new_y = bacterium.position.y + random.uniform(-20, 20)
                new_bacterium = Bacterium(new_x, new_y)
                new_bacterium.hunger = 50  # Start with moderate hunger
                new_bacteria.append(new_bacterium)
                bacterium.hunger = 50  # Reset parent's hunger
                self.total_births += 1
        
        self.bacteria_list.extend(new_bacteria)
        
        # Remove dead bacteria
        alive_bacteria = [b for b in self.bacteria_list if b.alive]
        self.total_deaths += len(self.bacteria_list) - len(alive_bacteria)
        self.bacteria_list = alive_bacteria
    
    def update_statistics(self):
        bacteria_count = len([b for b in self.bacteria_list if b.alive])
        food_count = sum(1 for row in self.food_grid for cell in row if cell.alive)
        
        self.population_history.append(bacteria_count)
        self.food_history.append(food_count)
        
        # Keep only last 200 data points for graph
        if len(self.population_history) > 200:
            self.population_history.pop(0)
        if len(self.food_history) > 200:
            self.food_history.pop(0)
    

    def save_statistics(self):
        # Save every 100 steps
        if self.step_count % 100 != 0:
            return

        filename = "bacteria_stats.csv"
        file_exists = os.path.exists(filename)

        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header only once
            if not file_exists:
                writer.writerow(['Step', 'Bacteria Population', 'Food Population',
                                'Total Births', 'Total Deaths', 'Food Births', 'Food Deaths'])

            bacteria_count = len([b for b in self.bacteria_list if b.alive])
            food_count = sum(1 for row in self.food_grid for cell in row if cell.alive)

            writer.writerow([self.step_count, bacteria_count, food_count,
                            self.total_births, self.total_deaths,
                            self.food_births, self.food_deaths])

    def draw_grid(self, surface):
        if not self.show_grid:
            return

        # Create a transparent surface for grid
        grid_surface = pygame.Surface((SIM_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        grid_color = (255, 255, 0, 60)  # Yellow with ~25% opacity

        for row in range(1, GRID_HEIGHT):
            pygame.draw.line(grid_surface, grid_color, (0, row * GRID_SIZE), (SIM_WIDTH, row * GRID_SIZE))

        for col in range(1, GRID_WIDTH):
            pygame.draw.line(grid_surface, grid_color, (col * GRID_SIZE, 0), (col * GRID_SIZE, SCREEN_HEIGHT))

        # Blit grid behind everything else
        surface.blit(grid_surface, (0, 0))

    def draw_food_grid(self):
        for x in range(len(self.food_grid)):
            for y in range(len(self.food_grid[0])):
                cell = self.food_grid[x][y]
                if cell.alive:
                    rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                    pygame.draw.rect(self.screen, cell.get_color(), rect)

    
    def draw_bacteria(self):
        for bacterium in self.bacteria_list:
            bacterium.draw(self.screen)
    
    def draw_ui(self):
        # Draw UI background
        ui_rect = pygame.Rect(SIM_WIDTH, 0, UI_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, ui_rect)
        
        # Draw title
        title_text = self.font.render("Bacteria Ecosystem", True, WHITE)
        self.screen.blit(title_text, (SIM_WIDTH + 10, 0))
        
        # Draw sliders
        for slider in self.sliders.values():
            slider.draw(self.screen)
        
        # Draw statistics
        stats_y = 380
        bacteria_count = len([b for b in self.bacteria_list if b.alive])
        food_count = sum(1 for row in self.food_grid for cell in row if cell.alive)
        
        stats_text = [
            f"Step: {self.step_count}",
            f"Population: {bacteria_count}",
            f"Food Cells: {food_count}",
            f"Total Births: {self.total_births}",
            f"Total Deaths: {self.total_deaths}",
            "",
            "Controls:",
            "SPACE - Pause/Resume","R - Reset simulation",
            "F - Toggle food distribution",
            "Click sliders to adjust"
        ]
        
        for i, text in enumerate(stats_text):
            rendered_text = self.small_font.render(text, True, WHITE)
            self.screen.blit(rendered_text, (SIM_WIDTH + 10, stats_y + i * 25))
        
        # Draw population graph
        self.draw_population_graph()
    
    def draw_population_graph(self):
        graph_rect = pygame.Rect(SIM_WIDTH + 30, 650, 280, 100)
        pygame.draw.rect(self.screen, BLACK, graph_rect)
        pygame.draw.rect(self.screen, WHITE, graph_rect, 2)

        # Draw bacteria population (white line)
        if len(self.population_history) > 1:
            max_pop = max(max(self.population_history), 1)
            graph_center_y = graph_rect.y + graph_rect.height // 2
            points = []

            # Start from center of Y axis (left edge)
            points.append((graph_rect.x, graph_center_y))

            for i, pop in enumerate(self.population_history):
                x = graph_rect.x + (i / len(self.population_history)) * graph_rect.width
                scaled_value = (pop / max_pop) * (graph_rect.height // 2)
                y = graph_center_y - scaled_value
                points.append((x, y))

            pygame.draw.lines(self.screen, WHITE, False, points, 2)

        # Draw food population (red line)
        if len(self.food_history) > 1:
            max_food = max(max(self.food_history), 1)
            points = []
            for i, food in enumerate(self.food_history):
                x = graph_rect.x + (i / len(self.food_history)) * graph_rect.width
                graph_center_y = graph_rect.y + graph_rect.height // 2
                scaled_value = (pop / max_pop) * (graph_rect.height // 2)
                y = graph_center_y - scaled_value
                points.append((x, y))
            pygame.draw.lines(self.screen, RED, False, points, 2)

        # Axis labels
        label_font = pygame.font.Font(None, 20)
        y_label = label_font.render("Population", True, WHITE)
        x_label = label_font.render("Steps", True, WHITE)

        # Rotate Y label vertically (optional)
        rotated_label = pygame.transform.rotate(y_label, 90)
        label_rect = rotated_label.get_rect()
        label_rect.center = (graph_rect.x - 15, graph_rect.y + graph_rect.height // 2)
        self.screen.blit(rotated_label, label_rect)
        self.screen.blit(x_label, (graph_rect.x + graph_rect.width // 2 - 20, graph_rect.y + graph_rect.height + 10))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset_simulation()
                elif event.key == pygame.K_f:
                    self.toggle_food_distribution()
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid 
            
            # Handle slider events
            for slider in self.sliders.values():
                slider.handle_event(event)
    
    def reset_simulation(self):
        self.step_count = 1
        self.total_births = 0
        self.total_deaths = 0
        self.food_births = 0
        self.food_deaths = 0
        self.population_history = []
        self.food_history = []
        self.init_food_grid()
        self.init_bacteria()
    
    def toggle_food_distribution(self):
        self.food_distribution_index = (self.food_distribution_index + 1) % len(self.food_distribution_modes)
        self.food_distribution = self.food_distribution_modes[self.food_distribution_index]
        self.reset_simulation()

    def run(self):
        while self.running:
            self.handle_events()
            
            if not self.paused:
            #     # Update simulation
                self.update_food_grid()
                # self.update_bacteria()
                self.update_statistics()
                # self.save_statistics()
                self.step_count += 1
            
            # Draw everything
            self.screen.fill(BLACK)
            self.draw_food_grid()
            # self.draw_bacteria()
            self.draw_ui()
            self.draw_grid(self.screen)

            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
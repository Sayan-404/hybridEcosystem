# bacteria.py
import random
import math
import pygame
from utils.vector import Vector2D
from utils.constants import GRID_SIZE, SIM_WIDTH, SCREEN_HEIGHT, BLACK, BLUE
from core.food import FoodCell

class Bacterium:
    def __init__(self, x, y):
        self.position = Vector2D(x, y)
        self.velocity = Vector2D(random.uniform(-1, 1), random.uniform(-1, 1))
        self.acceleration = Vector2D(0, 0)
        self.max_speed = 2.0
        self.max_force = 0.03
        self.hunger = 50
        self.age = 0
        self.size = 6
        self.perception_radius = 50
        self.food_perception_radius = 100
        self.alive = True

    def update(self, others, food_grid, params):
        if not self.alive: return
        self.flock(others, params)
        self.seek_food(food_grid, params['food_attraction'])
        self.velocity = (self.velocity + self.acceleration).limit(self.max_speed)
        self.position = self.position + self.velocity
        self.acceleration = Vector2D(0, 0)
        self.hunger += 0.25
        self.age += 1
        if self.hunger >= 150 or self.age >= 1000:
            self.alive = False
            return
        self.consume_food(food_grid)
        self.wrap()

    def wrap(self):
        if self.position.x <= 0 or self.position.x >= SIM_WIDTH:
            self.velocity.x *= -1
            self.position.x = max(1, min(self.position.x, SIM_WIDTH - 1))
        if self.position.y <= 0 or self.position.y >= SCREEN_HEIGHT:
            self.velocity.y *= -1
            self.position.y = max(1, min(self.position.y, SCREEN_HEIGHT - 1))

    def flock(self, others, params):
        self.acceleration += self.align(others) * params['alignment']
        self.acceleration += self.cohesion(others) * params['cohesion']
        self.acceleration += self.separation(others) * params['separation']

    def align(self, others):
        total, steer = 0, Vector2D()
        for other in others:
            if other != self and other.alive:
                if (self.position - other.position).magnitude() < self.perception_radius:
                    steer += other.velocity
                    total += 1
        if total:
            steer = (steer / total).normalize() * self.max_speed - self.velocity
            return steer.limit(self.max_force)
        return Vector2D()

    def cohesion(self, others):
        total, center = 0, Vector2D()
        for other in others:
            if other != self and other.alive:
                if (self.position - other.position).magnitude() < self.perception_radius:
                    center += other.position
                    total += 1
        if total:
            desired = ((center / total) - self.position).normalize() * self.max_speed
            return (desired - self.velocity).limit(self.max_force)
        return Vector2D()

    def separation(self, others):
        total, steer = 0, Vector2D()
        for other in others:
            if other != self and other.alive:
                diff = self.position - other.position
                dist = diff.magnitude()
                if dist < self.perception_radius and dist > 0:
                    steer += diff / dist
                    total += 1
        if total:
            steer = (steer / total).normalize() * self.max_speed - self.velocity
            return steer.limit(self.max_force)
        return Vector2D()

    def seek_food(self, food_grid, attraction_strength):
        grid_x = int(self.position.x // GRID_SIZE)
        grid_y = int(self.position.y // GRID_SIZE)
        best_dist, target = float('inf'), None
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                x, y = grid_x + dx, grid_y + dy
                if 0 <= x < len(food_grid) and 0 <= y < len(food_grid[0]):
                    cell = food_grid[x][y]
                    if cell.alive:
                        fx, fy = x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2
                        dist = math.hypot(self.position.x - fx, self.position.y - fy)
                        if dist < best_dist:
                            best_dist, target = dist, Vector2D(fx, fy)
        if target:
            desired = (target - self.position).normalize() * self.max_speed
            self.acceleration += (desired - self.velocity).limit(self.max_force) * attraction_strength

    def consume_food(self, food_grid):
        gx = int(self.position.x // GRID_SIZE)
        gy = int(self.position.y // GRID_SIZE)
        if 0 <= gx < len(food_grid) and 0 <= gy < len(food_grid[0]):
            consumed = food_grid[gx][gy].consume(0.5)
            if consumed > 0:
                self.hunger = max(0, self.hunger - consumed)

    def should_reproduce(self): return self.hunger < 10 and self.alive
    def get_color(self): return BLUE if self.alive else BLACK

    def draw(self, screen):
        if not self.alive: return
        angle = math.atan2(self.velocity.y, self.velocity.x)
        tip = (self.position.x + self.size * math.cos(angle), self.position.y + self.size * math.sin(angle))
        left = (self.position.x + self.size * math.cos(angle + 2.5), self.position.y + self.size * math.sin(angle + 2.5))
        right = (self.position.x + self.size * math.cos(angle - 2.5), self.position.y + self.size * math.sin(angle - 2.5))
        pygame.draw.polygon(screen, self.get_color(), [tip, left, right])


import random
from utils.constants import GRID_SIZE, BLACK

class FoodCell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.density = random.randint(0,100)
        self.age = 0
        self.alive = True
        self.next_state = True

    def get_color(self):
        if not self.alive or self.density <= 0:
            return BLACK
        age_factor = min(self.age / 50.0, 1.0)
        density_factor = self.density / 100.0
        red = int(255 * age_factor * density_factor)
        green = int(255 * (1 - age_factor) * density_factor)
        return (red, green, 0)

    def consume(self, amount):
        if self.alive and self.density > 0:
            consumed = min(amount, self.density)
            self.density -= consumed
            if self.density <= 0:
                self.alive = False
            return consumed
        return 0

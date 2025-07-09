# slider.py
import pygame
from utils.constants import GRAY, WHITE

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
        self.font = pygame.font.Font(None, 24)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            relative_x = event.pos[0] - self.rect.x
            self.val = self.min_val + (relative_x / self.rect.width) * (self.max_val - self.min_val)
            self.val = max(self.min_val, min(self.max_val, self.val))

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        handle_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_rect = pygame.Rect(handle_x - 5, self.rect.y, 10, self.rect.height)
        pygame.draw.rect(screen, WHITE, handle_rect)
        label_text = self.font.render(f"{self.label}: {self.val:.2f}", True, WHITE)
        screen.blit(label_text, (self.rect.x, self.rect.y - 25))

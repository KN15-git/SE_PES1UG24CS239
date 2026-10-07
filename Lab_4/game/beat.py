import pygame
import random

LANES = 4
LANE_KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
LANE_LABELS = ['D', 'F', 'J', 'K']
LANE_COLORS = [(220,80,80),(80,180,220),(100,220,100),(220,180,60)]

class Note:
    WIDTH = 70
    HEIGHT = 20
    def __init__(self, lane, y=-30, speed=4, is_hold=False, hold_duration=1.0, fps=60):
        self.lane = lane
        self.y = y
        self.speed = speed
        self.is_hold = is_hold
        self.hold_duration = hold_duration
        self.length = hold_duration * fps * speed if is_hold else 0
        self.hit = False
        self.missed = False
        self.holding = False
        self.completed = False
        self.head_grade = None
        self.head_pts = 0
        self.head_col = None

    def update(self):
        self.y += self.speed

    def get_rect(self, lane_x):
        return pygame.Rect(lane_x - self.WIDTH // 2, int(self.y), self.WIDTH, self.HEIGHT)

    def get_tail_rect(self, lane_x):
        return pygame.Rect(lane_x - self.WIDTH // 2, int(self.y - self.length), self.WIDTH, self.HEIGHT)

    def get_body_rect(self, lane_x):
        return pygame.Rect(lane_x - self.WIDTH // 2 + 10, int(self.y - self.length + self.HEIGHT // 2), self.WIDTH - 20, int(self.length))

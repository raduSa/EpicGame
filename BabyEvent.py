from constants import *
import random
import time

class BabyEvent:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.active = False
        self.room = random.randint(0, 3)
        self.x = random.randint(CIRCLE_RADIUS, WINDOW_WIDTH - CIRCLE_RADIUS)
        self.y = random.randint(CIRCLE_RADIUS, WINDOW_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN - CIRCLE_RADIUS)
        self.next_spawn_time = time.time() + random.uniform(2, 5)  # Spawn between 2-5 seconds
        self.active_time = None
        
    def update(self):
        current_time = time.time()
        if not self.active and current_time >= self.next_spawn_time:
            self.active = True
            self.active_time = current_time
            
    def draw(self, surface, current_room):
        if self.active and self.room == current_room:
            pygame.draw.circle(surface, YELLOW, (self.x, self.y), CIRCLE_RADIUS)
            pygame.draw.circle(surface, BLACK, (self.x, self.y), CIRCLE_RADIUS, 2)  # Border
            
    def is_clicked(self, pos, current_room):
        if not self.active or self.room != current_room:
            return False
        distance = ((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2) ** 0.5
        if distance <= CIRCLE_RADIUS:
            self.reset()
            return True
        return False
        
    def check_timeout(self):
        if self.active and time.time() - self.active_time > 5:  # 5 seconds timeout
            return True
        return False

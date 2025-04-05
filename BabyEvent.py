from constants import *
import random
import time

class BabyEvent:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.active = False
        self.room = random.randint(0, 3)
        allowed_positions = {
               0: [(int(WINDOW_WIDTH * 0.2), int(WINDOW_HEIGHT * 0.5)),
                    (int(WINDOW_WIDTH * 0.8), int(WINDOW_HEIGHT * 0.6))],
                1: [(int(WINDOW_WIDTH * 0.25), int(WINDOW_HEIGHT * 0.5)),
                    (int(WINDOW_WIDTH * 0.75), int(WINDOW_HEIGHT * 0.5))],
                2: [(int(WINDOW_WIDTH * 0.1), int(WINDOW_HEIGHT * 0.5)),
                    (int(WINDOW_WIDTH * 0.3), int(WINDOW_HEIGHT * 0.87))],
                3: [(int(WINDOW_WIDTH * 0.9), int(WINDOW_HEIGHT * 0.8)),
                    (int(WINDOW_WIDTH * 0.1), int(WINDOW_HEIGHT * 0.5))]
            }
            # Dacă sunt poziții definite pentru camera curentă, alege una aleatoriu
        if self.room in allowed_positions:
            self.x, self.y = random.choice(allowed_positions[self.room])
        else:
            # Fallback în cazul în care nu sunt poziții definite
            self.x = random.randint(CIRCLE_RADIUS, WINDOW_WIDTH - CIRCLE_RADIUS)
            self.y = random.randint(CIRCLE_RADIUS, WINDOW_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN - CIRCLE_RADIUS)
        self.next_spawn_time = time.time() + random.uniform(2, 5)
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
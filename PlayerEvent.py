from constants import *
import random
import time

# Define hardcoded events with their properties
PREDEFINED_EVENTS = [
    {
        "name": "Wash Dishes",
        "room": 1,  # Kitchen
        "x": WINDOW_WIDTH * (0.3),
        "y": WINDOW_HEIGHT * (7/12),
        "radius": CIRCLE_RADIUS * 3
    },
    {
        "name": "Wash Toielet",
        "room": 0,  # Bathroom
        "x": WINDOW_WIDTH * (5/12),
        "y": WINDOW_HEIGHT * (4/6),
        "radius": CIRCLE_RADIUS * 3
    },
    {
        "name": "Make Bed",
        "room": 2,  # Bedroom
        "x": WINDOW_WIDTH * (1/2),
        "y": WINDOW_HEIGHT * (4/6),
        "radius": CIRCLE_RADIUS * 4  # Slightly larger button
    },
    {
        "name": "Fix Lightbulb",
        "room": 3,  # Living Room
        "x": WINDOW_WIDTH * (0.43),
        "y": WINDOW_HEIGHT * (1/6),
        "radius": CIRCLE_RADIUS * 3
    }
]

class PlayerEvent:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.active = False
        # Choose a random event from our predefined list
        self.current_event = random.choice(PREDEFINED_EVENTS)
        self.room = self.current_event["room"]
        self.x = self.current_event["x"]
        self.y = self.current_event["y"]
        self.radius = self.current_event["radius"]
        self.name = self.current_event["name"]
        self.next_spawn_time = time.time() + random.uniform(2, 5)
        self.active_time = None
        self.clicks = 0
        self.completed = False
        self.grace_period_end = None
        
    def update(self):
        current_time = time.time()
        if not self.active and not self.completed and current_time >= self.next_spawn_time:
            self.active = True
            self.active_time = current_time
        elif self.completed and current_time >= self.grace_period_end:
            self.reset()
            
    def draw_current_event_name(self, surface):
        # Create a semi-transparent background for the text
        text_bg = pygame.Surface((800, 60), pygame.SRCALPHA)  # Increased size
        text_bg.fill((0, 0, 0, 128))  # Black with 50% opacity
        
        # Draw the background
        surface.blit(text_bg, (WINDOW_WIDTH - 400, 10))  # Adjusted position
        
        # Draw the text with larger font
        font = pygame.font.Font(None, 36)  # Increased font size
        
        # Choose text based on event state
        if self.active:
            text = font.render(f"Current Task: {self.name}", True, WHITE)
        elif self.completed:
            text = font.render("Task Completed!", True, WHITE)
        else:
            text = font.render("Nothing to do :(", True, WHITE)
            
        text_rect = text.get_rect(topright=(WINDOW_WIDTH - 20, 20))
        surface.blit(text, text_rect)
            
    def draw(self, surface, current_room):
        # Draw the current event name in the top right corner
        self.draw_current_event_name(surface)
        
        if self.active and self.room == current_room:            
            # Draw progress bar above the circle
            progress_width = (self.clicks / PLAYER_EVENT_CLICKS_REQUIRED) * PROGRESS_BAR_WIDTH
            progress_rect = pygame.Rect(
                self.x - PROGRESS_BAR_WIDTH//2,
                self.y - self.radius - PROGRESS_BAR_HEIGHT - 5,
                progress_width,
                PROGRESS_BAR_HEIGHT
            )
            pygame.draw.rect(surface, PROGRESS_BAR_COLOR, progress_rect)
            pygame.draw.rect(surface, BLACK, progress_rect, 1)  # Border
                
            
    def is_clicked(self, pos, current_room):
        if not self.active or self.room != current_room:
            return False
        distance = ((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2) ** 0.5
        if distance <= self.radius:
            self.clicks += 1
            if self.clicks >= PLAYER_EVENT_CLICKS_REQUIRED:
                self.completed = True
                self.active = False
                self.grace_period_end = time.time() + PLAYER_EVENT_GRACE_PERIOD
            return True
        return False
        
    def check_timeout(self):
        if self.active and time.time() - self.active_time > PLAYER_EVENT_TIMEOUT:
            return True
        return False

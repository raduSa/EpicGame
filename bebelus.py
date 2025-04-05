import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 20
CIRCLE_RADIUS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)    # Room 1
BLUE = (100, 100, 255)   # Room 2
GREEN = (100, 255, 100)  # Room 3
PURPLE = (200, 100, 255) # Room 4
GRAY = (150, 150, 150)   # Button color
YELLOW = (255, 255, 0)   # Event circle color

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Room Navigation Game")

class BabyEvent:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.active = False
        self.room = random.randint(0, 3)
        self.x = random.randint(CIRCLE_RADIUS, WINDOW_WIDTH - CIRCLE_RADIUS)
        self.y = random.randint(CIRCLE_RADIUS, WINDOW_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN - CIRCLE_RADIUS)
        self.next_spawn_time = time.time() + random.uniform(2, 5)  # Spawn between 2-5 seconds
        
    def update(self):
        current_time = time.time()
        if not self.active and current_time >= self.next_spawn_time:
            self.active = True
            
    def draw(self, surface, current_room):
        if self.active and self.room == current_room:
            pygame.draw.circle(surface, YELLOW, (self.x, self.y), CIRCLE_RADIUS)
            pygame.draw.circle(surface, BLACK, (self.x, self.y), CIRCLE_RADIUS, 2)  # Border
            
    def is_clicked(self, pos, current_room):
        if not self.active or self.room != current_room:
            return False
        distance = ((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2) ** 0.5
        return distance <= CIRCLE_RADIUS

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = GRAY
        self.disabled_color = (100, 100, 100)  # Darker gray for disabled state
        self.font = pygame.font.Font(None, 36)
        self.enabled = True
        
    def draw(self, surface):
        # Draw button rectangle with appropriate color
        current_color = self.disabled_color if not self.enabled else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Border
        
        # Draw text
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.enabled and self.rect.collidepoint(pos)
        
    def set_enabled(self, enabled):
        self.enabled = enabled

class Game:
    def __init__(self):
        self.current_room = 0  # Start in first room
        self.rooms = [RED, BLUE, GREEN, PURPLE]
        
        # Create navigation buttons
        left_x = BUTTON_MARGIN
        right_x = WINDOW_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN
        button_y = WINDOW_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN
        
        self.left_button = Button(left_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Left")
        self.right_button = Button(right_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Right")
        
        # Create baby event
        self.baby_event = BabyEvent()
        
        # Update button states initially
        self.update_button_states()
        
    def update_button_states(self):
        # Left button is disabled in first room
        self.left_button.set_enabled(self.current_room > 0)
        # Right button is disabled in last room
        self.right_button.set_enabled(self.current_room < len(self.rooms) - 1)
        
    def handle_click(self, pos):
        if self.left_button.is_clicked(pos):
            self.current_room -= 1
            self.update_button_states()
        elif self.right_button.is_clicked(pos):
            self.current_room += 1
            self.update_button_states()
        elif self.baby_event.is_clicked(pos, self.current_room):
            self.baby_event.reset()
            
    def draw(self, surface):
        # Fill background with current room color
        surface.fill(self.rooms[self.current_room])
        
        # Draw room number
        font = pygame.font.Font(None, 72)
        text = font.render(f"Room {self.current_room + 1}", True, BLACK)
        text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        surface.blit(text, text_rect)
        
        # Draw navigation buttons
        self.left_button.draw(surface)
        self.right_button.draw(surface)
        
        # Update and draw baby event
        self.baby_event.update()
        self.baby_event.draw(surface, self.current_room)

def main():
    game = Game()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    game.handle_click(event.pos)
        
        # Draw everything
        game.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

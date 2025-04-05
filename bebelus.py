import pygame
import sys
import random
import time
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 20
CIRCLE_RADIUS = 30
PROGRESS_BAR_HEIGHT = 10
PROGRESS_BAR_WIDTH = 60
PLAYER_EVENT_CLICKS_REQUIRED = 10
PLAYER_EVENT_TIMEOUT = 15  # seconds
PLAYER_EVENT_GRACE_PERIOD = 5  # seconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)    # Room 1
BLUE = (100, 100, 255)   # Room 2
GREEN = (100, 255, 100)  # Room 3
PURPLE = (200, 100, 255) # Room 4
GRAY = (150, 150, 150)   # Button color
YELLOW = (255, 255, 0)   # Event circle color
PROGRESS_BAR_COLOR = (0, 255, 0)  # Green for progress

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

class PlayerEvent:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.active = False
        self.room = random.randint(0, 3)
        self.x = random.randint(CIRCLE_RADIUS, WINDOW_WIDTH - CIRCLE_RADIUS)
        self.y = random.randint(CIRCLE_RADIUS, WINDOW_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN - CIRCLE_RADIUS)
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
            
    def draw(self, surface, current_room):
        if self.active and self.room == current_room:
            # Draw the black circle
            pygame.draw.circle(surface, BLACK, (self.x, self.y), CIRCLE_RADIUS)
            
            # Draw progress bar above the circle
            progress_width = (self.clicks / PLAYER_EVENT_CLICKS_REQUIRED) * PROGRESS_BAR_WIDTH
            progress_rect = pygame.Rect(
                self.x - PROGRESS_BAR_WIDTH//2,
                self.y - CIRCLE_RADIUS - PROGRESS_BAR_HEIGHT - 5,
                progress_width,
                PROGRESS_BAR_HEIGHT
            )
            pygame.draw.rect(surface, PROGRESS_BAR_COLOR, progress_rect)
            pygame.draw.rect(surface, BLACK, progress_rect, 1)  # Border
            
    def is_clicked(self, pos, current_room):
        if not self.active or self.room != current_room:
            return False
        distance = ((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2) ** 0.5
        if distance <= CIRCLE_RADIUS:
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
        
        # Load room backgrounds
        self.room_backgrounds = []
        room_images = ["baie.png", "bucatarie.png", "dormitor.png", "living.PNG"]
        for img_name in room_images:
            try:
                img = pygame.image.load(os.path.join("HACK", img_name))
                # Scale image to fit the window
                img = pygame.transform.scale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
                self.room_backgrounds.append(img)
            except:
                print(f"Warning: Could not load image {img_name}")
                # Fallback to white background if image fails to load
                self.room_backgrounds.append(pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)))
                self.room_backgrounds[-1].fill(WHITE)
        
        self.game_over = False
        self.game_over_cause = None  # "baby" or "task"
        
        # Create navigation buttons
        left_x = BUTTON_MARGIN
        right_x = WINDOW_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN
        button_y = WINDOW_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN
        
        self.left_button = Button(left_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Left")
        self.right_button = Button(right_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Right")
        
        # Create retry button
        retry_width = 150
        retry_height = 50
        retry_x = (WINDOW_WIDTH - retry_width) // 2
        retry_y = WINDOW_HEIGHT - retry_height - BUTTON_MARGIN
        self.retry_button = Button(retry_x, retry_y, retry_width, retry_height, "Retry")
        
        # Create events
        self.baby_event = BabyEvent()
        self.player_event = PlayerEvent()
        
        # Update button states initially
        self.update_button_states()
        
    def update_button_states(self):
        # Left button is disabled in first room
        self.left_button.set_enabled(self.current_room > 0)
        # Right button is disabled in last room
        self.right_button.set_enabled(self.current_room < len(self.room_backgrounds) - 1)
        
    def reset_game(self):
        self.current_room = 0
        self.game_over = False
        self.game_over_cause = None
        self.baby_event = BabyEvent()
        self.player_event = PlayerEvent()
        self.update_button_states()
        
    def handle_click(self, pos):
        if self.game_over:
            if self.retry_button.is_clicked(pos):
                self.reset_game()
            return
            
        if self.left_button.is_clicked(pos):
            self.move_left()
        elif self.right_button.is_clicked(pos):
            self.move_right()
        elif self.baby_event.is_clicked(pos, self.current_room):
            self.baby_event.reset()
        elif self.player_event.is_clicked(pos, self.current_room):
            pass  # Progress is handled in the PlayerEvent class
            
    def move_left(self):
        if self.current_room > 0:  # Only move if not in first room
            self.current_room -= 1
            self.update_button_states()
            
    def move_right(self):
        if self.current_room < len(self.room_backgrounds) - 1:  # Only move if not in last room
            self.current_room += 1
            self.update_button_states()
            
    def draw(self, surface):
        if self.game_over:
            # Keep the room background
            surface.blit(self.room_backgrounds[self.current_room], (0, 0))
            
            # Draw semi-transparent gray overlay strip in the middle
            overlay_height = 150  # Height of the overlay strip
            overlay_y = (WINDOW_HEIGHT - overlay_height) // 2  # Center vertically
            overlay = pygame.Surface((WINDOW_WIDTH, overlay_height), pygame.SRCALPHA)
            overlay.fill((100, 100, 100, 128))  # Gray with 50% opacity
            surface.blit(overlay, (0, overlay_y))
            
            # Draw game over text in two lines
            font_bold = pygame.font.Font(None, 72)
            font_italic = pygame.font.Font(None, 48)
            
            # First line: "GAME OVER"
            text1 = font_bold.render("GAME OVER", True, (255, 0, 0))
            text1_rect = text1.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 30))
            
            # Second line: appropriate message based on game over cause
            if self.game_over_cause == "baby":
                message = "the baby has died"
            else:  # task
                message = "task incomplete"
                
            text2 = font_italic.render(message, True, (255, 0, 0))
            text2_rect = text2.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 30))
            
            # Draw both text lines
            surface.blit(text1, text1_rect)
            surface.blit(text2, text2_rect)
            
            # Draw retry button
            self.retry_button.draw(surface)
            return
            
        # Draw room background
        surface.blit(self.room_backgrounds[self.current_room], (0, 0))
        
        # Draw navigation buttons
        self.left_button.draw(surface)
        self.right_button.draw(surface)
        
        # Update and draw events
        self.baby_event.update()
        self.baby_event.draw(surface, self.current_room)
        
        self.player_event.update()
        self.player_event.draw(surface, self.current_room)
        
        # Check for timeouts
        if self.baby_event.check_timeout():
            self.game_over = True
            self.game_over_cause = "baby"
        elif self.player_event.check_timeout():
            self.game_over = True
            self.game_over_cause = "task"

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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move_left()
                elif event.key == pygame.K_RIGHT:
                    game.move_right()
        
        # Draw everything
        game.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

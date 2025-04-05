import pygame
import sys
import random
import time
import os
from constants import *
from BabyEvent import *
from PlayerEvent import *

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Room Navigation Game")


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
                # Scale image to fit the full screen
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Handle ESCAPE key
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_LEFT:
                    game.move_left()
                elif event.key == pygame.K_RIGHT:
                    game.move_right()
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

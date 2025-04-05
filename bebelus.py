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
        self.start_time = time.time()  # Add start time for win condition
        self.WIN_TIME = 100  # Time in seconds to win
        self.won = False  # Add win state
        
        # Initialize empty containers for backgrounds
        self.default_backgrounds = []
        self.event_backgrounds = {}
        self.haunted_changes_applied = {20: False, 40: False, 60: False, 80: False}
        
        # Load all background textures
        self.load_background_textures()
        
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
        
    def load_background_textures(self):
        # Clear existing backgrounds
        self.default_backgrounds = []
        self.event_backgrounds = {}
        
        # Load default backgrounds
        default_images = ["baie.png", "bucatarie.png", "dormitor.png", "living.PNG"]
        for img_name in default_images:
            try:
                img = pygame.image.load(os.path.join("HACK", img_name))
                # Scale image to fit the full screen
                img = pygame.transform.scale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
                self.default_backgrounds.append(img)
            except:
                print(f"Warning: Could not load image {img_name}")
                # Fallback to white background if image fails to load
                self.default_backgrounds.append(pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)))
                self.default_backgrounds[-1].fill(WHITE)
        
        # Load event-specific backgrounds
        event_images = {
            "Wash Dishes": ("bucatarie_vase.png", 1),
            "Wash Toielet": ("baie_murdara.png", 0),
            "Make Bed": ("pat_dezordonat.png", 2),
            "Fix Lightbulb": ("lampa_sparta.png", 3)
        }
        
        for event_name, (img_name, room_id) in event_images.items():
            try:
                img = pygame.image.load(os.path.join("HACK", img_name))
                img = pygame.transform.scale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
                self.event_backgrounds[event_name] = img
            except:
                print(f"Warning: Could not load event image {img_name}")
                self.event_backgrounds[event_name] = self.default_backgrounds[room_id]
                
    def update_button_states(self):
        # Left button is disabled in first room
        self.left_button.set_enabled(self.current_room > 0)
        # Right button is disabled in last room
        self.right_button.set_enabled(self.current_room < len(self.default_backgrounds) - 1)
        
    def update_haunted_textures(self):
        current_time = time.time() - self.start_time
        
        # At 20 seconds - Bedroom becomes haunted
        if current_time >= 20 and not self.haunted_changes_applied[20]:
            try:
                # Update default background
                haunted_bg = pygame.image.load(os.path.join("HACK", "dormitor_haunted.png"))
                haunted_bg = pygame.transform.scale(haunted_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
                self.default_backgrounds[2] = haunted_bg  # Index 2 is bedroom
                
                # Update event background
                haunted_event = pygame.image.load(os.path.join("HACK", "pat_dezordonat_haunted.png"))
                haunted_event = pygame.transform.scale(haunted_event, (WINDOW_WIDTH, WINDOW_HEIGHT))
                self.event_backgrounds["Make Bed"] = haunted_event
            except Exception as e:
                print(f"Warning: Could not load haunted bedroom textures: {e}")
            self.haunted_changes_applied[20] = True
            
        # At 40 seconds - Kitchen becomes haunted
        if current_time >= 40 and not self.haunted_changes_applied[40]:
            try:
                haunted_bg = pygame.image.load(os.path.join("HACK", "bucatarie_haunted.png"))
                haunted_bg = pygame.transform.scale(haunted_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
                self.default_backgrounds[1] = haunted_bg  # Index 1 is kitchen
                
                haunted_event = pygame.image.load(os.path.join("HACK", "bucatarie_vase_haunted.png"))
                haunted_event = pygame.transform.scale(haunted_event, (WINDOW_WIDTH, WINDOW_HEIGHT))
                self.event_backgrounds["Wash Dishes"] = haunted_event
            except Exception as e:
                print(f"Warning: Could not load haunted kitchen textures: {e}")
            self.haunted_changes_applied[40] = True
            
        # At 60 seconds - Living room becomes haunted
        if current_time >= 60 and not self.haunted_changes_applied[60]:
            try:
                haunted_bg = pygame.image.load(os.path.join("HACK", "living_haunted.png"))
                haunted_bg = pygame.transform.scale(haunted_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
                self.default_backgrounds[3] = haunted_bg  # Index 3 is living room
                
                haunted_event = pygame.image.load(os.path.join("HACK", "lampa_sparta_haunted.png"))
                haunted_event = pygame.transform.scale(haunted_event, (WINDOW_WIDTH, WINDOW_HEIGHT))
                self.event_backgrounds["Fix Lightbulb"] = haunted_event
            except Exception as e:
                print(f"Warning: Could not load haunted living room textures: {e}")
            self.haunted_changes_applied[60] = True
            
        # At 80 seconds - Bathroom becomes haunted
        if current_time >= 80 and not self.haunted_changes_applied[80]:
            try:
                haunted_bg = pygame.image.load(os.path.join("HACK", "baie_haunted.png"))
                haunted_bg = pygame.transform.scale(haunted_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
                self.default_backgrounds[0] = haunted_bg  # Index 0 is bathroom
                
                haunted_event = pygame.image.load(os.path.join("HACK", "baie_murdara_haunted.png"))
                haunted_event = pygame.transform.scale(haunted_event, (WINDOW_WIDTH, WINDOW_HEIGHT))
                self.event_backgrounds["Wash Toielet"] = haunted_event
            except Exception as e:
                print(f"Warning: Could not load haunted bathroom textures: {e}")
            self.haunted_changes_applied[80] = True
                
    def reset_game(self):
        self.current_room = 0
        self.game_over = False
        self.game_over_cause = None
        self.won = False
        self.start_time = time.time()
        self.haunted_changes_applied = {20: False, 40: False, 60: False, 80: False}
        # Reload all background textures to their original state
        self.load_background_textures()
        self.baby_event = BabyEvent()
        self.player_event = PlayerEvent()
        self.update_button_states()
        
    def handle_click(self, pos):
        if self.game_over or self.won:  # Check for both game over and win states
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
        if self.current_room < len(self.default_backgrounds) - 1:  # Only move if not in last room
            self.current_room += 1
            self.update_button_states()
            
    def get_current_background(self):
        # If there's an active event and we're in the room where it's happening
        if (self.player_event.active and 
            self.player_event.room == self.current_room and 
            self.player_event.name in self.event_backgrounds):
            return self.event_backgrounds[self.player_event.name]
        return self.default_backgrounds[self.current_room]
            
    def draw(self, surface):
        # Update haunted textures based on time
        self.update_haunted_textures()
        
        # Check for win condition
        if not self.game_over and not self.won and (time.time() - self.start_time) >= self.WIN_TIME:
            self.won = True
        
        if self.won:
            # Draw the current background
            surface.blit(self.get_current_background(), (0, 0))
            
            # Draw semi-transparent gray overlay strip in the middle
            overlay_height = 150
            overlay_y = (WINDOW_HEIGHT - overlay_height) // 2
            overlay = pygame.Surface((WINDOW_WIDTH, overlay_height), pygame.SRCALPHA)
            overlay.fill((100, 100, 100, 128))
            surface.blit(overlay, (0, overlay_y))
            
            # Draw winner text in two lines with yellow color
            font_bold = pygame.font.Font(None, 72)
            font_italic = pygame.font.Font(None, 48)
            
            # First line: "WINNER!"
            text1 = font_bold.render("WINNER!", True, (255, 255, 0))  # Yellow color
            text1_rect = text1.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 30))
            
            # Draw both text lines
            surface.blit(text1, text1_rect)
            
            # Draw retry button
            self.retry_button.draw(surface)
            return
            
        if self.game_over:
            # Keep the room background
            surface.blit(self.get_current_background(), (0, 0))
            
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
        surface.blit(self.get_current_background(), (0, 0))
        
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

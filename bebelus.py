import pygame
import cv2
import numpy as np
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

class StartScreen:
    def __init__(self):
        # Load and blur background
        try:
            self.bg = pygame.image.load(os.path.join("HACK", "living.PNG"))
            self.bg = pygame.transform.scale(self.bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
            # Create stronger blur effect by scaling down more
            small_surf = pygame.transform.scale(self.bg, (WINDOW_WIDTH // 8, WINDOW_HEIGHT // 8))  # Scaled to 1/8 instead of 1/4
            # Apply blur twice for stronger effect
            medium_surf = pygame.transform.scale(small_surf, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.bg = pygame.transform.scale(medium_surf, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except:
            self.bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.bg.fill(WHITE)
            
        # Create start button
        button_width = 200
        button_height = 60
        button_x = (WINDOW_WIDTH - button_width) // 2
        button_y = WINDOW_HEIGHT - button_height - 50
        self.start_button = Button(button_x, button_y, button_width, button_height, "Start Game")
        
        # Prepare text
        self.title_font = pygame.font.Font(None, 72)
        self.text_font = pygame.font.Font(None, 45)
        
        self.title = self.title_font.render("Demon Diapers", True, WHITE)
        self.title_rect = self.title.get_rect(center=(WINDOW_WIDTH//2, 100))
        
        # Instructions text
        self.instructions = [
            "Keep the baby safe and the house clean",
            "The baby is VERY fragile",
            "Click to interact with the environment",
            "Use arrow keys or buttons to move between rooms",
            "Press ESC to exit the game",
            "",
            "Good luck!"
        ]
        
    def draw(self, surface):
        # Draw blurred background
        surface.blit(self.bg, (0, 0))
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Dark overlay with 50% opacity
        surface.blit(overlay, (0, 0))
        
        # Draw title
        surface.blit(self.title, self.title_rect)
        
        # Draw instructions
        for i, line in enumerate(self.instructions):
            text = self.text_font.render(line, True, WHITE)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, 250 + i * 50))
            surface.blit(text, rect)
        
        # Draw start button
        self.start_button.draw(surface)
        
    def handle_click(self, pos):
        return self.start_button.is_clicked(pos)

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
        self.victory_video = None
        self.video_rect = None
        self.last_frame = None
        self.frame_time = 0
        self.victory_sound_played = False
        self.background_sound = None
        self.current_volume = 0.0
        self.target_volume = 0.0
        self.fade_duration = 5.0  # Duration of fade in seconds
        self.fade_start_time = 0.0
        
        try:
            # Initialize video capture
            self.victory_video = cv2.VideoCapture(os.path.join("HACK", "scary_final.mp4"))
            # Calculate video size (half of screen width)
            video_width = WINDOW_WIDTH // 2
            video_height = int(video_width * (9/16))
            self.video_dimensions = (video_width, video_height)
            # Center the video
            self.video_rect = pygame.Rect(
                (WINDOW_WIDTH - video_width) // 2,
                (WINDOW_HEIGHT - video_height) // 2,
                video_width,
                video_height
            )
            # Get video FPS
            self.video_fps = self.victory_video.get(cv2.CAP_PROP_FPS)
            self.frame_delay = 1.0 / self.video_fps
        except Exception as e:
            print(f"Warning: Could not load victory video: {e}")
            self.victory_video = None
            
        try:
            # Load victory sound
            self.victory_sound = pygame.mixer.Sound(os.path.join("HACK", "sunet", "death.wav"))
        except Exception as e:
            print(f"Warning: Could not load victory sound: {e}")
            self.victory_sound = None
            
        try:
            # Load background sound
            self.background_sound = pygame.mixer.Sound(os.path.join("HACK", "sunet", "eerie_noise.wav"))
            self.background_sound.set_volume(0.0)  # Start with no volume
        except Exception as e:
            print(f"Warning: Could not load background sound: {e}")
            self.background_sound = None
        
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
        
    def get_video_frame(self):
        if not self.victory_video:
            return None
            
        current_time = time.time()
        if self.last_frame is None or (current_time - self.frame_time) >= self.frame_delay:
            ret, frame = self.victory_video.read()
            if not ret:
                # Video ended, close the game
                pygame.quit()
                sys.exit()
                    
            # Convert frame from BGR to RGB and resize
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, self.video_dimensions)
            
            # Convert to pygame surface
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            
            self.last_frame = frame
            self.frame_time = current_time
            
        return self.last_frame
        
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
        
    def update_sound_volume(self):
        if not self.background_sound:
            return
            
        current_time = time.time()
        elapsed = current_time - self.fade_start_time
        
        if elapsed < self.fade_duration:
            # Calculate new volume based on fade progress using cubic easing
            progress = elapsed / self.fade_duration
            # Cubic easing in/out - steeper at beginning and end
            if progress < 0.5:
                progress = 4 * progress * progress * progress
            else:
                progress = 1 - 4 * (1 - progress) * (1 - progress) * (1 - progress)
            new_volume = self.current_volume + (self.target_volume - self.current_volume) * progress
            self.background_sound.set_volume(new_volume)
        else:
            # Fade complete, set final volume
            self.background_sound.set_volume(self.target_volume)
            self.current_volume = self.target_volume

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
                
                # Start background sound with fade in
                if self.background_sound:
                    self.background_sound.play(-1)  # -1 means loop indefinitely
                    self.target_volume = 0.1
                    self.fade_start_time = time.time()
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
                
                # Increase background sound volume with fade
                if self.background_sound:
                    self.target_volume = 0.2
                    self.fade_start_time = time.time()
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
                
                # Increase background sound volume with fade
                if self.background_sound:
                    self.target_volume = 0.4
                    self.fade_start_time = time.time()
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
                
                # Increase background sound volume with fade
                if self.background_sound:
                    self.target_volume = 0.9
                    self.fade_start_time = time.time()
            except Exception as e:
                print(f"Warning: Could not load haunted bathroom textures: {e}")
            self.haunted_changes_applied[80] = True
            
        # Update sound volume for smooth transitions
        self.update_sound_volume()
        
    def reset_game(self):
        self.current_room = 0
        self.game_over = False
        self.game_over_cause = None
        self.won = False
        self.victory_sound_played = False
        self.current_volume = 0.0
        self.target_volume = 0.0
        if self.background_sound:
            # Fade out the sound
            self.target_volume = 0.0
            self.fade_start_time = time.time()
            # Wait for fade to complete before stopping
            pygame.time.wait(int(self.fade_duration * 1000))
            self.background_sound.stop()
        self.start_time = time.time()
        self.haunted_changes_applied = {20: False, 40: False, 60: False, 80: False}
        self.last_frame = None
        self.frame_time = 0
        # Reset video to start
        if self.victory_video:
            self.victory_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
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
            # Play victory sound once when winning
            if not self.victory_sound_played and self.victory_sound:
                self.victory_sound.play()
                self.victory_sound_played = True
        
        if self.won:
            # Draw the current background
            surface.blit(self.get_current_background(), (0, 0))
            
            # Add darkening overlay
            dark_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 250))  # Black with 90% opacity
            surface.blit(dark_overlay, (0, 0))
            
            # Get and draw video frame if available
            frame = self.get_video_frame()
            if frame is not None:
                # Create a copy of the frame with transparency
                transparent_surface = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
                transparent_surface.fill((255, 255, 255, 128))  # White with 50% transparency
                frame.blit(transparent_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                # Draw the video frame
                surface.blit(frame, self.video_rect)
            else:
                # Fallback if video fails
                # Draw semi-transparent gray overlay strip in the middle
                overlay_height = 150
                overlay_y = (WINDOW_HEIGHT - overlay_height) // 2
                overlay = pygame.Surface((WINDOW_WIDTH, overlay_height), pygame.SRCALPHA)
                overlay.fill((100, 100, 100, 128))
                surface.blit(overlay, (0, overlay_y))
                
                # Draw winner text
                font_bold = pygame.font.Font(None, 72)
                text = font_bold.render("WINNER!", True, (255, 255, 0))
                text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                surface.blit(text, text_rect)
            
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
    # Create start screen
    start_screen = StartScreen()
    game = None
    game_started = False
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
                elif game_started and event.key == pygame.K_LEFT:
                    game.move_left()
                elif game_started and event.key == pygame.K_RIGHT:
                    game.move_right()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if not game_started:
                        if start_screen.handle_click(event.pos):
                            game_started = True
                            game = Game()  # Initialize game only when starting
                    else:
                        game.handle_click(event.pos)
        
        # Draw everything
        if game_started:
            game.draw(screen)
        else:
            start_screen.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

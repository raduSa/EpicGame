import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)    # Room 1
BLUE = (100, 100, 255)   # Room 2
GREEN = (100, 255, 100)  # Room 3
PURPLE = (200, 100, 255) # Room 4
GRAY = (150, 150, 150)   # Button color

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Room Navigation Game")

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = GRAY
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, surface):
        # Draw button rectangle
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Border
        
        # Draw text
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

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
        
    def handle_click(self, pos):
        if self.left_button.is_clicked(pos):
            self.current_room = (self.current_room - 1) % len(self.rooms)
        elif self.right_button.is_clicked(pos):
            self.current_room = (self.current_room + 1) % len(self.rooms)
            
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

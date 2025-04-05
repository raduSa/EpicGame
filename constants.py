import pygame

# Constants
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

# Initialize Pygame
pygame.init()

# Get screen info for fullscreen
screen_info = pygame.display.Info()
WINDOW_WIDTH = screen_info.current_w
WINDOW_HEIGHT = screen_info.current_h
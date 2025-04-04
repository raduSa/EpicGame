import pygame
import math
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Heart Cursor Game")

# Colors
PINK = (255, 192, 203)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Game parameters
HEART_SIZE = 0.5
ENEMY_RADIUS = 10
ENEMY_SPEED = 2
ENEMY_SPAWN_RATE = 60  # frames between enemy spawns

class Player:
    def __init__(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.hp = 1
        self.size = HEART_SIZE
        
    def draw_heart(self, surface, color):
        # Draw a heart shape using mathematical equations
        points = []
        for t in range(0, 360, 1):
            t_rad = math.radians(t)
            # Heart equation
            x_point = self.x + self.size * 16 * math.sin(t_rad) ** 3
            y_point = self.y - self.size * (13 * math.cos(t_rad) - 5 * math.cos(2*t_rad) - 2 * math.cos(3*t_rad) - math.cos(4*t_rad))
            points.append((x_point, y_point))
        
        if len(points) > 2:
            pygame.draw.polygon(surface, color, points)
            
    def get_radius(self):
        # Approximate the heart's radius for collision detection
        return self.size * 16
            
    def update_position(self, x, y):
        self.x = max(self.get_radius(), min(x, WINDOW_WIDTH - self.get_radius()))
        self.y = max(self.get_radius(), min(y, WINDOW_HEIGHT - self.get_radius()))

class Enemy:
    def __init__(self):
        # Randomly choose which edge to spawn from
        edge = random.randint(0, 3)
        if edge == 0:  # Top
            self.x = random.randint(0, WINDOW_WIDTH)
            self.y = -ENEMY_RADIUS
        elif edge == 1:  # Right
            self.x = WINDOW_WIDTH + ENEMY_RADIUS
            self.y = random.randint(0, WINDOW_HEIGHT)
        elif edge == 2:  # Bottom
            self.x = random.randint(0, WINDOW_WIDTH)
            self.y = WINDOW_HEIGHT + ENEMY_RADIUS
        else:  # Left
            self.x = -ENEMY_RADIUS
            self.y = random.randint(0, WINDOW_HEIGHT)
        
        # Calculate direction to center
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        dx = center_x - self.x
        dy = center_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Normalize direction vector
        self.vx = (dx / distance) * ENEMY_SPEED
        self.vy = (dy / distance) * ENEMY_SPEED
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), ENEMY_RADIUS)
        
    def is_at_center(self):
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        distance = math.sqrt((self.x - center_x) ** 2 + (self.y - center_y) ** 2)
        return distance < ENEMY_RADIUS
        
    def check_collision(self, player):
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        return distance < (ENEMY_RADIUS + player.get_radius())

# Game loop
running = True
game_over = False
clock = pygame.time.Clock()
enemies = []
spawn_timer = 0
player = Player()

# Set up font for HP display and game over
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:  # Press R to restart
                game_over = False
                player = Player()
                enemies = []
                spawn_timer = 0
    
    if not game_over:
        # Get mouse position and update player
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player.update_position(mouse_x, mouse_y)
        
        # Spawn new enemies
        spawn_timer += 1
        if spawn_timer >= ENEMY_SPAWN_RATE:
            enemies.append(Enemy())
            spawn_timer = 0
        
        # Update and check collisions for enemies
        for enemy in enemies[:]:
            enemy.update()
            if enemy.is_at_center():
                enemies.remove(enemy)
            elif enemy.check_collision(player):
                player.hp -= 1
                enemies.remove(enemy)
                if player.hp <= 0:
                    game_over = True
    
    # Fill the screen with white
    screen.fill(WHITE)
    
    if game_over:
        # Draw game over screen
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        restart_text = font.render("Press R to Restart", True, (0, 0, 0))
        
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
        
        screen.blit(game_over_text, game_over_rect)
        screen.blit(restart_text, restart_rect)
    else:
        # Draw the player
        player.draw_heart(screen, PINK)
        
        # Draw all enemies
        for enemy in enemies:
            enemy.draw(screen)
            
        # Draw HP
        hp_text = font.render(f"HP: {player.hp}", True, (0, 0, 0))
        screen.blit(hp_text, (10, 10))
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit() 
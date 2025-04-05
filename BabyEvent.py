from constants import *
import random
import time
import os

class BabyEvent:
    def __init__(self):
        # Load all baby textures
        self.textures = {}
        self.load_textures()
        self.reset()
        
    def load_textures(self):
        # Define texture mapping for each room and position
        texture_mapping = {
            0: {  # Bathroom
                (int(WINDOW_WIDTH * 0.2), int(WINDOW_HEIGHT * 0.4)): "bebe_lama.png",
                (int(WINDOW_WIDTH * 0.8), int(WINDOW_HEIGHT * 0.55)): "bebe_inec.png"
            },
            1: {  # Kitchen
                (int(WINDOW_WIDTH * 0.45), int(WINDOW_HEIGHT * 0.4)): "bebe_cutit.png",
                (int(WINDOW_WIDTH * 0.7), int(WINDOW_HEIGHT * 0.45)): "bebe_foc.png"
            },
            2: {  # Bedroom
                (int(WINDOW_WIDTH * 0.1), int(WINDOW_HEIGHT * 0.5)): "bebe_geam.png",
                (int(WINDOW_WIDTH * 0.3), int(WINDOW_HEIGHT * 0.87)): "bebe_fantoma.png"
            },
            3: {  # Living Room
                (int(WINDOW_WIDTH * 0.9), int(WINDOW_HEIGHT * 0.75)): "bebe_priza.png"
            }
        }
        
        # Load each texture
        for room in texture_mapping:
            self.textures[room] = {}
            for pos, img_name in texture_mapping[room].items():
                try:
                    img = pygame.image.load(os.path.join("HACK", img_name))
                    # Scale image to 3 times the circle size
                    size = CIRCLE_RADIUS * 2 * 4  # Multiplied by 3 for larger size
                    img = pygame.transform.scale(img, (size, size))
                    self.textures[room][pos] = img
                except:
                    print(f"Warning: Could not load baby texture {img_name}")
                    self.textures[room][pos] = None
        
    def reset(self):
        self.active = False
        self.room = random.randint(0, 3)
        allowed_positions = {
            0: [(int(WINDOW_WIDTH * 0.2), int(WINDOW_HEIGHT * 0.4)),
                (int(WINDOW_WIDTH * 0.8), int(WINDOW_HEIGHT * 0.55))],
            1: [(int(WINDOW_WIDTH * 0.45), int(WINDOW_HEIGHT * 0.4)),
                (int(WINDOW_WIDTH * 0.7), int(WINDOW_HEIGHT * 0.45))],
            2: [(int(WINDOW_WIDTH * 0.1), int(WINDOW_HEIGHT * 0.5)),
                (int(WINDOW_WIDTH * 0.3), int(WINDOW_HEIGHT * 0.87))],
            3: [(int(WINDOW_WIDTH * 0.9), int(WINDOW_HEIGHT * 0.75))]
        }
        
        # Choose position and store it as a tuple for texture lookup
        if self.room in allowed_positions:
            pos = random.choice(allowed_positions[self.room])
            self.x, self.y = pos
            self.current_texture = self.textures[self.room].get(pos)
        else:
            self.x = random.randint(CIRCLE_RADIUS, WINDOW_WIDTH - CIRCLE_RADIUS)
            self.y = random.randint(CIRCLE_RADIUS, WINDOW_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN - CIRCLE_RADIUS)
            self.current_texture = None
            
        self.next_spawn_time = time.time() + random.uniform(2, 5)
        self.active_time = None
        
    def update(self):
        current_time = time.time()
        if not self.active and current_time >= self.next_spawn_time:
            self.active = True
            self.active_time = current_time
            
    def draw(self, surface, current_room):
        if self.active and self.room == current_room:
            if self.current_texture:
                # Calculate position to center the larger texture
                texture_rect = self.current_texture.get_rect(center=(self.x, self.y))
                surface.blit(self.current_texture, texture_rect)
            else:
                # Fallback to larger circle if texture not available
                pygame.draw.circle(surface, YELLOW, (self.x, self.y), CIRCLE_RADIUS * 3)  # Tripled radius
                pygame.draw.circle(surface, BLACK, (self.x, self.y), CIRCLE_RADIUS * 3, 2)  # Border
            
    def is_clicked(self, pos, current_room):
        if not self.active or self.room != current_room:
            return False
        distance = ((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2) ** 0.5
        if distance <= CIRCLE_RADIUS * 3:
            self.reset()
            return True
        return False
        
    def check_timeout(self):
        if self.active and time.time() - self.active_time > 5:  # 5 seconds timeout
            return True
        return False
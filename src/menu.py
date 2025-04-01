import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import os

class MenuItem:
    def __init__(self, text, position, size=(300, 60), callback=None):
        self.text = text
        self.position = position  # Center position (x, y)
        self.size = size  # Width, height
        self.callback = callback
        self.hover = False
        self.active = False
        
        # Create font for the button text
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 32, bold=True)
    
    def is_point_inside(self, point):
        x, y = point
        left = self.position[0] - self.size[0] / 2
        right = self.position[0] + self.size[0] / 2
        top = self.position[1] - self.size[1] / 2
        bottom = self.position[1] + self.size[1] / 2
        
        return left <= x <= right and top <= y <= bottom
    
    def set_hover(self, is_hover):
        self.hover = is_hover
    
    def activate(self):
        self.active = True
        if self.callback:
            self.callback()
    
    def render(self, surface):
        # Calculate corners
        half_width = self.size[0] / 2
        half_height = self.size[1] / 2
        left = self.position[0] - half_width
        right = self.position[0] + half_width
        top = self.position[1] - half_height
        bottom = self.position[1] + half_height
        
        # Choose color based on state
        if self.active:
            # Pressed state - darker red
            bg_color = (180, 40, 40)
            border_color = (255, 255, 255)
        elif self.hover:
            # Hover state - brighter red
            bg_color = (220, 60, 60)
            border_color = (255, 255, 255)
        else:
            # Normal state - standard red
            bg_color = (180, 20, 20)
            border_color = (220, 220, 220)
        
        # Draw button background using pygame
        pygame.draw.rect(surface, bg_color, (left, top, self.size[0], self.size[1]))
        pygame.draw.rect(surface, border_color, (left, top, self.size[0], self.size[1]), 2)
        
        # Render the text
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.position[0], self.position[1]))
        surface.blit(text_surface, text_rect)


class MainMenu:
    def __init__(self, display_size, start_game_callback):
        self.display_size = display_size
        self.start_game_callback = start_game_callback
        self.active = True
        self.time_elapsed = 0
        
        # Create a surface for 2D UI elements
        self.surface = pygame.Surface(display_size, pygame.SRCALPHA)
        
        # Create menu items
        center_x = display_size[0] / 2
        center_y = display_size[1] / 2
        
        self.start_button = MenuItem(
            "Start Game", 
            (center_x, center_y + 100), 
            (300, 60),
            self.start_game
        )
        
        self.quit_button = MenuItem(
            "Quit", 
            (center_x, center_y + 200), 
            (200, 60),
            self.quit_game
        )
        
        self.menu_items = [self.start_button, self.quit_button]
        
        # Create logo text font
        self.logo_font = pygame.font.SysFont('Impact', 120, bold=True)
        
        # Initialize sound
        try:
            pygame.mixer.init()
            self.music_path = os.path.join('assets', 'sound', 'music.mp3')
            
            # Check if the music file exists and isn't already playing
            if os.path.exists(self.music_path) and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.set_volume(0.3)  # 50% volume
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                print("Menu music started")
        except Exception as e:
            print(f"Error setting up menu music: {e}")
    
    def start_game(self):
        self.active = False
        self.start_game_callback()
    
    def quit_game(self):
        pygame.quit()
        exit()
    
    def handle_input(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
        # Check for button hover
        for item in self.menu_items:
            item.set_hover(item.is_point_inside(mouse_pos))
        
        # Check for mouse clicks
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                for item in self.menu_items:
                    if item.hover:
                        item.activate()
                        break
    
    def update(self, delta_time):
        self.time_elapsed += delta_time
    
    def render(self):
        # Clear the screen with a dark background
        glClearColor(0.1, 0.1, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Clear the 2D surface
        self.surface.fill((0, 0, 0, 0))
        
        # Draw background
        pygame.draw.rect(self.surface, (25, 25, 38), (0, 0, self.display_size[0], self.display_size[1]))
        
        # Draw logo text with pulsing effect
        scale = 1.0 + 0.05 * math.sin(self.time_elapsed * 2)
        logo_text = self.logo_font.render("THE WORST", True, (220, 20, 20))
        
        # Apply pulsing scale
        scaled_size = (int(logo_text.get_width() * scale), int(logo_text.get_height() * scale))
        scaled_logo = pygame.transform.scale(logo_text, scaled_size)
        
        # Position logo
        logo_rect = scaled_logo.get_rect(center=(self.display_size[0] / 2, self.display_size[1] / 3))
        self.surface.blit(scaled_logo, logo_rect)
        
        # Add subtitle
        subtitle_font = pygame.font.SysFont('Arial', 24)
        subtitle = subtitle_font.render("A First-Person Shooter Experience", True, (180, 180, 180))
        subtitle_rect = subtitle.get_rect(center=(self.display_size[0] / 2, self.display_size[1] / 3 + 80))
        self.surface.blit(subtitle, subtitle_rect)
        
        # Draw menu items
        for item in self.menu_items:
            item.render(self.surface)
        
        # Draw the surface to the screen using OpenGL
        self.render_surface_to_screen()
    
    def render_surface_to_screen(self):
        # Save current states
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display_size[0], self.display_size[1], 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable depth testing and lighting for 2D rendering
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Convert Pygame surface to texture
        texture_data = pygame.image.tostring(self.surface, "RGBA", 1)
        texture_id = glGenTextures(1)
        
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.display_size[0], self.display_size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        
        # Draw textured quad
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        # Fixed texture coordinate mapping to correct the upside-down rendering
        glTexCoord2f(0, 1); glVertex2f(0, 0)                           # Bottom-left
        glTexCoord2f(1, 1); glVertex2f(self.display_size[0], 0)       # Bottom-right
        glTexCoord2f(1, 0); glVertex2f(self.display_size[0], self.display_size[1])  # Top-right
        glTexCoord2f(0, 0); glVertex2f(0, self.display_size[1])      # Top-left
        glEnd()
        
        # Clean up
        glDisable(GL_TEXTURE_2D)
        glDeleteTextures(1, [texture_id])
        
        # Restore states
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
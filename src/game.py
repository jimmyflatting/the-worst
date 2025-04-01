import pygame
import os
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from .player import Player
from .skybox import Skybox
from .crosshair import Crosshair
from .terrain import Terrain
from .bullet import BulletManager
from .hud import HUD
from .enemy_manager import EnemyManager

class Game:
    def __init__(self, display_size):
        self.display_size = display_size
        self.terrain = Terrain(size=100, resolution=50)
        self.player = Player()
        self.player.set_terrain(self.terrain)
        self.skybox = Skybox()
        self.crosshair = Crosshair(display_size)
        self.hud = HUD(display_size)
        
        # Bullet system
        self.bullet_manager = BulletManager()
        
        # Enemy manager for handling waves of skulls
        self.enemy_manager = EnemyManager(self.terrain)
        
        # Set up clear color - sky blue
        glClearColor(0.5, 0.7, 1.0, 1.0)
        
        # Game state
        self.game_over = False
        self.last_time = pygame.time.get_ticks() / 1000.0
        
        # Enable fog for distance effect
        self.setup_fog()
        
        # Set up basic lighting
        self.setup_lighting()
        
        # Initialize sound system
        try:
            pygame.mixer.init()
            self.init_sounds()
        except Exception as e:
            print(f"Could not initialize sound system: {e}")
        
    def setup_fog(self):
        # Add fog to create depth perception
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogfv(GL_FOG_COLOR, (0.7, 0.8, 1.0, 1.0))  # Match horizon color
        glFogf(GL_FOG_START, 30.0)  # Start fog farther away
        glFogf(GL_FOG_END, 80.0)    # Extend fog distance
        
    def setup_lighting(self):
        # Set up basic ambient lighting
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up directional light (sun)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Position light (as directional)
        glLightfv(GL_LIGHT0, GL_POSITION, (0.5, 1.0, 0.5, 0.0))  # Directional from top-right
        
        # Ambient, diffuse and specular components
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.4, 0.4, 0.4, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 0.9, 1.0)) 
        
        # Enable normalization of normals
        glEnable(GL_NORMALIZE)
        
    def handle_input(self):
        # Handle mouse clicks for shooting
        mouse_buttons = pygame.mouse.get_pressed()
        current_time = pygame.time.get_ticks() / 1000.0
        
        if mouse_buttons[0]:  # Left mouse button
            self.bullet_manager.shoot(self.player, current_time)
        
    def handle_events(self, events):
        # Process any events sent from the main loop
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    print("R KEY PRESSED - DIRECT FROM MAIN")
                    if hasattr(self.player, 'weapon'):
                        self.player.weapon.start_reload()
        
    def update(self):
        # Calculate delta time
        current_time = pygame.time.get_ticks() / 1000.0
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        # If game is over, don't update
        if self.game_over:
            return
        
        # Get input events
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        mouse_rel = pygame.mouse.get_rel()
        
        # Process reload key directly here - this is our primary fix
        if keys[pygame.K_r]:
            if hasattr(self.player, 'weapon') and not self.player.weapon.is_reloading:
                reload_success = self.player.weapon.start_reload()
                if reload_success:
                    print("RELOAD INITIATED from key check!")
        
        # Also check for specific keydown event for better responsiveness
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if hasattr(self.player, 'weapon') and not self.player.weapon.is_reloading:
                        reload_success = self.player.weapon.start_reload()
                        if reload_success:
                            print("RELOAD INITIATED from event!")
        
        # Handle player input including weapon handling
        self.player.handle_input(events, keys, mouse_rel, current_time, delta_time)
        
        # Shoot if mouse button is clicked
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # Left mouse button
            self.bullet_manager.shoot(self.player, current_time)
        
        # Update weapon state separately to ensure it gets updated
        if hasattr(self.player, 'weapon'):
            self.player.weapon.update(delta_time)
        
        # Update player
        self.player.update(delta_time)
        
        # Update enemies
        self.enemy_manager.update(delta_time, self.player)
        
        # Check for enemy-player collisions
        self.enemy_manager.check_collisions(self.player)
        
        # Update bullets
        active_enemies = self.enemy_manager.get_active_enemies()
        self.bullet_manager.update(delta_time, active_enemies)
        
        # Check for bullet hits and handle scoring
        for enemy in active_enemies:
            if not enemy.is_alive:
                self.enemy_manager.handle_bullet_hit(enemy)
        
        # Check game over conditions
        if not self.player.is_alive:
            print("Game Over - Player died!")
            self.game_over = True
            
        # Handle exit events
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
    
    def render(self):
        # First render skybox
        glDisable(GL_DEPTH_TEST)
        glDepthMask(GL_FALSE)
        
        glPushMatrix()
        
        # For skybox, apply only rotation
        modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
        for i in range(3):
            modelview[3][i] = 0
        glLoadMatrixf(modelview)
        
        # Render skybox
        self.skybox.render()
        
        glPopMatrix()
        
        # Re-enable depth for other objects
        glDepthMask(GL_TRUE)
        glEnable(GL_DEPTH_TEST)
        
        # Render 3D scene
        glPushMatrix()
        
        # Apply player's view
        self.player.apply_view()
        
        # Render terrain
        self.terrain.render()
        
        # Render enemies
        self.enemy_manager.render()
        
        # Render bullets
        self.bullet_manager.render()
        
        glPopMatrix()
        
        # Render 2D elements
        self.crosshair.render()
        
        # Render HUD
        self.hud.render(self.player, self.enemy_manager)
        
        # If game over, draw game over screen
        if self.game_over:
            self.render_game_over()
    
    def render_game_over(self):
        # Draw game over overlay
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display_size[0], self.display_size[1], 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Dark overlay
        glColor4f(0.0, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.display_size[0], 0)
        glVertex2f(self.display_size[0], self.display_size[1])
        glVertex2f(0, self.display_size[1])
        glEnd()
        
        # Game over box
        center_x = self.display_size[0] / 2
        center_y = self.display_size[1] / 2
        box_width = 400
        box_height = 200
        
        glColor4f(0.8, 0.2, 0.2, 0.9)
        glBegin(GL_QUADS)
        glVertex2f(center_x - box_width/2, center_y - box_height/2)
        glVertex2f(center_x + box_width/2, center_y - box_height/2)
        glVertex2f(center_x + box_width/2, center_y + box_height/2)
        glVertex2f(center_x - box_width/2, center_y + box_height/2)
        glEnd()
        
        # In a real game, you'd render text here with score
        
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def init_sounds(self):
        """Initialize and load sound effects and music"""
        try:
            # Set up background music
            self.music_path = os.path.join('assets', 'sound', 'music.mp3')
            
            # Check if the music file exists
            if os.path.exists(self.music_path):
                print(f"Loading music from: {self.music_path}")
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.set_volume(0.3)  # 50% volume
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                print("Background music started")
            else:
                print(f"Warning: Music file not found at {self.music_path}")
            
            # We could also load other sound effects here
            # self.sound_shot = pygame.mixer.Sound(os.path.join('assets', 'sound', 'shot.wav'))
            # self.sound_hit = pygame.mixer.Sound(os.path.join('assets', 'sound', 'hit.wav'))
            # etc.
        
        except Exception as e:
            print(f"Error loading sounds: {e}")

    def cleanup(self):
        """Stop music and release resources when game is exiting"""
        try:
            pygame.mixer.music.stop()
            print("Background music stopped")
        except:
            pass
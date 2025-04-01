import pygame
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from .weapon import Weapon

class Player:
    def __init__(self, position=None):
        # Initialize position
        self.position = position or [0, 2, 0]  # Default position with y=2 to start above ground
        self.velocity = [0, 0, 0]
        self.acceleration = [0, 0, 0]
        
        # Camera/rotation values
        self.rotation = [0, 0, 0]  # [pitch, yaw, roll] in degrees
        self.camera_height = 1.8  # Eye level in world units
        
        # Physics parameters
        self.gravity = -9.8
        self.move_speed = 20.0  # Increased from 10.0 to 15.0
        self.jump_force = 4.5
        self.is_grounded = False
        
        # Health and status
        self.health = 100
        self.max_health = 100
        self.damage_flash_time = 0
        self.is_alive = True
        
        # Collision values
        self.collision_radius = 0.5  # Player radius for collision detection
        
        # Add weapon
        self.weapon = Weapon()
        
        # Store reference to terrain
        self.terrain = None
    
    def set_terrain(self, terrain):
        """Set the terrain reference for collision detection"""
        self.terrain = terrain
    
    def handle_input(self, events, keys, mouse_rel, current_time, delta_time):
        # Handle mouse movement for looking around
        # Adjust rotation based on mouse movement
        self.rotation[1] += mouse_rel[0] * 0.2  # Yaw (left/right)
        self.rotation[0] -= mouse_rel[1] * 0.2  # Pitch (up/down)
        
        # Clamp pitch to prevent over-rotation
        self.rotation[0] = max(-89, min(89, self.rotation[0]))
        
        # Normalize yaw to stay within 0-360 range
        self.rotation[1] %= 360
        
        # Movement controls
        # Get directional vectors based on current rotation
        yaw_rad = math.radians(self.rotation[1])
        forward_vec = [math.sin(yaw_rad), 0, -math.cos(yaw_rad)]
        right_vec = [math.cos(yaw_rad), 0, math.sin(yaw_rad)]
        
        # Reset horizontal acceleration
        self.acceleration[0] = 0
        self.acceleration[2] = 0
        
        # Move forward/backward
        if keys[pygame.K_w]:
            self.acceleration[0] += forward_vec[0] * self.move_speed
            self.acceleration[2] += forward_vec[2] * self.move_speed
        if keys[pygame.K_s]:
            self.acceleration[0] -= forward_vec[0] * self.move_speed
            self.acceleration[2] -= forward_vec[2] * self.move_speed
        
        # Strafe left/right
        if keys[pygame.K_a]:
            self.acceleration[0] -= right_vec[0] * self.move_speed
            self.acceleration[2] -= right_vec[2] * self.move_speed
        if keys[pygame.K_d]:
            self.acceleration[0] += right_vec[0] * self.move_speed
            self.acceleration[2] += right_vec[2] * self.move_speed
        
        # Jump if grounded
        if keys[pygame.K_SPACE] and self.is_grounded:
            self.velocity[1] = self.jump_force
            self.is_grounded = False
        
        # DO NOT handle reload here anymore - it's handled in the Game class
    
    def update(self, delta_time):
        if not self.is_alive:
            return
            
        # Apply gravity if not grounded
        if not self.is_grounded:
            self.acceleration[1] = self.gravity
        else:
            self.acceleration[1] = 0
        
        # Update velocity based on acceleration
        self.velocity[0] += self.acceleration[0] * delta_time
        self.velocity[1] += self.acceleration[1] * delta_time
        self.velocity[2] += self.acceleration[2] * delta_time
        
        # Apply damping to horizontal velocity
        damping = 0.9
        self.velocity[0] *= damping
        self.velocity[2] *= damping
        
        # Update position based on velocity
        new_pos = [
            self.position[0] + self.velocity[0] * delta_time,
            self.position[1] + self.velocity[1] * delta_time,
            self.position[2] + self.velocity[2] * delta_time
        ]
        
        # Check for terrain collision and adjust position if terrain is set
        if self.terrain:
            terrain_height = self.terrain.get_height(new_pos[0], new_pos[2])
            player_feet_height = new_pos[1]  # Bottom of player collision cylinder
            
            if player_feet_height < terrain_height:
                # Player is below terrain, move up and set as grounded
                new_pos[1] = terrain_height
                self.velocity[1] = 0
                self.is_grounded = True
            elif player_feet_height - terrain_height < 0.1:
                # Player is very close to terrain, consider grounded
                self.is_grounded = True
            else:
                # Player is above terrain
                self.is_grounded = False
        
        # Update position
        self.position = new_pos
        
        # Update damage flash
        if self.damage_flash_time > 0:
            self.damage_flash_time -= delta_time
    
    def take_damage(self, amount):
        if not self.is_alive:
            return False
            
        self.health = max(0, self.health - amount)
        self.damage_flash_time = 0.3  # Flash red for 0.3 seconds
        
        if self.health <= 0:
            self.is_alive = False
            return True  # Return True if player died
        
        return False
    
    def check_collision(self, entity, collision_distance=None):
        if not hasattr(entity, 'position'):
            return False
            
        dx = self.position[0] - entity.position[0]
        dz = self.position[2] - entity.position[2]
        
        # Use provided collision distance or sum of radii
        if collision_distance is None:
            entity_radius = getattr(entity, 'collision_radius', 0.5)
            collision_distance = self.collision_radius + entity_radius
        
        # Check horizontal distance only (cylinder collision)
        distance_sq = dx*dx + dz*dz
        
        return distance_sq < collision_distance * collision_distance
    
    def apply_view(self):
        """Apply first-person view transform"""
        # Apply a red tint if recently damaged
        if self.damage_flash_time > 0:
            # The closer to when damage was taken, the redder the screen
            flash_intensity = self.damage_flash_time / 0.3  # 0.3 is the flash time duration
            glColor4f(1.0, 0.3, 0.3, flash_intensity * 0.5)  # Semi-transparent red
            
            # Draw a fullscreen quad for the damage flash
            glPushMatrix()
            glLoadIdentity()
            
            # Disable depth test to draw over everything
            glDisable(GL_DEPTH_TEST)
            
            # Draw a fullscreen quad
            glBegin(GL_QUADS)
            glVertex3f(-1, -1, -0.9)
            glVertex3f(1, -1, -0.9)
            glVertex3f(1, 1, -0.9)
            glVertex3f(-1, 1, -0.9)
            glEnd()
            
            # Reset color and restore depth test
            glColor4f(1.0, 1.0, 1.0, 1.0)
            glEnable(GL_DEPTH_TEST)
            glPopMatrix()
        
        # Apply view rotation
        glRotatef(self.rotation[0], 1, 0, 0)  # Pitch
        glRotatef(self.rotation[1], 0, 1, 0)  # Yaw
        glRotatef(self.rotation[2], 0, 0, 1)  # Roll (usually 0)
        
        # Position the camera at player's view position
        glTranslatef(-self.position[0], -(self.position[1] + self.camera_height), -self.position[2])
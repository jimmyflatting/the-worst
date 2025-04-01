import math
from OpenGL.GL import *
from OpenGL.GLU import *

class Bullet:
    def __init__(self, position, direction, speed=1.0, lifespan=2.0):
        self.position = position.copy()
        self.direction = direction.copy()
        self.speed = speed
        self.lifespan = lifespan  # Time in seconds before bullet disappears
        self.active = True
        self.damage = 30  # Increased from 10 to 30 for more impact
    
    def update(self, delta_time):
        # Move the bullet along its direction
        self.position[0] += self.direction[0] * self.speed * delta_time
        self.position[1] += self.direction[1] * self.speed * delta_time
        self.position[2] += self.direction[2] * self.speed * delta_time
        
        # Decrease lifespan
        self.lifespan -= delta_time
        if self.lifespan <= 0:
            self.active = False
    
    def render(self):
        if not self.active:
            return
            
        # Draw a small sphere for the bullet
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        
        # Set bullet color (bright yellow)
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 0.0)
        
        # Draw bullet as a small sphere
        quadric = gluNewQuadric()
        gluSphere(quadric, 0.1, 8, 8)  # Small radius, low detail
        gluDeleteQuadric(quadric)
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    def check_collision(self, entity):
        # Simple sphere collision detection
        dx = self.position[0] - entity.position[0]
        dy = self.position[1] - entity.position[1]
        dz = self.position[2] - entity.position[2]
        
        # Calculate distance squared
        distance_sq = dx*dx + dy*dy + dz*dz
        
        # Check if distance is less than sum of radii
        # Use entity's collision radius instead of scale-based calculation
        entity_radius = entity.collision_radius if hasattr(entity, 'collision_radius') else max(entity.scale) * 1.0
        bullet_radius = 0.1  # Same as rendering size
        
        if distance_sq < (entity_radius + bullet_radius) ** 2:
            return True
        
        return False

class BulletManager:
    def __init__(self):
        self.bullets = []
        self.cooldown = 0.2  # Time between shots in seconds
        self.last_shot_time = 0
    
    def shoot(self, player, current_time):
        # Try to fire the weapon
        if player.weapon.shoot(current_time):
            # Calculate bullet direction from player's view
            pitch_rad = math.radians(player.rotation[0])
            yaw_rad = math.radians(player.rotation[1])
            
            # Direction vector normalized
            direction = [
                math.sin(yaw_rad) * math.cos(pitch_rad),
                -math.sin(pitch_rad),  # Negative for proper pitch direction
                -math.cos(yaw_rad) * math.cos(pitch_rad)
            ]
            
            # Create bullet at player's position, slightly forward
            bullet_pos = player.position.copy()
            # Adjust position to be at eye level and further forward
            bullet_pos[0] += direction[0] * 0.5
            bullet_pos[1] += direction[1] * 0.5 + player.camera_height  # Add camera height
            bullet_pos[2] += direction[2] * 0.5
            
            # Create and add the bullet
            bullet = Bullet(bullet_pos, direction, speed=40.0)  # Doubled speed
            bullet.damage = player.weapon.damage  # Use weapon damage
            self.bullets.append(bullet)
            return True
        
        return False
    
    def update(self, delta_time, entities):
        # Update all bullets
        for bullet in self.bullets[:]:
            bullet.update(delta_time)
            
            # Check for collisions with entities
            for entity in entities:
                if hasattr(entity, 'is_alive') and entity.is_alive:
                    if bullet.check_collision(entity) and bullet.active:
                        # Apply damage to entity
                        entity.take_damage(bullet.damage)
                        bullet.active = False
                        break
            
            # Remove inactive bullets
            if not bullet.active:
                self.bullets.remove(bullet)
    
    def render(self):
        # Render all active bullets
        for bullet in self.bullets:
            bullet.render()
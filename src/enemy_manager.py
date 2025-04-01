import os
import random
import math
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from .model import Model

class EnemyManager:
    def __init__(self, terrain):
        self.enemies = []
        self.terrain = terrain
        self.score = 0
        self.wave = 1
        self.enemies_per_wave = 3  # Start with 3 enemies, increase each wave
        self.spawn_cooldown = 0
        self.max_active_enemies = 5  # Maximum enemies active at once
        self.wave_cleared = True
        self.wave_spawned = False
        
        # Add damage cooldown tracking
        self.damage_cooldowns = {}  # Dictionary to track cooldown for each enemy
        self.damage_cooldown_time = 1.0  # One second between hits from same enemy
        
        # Load skull model path
        self.skull_model_path = os.path.join('src', 'assets', 'models', 'skull.obj')
        
        # Preload the skull model data to avoid lag when spawning
        print("Preloading skull model...")
        self.preloaded_skull = Model(self.skull_model_path)
        print("Skull model preloaded")
    
    def spawn_enemy(self, player_pos):
        # Determine spawn position (random position around player)
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(15, 25)  # Spawn 15-25 units away
        
        spawn_x = player_pos[0] + math.sin(angle) * distance
        spawn_z = player_pos[2] + math.cos(angle) * distance
        
        # Get terrain height at spawn position
        terrain_height = self.terrain.get_height(spawn_x, spawn_z)
        spawn_y = terrain_height + 1.5  # Spawn slightly above terrain
        
        # Create a new skull instance by cloning the preloaded model
        skull = self.preloaded_skull.clone()
        skull.id = len(self.enemies)  # Assign unique ID to each enemy
        
        # Set position
        skull.set_position(spawn_x, spawn_y, spawn_z)
        
        # Make small scale
        skull.set_scale(0.05, 0.05, 0.05)
        
        # Set collision radius
        skull.set_collision_radius(1.0)
        
        # Set initial rotation (X axis 270 degrees to face upright)
        skull.set_rotation(270, 0, 0)
        
        # Set movement parameters
        skull.set_speed(1.0)  # Reduced from 1.5 to 1.0
        
        # Add to enemies list
        self.enemies.append(skull)
        
        return skull
    
    def spawn_wave(self, player_pos):
        # Clear any remaining dead enemies from the list
        self.enemies = [e for e in self.enemies if e.is_alive]
        
        # Spawn all enemies for the current wave
        for i in range(self.enemies_per_wave):
            skull = self.spawn_enemy(player_pos)
            # Slightly different health for variety
            skull.health = random.randint(80, 120)
            skull.max_health = skull.health
        
        self.wave_spawned = True
        self.wave_cleared = False
        print(f"Wave {self.wave} started with {self.enemies_per_wave} enemies!")
    
    def update(self, delta_time, player):
        # Count active enemies
        active_enemies = len([e for e in self.enemies if e.is_alive])
        
        # Check if wave is cleared
        if active_enemies == 0 and self.wave_spawned:
            self.wave_cleared = True
            self.wave_spawned = False
            self.wave += 1
            self.enemies_per_wave += 1  # Increase enemies per wave
            self.max_active_enemies = min(10, self.max_active_enemies + 1)  # Cap at 10
            print(f"Wave {self.wave-1} cleared! Next wave will have {self.enemies_per_wave} enemies.")
            self.spawn_cooldown = 3.0  # Delay before next wave
        
        # Spawn new wave if needed
        if self.wave_cleared:
            if self.spawn_cooldown <= 0:
                self.spawn_wave(player.position)
            else:
                self.spawn_cooldown -= delta_time
        
        # Update all enemies
        for enemy in self.enemies:
            if enemy.is_alive:
                # Set player as target
                enemy.set_target(player.position)
                
                # Update enemy
                enemy.update(delta_time)
                
                # Calculate angle to face player
                dx = enemy.position[0] - player.position[0]
                dz = enemy.position[2] - player.position[2]
                angle = math.degrees(math.atan2(dx, dz))
                
                # Apply rotation - keep X at 270 to face upright, Y for tracking player
                enemy.set_rotation(270, angle, 0)
                
                # Adjust Y position based on terrain
                terrain_height = self.terrain.get_height(enemy.position[0], enemy.position[2])
                y_pos = terrain_height + 1.0  # Float 1 unit above terrain
                enemy.position[1] = y_pos
    
    def check_collisions(self, player):
        current_time = pygame.time.get_ticks() / 1000.0
        
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
                
            if player.check_collision(enemy, collision_distance=1.5):
                # Check if this enemy is on cooldown
                enemy_id = enemy.id
                last_hit_time = self.damage_cooldowns.get(enemy_id, 0)
                
                # Only apply damage if cooldown has expired
                if current_time - last_hit_time >= self.damage_cooldown_time:
                    # Apply damage and update cooldown
                    if player.take_damage(5):  # 5 damage per hit
                        print(f"Player took damage! Health: {player.health}")
                    
                    # Record time of this hit
                    self.damage_cooldowns[enemy_id] = current_time
    
    def handle_bullet_hit(self, enemy):
        # When enemy is defeated by bullet
        if not enemy.is_alive:
            self.score += 1
            print(f"Enemy defeated! Score: {self.score}")
    
    def render(self):
        # Only render the enemies themselves, no health bars
        for enemy in self.enemies:
            enemy.render()
    
    def get_active_enemies(self):
        return [e for e in self.enemies if e.is_alive]
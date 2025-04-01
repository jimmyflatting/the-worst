import pygame
import os

class Weapon:
    def __init__(self):
        self.name = "Desert Eagle"
        self.max_ammo = 7  # Desert Eagle typically has 7 rounds per magazine
        self.current_ammo = 7  # Start with a full magazine
        self.damage = 40  # Increased damage to kill skulls faster
        
        # Reload properties
        self.is_reloading = False
        self.reload_time = 2.0  # seconds
        self.reload_progress = 0.0
        
        # Firing properties
        self.last_shot_time = 0
        self.cooldown = 0.3  # 300ms between shots - slightly faster
        
        # Sound effects
        self.sound_shot = None
        self.sound_empty = None
        self.sound_reload = None
        
        # Load sound effects
        self.load_sounds()
        
        print("Weapon initialized with damage:", self.damage)
    
    def load_sounds(self):
        """Load weapon sound effects"""
        try:
            pygame.mixer.init()
            
            # Load Desert Eagle shot sound
            shot_path = os.path.join('src', 'assets', 'sound', 'deserteagle.mp3')
            if os.path.exists(shot_path):
                self.sound_shot = pygame.mixer.Sound(shot_path)
                self.sound_shot.set_volume(1.0)  # 40% volume to not overpower music
                print(f"Loaded weapon sound: {shot_path}")
            else:
                print(f"Warning: Weapon sound file not found at {shot_path}")
            
            # We could also load empty and reload sounds here
            # empty_path = os.path.join('src', 'assets', 'sound', 'empty.mp3')
            # reload_path = os.path.join('src', 'assets', 'sound', 'reload.mp3')
        except Exception as e:
            print(f"Error loading weapon sounds: {e}")
    
    def shoot(self, current_time):
        # Check if we're reloading
        if self.is_reloading:
            print("Can't shoot while reloading")
            return False
        
        # Check cooldown
        if current_time - self.last_shot_time < self.cooldown:
            # Still on cooldown
            return False
        
        # Check ammo
        if self.current_ammo <= 0:
            print("Out of ammo! Press R to reload.")
            # Play empty sound effect instead of auto-reloading
            # if self.sound_empty:
            #     self.sound_empty.play()
            return False
        
        # Update state
        self.current_ammo -= 1
        self.last_shot_time = current_time
        
        # Play gunshot sound
        if self.sound_shot:
            self.sound_shot.play()
        
        print(f"Shot fired! Ammo: {self.current_ammo}/{self.max_ammo}")
        return True
    
    def start_reload(self):
        # Add more debug output to diagnose the issue
        print(f"start_reload called. Current state: ammo={self.current_ammo}/{self.max_ammo}, is_reloading={self.is_reloading}")
        
        # Only reload if not already reloading and not full
        if not self.is_reloading and self.current_ammo < self.max_ammo:
            self.is_reloading = True
            self.reload_progress = 0.0
            print("⭐ RELOAD STARTED ⭐")
            return True
        elif self.is_reloading:
            print("Cannot reload: Already reloading")
        elif self.current_ammo >= self.max_ammo:
            print("Cannot reload: Magazine already full")
        return False
    
    def update(self, delta_time):
        # Process reload
        if self.is_reloading:
            self.reload_progress += delta_time
            
            # Finished reloading
            if self.reload_progress >= self.reload_time:
                self.current_ammo = self.max_ammo  # Unlimited ammo, always refill to max
                self.is_reloading = False
                self.reload_progress = 0.0
                print("⭐ RELOAD COMPLETE ⭐ - Ammo now", self.current_ammo)
import pygame
from OpenGL.GL import *

class HUD:
    def __init__(self, display_size):
        self.display_size = display_size
        
        # Create fonts for text rendering
        pygame.font.init()
        self.font_large = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 20, bold=True)
        
        # Create surface for text rendering
        self.text_surface = pygame.Surface((display_size[0], display_size[1]), pygame.SRCALPHA)
    
    def render(self, player, enemy_manager):
        # Clear the text surface
        self.text_surface.fill((0, 0, 0, 0))
        
        # Draw wave and enemy counter at top center
        active_enemies = len([e for e in enemy_manager.enemies if e.is_alive])
        wave_text = f"Wave {enemy_manager.wave}"
        enemies_text = f"{active_enemies}/{enemy_manager.enemies_per_wave} enemies remaining"
        
        # Render wave text
        wave_surf = self.font_large.render(wave_text, True, (255, 255, 255))
        wave_rect = wave_surf.get_rect(center=(self.display_size[0] // 2, 40))
        self.text_surface.blit(wave_surf, wave_rect)
        
        # Render enemies counter
        enemies_surf = self.font_medium.render(enemies_text, True, (255, 255, 255))
        enemies_rect = enemies_surf.get_rect(center=(self.display_size[0] // 2, 80))
        self.text_surface.blit(enemies_surf, enemies_rect)
        
        # Render score in top right
        score_text = f"Score: {enemy_manager.score}"
        score_surf = self.font_medium.render(score_text, True, (220, 220, 40))
        score_rect = score_surf.get_rect(topright=(self.display_size[0] - 20, 20))
        self.text_surface.blit(score_surf, score_rect)
        
        # Switch to orthographic projection for 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display_size[0], self.display_size[1], 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable lighting and depth testing for HUD
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Draw player health bar (bottom left)
        health_y = self.display_size[1] - 40
        self.draw_health_bar(20, health_y, 200, 20, player.health, player.max_health, (0.2, 0.8, 0.2))
        
        # Draw health label
        health_label = f"Health: {int(player.health)}/{player.max_health}"
        health_surf = self.font_small.render(health_label, True, (255, 255, 255))
        health_rect = health_surf.get_rect(bottomleft=(25, health_y - 5))
        self.text_surface.blit(health_surf, health_rect)
        
        # Draw ammo counter (bottom right)
        ammo_y = self.display_size[1] - 40
        ammo_x = self.display_size[0] - 220
        
        # Get ammo info from player's weapon
        current_ammo = player.weapon.current_ammo if hasattr(player, 'weapon') else 7
        max_ammo = player.weapon.max_ammo if hasattr(player, 'weapon') else 7
        
        # Draw ammo background
        self.draw_ammo_display(ammo_x, ammo_y, 200, 20, current_ammo, max_ammo)
        
        # Draw ammo label
        ammo_label = f"Ammo: {current_ammo}/{max_ammo}"
        ammo_surf = self.font_small.render(ammo_label, True, (255, 255, 255))
        ammo_rect = ammo_surf.get_rect(bottomright=(self.display_size[0] - 25, ammo_y - 5))
        self.text_surface.blit(ammo_surf, ammo_rect)
        
        # Show "Out of Ammo" warning if needed
        if current_ammo == 0 and not player.weapon.is_reloading:
            out_text = "Out of Ammo - Press R to Reload"
            out_surf = self.font_medium.render(out_text, True, (255, 80, 80))  # Red text
            out_rect = out_surf.get_rect(center=(self.display_size[0] // 2, self.display_size[1] - 120))
            self.text_surface.blit(out_surf, out_rect)
        
        # Draw reload progress bar if reloading
        if hasattr(player, 'weapon') and player.weapon.is_reloading:
            reload_progress = player.weapon.reload_progress / player.weapon.reload_time
            reload_width = 300
            reload_x = (self.display_size[0] - reload_width) // 2
            reload_y = self.display_size[1] - 80
            
            # Draw reload bar background
            glColor4f(0.2, 0.2, 0.2, 0.8)
            glBegin(GL_QUADS)
            glVertex2f(reload_x, reload_y)
            glVertex2f(reload_x + reload_width, reload_y)
            glVertex2f(reload_x + reload_width, reload_y + 15)
            glVertex2f(reload_x, reload_y + 15)
            glEnd()
            
            # Draw reload progress
            progress_width = reload_width * reload_progress
            glColor4f(0.8, 0.6, 0.2, 0.9)  # Orange-yellow for reload
            glBegin(GL_QUADS)
            glVertex2f(reload_x, reload_y)
            glVertex2f(reload_x + progress_width, reload_y)
            glVertex2f(reload_x + progress_width, reload_y + 15)
            glVertex2f(reload_x, reload_y + 15)
            glEnd()
            
            # Draw border
            glColor4f(1.0, 1.0, 1.0, 0.7)
            glLineWidth(1.0)
            glBegin(GL_LINE_LOOP)
            glVertex2f(reload_x, reload_y)
            glVertex2f(reload_x + reload_width, reload_y)
            glVertex2f(reload_x + reload_width, reload_y + 15)
            glVertex2f(reload_x, reload_y + 15)
            glEnd()
            
            # Draw "RELOADING" text
            reload_text = "RELOADING"
            reload_surf = self.font_small.render(reload_text, True, (255, 255, 255))
            reload_rect = reload_surf.get_rect(midtop=(self.display_size[0] // 2, reload_y - 25))
            self.text_surface.blit(reload_surf, reload_rect)
        
        # Render the text surface to OpenGL
        self.render_text_surface()
        
        # Re-enable depth testing
        glEnable(GL_DEPTH_TEST)
        
        # Restore matrices
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def draw_health_bar(self, x, y, width, height, current, maximum, color):
        # Draw background
        glColor4f(0.2, 0.2, 0.2, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
        # Draw health
        health_percent = current / maximum
        bar_width = width * health_percent
        
        # Change color based on health (green -> yellow -> red)
        if health_percent > 0.6:
            bar_color = (0.2, 0.8, 0.2)  # Green
        elif health_percent > 0.3:
            bar_color = (0.8, 0.8, 0.2)  # Yellow
        else:
            bar_color = (0.8, 0.2, 0.2)  # Red
        
        glColor4f(bar_color[0], bar_color[1], bar_color[2], 0.8)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + bar_width, y)
        glVertex2f(x + bar_width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
        # Draw border
        glColor4f(0.8, 0.8, 0.8, 0.9)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
    
    def draw_ammo_display(self, x, y, width, height, current, maximum):
        # Draw background
        glColor4f(0.2, 0.2, 0.2, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
        # Draw individual bullet slots
        slot_width = width / maximum
        slot_padding = 2
        slot_inner_width = slot_width - (slot_padding * 2)
        
        for i in range(maximum):
            slot_x = x + (i * slot_width) + slot_padding
            slot_y = y + slot_padding
            slot_height = height - (slot_padding * 2)
            
            # Determine if this bullet slot should be filled
            is_filled = i < current
            
            # Draw bullet slot (filled or empty)
            if is_filled:
                # Filled slot (gold color for bullets)
                glColor4f(0.9, 0.7, 0.1, 0.9)
            else:
                # Empty slot (dark gray)
                glColor4f(0.3, 0.3, 0.3, 0.5)
            
            glBegin(GL_QUADS)
            glVertex2f(slot_x, slot_y)
            glVertex2f(slot_x + slot_inner_width, slot_y)
            glVertex2f(slot_x + slot_inner_width, slot_y + slot_height)
            glVertex2f(slot_x, slot_y + slot_height)
            glEnd()
        
        # Draw border
        glColor4f(0.7, 0.6, 0.1, 0.9)  # Gold border for ammo
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
    
    def render_text_surface(self):
        # Enable texture and blending
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Convert Pygame surface to texture
        texture_data = pygame.image.tostring(self.text_surface, "RGBA", 1)
        texture_id = glGenTextures(1)
        
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.display_size[0], self.display_size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        
        # Draw textured quad
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(0, 0)
        glTexCoord2f(1, 1); glVertex2f(self.display_size[0], 0)
        glTexCoord2f(1, 0); glVertex2f(self.display_size[0], self.display_size[1])
        glTexCoord2f(0, 0); glVertex2f(0, self.display_size[1])
        glEnd()
        
        # Clean up
        glDisable(GL_TEXTURE_2D)
        glDeleteTextures(1, [texture_id])
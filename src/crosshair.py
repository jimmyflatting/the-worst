import pygame
from OpenGL.GL import *

class Crosshair:
    def __init__(self, display_size):
        self.display_size = display_size
        self.size = 20  # Size of the crosshair
        self.color = (1.0, 1.0, 1.0, 0.8)  # White with slight transparency
    
    def render(self):
        # Switch to orthographic projection for 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display_size[0], self.display_size[1], 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Disable depth testing for HUD elements
        glDisable(GL_DEPTH_TEST)
        
        # Draw crosshair
        center_x = self.display_size[0] // 2
        center_y = self.display_size[1] // 2
        
        glColor4fv(self.color)
        glLineWidth(2.0)
        
        # Horizontal line
        glBegin(GL_LINES)
        glVertex2f(center_x - self.size, center_y)
        glVertex2f(center_x + self.size, center_y)
        glEnd()
        
        # Vertical line
        glBegin(GL_LINES)
        glVertex2f(center_x, center_y - self.size)
        glVertex2f(center_x, center_y + self.size)
        glEnd()
        
        # Reset to previous state
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
        
        # Restore matrices
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
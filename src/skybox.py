import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class Skybox:
    def __init__(self):
        self.size = 50.0  # Larger size for more distant sky
        # Make colors brighter and more vivid
        self.top_color = (0.4, 0.6, 0.9)      # Sky blue
        self.horizon_color = (0.7, 0.85, 1.0)  # Lighter blue at horizon
        self.ground_color = (0.2, 0.6, 0.2)    # Ground/grass color
        
        # Create a textured look with some clouds
        self.create_cloud_pattern()
        
    def create_cloud_pattern(self):
        # This method would normally load textures
        # For now, we'll simulate clouds with a procedural pattern
        self.cloud_density = 0.3  # More clouds with higher values
        self.cloud_scale = 0.05   # Size of cloud details
        
    def cloud_pattern(self, x, y, z):
        # Simple procedural pattern to simulate clouds
        # Returns value between 0-1 where higher values are more "cloudy"
        value = abs(math.sin(x * self.cloud_scale) * 
                   math.cos(z * self.cloud_scale) * 
                   math.sin(x * z * self.cloud_scale * 0.1))
        return value > (1 - self.cloud_density)
    
    def render(self):
        # Save current attributes and matrix state
        glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT)
        
        # Important: Disable lighting for skybox if it's enabled
        glDisable(GL_LIGHTING)
        
        # Disable depth writing (but keep testing) so skybox is always in background
        glDepthMask(GL_FALSE)
        
        # Save current matrix
        glPushMatrix()
        
        # This is crucial: remove translation component from view matrix
        # so skybox stays centered on camera
        modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
        
        # Remove translation part
        for i in range(3):
            modelview[3][i] = 0
            
        # Apply only rotation to keep skybox centered on player
        glLoadMatrixf(modelview)
        
        size = self.size
        
        # Draw the sky - simplified to ensure it works
        # Simple box approach first to verify rendering
        
        # Top face (sky)
        glBegin(GL_QUADS)
        glColor3fv(self.top_color)
        glVertex3f(-size, size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, size, size)
        glVertex3f(-size, size, size)
        glEnd()
        
        # Side faces with gradient
        # Front face
        glBegin(GL_QUADS)
        glColor3fv(self.horizon_color)
        glVertex3f(-size, -size, -size)
        glVertex3f(size, -size, -size)
        glColor3fv(self.top_color)
        glVertex3f(size, size, -size)
        glVertex3f(-size, size, -size)
        glEnd()
        
        # Back face
        glBegin(GL_QUADS)
        glColor3fv(self.horizon_color)
        glVertex3f(-size, -size, size)
        glVertex3f(size, -size, size)
        glColor3fv(self.top_color)
        glVertex3f(size, size, size)
        glVertex3f(-size, size, size)
        glEnd()
        
        # Left face
        glBegin(GL_QUADS)
        glColor3fv(self.horizon_color)
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, -size, size)
        glColor3fv(self.top_color)
        glVertex3f(-size, size, size)
        glVertex3f(-size, size, -size)
        glEnd()
        
        # Right face
        glBegin(GL_QUADS)
        glColor3fv(self.horizon_color)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size, size)
        glColor3fv(self.top_color)
        glVertex3f(size, size, size)
        glVertex3f(size, size, -size)
        glEnd()
        
        # Bottom face (ground)
        glBegin(GL_QUADS)
        glColor3fv(self.ground_color)
        glVertex3f(-size, -size, -size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size, size)
        glVertex3f(-size, -size, size)
        glEnd()
        
        # Restore matrix and attributes
        glPopMatrix()
        glDepthMask(GL_TRUE)  # Re-enable depth writing
        glPopAttrib()
    
    def mix_colors(self, color1, color2, factor):
        # Linear interpolation between two colors
        r = color1[0] * (1 - factor) + color2[0] * factor
        g = color1[1] * (1 - factor) + color2[1] * factor
        b = color1[2] * (1 - factor) + color2[2] * factor
        return (r, g, b)
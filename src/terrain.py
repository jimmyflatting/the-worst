import pygame
import math
import random
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

class Terrain:
    def __init__(self, size=100, resolution=50):
        self.size = size  # Size of the terrain in world units
        self.resolution = resolution  # Grid resolution
        self.heights = None
        self.cell_size = size / resolution
        
        # Generate heightmap
        self.generate_heightmap()
        self.create_display_list()
        
    def generate_heightmap(self):
        # Create a random heightmap using Perlin-like noise
        self.heights = np.zeros((self.resolution + 1, self.resolution + 1))
        
        # Parameters for our noise
        scale = 15.0  # Higher values = more stretched out
        octaves = 4   # Number of layers of detail
        persistence = 0.5  # How much each octave contributes
        lacunarity = 2.0   # How frequency increases each octave
        
        # Generate height values
        for y in range(self.resolution + 1):
            for x in range(self.resolution + 1):
                nx = x / self.resolution - 0.5
                ny = y / self.resolution - 0.5
                
                # Apply several octaves of noise for more natural terrain
                height = 0
                amplitude = 1.0
                frequency = 1.0
                
                for i in range(octaves):
                    sx = nx * frequency * scale
                    sy = ny * frequency * scale
                    
                    # Simple coherent noise function
                    value = self.noise2d(sx, sy)
                    
                    height += value * amplitude
                    amplitude *= persistence
                    frequency *= lacunarity
                
                # Scale and offset the height
                height = height * 2.0  # Scale height by 2 units
                
                # Create valleys where height is below a threshold
                if height < -0.3:
                    height = -0.3 + (height + 0.3) * 0.3  # Flatten valleys
                
                # Store the height
                self.heights[y, x] = height
    
    def noise2d(self, x, y):
        # Simple coherent noise function
        # In a real implementation, you would use a proper noise library
        # This is a simple approximation
        n = x * 12.9898 + y * 78.233
        return math.sin(n) * 43758.5453 % 1.0
    
    def get_height(self, x, z):
        # Convert world coordinates to grid coordinates
        grid_x = (x + self.size / 2) / self.cell_size
        grid_z = (z + self.size / 2) / self.cell_size
        
        # Clamp to grid boundaries
        grid_x = max(0, min(self.resolution, grid_x))
        grid_z = max(0, min(self.resolution, grid_z))
        
        # Determine grid cell
        cell_x = int(grid_x)
        cell_z = int(grid_z)
        
        # Guard against edge cases
        if cell_x >= self.resolution:
            cell_x = self.resolution - 1
        if cell_z >= self.resolution:
            cell_z = self.resolution - 1
        
        # Get fractional parts for interpolation
        fx = grid_x - cell_x
        fz = grid_z - cell_z
        
        # Bilinear interpolation of height values
        h1 = self.heights[cell_z, cell_x]
        h2 = self.heights[cell_z, cell_x + 1] if cell_x < self.resolution else h1
        h3 = self.heights[cell_z + 1, cell_x] if cell_z < self.resolution else h1
        h4 = self.heights[cell_z + 1, cell_x + 1] if cell_x < self.resolution and cell_z < self.resolution else h1
        
        # Interpolate height
        height1 = h1 * (1 - fx) + h2 * fx
        height2 = h3 * (1 - fx) + h4 * fx
        height = height1 * (1 - fz) + height2 * fz
        
        return height
    
    def create_display_list(self):
        # Create display list for faster rendering
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        
        # Base terrain colors
        grass_color = (0.3, 0.5, 0.2)  # Darker grass
        dirt_color = (0.6, 0.5, 0.3)   # Brown dirt
        stone_color = (0.5, 0.5, 0.5)   # Gray stone
        
        # Render ground as triangle strips
        half_size = self.size / 2
        
        for z in range(self.resolution):
            glBegin(GL_TRIANGLE_STRIP)
            for x in range(self.resolution + 1):
                # Calculate world coordinates
                world_x1 = x * self.cell_size - half_size
                world_z1 = z * self.cell_size - half_size
                world_z2 = (z + 1) * self.cell_size - half_size
                
                # Get heights
                height1 = self.heights[z, x]
                height2 = self.heights[z + 1, x]
                
                # Calculate normal for lighting
                # Simple normal calculation based on neighbors
                nx1 = self.heights[z, min(x+1, self.resolution)] - self.heights[z, max(x-1, 0)]
                nz1 = self.heights[min(z+1, self.resolution), x] - self.heights[max(z-1, 0), x]
                normal1 = [-nx1, 2.0, -nz1]
                
                nx2 = self.heights[z+1, min(x+1, self.resolution)] - self.heights[z+1, max(x-1, 0)]
                nz2 = self.heights[min(z+2, self.resolution), x] - self.heights[z, x]
                normal2 = [-nx2, 2.0, -nz2]
                
                # Normalize normals
                length1 = math.sqrt(normal1[0]**2 + normal1[1]**2 + normal1[2]**2)
                length2 = math.sqrt(normal2[0]**2 + normal2[1]**2 + normal2[2]**2)
                
                if length1 > 0:
                    normal1 = [n / length1 for n in normal1]
                if length2 > 0:
                    normal2 = [n / length2 for n in normal2]
                
                # Color based on height and slope
                slope1 = abs(normal1[1])  # How flat the surface is (0-1)
                slope2 = abs(normal2[1])
                
                # Choose color based on height and slope
                if height1 > 0.9:  # Mountain peaks
                    color1 = stone_color
                elif slope1 < 0.8:  # Steep slope = dirt
                    color1 = dirt_color
                else:  # Flatter areas = grass
                    color1 = grass_color
                    
                if height2 > 0.9:
                    color2 = stone_color
                elif slope2 < 0.8:
                    color2 = dirt_color
                else:
                    color2 = grass_color
                
                # Add some height-based color variation
                color1 = (color1[0] * (0.8 + height1 * 0.4),
                          color1[1] * (0.8 + height1 * 0.4),
                          color1[2] * (0.8 + height1 * 0.4))
                
                color2 = (color2[0] * (0.8 + height2 * 0.4),
                          color2[1] * (0.8 + height2 * 0.4),
                          color2[2] * (0.8 + height2 * 0.4))
                
                # Draw vertices with calculated normals and colors
                glNormal3fv(normal1)
                glColor3fv(color1)
                glVertex3f(world_x1, height1, world_z1)
                
                glNormal3fv(normal2)
                glColor3fv(color2)
                glVertex3f(world_x1, height2, world_z2)
            
            glEnd()
        
        glEndList()
    
    def render(self):
        # Render the terrain using the display list
        glCallList(self.display_list)
    
    def check_collision(self, position):
        # Get terrain height at position
        terrain_height = self.get_height(position[0], position[2])
        
        # Add a small buffer above the terrain for player "feet"
        player_height = 0.8  # Player height from ground
        
        if position[1] < terrain_height + player_height:
            # Collision detected, adjust position
            return [position[0], terrain_height + player_height, position[2]]
        
        return position
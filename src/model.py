import pygame
import math
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import copy

class Model:
    def __init__(self, file_path=None):
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self.position = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.scale = [1, 1, 1]
        
        # Add health and status
        self.health = 100
        self.max_health = 100
        self.is_alive = True
        self.damage_flash_time = 0
        
        # Add collision radius - separate from visual scale
        self.collision_radius = 1.0
        
        # Add movement parameters
        self.speed = 0.0  # Default is stationary
        self.target_position = None  # Target to move towards
        
        # Add unique ID
        self.id = -1  # Will be set by EnemyManager
        
        # Display list for fast rendering
        self.compiled_list = None
        
        # If a file path is provided, load the model
        if file_path:
            self.load_obj(file_path)
            self.compiled_list = self.create_display_list()
    
    def clone(self):
        """Create a copy of this model that shares the same geometry data but has independent 
        transform, health, and other instance-specific properties."""
        # Create a new model instance without loading from file
        new_model = Model()
        
        # Share the mesh data (vertices, normals, texcoords, faces)
        new_model.vertices = self.vertices
        new_model.normals = self.normals
        new_model.texcoords = self.texcoords
        new_model.faces = self.faces
        
        # Share the compiled display list for faster rendering
        new_model.compiled_list = self.compiled_list
        
        # Set default properties
        new_model.position = self.position.copy()
        new_model.rotation = self.rotation.copy()
        new_model.scale = self.scale.copy()
        new_model.health = self.health
        new_model.max_health = self.max_health
        new_model.is_alive = True
        new_model.damage_flash_time = 0
        new_model.collision_radius = self.collision_radius
        new_model.speed = 0.0
        new_model.target_position = None
        
        return new_model
    
    def load_obj(self, file_path):
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            vertices = []
            normals = []
            texcoords = []
            faces = []
            
            for line in lines:
                if line.startswith('#'):  # Comment
                    continue
                    
                values = line.split()
                if not values:
                    continue
                    
                if values[0] == 'v':  # Vertex
                    vertices.append([float(x) for x in values[1:4]])
                elif values[0] == 'vn':  # Normal
                    normals.append([float(x) for x in values[1:4]])
                elif values[0] == 'vt':  # Texture coordinate
                    texcoords.append([float(x) for x in values[1:3]])
                elif values[0] == 'f':  # Face
                    # Handle different face formats
                    face = []
                    for v in values[1:]:
                        w = v.split('/')
                        # OBJ indices start at 1, so we subtract 1
                        # Format: vertex/texcoord/normal
                        face.append([
                            int(w[0]) - 1 if len(w) > 0 and w[0] else -1,
                            int(w[1]) - 1 if len(w) > 1 and w[1] else -1,
                            int(w[2]) - 1 if len(w) > 2 and w[2] else -1
                        ])
                    faces.append(face)
            
            self.vertices = vertices
            self.normals = normals
            self.texcoords = texcoords
            self.faces = faces
            
            print(f"Loaded model: {file_path}")
            print(f"  Vertices: {len(vertices)}")
            print(f"  Normals: {len(normals)}")
            print(f"  TexCoords: {len(texcoords)}")
            print(f"  Faces: {len(faces)}")
            
        except Exception as e:
            print(f"Error loading model {file_path}: {e}")
            
    def create_display_list(self):
        """Create an OpenGL display list for faster rendering."""
        display_list = glGenLists(1)
        glNewList(display_list, GL_COMPILE)
        
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            # For each vertex in the face
            for vertex_data in face:
                v_idx, t_idx, n_idx = vertex_data
                
                # Apply normal if available
                if n_idx >= 0 and n_idx < len(self.normals):
                    glNormal3fv(self.normals[n_idx])
                
                # Apply texture coordinate if available
                if t_idx >= 0 and t_idx < len(self.texcoords):
                    glTexCoord2fv(self.texcoords[t_idx])
                
                # Apply vertex position
                if v_idx >= 0 and v_idx < len(self.vertices):
                    glVertex3fv(self.vertices[v_idx])
        
        glEnd()
        glEndList()
        
        return display_list
    
    def set_position(self, x, y, z):
        self.position = [x, y, z]
        
    def set_rotation(self, x, y, z):
        self.rotation = [x, y, z]
        
    def set_scale(self, x, y, z):
        self.scale = [x, y, z]
        
    def set_collision_radius(self, radius):
        self.collision_radius = radius
    
    def set_speed(self, speed):
        self.speed = speed
    
    def set_target(self, target_position):
        self.target_position = target_position
    
    def take_damage(self, amount):
        if not self.is_alive:
            return
            
        self.health -= amount
        self.damage_flash_time = 0.3  # Flash for 0.3 seconds
        
        print(f"Enemy took {amount} damage! Health: {self.health}/{self.max_health}")
        
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            print("Enemy defeated!")
    
    def update(self, delta_time):
        # Update damage flash
        if self.damage_flash_time > 0:
            self.damage_flash_time -= delta_time
        
        # Move towards target if set and alive
        if self.target_position and self.is_alive and self.speed > 0:
            # Calculate direction vector to target
            dx = self.target_position[0] - self.position[0]
            dz = self.target_position[2] - self.position[2]
            
            # Calculate distance
            distance = math.sqrt(dx*dx + dz*dz)
            
            # Only move if not at target
            if distance > 0.1:  # Small threshold to prevent jitter
                # Normalize direction vector
                dx /= distance
                dz /= distance
                
                # Move towards target
                move_distance = self.speed * delta_time
                if move_distance > distance:
                    move_distance = distance  # Don't overshoot
                
                self.position[0] += dx * move_distance
                self.position[2] += dz * move_distance
    
    def render(self):
        if not self.is_alive:
            return  # Don't render if not alive
            
        glPushMatrix()
        
        # Apply transformations
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(self.scale[0], self.scale[1], self.scale[2])
        
        # Set material properties
        if self.damage_flash_time > 0:
            # Flash red when taking damage
            glDisable(GL_LIGHTING)
            glColor3f(1.0, 0.0, 0.0)  # Bright red
        else:
            # Normal rendering
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            
            # Set material properties for skull (bone-like)
            glMaterialfv(GL_FRONT, GL_AMBIENT, (0.4, 0.4, 0.4, 1.0))
            glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.8, 0.8, 0.75, 1.0))  # Slightly yellowish
            glMaterialfv(GL_FRONT, GL_SPECULAR, (0.3, 0.3, 0.3, 1.0))
            glMaterialf(GL_FRONT, GL_SHININESS, 30.0)
        
        # Render the model using the compiled display list
        glCallList(self.compiled_list)
        
        # Restore state
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
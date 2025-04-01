# Vertex shader code for rendering the skybox

# This shader transforms the vertex positions of the skybox and passes the texture coordinates to the fragment shader.
# It assumes that the skybox is rendered with a cube geometry.

# Version of GLSL
#version 330 core

# Input vertex position
layout(location = 0) in vec3 aPos;

# Output texture coordinates to the fragment shader
out vec3 TexCoords;

# Uniforms for the view and projection matrices
uniform mat4 projection;
uniform mat4 view;

void main()
{
    // Set the vertex position for the skybox
    gl_Position = projection * view * vec4(aPos, 1.0);
    
    // Pass the texture coordinates to the fragment shader
    TexCoords = aPos; // Assuming the skybox uses the same coordinates for textures
}
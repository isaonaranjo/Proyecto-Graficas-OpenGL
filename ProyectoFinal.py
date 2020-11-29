# Maria Isabel Ortiz Naranjo
# Carne:18176
# Proyecto Final: OpenGL

import pygame
import numpy
import glm
import pyassimp
from math import sin, tan, cos
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

pygame.init()

screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

vertex_shader = """
#version 450
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texcoords;


uniform mat4 theMatrix;
uniform mat4 MaNormal;
uniform vec3 light;
uniform float timer;

out float intensity;
out vec2 vertexTexcoords;
out vec4 shaderNormal;
out float time;

void main()
{
  vertexTexcoords = texcoords;
  intensity = dot(normal, normalize(light));
  time = timer;
  shaderNormal = normalize(MaNormal * vec4(normal, 1.0));
  gl_Position = theMatrix * vec4(position.x, position.y, position.z, 1.0);
}
"""

fragment_shader = """
#version 450
layout(location = 0) out vec4 fragColor;

in float intensity;
in vec2 vertexTexcoords;
in vec4 shaderNormal;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{

  fragColor = ambient + diffuse * texture(tex, vertexTexcoords) * intensity;
}
"""

time_shader = """
#version 450
layout(location = 0) out vec4 fragColor;

in float intensity;
in float intensity2;
in vec2 vertexTexcoords;
in vec4 shaderNormal;
in float time;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	fragColor = intensity * vec4(cos(time * 5.0), sin(time * 2.0), tan(time * 3.0), 1.0);
}
"""

tex_shader = """
#version 450
layout(location = 0) out vec4 fragColor;

in float intensity;
in vec2 vertexTexcoords;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
  fragColor = ambient + texture(tex, vertexTexcoords) * intensity;
}
"""

azul_shader = """
#version 450
layout(location = 0) out vec4 fragColor;

in float intensity;
in float intensity2;
in vec4 shaderNormal;
in float time;
in vec2 vertexTexcoords;
uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	fragColor = (shaderNormal * 1.1);
}
"""

shader = compileProgram(
    compileShader(vertex_shader, GL_VERTEX_SHADER),
    compileShader(fragment_shader, GL_FRAGMENT_SHADER)
)



scene = pyassimp.load('./LP_Firefox.obj')
print(scene)
texture_surface = pygame.image.load('./textura.png')
texture_data = pygame.image.tostring(texture_surface, 'RGB',1)
width = texture_surface.get_width()
height = texture_surface.get_height()

texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)
glTexImage2D(
  GL_TEXTURE_2D,
  0,
  GL_RGB,
  width,
  height,
  0,
  GL_RGB,
  GL_UNSIGNED_BYTE,
  texture_data
)
glGenerateMipmap(GL_TEXTURE_2D)

def glize(node):
  # render
  for mesh in node.meshes:
    vertex_data = numpy.hstack([
      numpy.array(mesh.vertices, dtype=numpy.float32),
      numpy.array(mesh.normals, dtype=numpy.float32),
      numpy.array(mesh.texturecoords[0], dtype=numpy.float32),
    ])

    index_data = numpy.hstack(
      numpy.array(mesh.faces, dtype=numpy.int32),
    )

    vertex_buffer_object = glGenVertexArrays(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(6 * 4))
    glEnableVertexAttribArray(2)

    element_buffer_object = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, element_buffer_object)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)


    glUniform3f(
      glGetUniformLocation(shader, "light"),
      #-100, 185, 0.2
      #-100, 300, 0
      -450,5000,7000
      #100, 300, 0.2
    )

    glUniform4f(
      glGetUniformLocation(shader, "diffuse"),
      0.7, 0.3, 0.3, 1
      #0.7, 1, 1, 1
      #1, 0.2, 0, 1
    )

    glUniform4f(
      glGetUniformLocation(shader, "ambient"),
      0.3, 0.2, 0.1, 1
      #1, 0, 0.02, 0.5
      #-0.1, 0.2, 0.1, -1.0
    )

    glDrawElements(GL_TRIANGLES, len(index_data), GL_UNSIGNED_INT, None)

  for child in node.children:
    glize(child)


i = glm.mat4()

def createTheMatrix(counter,x,y):
  translate = glm.translate(i, glm.vec3(0, 0, 0))
  rotate = glm.rotate(i, glm.radians(counter), glm.vec3(0, 1, 0))
  scale = glm.scale(i, glm.vec3(1, 1, 1))

  model = translate * rotate * scale
  view = glm.lookAt(glm.vec3(8 + x, 10 + x, 18 + y), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
  projection = glm.perspective(glm.radians(45), 800/600, 0.1, 1000)

  return projection * view * model

glViewport(0, 0, 800, 600)

glEnable(GL_DEPTH_TEST)

time = 0
x =0
y = 0
running = True
counter = 0
while running:
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  glClearColor(0, 0, 0, 0)

  glUseProgram(shader)


  MaNormal= createTheMatrix(counter,x,y)
  theMatrix = createTheMatrix(counter,x,y)

  theMatrixLocation = glGetUniformLocation(shader, 'theMatrix')

  glUniformMatrix4fv(
    theMatrixLocation, # location
    1, # count
    GL_FALSE,
    glm.value_ptr(theMatrix)
  )

  MaNormalLocation = glGetUniformLocation(shader, 'MaNormal')

  glUniformMatrix4fv(
		MaNormalLocation, # location
		1, # count
		GL_FALSE,
		glm.value_ptr(MaNormal)
	)

  time += 0.5
	
  glUniform1f(
    glGetUniformLocation(shader, 'timer'),
    time
	)

  glize(scene.rootnode)

  pygame.display.flip()

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
      print('keydown')
      if event.key == pygame.K_w:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
      if event.key == pygame.K_4:
        shader = compileProgram(
          compileShader(vertex_shader, GL_VERTEX_SHADER),
          compileShader(time_shader, GL_FRAGMENT_SHADER)
          )
        glUseProgram(shader)
      if event.key == pygame.K_f:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
      if event.key == pygame.K_5:
        shader = compileProgram(
          compileShader(vertex_shader, GL_VERTEX_SHADER),
          compileShader(tex_shader, GL_FRAGMENT_SHADER)
          )
        glUseProgram(shader)
      if event.key == pygame.K_a:
        shader = compileProgram(
          compileShader(vertex_shader, GL_VERTEX_SHADER),
          compileShader(azul_shader, GL_FRAGMENT_SHADER)
          )
        glUseProgram(shader)


  counter += 1
  clock.tick()
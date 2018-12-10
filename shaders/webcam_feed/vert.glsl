#version 330 core
layout(location = 0) in vec2 texcoord;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec3 vposition;

out vec4 vertColor;
out vec2 o_texcoord;
out vec3 o_normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
  gl_Position = projection * view * model * vec4(vposition, 1.0);
  o_texcoord = texcoord;
  o_normal = normal;
  vertColor = vec4(0.5, 0.0, 0.0, 1.0);
}
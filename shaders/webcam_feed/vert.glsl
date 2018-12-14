#version 330 core
layout(location = 4) in vec2 wtexcoord;
layout(location = 5) in vec3 wvposition;

out vec2 o_texcoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
  gl_Position = projection * view * model * vec4(wvposition, 1.0);
  // gl_Position = vec4(wvposition, 1.0);
  o_texcoord = wtexcoord;
}
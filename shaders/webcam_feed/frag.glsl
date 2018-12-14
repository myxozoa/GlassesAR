#version 330 core
out vec4 outputColor;

in vec2 o_texcoord;

uniform sampler2D texture1;

void main()
{
  outputColor = texture(texture1, o_texcoord);
}
#version 330 core
out vec4 outputColor;

in vec4 vertColor;
in vec3 o_normal;
in vec2 o_texcoord;

void main()
{
  vec3 test = o_normal + vec3(o_texcoord, 1.);
  outputColor = vec4(test, 1.);
}
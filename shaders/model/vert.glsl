#version 330 core
layout(location = 0) in vec2 vtexcoord;
layout(location = 1) in vec3 vnormal;
layout(location = 2) in vec3 vposition;

out vec3 WorldPos;
out vec2 TexCoords;
out vec3 Normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
  WorldPos = vec3(model * vec4(vposition, 1.0));
  gl_Position = projection * view * vec4(WorldPos, 1.0);
  TexCoords = vtexcoord;
  Normal = normalize(mat3(transpose(inverse(model))) * vnormal);
}

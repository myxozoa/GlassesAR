from PIL import Image
from OpenGL.GL import *
from pywavefront import Wavefront
import itertools


def load_MTL(filename):
  contents = {}
  mtl = None
  for line in open("./assets/" + filename, "r"):
    if line.startswith('#'): continue
    values = line.split()
    if not values: continue
    if values[0] == 'newmtl':
      mtl = contents[values[1]] = {}
    elif mtl is None:
      raise ValueError("mtl file doesn't start with newmtl stmt")
    elif values[0] == 'map_Kd':
      # load the texture referred to by this declaration
      mtl[values[0]] = values[1]
      surf = Image.open("./assets/" + mtl['map_Kd'])
      ix, iy, image = surf.size[0], surf.size[1], surf.tobytes("raw", "RGB", 0, -1)
      texid = mtl['texture_Kd'] = glGenTextures(1)
      glBindTexture(GL_TEXTURE_2D, texid)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
          GL_LINEAR)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
          GL_LINEAR)
      glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGB,
          GL_UNSIGNED_BYTE, image)
    else:
      mtl[values[0]] = list(map(float, values[1:]))
  return contents

class load_OBJ:
    def __init__(self, filename, swapyz=False):
      """Loads a Wavefront OBJ file. """
      self.vertices = []
      self.normals = []
      self.texcoords = []
      self.faces = []
      self.face_indices = []
      self.mtl = None
      # self.gl_list = None

      self.buffer_data = []

      obj = Wavefront(filename, parse=False)
      obj.parse()

      # print(obj.vertices[0])
      # Contains the vertex format (string) such as "T2F_N3F_V3F"
      # T2F, C3F, N3F and V3F may appear in this string

      # flatten array of tuples
      # print(obj.vertices)
      # print(len(obj.faces))
      # print('mesh #')
      # print(obj.meshes[None].faces)

      for name, material in obj.materials.items():
        print(material.vertex_format)
        print(material.texture)
        # print(material.vertices)
        self.buffer_data = self.buffer_data + material.vertices

      # print(self.face_indices)
      # material = None
      # for line in open(filename, "r"):
      #   if line.startswith('#'): continue
      #   values = line.split()
      #   if not values: continue
      #   if values[0] == 'v':
      #     v = list(map(float, values[1:4]))
      #     if swapyz:
      #       v = v[0], v[2], v[1]
      #     self.vertices.append(v)
      #     # self.vertices = self.vertices + v
      #   elif values[0] == 'vn':
      #     v = list(map(float, values[1:4]))
      #     if swapyz:
      #       v = v[0], v[2], v[1]
      #     self.normals.append(v)
      #     # self.normals = self.normals + v
      #   elif values[0] == 'vt':
      #     v = list(map(float, values[1:3]))
      #     self.texcoords.append(v)
      #     # self.texcoords = self.texcoords + v
      #   elif values[0] in ('usemtl', 'usemat'):
      #     material = values[1]
      #   elif values[0] == 'mtllib':
      #     self.mtl = load_MTL(values[1])
      #   elif values[0] == 'f':
      #     face = []
      #     texcoords = []
      #     norms = []
      #     for v in values[1:]:
      #       w = v.split('/')
      #       face.append(int(w[0]))
      #       if len(w) >= 2 and len(w[1]) > 0:
      #         texcoords.append(int(w[1]))
      #       else:
      #         texcoords.append(0)
      #       if len(w) >= 3 and len(w[2]) > 0:
      #         norms.append(int(w[2]))
      #       else:
      #         norms.append(0)
      #     self.face_indices = self.face_indices + face
      #     self.faces.append((face, norms, texcoords, material))

      # for i in range(len(self.vertices)):
      #   self.buffer_data = self.buffer_data + self.vertices[i]
      #   self.buffer_data = self.buffer_data + self.normals[i]
      #   self.buffer_data = self.buffer_data + self.texcoords[i]

      # self.gl_list = glGenLists(1)
      # glNewList(self.gl_list, GL_COMPILE)
      # glEnable(GL_TEXTURE_2D)
      # glMaterial(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
      # glFrontFace(GL_CCW)
      # for face in self.faces:
      #   vertices, normals, texture_coords, material = face

      #   mtl = self.mtl[material]
      #   if 'texture_Kd' in mtl:
      #     # use diffuse texmap
      #     glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
      #   else:
      #     # just use diffuse colour
      #     glColor(*mtl['Kd'])

      #   glBegin(GL_POLYGON)
      #   for i in range(len(vertices)):
      #     if normals[i] > 0:
      #       glNormal3fv(self.normals[normals[i] - 1])
      #     if texture_coords[i] > 0:
      #       glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
      #     glVertex3fv(self.vertices[vertices[i] - 1])
      #   glEnd()
      # glDisable(GL_TEXTURE_2D)
      # glEndList()

def load_shaders(vertex_file_path, fragment_file_path):
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    with open(vertex_file_path, "r") as f:
        vertex_shader_code = f.read()
    with open(fragment_file_path, "r") as f:
        fragment_shader_code = f.read()

    glShaderSource(vertex_shader, vertex_shader_code)
    glCompileShader(vertex_shader)
    result = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
    info_log = glGetShaderInfoLog(vertex_shader)
    print(result, info_log)

    glShaderSource(fragment_shader, fragment_shader_code)
    glCompileShader(fragment_shader)
    result = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
    info_log = glGetShaderInfoLog(fragment_shader)
    print(result, info_log)

    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    result = glGetProgramiv(program, GL_LINK_STATUS)
    info_log = glGetProgramInfoLog(program)
    print(result, info_log)

    # glDetachShader(program, vertex_shader)
    # glDetachShader(program, fragment_shader)
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    return program
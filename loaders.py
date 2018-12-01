def loadobj(obj_name):
  obj = open(obj_name, "r")
  vertex_array = []
  triangle_sections = []


  for line in obj:
    line_split = line.split(" ")

    if line_split[0] == "v":
      vertex_array.append([ float(x) for x in line_split[1:] ])

    if line_split[0] == "f":
      # fix since obj files seem to have 1-indexed verticies
      temp = [ max(int(x) - 1, 0) for x in line_split[1:] ]

      triangle_sections.append(temp[0:2])
      triangle_sections.append(temp[1:3])

  vertex_array.append([0, 0, 0])

  return vertex_array, triangle_sections
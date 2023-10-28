import cv2
import numpy as np
import sys

def read_poly(file_path):

    vertices = []
    edges = []
    holes = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    v_total = -1
    e_total = -1
    h_total = -1
    section = None
    for i, line in enumerate(lines):

        line = line.strip()

        if i == 0:
            v_total = int(line.split()[0])
            section = "vertices"
            continue

        if i == (v_total + 1):
            e_total = int(line.split()[0])
            section = "edges"
            continue

        if i == (e_total + v_total + 2):
            h_total = int(line.split()[0])
            section = "holes"
            continue

        if section == 'vertices':
            vertex = line.split()[1:]
            #int_v = [int(int(v)/4) for v in vertex]
            int_v = [int(v) for v in vertex]
            vertices.append(int_v)
        elif section == 'edges':
            edge = line.split()[1:]
            int_e = [int(e) for e in edge]
            edges.append(int_e)
        elif section == 'holes' and h_total > 0 and len(line) > 1:
            hole = line.split()[1:]
            #int_h = [int(int(h)/4) for h in hole]
            int_h = [int(h) for h in hole]
            holes.append(int_h)

    return {
        'vertices': vertices,
        'edges': edges,
        'holes': holes
    }

def draw_poly(file_path):
    poly_data = read_poly(file_path)

    vertices = poly_data['vertices']
    edges = poly_data['edges']
    holes = poly_data['holes']

    min_x = min(vertices, key=lambda v: v[0])[0]
    max_x = max(vertices, key=lambda v: v[0])[0]
    min_y = min(vertices, key=lambda v: v[1])[1]
    max_y = max(vertices, key=lambda v: v[1])[1]

    img_w = max_x - min_x
    img_h = max_y - min_y
    
    padding_x = round(img_w * 0.1)
    padding_y = round(img_h * 0.1)
    padding = max(padding_x, padding_y)

    canvas_width = img_w + padding*2
    canvas_height = img_h + padding*2
    canvas_color = (255, 255, 255)

    canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
    canvas[:] = canvas_color

    x_displace = padding - min_x
    y_displace = padding - min_y

    for v in vertices:
        cv2.circle(canvas, (v[0]+x_displace, canvas_height-(v[1]+y_displace)), 2, (0,0,0), -1)

    for e in edges:
        p1,p2 = vertices[e[0]]
        q1,q2 = vertices[e[1]]

        start = (p1+x_displace,canvas_height-(p2+y_displace))
        end = (q1+x_displace,canvas_height-(q2+y_displace))

        cv2.line(canvas, start, end, (0,0,0), 1)
    
    for h in holes:
        cv2.circle(canvas, (h[0]+x_displace, canvas_height-(h[1]+y_displace)), 2, (0,0,255), -1)

    name = file_path.split(".")[-2]

    cv2.imshow('Poly', canvas)
    cv2.imwrite(name + "_poly.png", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

draw_poly(sys.argv[1])
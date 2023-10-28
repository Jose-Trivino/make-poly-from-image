import math
import matplotlib.pyplot as plt
import sys
import numpy as np

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
            int_v = [int(int(v)/4) for v in vertex]
            #int_v = [int(v) for v in vertex]
            vertices.append(int_v)
        elif section == 'edges':
            edge = line.split()[1:]
            int_e = [int(e) for e in edge]
            edges.append(int_e)
        elif section == 'holes' and h_total > 0 and len(line) > 1:
            hole = line.split()[1:]
            int_h = [int(int(h)/4) for h in hole]
            #int_h = [int(h) for h in hole]
            holes.append(int_h)

    return {
        'vertices': vertices,
        'edges': edges,
        'holes': holes
    }

def metrics(file_path):

    poly_data = read_poly(file_path)

    vertices = poly_data['vertices']
    edges = poly_data['edges']
    holes = poly_data['holes']

    print("")
    print("==============  Elementos generados ==============")
    print("")
    print("Vértices: " + str(len(vertices)))
    print("Aristas: " + str(len(edges)))
    print("Agujeros: " + str(len(holes)))

    lengths = []

    for e in edges:

        p1,p2 = vertices[e[0]]
        q1,q2 = vertices[e[1]]

        length = math.sqrt((q1-p1)**2 + (q2-p2)**2)
        lengths.append(length)

    std_dev = round(np.std(lengths),2)
    avg = round(np.mean(lengths),2)

    max_len = max(lengths)
    min_len = min(lengths)

    step = int((max_len-min_len)//10)
    if step == 0:
        step = 1
    stop = int(((max_len//step)+1)*step)

    bin_edges = range(0,stop,step)

    plt.hist(lengths, bins=bin_edges)
     
    #bin_edges = np.histogram_bin_edges(lengths, bins=10) 
    plt.xticks(bin_edges)  

    plt.xlabel('Longitudes')
    plt.ylabel('Frecuencia')
    plt.title('Total = ' + str(len(lengths)) + ' ; Promedio = ' + str(avg) + " ; Desviación = " + str(std_dev))

    plt.show()
    
metrics(sys.argv[1])
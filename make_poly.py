from triangle_method import border_tri as t
from canny_method import border_canny as c
import argparse
import ast
import time
import cv2

# poly_list structure:
# A list of polygons, where each polygon is a tuple
# The first element of the tuple is a list of edges
# where the last edge and the first edge are connected
# The second element is a bool which determines if 
# the polygon is a hole or not

def make_poly(path_list, name):
    v_count = 0
    e_count = 0
    h_count = 0

    v_string = ""
    e_string = ""
    h_string = ""

    for path in path_list:

        # Unpack path
        vertices, hole_point = path

        for i in range(len(vertices)):

            if i == len(vertices)-1:
                e_string += '{0} {1} {2}\n'.format(e_count, v_count, v_count-len(vertices)+1)
            else:
                e_string += '{0} {1} {2}\n'.format(e_count, v_count, v_count+1)
            e_count += 1

            x,y = vertices[i]
            v_string += '{0} {1} {2}\n'.format(v_count, x, -y)
            v_count += 1

        if hole_point is not None:

            h_string += '{0} {1} {2}\n'.format(h_count, hole_point[0], -hole_point[1])
            h_count += 1
    
    if h_count == 0:
        h_string += '0\n'

    f = open(name + '.poly', 'w')
    f.write("{} 2 0 0\n".format(v_count))
    f.write(v_string)
    f.write("{} 0\n".format(e_count))
    f.write(e_string)
    f.write("{} 0\n".format(h_count))
    f.write(h_string)
    f.write('\n')
    f.close()


def main(method, image, params, show):

    method_id = method[0]

    if method_id == "c":
        print("\nMétodo de detección de bordes a utilizar: Canny\n")
    else:
        print("\nMétodo de detección de bordes a utilizar: Triangulación\n")

    start = time.time()
    match method_id:
        case "c":
            reduction = params[0]
            r_params = params[1]
            max_dist = params[2]
            fuse_dist = params[3]
            bw_thresh = params[4]
            paths, result = c.main(image, reduction, r_params, max_dist, fuse_dist, bw_thresh)
        
        case "t":
            triangle_dim = params[0]
            iterations = params[1]
            bw_thresh = params[2]
            min_e_len = params[3]
            verbose = params[4]
            timelapse = params[5]
            lapse_img = params[6]
            
            paths, result = t.main(image, triangle_dim, iterations,bw_thresh, min_e_len, verbose, timelapse, lapse_img)

    name = image.split(".")[-2]

    make_poly(paths, name)
    end = time.time()
    print("Tiempo total transcurrido: " + str(round(end-start,4)) + "s")

    if result is not None and show:
        cv2.imshow("Result",result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


canny_params = [
    "hybrid", # Reduction method
    [20,1], # Reduction parameters
    15, # Maximum reduction distance
    5, # Maximum fuse distance
    254  # Black-white threshold
    ]

triangle_params = [
    [20,20], # Dimensions
    40, # Iterations
    254, # Black-white threshold
    3, # Minimum edge length
    False, # Verbose
    False, # Timelapse
    "color" # Image for timelapse
    ]

used_method = "canny"
used_params = canny_params

parser = argparse.ArgumentParser()
parser.add_argument("filename")       # Filename
parser.add_argument("--method")     # Method used
parser.add_argument("--thresh")     # Thresholding function value

parser.add_argument("--reduction")  # Reduction method (fixed, variable, mixed)
parser.add_argument("--len")        # Edge length (for fixed and mixed)
parser.add_argument("--maxdist")    # Maximum distance (for variable and mixed)
parser.add_argument("--fusedist")   # Maximum distance (for variable and mixed)
parser.add_argument("--pathdist")   # Maximum distance for path fusion

parser.add_argument("--x")          # Horizontal triangle number
parser.add_argument("--y")          # Vertical triangle number
parser.add_argument("--xy")         # Dimension as tuple or single number
parser.add_argument("--it")         # Number of iterations (for triangle)
parser.add_argument("--minlen")     # Minimun edge length

parser.add_argument("--verbose", action='store_true')    # Show log
parser.add_argument("--timelapse", action='store_true')  # Generate .gif with timelapse
parser.add_argument("--show", action='store_true')       # Show resulting image

args = parser.parse_args()

if not args.filename:
    print("Please input a file")

else:

    if args.reduction:
        if args.reduction[0] in ["f","v","h"]:
            canny_params[0] = args.reduction

    if args.thresh:
        canny_params[4] = int(args.thresh)
        triangle_params[2] = int(args.thresh)
    
    if args.len:
        canny_params[1][0] = int(args.len)
    if args.maxdist:
        canny_params[1][1] = float(args.maxdist)
    if args.fusedist:
        canny_params[3] = int(args.fusedist)
    if args.pathdist:
        canny_params[2] = int(args.pathdist)
    
    if canny_params[0][0] != "h":
        if canny_params[0][0] == "f":
            canny_params[1].pop(1)
        if canny_params[0][0] == "v":
            canny_params[1].pop(0)

    if args.x:
        triangle_params[0][0] = int(args.x)
    if args.y:
        triangle_params[0][1] = int(args.y)
    if args.xy:
        value = ast.literal_eval(args.xy)
        if isinstance(value, tuple):
            triangle_params[0][0] = value[0]
            triangle_params[0][1] = value[1]
        elif isinstance(value, int):
            triangle_params[0][0] = value
            triangle_params[0][1] = value

    if args.it:
        triangle_params[1] = int(args.it)

    if args.minlen:
        triangle_params[3] = int(args.minlen)

    if args.verbose:
        triangle_params[4] = bool(args.verbose)
    if args.timelapse:
        triangle_params[5] = bool(args.timelapse)

    if args.method:
        if args.method[0] == "t":
            used_method = "triangle"
            used_params = triangle_params

    main(used_method, args.filename, used_params, args.show)

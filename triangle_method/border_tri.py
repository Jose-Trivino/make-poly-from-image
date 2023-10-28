from .mesh import *
import cv2
import time
import imageio

# Save paths in make_poly.py format
def format_paths(path_list):
        
    def get_cross(p1,p2,q1,q2):
        a_0 = [p2[0]-p1[0],p2[1]-p1[1]]
        b_0 = [q2[0]-q1[0],q2[1]-q1[1]]

        return np.cross(a_0,b_0)

    new_path_list = []
    
    for path in path_list:
        new_path = [e.get_end().to_tuple() for e in path]

        min_y = min(new_path, key=lambda v: v[1])
        i = new_path.index(min_y)
        
        prev = new_path[(i-1)%len(new_path)]
        next = new_path[(i+1)%len(new_path)]

        edge_1 = [min_y, next]
        edge_2 = [prev, min_y]

        cross = get_cross(edge_1[0], edge_1[1], edge_2[1], edge_2[0])

        hole = None
        if cross > 0:
            hole = path[0].get_twin().get_triangle().centroid()
        if cross == 0:
            if prev[0] < min_y[0]:
                hole = path[0].get_twin().get_triangle().centroid()

        new_path_list.append((new_path, hole))

    return new_path_list

# Main function
def main(filename, triangle_dim, iterations, bw_thresh, min_e_len, verbose=False, lapse=False, lapse_img="color"):

    new_img = Image(filename, bw_thresh)

    x_tri, y_tri = triangle_dim
    new_img.add_mesh(x_tri, y_tri, min_e_len)

    counter = 0
    borders = []

    # Only necessary for final print
    t0 = time.time()
    times = []
    v_errs = []
    t_errs = []
    collapses = 0
    flips = 0
    t_inserts = 0
    e_inserts = 0

    # Only necessary for timelapse
    frames = []

    #new_img.health_check(True)

    new_img.update_all()

    while True:

        try:

            # Border check (only final iteration)
            if counter == iterations:
                new_img.border_update()

            # This is only necessary for timelapse
            if lapse or (not lapse and counter == iterations):
                new_frame = new_img.draw_full(lapse_img)
                frames.append(new_frame)
                #cv2.imwrite("Iterations/" + str(counter) + ".png", new_frame)

            if counter == iterations:
                borders = format_paths(new_img.border_get())

            # This is only necessary for final print
            errs = new_img.error_totals()
            v_errs.append(round(errs[0]/len(new_img.mesh.get_vertices()),2))
            t_errs.append(round(errs[1]/len(new_img.mesh.get_triangles()),2))

            counter += 1
            if counter >= iterations+1:
                break

            step_size = 1

            curr_it = "Iteración " + str(counter) + " / " + str(iterations)
            padding = " "*(18-len(curr_it))
            bar = "[" + "#"*counter + "-"*(iterations-counter) + "]"
            status = curr_it+padding+bar

            if not verbose:
                if counter < iterations:
                    print(status, end='\r')
                    print(end='', flush=True)
                else:
                    print(status+"\n")
            else:
                if counter > 1:
                    print("\n"+status+"\n")
                else:
                    print(status+"\n")

            # REFINEMENT

            # A. Improve approximation:
            # 1. Move vertices
            if counter < 15:
                new_img.move_vertices(step_size)
            else:
                new_img.move_vertices_seq(step_size)

            new_img.update_all()

            # 2. Edge flip for approximation error
            flips += new_img.edge_flip_g(verbose)

            # 3. Point insertion
            inserts = (0,0)
            if counter > 5 and counter < iterations-5:
                if counter%2 == 0:
                    inserts = new_img.insert_points(verbose)
                else:
                    inserts = new_img.insert_points_v(10,verbose)
                    
            t_inserts += inserts[0]
            e_inserts += inserts[1]

            # B. Restore triangulation
            # 4. Edge-flip
            flips += new_img.edge_flip(verbose)

            #new_img.health_check(True)

            # 5. Edge-collapse
            collapses += new_img.edge_collapse(verbose)
            
            #new_img.health_check()

            # Only necessary for final print
            t1 = time.time()
            times.append(round(t1-t0,2))
            t0 = t1
        
        except Exception as e:
            print(e)
            print("Error durante la ejecución. Por favor reintentar con otro conjunto de parámetros.")
            return [[], None]

    # End of refinement

    if iterations > 0 and verbose:
        print("")
        print("==================== Métricas ====================")

        print("")
        print("Disminución de error promedio en vértices:")
        print(v_errs)

        print("")
        print("Disminución de error promedio en triángulos:")
        print(t_errs)

        min_v, max_v, min_t, max_t = new_img.err_max_min()
        print("")
        print("Error de aproximación en vértices:")
        print("Min: " + str(round(min_v,2)) + " | Max: " + str(round(max_v,2)))
        print("Error de aproximación en triángulos:")
        print("Min: " + str(round(min_t,2)) + " | Max: " + str(round(max_t,2)))

        t_sum = round(sum(times),2)
        t_avg = round(t_sum/len(times),2)

        m1 = "Total de tiempo en iteraciones: " + str(t_sum) + "s"
        m2 = " (" + str(round(t_sum/60,2)) + " mins)"
        m3 = "Tiempo promedio por iteración: " + str(t_avg) + "s"
        print("")
        print(m1 + m2 + " | " + m3)

        print("")
        print("Edge-collapses totales: " + str(collapses))
        print("Edge-flips totales: " + str(flips))
        print("Inserción de puntos en triángulos: " + str(t_inserts))
        print("Inserción de puntos en aristas: " + str(e_inserts))
        print("")

    # Generating timelapse animation
    img_name =  filename.split(".")[-2] + "_"
    img_name += str(x_tri) + "x" + str(y_tri) + "_"
    img_name += str(iterations) + "it_"
    img_name += "minlen=" + str(min_e_len)
    img_name += ".gif"

    if len(frames) > 1:
        with imageio.get_writer(img_name, mode="I") as writer:
            for i in range(len(frames)):
                rgb_frame = cv2.cvtColor(frames[i], cv2.COLOR_BGR2RGB)
                frame_len = 0
                max_len = 3
                if i >= len(frames)-1:
                    max_len = 10
                while frame_len < max_len:
                    writer.append_data(rgb_frame)
                    frame_len += 1

    return [borders, frames[-1]]

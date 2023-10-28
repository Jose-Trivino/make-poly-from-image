import cv2
import random
import copy
from .vertex import *
from .edge import *
from .triangle import *

# Mesh class, contains list of vertices, edges and triangles
# Always associated with underlying image
class Mesh:
    def __init__(self, image, min_e_len):

        self.image = image # Associated Image object
        self.min_e_len = min_e_len # Minimum edge length for mesh

        # Element arrays
        self.vertices = []
        self.edges = []
        self.triangles = []

        self.t_area = None # Initial triangle area

    ###############
    #   GETTERS   #
    ###############

    def get_vertices(self):
        return self.vertices
    
    def get_edges(self):
        return self.edges
    
    def get_triangles(self):
        return self.triangles
    
    def get_t_area(self):
        return self.t_area
    
    def get_min_e_len(self):
        return self.min_e_len

    ###############
    #   SETTERS   #
    ###############

    def add_vertex(self, vertex):
        self.vertices.append(vertex)

    def remove_vertex(self, vertex):
        if vertex in self.vertices:
            self.vertices.remove(vertex)
        else:
            print("ERROR: Can't remove vertex not in mesh vertex list")
            return
    
    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print("ERROR: Can't remove edge not in mesh edge list")
            return
        
    def add_triangle(self, t):
        self.triangles.append(t)

    def remove_triangle(self, t):
        if t in self.triangles:
            self.triangles.remove(t)
        else:
            print("ERROR: Can't remove triangle not in mesh triangle list")
            return
        
    def set_t_area(self, val):
        self.t_area = val

    ###############
    #    MAKERS   #
    ###############

    # Makes new vertex and adds it to mesh
    def make_vertex(self, x_pos, y_pos, add=True):
        new_v = Vertex(self, x_pos, y_pos)
        if add:
            self.add_vertex(new_v)
        return new_v
    
    # Makes new edge and adds it to mesh
    def make_edge(self, start_v, end_v, add=True):

        new_e = Edge(self, start_v, end_v)
        if add:
            self.add_edge(new_e)

        start_v.add_edge(new_e)

        opp_e = end_v.check_opposite(start_v)
        if opp_e:
            new_e.set_twin(opp_e)
            opp_e.set_twin(new_e)

        return new_e

    # Makes new triangle and adds it to mesh
    def make_triangle(self, edge_list, add=True):

        e1, e2, e3 = edge_list

        cond_1 = e1.can_connect(e2)
        cond_2 = e2.can_connect(e3)
        cond_3 = e3.can_connect(e1)

        if not (cond_1 and cond_2 and cond_3):
            print("WARNING: Edges do not form a closed loop")

        new_t = Triangle(self, edge_list)
        if add:
            self.add_triangle(new_t)
        
        for i in range(len(edge_list)):
            edge_list[i].set_triangle(new_t)
            edge_list[i].set_prev_next(edge_list[(i+2)%3],edge_list[(i+1)%3])

        return new_t
    
    # Makes edges and triangle from 3 vertices
    def connect_3(self, v_list, add=True):

        e_list = []
        for i in range(len(v_list)):
            e_list.append(self.make_edge(v_list[i],v_list[(i+1)%3],add))

        new_t = self.make_triangle(e_list,add)
        return new_t
    
    #################
    #  INITIALIZERS #
    #################
        
    def make(self, img_h, img_v, h_tri, v_tri, same=False):

        # Size in pixels for each triangle
        step_h = (img_h-1)/h_tri
        step_v = (img_v-1)/v_tri

        self.set_t_area(step_h*step_v)

        # Temporary vertices matrix
        temp_vertices = []

        # Create vertices
        for j in range(v_tri+1):
            new_row = []
            for i in range(h_tri+1):

                new_v = self.make_vertex(round(i*step_h),round(j*step_v))

                # Setting allowed movement directions
                h_mov = not (i == 0 or i == h_tri)
                v_mov = not (j == 0 or j == v_tri)

                if h_mov:
                    new_v.add_movement([(1,0),(-1,0)])
                if v_mov:
                    new_v.add_movement([(0,1),(0,-1)])

                # Appending new vertex to array
                new_row.append(new_v)

            temp_vertices.append(new_row)

        temp_vertices_copy = copy.deepcopy(temp_vertices)

        # Connect vertices
        for y in range(v_tri):
            for x in range(h_tri):

                # a b 
                # c d
                oa = temp_vertices[y][x]
                ob = temp_vertices[y][x+1]
                oc = temp_vertices[y+1][x]
                od = temp_vertices[y+1][x+1]

                va = temp_vertices_copy[y][x]
                vb = temp_vertices_copy[y][x+1]
                vc = temp_vertices_copy[y+1][x]
                vd = temp_vertices_copy[y+1][x+1]

                # NE connection [/]
                acb = self.connect_3([va,vc,vb], False)
                bcd = self.connect_3([vb,vc,vd], False)

                g_acb = acb.update_err(True)
                g_bcd = bcd.update_err(True)

                flip_false = g_acb + g_bcd

                # NW connection [\]
                acd = self.connect_3([va,vc,vd], False)
                adb = self.connect_3([va,vd,vb], False)

                g_acd = acd.update_err(True)
                g_adb = adb.update_err(True)

                flip_true = g_acd + g_adb

                # [\] case, create edges and triangles and append to lists
                if flip_true < flip_false or same:
                    self.connect_3([oa,oc,od])
                    self.connect_3([oa,od,ob])
                # [/] case, create edges and triangles and append to lists
                else:
                    self.connect_3([oa,oc,ob])
                    self.connect_3([ob,oc,od])

    ################
    #   UPDATERS   #
    ################

    # Update approximation error for every triangle
    # True parameter ensures that points and color
    # will be recalculated
    def update_triangles(self):
        for t in self.get_triangles():
            t.update_err(True)

    # Update approximation error for every vertex
    # No parameters means that the error value
    # will be updated for every vertex
    def update_vertices(self):
        for v in self.get_vertices():
            v.update_err()
    
    # For every vertex, the movement direction is calculated again
    # and then the vertices are moved in that direction
    # step size can be modified for testing purposes
    def move_vertices(self, step=1, verbose=None):

        total_v = len(self.get_vertices())
        counter = 1
        for v in self.get_vertices():
            if verbose:
                s = "[" + str(counter) + "/" + str(total_v) + "] " + verbose
                print(s)
                counter += 1
            v.update_mov_dir()

        for v in self.get_vertices():
            if v.get_mov_dir() != (0,0):
                x,y = v.get_mov_dir()
                v.move((x*step,y*step))

    # Move vertices sequentially, sorted by approximation error starting with highest
    def move_vertices_seq(self, step=1, verbose=None):
        
        sorted_v = sorted(self.get_vertices(), key=lambda v: v.get_err())
        total_v = len(self.get_vertices())
        counter = 1

        for v in sorted_v:

            if verbose:
                s = "[" + str(counter) + "/" + str(total_v) + "] " + verbose
                print(s)
                counter += 1
            v.update_mov_dir()

            if v.get_mov_dir() != (0,0):
                x,y = v.get_mov_dir()
                v.move((x*step,y*step))

    ################
    #  REFINEMENT  #
    ################

    # Edge flip for mesh structure
    # Geometry-based trigger
    # Helpful for triangles with base too wide
    # CONDITION: Opposite angle > 140
    def edge_flip(self, verbose=False):
        flips = 0

        e_len = len(self.get_edges())
        i = 0

        while i < e_len:

            e = self.get_edges()[i]
            flipped = False

            angle = e.get_opp_angle_sum()

            if angle:
                if angle > 240:
                    if e.edge_flip():
                        flips += 1
                        flipped = True
                        e_len -= 6
            
            if not flipped:
                i += 1
    
        if verbose:
            print("Edge-flips realizados: " + str(flips))
        
        return flips
    
    # Edge flip for image approximation
    # Executes edge flip if it decreases approximation error sum in triangles
    def edge_flip_g(self, verbose=False):
        flips = 0

        e_len = len(self.get_edges())
        i = 0

        while i < e_len:
            e = self.get_edges()[i]
            flipped = False
            if e.get_twin():
                if e.get_adj_angle() < 135 and e.get_twin().get_adj_angle() < 135:
                    if e.test_edge_flip():
                        flips += 1
                        e_len -= 6
                        flipped = True
            
            if not flipped:
                i += 1

        if verbose:
            print("Edge-flips realizados: " + str(flips))
        
        return flips   

    # Edge collapse for mesh structure
    # Helpful with triangles with very small base
    def edge_collapse(self, verbose=False):
        collapses = 0

        e_len = len(self.get_edges())
        i = 0

        # CASE 1: Edge too short
        while i < e_len:
            coll_1 = False
            e = self.get_edges()[i]

            if e.length() < self.get_min_e_len():
                coll_t_1 = e.edge_collapse()
                if coll_t_1 > 0:
                    collapses += 1
                    coll_1 = True
                    e_len -= coll_t_1*3
            
            if not coll_1:
                i += 1

        t_len = len(self.get_triangles())
        j = 0

        # CASE 2: Triangle too small
        while j < t_len:
            coll_2 = False
            t = self.get_triangles()[j]

            if t.bounding_box_area() < self.get_t_area()*0.2:
                coll_t_2 = t.shortest_edge().edge_collapse()
                if coll_t_2 > 0:
                    collapses += 1
                    coll_2 = True
                    t_len -= coll_t_2

            if not coll_2:
                j += 1

        if verbose:
            print("Edge-collapses realizados: " + str(collapses))
        
        return collapses

    # Point insertion in triangle or edge
    # CONDITION: Edge or triangle depending on proximity to middle vertex
    def insert_points(self, verbose=False):

        t_inserts = 0
        e_inserts = 0

        t_len = len(self.get_triangles())
        i = 0

        while i < t_len:
            t = self.get_triangles()[i]

            if t.get_new():
                i += 1
                continue

            # Insertion case 1: Triangle too big
            cond_1 = t.bounding_box_area() > self.get_t_area() * 3

            # Insertion case 2: Approximation error too high
            cond_2 = t.bounding_box_area() >= self.get_t_area() * 0.9 and t.get_err() > 100

            if cond_1 or cond_2:

                # Obtuse triangle, insert on edge
                if t.largest_angle() > 90 or t.smallest_angle() < 45:
                    if t.test_insert_point_edge(t.longest_edge()):
                        e_inserts += 1
                        t_len -= 2
                    else:
                        i += 1

                # Approximately equilateral triangle, insert in triangle
                else:
                    if t.test_insert_point():
                        t_inserts += 1
                        t_len -= 1
                    else:
                        i += 1
            
            else:
                    i += 1

        if verbose:
            print("Inserciones de puntos en triángulos: " + str(t_inserts))
            print("Inserciones de puntos en aristas: " + str(e_inserts))
        
        return (t_inserts, e_inserts)
    
    # Insert points in edge if vertex isn't moving and still has approximation error
    def insert_points_v(self, min_g, verbose=False):
        e_inserts = 0

        v_len = len(self.get_vertices())
        i = 0

        while i < v_len:
            v = self.get_vertices()[i]
            if v.get_mov_dir() == (0,0) and v.get_err() > min_g:
                #target_t = v.largest_t()
                target_t = v.highest_err_t()
                if target_t.bounding_box_area() >= self.get_t_area() * 0.7:
                    if target_t.test_insert_point():
                        e_inserts += 1

            i += 1
        
        if verbose:
            print("Inserciones de puntos en aristas: " + str(e_inserts))
        
        return (0, e_inserts)
    
    def border_update(self):
        for e in self.edges:
            e.update_is_border()
    
    def border_get(self):
        loop_list = []
        for e in self.edges:
            loop = e.get_loop()
            if len(loop) > 0:
                loop_list.append(loop)

        return loop_list
    
    # Check mesh integrity
    def health_check(self, verbose=False):

        broken_t = 0
        broken_e = 0
        broken_v = 0

        for t in self.triangles:

            is_broken_t = False

            for i in range(len(t.edges)):

                # Edge check 1: Adjacent edges form a closed loop
                if t.get_edge(i).get_end() != t.get_edge((i+1)%3).get_start():
                    if verbose:
                        print("\nERROR [T]: Aristas no forman un ciclo cerrado")
                        t.print()
                        t.get_edge(i).print()
                        t.get_edge((i+1)%3).print()
                    is_broken_t = True
                
                # Edge check 2: Adjacent edges associated with self
                if t.get_edge(i).get_triangle() != t:
                    if verbose:
                        print("\nERROR [T]: Triángulo no presente en arista adyacente")
                        t.print()
                        t.get_edge(i).print()
                        t.get_edge(i).get_triangle().print()
                    is_broken_t = True
                
                # Mesh check: Check if adjacent edges in mesh
                if t.get_edge(i) not in self.get_edges():
                    if verbose:
                        print("\nERROR [T]: Triángulo contiene aristas no presentes en la malla")
                        t.print()
                    is_broken_t = True
            
            if is_broken_t:
                broken_t += 1

        for e in self.edges:

            is_broken_e = False

            # Vertex check: Edge in start_v edge list
            if e not in e.get_start().get_edges():
                if verbose:
                    print("\nERROR [E]: Arista no presente en vértice de inicio")
                    e.print()
                    e.get_start().print()
                    for v_e in e.get_start().get_edges():
                        v_e.print()
                is_broken_e = True
            
            # Start check: Check if start_v in mesh
            if e.get_start() not in self.get_vertices():
                if verbose:
                    print("\nERROR [E]: Arista contiene vértice de inicio no presente en la malla")
                    e.print()
                is_broken_e = True

            # End check: Check if start_v in mesh
            if e.get_end() not in self.get_vertices():
                if verbose:
                    print("\nERROR [E]: Arista contiene vértice de término no presente en la malla")
                    e.print()
                is_broken_e = True

            if e.get_twin():

                # Mesh check: Opposite edge in mesh
                if e.get_twin() not in self.get_edges():
                    if verbose:
                        print("\nERROR [E]: Arista contiene vértice opuesto no presente en la malla")
                        e.print()
                        e.get_twin().print()
                    is_broken_e = True

                # Opposite check: Opposite edge has same coordinates
                cond_1 = e.get_start() == e.get_twin().get_end()
                cond_2 = e.get_end() == e.get_twin().get_start()

                if not (cond_1 and cond_2):
                    if verbose:
                        print("\nERROR [E]: Arista opuesta no tiene coordenadas correspondientes")
                        e.print()
                        e.get_twin().print()
                    is_broken_e = True

            # Triangle check: Edge in associated triangle's edge list
            if e not in e.get_triangle().get_edges():
                if verbose:
                    print("\nERROR [E]: Arista no presente en lista de aristas de triángulo asociado")
                    e.print()
                    e.get_triangle().print()
                is_broken_e = True
            
            # Mesh triangle check: Check if associated triangle in mesh
            if e.get_triangle() not in self.get_triangles():
                if verbose:
                    print("\nERROR [E]: Triángulo asociado a arista no presente en la malla")
                    e.print()
                    e.get_triangle().print()
                is_broken_e = True
            
            if e.get_prev():
                # Prev check: Prev edge shares vertex with current edge
                if e.get_start() != e.get_prev().get_end():
                    if verbose:
                        print("\nERROR [E]: Arista previa no comparte vértice con arista actual")
                        e.print()
                        e.get_prev().print()
                    is_broken_e = True

                # Prev mesh check: Check if prev in mesh
                if e.get_prev() not in self.get_edges():
                    if verbose:
                        print("\nERROR [E]: Arista contiene vértice previo no presente en la malla")
                        e.print()
                        e.get_prev().print()
                    is_broken_e = True

            if e.get_next():
                # Next check: Next edge shares vertex with current edge
                if e.get_end() != e.get_next().get_start():
                    if verbose:
                        print("\nERROR [E]: Arista siguiente no comparte vértice con arista actual")
                        e.print()
                        e.get_next().print()
                    is_broken_e = True
                
                # Next mesh check: Check if prev in mesh
                if e.get_next() not in self.get_edges():
                    if verbose:
                        print("\nERROR [E]: Arista contiene vértice previo no presente en la malla")
                        e.print()
                        e.get_next().print()
                    is_broken_e = True
            
            if is_broken_e:
                broken_e += 1

        for v in self.vertices:

            is_broken_v = False

            for e in v.get_edges():

                # Edge check: Check if vertex is in start_v for each edge in list
                if e.get_start() != v:
                    if verbose:
                        print("\nERROR [V]: Vértice asociado a arista con distinto punto de inicio")
                        v.print()
                        e.print()
                    is_broken_v = True

                # Edge mesh check: Check if all adjacent edges are in mesh
                if e not in self.get_edges():
                    if verbose:
                        print("\nERROR [V]: Vértice contiene arista no presente en malla")
                        v.print()
                        e.print()
                    is_broken_v = True
        
            if is_broken_v:
                broken_v += 1

        print("")
        print("Broken triangles: " + str(broken_t))
        print("Broken edges: " + str(broken_e))
        print("Broken vertices: " + str(broken_v))
    
    #######################
    # AUXILIARY FUNCTIONS #
    #######################

    # Print all vertices as string
    def print_vertices(self):
        for v in self.get_vertices():
            v.print()

    # Print all edges as string
    def print_edges(self):
        for e in self.get_edges():
            e.print()

    # Print all triangles as string
    def print_triangles(self):
        for t in self.get_triangles():
            t.print()
    
    # Get error totals for vertices and triangles:
    def error_totals(self):
        v_err = 0
        for v in self.get_vertices():
            v_err += v.get_err()
        
        t_err = 0
        for t in self.get_triangles():
            t_err += t.get_err()

        return [v_err, t_err]
    
    # Get maximum and minimum errors for log
    def err_max_min(self):
        v_errs = [v.get_err() for v in self.get_vertices()]
        max_v = max(v_errs)
        min_v = min(v_errs)

        t_errs = [t.get_err() for t in self.get_triangles()]
        max_t = max(t_errs)
        min_t = min(t_errs)

        return [min_v, max_v, min_t, max_t]
    
    # Randomize vertex positions    
    def random_vertices(self,h_range,v_range):
        for v in self.vertices:
            rand_h = random.randint(-h_range,h_range)
            rand_v = random.randint(-v_range,v_range)
            v.move((rand_h,rand_v))


# Image class, always associated to mesh
class Image:

    # Image object
    def __init__(self, filename, bw_thresh):
        self.filename = filename # Filename as string

        color_img = cv2.imread(self.filename) # Color image
        color_copy = copy.deepcopy(color_img)

        grey_img = cv2.cvtColor(color_copy, cv2.COLOR_BGR2GRAY)
        thresh, bw_img = cv2.threshold(grey_img, bw_thresh, 255, cv2.THRESH_BINARY)
        inverted = cv2.bitwise_not(bw_img)

        contours, _ = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        all_points = []
        for contour in contours:
            all_points.extend(contour)

        rect = cv2.minAreaRect(np.array(all_points))

        # Get the coordinates of the bounding box
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        x_values = [point[0] for point in box]
        y_values = [point[1] for point in box]

        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)

        # Calculate the width and height
        w = max_x - min_x
        h = max_y - min_y

        # Calculate the x and y coordinates
        x = min_x
        y = min_y

        if y < 0:
            y = 0
        if x < 0:
            x = 0

        img_h, img_w = bw_img.shape

        if h+y > img_h:
            h = img_h
            y = 0 

        if w+x > img_w:
            w = img_w
            x = 0 

        cropped_bw = bw_img[y:y+h, x:x+w]
        cropped_color = color_img[y:y+h, x:x+w]

        padding_x = round(w*0.1)
        padding_y = round(h*0.1)
        canvas_dim = max(h + padding_x*2, w + padding_y*2)

        color_canvas = np.zeros((canvas_dim, canvas_dim, 3), dtype=np.uint8)
        color_canvas[:] = (255, 255, 255)
        bw_canvas = np.ones((canvas_dim, canvas_dim), dtype=np.uint8) * 255

        x_pos = (canvas_dim-w)//2
        y_pos = (canvas_dim-h)//2

        bw_canvas[y_pos:y_pos+h, x_pos:x_pos+w] = cropped_bw
        color_canvas[y_pos:y_pos+h, x_pos:x_pos+w] = cropped_color

        self.bw = bw_canvas # Two-tone image, never modified, always used as reference!
        self.color = color_canvas

        self.dims = self.bw.shape # Image dimensions

        self.mesh = None # Associated mesh

    ###############
    #   GETTERS   #
    ###############

    def get_mesh(self):
        return self.mesh
    
    ###############
    # INITIALIZER #
    ###############

    # Create a new triangle mesh and associate it with image
    def add_mesh(self, h_tri, v_tri, min_e_len, same=False):

        self.mesh = Mesh(self, min_e_len)

        x = self.dims[1]
        y = self.dims[0]

        self.mesh.make(x,y,h_tri,v_tri,same)

    #####################
    # WRAPPER FUNCTIONS #
    #####################

    def update_triangles(self):
        self.mesh.update_triangles()

    def update_vertices(self):
        self.mesh.update_vertices()

    def update_all(self):
        self.update_triangles()
        self.update_vertices()

    def move_vertices(self, step=1, verbose=None):
        self.mesh.move_vertices(step, verbose)

    def move_vertices_seq(self, step=1, verbose=None):
        self.mesh.move_vertices_seq(step, verbose)

    def edge_flip(self, verbose=False):
        return self.mesh.edge_flip(verbose)
    
    def edge_flip_g(self, verbose=False):
        return self.mesh.edge_flip_g(verbose)

    def edge_collapse(self, verbose=False):
        return self.mesh.edge_collapse(verbose)

    def insert_points(self, verbose=False):
        return self.mesh.insert_points(verbose)
    
    def insert_points_v(self, min_g, verbose=False):
        return self.mesh.insert_points_v(min_g, verbose)
    
    def border_update(self):
        self.mesh.border_update()
    
    def border_get(self):
        return self.mesh.border_get()
    
    def health_check(self, verbose=False):
        self.mesh.health_check(verbose)

    #####################
    # DRAWING FUNCTIONS #
    #####################

    # Draw triangles with approximation error
    def draw_triangles(self, img, color="avg"):
        if self.get_mesh():
            for t in self.get_mesh().triangles:
                for p in t.points:
                    if color == "avg":
                        c = t.get_avg()
                    else:
                        c = t.get_err()*2
                    cv2.line(img, p[0], p[1], [c,c,c], 1)
        
        return img
    
    # Draw mesh edges
    def draw_edges(self, img, same=False):
        if self.mesh:
            # Draw edges
            for e in self.mesh.get_edges():
                p1 = e.start_v.to_tuple()
                p2= e.end_v.to_tuple()
                if e.get_is_border():
                    if same:
                        cv2.line(img, p1, p2, (0,255,0), 1)
                    else:
                        cv2.line(img, p1, p2, (0,0,255), 2)
                else:
                    can_draw = True
                    if e.get_twin():
                        if e.get_twin().get_is_border():
                            can_draw = False
                    if can_draw:
                        cv2.line(img, p1, p2, (0,255,0), 1)
            
        return img

    # Draw mesh vertices
    def draw_vertices(self, img, v_err=True):
        if self.mesh:
            for v in self.mesh.get_vertices():

                col = (0,0,0)

                if v_err:
                    c = v.get_err()*6
                    if c > 255:
                        c = 255
                    col = (c,0,0)

                cv2.circle(img, (v.x_pos, v.y_pos), 3, col, -1)
        
        return img

    # Draw mesh
    def draw_full(self, img, mesh=True, triangles=False):
        new_img = None
        if img == "color":
            new_img = copy.deepcopy(self.color)
            triangles = False
        elif img == "bw":
            new_bw = copy.deepcopy(self.bw)
            new_img = np.stack((new_bw,)*3, axis=-1)
        else:
            return

        if triangles:
            self.draw_triangles(new_img)
        if mesh:
            self.draw_edges(new_img)
            self.draw_vertices(new_img)
        
        return new_img

    ###################
    #  IMAGE DISPLAY  #
    ###################
    
    # Show modified image
    def show(self):
        cv2.imshow("show",self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Show unmodified image
    def show_original(self):
        cv2.imshow("show",self.original)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    #################
    # LOG FUNCTIONS #
    #################

    def error_totals(self):
        return self.mesh.error_totals()
    
    def err_max_min(self):
        return self.mesh.err_max_min()
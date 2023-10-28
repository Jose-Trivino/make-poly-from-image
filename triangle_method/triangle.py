import numpy as np

# Triangle class
class Triangle:
    def __init__(self, mesh, edge_list):
        self.mesh = mesh        # Associated mesh
        self.edges = edge_list  # List of 3 edges that define triangle
        self.points = []        # List of points contained in triangle
        self.avg = None         # Average color of triangle
        self.err = None         # Approximation error
        self.new = True         # New triangle flag, True in 1st iteration

    ###############
    #   GETTERS   #
    ###############

    # Get associated mesh
    def get_mesh(self):
        return self.mesh
    
    # Get edge list
    def get_edges(self):
        return self.edges
    
    # Get edge at index i
    def get_edge(self, i):
        return self.edges[i]

    # Get list of points contained inside triangle
    def get_points(self):
        return self.points
    
    # Get approximation error inside triangle
    def get_err(self):
        return self.err
    
    # Get average color of triangle
    def get_avg(self):
        if self.get_new():
            self.update_err(True)
        return self.avg
    
    # Check if triangle was created in current iteration
    def get_new(self):
        return self.new

    ###############
    #   SETTERS   #
    ###############

    def set_points(self, points):
        self.points = points

    def set_not_new(self):
        self.new = False
    
    def set_err(self, app_error):
        self.err = app_error

    def set_avg(self, avg):
        self.avg = avg
    
    ###############
    #   REMOVER   #
    ###############

    # Removes triangles and edges, vertices remain
    def remove(self):
        for e in self.get_edges():
            e.remove()
        self.mesh.remove_triangle(self)
    
    ################
    #   UPDATERS   #
    ################
    
    # Updates list of points contained inside triangle        
    def update_points(self):
        
        def get_equations(v1, v2):
            if v1[0] != v2[0]:
                m = (v1[1]-v2[1])/(v1[0]-v2[0])
                b = v1[1] - m*v1[0]
            else:
                m = None
                b = None
            return (m,b)
        
        def solve_equations(y, m, b, vertex):
            if not m:
                return vertex[0]
            
            return (y-b)//m
 
        vertices = self.vertex_list_t()
        
        # Define the vertices of the triangle
        lines = []

        # Sort vertices by y coordinate:
        y_sort = sorted(vertices, key=lambda v: v[1])

        # Case 1: Upper points at same heights
        if y_sort[0][1] == y_sort[1][1]:
            lower = y_sort.pop(2)
            top = sorted(y_sort, key=lambda v: v[0])
            left = top[0]
            right = top[1]

            left_m, left_b = get_equations(left, lower)
            right_m, right_b = get_equations(right, lower)

            lines.append((left, right))

            for y in range(left[1]+1,lower[1]+1):
                x1 = solve_equations(y,left_m,left_b,left)
                x2 = solve_equations(y,right_m,right_b,right)

                start = min(x1,x2)
                stop = max(x1,x2)

                lines.append(((int(start),y),(int(stop),y)))
        
        # Case 2: Lower points at same heights
        elif y_sort[1][1] == y_sort[2][1]:
            upper = y_sort.pop(0)
            base = sorted(y_sort, key=lambda v: v[0])
            left = base[0]
            right = base[1]

            left_m, left_b = get_equations(left, upper)
            right_m, right_b = get_equations(right, upper)

            for y in range(upper[1],left[1]):
                x1 = solve_equations(y,left_m,left_b,left)
                x2 = solve_equations(y,right_m,right_b,right)

                start = min(x1,x2)
                stop = max(x1,x2)

                lines.append(((int(start),y),(int(stop),y)))

            lines.append((left, right))

        # Case 3: All points at different heights
        else:
            middle = y_sort[1]
            top = y_sort.pop(0)
            base = sorted(y_sort, key=lambda v: v[0])
            left = base[0]
            right = base[1]

            left_m, left_b = get_equations(left, top)
            right_m, right_b = get_equations(right, top)
            base_m, base_b = get_equations(right, left)

            for y in range(top[1],max([v[1] for v in vertices])+1):
                if y < middle[1]:
                    x1 = solve_equations(y,left_m,left_b,left)
                    x2 = solve_equations(y,right_m,right_b,right)
                else:
                    if middle == left:
                        x1 = solve_equations(y,base_m,base_b,left)
                        x2 = solve_equations(y,right_m,right_b,right)
                    else:
                        x1 = solve_equations(y,left_m,left_b,left)
                        x2 = solve_equations(y,base_m,base_b,right)

                start = min(x1,x2)
                stop = max(x1,x2)
                
                lines.append(((int(start),y),(int(stop),y)))

        self.set_points(lines)
        return self.get_points()


    # Update average color from points inside triangle
    def update_err(self, update_all=False):

        # If points not set, calculate
        if update_all or (len(self.points) <= 0):
            self.update_points()
        
        color_arr = []

        for line in self.get_points():

            color = self.mesh.image.bw[line[0][1] , line[0][0]:line[1][0]]

            # Fill color_arr
            if len(color_arr) > 1:
                color_arr = np.concatenate((color_arr,color))
            else:
                color_arr = color
                    
        l = len(color_arr)
        
        if l == 0:
            #print("WARNING: Empty points array")
            #self.print()
            self.shortest_edge().edge_collapse()
            #self.print()
            #self.set_err(0)
            #self.set_avg(0)
            #self.set_broken_vertices()

        # Approximation error is distance to 0 or 255
        else:
            avg = np.mean(color_arr)
            self.set_avg(avg)
            if avg > 127:
                self.set_err(255 - avg)
            else:
                self.set_err(avg)
        
        self.set_not_new()

        return self.get_err()
    
    ################
    #  REFINEMENT  #
    ################

    # Flip shared edge between two triangles
    def edge_flip(self, tri_2):

        if tri_2.get_new():
            #print("SKIP: New triangle sharing edge, skipping edge-flip")
            return False

        shared = self.shared_edge(tri_2)

        if not shared:
            #print("ERROR: Can't perform edge flip, triangles don't share an edge")
            return
        
        # a b       Change from [\] -> acd , adb
        # c d       to [/]          -> acb , bcd
        va = shared.get_s("e")
        vb = shared.get_s("one")
        vc = shared.get_s("ne")
        vd = shared.get_s("s")

        # Remove old triangles
        self.remove()
        shared.get_twin().get_triangle().remove()

        # Create new triangles
        t_1 = self.mesh.connect_3([va,vc,vb])
        t_2 = self.mesh.connect_3([vb,vc,vd])

        t_1.update_err(True)
        t_2.update_err(True)

        va.update_err()
        vb.update_err()
        vc.update_err()
        vd.update_err()

        return True
    
    # Check if edges generated by edge-flip exceed minimum edge length
    def test_edge_flip(self, tri_2):

        if tri_2.get_new():
            #print("SKIP: New triangle sharing edge, skipping edge-flip")
            return False
        
        shared = self.shared_edge(tri_2)

        if not shared:
            #print("ERROR: Can't perform edge flip, triangles don't share an edge")
            return
        
        err_1 = shared.get_triangle().get_err()
        err_2 = shared.get_s("ot").get_err()
        curr_err = err_1 + err_2

        # a b       Change from [\] -> acd , adb
        # c d       to [/]          -> acb , bcd
        va = shared.get_s("e").copy()
        vb = shared.get_s("one").copy()
        vc = shared.get_s("ne").copy()
        vd = shared.get_s("s").copy()

        # Create new triangles without adding to mesh
        new_t_1 = self.mesh.connect_3([va,vc,vb], False)
        new_t_2 = self.mesh.connect_3([vb,vc,vd], False)

        # Get approximation error from new triangles
        new_err_1 = new_t_1.update_err(True)
        new_err_2 = new_t_2.update_err(True)

        new_err = new_err_1 + new_err_2
        
        if new_err < curr_err:
            return self.edge_flip(tri_2)

        return False
    
    # Insert new vertex in centroid of triangle
    def insert_point(self):
        x,y = self.centroid()

        v1,v2,v3 = self.vertex_list()

        new_v = self.mesh.make_vertex(x,y)
        new_v.set_full_movement()

        self.remove()

        t_1 = self.mesh.connect_3([v1,v2,new_v])
        t_2 = self.mesh.connect_3([v2,v3,new_v])
        t_3 = self.mesh.connect_3([v3,v1,new_v])

        t_1.update_err(True)
        t_2.update_err(True)
        t_3.update_err(True)

        v1.update_err()
        v2.update_err()
        v3.update_err()
        new_v.update_err()

        return True
    
    # Check if edges generated by point insertion exceed minimum edge length
    def test_insert_point(self):
        x,y = self.centroid()

        c = self.mesh.make_vertex(x,y,False)

        vertices = [v.copy() for v in self.vertex_list()]

        edges = [self.mesh.make_edge(c,v,False) for v in vertices]

        min_edge = min(edges, key=lambda e: e.length())

        if min_edge.length() > self.get_mesh().get_min_e_len():
            return self.insert_point()

        else:
            return False
        
    # Point insertion in edge midpoint
    def insert_point_edge(self, e):
        return e.insert_point()
    
    # Point insertion in edge with length check
    def test_insert_point_edge(self, e):
        return e.test_insert_point()

    ######################
    # GEOMETRY FUNCTIONS #
    ######################

    # Get edge with the shortest length
    def shortest_edge(self):
        lengths = [e.get_length() for e in self.edges]
        min_len = min(lengths)
        i = lengths.index(min_len)
        return self.edges[i]

    # Get centroid of triangle
    def centroid(self):
        verts = self.vertex_list_t()
        x = (verts[0][0] + verts[1][0] + verts[2][0])//3
        y = (verts[0][1] + verts[1][1] + verts[2][1])//3

        return (x,y)
    
    # Check if triangles share edge
    def shared_edge(self, t):

        shared = None
        for e in self.get_edges():
            if e.get_twin() in t.get_edges():
                shared = e
        
        return shared

    #######################
    # AUXILIARY FUNCTIONS #
    #######################

    # Get vertices as list
    def vertex_list(self):
        return [e.get_start() for e in self.get_edges()]
    
    # Get vertices as list of tuples
    def vertex_list_t(self):
        return [v.to_tuple() for v in self.vertex_list()]
    
    # Get approximation error of individual vertices:
    def vertex_err(self):
        return [v.get_err() for v in self.vertex_list()]

    # Set all adjacent vertices as broken:
    def set_broken_vertices(self):
        for v in self.vertex_list():
            v.set_broken()
    
    # Get edge defined by vertices with highest approximation error
    def high_err_e(self):
        min_g = min(self.vertex_err())
        i = self.vertex_err().index(min_g)
        return self.get_edges()[(i+1)%3]

    # Get edge defined by vertices with lowest approximation error
    def low_err_e(self):
        max_g = max(self.vertex_err())
        i = self.vertex_err().index(max_g)
        return self.get_edges()[(i+1)%3]

    # Get longest edge
    def longest_edge(self):
        sort_edges = sorted(self.get_edges(), key=lambda e: e.length())
        return sort_edges[2]
    
    # Get longest edge
    def shortest_edge(self):
        sort_edges = sorted(self.get_edges(), key=lambda e: e.length())
        return sort_edges[0]

    # Get largest angle:
    def largest_angle(self):
        angles = [e.get_opp_angle() for e in self.get_edges()]
        return max(angles)

    # Get smallest angle:
    def smallest_angle(self):
        angles = [e.get_opp_angle() for e in self.get_edges()]
        return min(angles)
    
    # Get area of bounding box
    def bounding_box_area(self):
        verts = self.vertex_list_t()

        v_x = [v[0] for v in verts]
        v_y = [v[1] for v in verts]

        width = max(v_x) - min(v_x)
        height = max(v_y) - min(v_y)

        return width*height

    # Get vertices as string
    def to_string(self):
        v = self.vertex_list_t()
        return "[" + str(v[0]) + " ; " + str(v[1]) + " ; " + str(v[2]) + "]"
    
    # Print function
    def print(self):
        print(self.to_string())


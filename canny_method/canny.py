import cv2
import numpy as np
import math
import copy

# Path class, associated with graph, stores edge list
class Path:

    def __init__(self, graph):
        self.graph = graph
        self.edges = []
        self.containers = 0
        self.clockwise = True 
        self.hole_point = None

    ###############
    #   GETTERS   #
    ###############

    def get_edges(self):
        return self.edges

    def get_first(self):
        return self.edges[0]
    
    def get_last(self):
        return self.edges[-1]
    
    def get_i(self, i):
        return self.edges[i]
    
    def get_edges_len(self):
        return len(self.edges)
    
    def get_bounding_box(self):
        return self.bounding_box
    
    def get_containers(self):
        return self.containers
    
    def get_hole_point(self):
        return self.hole_point
    
    ###############
    #   SETTERS   #
    ###############
    
    # Add edge at final position in edge list
    def add(self, edge):
        self.edges.append(edge)

    # Add edge at initial position in edge list
    def add_first(self, edge):
        self.edges.insert(0, edge)
    
    # Delete edge at index i
    def delete(self, i):
        return self.edges.pop(i)
    
    # Concatenate two edge lists
    def append(self, path):
        self.edges += path.get_edges()
    
    def add_container(self):
        self.containers += 1
    
    ################
    #   GEOMETRY   #
    ################

    # Get highest point in path
    def highest_point(self):
        return min(self.get_edges(), key=lambda e: e[0][1])

    # Get orientation of path. If < 0, counterclockwise, else clockwise
    def orientation(self):

        def get_cross(p1,p2,q1,q2):
            a_0 = [p2[0]-p1[0],p2[1]-p1[1]]
            b_0 = [q2[0]-q1[0],q2[1]-q1[1]]

            return np.cross(a_0,b_0)
        
        edge_1 = self.highest_point()

        i = self.get_edges().index(edge_1)
        edge_2 = self.get_i(i-1)

        cross = get_cross(edge_1[0], edge_1[1], edge_2[1], edge_2[0])

        if cross == 0:
            x1 = edge_1[1][0]
            x2 = edge_2[0][0]
            if x1 < x2:
                return -1
            else:
                return 1
        else:
            return -cross//abs(cross)
    
    # Swap orientation of path
    def change_orientation(self):

        new_edges = []

        for e in self.get_edges():
            new_edges.insert(0, [e[1],e[0]])

        self.edges = new_edges

    # Check containing polygons
    def container_check(self, path):

        def get_intersection(v1, v2, y):
            if v1[0] != v2[0]:
                m = (v1[1]-v2[1])/(v1[0]-v2[0])
                b = v1[1] - m*v1[0]
                return (y-b)//m
            else:
                return v1[0]

        def point_in_polygon(point, path):
            y = point[1]

            count = 0

            for e in path.get_edges():
                upper, lower = sorted(e, key=lambda v: v[1])
                if upper[1] <= y and lower[1] > y:
                    inters = get_intersection(e[0],e[1],y)
                    if inters > point[0]:
                        count += 1

            # If odd, point is in polygon
            return count%2==1

        first_point = self.get_edges()[0][0]
        if point_in_polygon(first_point, path):
            self.add_container()
    
    # If number of containers is odd, set hole to true
    def update_hole_point(self):

        def get_cross(p1,p2,q1,q2):
            a_0 = [p2[0]-p1[0],p2[1]-p1[1]]
            b_0 = [q2[0]-q1[0],q2[1]-q1[1]]

            return np.cross(a_0,b_0)

        def get_angle(p1,p2,q1,q2):
            v1 = [(p2[0]-p1[0]),(p2[1]-p1[1])]
            v2 = [(q2[0]-q1[0]),(q2[1]-q1[1])]

            dot = v1[0]*v2[0] + v1[1]*v2[1]

            mv1 = math.sqrt(v1[0]**2+v1[1]**2)
            mv2 = math.sqrt(v2[0]**2+v2[1]**2)

            a = dot/(mv1*mv2)
            if a > 1:
                a = 1
            if a < -1:
                a = -1

            cross = get_cross(p1,p2,q1,q2)
            
            angle = int(math.degrees(math.acos(a)))

            if cross < 0:
                return 360 - angle
            else:
                return angle 
            
        def length(p1, p2):
            return math.sqrt(((p2[0]-p1[0])**2)+((p2[1]-p1[1])**2))
        
        def centroid(p1, p2, p3):
            x = (p1[0] + p2[0] + p3[0])//3
            y = (p1[1] + p2[1] + p3[1])//3

            return (x,y)
        
        clockwise = self.orientation() > 0

        if self.get_containers()%2 == 1:

            # Hole paths always clockwise
            if not clockwise:
                self.change_orientation()

            min_a_w = 21
            min_i = 0

            for i in range(len(self.get_edges())):
                a2, a1 = self.get_i(i)
                b1, b2 = self.get_i((i+1)%len(self.get_edges()))

                angle = get_angle(a1,a2,b1,b2)

                if angle > 180:
                    continue

                len1 = length(a1,a2)
                len2 = length(b1,b2)

                len_diff = min(len1,len2)/max(len1,len2)

                # Distance to 60, greater is worse
                # Range from 0 to 10, 0 is best
                angle_weight = abs(angle-60)
                if angle_weight > 120:
                    angle_weight = 120
                angle_weight = angle_weight/6

                # Distance to 1, greater is worse
                # Range from 0 to 10, 0 is best
                len_weight = 0.5-len_diff
                if len_weight < 0:
                    len_weight = 0
                len_weight = len_weight*20

                cond1 = angle <= 90
                cond2 = len_diff > 0.5

                if angle_weight + len_weight < min_a_w:
                    min_a_w = angle_weight + len_weight
                    min_i = i

                if cond1 and cond2:
                    break

            a, v = self.get_i(min_i)
            _, b = self.get_i((min_i+1)%len(self.get_edges()))

            if self.get_edges()[0][0] == self.get_edges()[-1][1]:
                self.hole_point = centroid(a,v,b)
                
        else:
            # Border paths always counterclockwise
            if clockwise:
                self.change_orientation()
            self.hole_point = None
        return self.hole_point
    
    ###############
    #  REDUCTION  #
    ###############

    # Constant length edge reduction method
    def edge_reduce_constant(self, reduction_limit):

        # If reduction_limit is 0, return original array
        if reduction_limit == 0:
            return self.get_edges()

        limit = reduction_limit # Counter for reductions
        start_e = 0

        # Go through every edge in path
        while True:

            self.get_i(start_e)[1] = self.delete(start_e+1)[1]
            limit -= 1

            if limit <= 0:
                start_e += 1
                limit = reduction_limit
            
            if start_e >= self.get_edges_len()-1:
                break
        
        return self.get_edges()
    
    # Variable length edge reduction method
    def edge_reduce_variable(self, max_dist):

        #Auxiliary function
        def line_point_dist(p1,p2,p):
            x1, y1 = p1
            x2, y2 = p2
            x0, y0 = p

            if (x1, y1) == (x2, y2):
                return math.sqrt((x0 - x1)**2 + (y0 - y1)**2)

            return abs((x2-x1)*(y1-y0) - (x1-x0)*(y2-y1))/math.sqrt(((x2-x1)**2)+((y2-y1)**2))
        
        start_e = 0
        # Array of eliminated points for future comparison
        near_points = [self.get_i(start_e)[1]]

        # Go through every edge in path
        while True:

            if start_e+1 >= self.get_edges_len():
                break

            # New edge to be generated
            new_e = (self.get_i(start_e)[0],self.get_i(start_e+1)[1])
            valid = True

            # Check distance to all previous points
            for p in near_points:
                dist = line_point_dist(new_e[0],new_e[1],p)
                if dist > max_dist:
                    valid = False
        
            # If new vector fulfills the conditions, reduce vector
            if valid:
                new_point = self.delete(start_e+1)
                near_points.append(new_point[1])
                self.get_i(start_e)[1] = new_point[1]

            if start_e >= self.get_edges_len()-1:
                break

            # Else advance to next point
            if not valid:
                start_e += 1
                near_points = [self.get_i(start_e)[1]]

        return self.get_edges()
    
    # Hybrid edge reduction method
    def edge_reduce_threshold(self, reduction_limit, max_dist):

        #Auxiliary function
        def line_point_dist(p1,p2,p):
            x1, y1 = p1
            x2, y2 = p2
            x0, y0 = p

            if (x1, y1) == (x2, y2):
                return math.sqrt((x0 - x1)**2 + (y0 - y1)**2)

            return abs((x2-x1)*(y1-y0) - (x1-x0)*(y2-y1))/math.sqrt(((x2-x1)**2)+((y2-y1)**2))
        
        # If reduction_limit is 0, return original array
        if reduction_limit == 0:
            return self.get_paths()

        limit = reduction_limit # Counter for reductions

        start_e = 0
        # Array of eliminated points for future comparison
        near_points = [self.get_i(start_e)[1]]

        # Go through every edge in path
        while True:

            if start_e+1 >= self.get_edges_len():
                break

            # New edge to be generated
            new_e = (self.get_i(start_e)[0],self.get_i(start_e+1)[1])
            valid = True

            # Check distance to all previous points
            for p in near_points:
                dist = line_point_dist(new_e[0],new_e[1],p)
                if dist > max_dist:
                    valid = False
        
            # If new vector fulfills the conditions, reduce vector
            if valid:
                new_point = self.delete(start_e+1)
                near_points.append(new_point[1])
                self.get_i(start_e)[1] = new_point[1]
                limit -= 1

            if start_e >= self.get_edges_len()-1:
                break

            # Advance to next point
            if not valid or limit <= 0:
                start_e += 1
                near_points = [self.get_i(start_e)[1]]
                limit = reduction_limit
        
        return self.get_edges()
    
    ###################
    # POST-PROCESSING #
    ###################

    # Make loops in paths with similar start and end points
    def close_loops(self, max_dist):

        # Auxiliary function
        def dist_two_points(p1,p2):
            return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

        first_point = self.get_i(0)[0]
        last_point = self.get_i(-1)[1]

        dist = dist_two_points(first_point, last_point)

        if dist <= max_dist:
            new_point = (((first_point[0]+last_point[0])//2),((first_point[1]+last_point[1])//2))

            self.get_i(0)[0] = new_point
            self.get_i(-1)[1] = new_point
        
        return self.get_edges()
    
    # Fuse nearby points within same path
    def fuse_points(self, max_dist):

        # Auxiliary function
        def dist_two_points(p1,p2):
            return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

        i = 0

        while i < self.get_edges_len() and self.get_edges_len() >= 10:

            first_point = self.get_i(i)[0]
            last_point = self.get_i(i)[1]

            p_dist = dist_two_points(first_point,last_point)

            # If distance less than max, fuse points
            if p_dist <= max_dist:

                # If first or last edge, new point is endpoint
                if i == 0:
                    self.get_i(1)[0] = self.get_i(0)[0]
                    self.delete(0)

                elif i == self.get_edges_len()-1:
                    self.get_i(i-1)[1] = self.get_i(i)[1]
                    self.delete(i)
                
                else:
                    new_x = (first_point[0]+last_point[0])//2
                    new_y = (first_point[1]+last_point[1])//2
                    new_point = (new_x, new_y)

                    self.get_i(i-1)[1] = new_point
                    self.get_i(i+1)[0] = new_point
                    self.delete(i)
            
            else:
                i += 1

        return self.get_edges()



# Graph class, associated with image, stores generated paths
class Graph:

    def __init__(self, img):
        self.img = img
        self.paths = []

    ###############
    #   GETTERS   #
    ###############

    def get_img(self):
        return self.img
    
    def get_paths(self):
        return self.paths

    def get_original(self):
        return self.get_img().get_original()
    
    def get_canny(self):
        return self.get_img().get_canny()
    
    ##############
    #   MAKERS   #
    ##############

    # Generate paths from canny image 
    def make_edges(self):

        canny = self.get_canny()

        # Array with all generated edges
        edges = []

        # For every pixel in the array
        for i in range(len(canny)):
            for j in range(len(canny[0])):

                # If pixel is not black
                if canny[i][j] > 0:

                    # Check if adjacent pixels exist
                    right = j < len(canny[0])-1
                    down = i < len(canny)-1
                    left = j > 0

                    # Variables symbolizing adjacent pixels
                    r, br, b, bl, l = False, False, False, False, False

                    # If adjacent pixels exist, set to True if not black
                    if right:
                        r = canny[i][j+1] > 0
                    
                    if down:
                        b = canny[i+1][j] > 0

                        if left:
                            bl = canny[i+1][j-1] > 0

                        if right:
                            br = canny[i+1][j+1] > 0
                    
                    if left:
                        l = canny[i][j-1] > 0

                    # If right pixel is white, append vector to list
                    if r:
                        edges.append([(j,i),(j+1,i)])

                    # If bottom pixel is white, append vector to list
                    if b:
                        edges.append([(j,i),(j,i+1)])

                    # If bottom right pixel is white, append vector to list
                    # ONLY IF not connected with right and bottom pixels
                    if br:
                        if not b and not r:
                            edges.append([(j,i),(j+1,i+1)])
                    
                    # If bottom left pixel is white, append vector to list
                    # ONLY IF not connected with bottom and left pixels
                    if bl:
                        if not b and not l:
                            edges.append([(j,i),(j-1,i+1)])

        return edges
    
    # Generate a list of edge lists
    def make_paths(self):

        edge_list = self.make_edges()

        # Auxiliary function
        def get_angle(p1,p2,q1,q2):
            v1 = [(p2[0]-p1[0]),(p2[1]-p1[1])]
            v2 = [(q2[0]-q1[0]),(q2[1]-q1[1])]

            dot = v1[0]*v2[0] + v1[1]*v2[1]

            mv1 = math.sqrt(v1[0]**2+v1[1]**2)
            mv2 = math.sqrt(v2[0]**2+v2[1]**2)

            a = dot/(mv1*mv2)
            if a > 1:
                a = 1
            if a < -1:
                a = -1

            return int(math.degrees(math.acos(a)))
        
        # Initialize path array
        path_list = []

        curr_path = None
        search_start = True
        search_end = True

        while True:

            # If no more vectors remain in list, exit loop
            if len(edge_list) <= 0:
                if curr_path is not None:
                    path_list.append(curr_path)
                break

            # If starting a new path, append first vector of list
            if not curr_path:
                curr_path = Path(self)
                curr_path.add(edge_list.pop(0))
                search_start = True
                search_end = True

            # Arrays for candidate vectors
            found_start = []
            found_end = []

            # For every remaining element in vector list
            for i in range(len(edge_list)):

                if search_start:

                    # Get first edge from current path
                    first_edge = curr_path.get_first()

                    # Check for coincidence in endpoints
                    if first_edge[0] in edge_list[i]:

                        # If starting point is the same, flip obtained edge
                        if first_edge[0] == edge_list[i][0]:
                            edge_list[i][0], edge_list[i][1] = edge_list[i][1], edge_list[i][0]

                        found_start.append(edge_list[i]) # Append to first candidate list

                if search_end:

                    # Get last edge from current path
                    last_edge = curr_path.get_last()

                    # Check for coincidence in endpoints
                    if  last_edge[1] in edge_list[i]:

                        # If not already in candidate list
                        if edge_list[i] not in found_start:

                            # If ending point is the same, flip obtained edge
                            if last_edge[1] == edge_list[i][1]:
                                edge_list[i][0], edge_list[i][1] = edge_list[i][1], edge_list[i][0]

                            found_end.append(edge_list[i]) # Append to candidate list
            
            # If no candidate edges were found, start new path
            if len(found_start) == 0 and len(found_end) == 0:
                path_list.append(curr_path)
                curr_path = None

            # If edges were found at the start
            if len(found_start) > 0:

                best_match = 360
                best_i = -1

                # For every element in found_start
                for i in range(len(found_start)):

                    curr = curr_path.get_first()

                    # Current vector is combination of last 5 vectors
                    if curr_path.get_edges_len() >= 5:
                        curr = (curr_path.get_first()[0], curr_path.get_i(4)[1])
                    else:
                        l = curr_path.get_edges_len() - 1
                        curr = (curr_path.get_first()[0], curr_path.get_i(l)[1])

                    # Candidate vector
                    cand = found_start[i]

                    # Angle comparison
                    a = get_angle(curr[0],curr[1],cand[0],cand[1])

                    # Replace with best match
                    if a < best_match:
                        best_match = a
                        best_i = i

                # Remove best candidate from v_list and add to current path
                edge_list.remove(found_start[best_i])
                curr_path.add_first(found_start.pop(best_i))
            
            else:
                search_start = False

            # If vectors were found at the end
            if len(found_end) > 0:

                best_match = 360
                best_i = -1

                # For every element in found_end
                for i in range(len(found_end)):

                    # Current edge is combination of last 5 edges
                    if curr_path.get_edges_len() >= 5:
                        curr = (curr_path.get_i(-5)[0], curr_path.get_last()[1])
                    else:
                        l = curr_path.get_edges_len()
                        curr = (curr_path.get_i(-l)[0], curr_path.get_last()[1])

                    # Candidate vector
                    cand = found_end[i]

                    # Angle comparison
                    a = get_angle(curr[0],curr[1],cand[0],cand[1])

                    # Replace with best match
                    if a < best_match:
                        best_match = a
                        best_i = i
                
                # Remove best candidate from v_list and add to current path
                edge_list.remove(found_end[best_i])
                curr_path.add(found_end.pop(best_i))
            
            else:
                search_end = False

        # Paths with only one edge are removed
        i = 0
        while i < len(path_list):
            if path_list[i].get_edges_len() <= 1:
                path_list.pop(i)
            else:
                i += 1

        self.paths = path_list
        return self.paths
    
    ###############
    #  REDUCTION  #
    ###############
    
    # Applies constant length edge reduction method to all paths
    def edge_reduce_constant(self, reduction_limit):

        # If reduction_limit is 0, return original array
        if reduction_limit == 0:
            return self.get_paths()

        for path in self.get_paths():
            path.edge_reduce_constant(reduction_limit)
        
        return self.get_paths()
    
    # Applies variable length edge reduction method to all paths
    def edge_reduce_variable(self, max_dist):

        if max_dist < 1:
            return self.get_paths()

        for path in self.get_paths():
            path.edge_reduce_variable(max_dist)

        return self.get_paths()
    
    # Applies hybrid edge reduction method to all paths
    def edge_reduce_threshold(self, reduction_limit, max_dist):

        for path in self.get_paths():
            path.edge_reduce_threshold(reduction_limit, max_dist)

        return self.get_paths()
    
    ###################
    # POST-PROCESSING #
    ###################

    # Fuse paths with close endpoints
    def fuse_ends(self, max_dist):

        # Auxiliary function
        def dist_two_points(p1,p2):
            return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
        
        i = 0

        while i < len(self.get_paths()):

            j = i+1

            while j < len(self.get_paths()):

                curr_path = self.get_paths()[i]

                first_curr = curr_path.get_i(0)[0]
                last_curr = curr_path.get_i(-1)[1]

                comp_path = self.get_paths()[j]

                first_comp = comp_path.get_i(0)[0]
                last_comp = comp_path.get_i(-1)[1]

                c1 = dist_two_points(first_curr, last_comp) < max_dist
                c2 = dist_two_points(first_curr, first_comp) < max_dist
                c3 = dist_two_points(first_comp, last_curr) < max_dist
                c4 = dist_two_points(last_comp, last_curr) < max_dist

                if c1 or c2:

                    if c2:
                        comp_path.change_orientation()
                        new_point = (((first_curr[0]+first_comp[0])//2),((first_curr[1]+first_comp[1])//2))
                    else:
                        new_point = (((first_curr[0]+last_comp[0])//2),((first_curr[1]+last_comp[1])//2))

                    curr_path.get_i(0)[0] = new_point
                    comp_path.get_i(-1)[1] = new_point

                    new_prev = self.get_paths().pop(j)
                    old_path = self.get_paths()[i]

                    self.get_paths()[i] = new_prev
                    self.get_paths()[i].append(old_path)

                    j = i+1

                elif c3 or c4:

                    if c4:
                        comp_path.change_orientation()
                        new_point = (((last_comp[0]+last_curr[0])//2),((last_comp[1]+last_curr[1])//2))
                    else:
                        new_point = (((first_comp[0]+last_curr[0])//2),((first_comp[1]+last_curr[1])//2))

                    comp_path.get_i(0)[0] = new_point
                    curr_path.get_i(-1)[1] = new_point

                    new_next = self.get_paths().pop(j)

                    self.get_paths()[i].append(new_next)

                    j = i+1

                else:
                    j += 1
            
            i += 1

        return self.get_paths()
    
    # Make loops in paths with similar start and end points
    def close_loops(self, max_dist):

        for path in self.get_paths():
            path.close_loops(max_dist)

        return self.get_paths()
    
    # Keep only closed loops, remove other paths
    def keep_loops(self):

        i = 0

        while i < len(self.get_paths()):
            curr_path = self.get_paths()[i]

            first_point = curr_path.get_i(0)[0]
            last_point = curr_path.get_i(-1)[1]

            if first_point != last_point or len(curr_path.get_edges()) <= 2:
                self.get_paths().pop(i)
            else:
                i += 1
        
        return self.get_paths()
    
    # Nearby points within same path
    def fuse_points(self, max_dist):

        for path in self.get_paths():
            path.fuse_points(max_dist)

        return self.get_paths()
    
    # Remove small polygons
    def remove_small_polygons(self, max_dist):

        # Auxiliary function
        def dist_two_points(p1,p2):
            return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

        i = 0

        while i < len(self.get_paths()):
            curr_path = self.get_paths()[i]
            remove = False

            if curr_path.get_edges_len() <= 4:
                remove = True
                for edge in curr_path.get_edges():
                    edge_length = dist_two_points(edge[0],edge[1])
                    if edge_length > max_dist*2:
                        remove = False
                if remove:
                    self.get_paths().pop(i)
            
            if not remove:
                i += 1
        
        return self.get_paths()
    
    # Generate holes and hole points
    def final_processing(self):

        for i in range(len(self.get_paths())):
            for j in range(len(self.get_paths())):
                if i != j:
                    self.get_paths()[i].container_check(self.get_paths()[j])
        
        for path in self.get_paths():
            path.update_hole_point()

    #######################
    # AUXILIARY FUNCTIONS #
    #######################

    # Format paths for make_poly.py
    def format_paths(self):
        path_list = []
        for path in self.get_paths():
            new_path = []
            for i in range(path.get_edges_len()):
                new_path.append(path.get_i(i)[0])
            path_list.append((new_path,path.get_hole_point()))
        return path_list
    
    def print_edges(self):
        for p in self.get_paths():
            print(p.get_edges())

    def print_orientations(self):
        for p in self.get_paths():
            print(p.orientation())


# Image class, always associated to graph
class Image:

    # Image object
    def __init__(self, filename, t_lower, t_upper, bw_thresh):
        self.filename = filename

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

        self.original = color_canvas
        self.canny = cv2.Canny(bw_canvas, t_lower, t_upper)
        self.graph = None

    ###############
    #   GETTERS   #
    ###############

    def get_original(self):
        return self.original
    
    def get_bw(self):
        return self.bw

    def get_canny(self):
        return self.canny
    
    def get_graph(self):
        return self.graph
    
    ###############
    #   SETTERS   #
    ###############

    def set_graph(self, graph):
        self.graph = graph

    ################
    # INITIALIZERS #
    ################

    # Initialize graph object
    def make_edges(self):
        self.set_graph(Graph(self))
        self.get_graph().make_paths()

    #####################
    # WRAPPER FUNCTIONS #
    #####################

    # Choose edge reduction method
    def edge_reduce(self, type, params):
        match type[0]:
            case "f":
                self.get_graph().edge_reduce_constant(params[0])
            case "v":
                self.get_graph().edge_reduce_variable(params[0])
            case "h":
                self.get_graph().edge_reduce_threshold(params[0], params[1])
    
    def fuse_ends(self, max_dist):
        self.get_graph().fuse_ends(max_dist)

    def close_loops(self, max_dist):
        self.get_graph().close_loops(max_dist)

    def keep_loops(self):
        self.get_graph().keep_loops()

    def fuse_points(self, max_dist):
        self.get_graph().fuse_points(max_dist)

    def remove_small_polygons(self, max_dist):
        self.get_graph().remove_small_polygons(max_dist)

    def final_processing(self):
        self.get_graph().final_processing()

    def format_paths(self):
        return self.get_graph().format_paths()

    ###################
    #  IMAGE DISPLAY  #
    ###################

    # Draw mesh edges
    def draw_edges(self):

        def index_to_color(i):
            col = [100,100,100]
            if i == 5 or i <= 1:
                col[0] = 255
            if i >= 1 and i <= 3:
                col[1] = 255
            if i >= 3 and i <= 5:
                col[2] = 255
            return col 
        
        # Draw edges
        color_i = 0
        for path in self.get_graph().get_paths():
            line_color = index_to_color(color_i)
            for e in path.get_edges():
                p1 = e[0]
                p2 = e[1]
                cv2.line(self.get_original(), p1, p2, line_color, 2)
                cv2.circle(self.get_original(), p1, 1, (0,0,0), -1)
                cv2.circle(self.get_original(), p2, 1, (0,0,0), -1)

            if path.get_hole_point():
                cv2.circle(self.get_original(), path.get_hole_point(), 2, (0,0,255), -1)

            color_i = (color_i + 1)%6
            
    # Show original image
    def show_original(self):
        cv2.imshow("show",self.original)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Show original image
    def show_canny(self):
        cv2.imshow("show",self.canny)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
import math
import numpy as np

# Edge class
class Edge:
    def __init__(self, mesh, start_v, end_v):
        self.mesh = mesh        # Associated mesh
        self.start_v = start_v  # Start vertex
        self.end_v = end_v      # End vertex
        self.twin = None        # Opposite edge
        self.triangle = None    # Associated triangle
        self.prev = None        # Previous edge
        self.next = None        # Next edge
        self.is_border = False  # Border flag

    ###############
    #   GETTERS   #
    ###############

    def get_mesh(self):
        return self.mesh

    def get_start(self):
        return self.start_v
    
    def get_end(self):
        return self.end_v
    
    def get_start_t(self):
        return self.get_start().to_tuple()
    
    def get_end_t(self):
        return self.get_end().to_tuple()
    
    def get_twin(self):
        return self.twin

    def get_triangle(self):
        return self.triangle
    
    def get_prev(self):
        return self.prev
    
    def get_next(self):
        return self.next
    
    def get_is_border(self):
        return self.is_border
    
    def get_s(self, s):
        curr = self
        for i in range(len(s)):
            match s[i]:
                case "s":
                    curr = curr.get_start()
                case "e":
                    curr = curr.get_end()
                case "o":
                    curr = curr.get_twin()
                case "p":
                    curr = curr.get_prev()
                case "n":
                    curr = curr.get_next()
                case "t":
                    curr = curr.get_triangle()
            if curr == None:
                break
        
        return curr
    
    ###############
    #   SETTERS   #
    ###############

    def set_start(self, v):
        self.start_v = v
    
    def set_end(self, v):
        self.end_v = v

    def set_twin(self, e):
        self.twin = e
    
    def set_triangle(self, t):
        self.triangle = t
    
    def set_prev(self, e):
        if e:
            if not e.can_connect(self):
                print("WARNING: Aristas no comparten vértice")         
        self.prev = e

    def set_next(self, e):
        if e:
            if not self.can_connect(e):
                print("WARNING: Aristas no comparten vértice")
        self.next = e

    def set_prev_next(self, p, n):
        self.set_prev(p)
        self.set_next(n)

    def set_is_border(self, val):
        self.is_border = val

    # If adjacent triangle is white and twin is black, set as border
    def update_is_border(self):

        twn = self.get_twin()
        if twn:
            self_avg = self.get_triangle().get_avg()
            twn_avg = twn.get_triangle().get_avg()

            c1 = self_avg > 127
            c2 = twn_avg > 127

            if c2 and not c1:
                self.set_is_border(True)
            else:
                self.set_is_border(False)
    
    # Get complete path of border edges
    def get_loop(self):
        if not self.get_is_border():
            return []
        
        curr_e = self
        loop = [self]
        while True:
            next_border = curr_e.get_end().get_border()
            curr_e.set_is_border(False)
            if next_border:
                loop.append(next_border)
                curr_e = next_border
            else:
                break

        return loop

    ###############
    #   REMOVER   #
    ###############

    # Remove self from mesh and delete all references to object
    def remove(self):
        self.get_start().remove_edge(self)
        if self.get_prev():
            self.get_prev().set_next(None)
        if self.get_next():
            self.get_next().set_prev(None)
        if self.get_twin():
            self.get_twin().set_twin(None)
        self.mesh.remove_edge(self)

    ######################
    # GEOMETRY FUNCTIONS #
    ######################

    # True if two edges share a vertex at connection point
    def can_connect(self, next):
        return self.get_end() == next.get_start()

    # Connect 3 edges to make a triangle
    def connect(self, second, final):
        return self.mesh.make_triangle([self,second,final])
    
    # Get angle opposite to edge
    def get_opp_angle(self):

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
    
        v = self.get_s("ne").to_tuple()
        a = self.get_start().to_tuple()
        b = self.get_end().to_tuple()

        angle = get_angle(v,a,v,b)

        return angle
    
    # Get sum of angles opposite to self and opposite edge
    def get_opp_angle_sum(self):

        if self.get_twin():
            return self.get_opp_angle() + self.get_twin().get_opp_angle()

        return None
    
    def get_adj_angle(self):

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
        
        def get_cross(p1,p2,q1,q2):
            a_0 = [p2[0]-p1[0],p2[1]-p1[1]]
            b_0 = [q2[0]-q1[0],q2[1]-q1[1]]

            return np.cross(a_0,b_0)
        
        if not self.get_twin():
            return 0

        v = self.get_start().to_tuple()
        a = self.get_s("one").to_tuple()
        b = self.get_s("ps").to_tuple()

        angle = get_angle(v,a,v,b)
        cross = get_cross(b,v,v,a)

        if cross < 0:
            return angle
        else:
            return 360-angle

    # Get edge length
    def length(self):
        v1 = self.get_start_t()
        v2 = self.get_end_t()

        return math.sqrt(((v2[0]-v1[0])**2)+((v2[1]-v1[1])**2))
    
    # Get point between start and end point
    def get_midpoint(self):
        start_t = self.get_start_t()
        end_t = self.get_end_t()

        mid_x = (start_t[0] + end_t[0])//2
        mid_y = (start_t[1] + end_t[1])//2

        return (mid_x, mid_y)

    ################
    #  REFINEMENT  #
    ################
    
    # Remove edge and reassign connected edges
    def edge_collapse(self, retry=False):

        if not self.can_collapse():
            #print("SKIP: Border edge, skipping collapse")
            return 0
        
        del_v = self.get_start()
        end_v = self.get_end()

        prev_e = self.get_s("ono")
        if prev_e == None:
            return 0
        next_e = self.get_s("p")

        # If adjacent angles are too large, retry edge collapse in opposite direction
        # to avoid 
        if prev_e.get_adj_angle() > 175 or next_e.get_adj_angle() > 175:
            #print("SKIP: Angle too large, skipping collapse")
            if not retry:
                return self.get_twin().edge_collapse(True)
            else:
                return 0

        # Get neighboring vertices
        curr = self
        ring = []
        while True:
            if curr.get_triangle().get_new():
                #print("SKIP: New triangle in edge collapse")
                return 0
            curr = curr.get_s("po")
            if curr.get_end() != end_v:
                ring.append(curr.get_end())
            else:
                break

        # Removing edges, triangles and vertex
        removed_t = 0
        while len(del_v.get_edges()) > 0:
            del_v.get_edges()[0].get_triangle().remove()
            removed_t += 1

        del_v.remove()

        # Generating new triangles

        for i in range(len(ring)-1):
            new_tri = self.mesh.connect_3([ring[i],ring[i+1],end_v])
            new_tri.update_err(True)

        for v in ring:
            v.update_err()
        end_v.update_err()
        
        return removed_t    
    
    # Point insertion in edge midpoint
    def insert_point(self):

        if not self.get_twin():
            #print("SKIP: Edge has no opposite vector, can't insert vertex in midpoint")
            return False
        
        if self.get_twin().get_triangle().get_new():
            #print("SKIP: Uninitialized triangle, skipping point insertion in edge")
            return False
    
        # Creating new midpoint vertex
        x,y = self.get_midpoint()
        new_v = self.mesh.make_vertex(x,y)
        new_v.set_full_movement()

        # a b       Change from [\] -> acd , adb (self is "da")
        # c d       to [X]          -> acb , bcd
        va = self.get_s("e")
        vb = self.get_s("one")
        vc = self.get_s("ne")
        vd = self.get_s("s")

        self.get_twin().get_triangle().remove()
        self.get_triangle().remove()

        tri_1 = self.mesh.connect_3([va,vc,new_v])
        tri_2 = self.mesh.connect_3([vc,vd,new_v])
        tri_3 = self.mesh.connect_3([vd,vb,new_v])
        tri_4 = self.mesh.connect_3([vb,va,new_v])

        tri_1.update_err(True)
        tri_2.update_err(True)
        tri_3.update_err(True)
        tri_4.update_err(True)

        va.update_err()
        vb.update_err()
        vc.update_err()
        vd.update_err()
        new_v.update_err()

        return True
    
    # Check if edges generated by point insertion exceed minimum edge length
    def test_insert_point(self):

        x,y = self.get_midpoint()
        new_v = self.mesh.make_vertex(x,y,False)

        va = self.get_s("e").copy()
        vb = self.get_s("one").copy()
        vc = self.get_s("ne").copy()
        vd = self.get_s("s").copy()

        vertices = [va,vb,vc,vd]

        edges = [self.mesh.make_edge(new_v,v,False) for v in vertices]

        min_edge = min(edges, key=lambda e: e.length())

        if min_edge.length() > self.get_mesh().get_min_e_len():
            return self.insert_point()

        else:
            return False

    # Do edge flip in self and opposite triangle
    def edge_flip(self):
        if self.get_twin():
            return self.get_triangle().edge_flip(self.get_twin().get_triangle())
        return False
    
    # Check if edges generated by edge-flip exceed minimum edge length
    def test_edge_flip(self):
        if self.get_twin():
            return self.get_triangle().test_edge_flip(self.get_twin().get_triangle())
        return False

    #######################
    # AUXILIARY FUNCTIONS #
    #######################

    # Check if edge collapse is possible
    def can_collapse(self):

        # Collapse not possible for edges in image border
        if not self.get_twin():
            return False

        # Collapse not possible for edges near image border
        if 0 in self.get_start_t() or 0 in self.get_end_t():
            return False
        
        max_x = self.mesh.image.dims[0]-1
        max_y = self.mesh.image.dims[1]-1

        if max_x == self.get_start_t()[0] or max_x == self.get_end_t()[0]:
            return False
        
        if max_y == self.get_start_t()[1] or max_y == self.get_end_t()[1]:
            return False
    
        return True

    # String function
    def to_string(self):
        return "[" + self.get_start().to_string() + " ; " + self.get_end().to_string() + "]"
    
    # Print function
    def print(self):
        print(self.to_string())
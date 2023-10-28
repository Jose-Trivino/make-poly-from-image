# Vertex class
class Vertex:

    # Initialize vertex
    def __init__(self, mesh, x_pos, y_pos):
        self.mesh = mesh        # Associated mesh
        self.x_pos = x_pos      # x position
        self.y_pos = y_pos      # y position
        self.edges = []         # List of adjacent edges with self as start point
        self.err = None         # Sum of approximation error of adjacent triangles
        self.movement = []      # Allowed movement directions for x and y axes
        self.mov_dir = None     # Direction of next movement
        self.broken = False

    ###############
    #   GETTERS   #
    ###############

    # Get associated mesh
    def get_mesh(self):
        return self.mesh
    
    # Get leaving edge list
    def get_edges(self):
        return self.edges
    
    # Get color distance for all adjacent triangles
    def get_err(self):
        if self.err is None:
            return 0
        return self.err
    
    # Get movement array
    def get_movement(self):
        return self.movement
    
    # Get next movement direction
    def get_mov_dir(self):
        return self.mov_dir
    
    # Check if vertex is broken
    def get_broken(self):
        return self.broken

    ###############
    #   SETTERS   #
    ###############

    def set_err(self, app_err):
        self.err = app_err

    def set_mov_dir(self, dir):
        self.mov_dir = dir

    # Adds movement directions to movement list
    def add_movement(self, dirs):
        self.movement += dirs

    # Adds new edge to edge list
    def add_edge(self, edge):
        self.edges.append(edge)

    # Removes edge from edge list
    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print("ERROR: Can't remove edge not in vertex edge list")
            return
    
    # Set vertex as broken
    def set_broken(self):
        self.broken = True

    # Allow movement in all directions
    def set_full_movement(self):
        self.movement = [(1,0),(-1,0),(0,1),(0,-1)]
            
    ################
    #   UPDATERS   #
    ################
    
    # Update approximation error by getting error from all adjacent triangles
    # If update is set to false, calculate the error without changing
    # the value of the field
    def update_err(self, update=True):

        tri_list = self.adjacent_triangles()

        
        #if len(tri_list) <= 0:
        #    print("ERROR: Vertex has no adjacent triangles")

        v_err = 0
        for t in tri_list:
            v_err += t.get_err()//3
        if update:
            self.set_err(v_err)
        return v_err
    
    # Get next movement direction
    def update_mov_dir(self):

        # If movement not allowed, end
        if len(self.get_movement()) == 0:
            self.set_mov_dir((0,0))
            return
        
        # If all surrounding triangles have approximation error 0, end
        if self.get_err() == 0:
            self.set_mov_dir((0,0))
            return
    
        # Get new error for each direction
        tri_list = self.adjacent_triangles()
        test_err = []

        # Try diagonal movement for vertices with high error
        new_mov = self.get_movement() + [(1,1),(1,-1),(-1,1),(-1,-1)]

        if self.get_err() > 50 and len(self.get_movement()) >= 4:
            for dir in range(len(new_mov)):
                test_err.append(self.test_mov_dir(new_mov[dir],tri_list))
        else:
            for dir in range(len(self.get_movement())):
                test_err.append(self.test_mov_dir(self.get_movement()[dir],tri_list))

        # Get minimum calculated approximation error
        min_g = min(test_err, key=lambda g: g[0])

        # If test error is less than current error, 
        # set movement direction to new direction
        if min_g[0] < self.get_err():
            self.set_mov_dir(min_g[1])
        else:
            self.set_mov_dir((0,0))

        # If erorr still high and no set movement, force movement
        if self.get_mov_dir() == (0,0) and self.get_err() > 25:
            self.set_mov_dir(max(test_err, key=lambda g: g[0])[1])
    
    # Candidate new position 
    # mov: movement direction as tuple (x,y)
    # tri_list: adjacent triangle list
    def test_mov_dir(self, mov, tri_list):

        self.move(mov)

        for t in tri_list:
            # Recalculate points, color and approximation error according to new points
            t.update_err(True)

        # Get approximation error without updating field
        err = self.update_err(False)

        # Undo movement
        self.move((-mov[0],-mov[1]))

        return (err, mov)
    
    ###############
    #   REMOVER   #
    ###############

    def remove(self):
        self.mesh.remove_vertex(self)

    ######################
    # GEOMETRY FUNCTIONS #
    ######################

    # Move vertex in a direction
    def move(self,mov):
        self.x_pos += mov[0]
        self.y_pos += mov[1]

    # Get list of adjacent triangles
    def adjacent_triangles(self):
        tri_list = []
        for e in self.edges:
            tri_list.append(e.get_triangle())
        return tri_list
    
    # Connect vertex to another existent vertex
    def connect(self, new_v):
        # New edge, with self as start point, other vertex as end point
        # Automatically gets added to mesh
        return self.mesh.make_edge(self, new_v)
    
    # Check if edge exists with new_v as end_point
    def check_opposite(self, new_v):
        for e in self.edges:
            if e.get_end() == new_v:
                return e
        return None
    
    # Get vertices in 1-ring
    def get_ring(self):
        ring = []
        for e in self.edges:
            ring.append(e.get_end())
        return ring

    #######################
    # AUXILIARY FUNCTIONS #
    #######################

    # Convert position to tuple
    def to_tuple(self):
        return (self.x_pos, self.y_pos)
    
    # Copies vertex for test purposes
    def copy(self):
        return Vertex(self.mesh, self.x_pos, self.y_pos)

    # Get longest adjacent edge
    def longest_edge(self):
        return max(self.get_edges(), key=lambda e: e.length())
    
    # Get triangle with highest approximation error
    def highest_err_t(self):
        return max(self.adjacent_triangles(), key=lambda t: t.get_err())
    
    # Get largest adjacent triangle
    def largest_t(self):
        return max(self.adjacent_triangles(), key=lambda t: t.bounding_box_area())
    
    # Get first associated border edge
    def get_border(self):
        borders = [e for e in self.get_edges() if e.get_is_border()]
        if len(borders) >= 1:
            return borders[0]
        else:
            return None
    
    # String function
    def to_string(self):
        return str(self.to_tuple())
    
    # Print function
    def print(self):
        print(self.to_string())
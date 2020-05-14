class PrintPoint: 
    def __init__(self, pt, parent_path): 
        self.pt = pt # position of center of mass (compas.geometry.Point)
        self.parent_path = parent_path #class iheriting from PrintPath

        # printpoint details
        self.up_vector = None # compas.geometry.Vector
        self.closest_mesh_normal = None # compas.geometry.Vector
        self.plane = None

        self.layer_height = None
        self.layer_width = None 

        self.support_printpoint = None #class PrintPoint
        self.support_path = None  #class iheriting from PrintPath

        self.visualization_shape = None
        

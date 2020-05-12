class PrintPoint: 
    def __init__(self, pt, parent_path): 
        self.pt = pt # position of center of mass (compas.geometry.Point)
        self.parent_path = parent_path #class iheriting from PrintPath

        # fragment details
        self.up_vector = None
        self.closest_mesh_normal = None 
        self.plane = None

        self.layer_height = None
        self.layer_width = None 

        self.support_fragment = None #class Fragment
        self.support_path = None  #class iheriting from PrintPath

        self.visualization_shape = None
        

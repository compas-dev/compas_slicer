class PrintPoint: 
    def __init__(self, pt, layer_height, up_vector): 
        self.pt = pt # position of center of mass (compas.geometry.Point)
        self.layer_height = layer_height
        self.up_vector = up_vector # compas.geometry.Vector

        self.parent_path = None #class iheriting from PrintPath. The path in which this point belongs
        

        ### ----- parameters currently not yet filled in
        self.plane = None
        self.visualization_shape = None
        # parameters useful for curved slicing
        self.closest_shape_normal = None # compas.geometry.Vector
        self.support_printpoint = None #class PrintPoint
        self.support_path = None  #class iheriting from PrintPath

    def generate_plane(self):
        pass
        #TODO

    def generate_visualization_shape(self):
        pass
        #TODO
        
        

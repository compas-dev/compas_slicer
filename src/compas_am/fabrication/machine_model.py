import logging
logger = logging.getLogger('logger')

from compas.geometry import Box

class MachineModel(object):
    """
    Class for representing various fabrication machines (3D printers, robots etc.)
    """

    def get_machine_dimensions(self):
        return self.dimensions["x_bounds"], self.dimensions["y_bounds"], self.dimensions["z_bounds"]

    def get_machine_bounding_box(self):
        bbox = Box.from_corner_corner_height((0,0,0), (self.dimensions["x_bounds"], self.dimensions["y_bounds"], 0), self.dimensions["z_bounds"])
        return bbox

    def printout_info(self):
        print ("\n---- Machine Model Info ----")
        print ("Id : ", self.id)
        print ("Dimensions : ")
        print (self.dimensions)
        print ("Print parameters: ")
        print (self.print_parameters) 
        print ("")    


##############################
#### 3D printing
##############################

class Printer(MachineModel):
    """
    Class for representing 3D printers
    """
    def __init__(self, id):
        self.id = id

        ## print parameters
        self.dimensions = {}
        self.print_parameters = {}


        if self.id == "FDM_Prusa_i3_mk2":

            self.dimensions = {
                "x_bounds" : 250,
                "y_bounds" : 210,
                "z_bounds" : 200
            }

            self.print_parameters = {
                "extruder_temperature" : 210,   # Extrusion temperature (degr C)
                "bed_temperature"      : 60,    # Heated bed temperature (degr C)
                "print_speed"          : 50     # Movement speed (mm/s)
            }

        ### add here more 3d printer models

        else: 
            logger.warning("Unknown printer id : " + id + "! . Machine peramters remain empty.")



##############################
#### Robotic printing
##############################

class RobotPrinter(MachineModel):
    """
    Class for representing Robotic printers
    """
    def __init__(self, id):
        self.id = id

        ## print parameters
        self.dimensions = {}
        self.print_parameters = {}




if __name__ == "__main__":
    pass
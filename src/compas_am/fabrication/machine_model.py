import logging
logger = logging.getLogger('logger')

from compas.geometry import Box

class MachineModel(object):
    # class for representing various fabrication machines (3D printers, robots etc.)
    def __init__(self, printer_model):
        self.printer_model = printer_model

    def get_machine_data(self):
        if self.printer_model == "FDM_Prusa_i3_mk2":
            max_x, max_y, max_z = FDM_Prusa_i3_mk2.machine_data()
        return max_x, max_y, max_z

    def get_printer_bounding_box(self):
        max_x, max_y, max_z = get_machine_data(self.printer_model)
        bbox = Box.from_corner_corner_height((0,0,0), (max_x, max_y, 0), max_z)
        return bbox

class UR5Model(MachineModel):
    pass

class FDM_Prusa_i3_mk2(MachineModel):
    def machine_data():
        max_x = 250
        max_y = 210
        max_z = 200
        return max_x, max_y, max_z

if __name__ == "__main__":
    pass
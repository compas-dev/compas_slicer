import logging

logger = logging.getLogger('logger')

__all__ = ['Material']


class Material(object):
    def __init__(self, id):
        self.id = id
        self.parameters = self.get_parameters()

    def get_parameters(self):
        if self.id == "PLA":
            parameters = {
                "extruder_temperature": 210,  # Extrusion temperature (degr C)
                "bed_temperature": 60,  # Heated bed temperature (degr C)
                "print_speed": 50,  # Movement speed (mm/s)
                "z_hop": 0  # (mm)
            }
        elif self.id == "ABS":
            parameters = {
                "extruder_temperature": 230,  # Extrusion temperature (degr C)
                "bed_temperature": 100,  # Heated bed temperature (degr C)
                "print_speed": 50,  # Movement speed (mm/s)
                "z_hop": 0  # (mm)
            }
        else:
            logger.warning("Unknown material : " + self.id)
            parameters = {}

        return parameters

    def set_parameter(self, name, value):
        self.parameters[name] = value

    def load_parameters_from_json(self):
        pass  # TODO!

    def save_parameters_to_json(self):
        pass  # TODO!

    def printout_info(self):
        print("\n---- Material Info ----")
        print("ID : ", self.id)
        print("Parameters : ")
        print(self.parameters)
        print("")

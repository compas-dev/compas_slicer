import math

# TODO: These parameters should NOT be hardcoded! Instead they should be passed as a dictionary of parameters.
motor_omega = 2 * math.pi  # 1 revolution / sec = 2*pi rad/sec
motor_r = 4.0  # 4.25 #mm
motor_linear_speed = motor_omega * motor_r
D_filament = 2.75  # mm
filament_area = math.pi * (D_filament / 2.0) ** 2  # pi*r^2
multiplier = 0.25  # arbitrary value! You might have to change this


def calculate_linear_velocity_based_on_layer_height(printpoint):
    """
    Calculates the linear velocity during the print of a printpoint, so that the volume of extrusion matches the
    volume of the desired path cross-section
    path_area * robot_linear_speed = filament_area * motor_linear_speed

    Parameters
    ----------
    printpoint: :class: 'compas_slicer.geometry.PrintPoint'
    """
    layer_width = max(printpoint.layer_height, 0.4)
    path_area = layer_width * printpoint.layer_height
    linear_speed = (filament_area * motor_linear_speed) / path_area
    return linear_speed * multiplier

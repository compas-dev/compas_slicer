import logging
import math
import progressbar

from compas.geometry import Vector, angle_vectors

from compas_slicer.utilities import get_closest_mesh_normal_to_pt

logger = logging.getLogger('logger')

__all__ = ['set_linear_velocity']


def set_linear_velocity(print_organizer,
                        velocity_type,
                        v=25,
                        per_layer_velocities=None,
                        angle_range=(None, None),
                        speed_range=(None, None)):
    """ Sets the linear velocity parameter of the printpoints depending on the selected type.

    Parameters
    ----------
    print_organizer: :class:`compas.print_organization.PrintOrganizer`
    v: float
        Velocity value (in mm/s) to set for printpoints. Defaults to 25 mm/s.
    velocity_type: str
        Determines how to add linear velocity to the printpoints.

        constant:              one value used for all printpoints
        per_layer:             different values used for every layer
        by_layer_height:       set velocity in accordance to layer height
        by_overhang:           set velocity in accordance to the overhang
    per_layer_velocities: list of floats
        If setting velocity per layer, provide a list of floats with equal length to the number of layers.
    angle_range: tuple
        Two angles (in degrees) that give the minimum and maximum value to map the speed_range to.
        For example, (10, 50) will assign the maximum speed to overhang angles of 10 degrees
        or less, and the minimum speed to points with an overhang angle of 50 degrees and above.
    speed_range: tuple
        xxx
    """
    logger.info("Setting linear velocity with type : " + str(velocity_type))

    if not (velocity_type == "constant"
            or velocity_type == "per_layer"
            or velocity_type == "by_layer_height"
            or velocity_type == "by_overhang"):
        raise ValueError("Velocity method doesn't exist")

    pp_dict = print_organizer.printpoints_dict
    count = 0

    with progressbar.ProgressBar(max_value=print_organizer.total_number_of_points) as bar:
        for i, layer_key in enumerate(pp_dict):
            for path_key in pp_dict[layer_key]:
                path_printpoints = pp_dict[layer_key][path_key]
                for printpoint in path_printpoints:

                    if velocity_type == "constant":
                        printpoint.velocity = v

                    elif velocity_type == "per_layer":
                        assert per_layer_velocities, "You need to provide one velocity value per layer"
                        assert len(per_layer_velocities) == pp_dict, \
                            'Wrong number of velocity values. You need to provide one velocity value per layer, ' \
                            'on the "per_layer_velocities" list.'
                        printpoint.velocity = per_layer_velocities[i]

                    elif velocity_type == "by_layer_height":
                        printpoint.velocity = calculate_linear_velocity(printpoint)

                    elif velocity_type == "by_overhang":
                        mesh = print_organizer.slicer.mesh
                        # get mesh normal and calculate overhang angle
                        mesh_normal = get_closest_mesh_normal_to_pt(mesh, printpoint.pt)
                        vect_angle = angle_vectors(mesh_normal, Vector(0.0, 0.0, 1.0), deg=True)
                        overhang_angle = abs(90-vect_angle)

                        # remap values
                        min_speed, max_speed = speed_range
                        min_angle, max_angle = angle_range
                        oldrange = max_angle - min_angle
                        newrange = max_speed - min_speed

                        if overhang_angle <= min_angle:
                            print(overhang_angle, " is less than 10")
                            printpoint.velocity = max_speed
                        elif min_angle < overhang_angle <= max_angle:
                            print(overhang_angle, "is in between 10-40")
                            velocity = (((overhang_angle - min_angle) * newrange) / oldrange) + min_speed
                            printpoint.velocity = newrange - (velocity - newrange)
                            print(overhang_angle, velocity, printpoint.velocity)
                        elif overhang_angle > max_angle:
                            print(overhang_angle, " is more than 40")
                            printpoint.velocity = min_speed

                        bar.update(count)
                        count += 1


#############################
#  Nozzle linear velocity

motor_omega = 2 * math.pi  # 1 revolution / sec = 2*pi rad/sec
motor_r = 4.0  # 4.25 #mm
motor_linear_speed = motor_omega * motor_r
D_filament = 2.75  # mm
filament_area = math.pi * (D_filament / 2.0) ** 2  # pi*r^2

multiplier = 0.25  # arbitrary value! You might have to change this


def calculate_linear_velocity(printpoint):  # path_area * robot_linear_speed = filament_area * motor_linear_speed
    layer_width = max(printpoint.layer_height, 0.4)
    path_area = layer_width * printpoint.layer_height
    linear_speed = (filament_area * motor_linear_speed) / path_area
    return linear_speed * multiplier


if __name__ == "__main__":
    pass

import compas
import logging
import progressbar

from compas.geometry import Point, Polyline

from compas_slicer.utilities.utils import find_polyline_closest_parameter
from compas_slicer.geometry import Layer, Path
from compas_slicer.post_processing.contour_offsets_layer import contour_offsets_layer

logger = logging.getLogger('logger')

__all__ = ['infill_fermat_spiral']

# TODO add simple spiral function

def fermat_spiral(slicer, layer_width, seam_parameter, max_offsets=20, reverse=False):
    """
    Returns a fermat spiral path from an ordered list of paths

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.PlanarSlicer`
        An instance of the compas_slicer.slicers.PlanarSlicer class
    seam_parameter: float
        A number specifing the outer seam of the fermat spiral as
        normalized curve parameter on the first contour offset of the bottom layer
    layer_wwidth: float
        A number specifying the contour offset distances that create the fermat spiral
    max_offsets: int
        A number specifying the maximum amount of contour offsets that serve as paths for the fermat spiral
    reverse: boolean
        A boolean operator specifying if the fermat spiral starts inside or outside

    Returns
    -------
    None
    """

    logger.info(
        "Generating a{rv}fermat spiral with layer width: {lw} mm, starting at seam parameter {sp}".format(rv=(' reverse ' if reverse else ' '), lw=layer_width, sp=seam_parameter))


    for i, layer in enumerate(slicer.layers):
        slicer.layers[i] = contour_offsets_layer(layer, layer_width, max_offsets=max_offsets)

    pl_layer = []

    with progressbar.ProgressBar(max_value=len(slicer.layers)) as bar:
        for i, layer in enumerate(slicer.layers):

            if reverse:
                layer.paths.reverse()

            if len(layer.paths) > 3:
                pl_1_pts = []
                pl_2_pts = []

                for j, path in enumerate(layer.paths):
                    pts_in = []
                    pts_out = []

                    # convert path in polyline
                    pl = Polyline(path.points)
                
                    # define points in path
                    # first contour path
                    if j == 0:
                        # bottom layer          
                        if i == 0:      
                            pt_1 = pl.point(seam_parameter)
                            par_1 = seam_parameter
                        # above bottom layer
                        else:
                            pt_1 = compas.geometry.closest_point_on_polyline(pl_layer[i-1][1], pl)
                            par_1 = find_polyline_closest_parameter(pl, pt_1)
                    else:
                        pt = compas.geometry.closest_point_on_polyline(pt_2, pl)
                        pt_1 = Point(pt[0], pt[1], pt[2])
                        par_1 = find_polyline_closest_parameter(pl, pt_1)

                    # find second and third point (+ layer_width length)
                    par_2 = (par_1 + layer_width / pl.length) % 1.0
                    pt_2 = pl.point(par_2)

                    par_3 = (par_2 + layer_width / pl.length) % 1.0
                    pt_3 = pl.point(par_3)
                    
                    # assemble polyline points as paramter list
                    par_list = []
                    for x in range(len(pl.points)-1):
                        par_list.append(find_polyline_closest_parameter(pl, pl.points[x]) % 1.0)
                        
                    # assemble all points for new polyline
                    if j == 0:
                        pts_in.append(pt_2)  # TODO this line doesnt work in compas !!!
                    else:
                        pts_out.append(pt_2)

                    pts_in.append(pt_1) # first point
                    par_1 = par_1 % 1   # make sure 1.0 equals 0.0
                    
                    # condition: exceeding curve start/end
                    if par_1 > par_3:
                        pts = []
                        for x in par_list:
                            if x < par_1 and x > par_3:
                                pts.append(x)
                        pts = pts[::-1]
                    
                    # condition: not exceeding curve start/end
                    else:
                        pts_left = []
                        pts_right = []
                        for x in par_list:
                            if x < par_1:
                                pts_left.append(x)
                            if x > par_3:
                                pts_right.append(x)
                                
                        pts = pts_left[::-1] + pts_right[::-1]

                    for pt in pts:
                        pts_in.append((pl.point(pt)))
                            
                    # add last point
                    pts_in.append(pt_3)

                    # add point to polyline 2
                    #pts_out.append(pt_2)

                    # add all pts in layer
                    if j % 2 == 0:
                        pl_1_pts.extend(pts_in)
                        pl_2_pts.extend(pts_out)
                    else:
                        pl_1_pts.extend(pts_out)
                        pl_2_pts.extend(pts_in)
                
                # add all pts in layer (pl_1 + reverse pl_2)
                pl_layer.append(pl_1_pts + pl_2_pts[::-1])

                # workaround to replace tuples with points
                for k, point in enumerate(pl_layer[i]):
                    if isinstance(point, list):
                        pl_layer[i][k] = Point(point[0], point[1], point[2])

                # make path and add to layer
                new_path = Path(points=pl_layer[i], is_closed=False)

                # replace layer in slicer
                slicer.layers[i] = Layer(paths=[new_path])

            remaining_layers_num = len(slicer.layers) - i
            bar.update(i)
        
        logger.info('%d Points remaining after rdp simplification' % remaining_layers_num)


if __name__ == "__main__":
    pass
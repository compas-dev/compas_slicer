import numpy as np
import compas_slicer.utilities as utils
from compas_slicer.pre_processing.preprocessing_utils.gradient import normalize_gradient, \
    get_vertex_gradient_from_face_gradient, get_scalar_field_from_gradient, get_per_face_divergence


###################################################
### COMPOUND TARGET


def laplacian_smoothing_gradient_norm(self, g_evaluation, iterations, strength):
    """ Laplacian smoothing of the norm of the gradient. """
    assert len(self._distances_lists) == 1, "Only works for targets with a single neighborhood. "

    VG = np.array(g_evaluation.vertex_gradient)
    VG_norm = np.linalg.norm(VG, axis=1)
    utils.save_to_json(list(VG_norm), self.OUTPUT_PATH, 'n1.json')

    L = utils.get_mesh_cotmatrix_igl(self.mesh, fix_boundaries=True)  # sparse (#V x #V)
    for _ in range(iterations):  # iterative smoothing
        vg_norm_prime = VG_norm + strength * L * VG_norm
        VG_norm = vg_norm_prime
        print('min : ', np.min(VG_norm), 'max : ', np.max(VG_norm), 'mean : ', np.mean(VG_norm))
    utils.save_to_json(list(VG_norm), self.OUTPUT_PATH, 'n2.json')

    # --- update face gradient norm from the smoothened vertex grad norms
    X = g_evaluation.face_gradient
    X = normalize_gradient(X)

    for j, fkey in enumerate(self.mesh.faces()):
        vertex_indices = [self.mesh.key_index()[v_key] for v_key in self.mesh.face_vertices(fkey)]
        vertex_areas = np.array([self.mesh.vertex_area(vkey) for vkey in vertex_indices])
        v_norms = np.array([VG_norm[i] for i in vertex_indices])
        norm = np.sum(vertex_areas * v_norms) / np.sum(vertex_areas)

        X[j] = X[j] * norm

    L = utils.get_mesh_cotmatrix_igl(self.mesh, fix_boundaries=False)  # sparse (#V x #V)
    cotans = utils.get_mesh_cotans_igl(self.mesh)  # (#Fx3) list of 1/2*cotangents corresponding angles

    u = get_scalar_field_from_gradient(self.mesh, X, L, cotans)
    utils.save_to_json(list(u), self.OUTPUT_PATH, 'u.json')

    new_distances_lists = [list(u)]
    self.update_distances_lists(new_distances_lists)

    ###################################################
    ### PRE-PROCESSOR

    def targets_laplacian_smoothing_gradient_norm(self, iterations, strength, smooth_target_low=True,
                                                  smooth_target_high=True):
        """
        Smooth the norm of the gradient of the targets scalar field. Saves again the distances to json.

        Parameters
        ----------
        iterations: int
        strength: float
        smooth_target_low: bool
        smooth_target_high: bool
        """
        logger.info('Targets smoothing gradient norm. ')
        if smooth_target_low:
            g_eval = self.create_gradient_evaluation(target_1=self.target_LOW, save_output=False)
            self.target_LOW.laplacian_smoothing_gradient_norm(g_eval, iterations, strength)

        if smooth_target_high:
            pass

        self.target_LOW.save_distances("distances_LOW.json")
        self.target_HIGH.save_distances("distances_HIGH.json")
        self.target_HIGH.save_distances_clusters("distances_clusters_HIGH.json")

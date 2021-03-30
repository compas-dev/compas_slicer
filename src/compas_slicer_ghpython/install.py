from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import glob
import os
import shutil

import compas
import compas.plugins
import compas_ghpython
import compas_rhino


@compas.plugins.plugin(category='install')
def installable_rhino_packages():
    return ['compas_slicer_ghpython']


@compas.plugins.plugin(category='install')
def after_rhino_install(installed_packages):
    if 'compas_slicer_ghpython' not in installed_packages:
        return []

    results = []

    try:
        version = _get_version_from_args()
        dstdir = _get_grasshopper_userobjects_path(version)
        srcdir = os.path.join(os.path.dirname(__file__), 'gh_components')
        userobjects = glob.glob(os.path.join(srcdir, '*.ghuser'))

        for src in userobjects:
            dst = os.path.join(dstdir, os.path.basename(src))
            shutil.copyfile(src, dst)

        results.append(('compas_slicer_ghpython', 'Installed {} GH User Objects on {}'.format(len(userobjects), dstdir), True))
    except PermissionError:
        raise Exception('Please close first all instances of Rhino and then rerun the command')

    return results


@compas.plugins.plugin(category='install')
def after_rhino_uninstall(installed_packages):
    if 'compas_slicer_ghpython' not in installed_packages:
        return []

    results = []

    try:
        version = _get_version_from_args()
        dstdir = _get_grasshopper_userobjects_path(version)
        srcdir = os.path.join(os.path.dirname(__file__), 'gh_components')
        userobjects = glob.glob(os.path.join(srcdir, '*.ghuser'))

        for src in userobjects:
            dst = os.path.join(dstdir, os.path.basename(src))
            os.remove(dst)

        results.append(('compas_slicer_ghpython', 'Uninstalled {} GH User Objects'.format(len(userobjects)), True))
    except PermissionError:
        raise Exception('Please close first all instances of Rhino and then rerun the command')

    return results


def _get_version_from_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', choices=['5.0', '6.0', '7.0'], default='6.0')
    args = parser.parse_args()
    return compas_rhino._check_rhino_version(args.version)


# TODO: Remove once this PR is released: https://github.com/compas-dev/compas/pull/802
# For now, we just fake it get_grasshopper_library_path()
def _get_grasshopper_userobjects_path(version):
    lib_path = compas_ghpython.get_grasshopper_library_path(version)
    userobjects_path = lib_path.split(os.path.sep)[:-1] + ['UserObjects']
    return os.path.sep.join(userobjects_path)

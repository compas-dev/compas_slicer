import argparse
import glob
import os
import shutil
from pathlib import Path

import compas.plugins

try:
    import compas_ghpython
    import compas_rhino

    HAS_RHINO_DEPS = True
except ImportError:
    HAS_RHINO_DEPS = False


@compas.plugins.plugin(category="install")
def installable_rhino_packages():
    return ["compas_slicer_ghpython"]


@compas.plugins.plugin(category="install")
def after_rhino_install(installed_packages):
    if "compas_slicer_ghpython" not in installed_packages:
        return []

    if not HAS_RHINO_DEPS:
        return [("compas_slicer_ghpython", "compas_rhino not installed, skipping GH components", False)]

    results = []

    try:
        version = _get_version_from_args()
        dstdir = _get_grasshopper_userobjects_path(version)
        srcdir = Path(__file__).parent / "gh_components"
        userobjects = list(srcdir.glob("*.ghuser"))

        for src in userobjects:
            dst = Path(dstdir) / src.name
            shutil.copyfile(src, dst)

        results.append(
            ("compas_slicer_ghpython", f"Installed {len(userobjects)} GH User Objects on {dstdir}", True)
        )
    except PermissionError:
        raise Exception("Please close all instances of Rhino first and then rerun the command")

    return results


@compas.plugins.plugin(category="install")
def after_rhino_uninstall(installed_packages):
    if "compas_slicer_ghpython" not in installed_packages:
        return []

    if not HAS_RHINO_DEPS:
        return []

    results = []

    try:
        version = _get_version_from_args()
        dstdir = _get_grasshopper_userobjects_path(version)
        srcdir = Path(__file__).parent / "gh_components"
        userobjects = list(srcdir.glob("*.ghuser"))

        for src in userobjects:
            dst = Path(dstdir) / src.name
            if dst.exists():
                os.remove(dst)

        results.append(("compas_slicer_ghpython", f"Uninstalled {len(userobjects)} GH User Objects", True))
    except PermissionError:
        raise Exception("Please close all instances of Rhino first and then rerun the command")

    return results


def _get_version_from_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", choices=["6.0", "7.0", "8.0"], default="8.0")
    args, _ = parser.parse_known_args()
    return args.version


def _get_grasshopper_userobjects_path(version):
    lib_path = compas_ghpython.get_grasshopper_library_path(version)
    userobjects_path = Path(lib_path).parent / "UserObjects"
    return str(userobjects_path)

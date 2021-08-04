from __future__ import print_function

import glob
import os
import shutil
import sys

import clr
import System

clr.AddReferenceToFileAndPath(r"C:\Program Files\Rhino 6\Plug-ins\Grasshopper\GH_IO.dll")

from GH_IO.Serialization import GH_Archive  # noqa: E402


def process(file):
    archive = GH_Archive()
    if not archive.ReadFromFile(file):
        raise Exception('Cannot open file')

    root = archive.GetRootNode
    if not root:
        raise ValueError('GH Archive has no root')

    # Locate the single object present in the GHUser file
    object_item = root.FindItem("Object")

    # Load internal data and deserialize
    idata = System.Array[System.Byte](object_item.InternalData)

    component = GH_Archive()
    component.Deserialize_Binary(idata)

    # Update description
    desc_item = root.FindItem("Description")
    desc_text = update_description(file, str(desc_item.InternalData))
    root.RemoveItem(desc_item.Name, desc_item.Index)
    root.SetString(desc_item.Name, desc_text)

    # Locate CodeInput item
    component_root = component.GetRootNode
    code_input = component_root.FindItem("CodeInput")
    code = str(code_input.InternalData)

    # Run the code updates
    new_code = update_code(file, code)

    component_root.RemoveItem(code_input.Name, code_input.Index)
    component_root.SetString(code_input.Name, code_input.Index, new_code)

    root.RemoveItem(object_item.Name, object_item.Index)
    root.SetByteArray("Object", component.Serialize_Binary())

    target_dir = os.path.join(os.path.dirname(file), 'updated')
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    target_file = os.path.join(target_dir, os.path.basename(file)).replace('.ghuser', '.gh')
    if not archive.WriteToFile(target_file, True, False):
        raise Exception('Uh oh, something went wrong')

    shutil.move(target_file, target_file.replace('.gh', '.ghuser'))
    print('DONE'.rjust(74 - len(file)) + '\r', end='')


def update_description(component_file, old_text):
    new_text = old_text.replace("\nRequires to add '<path>/compas_slicer/src/grasshopper_visualization' to your python paths.", "")
    return new_text


def update_code(component_file, old_code):
    new_code = old_code.replace("import gh_compas_slicer", "import compas_slicer_ghpython.visualization as gh_compas_slicer")
    new_code = new_code.replace("Requires to add '<path>/compas_slicer/src/grasshopper_visualization' to your python paths.", "")
    return new_code


if __name__ == '__main__':

    print('Updating GH User components')

    files = list(glob.glob('*.ghuser'))
    for i, f in enumerate(files):
        progress = int((float(i + 1) / len(files)) * 100)
        print(' [{:>3}%] File: {}'.format(progress, f), end='')
        process(f)
        sys.stdout.flush()

    print()
    print('Successfully updated all GH User components')

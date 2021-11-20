import re
import os

import maya.cmds as cmds

from pathlib import Path
from re import match

# substance painter suffix file
BASE_COLOR = 'BaseColor'
METALNESS = 'Metalness'
ROUGHNESS = 'Roughness'
NORMAL = 'Normal'

# suffix files and maya props names map
PBR_MATERIAL_PROPERTIES = {
    BASE_COLOR: 'baseColor',
    METALNESS: 'metalness',
    ROUGHNESS: 'specularRoughness',
    NORMAL: 'normalCamera',
}

# supported image extensions
IMAGE_FILE_EXTENSIONS = ['png', 'jpeg', 'jpg', 'gif', 'tif', 'iff']

class TNC_Window(object):
    def close_window_button_clicked(self, *_):
        cmds.deleteUI(self.window, window=True)

    def browser_button_clicked(self, *_):
        print("Browser button clicked", os.listdir(self.startingDir))
        multipleFilters = "Image (*.png *.jpeg *.jpg *.gif *.tif *.iff);;"
        file_dialog = cmds.fileDialog2(startingDirectory=self.startingDir, fileFilter=multipleFilters, fileMode=4, okCaption="Load")

        self.texture_path = file_dialog

        print("TEXTURE_DIR_PATH: ", self.texture_path[0])

        self.shading_file_node = {}

        if self.texture_path:
            self.texture_path=Path(self.texture_path[0]).parent
            self.mat_name = os.path.basename(self.texture_path)
            cmds.textField(self.dirTextBox, text=self.texture_path, edit=True) 


    def _create_nodes(self):
        texture_files = os.listdir(self.texture_path)
        # create shading node
        self.shader = cmds.shadingNode('aiStandardSurface', name=self.mat_name, asShader=True, shared=True)

        for param in PBR_MATERIAL_PROPERTIES:
            for ext in IMAGE_FILE_EXTENSIONS:
                # create regex
                regex = f'.*.(_{param}).[0-9]*.{ext}|.*.(_{param}).{ext}'
                filtered_values = list(filter(lambda v: match(regex, v), texture_files))
                if len(filtered_values) > 0:
                    print(f"Create nodes for {param} with extension {ext}")
                    file_node_name = f'{self.shader}_{param}'
                    # create file node
                    file_node = cmds.shadingNode('file', name=f'{self.shader}_{param}', asTexture=True)

                    # if there are more files for the same param it set the UV Tiling Mode to UDIM (Mari)
                    if(len(filtered_values) > 1):
                        cmds.setAttr('%s.uvTilingMode' % file_node, 3)

                    file_path = os.path.join(f"{self.texture_path}\{filtered_values[0]}")
                    print("FILE PATH:", file_path)

                    cmds.setAttr('%s.ftn' % file_node, '%s' % file_path, type='string')

                    if param == METALNESS or param == ROUGHNESS:
                        cmds.connectAttr('%s.outAlpha' % file_node, f'{self.shader}.{PBR_MATERIAL_PROPERTIES[param]}')
                        cmds.setAttr('%s.colorSpace' % file_node, 'Raw', type='string')
                    else:
                        if param == NORMAL:
                            ai_normal_map_node = cmds.shadingNode('aiNormalMap', name='aiNormalMap', asUtility=True)
                            cmds.connectAttr('%s.outColor' % file_node, f'{ai_normal_map_node}.input')
                            cmds.connectAttr(f'{ai_normal_map_node}.input',  f'{self.shader}.{PBR_MATERIAL_PROPERTIES[param]}')
                        else:
                            cmds.connectAttr('%s.outColor' % file_node, f'{self.shader}.{PBR_MATERIAL_PROPERTIES[param]}')

                    # if the files for a param are found with a specific extension is not necessary
                    # to continue
                    break
                else:
                    print(f"No file found for the {self.mat_name} {param} param")

            
    def convert_button_clicked(self, *_):
        if os.path.exists(self.texture_path):
            # list all the geometry shapes in order to create the shape node
            print("Path exists", cmds.ls(type='geometryShape'))
            # creates material nodes
            self._create_nodes()
        else:
            print("This path does not exists")
       

    def __init__(self):
        self.window = "Texture nodes creator"
        self.title = "Texture nodes creator"
        self.mat_name = "MAT"
        
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        self.window = cmds.window(self.window, title=self.title)
        cmds.columnLayout("root", adjustableColumn=True)

        projectDirectory = cmds.workspace(q=True, rd=True)
        self.startingDir = projectDirectory if projectDirectory else os.environ["MAYA_APP_DIR"]
        self.texture_path = self.startingDir

        cmds.rowLayout("directoryRow", numberOfColumns=2, adjustableColumn=True, parent="root")
        self.dirTextBox = cmds.textField(text=self.startingDir, editable=False)
        browser_button = cmds.button("Browser", command=self.browser_button_clicked)

        cmds.separator(height=3, style="in", parent="root")
        
        cmds.rowLayout("buttonsRow", numberOfColumns=2, parent="root", columnAlign=(12, "right"))
        self.convert_button = cmds.button("convertButton", label="Convert", command=self.convert_button_clicked, parent="buttonsRow")
        close_button = cmds.button(label="Cancel", command=self.close_window_button_clicked, parent="buttonsRow")

        cmds.showWindow()

my_window = TNC_Window()


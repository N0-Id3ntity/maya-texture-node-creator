import re
import os
from re import match
from pathlib import Path
import maya.cmds as cmds

PBR_MATERIAL_PROPERTIES = {
    'BaseColor': 'baseColor',
    'Metalness': 'metalness',
    'Roughness': 'specularRoughness',
    'Normal': 'normalCamera',
}

IMAGE_FILE_EXTENSIONS = ['png', 'jpeg', 'jpg', 'gif', 'tif', 'iff']

class TNC_Window(object):
    def close_window_button_clicked(self, *_):
        cmds.deleteUI(self.window, window=True)

    def load_button_clicked(self, *_):
        print("Load texture button custom function [empty]")

    def browser_button_clicked(self, *_):
        print("Browser button clicked", os.listdir(self.startingDir))
        multipleFilters = "Image (*.png *.jpeg *.jpg *.gif *.tif *.iff);;"
        file_dialog = cmds.fileDialog2(startingDirectory=self.startingDir, fileFilter=multipleFilters, fileMode=4, okCaption="Load", optionsUICommit=self.load_button_clicked)

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
            print("PBR PROPERTY:", param)
            for ext in IMAGE_FILE_EXTENSIONS:
                print("PBR FILE EXTENSION:", ext)
                # create regex
                regex = f'.*.(_{param}).[0-9]*.{ext}|.*.(_{param}).{ext}'
                filtered_values = list(filter(lambda v: match(regex, v), texture_files))
                if len(filtered_values) > 0:
                    print(f"Create nodes for {param} with extension {ext}")
                    file_node_name = f'{self.shader}_{param}'
                    print("FILE NODE NAME: ", file_node_name)
                    # create file node
                    file_node = cmds.shadingNode('file', name=f'{self.shader}_{param}', asTexture=True)

                    # if there are more files for the same param it set the UV Tiling Mode to UDIM (Mari)
                    if(len(filtered_values) > 1):
                        cmds.setAttr('%s.uvTilingMode' % file_node, 3)

                    file_path = os.path.join(f"{self.texture_path}\{filtered_values[0]}")
                    print("FILE PATH:", file_path)

                    cmds.setAttr('%s.ftn' % file_node, '%s' % file_path, type='string')

                    if param == 'Metalness' or param == 'Roughness':
                        cmds.connectAttr('%s.outAlpha' % file_node, f'{self.shader}.{PBR_MATERIAL_PROPERTIES[param]}')
                        # cmds.setAttr('%s.colorSpace' % file_node, 10)
                    else:
                        if param == "Normal":
                            # ai_normal_map_node = cmds.createNode('aiNormalMap', type='aiNormalMap')
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
        print("Continue conversion process")
        if os.path.exists(self.texture_path):
            # list all the geometry shapes in order to create the shape node
            print("Path exists", cmds.ls(type='geometryShape'))
            # creates material nodes
            self._create_nodes()

        else:
            print("This path does not exists")
    
    # def _check_contains_images(self):
    #         texture_files = os.listdir(self.texture_path)
    #         regex = '.*.png|.*.jpeg|.*.jpg|.*.gif|.*.tif|.*.iff'
    #         filtered_values = list(filter(lambda v: match(regex, v), texture_files))
    #         if(len(filtered_values) == 0):
    #             print("No image found in this folder")
    #             cmds.setAttr("%s.enable" % self.convert_button, False)
    #         else:
    #             cmds.setAttr("%s.enable" % self.convert_button, True)
        
       

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

        # self.objects_list = cmds.ls(type='geometryShape') if len(cmds.ls(type='geometryShape')) > 0 else []
        # self.scroll_view = cmds.textScrollList('objectsList', parent='root', allowMultiSelection=True, append=self.objects_list, visible=len(self.objects_list) > 0)        


        cmds.separator(height=3, style="in", parent="root")
        
        cmds.rowLayout("buttonsRow", numberOfColumns=2, parent="root", columnAlign=(12, "right"))
        self.convert_button = cmds.button("convertButton", label="Convert", command=self.convert_button_clicked, parent="buttonsRow")
        close_button = cmds.button(label="Cancel", command=self.close_window_button_clicked, parent="buttonsRow")

        # self._check_contains_images()

        cmds.showWindow()

my_window = TNC_Window()


import re
import os
from re import match
from pathlib import Path
import maya.cmds as cmds

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


            
    def convert_button_clicked(self, *_):
        print("Continue conversion process")
        if os.path.exists(self.texture_path):
            # list all the geometry shapes in order to create the shape node
            print("Path exists", cmds.ls(type='geometryShape'))

            # create shading node
            self.shader = cmds.shadingNode('aiStandardSurface', name=self.mat_name, asShader=True, shared=True)
            # create albedo file
            albedo_file = cmds.shadingNode('file', name='%s_BaseColor' % self.shader, asTexture=True)
            
            texture_files = os.listdir(self.texture_path)
            regex = '.*.(_BaseColor).[0-9]*.png|.*.(_BaseColor).png'
            filtered_values = list(filter(lambda v: match(regex, v), texture_files))

            if (filtered_values):
                if(len(filtered_values) > 1):
                    cmds.setAttr('%s.uvTilingMode' % albedo_file, 3)

                albedo_file_path = os.path.join(f"{self.texture_path}\{texture_files[0]}")
                print("ALBEDO FILE PATH:", albedo_file_path)

                cmds.setAttr('%s.ftn' % albedo_file, '%s' % albedo_file_path, type='string')

                cmds.connectAttr('%s.outColor' % albedo_file, '%s.baseColor' %self.shader)
            else:
                print("No texture found for %s property" % regex)

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


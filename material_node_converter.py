import re
import os
from pathlib import Path
import maya.cmds as cmds

class TNC_Window(object):
    def close_window_button_clicked(self, *_):
        cmds.deleteUI(self.window, window=True)

    def load_button_clicked(self, *_):
        print("AOOOOOOO")

    def browser_button_clicked(self, *_):
        print("Browser button clicked", os.listdir(self.startingDir))
        multipleFilters = "Image (*.png *.jpeg *.jpg *.gif *.tif *.iff);;"
        file_dialog = cmds.fileDialog2(startingDirectory=self.startingDir, fileFilter=multipleFilters, fileMode=4, okCaption="Load", optionsUICommit=self.load_button_clicked)

        self.texture_path = file_dialog

        print("TEXTURE_DIR_PATH: ", self.texture_path[0])
        if self.texture_path:
            self.texture_path=Path(self.texture_path[0]).parent
            self.mat_name = os.path.basename(self.texture_path)
            print("AOOOOO", self.mat_name)
            cmds.textField(self.dirTextBox, text=self.texture_path, edit=True)
            material = cmds.shadingNode('aiStandardSurface', name=self.mat_name, asShader=True, shared=True)

    def convert_button_clicked(self, *_):
        print("Continue conversion process")
        if os.path.exists(self.texture_path):
            # list all the geometry shapes in order to create the shape node
            print("Path exists", cmds.ls(type='geometryShape'))
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

        cmds.rowLayout("directoryRow", numberOfColumns=2, adjustableColumn=True, parent="root")
        self.dirTextBox = cmds.textField(text=self.startingDir)
        browser_button = cmds.button("Browser", command=self.browser_button_clicked)

        # self.objects_list = cmds.ls(type='geometryShape') if len(cmds.ls(type='geometryShape')) > 0 else []
        # self.scroll_view = cmds.textScrollList('objectsList', parent='root', allowMultiSelection=True, append=self.objects_list, visible=len(self.objects_list) > 0)        
        
        # material = cmds.shadingNode('aiStandardSurface', name="myMaterial", asShader=True, shared=True)
        # cmds.select('pCubeShape1')
        # cmds.hyperShade(name=self.mat_name, assign=material)
        # # cmds.select(cl=True)
        # cmds.hyperShade( objects='pCubeShape1' )
        # blinn = cmds.createNode('blinn')
        # cmds.select( 'aiStandardSurface', blinn )
        # cmds.hyperShade( objects='' )

        cmds.separator(height=3, style="in", parent="root")
        
        cmds.rowLayout("buttonsRow", numberOfColumns=2, parent="root", columnAlign=(12, "right"))
        convert_button = cmds.button("Convert", command=self.convert_button_clicked, parent="buttonsRow")
        close_button = cmds.button("Cancel", command=self.close_window_button_clicked, parent="buttonsRow")

        cmds.showWindow()

my_window = TNC_Window()
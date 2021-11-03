import os
import maya.cmds as cmds

class TNC_Window(object):
    def close_window_button_clicked(self, *_):
        cmds.deleteUI(self.window, window=True)
        
    def browser_button_clicked(self, *_):
        print("Browser button clicked", os.listdir(self.startingDir))
        multipleFilters = "Image (*.png *.jpeg *.jpg *.gif *.tif *.iff);;"
        cmds.fileDialog2(startingDirectory=self.startingDir, fileFilter=multipleFilters, okCaption="Load")

    def convert_button_clicked(self, *_):
       print("Continue conversion process")
   
    def __init__(self):
        self.window = "Texture nodes creator"
        self.title = "Texture nodes creator"
        
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        self.window = cmds.window(self.window, title=self.title)
        cmds.columnLayout("root", adjustableColumn=True)

        
        projectDirectory = cmds.workspace(q=True, rd=True)
        self.startingDir = projectDirectory if projectDirectory else os.environ["MAYA_APP_DIR"]

        cmds.rowLayout("directoryRow", numberOfColumns=2, adjustableColumn=True, parent="root")
        dirTextBox = cmds.textField(text=self.startingDir)
        browser_button = cmds.button("Browser", command=self.browser_button_clicked)
        
        cmds.separator(height=3, style="in", parent="root")
        
        cmds.rowLayout("buttonsRow", numberOfColumns=2, parent="root", columnAlign=(12, "right"))
        convert_button = cmds.button("Convert", command=self.convert_button_clicked, parent="buttonsRow")
        close_button = cmds.button("Cancel", command=self.close_window_button_clicked, parent="buttonsRow")

        cmds.showWindow()

my_window = TNC_Window()
import os
import maya.cmds as cmds

class TNC_Window(object):
    def close_window(self, *_):
        cmds.deleteUI(self.window, window=True)
        
    def __init__(self):
        self.window = "Texture nodes creator"
        self.title = "Texture nodes creator"
        
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        self.window = cmds.window(self.window, title=self.title)
        cmds.columnLayout(adjustableColumn=True)

        
        projectDirectory = cmds.workspace(q=True, rd=True)
        startingDir = projectDirectory if projectDirectory else os.environ["MAYA_APP_DIR"]
        cmds.fileDialog2(caption="Select the texture's folder...", startingDirectory=startingDir, dialogStyle=2, fileFilter="*.png;;*.jpg;;*.jpeg;;*.sgi;;*.iff;;")
        
        button = cmds.button("Close", command=self.close_window)

        cmds.showWindow()

my_window = TNC_Window()
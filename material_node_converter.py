import re
import os

import maya.cmds as cmds

from pathlib import Path
from re import match

# substance painter suffix file
BASE_COLOR = "BaseColor"
METALNESS = "Metalness"
ROUGHNESS = "Roughness"
NORMAL = "Normal"

# suffix files and maya props names map
PBR_MATERIAL_PROPERTIES = {
    BASE_COLOR: "baseColor",
    METALNESS: "metalness",
    ROUGHNESS: "specularRoughness",
    NORMAL: "normalCamera",
}

# supported image extensions
IMAGE_FILE_EXTENSIONS = ["png", "jpeg", "jpg", "gif", "tif", "iff"]


class TNC_Window(object):
    """
    It creates a window in which the user select the texture folder and it creates the shading
    nodes.
    """

    def __init__(self):
        self.window = "Texture nodes creator"
        self.title = "Texture nodes creator"
        self.mat_name = "MAT"

        # it contains all the info (steps/errors) about the running process.
        self.messages = []

        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        self.window = cmds.window(self.window, title=self.title)
        cmds.columnLayout("root", adjustableColumn=True)

        projectDirectory = cmds.workspace(q=True, rd=True)
        self.startingDir = (
            projectDirectory if projectDirectory else os.environ["MAYA_APP_DIR"]
        )
        self.texture_path = self.startingDir

        cmds.rowLayout(
            "directoryRow", numberOfColumns=2, adjustableColumn=True, parent="root"
        )
        self.dirTextBox = cmds.textField(text=self.startingDir, editable=False)
        browser_button = cmds.button("Browser", command=self.browser_button_clicked)

        cmds.separator(height=3, style="in", parent="root")

        cmds.rowLayout(
            "noImageErrorRow",
            numberOfColumns=2,
            adjustableColumn=True,
            parent="root",
        )

        self.scroll_message_list = cmds.textScrollList(
            "processInfoAndErrorMessages",
            allowMultiSelection=False,
            append=self.messages,
        )

        cmds.rowLayout(
            "buttonsRow", numberOfColumns=2, parent="root", columnAlign=(12, "right")
        )
        self.convert_button = cmds.button(
            "convertButton",
            label="Convert",
            command=self.convert_button_clicked,
            parent="buttonsRow",
        )
        close_button = cmds.button(
            label="Cancel",
            command=self.close_window_button_clicked,
            parent="buttonsRow",
        )

        cmds.showWindow()

    def _create_nodes(self):
        """
        Using the texture folder path selected by the user it creates the linked shading nodes.
        """

        texture_files = os.listdir(self.texture_path)
        # create shading node
        self.shader = cmds.shadingNode(
            "aiStandardSurface", name=self.mat_name, asShader=True, shared=True
        )

        for param in PBR_MATERIAL_PROPERTIES:
            for ext in IMAGE_FILE_EXTENSIONS:
                # create regex
                regex = f".*.(_{param}).[0-9]*.{ext}|.*.(_{param}).{ext}"
                filtered_values = list(filter(lambda v: match(regex, v), texture_files))
                if len(filtered_values) > 0:
                    self.messages.append(
                        f"Create nodes for {param} with extension {ext}"
                    )
                    cmds.textScrollList(
                        self.scroll_message_list,
                        edit=True,
                        append=f"Create nodes for {param} with extension {ext}",
                        numberOfItems=len(self.messages),
                    )

                    file_node_name = f"{self.shader}_{param}"
                    # create file node
                    file_node = cmds.shadingNode(
                        "file", name=f"{self.shader}_{param}", asTexture=True
                    )

                    # if there are more files for the same param it set the UV Tiling Mode to
                    # UDIM (Mari)
                    if len(filtered_values) > 1:
                        cmds.setAttr("%s.uvTilingMode" % file_node, 3)

                    file_path = os.path.join(self.texture_path, filtered_values[0])
                    print("FILE PATH:", file_path)

                    cmds.setAttr("%s.ftn" % file_node, "%s" % file_path, type="string")

                    if param == METALNESS or param == ROUGHNESS:
                        cmds.connectAttr(
                            "%s.outAlpha" % file_node,
                            f"{self.shader}.{PBR_MATERIAL_PROPERTIES[param]}",
                        )
                        cmds.setAttr("%s.colorSpace" % file_node, "Raw", type="string")
                    else:
                        if param == NORMAL:
                            ai_normal_map_node = cmds.shadingNode(
                                "aiNormalMap", name="aiNormalMap", asUtility=True
                            )
                            cmds.connectAttr(
                                "%s.outColor" % file_node, f"{ai_normal_map_node}.input"
                            )
                            cmds.connectAttr(
                                f"{ai_normal_map_node}.input",
                                f"{self.shader}.{PBR_MATERIAL_PROPERTIES[param]}",
                            )
                        else:
                            cmds.connectAttr(
                                "%s.outColor" % file_node,
                                f"{self.shader}.{PBR_MATERIAL_PROPERTIES[param]}",
                            )

                    # if the files for a param are found with a specific extension is not
                    # necessary to continue
                    break
                else:
                    print(f"No file found for the {self.mat_name} {param} param")
                    self.messages.append(
                        f"No file found for the {self.mat_name} {param} param with {ext} extension."
                    )
                    cmds.textScrollList(
                        self.scroll_message_list,
                        edit=True,
                        append=f"No file found for the {self.mat_name} {param} param with {ext} extension.",
                        numberOfItems=len(self.messages),
                    )

        self.messages.append("FINISH")
        cmds.textScrollList(
            self.scroll_message_list,
            edit=True,
            append="FINISH",
            numberOfItems=len(self.messages),
        )
        print(self.process_messages)

    def _folder_contains_images(self):
        """
        Check if the selected folder contains images. If not show an error message.
        """
        regex = f".*.{'|.*.'.join(IMAGE_FILE_EXTENSIONS)}"
        texture_files = os.listdir(self.texture_path)
        filtered_values = list(filter(lambda v: match(regex, v), texture_files))

        return len(filtered_values) > 0

    def browser_button_clicked(self, *_):
        """
        It opens a file dialog in which the user select the texture folder.
        """
        multipleFilters = "Image (*.png *.jpeg *.jpg *.gif *.tif *.iff);;"
        file_dialog = cmds.fileDialog2(
            startingDirectory=self.texture_path
            if self.texture_path
            else self.startingDir,
            fileFilter=multipleFilters,
            fileMode=4,
            okCaption="Load",
        )

        self.texture_path = Path(file_dialog[0]).parent
        print("TEXTURE_DIR_PATH: ", self.texture_path)
        self.messages.append(f"TEXTURE_DIR_PATH: {self.texture_path}")
        cmds.textScrollList(
            self.scroll_message_list,
            edit=True,
            append=f"TEXTURE_DIR_PATH: {self.texture_path}",
            numberOfItems=len(self.messages),
        )

        self.shading_file_node = {}

        if self.texture_path:
            self.mat_name = os.path.basename(self.texture_path)
            cmds.textField(self.dirTextBox, text=self.texture_path, edit=True)

    def convert_button_clicked(self, *_):
        self.messages.clear()
        if self._folder_contains_images():
            if os.path.exists(self.texture_path):
                # list all the geometry shapes in order to create the shape node
                print("Path exists", cmds.ls(type="geometryShape"))
                # creates material nodes
                self._create_nodes()
            else:
                self.messages.append("This path does not exists.")
                cmds.textScrollList(
                    self.scroll_message_list,
                    edit=True,
                    append="This path does not exists.",
                    numberOfItems=len(self.messages),
                )
        else:
            self.messages.append(
                "This folder does not contains any images. Please select another one."
            )
            cmds.textScrollList(
                self.scroll_message_list,
                edit=True,
                append="This folder does not contains any images. Please select another one.",
                # highlightColor=[0.69, 0, 0.12],
                numberOfItems=len(self.messages),
            )

    def close_window_button_clicked(self, *_):
        """It closes the window."""
        cmds.deleteUI(self.window, window=True)


my_window = TNC_Window()

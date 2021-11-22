# TEXTURE NODE CREATOR

It is a python script that, once selected the texture folder, it creates and connect all the needed nodes.
It also evaluates if there are more UDIM and sets the correct value in the node params.

**NOTE:** It works only if the texture files name follow the name conventions of Substance Painter.

## Requirements
- Maya 2020 and greater
- Python 2.7 and greater

## How it works

1. Copy paste the script on the `Script Editor` of Maya and execute it.
2. Select an image inside the folder that contains the texuture for a specific object in the scene trhough the `Browser` button.
3. Click on the `Convert` button.
4. Open the `Shade Editor` and check if it creates correctly the material.

**NOTE:** The material by default takes the name of the selected folder with `_MAT` suffix.

5. Select the meshes you want to assign the material.
6. Right click on the viewport -> Assign Existing Material -> select the just created material.


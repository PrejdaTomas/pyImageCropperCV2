# pyCropper
Quick Image Cropper built upon OpenCV

**Dependencies**
- python-opencv-contrib (CV2 4.10.0.84)
- numpy (1.26.4)
- (C)Python 3.11.8
- Windows 10 (might work on any OS, provided the libs are included)

**Usage**
0) Download the dependencies through pip (Windows batch script included)
1) Put the script into a folder full of pictures
2) Launch it through a command line (python main.py -x -y -f -m -s -j -p)
   - -x: x-component of the aspect ratio (width), positive nonzero integer
   - -y: y-component of the aspect ratio (height), positive nonzero integer
   - -i: Path to the folder, from which the images are loaded. String. Defaults to the directory containing the main.py
   - -o: Name of the folder created in the workdir (-i flag), where the images will be stored. String. Defaults to 'CROPPED'
   - -s: Zoom of the displayed image. Float. Defaults to 0.25. Range = <0.05, inf)
   - -t: Output image type. Defaults to JPG. Range = {JPG, PNG}
   - -j: Quality of the resulting JPG. Integer. Defaults to 95. Range = <10, 100>.
   - -p: Compression of the resulting PNG. Integer. Defaults to 5. Range = <1, 10>.
   - -m": Minimum amount of pixels on the resulting image diagonal (minimum image size). Defaults to 0. Integer. Range = <0, inf)
3) When the image is displayed
  - select the first corner by moving the mouse cursor and left clicking the mouse
  - select the second corner by moving the mouse cursor and left clicking the mouse, this stores the cropped image into the folder in workdir by default named "CROPPED"
      - if the size image size is too small, a red appears
      - if the size is ok, a green rectangle appears
    - to reset the corners, press middle mouse button
    - to change the image orientation (landscape <-> portrait), press the "t" keyboard button
    - to change the selector tool orientation (invert aspect ratio), press the "tab" keyboard button
    - to rotate counter clockwise, press the "q" keyboard button
    - to rotate clockwise, press the "e" keyboard button
    - to reset the image, press the "r" keyboard button
    - to store the image, press "space" keyboard button
    - to turn the program off press "escape
4) After the second left mouse button click, another image is loaded.
5) Repeat till the last picture
6) Another functions will get added (skipping, going back and saving the image transforms like rotation and mirroring, perhaps ctrl-c and ctrl-z)

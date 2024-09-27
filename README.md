# Change Detection Tool - Polygon Labeling 🛰️

This **Change Detection Tool** is designed for creating and managing polygon labels on images, specifically for tasks such as satellite image analysis and change detection. With this tool, users can draw, label, and save polygons, allowing for efficient labeling of satellite images with various classes like buildings, roads, and green spaces. The tool supports importing images, comparing between two different images, and saving polygon data in a structured format.

## 📋 Features

- **Polygon Drawing and Labeling** ✍️  
  Allows users to draw polygons on imported images and assign them one of five predefined classes. This makes labeling for change detection quick and structured.
  
- **Class Support** 🏛️🛣️🌳🔥💧  
  You can label the polygons with the following classes:  
  1. **Buildings** 🏛️  
  2. **Roads** 🛣️  
  3. **Green Spaces** 🌳  
  4. **Wildfire Damage** 🔥  
  5. **Water Bodies** 💧  

- **Undo and Redo Support** ↩️↪️  
  The tool supports undo and redo functionality so you can reverse any mistakes while drawing polygons.

- **Switch Between Images** 🖼️  
  You can load two images and switch between them for easy comparison during change detection tasks.

- **Save and Load Labels** 💾  
  Labels can be saved as `.csv` files with polygons and their respective classes. You can also load previously saved labels for further editing.

- **Zoom and Pan** 🔍👆  
  Zoom in/out and pan around the image for precise labeling of small details.

- **Auto-switching Between Images** 🔄  
  Automatically switch between two loaded images for dynamic change detection comparison.

## ⚙️ Usage Instructions

1. **Start the Application**  
   Run the script and launch the tool. The main window will display options to import and work with images.

2. **Import Images** 🖼️  
   Use the "Import" button to load an image into the workspace. You can load two images for comparison.

3. **Drawing Polygons**  
   - Select the target class using the buttons for Buildings 🏛️, Roads 🛣️, Green Spaces 🌳, Wildfire Damage 🔥, or Water Bodies 💧.  
   - Click on the image to start drawing the polygon. Continue clicking to add vertices.
   - Right-click to finish the polygon or cancel the drawing.

4. **Save and Load Labels**  
   After labeling the image, save your work by clicking the "Save Label" button. Labels will be stored in CSV format with coordinates and class information.

5. **Switching Between Images**  
   Load two images and use the "Switch" button to toggle between them for easy comparison. You can also use the auto-switch feature to alternate between the images at set intervals.

6. **Undo/Redo**  
   Made a mistake? No problem! You can undo the last action using the Undo button, or bring back an undone action using Redo.

7. **Zoom and Pan**  
   Zoom in/out on the image using the mouse wheel, and pan around by dragging the image.

## 🚀 System Requirements

- **Python 3.x**
- **PyQt5**

To install PyQt5, use the following command:

```bash
pip install PyQt5
```

## ⌨️ Key Bindings

The tool also supports several keyboard shortcuts to make the labeling process faster and more efficient:

- **A**: 🖱️ Simulate a left mouse click at the current cursor position to start or finish drawing a polygon.
- **Shift**: 🔀 Switch between the two loaded images (if both images are loaded).
- **1-5**: 🔢 Change the polygon class based on the target:
  - **1**: Buildings 🏛️
  - **2**: Roads 🛣️
  - **3**: Green Spaces 🌳
  - **4**: Wildfire Damage 🔥
  - **5**: Water Bodies 💧
- **Ctrl + Z**: ↩️ Undo the last polygon drawing.
- **Ctrl + Y**: ↪️ Redo the last undone action.
- **Ctrl + S**: 💾 Save the current labels.
- **+ / -**: ⏱️ Adjust the auto-switching interval between images during comparison. "+" increases the interval, "-" decreases it.

These keyboard shortcuts help streamline the workflow, allowing you to quickly switch between tools and functions without relying on mouse actions alone.



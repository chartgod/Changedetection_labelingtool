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

## 📅 Update 10/11

We are excited to announce several new features and improvements to the **Change Detection Tool**, enhancing usability and efficiency for your labeling tasks.

### 1. Undo/Redo Functionality While Drawing Polygons 🔄

- **New Feature**: You can now use `Ctrl+Z` to **Undo** and `Ctrl+Y` to **Redo** while drawing polygons.
- **Details**:
  - In the `ImageBox` class, the `keyPressEvent` method has been updated to handle Undo/Redo actions even during the polygon drawing process.
  - The points of the currently drawn line are managed using the `self.line` list. Undo removes the last point, and Redo restores it.

### 2. Improved Layout and User Interface 🖥️

- **Changes**: Utilized `QSplitter` to create a more intuitive layout between the image display area and the tool panel.
- **Benefit**: Enhanced user interface makes the tool more convenient to use.

### 3. Simultaneous Loading of Image Pairs 🖼️🖼️

- **New Feature**: Load Base Image and Temporary B images as pairs for synchronized comparison.
- **Details**:
  - Added the `load_image_pair` method to load images from both lists simultaneously based on their indices.
  - Displays a warning message if the number of images in the two lists does not match.

### 4. Improved Saving of Labels for All Images 💾

- **Changes**: Enhanced functionality to save labels for **all images**, not just the current one.
- **Details**:
  - Modified the `savepoint` method to iterate over `self.image_labels` and save labels for each image.
  - Images without labels are skipped during the save process.

### 5. Better Unicode Filename Handling 🌐

- **Changes**: Improved image loading to correctly handle filenames containing Unicode characters, such as Korean.
- **Details**:
  - Used `np.fromfile` and `cv2.imdecode` to load images, ensuring proper handling of Unicode paths.

### 6. Added Class Selection Buttons 🔘

- **New Feature**: Introduced quick-select buttons for classes (Buildings, Roads, Green Spaces, Wildfire Damage, Water Bodies).
- **Benefit**: Easier and faster class switching during labeling.

### 7. Keyboard Shortcuts for Class Selection ⌨️

- **New Feature**: Use number keys **1-5** to quickly switch between classes.
- **Details**:
  - The `keyPressEvent` method in the `change_detection` class now handles number key inputs to change the current class.

### 8. Other Improvements ✨

- **Enhanced Zoom Functionality**: Adjusted the `wheelEvent` method for smoother zooming.
- **Improved Polygon Selection**: Enhanced highlighting when selecting polygons from the label list.
- **Automatic Label Loading**: When loading images, existing labels are automatically loaded if available.

---

These updates significantly improve the overall user experience of the **Change Detection Tool**, making labeling tasks more efficient and user-friendly.

# --------------------------------------------------------------------------------
# File generated from BuliPy/build_docs.py
# Can be used by IDE for auto-complete
# Build from header files from Krita's libkis source code folder
# 
# Git tag:  v5.2.0 (2023-10-13)
# Git hash: 1d16de46b01426233324dc2eb6775f081b4a8ddd
# --------------------------------------------------------------------------------

from PyQt5.Qt import *

# Declare empty classes to avoid inter-dependencies failure
class Canvas: pass
class Channel: pass
class CloneLayer: pass
class ColorizeMask: pass
class DockWidget: pass
class DockWidgetFactoryBase: pass
class Document: pass
class Extension: pass
class FileLayer: pass
class FillLayer: pass
class Filter: pass
class FilterLayer: pass
class FilterMask: pass
class GroupLayer: pass
class GroupShape: pass
class InfoObject: pass
class Krita: pass
class ManagedColor: pass
class Node: pass
class Notifier: pass
class Palette: pass
class PaletteView: pass
class Preset: pass
class PresetChooser: pass
class Resource: pass
class Scratchpad: pass
class Selection: pass
class SelectionMask: pass
class Shape: pass
class Swatch: pass
class TransformMask: pass
class TransparencyMask: pass
class VectorLayer: pass
class View: pass
class Window: pass
class DockPosition: pass


# Source
# - File: Canvas.h
# - Line: 22
class Canvas(QObject):
    """Canvas wraps the canvas inside a view on an image/document.
    It is responsible for the view parameters of the document:
    zoom, rotation, mirror, wraparound and instant preview.

    @Implemented with: 4.0.0
    """
    # Source location, line 90
    def levelOfDetailMode(self) -> bool:
        """@return true if the canvas is in Instant Preview mode, false if not. Only when OpenGL is enabled,
        is Instant Preview mode available.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 68
    def mirror(self) -> bool:
        """@return return true if the canvas is mirrored, false otherwise.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 63
    def resetRotation(self):
        """@brief resetRotation reset the canvas rotation.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 48
    def resetZoom(self):
        """@brief resetZoom set the zoomlevel to 100%
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 53
    def rotation(self) -> float:
        """@return the rotation of the canvas in degrees.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 95
    def setLevelOfDetailMode(self, enable: bool):
        """@brief setLevelOfDetailMode sets Instant Preview to @param enable
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 73
    def setMirror(self, value: bool):
        """@brief setMirror turn the canvas mirroring on or off depending on @param value
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 58
    def setRotation(self, angle: float):
        """@brief setRotation set the rotation of the canvas to the given  @param angle in degrees.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 84
    def setWrapAroundMode(self, enable: bool):
        """@brief setWrapAroundMode set wraparound mode to  @param enable
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 43
    def setZoomLevel(self, value: float):
        """@brief setZoomLevel set the zoomlevel to the given @p value. 1.0 is 100%.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 100
    def view(self) -> View:
        """@return the view that holds this canvas
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 79
    def wrapAroundMode(self) -> bool:
        """@return true if the canvas is in wraparound mode, false if not. Only when OpenGL is enabled,
        is wraparound mode available.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 38
    def zoomLevel(self) -> float:
        """@return the current zoomlevel. 1.0 is 100%.
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: Channel.h
# - Line: 22
class Channel(QObject):
    """A Channel represents a single channel in a Node. Krita does not
    use channels to store local selections: these are strictly the
    color and alpha channels.

    @Implemented with: 4.0.0
    """
    # Source location, line 62
    def bounds(self) -> QRect:
        """@return the exact bounds of the channel. This can be smaller than the bounds of the Node this channel is part of.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 57
    def channelSize(self) -> int:
        """@return the number of bytes this channel takes
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 47
    def name(self) -> str:
        """@return the name of the channel
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 70
    def pixelData(self, rect: QRect) -> QByteArray:
        """Read the values of the channel into the a byte array for each pixel in the rect from the Node this channel is part of, and returns it.

        Note that if Krita is built with OpenEXR and the Node has the 16 bits floating point channel depth type, Krita returns
        32 bits float for every channel; the libkis scripting API does not support half.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 52
    def position(self) -> int:
        """@returns the position of the first byte of the channel in the pixel
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 82
    def setPixelData(self, value: QByteArray, rect: QRect):
        """@brief setPixelData writes the given data to the relevant channel in the Node. This is only possible for Nodes
        that have a paintDevice, so nothing will happen when trying to write to e.g. a group layer.

        Note that if Krita is built with OpenEXR and the Node has the 16 bits floating point channel depth type, Krita expects
        to be given a 4 byte, 32 bits float for every channel; the libkis scripting API does not support half.

        @param value a byte array with exactly enough bytes.
        @param rect the rectangle to write the bytes into
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 42
    def setVisible(self, value: bool):
        """@brief setvisible set the visibility of the channel to the given value.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 37
    def visible(self) -> bool:
        """@brief visible checks whether this channel is visible in the node
        @return the status of this channel
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: CloneLayer.h
# - Line: 25
class CloneLayer(Node):
    """@brief The CloneLayer class
    A clone layer is a layer that takes a reference inside the image
    and shows the exact same pixeldata.

    If the original is updated, the clone layer will update too.

    @Implemented with: 4.0.0
    @Updated with: 5.2.0
    """
    # Source location, line 61
    def setSourceNode(self, node: Node):
        """@brief setSourceNode
        @param node the node to use as the source of the clone layer.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 55
    def sourceNode(self) -> Node:
        """@brief sourceNode
        @return the node the clone layer is based on.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 49
    def type(self) -> str:
        """@brief type Krita has several types of nodes, split in layers and masks. Group
        layers can contain other layers, any layer can contain masks.

        @return clonelayer
        @Virtual
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: ColorizeMask.h
# - Line: 59
class ColorizeMask(Node):
    """@brief The ColorizeMask class
    A colorize mask is a mask type node that can be used
    to color in line art.

    @code
    window = Krita.instance().activeWindow()
    doc = Krita.instance().createDocument(10, 3, "Test", "RGBA", "U8", "", 120.0)
    window.addView(doc)
    root = doc.rootNode();
    node = doc.createNode("layer", "paintLayer")
    root.addChildNode(node, None)
    nodeData = QByteArray.fromBase64(b"AAAAAAAAAAAAAAAAEQYMBhEGDP8RBgz/EQYMAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARBgz5EQYM/xEGDAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEQYMAhEGDAkRBgwCAAAAAAAAAAAAAAAA");
    node.setPixelData(nodeData,0,0,10,3)

    cols = [ ManagedColor('RGBA','U8',''), ManagedColor('RGBA','U8','') ]
    cols[0].setComponents([0.65490198135376, 0.345098048448563, 0.474509805440903, 1.0]);
    cols[1].setComponents([0.52549022436142, 0.666666686534882, 1.0, 1.0]);
    keys = [
            QByteArray.fromBase64(b"/48AAAAAAAAAAAAAAAAAAAAAAACmCwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"),
            QByteArray.fromBase64(b"AAAAAAAAAACO9ocAAAAAAAAAAAAAAAAAAAAAAMD/uQAAAAAAAAAAAAAAAAAAAAAAGoMTAAAAAAAAAAAA")
            ]

    mask = doc.createColorizeMask('c1')
    node.addChildNode(mask,None)
    mask.setEditKeyStrokes(True)

    mask.setUseEdgeDetection(True)
    mask.setEdgeDetectionSize(4.0)
    mask.setCleanUpAmount(70.0)
    mask.setLimitToDeviceBounds(True)
    mask.initializeKeyStrokeColors(cols)

    for col,key in zip(cols,keys):
        mask.setKeyStrokePixelData(key,col,0,0,20,3)

    mask.updateMask()
    mask.setEditKeyStrokes(False);
    mask.setShowOutput(True);
    @endcode

    @Implemented with: 5.2.0
    """
    # Source location, line 178
    def cleanUpAmount(self) -> float:
        """@brief cleanUpAmount
        @return a float value of 0.0 to 100.0 representing the cleanup amount where 0.0 is no cleanup is done and 100.00 is most aggressive.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 165
    def edgeDetectionSize(self) -> float:
        """@brief edgeDetectionSize
        @return a float value of the edge detection size in pixels.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 221
    def editKeyStrokes(self) -> bool:
        """@brief editKeyStrokes
        Edit keystrokes mode allows the user to modify keystrokes on the active Colorize Mask.
        @return true if edit keystrokes mode is enabled, false if disabled.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 94
    def initializeKeyStrokeColors(self, colors: list[ManagedColor], transparentIndex: int = 1):
        """@brief initializeKeyStrokeColors
        Set the colors to use for the Colorize Mask's keystrokes.
        @param colors a list of ManagedColor to use for the keystrokes.
        @param transparentIndex index of the color that should be marked as transparent.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 121
    def keyStrokePixelData(self, color: ManagedColor, x: int, y: int, w: int, h: int) -> QByteArray:
        """@brief keyStrokePixelData
        reads the given rectangle from the keystroke image data and returns it as a byte
        array. The pixel data starts top-left, and is ordered row-first.
        @param color a ManagedColor to get keystrokes pixeldata from.
        @param x x position from where to start reading
        @param y y position from where to start reading
        @param w row length to read
        @param h number of rows to read
        @return a QByteArray with the pixel data. The byte array may be empty.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 86
    def keyStrokesColors(self) -> list[ManagedColor]:
        """@brief keyStrokesColors
        Colors used in the Colorize Mask's keystrokes.
        @return a ManagedColor list containing the colors of keystrokes.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 191
    def limitToDeviceBounds(self) -> bool:
        """@brief limitToDeviceBounds
        @return true if limit bounds is enabled, false if disabled.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 101
    def removeKeyStroke(self, color: ManagedColor):
        """@brief removeKeyStroke
        Remove a color from the Colorize Mask's keystrokes.
        @param color a ManagedColor to be removed from the keystrokes.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 200
    def resetCache(self):
        """@Implemented with: 5.2.0"""
        pass

    # Source location, line 172
    def setCleanUpAmount(self, value: float):
        """@brief setCleanUpAmount
        This will attempt to handle messy strokes that overlap the line art where they shouldn't.
        @param value a float value from 0.0 to 100.00 where 0.0 is no cleanup is done and 100.00 is most aggressive.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 159
    def setEdgeDetectionSize(self, value: float):
        """@brief setEdgeDetectionSize
        Set the value to the thinnest line on the image.
        @param value a float value of the edge size to detect in pixels.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 228
    def setEditKeyStrokes(self, enabled: bool):
        """@brief setEditKeyStrokes
        Toggle Colorize Mask's edit keystrokes mode.
        @param enabled set true to enable edit keystrokes mode and false to disable it.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 139
    def setKeyStrokePixelData(self, value: QByteArray, color: ManagedColor, x: int, y: int, w: int, h: int) -> bool:
        """@brief setKeyStrokePixelData
        writes the given bytes, of which there must be enough, into the
        keystroke, the keystroke's original pixels are overwritten

        @param value the byte array representing the pixels. There must be enough bytes available.
        Krita will take the raw pointer from the QByteArray and start reading, not stopping before
        (number of channels * size of channel * w * h) bytes are read.

        @param color a ManagedColor to set keystrokes pixeldata for.
        @param x the x position to start writing from
        @param y the y position to start writing from
        @param w the width of each row
        @param h the number of rows to write
        @return true if writing the pixeldata worked
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 185
    def setLimitToDeviceBounds(self, value: bool):
        """@brief setLimitToDeviceBounds
        Limit the colorize mask to the combined layer bounds of the strokes and the line art it is filling. This can speed up the use of the mask on complicated compositions, such as comic pages.
        @param value set true to enabled limit bounds, false to disable.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 214
    def setShowOutput(self, enabled: bool):
        """@brief setShowOutput
        Toggle Colorize Mask's show output mode.
        @param enabled set true to enable show coloring mode and false to disable it.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 146
    def setUseEdgeDetection(self, value: bool):
        """@brief setUseEdgeDetection
        Activate this for line art with large solid areas, for example shadows on an object.
        @param value true to enable edge detection, false to disable.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 207
    def showOutput(self) -> bool:
        """@brief showOutput
        Show output mode allows the user to see the result of the Colorize Mask's algorithm.
        @return true if edit show coloring mode is enabled, false if disabled.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 108
    def transparencyIndex(self) -> int:
        """@brief transparencyIndex
        Index of the transparent color.
        @return an integer containing the index of the current color marked as transparent.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 79
    def type(self) -> str:
        """@brief type Krita has several types of nodes, split in layers and masks. Group
        layers can contain other layers, any layer can contain masks.

        @return colorizemask

        If the Node object isn't wrapping a valid Krita layer or mask object, and
        empty string is returned.
        @Virtual
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 198
    def updateMask(self, force: bool = False):
        """@brief updateMask
        Process the Colorize Mask's keystrokes and generate a projection of the computed colors.
        @param force force an update
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 152
    def useEdgeDetection(self) -> bool:
        """@brief useEdgeDetection
        @return true if Edge detection is enabled, false if disabled.
        @Implemented with: 5.2.0
        """
        pass


# Source
# - File: DockWidget.h
# - Line: 42
class DockWidget(QDockWidget):
    """DockWidget is the base class for custom Dockers. Dockers are created by a
    factory class which needs to be registered by calling Application.addDockWidgetFactory:

    @code
    class HelloDocker(DockWidget):
      def __init__(self):
          super().__init__()
          label = QLabel("Hello", self)
          self.setWidget(label)
          self.label = label
          self.setWindowTitle("Hello Docker")

    def canvasChanged(self, canvas):
          self.label.setText("Hellodocker: canvas changed");

    Application.addDockWidgetFactory(DockWidgetFactory("hello", DockWidgetFactoryBase.DockRight, HelloDocker))

    @endcode

    One docker per window will be created, not one docker per canvas or view. When the user
    switches between views/canvases, canvasChanged will be called. You can override that
    method to reset your docker's internal state, if necessary.

    @Implemented with: 4.0.0
    """
    # Source location, line 61
    def canvas(self) -> Canvas:
        """@@return the canvas object that this docker is currently associated with
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 68
    def canvasChanged(self, canvas: Canvas):
        """@brief canvasChanged is called whenever the current canvas is changed
        in the mainwindow this dockwidget instance is shown in.
        @param canvas The new canvas.
        @Virtual
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: DockWidgetFactoryBase.h
# - Line: 36
class DockWidgetFactoryBase:
    """@brief The DockWidgetFactoryBase class is the base class for plugins that want
    to add a dock widget to every window. You do not need to implement this class
    yourself, but create a DockWidget implementation and then add the DockWidgetFactory
    to the Krita instance like this:

    @code
    class HelloDocker(DockWidget):
      def __init__(self):
          super().__init__()
          label = QLabel("Hello", self)
          self.setWidget(label)
          self.label = label

    def canvasChanged(self, canvas):
          self.label.setText("Hellodocker: canvas changed");

    Application.addDockWidgetFactory(DockWidgetFactory("hello", DockWidgetFactoryBase.DockRight, HelloDocker))

    @endcode

    @Implemented with: 4.0.0
    """
    # Source location, line 39
    def DockWidgetFactoryBase(self, _id: str, _dockPosition: DockPosition):
        """@Implemented with: 4.0.0
        @Last updated with: 5.0.0
        """
        pass

    # Source location, line 56
    def defaultCollapsed(self) -> bool:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 42
    def defaultDockPosition(self) -> DockPosition:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 41
    def id(self) -> str:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 55
    def isCollapsable(self) -> bool:
        """@Implemented with: 4.0.0"""
        pass


# Source
# - File: Document.h
# - Line: 33
class Document(QObject):
    """The Document class encapsulates a Krita Document/Image. A Krita document is an Image with
    a filename. Libkis does not differentiate between a document and an image, like Krita does
    internally.

    @Implemented with: 4.0.0
    @Updated with: 5.2.0
    """
    # Source location, line 95
    def activeNode(self) -> Node:
        """@brief activeNode retrieve the node that is currently active in the currently active window
        @return the active node. If there is no active window, the first child node is returned.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 864
    def animationLength(self) -> int:
        """@brief get total frame range for animation
        @return total frame range for animation
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 913
    def annotation(self, type: str) -> QByteArray:
        """@brief annotation the actual data for the annotation for this type. It's a simple
        QByteArray, what's in it depends on the type of the annotation
        @param type the type of the annotation
        @return a bytearray, possibly empty if this type of annotation doesn't exist
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 905
    def annotationDescription(self, type: str) -> str:
        """@brief annotationDescription gets the pretty description for the current annotation
        @param type the type of the annotation
        @return a string that can be presented to the user
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 898
    def annotationTypes(self) -> list[str]:
        """@brief annotationTypes returns the list of annotations present in the document.
        Each annotation type is unique.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 198
    def backgroundColor(self) -> QColor:
        """@brief backgroundColor returns the current background color of the document. The color will
        also include the opacity.

        @return QColor
        @Implemented with: 4.0.2
        """
        pass

    # Source location, line 83
    def batchmode(self) -> bool:
        """Batchmode means that no actions on the document should show dialogs or popups.
        @return true if the document is in batchmode.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 811
    def bounds(self) -> QRect:
        """@brief bounds return the bounds of the image
        @return the bounds
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 77
    def clone(self):
        """@brief clone create a shallow clone of this document.
        @return a new Document that should be identical to this one in every respect.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 420
    def close(self) -> bool:
        """@brief close Close the document: remove it from Krita's internal list of documents and
        close all views. If the document is modified, you should save it first. There will be
        no prompt for saving.

        After closing the document it becomes invalid.

        @return true if the document is closed.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 133
    def colorDepth(self) -> str:
        """colorDepth A string describing the color depth of the image:
        <ul>
        <li>U8: unsigned 8 bits integer, the most common type</li>
        <li>U16: unsigned 16 bits integer</li>
        <li>F16: half, 16 bits floating point. Only available if Krita was built with OpenEXR</li>
        <li>F32: 32 bits floating point</li>
        </ul>
        @return the color depth.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 148
    def colorModel(self) -> str:
        """@brief colorModel retrieve the current color model of this document:
        <ul>
        <li>A: Alpha mask</li>
        <li>RGBA: RGB with alpha channel (The actual order of channels is most often BGR!)</li>
        <li>XYZA: XYZ with alpha channel</li>
        <li>LABA: LAB with alpha channel</li>
        <li>CMYKA: CMYK with alpha channel</li>
        <li>GRAYA: Gray with alpha channel</li>
        <li>YCbCrA: YCbCr with alpha channel</li>
        </ul>
        @return the internal color model string.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 153
    def colorProfile(self) -> str:
        """@return the name of the current color profile
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 641
    def createCloneLayer(self, name: str, source: Node) -> CloneLayer:
        """@brief createCloneLayer
        @param name
        @param source
        @return
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 701
    def createColorizeMask(self, name: str) -> ColorizeMask:
        """@brief createColorizeMask
        Creates a colorize mask, which can be used to color fill via keystrokes.
        @param name - the name of the layer.
        @return a TransparencyMask
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 599
    def createFileLayer(self, name: str, fileName: str, scalingMethod: str, scalingFilter: str = "Bicubic") -> FileLayer:
        """@brief createFileLayer returns a layer that shows an external image.
        @param name name of the file layer.
        @param fileName the absolute filename of the file referenced. Symlinks will be resolved.
        @param scalingMethod how the dimensions of the file are interpreted
               can be either "None", "ImageToSize" or "ImageToPPI"
        @param scalingFilter filter used to scale the file
               can be "Bicubic", "Hermite", "NearestNeighbor", "Bilinear", "Bell", "BSpline", "Lanczos3", "Mitchell"
        @return a FileLayer
        @Implemented with: 4.0.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 633
    def createFillLayer(self, name: str, generatorName: str, configuration: InfoObject, selection: Selection) -> FillLayer:
        """@brief createFillLayer creates a fill layer object, which is a layer
        @param name
        @param generatorName - name of the generation filter.
        @param configuration - the configuration for the generation filter.
        @param selection - the selection.
        @return a filllayer object.

        @code
        from krita import *
        d = Krita.instance().activeDocument()
        i = InfoObject();
        i.setProperty("pattern", "Cross01.pat")
        s = Selection();
        s.select(0, 0, d.width(), d.height(), 255)
        n = d.createFillLayer("test", "pattern", i, s)
        r = d.rootNode();
        c = r.childNodes();
        r.addChildNode(n, c[0])
        d.refreshProjection()
        @endcode
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 609
    def createFilterLayer(self, name: str, filter: Filter, selection: Selection) -> FilterLayer:
        """@brief createFilterLayer creates a filter layer, which is a layer that represents a filter
        applied non-destructively.
        @param name name of the filterLayer
        @param filter the filter that this filter layer will us.
        @param selection the selection.
        @return a filter layer object.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 669
    def createFilterMask(self, name: str, filter: Filter, selection_source: Node) -> FilterMask:
        """@brief createFilterMask
        Creates a filter mask object that much like a filterlayer can apply a filter non-destructively.
        @param name the name of the layer.
        @param filter the filter assigned.
        @param selection_source a node from which the selection should be initialized
        @return a FilterMask
        @Implemented with: 4.0.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 588
    def createGroupLayer(self, name: str) -> GroupLayer:
        """@brief createGroupLayer
        Returns a grouplayer object. Grouplayers are nodes that can have
        other layers as children and have the passthrough mode.
        @param name the name of the layer.
        @return a GroupLayer object.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 580
    def createNode(self, name: str, nodeType: str) -> Node:
        """@brief createNode create a new node of the given type. The node is not added
        to the node hierarchy; you need to do that by finding the right parent node,
        getting its list of child nodes and adding the node in the right place, then
        calling Node::SetChildNodes

        @param name The name of the node

        @param nodeType The type of the node. Valid types are:
        <ul>
         <li>paintlayer
         <li>grouplayer
         <li>filelayer
         <li>filterlayer
         <li>filllayer
         <li>clonelayer
         <li>vectorlayer
         <li>transparencymask
         <li>filtermask
         <li>transformmask
         <li>selectionmask
        </ul>

        When relevant, the new Node will have the colorspace of the image by default;
        that can be changed with Node::setColorSpace.

        The settings and selections for relevant layer and mask types can also be set
        after the Node has been created.

        @code
        d = Application.createDocument(1000, 1000, "Test", "RGBA", "U8", "", 120.0)
        root = d.rootNode();
        print(root.childNodes())
        l2 = d.createNode("layer2", "paintLayer")
        print(l2)
        root.addChildNode(l2, None)
        print(root.childNodes())
        @endcode


        @return the new Node.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 677
    def createSelectionMask(self, name: str) -> SelectionMask:
        """@brief createSelectionMask
        Creates a selection mask, which can be used to store selections.
        @param name - the name of the layer.
        @return a SelectionMask
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 693
    def createTransformMask(self, name: str) -> TransformMask:
        """@brief createTransformMask
        Creates a transform mask, which can be used to apply a transformation non-destructively.
        @param name - the name of the layer mask.
        @return a TransformMask
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 685
    def createTransparencyMask(self, name: str) -> TransparencyMask:
        """@brief createTransparencyMask
        Creates a transparency mask, which can be used to assign transparency to regions.
        @param name - the name of the layer.
        @return a TransparencyMask
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 649
    def createVectorLayer(self, name: str) -> VectorLayer:
        """@brief createVectorLayer
        Creates a vector layer that can contain vector shapes.
        @param name the name of this layer.
        @return a VectorLayer.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 430
    def crop(self, x: int, y: int, w: int, h: int):
        """@brief crop the image to rectangle described by @p x, @p y,
        @p w and @p h
        @param x x coordinate of the top left corner
        @param y y coordinate of the top left corner
        @param w width
        @param h height
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 887
    def currentTime(self) -> int:
        """@brief get current frame selected of animation
        @return current frame selected of animation
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 252
    def documentInfo(self) -> str:
        """@brief documentInfo creates and XML document representing document and author information.
        @return a string containing a valid XML document with the right information about the document
        and author. The DTD can be found here:

        https://phabricator.kde.org/source/krita/browse/master/krita/dtd/

        @code
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE document-info PUBLIC '-//KDE//DTD document-info 1.1//EN' 'http://www.calligra.org/DTD/document-info-1.1.dtd'>
        <document-info xmlns="http://www.calligra.org/DTD/document-info">
        <about>
         <title>My Document</title>
          <description></description>
          <subject></subject>
          <abstract><![CDATA[]]></abstract>
          <keyword></keyword>
          <initial-creator>Unknown</initial-creator>
          <editing-cycles>1</editing-cycles>
          <editing-time>35</editing-time>
          <date>2017-02-27T20:15:09</date>
          <creation-date>2017-02-27T20:14:33</creation-date>
          <language></language>
         </about>
         <author>
          <full-name>Boudewijn Rempt</full-name>
          <initial></initial>
          <author-title></author-title>
          <email></email>
          <telephone></telephone>
          <telephone-work></telephone-work>
          <fax></fax>
          <country></country>
          <postal-code></postal-code>
          <city></city>
          <street></street>
          <position></position>
          <company></company>
         </author>
        </document-info>
        @endcode
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 471
    def exportImage(self, filename: str, exportConfiguration: InfoObject) -> bool:
        """@brief exportImage export the image, without changing its URL to the given path.
        @param filename the full path to which the image is to be saved
        @param exportConfiguration a configuration object appropriate to the file format.
        An InfoObject will used to that configuration.

        The supported formats have specific configurations that must be used when in
        batchmode. They are described below:

        \b png
        <ul>
        <li>alpha: bool (True or False)
        <li>compression: int (1 to 9)
        <li>forceSRGB: bool (True or False)
        <li>indexed: bool (True or False)
        <li>interlaced: bool (True or False)
        <li>saveSRGBProfile: bool (True or False)
        <li>transparencyFillcolor: rgb (Ex:[255,255,255])
        </ul>

        \b jpeg
        <ul>
        <li>baseline: bool (True or False)
        <li>exif: bool (True or False)
        <li>filters: bool (['ToolInfo', 'Anonymizer'])
        <li>forceSRGB: bool (True or False)
        <li>iptc: bool (True or False)
        <li>is_sRGB: bool (True or False)
        <li>optimize: bool (True or False)
        <li>progressive: bool (True or False)
        <li>quality: int (0 to 100)
        <li>saveProfile: bool (True or False)
        <li>smoothing: int (0 to 100)
        <li>subsampling: int (0 to 3)
        <li>transparencyFillcolor: rgb (Ex:[255,255,255])
        <li>xmp: bool (True or False)
        </ul>
        @return true if the export succeeded, false if it failed.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 266
    def fileName(self) -> str:
        """@return the full path to the document, if it has been set.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 476
    def flatten(self):
        """@brief flatten all layers in the image
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 830
    def framesPerSecond(self) -> int:
        """@brief frames per second of document
        @return the fps of the document
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 858
    def fullClipRangeEndTime(self) -> int:
        """@brief get the full clip range end time
        @return full clip range end time
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 846
    def fullClipRangeStartTime(self) -> int:
        """@brief get the full clip range start time
        @return full clip range start time
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 69
    def guidesLocked(self) -> bool:
        """@brief guidesLocked
        Returns guide lockedness.
        @return whether the guides are locked.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 63
    def guidesVisible(self) -> bool:
        """@brief guidesVisible
        Returns guide visibility.
        @return whether the guides are visible.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 276
    def height(self) -> int:
        """@return the height of the image in pixels
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 50
    def horizontalGuides(self) -> list[float]:
        """@brief horizontalGuides
        The horizontal guides.
        @return a list of the horizontal positions of guides.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 824
    def importAnimation(self, files: list[str], firstFrame: int, step: int) -> bool:
        """@brief Import an image sequence of files from a directory. This will grab all
        images from the directory and import them with a potential offset (firstFrame)
        and step (images on 2s, 3s, etc)
        @returns whether the animation import was successful
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 723
    def isIdle(self) -> bool:
        """Why this should be used, When it should be used, How it should be used,
        and warnings about when not.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 736
    def lock(self):
        """[low-level] Lock the image without waiting for all the internal job queues are processed

        WARNING: Don't use it unless you really know what you are doing! Use barrierLock() instead!

        Waits for all the **currently running** internal jobs to complete and locks the image
        for writing. Please note that this function does **not** wait for all the internal
        queues to process, so there might be some non-finished actions pending. It means that
        you just postpone these actions until you unlock() the image back. Until then, then image
        might easily be frozen in some inconsistent state.

        The only sane usage for this function is to lock the image for **emergency**
        processing, when some internal action or scheduler got hung up, and you just want
        to fetch some data from the image without races.

        In all other cases, please use barrierLock() instead!
        @Implemented with: 4.0.0
        @Last updated with: 4.3.0
        """
        pass

    # Source location, line 799
    def modified(self) -> bool:
        """@brief modified returns true if the document has unsaved modifications.
        @Implemented with: 4.1.2
        """
        pass

    # Source location, line 286
    def name(self) -> str:
        """@return the name of the document. This is the title field in the @ref documentInfo
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 113
    def nodeByName(self, name: str) -> Node:
        """@brief nodeByName searches the node tree for a node with the given name and returns it
        @param name the name of the node
        @return the first node with the given name or 0 if no node is found
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 121
    def nodeByUniqueID(self, id: QUuid) -> Node:
        """@brief nodeByUniqueID searches the node tree for a node with the given name and returns it.
        @param uuid the unique id of the node
        @return the node with the given unique id, or 0 if no node is found.
        @Implemented with: 4.4.5
        """
        pass

    # Source location, line 409
    def pixelData(self, x: int, y: int, w: int, h: int) -> QByteArray:
        """@brief pixelData reads the given rectangle from the image projection and returns it as a byte
        array. The pixel data starts top-left, and is ordered row-first.

        The byte array can be interpreted as follows: 8 bits images have one byte per channel,
        and as many bytes as there are channels. 16 bits integer images have two bytes per channel,
        representing an unsigned short. 16 bits float images have two bytes per channel, representing
        a half, or 16 bits float. 32 bits float images have four bytes per channel, representing a
        float.

        You can read outside the image boundaries; those pixels will be transparent black.

        The order of channels is:

        <ul>
        <li>Integer RGBA: Blue, Green, Red, Alpha
        <li>Float RGBA: Red, Green, Blue, Alpha
        <li>LabA: L, a, b, Alpha
        <li>CMYKA: Cyan, Magenta, Yellow, Key, Alpha
        <li>XYZA: X, Y, Z, A
        <li>YCbCrA: Y, Cb, Cr, Alpha
        </ul>

        The byte array is a copy of the original image data. In Python, you can use bytes, bytearray
        and the struct module to interpret the data and construct, for instance, a Pillow Image object.

        @param x x position from where to start reading
        @param y y position from where to start reading
        @param w row length to read
        @param h number of rows to read
        @return a QByteArray with the pixel data. The byte array may be empty.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 881
    def playBackEndTime(self) -> int:
        """@brief get end time of current playback
        @return end time of current playback
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 875
    def playBackStartTime(self) -> int:
        """@brief get start time of current playback
        @return start time of current playback
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 707
    def projection(self, x: int = 0, y: int = 0, w: int = 0, h: int = 0) -> QImage:
        """@brief projection creates a QImage from the rendered image or
        a cutout rectangle.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 767
    def refreshProjection(self):
        """Starts a synchronous recomposition of the projection: everything will
        wait until the image is fully recomputed.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 927
    def removeAnnotation(self, type: str):
        """@brief removeAnnotation remove the specified annotation from the image
        @param type the type defining the annotation
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 486
    def resizeImage(self, x: int, y: int, w: int, h: int):
        """@brief resizeImage resizes the canvas to the given left edge, top edge, width and height.
        Note: This doesn't scale, use scale image for that.
        @param x the new left edge
        @param y the new top edge
        @param w the new width
        @param h the new height
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 296
    def resolution(self) -> int:
        """@return the resolution in pixels per inch
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 308
    def rootNode(self) -> Node:
        """@brief rootNode the root node is the invisible group layer that contains the entire node
        hierarchy.
        @return the root of the image
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 514
    def rotateImage(self, radians: float):
        """@brief rotateImage
        Rotate the image by the given radians.
        @param radians the amount you wish to rotate the image in radians
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 528
    def save(self) -> bool:
        """@brief save the image to its currently set path. The modified flag of the
        document will be reset
        @return true if saving succeeded, false otherwise.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 536
    def saveAs(self, filename: str) -> bool:
        """@brief saveAs save the document under the @p filename. The document's
        filename will be reset to @p filename.
        @param filename the new filename (full path) for the document
        @return true if saving succeeded, false otherwise.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 507
    def scaleImage(self, w: int, h: int, xres: int, yres: int, strategy: str):
        """@brief scaleImage
        @param w the new width
        @param h the new height
        @param xres the new xres
        @param yres the new yres
        @param strategy the scaling strategy. There's several ones amongst these that aren't available in the regular UI.
        The list of filters is extensible and can be retrieved with Krita::filter
        <ul>
        <li>Hermite</li>
        <li>Bicubic - Adds pixels using the color of surrounding pixels. Produces smoother tonal gradations than Bilinear.</li>
        <li>Box - Replicate pixels in the image. Preserves all the original detail, but can produce jagged effects.</li>
        <li>Bilinear - Adds pixels averaging the color values of surrounding pixels. Produces medium quality results when the image is scaled from half to two times the original size.</li>
        <li>Bell</li>
        <li>BSpline</li>
        <li>Kanczos3 - Offers similar results than Bicubic, but maybe a little bit sharper. Can produce light and dark halos along strong edges.</li>
        <li>Mitchell</li>
        </ul>
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 314
    def selection(self) -> Selection:
        """@brief selection Create a Selection object around the global selection, if there is one.
        @return the global selection or None if there is no global selection.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 101
    def setActiveNode(self, value: Node):
        """@brief setActiveNode make the given node active in the currently active view and window
        @param value the node to make active.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 921
    def setAnnotation(self, type: str, description: str, annotation: QByteArray):
        """@brief setAnnotation Add the given annotation to the document
        @param type the unique type of the annotation
        @param description the user-visible description of the annotation
        @param annotation the annotation itself
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 208
    def setBackGroundColor(self, color: QColor) -> bool:
        """@brief setBackGroundColor sets the background color of the document. It will trigger a projection
        update.

        @param color A QColor. The color will be converted from sRGB.
        @return bool
        @Implemented with: 4.0.2
        """
        pass

    # Source location, line 207
    def setBackgroundColor(self, color: QColor) -> bool:
        """@brief setBackgroundColor sets the background color of the document. It will trigger a projection
        update.

        @param color A QColor. The color will be converted from sRGB.
        @return bool
        @Implemented with: 4.0.3
        """
        pass

    # Source location, line 89
    def setBatchmode(self, value: bool):
        """Set batchmode to @p value. If batchmode is true, then there should be no popups
        or dialogs shown to the user.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 163
    def setColorProfile(self, colorProfile: str) -> bool:
        """@brief setColorProfile set the color profile of the image to the given profile. The profile has to
        be registered with krita and be compatible with the current color model and depth; the image data
        is <i>not</i> converted.
        @param colorProfile
        @return false if the colorProfile name does not correspond to to a registered profile or if assigning
        the profile failed.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 190
    def setColorSpace(self, colorModel: str, colorDepth: str, colorProfile: str) -> bool:
        """@brief setColorSpace convert the nodes and the image to the given colorspace. The conversion is
        done with Perceptual as intent, High Quality and No LCMS Optimizations as flags and no blackpoint
        compensation.

        @param colorModel A string describing the color model of the image:
        <ul>
        <li>A: Alpha mask</li>
        <li>RGBA: RGB with alpha channel (The actual order of channels is most often BGR!)</li>
        <li>XYZA: XYZ with alpha channel</li>
        <li>LABA: LAB with alpha channel</li>
        <li>CMYKA: CMYK with alpha channel</li>
        <li>GRAYA: Gray with alpha channel</li>
        <li>YCbCrA: YCbCr with alpha channel</li>
        </ul>
        @param colorDepth A string describing the color depth of the image:
        <ul>
        <li>U8: unsigned 8 bits integer, the most common type</li>
        <li>U16: unsigned 16 bits integer</li>
        <li>F16: half, 16 bits floating point. Only available if Krita was built with OpenEXR</li>
        <li>F32: 32 bits floating point</li>
        </ul>
        @param colorProfile a valid color profile for this color model and color depth combination.
        @return false the combination of these arguments does not correspond to a colorspace.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 892
    def setCurrentTime(self, time: int):
        """@brief set current time of document's animation
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 261
    def setDocumentInfo(self, document: str):
        """@brief setDocumentInfo set the Document information to the information contained in document
        @param document A string containing a valid XML document that conforms to the document-info DTD
        that can be found here:

        https://phabricator.kde.org/source/krita/browse/master/krita/dtd/
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 271
    def setFileName(self, value: str):
        """@brief setFileName set the full path of the document to @param value
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 835
    def setFramesPerSecond(self, fps: int):
        """@brief set frames per second of document
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 852
    def setFullClipRangeEndTime(self, endTime: int):
        """@brief set full clip range end time
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 840
    def setFullClipRangeStartTime(self, startTime: int):
        """@brief set start time of animation
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 794
    def setGuidesLocked(self, locked: bool):
        """@brief setGuidesLocked
        set guides locked on this document
        @param locked whether or not to lock the guides on this document.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 787
    def setGuidesVisible(self, visible: bool):
        """@brief setGuidesVisible
        set guides visible on this document.
        @param visible whether or not the guides are visible.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 281
    def setHeight(self, value: int):
        """@brief setHeight resize the document to @param value height. This is a canvas resize, not a scale.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 774
    def setHorizontalGuides(self, lines: list[float]):
        """@brief setHorizontalGuides
        replace all existing horizontal guides with the entries in the list.
        @param lines a list of floats containing the new guides.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 805
    def setModified(self, modified: bool):
        """@brief setModified sets the modified status of the document
        @param modified if true, the document is considered modified and closing it will ask for saving.
        @Implemented with: 5.1.2
        """
        pass

    # Source location, line 291
    def setName(self, value: str):
        """@brief setName sets the name of the document to @p value. This is the title field in the @ref documentInfo
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 869
    def setPlayBackRange(self, start: int, stop: int):
        """@brief set temporary playback range of document
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 301
    def setResolution(self, value: int):
        """@brief setResolution set the resolution of the image; this does not scale the image
        @param value the resolution in pixels per inch
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 320
    def setSelection(self, value: Selection):
        """@brief setSelection set or replace the global selection
        @param value a valid selection object.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 780
    def setVerticalGuides(self, lines: list[float]):
        """@brief setVerticalGuides
        replace all existing horizontal guides with the entries in the list.
        @param lines a list of floats containing the new guides.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 330
    def setWidth(self, value: int):
        """@brief setWidth resize the document to @param value width. This is a canvas resize, not a scale.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 340
    def setXOffset(self, x: int):
        """@brief setXOffset sets the left edge of the canvas to @p x.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 363
    def setXRes(self, xRes: float):
        """@brief setXRes set the horizontal resolution of the image to
        xRes in pixels per inch
        @Implemented with: 4.0.0
        @Last updated with: 4.2.8
        """
        pass

    # Source location, line 350
    def setYOffset(self, y: int):
        """@brief setYOffset sets the top edge of the canvas to @p y.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 375
    def setYRes(self, yRes: float):
        """@brief setYRes set the vertical resolution of the image to yRes
        in pixels per inch
        @Implemented with: 4.0.0
        @Last updated with: 4.2.8
        """
        pass

    # Source location, line 521
    def shearImage(self, angleX: float, angleY: float):
        """@brief shearImage shear the whole image.
        @param angleX the X-angle in degrees to shear by
        @param angleY the Y-angle in degrees to shear by
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 716
    def thumbnail(self, w: int, h: int) -> QImage:
        """@brief thumbnail create a thumbnail of the given dimensions.

        If the requested size is too big a null QImage is created.

        @return a QImage representing the layer contents.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 106
    def topLevelNodes(self) -> list[Node]:
        """@brief toplevelNodes return a list with all top level nodes in the image graph
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 761
    def tryBarrierLock(self) -> bool:
        """@brief Tries to lock the image without waiting for the jobs to finish

        Same as barrierLock(), but doesn't block execution of the calling thread
        until all the background jobs are finished. Instead, in case of presence of
        unfinished jobs in the queue, it just returns false

        @return whether the lock has been acquired
        @Implemented with: 4.0.0
        @Last updated with: 4.3.0
        """
        pass

    # Source location, line 743
    def unlock(self):
        """Unlocks the image and starts/resumes all the pending internal jobs. If the image
        has been locked for a non-readOnly access, then all the internal caches of the image
        (e.g. lod-planes) are reset and regeneration jobs are scheduled.
        @Implemented with: 4.0.0
        @Last updated with: 4.3.0
        """
        pass

    # Source location, line 56
    def verticalGuides(self) -> list[float]:
        """@brief verticalGuides
        The vertical guide lines.
        @return a list of vertical guides.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 750
    def waitForDone(self):
        """Wait for all the internal image jobs to complete and return without locking
        the image. This function is handy for tests or other synchronous actions,
        when one needs to wait for the result of his actions.
        @Implemented with: 4.0.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 325
    def width(self) -> int:
        """@return the width of the image in pixels.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 335
    def xOffset(self) -> int:
        """@return the left edge of the canvas in pixels.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 357
    def xRes(self) -> float:
        """@return xRes the horizontal resolution of the image in pixels
        per inch
        @Implemented with: 4.0.0
        @Last updated with: 4.2.8
        """
        pass

    # Source location, line 345
    def yOffset(self) -> int:
        """@return the top edge of the canvas in pixels.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 369
    def yRes(self) -> float:
        """@return yRes the vertical resolution of the image in pixels per
        inch
        @Implemented with: 4.0.0
        @Last updated with: 4.2.8
        """
        pass


# Source
# - File: Extension.h
# - Line: 49
class Extension(QObject):
    """An Extension is the base for classes that extend Krita. An Extension
    is loaded on startup, when the setup() method will be executed.

    The extension instance should be added to the Krita Application object
    using Krita.instance().addViewExtension or Application.addViewExtension
    or Scripter.addViewExtension.

    Example:

    @code
    import sys
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from krita import *
    class HelloExtension(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def hello(self):
        QMessageBox.information(QWidget(), "Test", "Hello! This is Krita " + Application.version())

    def setup(self):
        qDebug("Hello Setup")

    def createActions(self, window)
        action = window.createAction("hello")
        action.triggered.connect(self.hello)

    Scripter.addExtension(HelloExtension(Krita.instance()))

    @endcode

    @Implemented with: 4.0.0
    """
    # Source location, line 67
    def createActions(self, window: Window):
        """@Virtual
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 65
    def setup(self):
        """Override this function to setup your Extension. You can use it to integrate
        with the Krita application instance.
        @Virtual
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: FileLayer.h
# - Line: 26
class FileLayer(Node):
    """@brief The FileLayer class
    A file layer is a layer that can reference an external image
    and show said reference in the layer stack.

    If the external image is updated, Krita will try to update the
    file layer image as well.

    @Implemented with: 4.0.0
    @Updated with: 5.2.0
    """
    # Source location, line 71
    def path(self) -> str:
        """@brief path
        @return A QString with the full path of the referenced image.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 65
    def resetCache(self):
        """@brief makes the file layer to reload the connected image from disk
        @Implemented with: 4.1.2
        """
        pass

    # Source location, line 89
    def scalingFilter(self) -> str:
        """@brief scalingFilter
        returns the filter with which the file referenced is scaled.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 83
    def scalingMethod(self) -> str:
        """@brief scalingMethod
        returns how the file referenced is scaled.
        @return one of the following:
        <ul>
         <li> None - The file is not scaled in any way.
         <li> ToImageSize - The file is scaled to the full image size;
         <li> ToImagePPI - The file is scaled by the PPI of the image. This keep the physical dimensions the same.
        </ul>
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 60
    def setProperties(self, fileName: str, scalingMethod: str = "None", scalingFilter: str = "Bicubic"):
        """@brief setProperties
        Change the properties of the file layer.
        @param fileName - A String containing the absolute file name.
        @param scalingMethod - a string with the scaling method, defaults to "None",
         other options are "ToImageSize" and "ToImagePPI"
        @param scalingFilter - a string with the scaling filter, defaults to "Bicubic",
         other options are "Hermite", "NearestNeighbor", "Bilinear", "Bell", "BSpline", "Lanczos3", "Mitchell"
        @Implemented with: 4.0.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 49
    def type(self) -> str:
        """@brief type Krita has several types of nodes, split in layers and masks. Group
        layers can contain other layers, any layer can contain masks.

        @return "filelayer"
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: FillLayer.h
# - Line: 24
class FillLayer(Node):
    """@brief The FillLayer class
    A fill layer is much like a filter layer in that it takes a name
    and filter. It however specializes in filters that fill the whole canvas,
    such as a pattern or full color fill.

    @Implemented with: 4.0.0
    """
    # Source location, line 85
    def filterConfig(self) -> InfoObject:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 83
    def generatorName(self) -> str:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 82
    def setGenerator(self, generatorName: str, filterConfig: InfoObject) -> bool:
        """@brief setGenerator set the given generator for this fill layer
        @param generatorName "pattern" or "color"
        @param filterConfig a configuration object appropriate to the given generator plugin
        @return true if the generator was correctly created and set on the layer
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 74
    def type(self) -> str:
        """@brief type Krita has several types of nodes, split in layers and masks. Group
        layers can contain other layers, any layer can contain masks.

        @return The type of the node. Valid types are:
        <ul>
         <li>paintlayer
         <li>grouplayer
         <li>filelayer
         <li>filterlayer
         <li>filllayer
         <li>clonelayer
         <li>vectorlayer
         <li>transparencymask
         <li>filtermask
         <li>transformmask
         <li>selectionmask
         <li>colorizemask
        </ul>

        If the Node object isn't wrapping a valid Krita layer or mask object, and
        empty string is returned.
        @Virtual
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: Filter.h
# - Line: 30
class Filter(QObject):
    """Filter: represents a filter and its configuration. A filter is identified by
    an internal name. The configuration for each filter is defined as an InfoObject:
    a map of name and value pairs.

    Currently available filters are:

    'autocontrast', 'blur', 'bottom edge detections', 'brightnesscontrast', 'burn', 'colorbalance', 'colortoalpha', 'colortransfer',
    'desaturate', 'dodge', 'emboss', 'emboss all directions', 'emboss horizontal and vertical', 'emboss horizontal only',
    'emboss laplascian', 'emboss vertical only', 'gaussian blur', 'gaussiannoisereducer', 'gradientmap', 'halftone', 'hsvadjustment',
    'indexcolors', 'invert', 'left edge detections', 'lens blur', 'levels', 'maximize', 'mean removal', 'minimize', 'motion blur',
    'noise', 'normalize', 'oilpaint', 'perchannel', 'phongbumpmap', 'pixelize', 'posterize', 'raindrops', 'randompick',
    'right edge detections', 'roundcorners', 'sharpen', 'smalltiles', 'sobel', 'threshold', 'top edge detections', 'unsharp',
    'wave', 'waveletnoisereducer']

    @Implemented with: 4.0.0
    """
    # Source location, line 82
    def apply(self, node: Node, x: int, y: int, w: int, h: int) -> bool:
        """@brief Apply the filter to the given node.
        @param node the node to apply the filter to
        @param x
        @param y
        @param w
        @param h describe the rectangle the filter should be apply.
        This is always in image pixel coordinates and not relative to the x, y
        of the node.
        @return @c true if the filter was applied successfully, or
        @c false if the filter could not be applied because the node is locked or
        does not have an editable paint device.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 62
    def configuration(self) -> InfoObject:
        """@return the configuration object for the filter
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 52
    def name(self) -> str:
        """@brief name the internal name of this filter.
        @return the name.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 67
    def setConfiguration(self, value: InfoObject):
        """@brief setConfiguration set the configuration object for the filter
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 57
    def setName(self, name: str):
        """@brief setName set the filter's name to the given name.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 95
    def startFilter(self, node: Node, x: int, y: int, w: int, h: int) -> bool:
        """@brief startFilter starts the given filter on the given node.

        @param node the node to apply the filter to
        @param x
        @param y
        @param w
        @param h describe the rectangle the filter should be apply.
        This is always in image pixel coordinates and not relative to the x, y
        of the node.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass


# Source
# - File: FilterLayer.h
# - Line: 33
class FilterLayer(Node):
    """@brief The FilterLayer class
    A filter layer will, when compositing, take the composited
    image up to the point of the location of the filter layer
    in the stack, create a copy and apply a filter.

    This means you can use blending modes on the filter layers,
    which will be used to blend the filtered image with the original.

    Similarly, you can activate things like alpha inheritance, or
    you can set grayscale pixeldata on the filter layer to act as
    a mask.

    Filter layers can be animated.

    @Implemented with: 4.0.0
    """
    # Source location, line 54
    def filter(self) -> Filter:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 52
    def setFilter(self, filter: Filter):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 50
    def type(self) -> str:
        """@brief type Krita has several types of nodes, split in layers and masks. Group
        layers can contain other layers, any layer can contain masks.

        @return "filterlayer"
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: FilterMask.h
# - Line: 28
class FilterMask(Node):
    """@brief The FilterMask class
    A filter mask, unlike a filter layer, will add a non-destructive filter
    to the composited image of the node it is attached to.

    You can set grayscale pixeldata on the filter mask to adjust where the filter is applied.

    Filtermasks can be animated.

    @Implemented with: 4.0.0
    """
    # Source location, line 65
    def filter(self) -> Filter:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 64
    def setFilter(self, filter: Filter):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 62
    def type(self) -> str:
        """@brief type Krita has several types of nodes, split in layers and masks. Group
        layers can contain other layers, any layer can contain masks.

        @return The type of the node. Valid types are:
        <ul>
         <li>paintlayer
         <li>grouplayer
         <li>filelayer
         <li>filterlayer
         <li>filllayer
         <li>clonelayer
         <li>vectorlayer
         <li>transparencymask
         <li>filtermask
         <li>transformmask
         <li>selectionmask
         <li>colorizemask
        </ul>

        If the Node object isn't wrapping a valid Krita layer or mask object, and
        empty string is returned.
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: GroupLayer.h
# - Line: 29
class GroupLayer(Node):
    """@brief The GroupLayer class
    A group layer is a layer that can contain other layers.
    In Krita, layers within a group layer are composited
    first before they are added into the composition code for where
    the group is in the stack. This has a significant effect on how
    it is interpreted for blending modes.

    PassThrough changes this behaviour.

    Group layer cannot be animated, but can contain animated layers or masks.

    @Implemented with: 4.0.0
    """
    # Source location, line 66
    def passThroughMode(self) -> bool:
        """@brief passThroughMode
        @return returns whether or not this layer is in passthrough mode. @see setPassThroughMode
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 60
    def setPassThroughMode(self, passthrough: bool):
        """@brief setPassThroughMode
        This changes the way how compositing works.
        Instead of compositing all the layers before compositing it with the rest of the image,
        the group layer becomes a sort of formal way to organise everything.

        Passthrough mode is the same as it is in photoshop,
        and the inverse of SVG's isolation attribute(with passthrough=false being the same as
        isolation="isolate").

        @param passthrough whether or not to set the layer to passthrough.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 46
    def type(self) -> str:
        """@brief type Krita has several types of nodes, split in layers and masks. Group
        layers can contain other layers, any layer can contain masks.

        @return grouplayer
        @Virtual
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: GroupShape.h
# - Line: 20
class GroupShape(Shape):
    """@brief The GroupShape class
    A group shape is a vector object with child shapes.

    @Implemented with: 4.0.0
    """
    # Source location, line 40
    def children(self) -> list[Shape]:
        """@brief children
        @return the child shapes of this group shape.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 34
    def type(self) -> str:
        """@brief type returns the type.
        @return "groupshape"
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: InfoObject.h
# - Line: 19
class InfoObject(QObject):
    """InfoObject wrap a properties map. These maps can be used to set the
    configuration for filters.

    @Implemented with: 4.0.0
    """
    # Source location, line 37
    def properties(self) -> dict[str: QVariant]:
        """Return all properties this InfoObject manages.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 57
    def property(self, key: str) -> QVariant:
        """return the value for the property identified by key, or None if there is no such key.
        @Implemented with: 4.0.0
        @Last updated with: 4.0.1
        """
        pass

    # Source location, line 42
    def setProperties(self, propertyMap: dict[str: QVariant]):
        """Add all properties in the @p propertyMap to this InfoObject
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 52
    def setProperty(self, key: str, value: QVariant):
        """set the property identified by @p key to @p value

        If you want create a property that represents a color, you can use a QColor
        or hex string, as defined in https://doc.qt.io/qt-5/qcolor.html#setNamedColor.
        @Implemented with: 4.0.0
        @Last updated with: 4.3.0
        """
        pass


# Source
# - File: Krita.h
# - Line: 27
class Krita(QObject):
    """Krita is a singleton class that offers the root access to the Krita object hierarchy.

    The Krita.instance() is aliased as two builtins: Scripter and Application.

    @Implemented with: 4.0.0
    @Updated with: 5.1.0
    """
    @staticmethod
    # Source location, line 321
    def fromVariant(v: QVariant) -> QObject:
        """Internal only: for use with mikro.py
        @Implemented with: 4.0.0
        """
        pass

    @staticmethod
    # Source location, line 327
    def getAppDataLocation() -> str:
        """@Implemented with: 5.1.0"""
        pass

    @staticmethod
    # Source location, line 318
    def instance() -> Krita:
        """@brief instance retrieve the singleton instance of the Application object.
        @Implemented with: 4.0.0
        """
        pass

    @staticmethod
    # Source location, line 323
    def krita_i18n(text: str) -> str:
        """@Implemented with: 4.1.0"""
        pass

    @staticmethod
    # Source location, line 324
    def krita_i18nc(context: str, text: str) -> str:
        """@Implemented with: 4.4.0"""
        pass
    # Source location, line 74
    def action(self, name: str) -> QAction:
        """@return the action that has been registered under the given name, or 0 if no such action exists.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 69
    def actions(self) -> list[QAction]:
        """@return return a list of all actions for the currently active mainWindow.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 41
    def activeDocument(self) -> Document:
        """@return the currently active document, if there is one.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 179
    def activeWindow(self) -> Window:
        """@return the currently active window or None if there is no window
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 285
    def addDockWidgetFactory(self, factory: DockWidgetFactoryBase):
        """@brief addDockWidgetFactory Add the given docker factory to the application. For scripts
        loaded on startup, this means that every window will have one of the dockers created by the
        factory.
        @param factory The factory object.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 272
    def addExtension(self, extension: Extension):
        """@brief addExtension add the given plugin to Krita. There will be a single instance of each Extension in the Krita process.
        @param extension the extension to add.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 153
    def addProfile(self, profilePath: str) -> bool:
        """@brief addProfile load the given profile into the profile registry.
        @param profilePath the path to the profile.
        @return true if adding the profile succeeded.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 58
    def batchmode(self) -> bool:
        """@brief batchmode determines whether the script is run in batch mode. If batchmode
        is true, scripts should now show messageboxes or dialog boxes.

        Note that this separate from Document.setBatchmode(), which determines whether
        export/save option dialogs are shown.

        @return true if the script is run in batchmode
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 114
    def colorDepths(self, colorModel: str) -> list[str]:
        """@brief colorDepths creates a list with the names of all color depths
        compatible with the given color model.
        @param colorModel the id of a color model.
        @return a list of all color depths or a empty list if there is no such
        color depths.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 105
    def colorModels(self) -> list[str]:
        """@brief colorModels creates a list with all color models id's registered.
        @return a list of all color models or a empty list if there is no such color models.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 254
    def createDocument(self, width: int, height: int, name: str, colorModel: str, colorDepth: str, profile: str, resolution: float) -> Document:
        """@brief createDocument creates a new document and image and registers
        the document with the Krita application.

        Unless you explicitly call Document::close() the document will remain
        known to the Krita document registry. The document and its image will
        only be deleted when Krita exits.

        The document will have one transparent layer.

        To create a new document and show it, do something like:
        @code
        from Krita import *

        def add_document_to_window():
            d = Application.createDocument(100, 100, "Test", "RGBA", "U8", "", 120.0)
            Application.activeWindow().addView(d)

        add_document_to_window()
        @endcode

        @param width the width in pixels
        @param height the height in pixels
        @param name the name of the image (not the filename of the document)
        @param colorModel A string describing the color model of the image:
        <ul>
        <li>A: Alpha mask</li>
        <li>RGBA: RGB with alpha channel (The actual order of channels is most often BGR!)</li>
        <li>XYZA: XYZ with alpha channel</li>
        <li>LABA: LAB with alpha channel</li>
        <li>CMYKA: CMYK with alpha channel</li>
        <li>GRAYA: Gray with alpha channel</li>
        <li>YCbCrA: YCbCr with alpha channel</li>
        </ul>
        @param colorDepth A string describing the color depth of the image:
        <ul>
        <li>U8: unsigned 8 bits integer, the most common type</li>
        <li>U16: unsigned 16 bits integer</li>
        <li>F16: half, 16 bits floating point. Only available if Krita was built with OpenEXR</li>
        <li>F32: 32 bits floating point</li>
        </ul>
        @param profile The name of an icc profile that is known to Krita. If an empty string is passed, the default is
        taken.
        @param resolution the resolution in points per inch.
        @return the created document.
        @Implemented with: 4.0.0
        @Last updated with: 4.1.0
        """
        pass

    # Source location, line 84
    def dockers(self) -> list[QDockWidget]:
        """@return a list of all the dockers
        @Implemented with: 4.4.0
        """
        pass

    # Source location, line 79
    def documents(self) -> list[Document]:
        """@return a list of all open Documents
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 277
    def extensions(self) -> list[Extension]:
        """return a list with all registered extension objects.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 99
    def filter(self, name: str) -> Filter:
        """@brief filter construct a Filter object with a default configuration.
        @param name the name of the filter. Use Krita.instance().filters() to get
        a list of all possible filters.
        @return the filter or None if there is no such filter.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 122
    def filterStrategies(self) -> list[str]:
        """@brief filterStrategies Retrieves all installed filter strategies. A filter
        strategy is used when transforming (scaling, shearing, rotating) an image to
        calculate the value of the new pixels. You can use th
        @return the id's of all available filters.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 91
    def filters(self) -> list[str]:
        """@brief Filters are identified by an internal name. This function returns a list
        of all existing registered filters.
        @return a list of all registered filters
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 313
    def icon(self, iconName: str) -> QIcon:
        """@brief icon
        This allows you to get icons from Krita's internal icons.
        @param iconName name of the icon.
        @return the icon related to this name.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 160
    def notifier(self) -> Notifier:
        """@brief notifier the Notifier singleton emits signals when documents are opened and
        closed, the configuration changes, views are opened and closed or windows are opened.
        @return the notifier object
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 261
    def openDocument(self, filename: str) -> Document:
        """@brief openDocument creates a new Document, registers it with the Krita application and loads the given file.
        @param filename the file to open in the document
        @return the document
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 266
    def openWindow(self) -> Window:
        """@brief openWindow create a new main window. The window is not shown by default.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 146
    def profiles(self, colorModel: str, colorDepth: str) -> list[str]:
        """@brief profiles creates a list with the names of all color profiles compatible
        with the given color model and color depth.
        @param colorModel A string describing the color model of the image:
        <ul>
        <li>A: Alpha mask</li>
        <li>RGBA: RGB with alpha channel (The actual order of channels is most often BGR!)</li>
        <li>XYZA: XYZ with alpha channel</li>
        <li>LABA: LAB with alpha channel</li>
        <li>CMYKA: CMYK with alpha channel</li>
        <li>GRAYA: Gray with alpha channel</li>
        <li>YCbCrA: YCbCr with alpha channel</li>
        </ul>
        @param colorDepth A string describing the color depth of the image:
        <ul>
        <li>U8: unsigned 8 bits integer, the most common type</li>
        <li>U16: unsigned 16 bits integer</li>
        <li>F16: half, 16 bits floating point. Only available if Krita was built with OpenEXR</li>
        <li>F32: 32 bits floating point</li>
        </ul>
        @return a list with valid names
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 305
    def readSetting(self, group: str, name: str, defaultValue: str) -> str:
        """@brief readSetting read the given setting value from the kritarc file.
        @param group The group the setting is part of. If empty, then the setting is read from
        the general group.
        @param name The name of the setting
        @param defaultValue The default value of the setting
        @return a string representing the setting.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 205
    def recentDocuments(self) -> list[str]:
        """@brief return all recent documents registered in the RecentFiles group of the kritarc
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 199
    def resources(self, type: str) -> dict[str: Resource]:
        """@brief resources returns a list of Resource objects of the given type
        @param type Valid types are:

        <ul>
        <li>pattern</li>
        <li>gradient</li>
        <li>brush</li>
        <li>preset</li>
        <li>palette</li>
        <li>workspace</li>
        </ul>
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 47
    def setActiveDocument(self, value: Document):
        """@brief setActiveDocument activates the first view that shows the given document
        @param value the document we want to activate
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 64
    def setBatchmode(self, value: bool):
        """@brief setBatchmode sets the batchmode to @param value; if true, scripts should
        not show dialogs or messageboxes.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 169
    def version(self) -> str:
        """@brief version Determine the version of Krita

        Usage: print(Application.version ())

        @return the version string including git sha1 if Krita was built from git
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 174
    def views(self) -> list[View]:
        """@return a list of all views. A Document can be shown in more than one view.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 184
    def windows(self) -> list[Window]:
        """@return a list of all windows
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 295
    def writeSetting(self, group: str, name: str, value: str):
        """@brief writeSetting write the given setting under the given name to the kritarc file in
        the given settings group.
        @param group The group the setting belongs to. If empty, then the setting is written in the
        general section
        @param name The name of the setting
        @param value The value of the setting. Script settings are always written as strings.
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: ManagedColor.h
# - Line: 45
class ManagedColor(QObject):
    """@brief The ManagedColor class is a class to handle colors that are color managed.
    A managed color is a color of which we know the model(RGB, LAB, CMYK, etc), the bitdepth and
    the specific properties of its colorspace, such as the whitepoint, chromaticities, trc, etc, as represented
    by the color profile.

    Krita has two color management systems. LCMS and OCIO.
    LCMS is the one handling the ICC profile stuff, and the major one handling that ManagedColor deals with.
    OCIO support is only in the display of the colors. ManagedColor has some support for it in colorForCanvas()

    All colors in Krita are color managed. QColors are understood as RGB-type colors in the sRGB space.

    We recommend you make a color like this:

    @code
    colorYellow = ManagedColor("RGBA", "U8", "")
    QVector<float> yellowComponents = colorYellow.components()
    yellowComponents[0] = 1.0
    yellowComponents[1] = 1.0
    yellowComponents[2] = 0
    yellowComponents[3] = 1.0

    colorYellow.setComponents(yellowComponents)
    QColor yellow = colorYellow.colorForCanvas(canvas)
    @endcode

    @Implemented with: 4.0.0
    @Updated with: 4.3.0
    """
    @staticmethod
    # Source location, line 79
    def fromQColor(qcolor: QColor, canvas: Canvas = None) -> ManagedColor:
        """@brief fromQColor is the (approximate) reverse of colorForCanvas()
        @param qcolor the QColor to convert to a KoColor.
        @param canvas the canvas whose color management you'd like to use.
        @return the approximated ManagedColor, to use for canvas resources.
        @Implemented with: 4.3.0
        """
        pass
    # Source location, line 58
    def ManagedColor(self, colorModel: str, colorDepth: str, colorProfile: str, parent: QObject = None):
        """@brief ManagedColor create a managed color with the given color space properties.
        @see setColorModel() for more details.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 91
    def colorDepth(self) -> str:
        """colorDepth A string describing the color depth of the image:
        <ul>
        <li>U8: unsigned 8 bits integer, the most common type</li>
        <li>U16: unsigned 16 bits integer</li>
        <li>F16: half, 16 bits floating point. Only available if Krita was built with OpenEXR</li>
        <li>F32: 32 bits floating point</li>
        </ul>
        @return the color depth.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 71
    def colorForCanvas(self, canvas: Canvas) -> QColor:
        """@brief colorForCanvas
        @param canvas the canvas whose color management you'd like to use. In Krita, different views have
        separate canvasses, and these can have different OCIO configurations active.
        @return the QColor as it would be displaying on the canvas. This result can be used to draw widgets with
        the correct configuration applied.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 106
    def colorModel(self) -> str:
        """@brief colorModel retrieve the current color model of this document:
        <ul>
        <li>A: Alpha mask</li>
        <li>RGBA: RGB with alpha channel (The actual order of channels is most often BGR!)</li>
        <li>XYZA: XYZ with alpha channel</li>
        <li>LABA: LAB with alpha channel</li>
        <li>CMYKA: CMYK with alpha channel</li>
        <li>GRAYA: Gray with alpha channel</li>
        <li>YCbCrA: YCbCr with alpha channel</li>
        </ul>
        @return the internal color model string.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 111
    def colorProfile(self) -> str:
        """@return the name of the current color profile
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 154
    def components(self) -> list[float]:
        """@brief components
        @return a QVector containing the channel/components of this color normalized. This includes the alphachannel.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 160
    def componentsOrdered(self) -> list[float]:
        """@brief componentsOrdered()
        @return same as Components, except the values are ordered to the display.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 185
    def fromXML(self, xml: str):
        """Unserialize a color following Create's swatch color specification available
        at https://web.archive.org/web/20110826002520/http://create.freedesktop.org/wiki/Swatches_-_color_file_format/Draft

        @param xml an XML color

        @return the unserialized color, or an empty color object if the function failed
                to unserialize the color
        @Implemented with: 4.0.0
        @Last updated with: 5.1.0
        """
        pass

    # Source location, line 121
    def setColorProfile(self, colorProfile: str) -> bool:
        """@brief setColorProfile set the color profile of the image to the given profile. The profile has to
        be registered with krita and be compatible with the current color model and depth; the image data
        is <i>not</i> converted.
        @param colorProfile
        @return false if the colorProfile name does not correspond to to a registered profile or if assigning
        the profile failed.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 148
    def setColorSpace(self, colorModel: str, colorDepth: str, colorProfile: str) -> bool:
        """@brief setColorSpace convert the nodes and the image to the given colorspace. The conversion is
        done with Perceptual as intent, High Quality and No LCMS Optimizations as flags and no blackpoint
        compensation.

        @param colorModel A string describing the color model of the image:
        <ul>
        <li>A: Alpha mask</li>
        <li>RGBA: RGB with alpha channel (The actual order of channels is most often BGR!)</li>
        <li>XYZA: XYZ with alpha channel</li>
        <li>LABA: LAB with alpha channel</li>
        <li>CMYKA: CMYK with alpha channel</li>
        <li>GRAYA: Gray with alpha channel</li>
        <li>YCbCrA: YCbCr with alpha channel</li>
        </ul>
        @param colorDepth A string describing the color depth of the image:
        <ul>
        <li>U8: unsigned 8 bits integer, the most common type</li>
        <li>U16: unsigned 16 bits integer</li>
        <li>F16: half, 16 bits floating point. Only available if Krita was built with OpenEXR</li>
        <li>F32: 32 bits floating point</li>
        </ul>
        @param colorProfile a valid color profile for this color model and color depth combination.
        @return false the combination of these arguments does not correspond to a colorspace.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 168
    def setComponents(self, values: list[float]):
        """@brief setComponents
        Set the channel/components with normalized values. For integer colorspace, this obviously means the limit
        is between 0.0-1.0, but for floating point colorspaces, 2.4 or 103.5 are still meaningful (if bright) values.
        @param values the QVector containing the new channel/component values. These should be normalized.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 191
    def toQString(self) -> str:
        """@brief toQString create a user-visible string of the channel names and the channel values
        @return a string that can be used to display the values of this color to the user.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 174
    def toXML(self) -> str:
        """Serialize this color following Create's swatch color specification available
        at https://web.archive.org/web/20110826002520/http://create.freedesktop.org/wiki/Swatches_-_color_file_format/Draft
        @Implemented with: 4.0.0
        @Last updated with: 5.1.0
        """
        pass


# Source
# - File: Node.h
# - Line: 21
class Node(QObject):
    """Node represents a layer or mask in a Krita image's Node hierarchy. Group layers can contain
    other layers and masks; layers can contain masks.


    @Implemented with: 4.0.0
    @Updated with: 5.2.0
    """
    # Source location, line 97
    def addChildNode(self, child: Node, above: Node) -> bool:
        """@brief addChildNode adds the given node in the list of children.
        @param child the node to be added
        @param above the node above which this node will be placed
        @return false if adding the node failed
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 43
    def alphaLocked(self) -> bool:
        """@brief alphaLocked checks whether the node is a paint layer and returns whether it is alpha locked
        @return whether the paint layer is alpha locked, or false if the node is not a paint layer
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 181
    def animated(self) -> bool:
        """@brief Krita layers can be animated, i.e., have frames.
        @return return true if the layer has frames. Currently, the scripting framework
        does not give access to the animation features.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 53
    def blendingMode(self) -> str:
        """@return the blending mode of the layer. The values of the blending modes are defined in @see KoCompositeOpRegistry.h
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 452
    def bounds(self) -> QRect:
        """@brief bounds return the exact bounds of the node's paint device
        @return the bounds, or an empty QRect if the node has no paint device or is empty.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 71
    def channels(self) -> list[Channel]:
        """@brief channels creates a list of Channel objects that can be used individually to
        show or hide certain channels, and to retrieve the contents of each channel in a
        node separately.

        Only layers have channels, masks do not, and calling channels on a Node that is a mask
        will return an empty list.

        @return the list of channels ordered in by position of the channels in pixel position
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 78
    def childNodes(self) -> list[Node]:
        """@brief childNodes
        @return returns a list of child nodes of the current node. The nodes are ordered from the bottommost up.
        The function is not recursive.
        @Implemented with: 4.0.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 37
    def clone(self):
        """@brief clone clone the current node. The node is not associated with any image.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 207
    def collapsed(self) -> bool:
        """returns the collapsed state of this node
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 122
    def colorDepth(self) -> str:
        """colorDepth A string describing the color depth of the image:
        <ul>
        <li>U8: unsigned 8 bits integer, the most common type</li>
        <li>U16: unsigned 16 bits integer</li>
        <li>F16: half, 16 bits floating point. Only available if Krita was built with OpenEXR</li>
        <li>F32: 32 bits floating point</li>
        </ul>
        @return the color depth.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 214
    def colorLabel(self) -> int:
        """Sets a color label index associated to the layer.  The actual
        color of the label and the number of available colors is
        defined by Krita GUI configuration.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 137
    def colorModel(self) -> str:
        """@brief colorModel retrieve the current color model of this document:
        <ul>
        <li>A: Alpha mask</li>
        <li>RGBA: RGB with alpha channel (The actual order of channels is most often BGR!)</li>
        <li>XYZA: XYZ with alpha channel</li>
        <li>LABA: LAB with alpha channel</li>
        <li>CMYKA: CMYK with alpha channel</li>
        <li>GRAYA: Gray with alpha channel</li>
        <li>YCbCrA: YCbCr with alpha channel</li>
        </ul>
        @return the internal color model string.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 142
    def colorProfile(self) -> str:
        """@return the name of the current color profile
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 530
    def cropNode(self, x: int, y: int, w: int, h: int):
        """@brief cropNode crop this layer.
        @param x the left edge of the cropping rectangle.
        @param y the top edge of the cropping rectangle
        @param w the right edge of the cropping rectangle
        @param h the bottom edge of the cropping rectangle
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 476
    def duplicate(self):
        """@brief duplicate returns a full copy of the current node. The node is not inserted in the graphic
        @return a valid Node object or 0 if the node couldn't be duplicated.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 186
    def enableAnimation(self):
        """@brief enableAnimation make the current layer animated, so it can have frames.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 89
    def findChildNodes(self, name: str = "", recursive: bool = False, partialMatch: bool = False, type: str = "", colorLabelIndex: int = 0) -> list[Node]:
        """@brief findChildNodes
        @param name name of the child node to search for. Leaving this blank will return all nodes.
        @param recursive whether or not to search recursively. Defaults to false.
        @param partialMatch return if the name partially contains the string (case insensitive). Defaults to false.
        @param type filter returned nodes based on type
        @param colorLabelIndex filter returned nodes based on color label index
        @return returns a list of child nodes and grand child nodes of the current node that match the search criteria.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 250
    def hasExtents(self) -> bool:
        """@brief does the node have any content in it?
        @return if node has any content in it
        @Implemented with: 4.1.0
        """
        pass

    # Source location, line 317
    def hasKeyframeAtTime(self, frameNumber: int) -> bool:
        """Check to see if frame number on layer is a keyframe
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 307
    def icon(self) -> QIcon:
        """@brief icon
        @return the icon associated with the layer.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 565
    def index(self) -> int:
        """@brief index the index of the node inside the parent
        @return an integer representing the node's index inside the parent
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 228
    def inheritAlpha(self) -> bool:
        """@brief inheritAlpha checks whether this node has the inherits alpha flag set
        @return true if the Inherit Alpha is set
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 197
    def isPinnedToTimeline(self) -> bool:
        """@return Returns true if node is pinned to the Timeline Docker or false if it is not.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 552
    def layerStyleToAsl(self) -> str:
        """@brief layerStyleToAsl retrieve the current layer's style in ASL format.
        @return a QString in ASL format representing the layer style.
        @Implemented with: 5.0.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 239
    def locked(self) -> bool:
        """@brief locked checks whether the Node is locked. A locked node cannot be changed.
        @return true if the Node is locked, false if it hasn't been locked.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 496
    def mergeDown(self):
        """@brief mergeDown merges the given node with the first visible node underneath this node in the layerstack.
        This will drop all per-layer metadata.
        @Implemented with: 4.0.0
        @Last updated with: 4.1.2
        """
        pass

    # Source location, line 457
    def move(self, x: int, y: int):
        """ move the pixels to the given x, y location in the image coordinate space.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 256
    def name(self) -> str:
        """@return the user-visible name of this node.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 266
    def opacity(self) -> int:
        """return the opacity of the Node. The opacity is a value between 0 and 255.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 276
    def parentNode(self):
        """return the Node that is the parent of the current Node, or 0 if this is the root Node.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 366
    def pixelData(self, x: int, y: int, w: int, h: int) -> QByteArray:
        """@brief pixelData reads the given rectangle from the Node's paintable pixels, if those
        exist, and returns it as a byte array. The pixel data starts top-left, and is ordered row-first.

        The byte array can be interpreted as follows: 8 bits images have one byte per channel,
        and as many bytes as there are channels. 16 bits integer images have two bytes per channel,
        representing an unsigned short. 16 bits float images have two bytes per channel, representing
        a half, or 16 bits float. 32 bits float images have four bytes per channel, representing a
        float.

        You can read outside the node boundaries; those pixels will be transparent black.

        The order of channels is:

        <ul>
        <li>Integer RGBA: Blue, Green, Red, Alpha
        <li>Float RGBA: Red, Green, Blue, Alpha
        <li>GrayA: Gray, Alpha
        <li>Selection: selectedness
        <li>LabA: L, a, b, Alpha
        <li>CMYKA: Cyan, Magenta, Yellow, Key, Alpha
        <li>XYZA: X, Y, Z, A
        <li>YCbCrA: Y, Cb, Cr, Alpha
        </ul>

        The byte array is a copy of the original node data. In Python, you can use bytes, bytearray
        and the struct module to interpret the data and construct, for instance, a Pillow Image object.

        If you read the pixeldata of a mask, a filter or generator layer, you get the selection bytes,
        which is one channel with values in the range from 0..255.

        If you want to change the pixels of a node you can write the pixels back after manipulation
        with setPixelData(). This will only succeed on nodes with writable pixel data, e.g not on groups
        or file layers.

        @param x x position from where to start reading
        @param y y position from where to start reading
        @param w row length to read
        @param h number of rows to read
        @return a QByteArray with the pixel data. The byte array may be empty.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 377
    def pixelDataAtTime(self, x: int, y: int, w: int, h: int, time: int) -> QByteArray:
        """@brief pixelDataAtTime a basic function to get pixeldata from an animated node at a given time.
        @param x the position from the left to start reading.
        @param y the position from the top to start reader
        @param w the row length to read
        @param h the number of rows to read
        @param time the frame number
        @return a QByteArray with the pixel data. The byte array may be empty.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 465
    def position(self) -> QPoint:
        """@brief position returns the position of the paint device of this node. The position is
        always 0,0 unless the layer has been moved. If you want to know the topleft position of
        the rectangle around the actual non-transparent pixels in the node, use bounds().
        @return the top-left position of the node
        @Implemented with: 4.0.0
        @Last updated with: 4.1.2
        """
        pass

    # Source location, line 421
    def projectionPixelData(self, x: int, y: int, w: int, h: int) -> QByteArray:
        """@brief projectionPixelData reads the given rectangle from the Node's projection (that is, what the node
        looks like after all sub-Nodes (like layers in a group or masks on a layer) have been applied,
        and returns it as a byte array. The pixel data starts top-left, and is ordered row-first.

        The byte array can be interpreted as follows: 8 bits images have one byte per channel,
        and as many bytes as there are channels. 16 bits integer images have two bytes per channel,
        representing an unsigned short. 16 bits float images have two bytes per channel, representing
        a half, or 16 bits float. 32 bits float images have four bytes per channel, representing a
        float.

        You can read outside the node boundaries; those pixels will be transparent black.

        The order of channels is:

        <ul>
        <li>Integer RGBA: Blue, Green, Red, Alpha
        <li>Float RGBA: Red, Green, Blue, Alpha
        <li>GrayA: Gray, Alpha
        <li>Selection: selectedness
        <li>LabA: L, a, b, Alpha
        <li>CMYKA: Cyan, Magenta, Yellow, Key, Alpha
        <li>XYZA: X, Y, Z, A
        <li>YCbCrA: Y, Cb, Cr, Alpha
        </ul>

        The byte array is a copy of the original node data. In Python, you can use bytes, bytearray
        and the struct module to interpret the data and construct, for instance, a Pillow Image object.

        If you read the projection of a mask, you get the selection bytes, which is one channel with
        values in the range from 0..255.

        If you want to change the pixels of a node you can write the pixels back after manipulation
        with setPixelData(). This will only succeed on nodes with writable pixel data, e.g not on groups
        or file layers.

        @param x x position from where to start reading
        @param y y position from where to start reading
        @param w row length to read
        @param h number of rows to read
        @return a QByteArray with the pixel data. The byte array may be empty.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 470
    def remove(self) -> bool:
        """@brief remove removes this node from its parent image.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 103
    def removeChildNode(self, child: Node) -> bool:
        """@brief removeChildNode removes the given node from the list of children.
        @param child the node to be removed
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 521
    def rotateNode(self, radians: float):
        """@brief rotateNode rotate this layer by the given radians.
        @param radians amount the layer should be rotated in, in radians.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 490
    def save(self, filename: str, xRes: float, yRes: float, exportConfiguration: InfoObject, exportRect: QRect = QRect()) -> bool:
        """@brief save exports the given node with this filename. The extension of the filename determines the filetype.
        @param filename the filename including extension
        @param xRes the horizontal resolution in pixels per pt (there are 72 pts in an inch)
        @param yRes the horizontal resolution in pixels per pt (there are 72 pts in an inch)
        @param exportConfiguration a configuration object appropriate to the file format.
        @param exportRect the export bounds for saving a node as a QRect
        If \p exportRect is empty, then save exactBounds() of the node. If you'd like to save the image-
        aligned area of the node, just pass image->bounds() there.
        See Document->exportImage for InfoObject details.
        @return true if saving succeeded, false if it failed.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 515
    def scaleNode(self, origin: QPointF, width: int, height: int, strategy: str):
        """@brief scaleNode
        @param origin the origin point
        @param width the width
        @param height the height
        @param strategy the scaling strategy. There's several ones amongst these that aren't available in the regular UI.
        <ul>
        <li>Hermite</li>
        <li>Bicubic - Adds pixels using the color of surrounding pixels. Produces smoother tonal gradations than Bilinear.</li>
        <li>Box - Replicate pixels in the image. Preserves all the original detail, but can produce jagged effects.</li>
        <li>Bilinear - Adds pixels averaging the color values of surrounding pixels. Produces medium quality results when the image is scaled from half to two times the original size.</li>
        <li>Bell</li>
        <li>BSpline</li>
        <li>Lanczos3 - Offers similar results than Bicubic, but maybe a little bit sharper. Can produce light and dark halos along strong edges.</li>
        <li>Mitchell</li>
        </ul>
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 48
    def setAlphaLocked(self, value: bool):
        """@brief setAlphaLocked set the layer to value if the node is paint layer.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 59
    def setBlendingMode(self, value: str):
        """@brief setBlendingMode set the blending mode of the node to the given value
        @param value one of the string values from @see KoCompositeOpRegistry.h
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 110
    def setChildNodes(self, nodes: list[Node]):
        """@brief setChildNodes this replaces the existing set of child nodes with the new set.
        @param nodes The list of nodes that will become children, bottom-up -- the first node,
        is the bottom-most node in the stack.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 202
    def setCollapsed(self, collapsed: bool):
        """Sets the state of the node to the value of @param collapsed
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 222
    def setColorLabel(self, index: int):
        """@brief setColorLabel sets a color label index associated to the layer.  The actual
        color of the label and the number of available colors is
        defined by Krita GUI configuration.
        @param index an integer corresponding to the set of available color labels.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 151
    def setColorProfile(self, colorProfile: str) -> bool:
        """@brief setColorProfile set the color profile of the image to the given profile. The profile has to
        be registered with krita and be compatible with the current color model and depth; the image data
        is <i>not</i> converted.
        @param colorProfile
        @return if assigning the color profile worked
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 174
    def setColorSpace(self, colorModel: str, colorDepth: str, colorProfile: str) -> bool:
        """@brief setColorSpace convert the node to the given colorspace
        @param colorModel A string describing the color model of the node:
        <ul>
        <li>A: Alpha mask</li>
        <li>RGBA: RGB with alpha channel (The actual order of channels is most often BGR!)</li>
        <li>XYZA: XYZ with alpha channel</li>
        <li>LABA: LAB with alpha channel</li>
        <li>CMYKA: CMYK with alpha channel</li>
        <li>GRAYA: Gray with alpha channel</li>
        <li>YCbCrA: YCbCr with alpha channel</li>
        </ul>
        @param colorDepth A string describing the color depth of the image:
        <ul>
        <li>U8: unsigned 8 bits integer, the most common type</li>
        <li>U16: unsigned 16 bits integer</li>
        <li>F16: half, 16 bits floating point. Only available if Krita was built with OpenEXR</li>
        <li>F32: 32 bits floating point</li>
        </ul>
        @param colorProfile a valid color profile for this color model and color depth combination.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 233
    def setInheritAlpha(self, value: bool):
        """set the Inherit Alpha flag to the given value
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 559
    def setLayerStyleFromAsl(self, asl: str) -> bool:
        """@brief setLayerStyleFromAsl set a new layer style for this node.
        @param aslContent a string formatted in ASL format containing the layer style
        @return true if layer style was set, false if failed.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 244
    def setLocked(self, value: bool):
        """set the Locked flag to the give value
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 261
    def setName(self, name: str):
        """rename the Node to the given name
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 271
    def setOpacity(self, value: int):
        """set the opacity of the Node to the given value. The opacity is a value between 0 and 255.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 192
    def setPinnedToTimeline(self, pinned: bool):
        """@brief Sets whether or not node should be pinned to the Timeline Docker,
        regardless of selection activity.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 446
    def setPixelData(self, value: QByteArray, x: int, y: int, w: int, h: int) -> bool:
        """@brief setPixelData writes the given bytes, of which there must be enough, into the
        Node, if the Node has writable pixel data:

        <ul>
        <li>paint layer: the layer's original pixels are overwritten
        <li>filter layer, generator layer, any mask: the embedded selection's pixels are overwritten.
        <b>Note:</b> for these
        </ul>

        File layers, Group layers, Clone layers cannot be written to. Calling setPixelData on
        those layer types will silently do nothing.

        @param value the byte array representing the pixels. There must be enough bytes available.
        Krita will take the raw pointer from the QByteArray and start reading, not stopping before
        (number of channels * size of channel * w * h) bytes are read.

        @param x the x position to start writing from
        @param y the y position to start writing from
        @param w the width of each row
        @param h the number of rows to write
        @return true if writing the pixeldata worked
        @Implemented with: 4.0.0
        @Last updated with: 5.0.0
        """
        pass

    # Source location, line 192
    def setShowInTimeline(self, showInTimeline: bool):
        """@brief Should the node be visible in the timeline. It defaults to false
        with new layer
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 322
    def setVisible(self, visible: bool):
        """Set the visibility of the current node to @param visible
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 537
    def shearNode(self, angleX: float, angleY: float):
        """@brief shearNode perform a shear operation on this node.
        @param angleX the X-angle in degrees to shear by
        @param angleY the Y-angle in degrees to shear by
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 197
    def showInTimeline(self) -> bool:
        """@return is layer is shown in the timeline
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 546
    def thumbnail(self, w: int, h: int) -> QImage:
        """@brief thumbnail create a thumbnail of the given dimensions. The thumbnail is sized according
        to the layer dimensions, not the image dimensions. If the requested size is too big a null
        QImage is created. If the current node cannot generate a thumbnail, a transparent QImage of the
        requested size is generated.
        @return a QImage representing the layer contents.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 301
    def type(self) -> str:
        """@brief type Krita has several types of nodes, split in layers and masks. Group
        layers can contain other layers, any layer can contain masks.

        @return The type of the node. Valid types are:
        <ul>
         <li>paintlayer
         <li>grouplayer
         <li>filelayer
         <li>filterlayer
         <li>filllayer
         <li>clonelayer
         <li>vectorlayer
         <li>transparencymask
         <li>filtermask
         <li>transformmask
         <li>selectionmask
         <li>colorizemask
        </ul>

        If the Node object isn't wrapping a valid Krita layer or mask object, and
        empty string is returned.
        @Virtual
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 571
    def uniqueId(self) -> QUuid:
        """@brief uniqueId uniqueId of the node
        @return a QUuid representing a unique id to identify the node
        @Implemented with: 4.4.5
        @Last updated with: 5.0.0
        """
        pass

    # Source location, line 312
    def visible(self) -> bool:
        """Check whether the current Node is visible in the layer stack
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: Notifier.h
# - Line: 22
class Notifier(QObject):
    """The Notifier can be used to be informed of state changes in the Krita application.

    @Implemented with: 4.0.0
    @Updated with: 4.3.0
    """
    # @brief applicationClosing is emitted when the application is about to close. This
    # happens after any documents and windows are closed.
    # @Implemented with: 4.0.0
    applicationClosing = pyqtSignal()

    # @brief configurationChanged is emitted every time Krita's configuration
    # has changed.
    # @Implemented with: 4.0.0
    configurationChanged = pyqtSignal()

    # @brief imageClosed is emitted whenever the last view on an image is closed. The image
    # does not exist anymore in Krita
    # @param filename the filename of the image.
    # @Implemented with: 4.0.0
    imageClosed = pyqtSignal(str)

    # @brief imageCreated is emitted whenever a new image is created and registered with
    # the application.
    # @Implemented with: 4.0.0
    imageCreated = pyqtSignal(Document)

    # @brief imageSaved is emitted whenever a document is saved.
    # @param filename the filename of the document that has been saved.
    # @Implemented with: 4.0.0
    imageSaved = pyqtSignal(str)

    # @brief viewClosed is emitted whenever a view is closed
    # @param view the view
    # @Implemented with: 4.0.0
    viewClosed = pyqtSignal(View)

    # @brief viewCreated is emitted whenever a new view is created.
    # @param view the view
    # @Implemented with: 4.0.0
    viewCreated = pyqtSignal(View)

    # @brief windowIsCreated is emitted after main window is completely created
    # @Implemented with: 4.0.0
    # @Last updated with: 5.0.0
    windowCreated = pyqtSignal()

    # @brief windowCreated is emitted whenever a window is being created
    # @param window the window; this is called from the constructor of the window, before the xmlgui file is loaded
    # @Implemented with: 4.3.0
    windowIsBeingCreated = pyqtSignal(Window)
    # Source location, line 36
    def active(self) -> bool:
        """@return true if the Notifier is active.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 41
    def setActive(self, value: bool):
        """Enable or disable the Notifier
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: Palette.h
# - Line: 45
class Palette(QObject):
    """@brief The Palette class
    Palette is a resource object that stores organised color data.
    It's purpose is to allow artists to save colors and store them.

    An example for printing all the palettes and the entries:

    @code
    import sys
    from krita import *

    resources = Application.resources("palette")

    for (k, v) in resources.items():
        print(k)
        palette = Palette(v)
        for x in range(palette.numberOfEntries()):
            entry = palette.colorSetEntryByIndex(x)
            c = palette.colorForEntry(entry);
            print(x, entry.name(), entry.id(), entry.spotColor(), c.toQString())
    @endcode

    @Implemented with: 4.0.0
    @Updated with: 4.2.0
    """
    # Source location, line 48
    def Palette(self, resource: Resource):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 124
    def addEntry(self, entry: Swatch, groupName: str = ""):
        """@brief addEntry
        add an entry to a group. Gets appended to the end.
        @param entry the entry
        @param groupName the name of the group to add to.
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 88
    def addGroup(self, name: str):
        """@brief addGroup
        @param name of the new group
        @return whether adding the group was successful.
        @Implemented with: 4.0.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 138
    def changeGroupName(self, oldGroupName: str, newGroupName: str):
        """@brief changeGroupName
        change the group name.
        @param oldGroupName the old groupname to change.
        @param newGroupName the new name to change it into.
        @return whether successful. Reasons for failure include not knowing have oldGroupName
        @Implemented with: 4.0.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 109
    def colorSetEntryByIndex(self, index: int) -> Swatch:
        """@brief colorSetEntryByIndex
        get the colorsetEntry from the global index.
        @param index the global index
        @return the colorset entry
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 116
    def colorSetEntryFromGroup(self, index: int, groupName: str) -> Swatch:
        """@brief colorSetEntryFromGroup
        @param index index in the group.
        @param groupName the name of the group to get the color from.
        @return the colorsetentry.
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 116
    def colorsCountGroup(self, name: str) -> int:
        """@brief colorsCountGroup
        @param name of the group to check. Empty is the default group.
        @return the amount of colors within that group.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 101
    def colorsCountTotal(self) -> int:
        """@brief colorsCountTotal
        @return the total amount of entries in the whole group
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 61
    def columnCount(self) -> int:
        """@brief columnCount
        @return the amount of columns this palette is set to use.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 71
    def comment(self) -> str:
        """@brief comment
        @return the comment or description associated with the palette.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 82
    def groupNames(self) -> list[str]:
        """@brief groupNames
        @return the list of group names. This is list is in the order these groups are in the file.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 146
    def moveGroup(self, groupName: str, groupNameInsertBefore: str = ""):
        """@brief moveGroup
        move the group to before groupNameInsertBefore.
        @param groupName group to move.
        @param groupNameInsertBefore group to inset before.
        @return whether successful. Reasons for failure include either group not existing.
        @Implemented with: 4.0.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 55
    def numberOfEntries(self) -> int:
        """@brief numberOfEntries
        @return
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 129
    def removeEntry(self, index: int, groupName: str):
        """@brief removeEntry
        remove the entry at @p index from the group @p groupName.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 95
    def removeGroup(self, name: str, keepColors: bool = True):
        """@brief removeGroup
        @param name the name of the group to remove.
        @param keepColors whether or not to delete all the colors inside, or to move them to the default group.
        @return
        @Implemented with: 4.0.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 153
    def save(self) -> bool:
        """@brief save
        save the palette
        @return whether it was successful.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 66
    def setColumnCount(self, columns: int):
        """@brief setColumnCount
        Set the amount of columns this palette should use.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 77
    def setComment(self, comment: str):
        """@brief setComment
        set the comment or description associated with the palette.
        @param comment
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: PaletteView.h
# - Line: 31
class PaletteView(QWidget):
    """@class PaletteView
    @brief The PaletteView class is a wrapper around a MVC method for handling
    palettes. This class shows a nice widget that can drag and drop, edit colors in a colorset
    and will handle adding and removing entries if you'd like it to.

    @Implemented with: 4.0.0
    @Updated with: 4.2.0
    """
    # @brief entrySelectedBackGround
    # fires when a swatch is selected with rightclick.
    # @param entry
    # @Implemented with: 4.2.0
    entrySelectedBackGround = pyqtSignal(Swatch)

    # @brief entrySelectedForeGround
    # fires when a swatch is selected with leftclick.
    # @param entry
    # @Implemented with: 4.2.0
    entrySelectedForeGround = pyqtSignal(Swatch)
    # Source location, line 35
    def PaletteView(self, parent: QWidget = None):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 51
    def addEntryWithDialog(self, color: ManagedColor) -> bool:
        """@brief addEntryWithDialog
        This gives a simple dialog for adding colors, with options like
        adding name, id, and to which group the color should be added.
        @param color the default color to add
        @return whether it was successful.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 57
    def addGroupWithDialog(self) -> bool:
        """@brief addGroupWithDialog
        gives a little dialog to ask for the desired groupname.
        @return whether this was successful.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 64
    def removeSelectedEntryWithDialog(self) -> bool:
        """@brief removeSelectedEntryWithDialog
        removes the selected entry. If it is a group, it pop up a dialog
        asking whether the colors should also be removed.
        @return whether this was successful
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 43
    def setPalette(self, palette: Palette):
        """@brief setPalette
        Set a new palette.
        @param palette
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 71
    def trySelectClosestColor(self, color: ManagedColor):
        """@brief trySelectClosestColor
        tries to select the closest color to the one given.
        It does not force a change on the active color.
        @param color the color to compare to.
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: Preset.h
# - Line: 34
class Preset(QObject):
    """@brief The Preset class
    Preset is a resource object that stores brush preset data.

    An example for printing the current brush preset and all its settings:

    @code
    from krita import *

    view = Krita.instance().activeWindow().activeView()
    preset = Preset(view.currentBrushPreset())

    print ( preset.toXML() )
    @endcode

    @Implemented with: 5.2.0
    """
    # Source location, line 37
    def Preset(self, resource: Resource):
        """@Implemented with: 5.2.0"""
        pass

    # Source location, line 52
    def fromXML(self, xml: str):
        """@brief fromXML
        convert the preset settings into a preset formatted xml.
        @param xml valid xml preset string.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 45
    def toXML(self) -> str:
        """@brief toXML
        convert the preset settings into a preset formatted xml.
        @return the xml in a string.
        @Implemented with: 5.2.0
        """
        pass


# Source
# - File: PresetChooser.h
# - Line: 25
class PresetChooser:
    """@brief The PresetChooser widget wraps the KisPresetChooser widget.
    The widget provides for selecting brush presets. It has a tagging
    bar and a filter field. It is not automatically synchronized with 
    the currently selected preset in the current Windows.

    @Implemented with: 4.0.0
    """
    # Emitted whenever a user clicks on the given preset.
    # @Implemented with: 4.0.0
    presetClicked = pyqtSignal(Resource)

    # Emitted whenever a user selects the given preset.
    # @Implemented with: 4.0.0
    presetSelected = pyqtSignal(Resource)
    # Source location, line 29
    def PresetChooser(self, parent: QWidget = None):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 43
    def currentPreset(self) -> Resource:
        """@return a Resource wrapper around the currently selected
        preset. 
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: Resource.h
# - Line: 30
class Resource(QObject):
    """A Resource represents a gradient, pattern, brush tip, brush preset, palette or 
    workspace definition.

    @code
    allPresets = Application.resources("preset")
    for preset in allPresets:
        print(preset.name())
    @endcode

    Resources are identified by their type, name and filename. If you want to change
    the contents of a resource, you should read its data using data(), parse it and
    write the changed contents back.

    @Implemented with: 4.0.0
    @Updated with: 5.0.0
    """
    # Source location, line 38
    def Resource(self, rhs: Resource):
        """@Implemented with: 5.0.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 100
    def data(self) -> QByteArray:
        """Return the resource as a byte array.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 74
    def filename(self) -> str:
        """The filename of the resource, if present. Not all resources
        are loaded from files.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 82
    def image(self) -> QImage:
        """An image that can be used to represent the resource in the
        user interface. For some resources, like patterns, the 
        image is identical to the resource, for others it's a mere
        icon.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 63
    def name(self) -> str:
        """The user-visible name of the resource.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 107
    def setData(self, data: QByteArray) -> bool:
        """Change the internal data of the resource to the given byte 
        array. If the byte array is not valid, setData returns
        false, otherwise true.
        @Implemented with: 4.0.0
        @Last updated with: 4.3.0
        """
        pass

    # Source location, line 87
    def setImage(self, image: QImage):
        """Change the image for this resource.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 68
    def setName(self, value: str):
        """setName changes the user-visible name of the current resource.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 58
    def type(self) -> str:
        """Return the type of this resource. Valid types are:
        <ul>
        <li>pattern: a raster image representing a pattern
        <li>gradient: a gradient
        <li>brush: a brush tip
        <li>preset: a brush preset
        <li>palette: a color set
        <li>workspace: a workspace definition.
        </ul>
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: Scratchpad.h
# - Line: 27
class Scratchpad(QWidget):
    """@brief The Scratchpad class
    A scratchpad is a type of blank canvas area that can be painted on 
    with the normal painting devices


    @Implemented with: 4.4.0
    """
    # Source location, line 31
    def Scratchpad(self, view: View, defaultColor: QColor, parent: QWidget = None):
        """@Implemented with: 4.4.0"""
        pass

    # Source location, line 39
    def clear(self):
        """@brief Clears out scratchpad with color specified set during setup
        @Implemented with: 4.4.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 77
    def copyScratchpadImageData(self) -> QImage:
        """@brief Take what is on the scratchpad area and grab image
        @return the image data from the scratchpad
        @Implemented with: 4.4.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 64
    def linkCanvasZoom(self, value: bool):
        """@brief Makes a connection between the zoom of the canvas and scratchpad area so they zoom in sync
        @param Should the scratchpad share the zoom level. Default is true
        @Implemented with: 4.4.0
        @Last updated with: 5.0.0
        """
        pass

    # Source location, line 71
    def loadScratchpadImage(self, image: QImage):
        """@brief Load image data to the scratchpad
        @param Image object to load
        @Implemented with: 4.4.0
        @Last updated with: 5.0.0
        """
        pass

    # Source location, line 45
    def setFillColor(self, color: QColor):
        """@brief Fill the entire scratchpad with a color
        @param Color to fill the canvas with
        @Implemented with: 4.4.0
        @Last updated with: 5.0.0
        """
        pass

    # Source location, line 58
    def setMode(self, modeName: str):
        """@brief Manually set what mode scratchpad is in. Ignored if "setModeManually is set to false
        @param Available options are: "painting", "panning", and "colorsampling"
        @Implemented with: 4.4.0
        @Last updated with: 5.0.0
        """
        pass

    # Source location, line 51
    def setModeManually(self, value: bool):
        """@brief Switches between a GUI controlling the current mode and when mouse clicks control mode
        @param Setting to true allows GUI to control the mode with explicitly setting mode
        @Implemented with: 4.4.0
        @Last updated with: 5.0.0
        """
        pass


# Source
# - File: Selection.h
# - Line: 30
class Selection(QObject):
    """Selection represents a selection on Krita. A selection is
    not necessarily associated with a particular Node or Image.

    @code
    from krita import *

    d = Application.activeDocument()
    n = d.activeNode()
    r = n.bounds() 
    s = Selection()
    s.select(r.width() / 3, r.height() / 3, r.width() / 3, r.height() / 3, 255)
    s.cut(n)
    @endcode

    @Implemented with: 4.0.0
    @Updated with: 4.3.0
    """
    # Source location, line 180
    def add(self, selection: Selection):
        """Add the given selection's selected pixels to the current selection.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 128
    def border(self, xRadius: int, yRadius: int):
        """Border the selection with the given radius.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 86
    def clear(self):
        """Make the selection entirely unselected.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 92
    def contract(self, value: int):
        """Make the selection's width and height smaller by the given value.
        This will not move the selection's top-left position.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 98
    def copy(self, node: Node):
        """@brief copy copies the area defined by the selection from the node to the clipboard.
        @param node the node from where the pixels will be copied.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 104
    def cut(self, node: Node):
        """@brief cut erases the area defined by the selection from the node and puts a copy on the clipboard.
        @param node the node from which the selection will be cut.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 123
    def dilate(self):
        """Dilate the selection with a radius of 1 pixel.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 56
    def duplicate(self):
        """@return a duplicate of the selection
        @Implemented with: 4.3.0
        @Last updated with: 5.0.0
        """
        pass

    # Source location, line 118
    def erode(self):
        """Erode the selection with a radius of 1 pixel.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 133
    def feather(self, radius: int):
        """Feather the selection with the given radius.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 138
    def grow(self, xradius: int, yradius: int):
        """Grow the selection with the given radius.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 66
    def height(self) -> int:
        """@return the height of the selection
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 190
    def intersect(self, selection: Selection):
        """Intersect the given selection with this selection.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 153
    def invert(self):
        """Invert the selection.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 81
    def move(self, x: int, y: int):
        """Move the selection's top-left corner to the given coordinates.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 113
    def paste(self, destination: Node, x: int, y: int):
        """@brief paste pastes the content of the clipboard to the given node, limited by the area of the current
        selection.
        @param destination the node where the pixels will be written
        @param x: the x position at which the clip will be written
        @param y: the y position at which the clip will be written
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 213
    def pixelData(self, x: int, y: int, w: int, h: int) -> QByteArray:
        """@brief pixelData reads the given rectangle from the Selection's mask and returns it as a
        byte array. The pixel data starts top-left, and is ordered row-first.

        The byte array will contain one byte for every pixel, representing the selectedness. 0
        is totally unselected, 255 is fully selected.

        You can read outside the Selection's boundaries; those pixels will be unselected.

        The byte array is a copy of the original selection data.
        @param x x position from where to start reading
        @param y y position from where to start reading
        @param w row length to read
        @param h number of rows to read
        @return a QByteArray with the pixel data. The byte array may be empty.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 175
    def replace(self, selection: Selection):
        """Replace the current selection's selection with the one of the given selection.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 158
    def resize(self, w: int, h: int):
        """Resize the selection to the given width and height. The top-left position will not be moved.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 164
    def select(self, x: int, y: int, w: int, h: int, value: int):
        """Select the given area. The value can be between 0 and 255; 0 is 
        totally unselected, 255 is totally selected.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 170
    def selectAll(self, node: Node, value: int):
        """Select all pixels in the given node. The value can be between 0 and 255; 0 is 
        totally unselected, 255 is totally selected.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 228
    def setPixelData(self, value: QByteArray, x: int, y: int, w: int, h: int):
        """@brief setPixelData writes the given bytes, of which there must be enough, into the
        Selection.

        @param value the byte array representing the pixels. There must be enough bytes available.
        Krita will take the raw pointer from the QByteArray and start reading, not stopping before
        (w * h) bytes are read.

        @param x the x position to start writing from
        @param y the y position to start writing from
        @param w the width of each row
        @param h the number of rows to write
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 143
    def shrink(self, xRadius: int, yRadius: int, edgeLock: bool):
        """Shrink the selection with the given radius.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 148
    def smooth(self):
        """Smooth the selection.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 185
    def subtract(self, selection: Selection):
        """Subtract the given selection's selected pixels from the current selection.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 195
    def symmetricdifference(self, selection: Selection):
        """Intersect with the inverse of the given selection with this selection.
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 61
    def width(self) -> int:
        """@return the width of the selection
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 71
    def x(self) -> int:
        """@return the left-hand position of the selection.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 76
    def y(self) -> int:
        """@return the top position of the selection.
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: SelectionMask.h
# - Line: 26
class SelectionMask(Node):
    """@brief The SelectionMask class
    A selection mask is a mask type node that can be used
    to store selections. In the gui, these are referred to
    as local selections.

    A selection mask can hold both raster and vector selections, though
    the API only supports raster selections.

    @Implemented with: 4.0.0
    """
    # Source location, line 48
    def selection(self) -> Selection:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 50
    def setSelection(self, selection: Selection):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 46
    def type(self) -> str:
        """@brief type Krita has several types of nodes, split in layers and masks. Group
        layers can contain other layers, any layer can contain masks.

        @return selectionmask

        If the Node object isn't wrapping a valid Krita layer or mask object, and
        empty string is returned.
        @Virtual
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: Shape.h
# - Line: 37
class Shape(QObject):
    """@brief The Shape class
    The shape class is a wrapper around Krita's vector objects.

    Some example code to parse through interesting information in a given vector layer with shapes.
    @code
    import sys
    from krita import *

    doc = Application.activeDocument()

    root = doc.rootNode()

    for layer in root.childNodes():
        print (str(layer.type())+" "+str(layer.name()))
        if (str(layer.type())=="vectorlayer"):
            for shape in layer.shapes():
                print(shape.name())
                print(shape.toSvg())
    @endcode

    @Implemented with: 4.0.0
    @Updated with: 5.2.0
    """
    # Source location, line 151
    def absoluteTransformation(self) -> QTransform:
        """@brief transformation the 2D transformation matrix of the shape including all grandparent transforms.
        @return the 2D transformation matrix.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 121
    def boundingBox(self) -> QRectF:
        """@brief boundingBox the bounding box of the shape in points
        @return RectF containing the bounding box.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 187
    def deselect(self):
        """@brief deselect deselects the shape.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 97
    def geometryProtected(self) -> bool:
        """@brief geometryProtected
        @return whether the shape is protected from user changing the shape geometry.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 193
    def isSelected(self) -> bool:
        """@brief isSelected
        @return whether the shape is selected.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 55
    def name(self) -> str:
        """@brief name
        @return the name of the shape
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 199
    def parentShape(self):
        """@brief parentShape
        @return the parent GroupShape of the current shape.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 127
    def position(self) -> QPointF:
        """@brief position the position of the shape in points.
        @return the position of the shape in points.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 156
    def remove(self) -> bool:
        """@brief remove delete the shape.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 182
    def select(self):
        """@brief select selects the shape.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 85
    def selectable(self) -> bool:
        """@brief selectable
        @return whether the shape is user selectable.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 103
    def setGeometryProtected(self, protect: bool):
        """@brief setGeometryProtected
        @param protect whether the shape should be geometry protected from the user.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 61
    def setName(self, name: str):
        """@brief setName
        @param name which name the shape should have.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 133
    def setPosition(self, point: QPointF):
        """@brief setPosition set the position of the shape.
        @param point the new position in points
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 91
    def setSelectable(self, selectable: bool):
        """@brief setSelectable
        @param selectable whether the shape should be user selectable.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 145
    def setTransformation(self, matrix: QTransform):
        """@brief setTransformation set the 2D transformation matrix of the shape.
        @param matrix the new 2D transformation matrix.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 115
    def setVisible(self, visible: bool):
        """@brief setVisible
        @param visible whether the shape should be visible.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 79
    def setZIndex(self, zindex: int):
        """@brief setZIndex
        @param zindex set the shape zindex value.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 177
    def toSvg(self, prependStyles: bool = False, stripTextMode: bool = True) -> str:
        """@brief toSvg
        convert the shape to svg, will not include style definitions.
        @param prependStyles prepend the style data. Default: false
        @param stripTextMode enable strip text mode. Default: true
        @return the svg in a string.
        @Implemented with: 4.0.0
        @Last updated with: 5.0.0
        """
        pass

    # Source location, line 139
    def transformation(self) -> QTransform:
        """@brief transformation the 2D transformation matrix of the shape.
        @return the 2D transformation matrix.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 67
    def type(self) -> str:
        """@brief type
        @return the type of shape.
        @Virtual
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 161
    def update(self):
        """@brief update queue the shape update.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 167
    def updateAbsolute(self, box: QRectF):
        """@brief updateAbsolute queue the shape update in the specified rectangle.
        @param box the RectF rectangle to update.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 109
    def visible(self) -> bool:
        """@brief visible
        @return whether the shape is visible.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 73
    def zIndex(self) -> int:
        """@brief zIndex
        @return the zindex of the shape.
        @Implemented with: 5.0.0
        """
        pass


# Source
# - File: Swatch.h
# - Line: 21
class Swatch:
    """@brief The Swatch class is a thin wrapper around the KisSwatch class.

    A Swatch is a single color that is part of a palette, that has a name
    and an id. A Swatch color can be a spot color.

    @Implemented with: 4.2.0
    """
    # Source location, line 30
    def Swatch(self, rhs: Swatch):
        """@Implemented with: 4.2.0
        @Last updated with: 5.2.0
        """
        pass

    # Source location, line 25
    def Swatch(self):
        """@Virtual
        @Implemented with: 4.2.0
        """
        pass

    # Source location, line 26
    def Swatch(self, rhs: Swatch):
        """@Implemented with: 4.2.0"""
        pass

    # Source location, line 39
    def color(self) -> ManagedColor:
        """@Implemented with: 4.2.0"""
        pass

    # Source location, line 36
    def id(self) -> str:
        """@Implemented with: 4.2.0"""
        pass

    # Source location, line 45
    def isValid(self) -> bool:
        """@Implemented with: 4.2.0"""
        pass

    # Source location, line 33
    def name(self) -> str:
        """@Implemented with: 4.2.0"""
        pass

    # Source location, line 40
    def setColor(self, color: ManagedColor):
        """@Implemented with: 4.2.0"""
        pass

    # Source location, line 37
    def setId(self, id: str):
        """@Implemented with: 4.2.0"""
        pass

    # Source location, line 34
    def setName(self, name: str):
        """@Implemented with: 4.2.0"""
        pass

    # Source location, line 43
    def setSpotColor(self, spotColor: bool):
        """@Implemented with: 4.2.0"""
        pass

    # Source location, line 42
    def spotColor(self) -> bool:
        """@Implemented with: 4.2.0"""
        pass


# Source
# - File: TransformMask.h
# - Line: 22
class TransformMask(Node):
    """@brief The TransformMask class
    A transform mask is a mask type node that can be used
    to store transformations.

    @Implemented with: 5.0.0
    @Updated with: 5.2.0
    """
    # Source location, line 44
    def finalAffineTransform(self) -> QTransform:
        """@Implemented with: 5.0.0"""
        pass

    # Source location, line 88
    def fromXML(self, xml: str) -> bool:
        """@brief fromXML set the transform of the transform mask from XML formatted data.
        The xml must have a valid id

        dumbparams - placeholder for static transform masks
        tooltransformparams - static transform mask
        animatedtransformparams - animated transform mask

        @code
        <!DOCTYPE transform_params>
        <transform_params>
          <main id="tooltransformparams"/>
          <data mode="0">
           <free_transform>
            <transformedCenter type="pointf" x="12.3102137276208" y="11.0727768562035"/>
            <originalCenter type="pointf" x="20" y="20"/>
            <rotationCenterOffset type="pointf" x="0" y="0"/>
            <transformAroundRotationCenter value="0" type="value"/>
            <aX value="0" type="value"/>
            <aY value="0" type="value"/>
            <aZ value="0" type="value"/>
            <cameraPos z="1024" type="vector3d" x="0" y="0"/>
            <scaleX value="1" type="value"/>
            <scaleY value="1" type="value"/>
            <shearX value="0" type="value"/>
            <shearY value="0" type="value"/>
            <keepAspectRatio value="0" type="value"/>
            <flattenedPerspectiveTransform m23="0" m31="0" m32="0" type="transform" m33="1" m12="0" m13="0" m22="1" m11="1" m21="0"/>
            <filterId value="Bicubic" type="value"/>
           </free_transform>
          </data>
        </transform_params>
        @endcode
        @param xml a valid formated XML string with proper main and data elements.
        @return a true response if successful, a false response if failed.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 50
    def toXML(self) -> str:
        """@brief toXML
        @return a string containing XML formated transform parameters.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 42
    def type(self) -> str:
        """@brief type Krita has several types of nodes, split in layers and masks. Group
        layers can contain other layers, any layer can contain masks.

        @return transformmask

        If the Node object isn't wrapping a valid Krita layer or mask object, and
        empty string is returned.
        @Virtual
        @Implemented with: 5.0.0
        """
        pass


# Source
# - File: TransparencyMask.h
# - Line: 23
class TransparencyMask(Node):
    """@brief The TransparencyMask class
    A transparency mask is a mask type node that can be used
    to show and hide parts of a layer.


    @Implemented with: 5.2.0
    """
    # Source location, line 45
    def selection(self) -> Selection:
        """@Implemented with: 5.2.0"""
        pass

    # Source location, line 47
    def setSelection(self, selection: Selection):
        """@Implemented with: 5.2.0"""
        pass

    # Source location, line 43
    def type(self) -> str:
        """@brief type Krita has several types of nodes, split in layers and masks. Group
        layers can contain other layers, any layer can contain masks.

        @return transparencymask

        If the Node object isn't wrapping a valid Krita layer or mask object, and
        empty string is returned.
        @Virtual
        @Implemented with: 5.2.0
        """
        pass


# Source
# - File: VectorLayer.h
# - Line: 31
class VectorLayer(Node):
    """@brief The VectorLayer class
    A vector layer is a special layer that stores
    and shows vector shapes.

    Vector shapes all have their coordinates in points, which
    is a unit that represents 1/72th of an inch. Keep this in
    mind wen parsing the bounding box and position data.

    @Implemented with: 4.0.0
    @Updated with: 5.2.0
    """
    # Source location, line 69
    def addShapesFromSvg(self, svg: str) -> list[Shape]:
        """@brief addShapesFromSvg
        add shapes to the layer from a valid svg.
        @param svg valid svg string.
        @return the list of shapes added to the layer from the svg.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 96
    def createGroupShape(self, name: str, shapes: list[Shape]) -> Shape:
        """@brief createGroupShape
        combine a list of top level shapes into a group.
        @param name the name of the shape.
        @param shapes list of top level shapes.
        @return if successful, a GroupShape object will be returned.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 77
    def shapeAtPosition(self, position: QPointF) -> Shape:
        """@brief shapeAtPoint
        check if the position is located within any non-group shape's boundingBox() on the current layer.
        @param position a QPointF of the position.
        @return the shape at the position, or None if no shape is found.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 54
    def shapes(self) -> list[Shape]:
        """@brief shapes
        @return the list of top-level shapes in this vector layer.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 87
    def shapesInRect(self, rect: QRectF, omitHiddenShapes: bool = True, containedMode: bool = False) -> list[Shape]:
        """@brief shapeInRect
        get all non-group shapes that the shape's boundingBox() intersects or is contained within a given rectangle on the current layer.
        @param rect a QRectF
        @param omitHiddenShapes true if non-visible() shapes should be omitted, false if they should be included. \p omitHiddenShapes defaults to true.
        @param containedMode false if only shapes that are within or intersect with the outline should be included, true if only shapes that are fully contained within the outline should be included. \p containedMode defaults to false
        @return returns a list of shapes.
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 61
    def toSvg(self) -> str:
        """@brief toSvg
        convert the shapes in the layer to svg.
        @return the svg in a string.
        @Implemented with: 5.0.0
        """
        pass

    # Source location, line 48
    def type(self) -> str:
        """@brief type Krita has several types of nodes, split in layers and masks. Group
        layers can contain other layers, any layer can contain masks.

        @return vectorlayer
        @Virtual
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: View.h
# - Line: 24
class View(QObject):
    """View represents one view on a document. A document can be
    shown in more than one view at a time.

    @Implemented with: 4.0.0
    @Updated with: 5.2.0
    """
    # Source location, line 108
    def HDRExposure(self) -> float:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 111
    def HDRGamma(self) -> float:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 73
    def activateResource(self, resource: Resource):
        """@brief activateResource activates the given resource.
        @param resource: a pattern, gradient or paintop preset
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 97
    def backGroundColor(self) -> ManagedColor:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 93
    def backgroundColor(self) -> ManagedColor:
        """@Implemented with: 4.0.2"""
        pass

    # Source location, line 117
    def brushSize(self) -> float:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 67
    def canvas(self) -> Canvas:
        """@return the canvas this view is showing. The canvas controls
        things like zoom and rotation.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 105
    def currentBlendingMode(self) -> str:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 96
    def currentBrushPreset(self) -> Resource:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 102
    def currentGradient(self) -> Resource:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 99
    def currentPattern(self) -> Resource:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 46
    def document(self) -> Document:
        """@return the document this view is showing.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 162
    def flakeToCanvasTransform(self) -> QTransform:
        """@brief flakeToCanvasTransform
        The transformation of the canvas relative to the view without rotation and mirroring
        @return QTransform
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 155
    def flakeToDocumentTransform(self) -> QTransform:
        """@brief flakeToDocumentTransform
        The transformation of the document relative to the view without rotation and mirroring
        @return QTransform
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 169
    def flakeToImageTransform(self) -> QTransform:
        """@brief flakeToImageTransform
        The transformation of the image relative to the view without rotation and mirroring
        @return QTransform
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 94
    def foreGroundColor(self) -> ManagedColor:
        """@brief foreGroundColor allows access to the currently active color.
        This is nominally per canvas/view, but in practice per mainwindow.
        @code
        color = Application.activeWindow().activeView().foreGroundColor()
        components = color.components()
        components[0] = 1.0
        components[1] = 0.6
        components[2] = 0.7
        color.setComponents(components)
        Application.activeWindow().activeView().setForeGroundColor(color)
        @endcode
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 90
    def foregroundColor(self) -> ManagedColor:
        """@brief foregroundColor allows access to the currently active color.
        This is nominally per canvas/view, but in practice per mainwindow.
        @code
        color = Application.activeWindow().activeView().foregroundColor()
        components = color.components()
        components[0] = 1.0
        components[1] = 0.6
        components[2] = 0.7
        color.setComponents(components)
        Application.activeWindow().activeView().setForeGroundColor(color)
        @endcode
        @Implemented with: 4.0.2
        """
        pass

    # Source location, line 120
    def paintingFlow(self) -> float:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 114
    def paintingOpacity(self) -> float:
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 148
    def selectedNodes(self) -> list[Node]:
        """@brief selectedNodes returns a list of Nodes that are selected in this view.


        @code
        from krita import *
        w = Krita.instance().activeWindow()
        v = w.activeView()
        selected_nodes = v.selectedNodes()
        print(selected_nodes)
        @endcode


        @return a list of Node objects which may be empty.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 94
    def setBackGroundColor(self, color: ManagedColor):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 118
    def setBrushSize(self, brushSize: float):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 106
    def setCurrentBlendingMode(self, blendingMode: str):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 97
    def setCurrentBrushPreset(self, resource: Resource):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 103
    def setCurrentGradient(self, resource: Resource):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 100
    def setCurrentPattern(self, resource: Resource):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 51
    def setDocument(self, document: Document):
        """Reset the view to show @p document.
        @Implemented with: 4.3.0
        """
        pass

    # Source location, line 91
    def setForeGroundColor(self, color: ManagedColor):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 109
    def setHDRExposure(self, exposure: float):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 112
    def setHDRGamma(self, gamma: float):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 121
    def setPaintingFlow(self, flow: float):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 115
    def setPaintingOpacity(self, opacity: float):
        """@Implemented with: 4.0.0"""
        pass

    # Source location, line 61
    def setVisible(self):
        """Make the current view visible.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 131
    def showFloatingMessage(self, message: str, icon: QIcon, timeout: int, priority: int):
        """@brief showFloatingMessage displays a floating message box on the top-left corner of the canvas
        @param message: Message to be displayed inside the floating message box
        @param icon: Icon to be displayed inside the message box next to the message string
        @param timeout: Milliseconds until the message box disappears
        @param priority: 0 = High, 1 = Medium, 2 = Low. Higher priority
        messages will be displayed in place of lower priority messages
        @Implemented with: 4.4.0
        @Last updated with: 5.0.0
        """
        pass

    # Source location, line 56
    def visible(self) -> bool:
        """@return true if the current view is visible, false if not.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 41
    def window(self) -> Window:
        """@return the window this view is shown in.
        @Implemented with: 4.0.0
        """
        pass


# Source
# - File: Window.h
# - Line: 22
class Window(QObject):
    """Window represents one Krita mainwindow. A window can have any number
    of views open on any number of documents.

    @Implemented with: 4.0.0
    @Updated with: 5.2.0
    """
    # Emitted when the active view changes
    # @Implemented with: 4.4.0
    activeViewChanged = pyqtSignal()

    #  Emitted when we change the color theme
    # @Implemented with: 4.4.0
    themeChanged = pyqtSignal()

    # Emitted when the window is closed.
    # @Implemented with: 4.0.0
    windowClosed = pyqtSignal()
    # Source location, line 72
    def activate(self):
        """@brief activate activates this Window.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 67
    def activeView(self) -> View:
        """@return the currently active view or 0 if no view is active
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 55
    def addView(self, document: Document) -> View:
        """Open a new view on the given document in this window
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 79
    def close(self):
        """@brief close the active window and all its Views. If there
        are no Views left for a given Document, that Document will
        also be closed.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 92
    def createAction(self, id: str, text: str = "", menuLocation: str = "tools/scripts") -> QAction:
        """@brief createAction creates a QAction object and adds it to the action
        manager for this Window.
        @param id The unique id for the action. This will be used to
            propertize the action if any .action file is present
        @param text The user-visible text of the action. If empty, the text from the
           .action file is used.
        @param menuLocation a /-separated string that describes which menu the action should
            be places in. Default is "tools/scripts"
        @return the new action.
        @Implemented with: 4.0.0
        @Last updated with: 4.2.0
        """
        pass

    # Source location, line 45
    def dockers(self) -> list[QDockWidget]:
        """@brief dockers
        @return a list of all the dockers belonging to this window
        @Implemented with: 5.2.0
        """
        pass

    # Source location, line 39
    def qwindow(self) -> QMainWindow:
        """Return a handle to the QMainWindow widget. This is useful
        to e.g. parent dialog boxes and message box.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 61
    def showView(self, view: View):
        """Make the given view active in this window. If the view
        does not belong to this window, nothing happens.
        @Implemented with: 4.0.0
        """
        pass

    # Source location, line 50
    def views(self) -> list[View]:
        """@return a list of open views in this window
        @Implemented with: 4.0.0
        """
        pass
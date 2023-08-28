# -----------------------------------------------------------------------------
# BuliPy
# Copyright (C) 2023 - Grum999
# -----------------------------------------------------------------------------
# SPDX-License-Identifier: GPL-3.0-or-later
#
# https://spdx.org/licenses/GPL-3.0-or-later.html
# -----------------------------------------------------------------------------
# A Krita plugin to write and execute scripts
# -----------------------------------------------------------------------------

import html
import re
import random

from PyQt5.Qt import *
from PyQt5.QtWidgets import (
        QToolTip,
        QDockWidget
    )
from PyQt5.QtCore import (
        pyqtSignal as Signal
    )


from ..pktk.modules.imgutils import buildIcon
from ..pktk.widgets.wiodialog import (
        WDialogMessage,
        WDialogFile
    )
from ..pktk.widgets.wdockwidget import WDockWidget
from ..pktk.widgets.wseparator import WVLine
from ..pktk.widgets.wconsole import (
        WConsole,
        WConsoleType,
        WConsoleUserData
    )
from ..pktk.widgets.wsearchinput import (
        WSearchInput,
        SearchOptions
    )

from ..pktk.pktk import *


class BPDockWidgetConsoleOutput(WDockWidget):
    """A dock widget to display a console with some advanced features

    Docker is made of:
    - A QLineEdit: used as search filter
    - QButtons: used to define quick filters & actions
    - A WConsole: used to provide output content
    """
    # click on a source reference in console (source, fromPosition, toPosition)
    sourceRefClicked = Signal(str, QPoint, QPoint)

    # console has been cleared (ONLY triggered with  BPDockWidgetConsoleOutput.clear() method!!!
    consoleClear = Signal()

    OPTION_BTN_REGEX =               0b00000000000_00001
    OPTION_BTN_CASESENSITIVE =       0b00000000000_00010
    OPTION_BTN_WHOLEWORD =           0b00000000000_00100
    OPTION_BTN_BACKWARD =            0b00000000000_01000
    OPTION_BTN_HIGHLIGHT =           0b00000000000_10000
    # available bits:                         <-->
    OPTION_BTN_BUTTONSHOW =          0b10000000000_00000
    OPTION_TXT_SEARCH =              0b01000000000_00000
    OPTION_FILTER_TYPES =            0b00100000000_00000
    OPTION_FILTER_SEARCH =           0b00010000000_00000
    OPTION_BUFFER_SIZE =             0b00001000000_00000
    OPTION_AUTOCLEAR =               0b00000100000_00000
    OPTION_FONTSIZE =                0b00000010000_00000
    #                                         <-->

    def __init__(self, parent, documents, name='Script execution output'):
        super(BPDockWidgetConsoleOutput, self).__init__(name, parent)

        self.__widget = QWidget(self)
        self.__widget.setMinimumWidth(200)

        self.__layout = QVBoxLayout(self.__widget)
        self.__widget.setLayout(self.__layout)

        self.__cConsole = WConsole(self)
        self.__tbFilter = BPConsoleTBar(self.__cConsole)
        self.__tbFilter.consoleClear.connect(self.clear)

        self.__layout.addWidget(self.__tbFilter)
        self.__layout.addWidget(self.__cConsole)

        self.__cConsole.setOptionBufferSize(0)

        # not the cleanest way to implement this :-)
        self.__origConsoleMousePressEvent = self.__cConsole.mousePressEvent
        self.__origConsoleMouseMoveEvent = self.__cConsole.mouseMoveEvent
        self.__cConsole.mousePressEvent = self.__mouseClick
        self.__cConsole.mouseMoveEvent = self.__mouseMove
        self.__cConsole.setMouseTracking(True)

        self.__scriptRunning = False
        self.__documents = documents

        self.setWidget(self.__widget)

    def __mouseClick(self, event):
        """Clicked on console"""
        if self.__origConsoleMousePressEvent:
            self.__origConsoleMousePressEvent(event)

        cursor = self.__cConsole.cursorForPosition(event.pos())
        if cursor and event.modifiers() == Qt.ControlModifier:
            data = cursor.block().userData()
            if not isinstance(data, WConsoleUserData):
                return

            data = data.data()
            if not isinstance(data, dict):
                return

            fromPosition = data['fromPosition']
            toPosition = data['toPosition']
            source = data['source']

            if source[0] == '@':
                # cacheUuid of executed document
                self.__documents.setActiveDocument(source[1:])
            else:
                # a file name
                # => check if already open
                opened = False
                for document in self.__documents.documents():
                    if document.tabName(True) == source:
                        self.__documents.setActiveDocument(document)
                        opened = True
                        break

                if not opened:
                    # open file
                    self.__documents.openDocument(source)

            self.sourceRefClicked.emit(source, fromPosition, toPosition)

    def __mouseMove(self, event):
        """Clicked on console"""
        if self.__origConsoleMouseMoveEvent:
            self.__origConsoleMouseMoveEvent(event)

        cursor = self.__cConsole.cursorForPosition(event.pos())
        if cursor:
            data = cursor.block().userData()
            if not isinstance(data, WConsoleUserData):
                QToolTip.hideText()
                return

            data = data.data()
            if not isinstance(data, dict):
                QToolTip.hideText()
                return

            document = self.__documents.document()
            line = data['fromPosition'].y()
            file = data['source'].replace(f"@{document.cacheUuid()}", document.tabName(True))

            rect = self.__cConsole.blockBoundingGeometry(cursor.block()).translated(self.__cConsole.contentOffset())
            position = self.__cConsole.mapToGlobal(rect.topLeft().toPoint()) + QPoint(25, 30)

            msg = i18n(f"CTRL+Click to go to file {file}, line {line}")

            QToolTip.showText(position, msg+" ", self)  # dirty trick to force tooltip to be displayed at expected position when mouse move
            QToolTip.showText(position, msg, self)
        else:
            QToolTip.hideText()

    def option(self, optionId):
        """Return current option value

        Option Id refer to:                                                 Returned Value
            BPDockWidgetConsoleOutput.OPTION_BTN_REGEX                      Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_CASESENSITIVE              Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_WHOLEWORD                  Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_BACKWARD                   Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_HIGHLIGHT                  Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_BUTTONSHOW                 Boolean
            BPDockWidgetConsoleOutput.OPTION_TXT_SEARCH                     String
            BPDockWidgetConsoleOutput.OPTION_FILTER_TYPES                   List
            BPDockWidgetConsoleOutput.OPTION_BUFFER_SIZE                    Integer
            BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR                      Boolean
            BPDockWidgetConsoleOutput.OPTION_FONTSIZE                       Integer
        """
        if optionId & BPDockWidgetConsoleOutput.OPTION_BUFFER_SIZE == BPDockWidgetConsoleOutput.OPTION_BUFFER_SIZE:
            return self.__cConsole.optionBufferSize()
        elif optionId & BPDockWidgetConsoleOutput.OPTION_FONTSIZE == BPDockWidgetConsoleOutput.OPTION_FONTSIZE:
            return self.__cConsole.optionFontSize()
        else:
            return self.__tbFilter.option(optionId)

    def setOption(self, optionId, value):
        """Set option value

        Option Id refer to:                                                 Value
            BPDockWidgetConsoleOutput.OPTION_BTN_REGEX                      Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_CASESENSITIVE              Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_WHOLEWORD                  Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_BACKWARD                   Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_HIGHLIGHT                  Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_BUTTONSHOW                 Boolean
            BPDockWidgetConsoleOutput.OPTION_TXT_SEARCH                     String
            BPDockWidgetConsoleOutput.OPTION_FILTER_TYPES                   List
            BPDockWidgetConsoleOutput.OPTION_BUFFER_SIZE                    Integer
            BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR                      Boolean
            BPDockWidgetConsoleOutput.OPTION_FONTSIZE                       Integer
        """
        if optionId & BPDockWidgetConsoleOutput.OPTION_BUFFER_SIZE == BPDockWidgetConsoleOutput.OPTION_BUFFER_SIZE:
            self.__cConsole.setOptionBufferSize(value)
        elif optionId & BPDockWidgetConsoleOutput.OPTION_FONTSIZE == BPDockWidgetConsoleOutput.OPTION_FONTSIZE:
            self.__cConsole.setOptionFontSize(value)
        else:
            self.__tbFilter.setOption(optionId, value)

    def console(self):
        """Return console instance"""
        return self.__cConsole

    def append(self, text, type=WConsoleType.NORMAL, data=None, cReturn=True, cRaw=False):
        """Append `text` to console, using given `type`
        If `cReturn` is True, apply a carriage return
        """
        if cReturn is True:
            self.__cConsole.appendLine(text, type, data, cRaw)
        else:
            self.__cConsole.append(text, cRaw)

    def autoClear(self):
        """Clear console if option autoclear is active, otherwise does nothing"""
        if self.option(BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR):
            self.__cConsole.clear()
            return True
        else:
            return False

    def clear(self):
        """Clear console, delete console cache file if any"""
        self.__cConsole.clear()
        self.consoleClear.emit()
        try:
            os.unlink(self.__documents.document().cacheFileNameConsole())
        except Exception as e:
            pass

    def scriptIsRunning(self):
        """Return true if console 'scriptIsRunning' flag is active"""
        return self.__scriptRunning

    def setScriptIsRunning(self, isRunning):
        """Set console 'scriptIsRunning' flag active/inactive"""
        if not isinstance(isRunning, bool):
            raise EInvalidType("Given `isRunning` value must be a <bool>")

        self.__isRunning = isRunning
        self.__tbFilter.setScriptIsRunning(self.__isRunning)

        if not self.__scriptRunning:
            self.updateSearchAndFilter()

    def scrollToLastRow(self):
        """Go to last row"""
        self.__cConsole.scrollToLastRow()

    def updateSearchAndFilter(self):
        """Update search and filter if needed"""
        self.__tbFilter.updateSearchAndFilter()


class BPConsoleTBar(QWidget):
    """Interface to manage filter + buttons"""

    consoleClear = Signal()

    def __init__(self, console, parent=None):
        super(BPConsoleTBar, self).__init__(parent)
        self.__console = console

        self.__layout = QHBoxLayout(self)

        self.__isScriptRunning = False

        self.__btFilterType = QToolButton(self)
        self.__btFilterType.setAutoRaise(True)
        self.__btFilterType.setIcon(buildIcon('pktk:filter_alt'))
        self.__btFilterType.setToolTip(i18n('Apply filter'))
        self.__btFilterType.setPopupMode(QToolButton.InstantPopup)

        self.__btSave = QToolButton(self)
        self.__btSave.setAutoRaise(True)
        self.__btSave.setIcon(buildIcon('pktk:file_save'))
        self.__btSave.setToolTip(i18n('Save console output'))
        self.__btSave.clicked.connect(lambda: self.saveConsole())

        self.__btClear = QToolButton(self)
        self.__btClear.setAutoRaise(True)
        self.__btClear.setIcon(buildIcon('pktk:clear'))
        self.__btClear.setToolTip(i18n('Clear console output'))
        self.__btClear.setPopupMode(QToolButton.MenuButtonPopup)
        self.__btClear.clicked.connect(lambda: self.consoleClear.emit())

        self.__siSearch = WSearchInput(WSearchInput.OPTION_ALL_BUTTONS | WSearchInput.OPTION_STATE_BUTTONSHOW, self)
        self.__siSearch.searchActivated.connect(self.__searchActivated)
        self.__siSearch.searchModified.connect(self.__searchModified)
        self.__siSearch.searchOptionModified.connect(self.__searchOptionModified)
        self.__siSearch.setToolTip(i18n('Search for text'))

        # used when options are modified, to compare current and previous options
        self.__currentOptions = 0

        self.__layout.addWidget(self.__btSave)
        self.__layout.addWidget(self.__btClear)
        self.__layout.addWidget(WVLine(self))
        self.__layout.addWidget(self.__btFilterType)
        self.__layout.addWidget(self.__siSearch)
        self.__layout.setContentsMargins(0, 0, 0, 0)

        # -- build menu for filter type
        self.__actionFilterTypeError = QAction(i18n('Show errors'), self)
        self.__actionFilterTypeError.setCheckable(True)
        self.__actionFilterTypeError.setChecked(True)
        self.__actionFilterTypeError.toggled.connect(self.__filterOptionModified)
        self.__actionFilterTypeWarning = QAction(i18n('Show warnings'), self)
        self.__actionFilterTypeWarning.setCheckable(True)
        self.__actionFilterTypeWarning.setChecked(True)
        self.__actionFilterTypeWarning.toggled.connect(self.__filterOptionModified)
        self.__actionFilterTypeInfo = QAction(i18n('Show information'), self)
        self.__actionFilterTypeInfo.setCheckable(True)
        self.__actionFilterTypeInfo.setChecked(True)
        self.__actionFilterTypeInfo.toggled.connect(self.__filterOptionModified)
        self.__actionFilterTypeOutput = QAction(i18n('Show output'), self)
        self.__actionFilterTypeOutput.setCheckable(True)
        self.__actionFilterTypeOutput.setChecked(True)
        self.__actionFilterTypeOutput.toggled.connect(self.__filterOptionModified)
        self.__actionFilterSearchFoundOnly = QAction(i18n('Show found occurences only'), self)
        self.__actionFilterSearchFoundOnly.setStatusTip(i18n("If there's a current search ongoing and option 'Highlight all occurences found' is checked, will filter script output to display found items only"))
        self.__actionFilterSearchFoundOnly.setCheckable(True)
        self.__actionFilterSearchFoundOnly.setChecked(False)
        self.__actionFilterSearchFoundOnly.toggled.connect(self.__filterOptionModified)

        self.__menuFilterType = QMenu(self.__btFilterType)
        self.__menuFilterType.addAction(self.__actionFilterTypeError)
        self.__menuFilterType.addAction(self.__actionFilterTypeWarning)
        self.__menuFilterType.addAction(self.__actionFilterTypeInfo)
        self.__menuFilterType.addAction(self.__actionFilterTypeOutput)
        self.__menuFilterType.addSeparator()
        self.__menuFilterType.addAction(self.__actionFilterSearchFoundOnly)
        self.__btFilterType.setMenu(self.__menuFilterType)

        # -- build menu for clear button
        self.__actionAutoClear = QAction(i18n('Auto clear'), self)
        self.__actionAutoClear.setCheckable(True)
        self.__actionAutoClear.setChecked(True)
        self.__actionAutoClear.setStatusTip(i18n('When checked, clear console output automatically before script execution'))

        self.__menuClearOptions = QMenu(self.__btClear)
        self.__menuClearOptions.addAction(self.__actionAutoClear)
        self.__btClear.setMenu(self.__menuClearOptions)

        self.setLayout(self.__layout)
        self.updateSearchAndFilter()

    def __searchActivated(self, text, options, searchAll=False):
        """Ask to search for text"""
        if self.__isScriptRunning:
            return

        if options & SearchOptions.HIGHLIGHT == SearchOptions.HIGHLIGHT:
            # select all occurences
            self.__console.search().searchAll(text, options)
        else:
            # deselect all highlighted occurences
            self.__console.search().searchAll(None, SearchOptions.HIGHLIGHT)

        # force highlight option when searching a text
        self.__console.search().searchNext(text, options | SearchOptions.HIGHLIGHT)
        if self.__console.optionFilteredExtraSelection():
            self.__console.updateFilter()

        self.__currentOptions = options

    def __searchModified(self, text, options):
        """Ask to search for text -- search made only for highlighted text"""
        if self.__isScriptRunning:
            return

        if options & SearchOptions.HIGHLIGHT == SearchOptions.HIGHLIGHT:
            # select all occurences
            self.__console.search().searchAll(text, options)
        else:
            # deselect all highlighted occurences
            self.__console.search().searchAll(None, SearchOptions.HIGHLIGHT)

        if self.__console.optionFilteredExtraSelection():
            self.__console.updateFilter()
        self.__currentOptions = options

    def __searchOptionModified(self, text, options):
        """option have been modified, ask to search for text taking in account new options"""
        if self.__isScriptRunning:
            return

        if options & SearchOptions.HIGHLIGHT == SearchOptions.HIGHLIGHT:
            # select all occurences
            self.__console.search().searchAll(text, options)
        else:
            # deselect all highlighted occurences
            self.__console.search().searchAll(None, SearchOptions.HIGHLIGHT)

        if (self.__currentOptions ^ options) & SearchOptions.HIGHLIGHT != SearchOptions.HIGHLIGHT:
            # search only if modified option is not highlight all

            # force highlight option when searching a text
            self.__console.search().searchNext(text, options | SearchOptions.HIGHLIGHT)

        if self.__console.optionFilteredExtraSelection():
            self.__console.updateFilter()

        self.__currentOptions = options
        self.__console.setOptionFilteredExtraSelection(self.__actionFilterSearchFoundOnly.isChecked() and (self.__currentOptions & SearchOptions.HIGHLIGHT == SearchOptions.HIGHLIGHT))

    def __filterOptionModified(self):
        """A filter option has been modified"""
        if self.__isScriptRunning:
            return

        filtered = []
        if not self.__actionFilterTypeError.isChecked():
            filtered.append(WConsoleType.ERROR)
        if not self.__actionFilterTypeWarning.isChecked():
            filtered.append(WConsoleType.WARNING)
        if not self.__actionFilterTypeInfo.isChecked():
            filtered.append(WConsoleType.INFO)
        if not self.__actionFilterTypeOutput.isChecked():
            filtered.append(WConsoleType.NORMAL)
            filtered.append(WConsoleType.VALID)

        self.__console.setOptionFilteredExtraSelection(self.__actionFilterSearchFoundOnly.isChecked() and (self.__currentOptions & SearchOptions.HIGHLIGHT == SearchOptions.HIGHLIGHT))
        self.__console.setOptionFilteredTypes(filtered)

    def setScriptIsRunning(self, isRunning):
        """Set console 'scriptIsRunning' flag active/inactive"""
        self.__isScriptRunning = isRunning

    def option(self, optionId):
        """Return current option value

        Option Id refer to:                                                 Returned Value
            BPDockWidgetConsoleOutput.OPTION_BTN_REGEX                      Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_CASESENSITIVE              Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_WHOLEWORD                  Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_BACKWARD                   Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_HIGHLIGHT                  Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_BUTTONSHOW                 Boolean
            BPDockWidgetConsoleOutput.OPTION_TXT_SEARCH                     String
            BPDockWidgetConsoleOutput.OPTION_FILTER_TYPES                   List
            BPDockWidgetConsoleOutput.OPTION_FILTER_SEARCH                  Boolean
            BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR                      Boolean
        """
        if optionId & BPDockWidgetConsoleOutput.OPTION_BTN_REGEX == BPDockWidgetConsoleOutput.OPTION_BTN_REGEX:
            return self.__siSearch.options() & SearchOptions.REGEX == SearchOptions.REGEX
        elif optionId & BPDockWidgetConsoleOutput.OPTION_BTN_CASESENSITIVE == BPDockWidgetConsoleOutput.OPTION_BTN_CASESENSITIVE:
            return self.__siSearch.options() & SearchOptions.CASESENSITIVE == SearchOptions.CASESENSITIVE
        elif optionId & BPDockWidgetConsoleOutput.OPTION_BTN_WHOLEWORD == BPDockWidgetConsoleOutput.OPTION_BTN_WHOLEWORD:
            return self.__siSearch.options() & SearchOptions.WHOLEWORD == SearchOptions.WHOLEWORD
        elif optionId & BPDockWidgetConsoleOutput.OPTION_BTN_BACKWARD == BPDockWidgetConsoleOutput.OPTION_BTN_BACKWARD:
            return self.__siSearch.options() & SearchOptions.BACKWARD == SearchOptions.BACKWARD
        elif optionId & BPDockWidgetConsoleOutput.OPTION_BTN_HIGHLIGHT == BPDockWidgetConsoleOutput.OPTION_BTN_HIGHLIGHT:
            return self.__siSearch.options() & SearchOptions.HIGHLIGHT == SearchOptions.HIGHLIGHT
        elif optionId & BPDockWidgetConsoleOutput.OPTION_BTN_BUTTONSHOW == BPDockWidgetConsoleOutput.OPTION_BTN_BUTTONSHOW:
            return self.__siSearch.options() & WSearchInput.OPTION_STATE_BUTTONSHOW == WSearchInput.OPTION_STATE_BUTTONSHOW
        elif optionId & BPDockWidgetConsoleOutput.OPTION_TXT_SEARCH == BPDockWidgetConsoleOutput.OPTION_TXT_SEARCH:
            return self.__siSearch.searchText()
        elif optionId & BPDockWidgetConsoleOutput.OPTION_FILTER_TYPES == BPDockWidgetConsoleOutput.OPTION_FILTER_TYPES:
            returned = []
            if self.__actionFilterTypeError.isChecked():
                returned.append(WConsoleType.ERROR)
            if self.__actionFilterTypeWarning.isChecked():
                returned.append(WConsoleType.WARNING)
            if self.__actionFilterTypeInfo.isChecked():
                returned.append(WConsoleType.INFO)
            if self.__actionFilterTypeOutput.isChecked():
                returned.append(WConsoleType.VALID)
            return returned
        elif optionId & BPDockWidgetConsoleOutput.OPTION_FILTER_SEARCH == BPDockWidgetConsoleOutput.OPTION_FILTER_SEARCH:
            return self.__actionFilterSearchFoundOnly.isChecked()
        elif optionId & BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR == BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR:
            return self.__actionAutoClear.isChecked()

    def setOption(self, optionId, value):
        """Set option value

        Option Id refer to:                                                 Value
            BPDockWidgetConsoleOutput.OPTION_BTN_REGEX                      Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_CASESENSITIVE              Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_WHOLEWORD                  Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_BACKWARD                   Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_HIGHLIGHT                  Boolean
            BPDockWidgetConsoleOutput.OPTION_BTN_BUTTONSHOW                 Boolean
            BPDockWidgetConsoleOutput.OPTION_TXT_SEARCH                     String
            BPDockWidgetConsoleOutput.OPTION_FILTER_TYPES                   List
            BPDockWidgetConsoleOutput.OPTION_FILTER_SEARCH                  Boolean
            BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR                      Boolean
        """
        if optionId & BPDockWidgetConsoleOutput.OPTION_BTN_REGEX == BPDockWidgetConsoleOutput.OPTION_BTN_REGEX:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.REGEX)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.REGEX))
        elif optionId & BPDockWidgetConsoleOutput.OPTION_BTN_CASESENSITIVE == BPDockWidgetConsoleOutput.OPTION_BTN_CASESENSITIVE:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.CASESENSITIVE)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.CASESENSITIVE))
        elif optionId & BPDockWidgetConsoleOutput.OPTION_BTN_WHOLEWORD == BPDockWidgetConsoleOutput.OPTION_BTN_WHOLEWORD:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.WHOLEWORD)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.WHOLEWORD))
        elif optionId & BPDockWidgetConsoleOutput.OPTION_BTN_BACKWARD == BPDockWidgetConsoleOutput.OPTION_BTN_BACKWARD:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.BACKWARD)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.BACKWARD))
        elif optionId & BPDockWidgetConsoleOutput.OPTION_BTN_HIGHLIGHT == BPDockWidgetConsoleOutput.OPTION_BTN_HIGHLIGHT:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.HIGHLIGHT)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.HIGHLIGHT))
        elif optionId & BPDockWidgetConsoleOutput.OPTION_BTN_BUTTONSHOW == BPDockWidgetConsoleOutput.OPTION_BTN_BUTTONSHOW:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | WSearchInput.OPTION_STATE_BUTTONSHOW)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ WSearchInput.OPTION_STATE_BUTTONSHOW))
        elif optionId & BPDockWidgetConsoleOutput.OPTION_TXT_SEARCH == BPDockWidgetConsoleOutput.OPTION_TXT_SEARCH:
            self.__siSearch.setSearchText(value)
        elif optionId & BPDockWidgetConsoleOutput.OPTION_FILTER_TYPES == BPDockWidgetConsoleOutput.OPTION_FILTER_TYPES:
            self.__actionFilterTypeError.setChecked(WConsoleType.ERROR in value)
            self.__actionFilterTypeWarning.setChecked(WConsoleType.WARNING in value)
            self.__actionFilterTypeInfo.setChecked(WConsoleType.INFO in value)
            self.__actionFilterTypeOutput.setChecked(WConsoleType.VALID in value)
        elif optionId & BPDockWidgetConsoleOutput.OPTION_FILTER_SEARCH == BPDockWidgetConsoleOutput.OPTION_FILTER_SEARCH:
            self.__actionFilterSearchFoundOnly.setChecked(value)
        elif optionId & BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR == BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR:
            self.__actionAutoClear.setChecked(value)

    def saveConsole(self, fileName=None):
        """Save console content"""
        if fileName is None:
            save = WDialogFile.saveFile(i18n('Save script output'), '', f"{i18n('Text file')} (*.txt)")
            if save:
                fileName = save['file']

                if not re.search(r"\.txt$", fileName):
                    fileName += '.txt'

        try:
            with open(fileName, 'w') as fHandle:
                fHandle.write(self.__console.toPlainText())
        except Exception as e:
            print(f"Unable to save file: {fileName}", e)
            WDialogMessage.display(i18n('Save script output'), "Unable to save file!")

    def updateSearchAndFilter(self):
        """Update search and filter if needed"""
        if self.__isScriptRunning:
            return

        self.__siSearch.applySearch()
        self.__filterOptionModified()

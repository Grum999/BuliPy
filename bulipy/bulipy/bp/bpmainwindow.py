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

# -----------------------------------------------------------------------------

import os
import re
import sys
import time
import html

from PyQt5.Qt import *
from PyQt5.QtGui import (
        QPalette,
        QPixmap,
        QPainter
    )
from PyQt5.QtCore import (
        pyqtSignal as Signal
    )
from PyQt5.QtWidgets import (
        QMainWindow,
        QStatusBar
    )

from .bplanguagedef import BPLanguageDefPython

from ..pktk.modules.uitheme import UITheme
from ..pktk.modules.utils import loadXmlUi
from ..pktk.modules.imgutils import bullet
from ..pktk.modules.strutils import (
        stripHtml,
        stripTags
    )
from ..pktk.modules.menuutils import buildQMenuTree
from ..pktk.modules.parser import Parser
from ..pktk.modules.tokenizer import TokenizerRule

from ..pktk.widgets.wseparator import WVLine
from ..pktk.widgets.wlabelelide import WLabelElide

from ..pktk.pktk import *


# -----------------------------------------------------------------------------


class BPMainWindow(QMainWindow):
    """BuliPy main window"""

    DARK_THEME = 'dark'
    LIGHT_THEME = 'light'

    STATUSBAR_MODIFICATIONSTATUS = 0
    STATUSBAR_FILENAME = 1
    STATUSBAR_LANGUAGEDEF = 2
    STATUSBAR_RO = 3
    STATUSBAR_POS = 4
    STATUSBAR_SELECTION = 5
    STATUSBAR_INSOVR_MODE = 6
    STATUSBAR_LASTSECTION = 6

    dialogShown = pyqtSignal()

    # region: initialisation methods -------------------------------------------

    def __init__(self, uiController, parent=None):
        super(BPMainWindow, self).__init__(parent)

        uiFileName = os.path.join(os.path.dirname(__file__), 'resources', 'bpmainwindow.ui')
        returnd = loadXmlUi(uiFileName, self)

        self.__uiController = uiController
        self.__eventCallBack = {}

        self.__pixmapBullet = None

        self.__toolbars = []

        self.setDockOptions(QMainWindow.AllowTabbedDocks | QMainWindow.AllowNestedDocks)
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        self.setDocumentMode(False)

        self.setStyleSheet("""
            QToolBar { border-width: 0px; }
            QToolBar QToolButton:checked {
                    background-color: palette(Highlight);
                }

            /* QMenu::icon ==> doesn't work?? */
            QMenu::item:checked:enabled {
                    background-color: palette(Highlight);
                }
        """)

        self.__initStatusBar()
        self.__initBPDocuments()

    def __initStatusBar(self):
        """Initialise status bar

        [ Path/File name    | Column: 999 . Row: 999/999 | Selection: 999 | INSOVR ]
        """
        statusBar = self.statusBar()

        self.__statusBarWidgets = [
                QLabel(),                                   # Modification status
                WLabelElide(Qt.ElideLeft),                  # File name
                QLabel(),                                   # Language definition
                QLabel('RW'),                               # file is in read-write/read-only mode
                QLabel("000:00000/00000"),                  # Current column:row/total number of rows
                QLabel("000:00000 - 000:00000 [000000]"),   # Selection start (col:row) - Selection end (col:row) [selection length]
                QLabel("WWW"),                              # INSert/OVeRwrite
            ]

        for statusBarItem in self.__statusBarWidgets:
            statusBarItem.setFont(statusBar.font())

        fontMetrics = self.__statusBarWidgets[BPMainWindow.STATUSBAR_FILENAME].fontMetrics()

        self.__statusBarWidgets[BPMainWindow.STATUSBAR_MODIFICATIONSTATUS].setMinimumWidth(fontMetrics.boundingRect("RO").width())
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_FILENAME].setMinimumWidth(1)  # can't be 0 (not taken in account)
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_LANGUAGEDEF].setMinimumWidth(1)  # can't be 0 (not taken in account)
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_RO].setMinimumWidth(fontMetrics.boundingRect("RO").width())
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_POS].setMinimumWidth(fontMetrics.boundingRect("000:00000/00000").width())
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_SELECTION].setMinimumWidth(fontMetrics.boundingRect("000:00000 - 000:00000 [000000]").width())
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_INSOVR_MODE].setMinimumWidth(fontMetrics.boundingRect("INS_").width())

        self.__statusBarWidgets[BPMainWindow.STATUSBAR_POS].setAlignment(Qt.AlignRight)
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_SELECTION].setAlignment(Qt.AlignRight)

        self.__statusBarWidgets[BPMainWindow.STATUSBAR_MODIFICATIONSTATUS].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_FILENAME].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_LANGUAGEDEF].setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_RO].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_POS].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_SELECTION].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.__statusBarWidgets[BPMainWindow.STATUSBAR_INSOVR_MODE].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        statusBar.addWidget(self.__statusBarWidgets[BPMainWindow.STATUSBAR_MODIFICATIONSTATUS])
        statusBar.addWidget(self.__statusBarWidgets[BPMainWindow.STATUSBAR_FILENAME])
        statusBar.addPermanentWidget(WVLine())
        statusBar.addPermanentWidget(self.__statusBarWidgets[BPMainWindow.STATUSBAR_LANGUAGEDEF])
        statusBar.addPermanentWidget(WVLine())
        statusBar.addPermanentWidget(self.__statusBarWidgets[BPMainWindow.STATUSBAR_RO])
        statusBar.addPermanentWidget(WVLine())
        statusBar.addPermanentWidget(self.__statusBarWidgets[BPMainWindow.STATUSBAR_POS])
        statusBar.addPermanentWidget(WVLine())
        statusBar.addPermanentWidget(self.__statusBarWidgets[BPMainWindow.STATUSBAR_SELECTION])
        statusBar.addPermanentWidget(WVLine())
        statusBar.addPermanentWidget(self.__statusBarWidgets[BPMainWindow.STATUSBAR_INSOVR_MODE])
        statusBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def __initBPDocuments(self):
        """Initialise documents manager"""
        self.msDocuments.setUiController(self.__uiController)

    def __menuSettingsToolbarsToggled(self, value):
        """A toolbar Sub-menu checkedbox has been changed"""
        action = self.sender()
        action.data().setVisible(value)

    def __menuSettingsToolbarsShow(self):
        """Display toolbar menu"""
        self.menuSettingsToolbars.clear()

        for toolbar in self.__toolbars:
            action = self.menuSettingsToolbars.addAction(toolbar.windowTitle())
            action.setCheckable(True)
            action.setChecked(toolbar.isVisible())
            action.setData(toolbar)
            action.toggled.connect(self.__menuSettingsToolbarsToggled)

    def __menuFileRecentShow(self):
        """Menu for 'file recent' is about to be displayed

        Build menu content
        """
        self.__uiController.buildmenuFileRecent(self.menuFileRecent)

    def __menuAboutToShow(self):
        """menu is about to show, force update"""
        self.__uiController.updateMenu()

    def __actionNotYetImplemented(self, v=None):
        """"Method called when an action not yet implemented is triggered"""
        QMessageBox.warning(
                QWidget(),
                self.__uiController.name(),
                i18n(f"Sorry! Action has not yet been implemented ({v})")
            )

    def showEvent(self, event):
        """Event trigerred when dialog is shown

           At this time, all widgets are initialised and size/visiblity is known


           Example
           =======
                # define callback function
                def my_callback_function():
                    # BPMa__menuEditShowinWindow shown!
                    pass

                # initialise a dialog from an xml .ui file
                dlgMain = BPMainWindow.loadUi(uiFileName)

                # execute my_callback_function() when dialog became visible
                dlgMain.dialogShown.connect(my_callback_function)
        """
        super(BPMainWindow, self).showEvent(event)

        pixmapBullet = bullet(self.__statusBarWidgets[BPMainWindow.STATUSBAR_MODIFICATIONSTATUS].height()//2, self.palette().color(QPalette.Active, QPalette.Highlight), 'circle')
        self.__pixmapBullet = QPixmap(self.__statusBarWidgets[BPMainWindow.STATUSBAR_MODIFICATIONSTATUS].size())
        self.__pixmapBullet.fill(Qt.transparent)
        painter = QPainter(self.__pixmapBullet)
        painter.drawPixmap((self.__pixmapBullet.width() - pixmapBullet.width())//2, (self.__pixmapBullet.height() - pixmapBullet.height())//2, pixmapBullet)
        painter.end()

        self.dialogShown.emit()

    def closeEvent(self, event):
        """Event executed when window is about to be closed"""
        # event.ignore()
        self.__uiController.close()
        event.accept()

    def eventFilter(self, object, event):
        """Manage event filters for window"""
        if object in self.__eventCallBack.keys():
            return self.__eventCallBack[object](event)

        return super(BPMainWindow, self).eventFilter(object, event)

    def setEventCallback(self, object, method):
        """Add an event callback method for given object

           Example
           =======
                # define callback function
                def my_callback_function(event):
                    if event.type() == QEvent.xxxx:
                        # Event!
                        return True
                    return False


                # initialise a dialog from an xml .ui file
                dlgMain = BPMainWindow.loadUi(uiFileName)

                # define callback for widget from ui
                dlgMain.setEventCallback(dlgMain.my_widget, my_callback_function)
        """
        if object is None:
            return False

        self.__eventCallBack[object] = method
        object.installEventFilter(self)

    def initToolbar(self, toolbarsConfig, toolbarsSession=None):
        """Initialise toolbars

        Given `toolbars` is a list of dictionary
        Each dictionary contains at least the following keys:
            id: toolbar id
            label : toolbar label
            actions: list of QAction id

        Can additionally contains:
            visible: toolbar is visible or hidden
            area: area in which toolbar is docked
            rect: position+size of toolbar
        """
        def sortToolbar(toolbarSessionDef):

            if toolbarSessionDef['area'] in (Qt.LeftToolBarArea, Qt.RightToolBarArea):
                return f"{toolbarSessionDef['area']:02}{toolbarSessionDef['rect'][0]:05}{toolbarSessionDef['rect'][1]:05}"
            else:
                return f"{toolbarSessionDef['area']:02}{toolbarSessionDef['rect'][1]:05}{toolbarSessionDef['rect'][0]:05}"

        # Disable window updates while preparing content (avoid flickering effect)
        self.setUpdatesEnabled(False)

        for toolbar in self.toolbarList():
            self.removeToolBar(toolbar)
        self.__toolbars = []

        # sort toolbar by area/position
        sortedId = []
        if toolbarsSession is not None:
            toolbarsSession.sort(key=sortToolbar)

            tmp = {toolbarDefinition['id']: toolbarDefinition for toolbarDefinition in toolbarsConfig}
            toolbarsConfigSorted = []
            for toolbarId in [toolbarSession['id'] for toolbarSession in toolbarsSession]:
                if toolbarId in tmp:
                    toolbarsConfigSorted.append(tmp.pop(toolbarId))

            for toolbarDefinition in toolbarsConfig:
                if toolbarDefinition['id'] in tmp:
                    toolbarsConfigSorted.append(toolbarDefinition)

            toolbarsConfig = toolbarsConfigSorted

        for toolbarDefinition in toolbarsConfig:
            toolbar = self.addToolBar(toolbarDefinition['label'])
            toolbar.setObjectName(toolbarDefinition['id'])
            toolbar.setToolButtonStyle(1)
            toolbar.setToolButtonStyle(toolbarDefinition['style'])
            toolbar.setFloatable(False)
            for action in toolbarDefinition['actions']:
                if action == 'ba32b31ff4730cbf42ba0962f981407bcb4e9c58':  # separator Id
                    toolbar.addSeparator()
                else:
                    foundAction = self.findChild(QAction, action, Qt.FindChildrenRecursively)
                    if foundAction:
                        toolbar.addAction(foundAction)
            self.__toolbars.append(toolbar)

        if toolbarsSession is not None:
            for toolbarSession in toolbarsSession:
                for toolbar in self.__toolbars:
                    if toolbar.objectName() == toolbarSession['id']:
                        if toolbarSession['break']:
                            self.addToolBarBreak(toolbarSession['area'])
                        self.addToolBar(toolbarSession['area'], toolbar)
                        geometry = toolbarSession['rect']
                        toolbar.setVisible(toolbarSession['visible'])
                        # not working...?
                        # toolbar.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
                        break

        self.menuSettingsToolbars.setEnabled(len(self.__toolbars) > 0)
        self.setUpdatesEnabled(True)

    def toolbarList(self):
        """Return list of toolbar"""
        return self.__toolbars

    def initMainView(self):
        """Initialise main view content"""
        pass

    def initMenu(self):
        """Initialise actions for menu defaukt menu"""

        # Menu SCRIPT
        # ----------------------------------------------------------------------
        self.actionFileNew.triggered.connect(self.__uiController.commandFileNew)
        self.actionFileOpen.triggered.connect(self.__uiController.commandFileOpen)
        self.actionFileReload.triggered.connect(self.__uiController.commandFileReload)
        self.actionFileSave.triggered.connect(self.__uiController.commandFileSave)
        self.actionFileSaveAs.triggered.connect(self.__uiController.commandFileSaveAs)
        self.actionFileSaveAll.triggered.connect(self.__uiController.commandFileSaveAll)
        self.actionFileClose.triggered.connect(self.__uiController.commandFileClose)
        self.actionFileCloseAll.triggered.connect(self.__uiController.commandFileCloseAll)
        self.actionFileQuit.triggered.connect(self.__uiController.commandQuit)

        self.menuFileRecent.aboutToShow.connect(self.__menuFileRecentShow)
        self.menuFile.aboutToShow.connect(self.__menuAboutToShow)

        # Menu EDIT
        # ----------------------------------------------------------------------
        self.actionEditUndo.triggered.connect(self.__uiController.commandEditUndo)
        self.actionEditRedo.triggered.connect(self.__uiController.commandEditRedo)
        self.actionEditCut.triggered.connect(self.__uiController.commandEditCut)
        self.actionEditCopy.triggered.connect(self.__uiController.commandEditCopy)
        self.actionEditPaste.triggered.connect(self.__uiController.commandEditPaste)
        self.actionEditSelectAll.triggered.connect(self.__uiController.commandEditSelectAll)
        self.actionEditSearchReplace.triggered.connect(lambda: self.__uiController.commandEditDockSearchAndReplaceVisible(True))

        self.actionEditCodeComment.triggered.connect(self.__uiController.commandEditComment)
        self.actionEditCodeIndent.triggered.connect(self.__uiController.commandEditIndent)
        self.actionEditCodeDedent.triggered.connect(self.__uiController.commandEditDedent)
        self.actionEditDeleteLine.triggered.connect(self.__uiController.commandEditDeleteLine)
        self.actionEditDuplicateLine.triggered.connect(self.__uiController.commandEditDuplicateLine)
        self.actionEditOverwriteMode.triggered.connect(lambda: self.__uiController.commandEditOverwriteMode())
        self.actionEditReadOnlyMode.triggered.connect(lambda: self.__uiController.commandEditReadOnlyMode())
        self.actionEditGoToLine.triggered.connect(self.__uiController.commandEditGoToLine)

        self.menuEdit.aboutToShow.connect(self.__menuAboutToShow)

        # Menu VIEW
        # ----------------------------------------------------------------------
        self.actionViewWrapLines.triggered.connect(self.__uiController.commandViewWrapLines)
        self.actionViewShowRightLimit.triggered.connect(self.__uiController.commandViewShowRightLimit)
        self.actionViewShowLineNumber.triggered.connect(self.__uiController.commandViewShowLineNumber)
        self.actionViewShowSpaces.triggered.connect(self.__uiController.commandViewShowSpaces)
        self.actionViewShowIndent.triggered.connect(self.__uiController.commandViewShowIndent)
        self.actionViewHighlightClassesFunctionDeclaration.triggered.connect(self.__uiController.commandViewHighlightClassesFunctionDeclaration)

        self.menuView.aboutToShow.connect(self.__menuAboutToShow)

        # Menu SCRIPT
        # ----------------------------------------------------------------------
        self.actionScriptExecute.triggered.connect(self.__uiController.commandScriptExecute)
        self.actionScriptBreakPause.triggered.connect(self.__uiController.commandScriptBreakPause)
        self.actionScriptStop.triggered.connect(self.__uiController.commandScriptStop)
        self.actionScriptDockOutputConsole.triggered.connect(lambda: self.__uiController.commandScriptDockOutputConsoleVisible(True))

        self.menuScript.aboutToShow.connect(self.__menuAboutToShow)

        # Menu TOOLS
        # ----------------------------------------------------------------------
        self.actionToolsColorPicker.triggered.connect(self.__uiController.commandToolsDockColorPickerVisible)
        self.actionToolsIconsSelector.triggered.connect(self.__uiController.commandToolsDockIconSelectorVisible)
        self.actionToolsDocuments.triggered.connect(self.__uiController.commandToolsDockDocumentsVisible)

        self.actionToolsCopyFullPathFileName.triggered.connect(self.__uiController.commandToolsCopyFullPathFileName)
        self.actionToolsCopyPathName.triggered.connect(self.__uiController.commandToolsCopyPathName)
        self.actionToolsCopyFileName.triggered.connect(self.__uiController.commandToolsCopyFileName)
        self.actionToolsMDocSortAscending.triggered.connect(self.__uiController.commandToolsMDocSortAscending)
        self.actionToolsMDocSortDescending.triggered.connect(self.__uiController.commandToolsMDocSortDescending)
        self.actionToolsMDocRemoveDuplicateLines.triggered.connect(self.__uiController.commandToolsMDocRemoveDuplicateLines)
        self.actionToolsMDocRemoveEmptyLines.triggered.connect(self.__uiController.commandToolsMDocRemoveEmptyLines)
        self.actionToolsMDocTrimSpaces.triggered.connect(self.__uiController.commandToolsMDocTrimSpaces)
        self.actionToolsMDocTrimLeadingSpaces.triggered.connect(self.__uiController.commandToolsMDocTrimLeadingSpaces)
        self.actionToolsMDocTrimTrailingSpaces.triggered.connect(self.__uiController.commandToolsMDocTrimTrailingSpaces)
        self.actionToolsMDocPrettify.triggered.connect(self.__uiController.commandToolsMDocPrettify)

        self.menuTools.aboutToShow.connect(self.__menuAboutToShow)

        # Menu SETTINGS
        # ----------------------------------------------------------------------
        self.actionSettingsPreferences.triggered.connect(self.__uiController.commandSettingsOpen)

        self.menuSettings.aboutToShow.connect(self.__menuAboutToShow)
        self.menuSettingsToolbars.aboutToShow.connect(self.__menuSettingsToolbarsShow)

        # Menu HELP
        # ----------------------------------------------------------------------
        self.actionHelpAboutBP.triggered.connect(self.__uiController.commandAboutBp)

    def getWidgets(self):
        """Return a list of ALL widgets"""
        def appendWithSubWidget(parent):
            list = [parent]
            if len(parent.children()) > 0:
                for w in parent.children():
                    list += appendWithSubWidget(w)
            return list

        return appendWithSubWidget(self)

    def statusBarText(self, index):
        """Return text in status bar section designed by `index`"""
        if not isinstance(index, int):
            raise EInvalidStatus("Given `index` must be <int>")
        elif index < 0 or index > BPMainWindow.STATUSBAR_LASTSECTION:
            raise EInvalidValue(f"Given `index` must be between 0 and {BPMainWindow.STATUSBAR_LASTSECTION}")
        return self.__statusBarWidgets[index].text()

    def setStatusBarText(self, index, text):
        """Set given `text` in status bar section designed by `index`"""
        if not isinstance(index, int):
            raise EInvalidStatus("Given `index` must be <int>")
        elif index < 0 or index > BPMainWindow.STATUSBAR_LASTSECTION:
            raise EInvalidValue(f"Given `index` must be between 0 and {BPMainWindow.STATUSBAR_LASTSECTION}")

        if index == BPMainWindow.STATUSBAR_MODIFICATIONSTATUS:
            if text is True and self.__pixmapBullet:
                self.__statusBarWidgets[index].setPixmap(self.__pixmapBullet)
                self.__statusBarWidgets[index].setToolTip(i18n("Modified file not saved"))
            else:
                self.__statusBarWidgets[index].setText(' ')
                self.__statusBarWidgets[index].setToolTip(i18n("Unmodified file"))
        elif self.__statusBarWidgets[index].text() != text:
            self.__statusBarWidgets[index].setText(text)

            if index == BPMainWindow.STATUSBAR_INSOVR_MODE:
                if text == 'INS':
                    self.__statusBarWidgets[index].setToolTip(i18n("INSERT mode"))
                else:
                    self.__statusBarWidgets[index].setToolTip(i18n("OVERWRITE mode"))
            elif index == BPMainWindow.STATUSBAR_RO:
                if text == 'RO':
                    self.__statusBarWidgets[index].setToolTip(i18n("Read-Only mode"))
                else:
                    self.__statusBarWidgets[index].setToolTip(i18n("Read-Write mode"))

            if len(text) == 0:
                self.__statusBarWidgets[index].setToolTipDuration(1)
            else:
                self.__statusBarWidgets[index].setToolTipDuration(30)

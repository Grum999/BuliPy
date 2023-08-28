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

        self.setDockOptions(QMainWindow.AllowTabbedDocks | QMainWindow.AllowNestedDocks)
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        self.setDocumentMode(False)

        self.__initStatusBar()
        self.__initBPDocuments()

    def __initStatusBar(self):
        """Initialise status bar

        [ Path/File name    | Column: 999 . Row: 999/999 | Selection: 999 | INSOVR ]
        """
        self.__statusBarWidgets = [
                QLabel(),                                   # Modification status
                WLabelElide(Qt.ElideLeft),                  # File name
                QLabel(),                                   # Language definition
                QLabel('RW'),                               # file is in read-write/read-only mode
                QLabel("000:00000/00000"),                  # Current column:row/total number of rows
                QLabel("000:00000 - 000:00000 [000000]"),   # Selection start (col:row) - Selection end (col:row) [selection length]
                QLabel("WWW"),                              # INSert/OVeRwrite
            ]

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

        statusBar = self.statusBar()
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
        self.actionEditSearchReplace.triggered.connect(lambda: self.__uiController.commandViewDockSearchAndReplaceVisible(True))

        self.menuEdit.aboutToShow.connect(self.__menuAboutToShow)

        # Menu SCRIPT
        # ----------------------------------------------------------------------
        self.actionScriptExecute.triggered.connect(self.__uiController.commandScriptExecute)
        self.actionScriptBreakPause.triggered.connect(self.__uiController.commandScriptBreakPause)
        self.actionScriptStop.triggered.connect(self.__uiController.commandScriptStop)
        self.actionScriptOutputConsole.triggered.connect(self.__uiController.commandViewDockConsoleOutputVisible)

        self.menuScript.aboutToShow.connect(self.__menuAboutToShow)

        # Menu TOOLS
        # ----------------------------------------------------------------------
        self.actionToolsColorPicker.triggered.connect(self.__uiController.commandViewDockColorPickerVisible)
        # self.actionToolsIconsSelector.triggered.connect(self.__uiController.commandViewDockConsoleOutputVisible)

        # Menu SETTINGS
        # ----------------------------------------------------------------------
        self.actionSettingsPreferences.triggered.connect(self.__uiController.commandSettingsOpen)

        # Menu HELP
        # ----------------------------------------------------------------------
        self.actionHelpAboutBP.triggered.connect(self.__uiController.commandAboutBp)

    def __menuFileRecentShow(self):
        """Menu for 'file recent' is about to be displayed

        Build menu content
        """
        self.__uiController.buildmenuFileRecent(self.menuFileRecent)

    def __menuAboutToShow(self):
        """menu is about to show, update it if needed"""
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

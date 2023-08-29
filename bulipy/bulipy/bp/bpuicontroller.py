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

import os
from pathlib import Path

import sys
import re
import base64
import traceback
import platform
import time

from krita import Krita

from PyQt5.Qt import *
from PyQt5.QtGui import (
        QColor,
        QGuiApplication,
        QTextCursor
    )
from PyQt5.QtCore import (
        pyqtSignal as Signal,
        QDir,
        QRect,
        QT_VERSION_STR,
        PYQT_VERSION_STR
    )

from PyQt5.QtWidgets import (
        QMessageBox,
        QWidget
    )

from .bpdwconsole import BPDockWidgetConsoleOutput
from .bpdwcolorpicker import BPDockWidgetColorPicker
from .bpdwsearchreplace import BPDockWidgetSearchReplace
from .bpwopensavedialog import BPWOpenSave

from .bppyrunner import (BPPyRunner, BPLogger)
from .bpdocument import (WBPDocument, BPDocuments)
from .bphistory import BPHistory
from .bplanguagedef import (
        BPLanguageDefPython,
        BPLanguageDefText,
        BPLanguageDefUnmanaged
    )
from .bpmainwindow import BPMainWindow
from .bpsettings import (
        BPSettings,
        BPSettingsKey
    )

from ..pktk.modules.languagedef import (
        LanguageDefXML,
        LanguageDefJSON
    )
from ..pktk.modules.tokenizer import TokenizerRule
from ..pktk.modules.uitheme import UITheme
from ..pktk.modules.utils import (
        checkKritaVersion,
        Debug
    )
from ..pktk.modules.imgutils import buildIcon
from ..pktk.widgets.wabout import WAboutWindow
from ..pktk.widgets.wconsole import WConsoleType

from ..pktk.pktk import *


# ------------------------------------------------------------------------------
class BPUIController(QObject):
    """The controller provide an access to all BuliPy functions"""
    bpWindowShown = Signal()
    bpWindowClosed = Signal()

    # set a timeout of 250ms for default delayed cache save
    __DELAYED_SAVECACHE_TIMEOUT = 250

    def __init__(self, bpName="BuliPy", bpVersion="testing", kritaIsStarting=False):
        super(BPUIController, self).__init__(None)

        self.__pbStarted = False
        self.__pbStarting = False

        self.__window = None
        self.__bpName = bpName
        self.__bpVersion = bpVersion
        self.__pbTitle = "{0} - {1}".format(bpName, bpVersion)

        self.__languageDefPython = BPLanguageDefPython()
        self.__languageDefXml = LanguageDefXML()
        self.__languageDefJson = LanguageDefJSON()
        self.__languageDefText = BPLanguageDefText()
        self.__languageDefUnmanaged = BPLanguageDefUnmanaged()

        BPSettings.load()

        UITheme.load()
        # BP theme must be loaded before systray is initialized

        # store a global reference to activeWindow to be able to work with
        # activeWindow signals
        # https://krita-artists.org/t/krita-4-4-new-api/12247?u = grum999
        self.__kraActiveWindow = None

        # keep in memory last directory from open/save dialog box
        self.__lastDocumentDirectoryOpen = ""
        self.__lastDocumentDirectorySave = ""

        # keep document history list
        self.__historyFiles = BPHistory()

        # clipboard
        self.__clipboard = QGuiApplication.clipboard()
        self.__clipboard.changed.connect(self.__updateMenuEditPaste)

        # cache directory
        self.__pbCachePath = os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "bulipy")
        try:
            os.makedirs(self.__pbCachePath, exist_ok=True)
            for subDirectory in ['documents']:
                os.makedirs(self.cachePath(subDirectory), exist_ok=True)
        except Exception as e:
            Debug.print('[BPUIController.__init__] Unable to create directory {0}: {1}', self.cachePath(subDirectory), str(e))

        # document manager
        self.__documents = BPDocuments(self)
        self.__documents.documentAdded.connect(self.__documentAdded)
        self.__documents.documentRemoved.connect(self.__documentRemoved)
        self.__documents.documentSaved.connect(self.__documentSaved)
        self.__documents.documentReloaded.connect(self.__documentReloaded)
        self.__documents.activeDocumentChanged.connect(self.__documentChanged)
        self.__documents.readOnlyModeChanged.connect(self.__documentReadOnlyModeChanged)
        self.__documents.overwriteModeChanged.connect(self.__documentOverwriteModeChanged)
        self.__documents.cursorCoordinatesChanged.connect(self.__documentCursorCoordinatesChanged)
        self.__documents.modificationChanged.connect(self.__documentModificationChanged)
        self.__documents.textChanged.connect(self.__delayedDocumentSaveCache)
        self.__documents.redoAvailable.connect(self.__invalidateMenu)
        self.__documents.undoAvailable.connect(self.__invalidateMenu)
        self.__documents.selectionChanged.connect(self.__delayedDocumentSaveCache)
        self.__documents.copyAvailable.connect(self.__invalidateMenu)
        self.__documents.languageDefChanged.connect(self.__documentLanguageDefChanged)

        # current active document
        self.__currentDocument = None

        self.__initialised = False

        # dockers
        self.__dwConsoleOutput = None
        self.__dwColorPicker = None
        self.__dwSearchReplace = None

        self.__dwConsoleOutputAction = None
        self.__dwColorPickerAction = None
        self.__dwSearchReplaceAction = None

        # -- misc
        # editor/syntax theme
        self.__theme = ''

        # flag to determinate if menu has to be updated or not
        self.__menuInvalidated = True

        # to save session
        self.__delayedSaveTimer = QTimer()
        self.__delayedSaveTimer.timeout.connect(lambda: self.saveSettings())

        if kritaIsStarting and BPSettings.get(BPSettingsKey.CONFIG_OPEN_ATSTARTUP):
            self.start()

    def start(self):
        """Start plugin interface"""
        if self.__pbStarted:
            # user interface is already started, bring to front and exit
            self.commandViewBringToFront()
            return
        elif self.__pbStarting:
            # user interface is already starting, exit
            return

        self.__pbStarting = True

        # Check if windows are opened and then, connect signal if needed
        self.__checkKritaWindows()

        self.__initialised = False
        self.__window = BPMainWindow(self)
        self.__window.dialogShown.connect(self.__initSettings)

        # initialise docker widgets
        self.__dwConsoleOutput = BPDockWidgetConsoleOutput(self.__window, self.__documents)
        self.__dwConsoleOutput.setObjectName('__dwConsoleOutput')
        self.__dwConsoleOutputAction = self.__dwConsoleOutput.toggleViewAction()
        self.__dwConsoleOutputAction.setText(i18n("Console output"))
        self.__window.addDockWidget(Qt.BottomDockWidgetArea, self.__dwConsoleOutput)
        self.__dwConsoleOutput.sourceRefClicked.connect(lambda source, fromPosition, toPosition: self.commandScriptGoToLine(fromPosition, toPosition, source, True))
        self.__dwConsoleOutput.consoleClear.connect(self.commandToolsShowVersion)

        self.__dwColorPicker = BPDockWidgetColorPicker(self.__window, self.__documents)
        self.__dwColorPicker.setObjectName('__dwColorPicker')
        self.__dwColorPicker.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.__dwColorPicker.apply.connect(self.commandColorCodeInsert)
        self.__dwColorPickerAction = self.__dwColorPicker.toggleViewAction()
        self.__dwColorPickerAction.setText(i18n("Color picker"))
        self.__window.addDockWidget(Qt.RightDockWidgetArea, self.__dwColorPicker)

        self.__dwSearchReplace = BPDockWidgetSearchReplace(self.__window, self.__documents)
        self.__dwSearchReplace.setObjectName('__dwSearchReplace')
        # self.__dwSearchReplace.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        self.__dwSearchReplaceAction = self.__dwSearchReplace.toggleViewAction()
        self.__dwSearchReplaceAction.setText(i18n("Search & Replace"))
        self.__window.addDockWidget(Qt.BottomDockWidgetArea, self.__dwSearchReplace)

        self.__window.setWindowTitle(self.__pbTitle)
        self.__window.show()
        self.__window.activateWindow()

        # after window is visible to let switch automatically to the tab
        self.commandViewDockConsoleOutputVisible(True)

    def __initSettings(self):
        """There's some visual settings that need to have the window visible
        (ie: the widget size are known) to be applied
        """
        if self.__initialised:
            self.__pbStarted = True
            self.bpWindowShown.emit()
            # already initialised, do nothing
            return

        # Here we know we have an active window
        if self.__kraActiveWindow is None:
            self.__kraActiveWindow = Krita.instance().activeWindow()
        try:
            # should not occurs as uicontroller is initialised only once, but...
            self.__kraActiveWindow.themeChanged.disconnect(self.__themeChanged)
        except Exception:
            pass

        self.__kraActiveWindow.themeChanged.connect(self.__themeChanged)

        self.__window.initMainView()

        # reload
        BPSettings.load()

        self.commandSettingsSaveSessionOnExit(BPSettings.get(BPSettingsKey.CONFIG_SESSION_SAVE))
        self.commandSettingsOpenAtStartup(BPSettings.get(BPSettingsKey.CONFIG_OPEN_ATSTARTUP))

        self.commandViewMainWindowGeometry(BPSettings.get(BPSettingsKey.SESSION_MAINWINDOW_WINDOW_GEOMETRY))
        self.commandViewMainWindowMaximized(BPSettings.get(BPSettingsKey.SESSION_MAINWINDOW_WINDOW_MAXIMIZED))

        qtlayoutNfoB64 = BPSettings.get(BPSettingsKey.SESSION_MAINWINDOW_VIEW_DOCKERS_LAYOUT)
        if qtlayoutNfoB64 != '':
            qtLayoutNfo = base64.b64decode(qtlayoutNfoB64.encode())
            self.__window.restoreState(qtLayoutNfo)

        self.__lastDocumentDirectoryOpen = BPSettings.get(BPSettingsKey.SESSION_PATH_LASTOPENED)
        self.__lastDocumentDirectorySave = BPSettings.get(BPSettingsKey.SESSION_PATH_LASTSAVED)

        # no ui controller command for dockers
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BTN_BUTTONSHOW, BPSettings.get(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_VISIBLE))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BTN_REGEX, BPSettings.get(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_REGEX_CHECKED))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BTN_CASESENSITIVE, BPSettings.get(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_CASESENSITIVE_CHECKED))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BTN_WHOLEWORD, BPSettings.get(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_WHOLEWORD_CHECKED))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BTN_BACKWARD, BPSettings.get(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_BACKWARD_CHECKED))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BTN_HIGHLIGHT, BPSettings.get(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_HIGHLIGHTALL_CHECKED))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_TXT_SEARCH, BPSettings.get(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_TEXT))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_FILTER_TYPES, [WConsoleType.fromStr(type) for type in BPSettings.get(BPSettingsKey.SESSION_DOCKER_CONSOLE_OPTIONS_FILTER_TYPES)])
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_FILTER_SEARCH, BPSettings.get(BPSettingsKey.SESSION_DOCKER_CONSOLE_OPTIONS_FILTER_SEARCH))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR, BPSettings.get(BPSettingsKey.SESSION_DOCKER_CONSOLE_OPTIONS_AUTOCLEAR))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_FONTSIZE, BPSettings.get(BPSettingsKey.SESSION_DOCKER_CONSOLE_OUTPUT_FONT_SIZE))

        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BUFFER_SIZE, BPSettings.get(BPSettingsKey.CONFIG_DOCKER_CONSOLE_BUFFERSIZE))

        self.__dwColorPicker.setOptions(BPSettings.get(BPSettingsKey.SESSION_DOCKER_COLORPICKER_MENU_SELECTED))

        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_BTN_REGEX, BPSettings.get(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_REGEX_CHECKED))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_BTN_CASESENSITIVE, BPSettings.get(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_CASESENSITIVE_CHECKED))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_BTN_WHOLEWORD, BPSettings.get(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_WHOLEWORD_CHECKED))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_BTN_BACKWARD, BPSettings.get(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_BACKWARD_CHECKED))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_BTN_HIGHLIGHT, BPSettings.get(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_HIGHLIGHTALL_CHECKED))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_TXT_SEARCH, BPSettings.get(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_TEXT))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_TXT_REPLACE, BPSettings.get(BPSettingsKey.SESSION_DOCKER_SAR_REPLACE_TEXT))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_FONTSIZE, BPSettings.get(BPSettingsKey.SESSION_DOCKER_SAR_OUTPUT_FONT_SIZE))

        # do not load from here, already loaded from BPDocuments() initialisation
        # for fileName in BPSettings.get(BPSettingsKey.SESSION_DOCUMENTS_OPENED):
        #     self.__documents.openDocument(fileName)

        self.__historyFiles.setMaxItems(BPSettings.get(BPSettingsKey.CONFIG_SESSION_DOCUMENTS_RECENTS_COUNT))
        self.__historyFiles.setItems(BPSettings.get(BPSettingsKey.SESSION_DOCUMENTS_RECENTS))
        self.__historyFiles.removeMissingFiles()

        self.__documents.initialise(BPSettings.get(BPSettingsKey.SESSION_DOCUMENTS_OPENED), BPSettings.get(BPSettingsKey.SESSION_DOCUMENTS_ACTIVE))

        self.__window.initMenu()

        self.__initialised = True
        self.__pbStarted = True
        self.__pbStarting = False

        self.bpWindowShown.emit()

        self.__currentDocument = self.__documents.document()
        self.__invalidateMenu()

    def __themeChanged(self):
        """Theme has been changed, reload resources"""
        UITheme.reloadResources()

    def __invalidateMenu(self):
        """Invalidate menu..."""
        self.__menuInvalidated = True

    def __documentChanged(self, document):
        """Current active document has been changed"""
        self.__currentDocument = document
        self.__window.msDocuments.setActive(self.__currentDocument)
        self.__updateDockersContent(self.__currentDocument)
        self.__updateStatusUiOverwrite(self.__currentDocument)
        self.__updateStatusUiCursor(self.__currentDocument)
        self.__updateStatusUiFileName(self.__currentDocument)
        self.__updateStatusUiLanguageDef(self.__currentDocument)
        self.__updateStatusUiReadOnly(self.__currentDocument)
        self.__updateStatusUiModified(self.__currentDocument)
        self.__invalidateMenu()
        if BPLogger.reloadCacheConsole(self.__dwConsoleOutput, self.__currentDocument.cacheFileNameConsole()) is False:
            self.commandToolsShowVersion()

    def __documentAdded(self, document):
        """New document added (new file or opened file)"""
        # added document automatically active document
        # then __documentChanged() already executed
        # need to update UI to add document
        self.__window.msDocuments.addDocument(document)

    def __documentRemoved(self, document):
        """A document has been closed"""
        # another document is automatically active
        # then __documentChanged() already executed
        # need to update UI to remove document
        self.__window.msDocuments.removeDocument(document)

    def __documentSaved(self, document):
        """A document has been saved"""
        # need to update UI
        self.__updateStatusUiFileName(document)
        self.__updateStatusUiModified(document)

    def __documentReloaded(self, document):
        """A document has been reloaded"""
        # need to update UI
        self.__updateDockersContent(document)
        self.__updateStatusUiCursor(document)
        self.__updateStatusUiFileName(document)
        self.__updateStatusUiModified(document)

    def __documentReadOnlyModeChanged(self, document):
        """A document read only status has been modified"""
        self.__updateStatusUiReadOnly(document)

    def __documentOverwriteModeChanged(self, document):
        """A document INSERT/OVERWRITE mode has been modified"""
        self.__updateStatusUiOverwrite(document)

    def __documentCursorCoordinatesChanged(self, document):
        """A document cursor position/selection has been modified"""
        self.__updateStatusUiCursor(document)
        self.__delayedDocumentSaveCache(document)

    def __documentModificationChanged(self, document):
        """A document status has been changed"""
        self.__updateStatusUiModified(document)
        self.__delayedDocumentSaveCache(document)

    def __documentLanguageDefChanged(self, document):
        """A document language definition has been changed"""
        self.__updateStatusUiLanguageDef(document)
        self.__delayedDocumentSaveCache(document)

    def __checkKritaWindows(self):
        """Check if windows signal windowClosed() is already defined and, if not,
        define it
        """
        # applicationClosing signal can't be used, because when while BP is opened,
        # application is still running and then signal is not trigerred..
        #
        # solution is, when a window is closed, to check how many windows are still
        # opened
        #
        for window in Krita.instance().windows():
            # DO NOT SET PROPERTY ON WINDOW
            # but on qwindow() as the qwindow() is always the same
            # and as window is just an instance that wrap the underlied QMainWindow
            # a new object is returned each time windows() list is returned
            if window.qwindow().property('__pbWindowClosed') is not True:
                window.windowClosed.connect(self.__windowClosed)
                window.qwindow().setProperty('__pbWindowClosed', True)

    def __windowClosed(self):
        """A krita window has been closed"""
        # check how many windows are still opened
        # if there's no window opened, close BP

        # need to ensure that all windows are connected to close signal
        # (maybe, since BS has been opened, new Krita windows has been created...)
        self.__checkKritaWindows()

        if len(Krita.instance().windows()) == 0:
            self.commandQuit()

    def __updateMenuEditPaste(self):
        """Update menu Edit > Paste according to clipboard content"""
        if self.__currentDocument:
            scriptIsRunning = False
            self.__window.actionEditPaste.setEnabled(self.__currentDocument.codeEditor().canPaste() and not (scriptIsRunning or self.__currentDocument.readOnly()))

    def __updateDockersContent(self, document):
        """Update docker content according to given document"""
        pass

    def __updateStatusUiOverwrite(self, document):
        """Update UI to take in account INS/OVR mode for document"""
        if document == self.__currentDocument:
            if self.__currentDocument.codeEditor().overwriteMode():
                self.__window.setStatusBarText(self.__window.STATUSBAR_INSOVR_MODE, 'OVR')
            else:
                self.__window.setStatusBarText(self.__window.STATUSBAR_INSOVR_MODE, 'INS')

    def __updateStatusUiCursor(self, document):
        """Update UI to take in account current position of cursor in document
            - Cursor position
            - Current selection
        """
        if document == self.__currentDocument:
            self.__window.statusBar().setUpdatesEnabled(False)

            position = self.__currentDocument.codeEditor().cursorPosition()
            self.__window.setStatusBarText(self.__window.STATUSBAR_POS, f'{position[0].x()}:{position[0].y()}/{self.__currentDocument.codeEditor().blockCount()}')

            if position[3] == 0:
                # no selection
                self.__window.setStatusBarText(self.__window.STATUSBAR_SELECTION, '')
                self.__updateDockersContent(document)
            else:
                # selection...
                self.__window.setStatusBarText(self.__window.STATUSBAR_SELECTION, f'{position[1].x()}:{position[1].y()} - {position[2].x()}:{position[2].y()} [{position[3]}]')
                self.__invalidateMenu()
            self.__window.statusBar().setUpdatesEnabled(True)

    def __updateStatusUiFileName(self, document):
        """Update UI to take in account file name of document"""
        self.__window.msDocuments.updateDocument(document)

        if document == self.__currentDocument:
            self.__window.setStatusBarText(self.__window.STATUSBAR_FILENAME, self.__currentDocument.tabName(True))

    def __updateStatusUiLanguageDef(self, document):
        """Update UI to take in account language definition of document"""
        if document == self.__currentDocument:
            languageDef = self.__currentDocument.languageDefinition()

            textNfo = languageDef.name()

            if textNfo == 'Unmanaged':
                if fileExtension := re.search(r"\.([^\.]*)$", document.fileName()):
                    textNfo = f"{i18n('Unmanaged')} (.{fileExtension.groups()[0]})"
                else:
                    textNfo = i18n('Unmanaged')

            self.__window.setStatusBarText(self.__window.STATUSBAR_LANGUAGEDEF, textNfo)

    def __updateStatusUiReadOnly(self, document):
        """Update UI to take in account R/W status of document"""
        if document == self.__currentDocument:
            if self.__currentDocument.readOnly():
                self.__window.setStatusBarText(self.__window.STATUSBAR_RO, 'RO')
            else:
                self.__window.setStatusBarText(self.__window.STATUSBAR_RO, 'RW')
            self.__invalidateMenu()

    def __updateStatusUiModified(self, document):
        """Update UI to take in account modified status of document"""
        self.__window.msDocuments.updateDocument(document)
        self.__window.setStatusBarText(self.__window.STATUSBAR_MODIFICATIONSTATUS, self.__currentDocument.modified())
        self.__invalidateMenu()

    def __delayedDocumentSaveCache(self, document):
        self.__invalidateMenu()
        if BPSettings.get(BPSettingsKey.CONFIG_SESSION_SAVE):
            document.saveCache(delayedSave=BPUIController.__DELAYED_SAVECACHE_TIMEOUT)
            self.saveSettings(BPUIController.__DELAYED_SAVECACHE_TIMEOUT)

    def updateMenu(self):
        """Update menu for current active document"""
        if not self.__currentDocument:
            # no active document? does nothing
            return

        if not self.__menuInvalidated:
            # menu already up-to-date
            return

        # TODO: need to check if script is running
        scriptIsRunning = False
        cursor = self.__currentDocument.codeEditor().cursorPosition()

        # Menu FILE
        # ----------------------------------------------------------------------
        self.__window.actionFileNew.setEnabled(not scriptIsRunning)
        self.__window.actionFileOpen.setEnabled(not scriptIsRunning)

        self.__window.actionFileReload.setEnabled(not (scriptIsRunning or self.__currentDocument.fileName() is None) and os.path.isfile(self.__currentDocument.fileName()))
        self.__window.actionFileSave.setEnabled(self.__currentDocument.modified() and not(scriptIsRunning or self.__currentDocument.readOnly()))

        self.__window.actionFileSaveAs.setEnabled(not scriptIsRunning)
        self.__window.actionFileSaveAll.setEnabled(not scriptIsRunning)
        self.__window.actionFileClose.setEnabled(not scriptIsRunning)
        self.__window.actionFileCloseAll.setEnabled(not scriptIsRunning)

        # Menu EDIT
        # ----------------------------------------------------------------------
        self.__window.actionEditUndo.setEnabled(self.__currentDocument.codeEditor().document().isUndoAvailable() and not (scriptIsRunning or self.__currentDocument.readOnly()))
        self.__window.actionEditRedo.setEnabled(self.__currentDocument.codeEditor().document().isRedoAvailable() and not (scriptIsRunning or self.__currentDocument.readOnly()))
        self.__window.actionEditCut.setEnabled(cursor[3] > 0 and not (scriptIsRunning or self.__currentDocument.readOnly()))
        self.__window.actionEditCopy.setEnabled(cursor[3] > 0 and not (scriptIsRunning or self.__currentDocument.readOnly()))
        self.__updateMenuEditPaste()

        # Menu SCRIPT
        # ----------------------------------------------------------------------
        self.__window.actionScriptExecute.setEnabled(not scriptIsRunning)

        # Menu TOOLS
        # ----------------------------------------------------------------------

        # Menu SETTINGS
        # ----------------------------------------------------------------------
        self.__window.actionSettingsPreferences.setEnabled(not scriptIsRunning)

        self.__menuInvalidated = False

    def buildmenuFileRecent(self, menu):
        """Menu for 'file recent' is about to be displayed

        Build menu content
        """
        @pyqtSlot('QString')
        def menuFileRecent_Clicked(action):
            # open document
            self.commandFileOpen(self.sender().property('fileName'))

        menu.clear()

        if self.__historyFiles.length() == 0:
            action = QAction(i18n("(no recent scripts)"), self)
            action.setEnabled(False)
            menu.addAction(action)
        else:
            for fileName in reversed(self.__historyFiles.list()):
                action = QAction(fileName.replace(' & ', ' & &'), self)
                action.setProperty('fileName', fileName)
                action.triggered.connect(menuFileRecent_Clicked)
                menu.addAction(action)

    def name(self):
        """Return BuliPy plugin name"""
        return self.__bpName

    def started(self):
        """Return True if BuliPy interface is started"""
        return self.__pbStarted

    def version(self):
        """Return BuliPy plugin version"""
        return self.__bpVersion

    def title(self):
        """Return BuliPy plugin title"""
        return self.__pbTitle

    def languageDef(self, extension=None):
        """Return BuliPy language definition"""
        if extension is None or extension in self.__languageDefPython.extensions():
            return self.__languageDefPython
        elif extension in self.__languageDefXml.extensions():
            return self.__languageDefXml
        elif extension in self.__languageDefJson.extensions():
            return self.__languageDefJson
        elif extension in self.__languageDefText.extensions():
            return self.__languageDefText
        else:
            return self.__languageDefUnmanaged

    def cachePath(self, subDirectory=None):
        """Return BuliPy cache directory

        If a `subDirectory` name is provided, return cache path for subdirectory
        """
        if subDirectory is None or subDirectory == '':
            return self.__pbCachePath
        elif isinstance(subDirectory, str):
            return os.path.join(self.__pbCachePath, subDirectory)
        else:
            raise EInvalidType('Given `subDirectory` must be None or <str > ')

    def currentDocument(self):
        """Return current document"""
        return self.__currentDocument

    def documents(self):
        """Return documents maanger"""
        return self.__documents

    def saveSettings(self, delayedSave=0):
        """Save the current settings"""
        BPSettings.set(BPSettingsKey.CONFIG_SESSION_SAVE, self.__window.actionSettingsSaveSessionOnExit.isChecked())

        if delayedSave > 0:
            self.__delayedSaveTimer.start(delayedSave)
        else:
            # if save immediately, cancel any delayedSave
            self.__delayedSaveTimer.stop()

        if BPSettings.get(BPSettingsKey.CONFIG_SESSION_SAVE):
            # save current session properties only if allowed
            BPSettings.set(BPSettingsKey.SESSION_PATH_LASTOPENED, self.__lastDocumentDirectoryOpen)
            BPSettings.set(BPSettingsKey.SESSION_PATH_LASTSAVED, self.__lastDocumentDirectorySave)

            BPSettings.set(BPSettingsKey.SESSION_DOCUMENTS_RECENTS, self.__historyFiles.list())

            tmpList = []
            for document in self.__documents.documents():
                tmpList.append(f"@{document.cacheUuid()}")

            BPSettings.set(BPSettingsKey.SESSION_DOCUMENTS_OPENED, tmpList)
            BPSettings.set(BPSettingsKey.SESSION_DOCUMENTS_ACTIVE, self.__documents.document().cacheUuid())

            qtlayoutNfoB64 = self.__window.saveState()
            BPSettings.set(BPSettingsKey.SESSION_MAINWINDOW_VIEW_DOCKERS_LAYOUT, base64.b64encode(qtlayoutNfoB64).decode())

            BPSettings.set(BPSettingsKey.SESSION_MAINWINDOW_WINDOW_MAXIMIZED, self.__window.isMaximized())
            if not self.__window.isMaximized():
                # when maximized geometry is full screen geometry, then do it only if no in maximized
                BPSettings.set(BPSettingsKey.SESSION_MAINWINDOW_WINDOW_GEOMETRY, [self.__window.geometry().x(), self.__window.geometry().y(), self.__window.geometry().width(), self.__window.geometry().height()])

            BPSettings.set(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_VISIBLE, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_BTN_BUTTONSHOW))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_REGEX_CHECKED, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_BTN_REGEX))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_CASESENSITIVE_CHECKED, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_BTN_CASESENSITIVE))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_WHOLEWORD_CHECKED, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_BTN_WHOLEWORD))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_BACKWARD_CHECKED, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_BTN_BACKWARD))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_HIGHLIGHTALL_CHECKED, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_BTN_HIGHLIGHT))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_TEXT, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_TXT_SEARCH))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_CONSOLE_OPTIONS_FILTER_TYPES, [WConsoleType.toStr(type) for type in self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_FILTER_TYPES)])
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_CONSOLE_OPTIONS_FILTER_SEARCH, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_FILTER_SEARCH))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_CONSOLE_OPTIONS_AUTOCLEAR, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_CONSOLE_OUTPUT_FONT_SIZE, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_FONTSIZE))

            BPSettings.set(BPSettingsKey.SESSION_DOCKER_COLORPICKER_MENU_SELECTED, self.__dwColorPicker.options())

            BPSettings.set(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_REGEX_CHECKED, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_BTN_REGEX))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_CASESENSITIVE_CHECKED, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_BTN_CASESENSITIVE))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_WHOLEWORD_CHECKED, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_BTN_WHOLEWORD))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_BACKWARD_CHECKED, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_BTN_BACKWARD))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_HIGHLIGHTALL_CHECKED, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_BTN_HIGHLIGHT))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_TEXT, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_TXT_SEARCH))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_SAR_REPLACE_TEXT, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_TXT_REPLACE))
            BPSettings.set(BPSettingsKey.SESSION_DOCKER_SAR_OUTPUT_FONT_SIZE, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_FONTSIZE))

        return BPSettings.save()

    def close(self):
        """When window is about to be closed, execute some cleanup/backup/stuff before exiting BuliPy"""
        # save current settings
        if not self.__pbStarted:
            return

        for document in self.__documents.documents():
            document.saveCache()

        self.saveSettings()

        # need to close dockers, because if they're floating, close BuliPy
        # don't close floating dockers
        self.__dwConsoleOutput.close()
        self.__dwColorPicker.close()
        self.__dwSearchReplace.close()

        self.__dwConsoleOutput = None
        self.__dwColorPicker = None
        self.__dwSearchReplace = None

        self.__pbStarted = False
        self.bpWindowClosed.emit()

    def optionIsMaximized(self):
        """Return current option value"""
        return self.__window.isMaximized()

    def commandQuit(self):
        """Close BuliPy"""
        self.__window.close()

    def commandFileNew(self):
        """Create a new empty document"""
        self.__documents.newDocument()

    def commandFileOpen(self, file=None):
        """Open file"""
        if file is None or isinstance(file, bool):
            # if bool = >triggered from menu
            result = BPWOpenSave.openFiles(i18n("Open a document"),
                                           self.__lastDocumentDirectoryOpen,
                                           f"{i18n('Python files')} (*.py);;"
                                           f"{i18n('Text files')} (*.txt);;"
                                           f"{i18n('JSON files')} (*.json);;"
                                           f"{i18n('XML files')} (*.xml);;"
                                           f"{i18n('All Files')} (*.*)",
                                           self)

            if isinstance(result, dict):
                for fileName in result['files']:
                    self.commandFileOpen(fileName)
        elif isinstance(file, str):
            try:
                if not self.__documents.openDocument(file):
                    raise EInvalidStatus("Unable to open file")

                self.__lastDocumentDirectoryOpen = os.path.dirname(file)
                self.__historyFiles.remove(file)
            except Exception as e:
                Debug.print('[BPUIController.commandFileOpen] unable to open file {0}: {1}', file, str(e))
                return False
            return True
        else:
            raise EInvalidType('Given `file` is not valid')

    def commandFileSave(self, documentId=None):
        """Save document designed by `index` (or current document if `index` is None),
        using document filename

        If document has never been saved, will execute "save as" to request for a file name
        """
        if not isinstance(documentId, (str, WBPDocument)):
            # probably called from menu event
            documentId = None

        document = self.__documents.document(documentId)
        if document is None:
            # can't find document
            return False

        if not document.modified():
            # don(t need to save is not modified
            return False

        if document.fileName() is None:
            # document never been saved (no path/file name)
            # then switch to "save as" to aks user for a filename
            return self.commandFileSaveAs(document)

        try:
            if not self.__documents.saveDocument(document):
                raise EInvalidStatus("Unable to save file")

            self.__invalidateMenu()
        except Exception as e:
            Debug.print('[BPUIController.commandFileSave] unable to save file {0}: {1}', document.fileName(), str(e))
            return False
        return True

    def commandFileSaveAs(self, documentId=None, newFileName=None):
        """Save current document with another name"""
        if not isinstance(documentId, (str, WBPDocument)):
            # probably called from menu event
            documentId = None

        document = self.__documents.document(documentId)
        if document is None:
            # can't find document
            return False

        if newFileName is None:
            oldFileName = document.fileName()
            fileName = oldFileName
        else:
            oldFileName = None
            fileName = newFileName

        if fileName is None:
            # if no filename, use last directory where a file has been saved
            # as default directory for dialog box
            fileName = self.__lastDocumentDirectorySave

        # switch to tab as document (mostly: if "save all" is executed, this help
        # to determinate which document is saved)
        self.__window.msDocuments.setActive(document)

        if newFileName is None:
            result = BPWOpenSave.saveFile(i18n("Save BuliPy document"),
                                          fileName,
                                          f"{i18n('Python files')} (*.py);;"
                                          f"{i18n('Text files')} (*.txt);;"
                                          f"{i18n('JSON files')} (*.json);;"
                                          f"{i18n('XML files')} (*.xml);;"
                                          f"{i18n('All Files')} (*.*)",
                                          self)
            if result is None:
                return False
            else:
                fileName = result['file']

        if fileName != '':
            try:
                if not self.__documents.saveDocument(document, fileName):
                    raise EInvalidStatus("Unable to save file")

                if oldFileName is not None and oldFileName != fileName:
                    # as saved with on another location, consider old location
                    # is closed and add it to history
                    self.__historyFiles.append(oldFileName)

                # keep in memory
                self.__lastDocumentDirectorySave = os.path.dirname(fileName)

                self.__invalidateMenu()
            except Exception as e:
                Debug.print('[BPUIController.commandFileSaveAs] unable to save file {0}: {1}', fileName, str(e))
                return False
            return True
        return False

    def commandFileSaveAll(self):
        """Save all documents at once"""
        for document in self.__documents.documents():
            self.commandFileSave(document)

    def commandFileClose(self, documentId=None, askIfNotSaved=True):
        """Close current document

        If document has been modified, ask for: save/don't save/cancel
        """
        if not isinstance(documentId, (str, WBPDocument)):
            # probably called from menu event
            documentId = None

        document = self.__documents.document(documentId)
        if document is None:
            # can't find document
            return False

        if document.modified() and askIfNotSaved:
            # message box to confirm to close document
            if QMessageBox.question(self.__window,
                                    i18n("Close document"),
                                    i18n("Document has been modified without being saved.\n\nClose without saving?"),
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                return False

        if not document.fileName() is None:
            # save in history when closed as, when opened/save, documents are in
            # cache and automatically opened on next startup
            self.__historyFiles.append(document.fileName())

        return self.__documents.closeDocument(document)

    def commandFileReload(self, documentId=None, askIfNotSaved=True):
        """Reload current document

        If document has been modified, ask confirmation for reload
        """
        if not isinstance(documentId, (str, WBPDocument)):
            # probably called from menu event
            documentId = None

        document = self.__documents.document(documentId)
        if document is None:
            # can't find document
            return False

        if document.fileName() is None:
            # no file name, can't be reloaded
            return False

        if document.modified() and askIfNotSaved:
            # message box to confirm to close document
            if QMessageBox.question(self.__window,
                                    i18n("Reload document"),
                                    i18n("Document has been modified and not saved.\n\nReload document?"),
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                return False

        return self.__documents.reloadDocument(document)

    def commandFileCloseAll(self, askIfNotSaved=True):
        """Close all documents

        If document has been modified, ask for: save/don't save/cancel
        """
        defaultChoice = None
        for index in reversed(range(self.__documents.count())):

            if document := self.__documents.document(index):
                # defautl choice
                closeDocument = True
                if document.modified():
                    if defaultChoice is None:
                        # activate tab
                        self.__window.msDocuments.setActive(document)

                        choice = QMessageBox.question(self.__window,
                                                      i18n("Close document"),
                                                      i18n("Document has been modified without being saved.\n\nClose without saving?"),
                                                      QMessageBox.Yes | QMessageBox.YesToAll | QMessageBox.No | QMessageBox.NoToAll | QMessageBox.Cancel)
                    else:
                        choice = defaultChoice

                    if choice == QMessageBox.Cancel:
                        # cancel action
                        return
                    elif choice == QMessageBox.No:
                        closeDocument = False
                    elif choice == QMessageBox.NoToAll:
                        defaultChoice = QMessageBox.No
                    elif choice == QMessageBox.YesToAll:
                        defaultChoice = QMessageBox.Yes

                if closeDocument:
                    # save in history when closed as, when opened/save, documents are in
                    # cache and automatically opened on next startup
                    if not document.fileName() is None:
                        self.__historyFiles.append(document.fileName())
                    self.__documents.closeDocument(document)

    def commandEditUndo(self):
        """Undo last modification on current document"""
        if self.__currentDocument:
            self.__currentDocument.codeEditor().document().undo()

    def commandEditRedo(self):
        """Undo undoed modification on current document"""
        if self.__currentDocument:
            self.__currentDocument.codeEditor().document().redo()

    def commandEditCut(self):
        """Cut selected text from current document to clipboard"""
        if self.__currentDocument:
            self.__currentDocument.codeEditor().cut()

    def commandEditCopy(self):
        """Copy selected text from current document to clipboard"""
        if self.__currentDocument:
            self.__currentDocument.codeEditor().copy()

    def commandEditPaste(self):
        """Paste clipboard content to current document"""
        if self.__currentDocument:
            self.__currentDocument.codeEditor().paste()

    def commandEditSelectAll(self):
        """Select all document content"""
        if self.__currentDocument:
            self.__currentDocument.codeEditor().selectAll()

    def commandScriptExecute(self):
        """Execute script"""
        if self.__currentDocument:
            if self.__dwConsoleOutput:
                runner = BPPyRunner(self.__currentDocument, self.__dwConsoleOutput)
                runner.run()

    def commandScriptBreakPause(self):
        """Made Break/Pause in script execution"""
        print("TODO: implement commandScriptBreakPause")

    def commandScriptStop(self):
        """Stop script execution"""
        print("TODO: implement commandScriptStop")

    def commandScriptGoToLine(self, fromPosition, toPosition, document=None, setFocus=False):
        """Scroll to line number"""
        if isinstance(document, WBPDocument):
            self.__documents.setActiveDocument(document)

        if self.__currentDocument:
            self.__currentDocument.codeEditor().scrollToLine(fromPosition.y())
            cursor = self.__currentDocument.codeEditor().textCursor()
            cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, fromPosition.y() - 1)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            self.__currentDocument.codeEditor().setTextCursor(cursor)
            if setFocus:
                self.__currentDocument.setFocus()

    def commandToolsShowVersion(self, forceDisplayConsole=False):
        """Clear console and display BuliPy, Krita, Qt, ..., versions"""
        if forceDisplayConsole:
            self.commandViewDockConsoleOutputVisible(True)

        bpVersion = f"{self.__bpName} v{self.__bpVersion}"
        bpVersionSep = "=" * len(bpVersion)
        self.__dwConsoleOutput.autoClear()
        self.__dwConsoleOutput.append(f"#lc#***{bpVersion}***#", WConsoleType.INFO)
        self.__dwConsoleOutput.append(f"#lc#**{bpVersionSep}**#", WConsoleType.INFO)
        self.__dwConsoleOutput.append(f"#lc#**Krita:**#  #c#{Krita.instance().version()}#", WConsoleType.INFO)
        self.__dwConsoleOutput.append(f"#lc#**Python:**# #c#{sys.version}#", WConsoleType.INFO)
        self.__dwConsoleOutput.append(f"#lc#**Qt:**#     #c#{QT_VERSION_STR}#", WConsoleType.INFO)
        self.__dwConsoleOutput.append(f"#lc#**PyQt:**#   #c#{PYQT_VERSION_STR}#", WConsoleType.INFO)
        self.__dwConsoleOutput.append(f"#lc#**OS:**#     #c#{platform.system()} {platform.release()}#", WConsoleType.INFO)
        self.__dwConsoleOutput.append(f"#lc#**Arch.:**#  #c#{platform.machine()}{' ('+'-'.join(platform.architecture())+')' if platform.architecture()[1]!='' else ''}#", WConsoleType.INFO)

        self.__dwConsoleOutput.setActive()

    def commandLanguageInsert(self, text, setFocus=True):
        """Insert given `text` at current position in document

        If `setFocus` is True, current document got focus
        """
        if self.__currentDocument:
            self.__currentDocument.codeEditor().insertLanguageText(text)
            if setFocus:
                self.__currentDocument.codeEditor().setFocus()

    def commandColorCodeInsert(self, color, mode=BPDockWidgetColorPicker.MODE_INSERT, setFocus=True):
        """According to `mode
            - Insert given `color` at current position in document
            - Update color at current position in document with given `color`

        If `setFocus` is True, current document got focus
        """
        if self.__currentDocument:
            if not isinstance(color, QColor):
                raise EInvalidType("Given `color` must be a <QColor>")

            if color.alpha() == 255:
                colorCode = color.name(QColor.HexRgb)
            else:
                colorCode = color.name(QColor.HexArgb)

            Debug.print('commandColorCodeInsert', color, colorCode, mode)

            if mode == BPDockWidgetColorPicker.MODE_INSERT:
                self.__currentDocument.codeEditor().insertLanguageText(colorCode)
            elif mode == BPDockWidgetColorPicker.MODE_UPDATE:
                self.__currentDocument.codeEditor().replaceTokenText(colorCode)
            else:
                raise EInvalidValue("Given `mode` value is not valid")

            if setFocus:
                self.__currentDocument.codeEditor().setFocus()

    def commandViewBringToFront(self):
        """Bring main window to front"""
        self.__window.setWindowState((self.__window.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
        self.__window.activateWindow()

    def commandViewMainWindowMaximized(self, maximized=False):
        """Set the window state"""
        if not isinstance(maximized, bool):
            raise EInvalidValue('Given `maximized` must be a <bool > ')

        if maximized:
            # store current geometry now because after window is maximized, it's lost
            BPSettings.set(BPSettingsKey.SESSION_MAINWINDOW_WINDOW_GEOMETRY,
                           [self.__window.geometry().x(), self.__window.geometry().y(), self.__window.geometry().width(), self.__window.geometry().height()])
            self.__window.showMaximized()
        else:
            self.__window.showNormal()

        return maximized

    def commandViewMainWindowGeometry(self, geometry=[-1, -1, -1, -1]):
        """Set the window geometry

        Given `geometry` is a list [x, y, width, height] or a QRect()
        """
        if isinstance(geometry, QRect):
            geometry = [geometry.x(), geometry.y(), geometry.width(), geometry.height()]

        if not isinstance(geometry, list) or len(geometry) != 4:
            raise EInvalidValue('Given `geometry` must be a <list[x, y, w, h] > ')

        rect = self.__window.geometry()

        if geometry[0] >= 0:
            rect.setX(geometry[0])

        if geometry[1] >= 0:
            rect.setY(geometry[1])

        if geometry[2] >= 0:
            rect.setWidth(geometry[2])

        if geometry[3] >= 0:
            rect.setHeight(geometry[3])

        self.__window.setGeometry(rect)

        return [self.__window.geometry().x(), self.__window.geometry().y(), self.__window.geometry().width(), self.__window.geometry().height()]

    def commandViewDockConsoleOutputVisible(self, visible=None):
        """Display/Hide Console output docker"""
        if visible is None:
            visible = self.__dwConsoleOutputAction.isChecked()
        elif not isinstance(visible, bool):
            raise EInvalidValue('Given `visible` must be a <bool>')

        if self.__dwConsoleOutput:
            if visible:
                self.__dwConsoleOutput.show()
            else:
                self.__dwConsoleOutput.hide()

    def commandViewDockColorPickerVisible(self, visible=None):
        """Display/Hide Color Picker docker"""
        if visible is None:
            visible = self.__dwColorPickerAction.isChecked()
        elif not isinstance(visible, bool):
            raise EInvalidValue('Given `visible` must be a <bool>')

        if self.__dwColorPicker:
            if visible:
                self.__dwColorPicker.show()
            else:
                self.__dwColorPicker.hide()

    def commandViewDockSearchAndReplaceVisible(self, visible=True):
        """Display search and replace docker"""
        if not isinstance(visible, bool):
            raise EInvalidValue('Given `visible` must be a <bool>')

        if self.__dwSearchReplace:
            if visible:
                self.__dwSearchReplace.show()
                self.__dwSearchReplace.setActive()
            else:
                self.__dwSearchReplace.hide()

    def commandDockColorPickerSetColor(self, color):
        """Set color for color picker

        Given `color` can be a QColor or a string
        """
        if self.__dwColorPicker:
            self.__dwColorPicker.setColor(color)

    def commandDockColorPickerSetMode(self, mode=BPDockWidgetColorPicker.MODE_INSERT):
        """Set mode for color picker"""
        if self.__dwColorPicker:
            self.__dwColorPicker.setMode(mode)

    def commandSettingsSaveSessionOnExit(self, saveSession=None):
        """Define if current session properties have to be save or not"""
        if saveSession is None:
            saveSession = self.__window.actionSettingsSaveSessionOnExit.isChecked()
        elif isinstance(saveSession, bool):
            self.__window.actionSettingsSaveSessionOnExit.setChecked(saveSession)
        else:
            raise EInvalidValue('Given `visible` must be a <bool>')

    def commandSettingsOpenAtStartup(self, value=False):
        """Set option to start BP at Krita's startup"""
        BPSettings.set(BPSettingsKey.CONFIG_OPEN_ATSTARTUP, value)

    def commandSettingsOpen(self):
        """Open dialog box settings"""
        # if BPSettingsDialogBox.open(f'{self.__bpName}::Settings', self):
        #    self.saveSettings()
        print("TODO: implement commandSettingsOpen")

    def commandAboutBp(self):
        """Display 'About BuliPy' dialog box"""
        WAboutWindow(self.__bpName, self.__bpVersion, os.path.join(os.path.dirname(__file__), 'resources', 'png', 'buli-powered-big.png'), None, ':BuliPy')

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
import html
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

from PyQt5.QtWidgets import QWidget

from .bpdwconsole import BPDockWidgetConsoleOutput
from .bpdwcolorpicker import BPDockWidgetColorPicker
from .bpdwiconselector import BPDockWidgetIconSelector
from .bpdwsearchreplace import BPDockWidgetSearchReplace
from .bpdwdocuments import BPDockWidgetDocuments
from .bpwopensavedialog import BPWOpenSave

from .bplanguagedef import BPLanguageDefPython
from .bppyrunner import (BPPyRunner, BPLogger)
from .bpdocument import (WBPDocument, BPDocuments)
from .bphistory import BPHistory
from .bpmainwindow import BPMainWindow
from .bpthemes import BPThemes
from .bpsettings import (
        BPSettings,
        BPSettingsKey,
        BPSettingsDialogBox
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
from ..pktk.modules.imgutils import (
        buildIcon,
        getIconList
    )
from ..pktk.widgets.wabout import WAboutWindow
from ..pktk.widgets.wiconselector import WIconSelector
from ..pktk.widgets.wconsole import WConsoleType
from ..pktk.widgets.wiodialog import (
        WDialogBooleanInput,
        WDialogIntInput,
        WDialogRadioButtonChoiceInput
    )

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

        self.__bpStarted = False
        self.__bpStarting = False

        self.__window = None
        self.__bpName = bpName
        self.__bpVersion = bpVersion
        self.__bpTitle = "{0} - {1}".format(bpName, bpVersion)

        # cache directory
        self.__bpCachePath = os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "bulipy")
        try:
            os.makedirs(self.__bpCachePath, exist_ok=True)
            for subDirectory in ['documents', 'themes']:
                os.makedirs(self.cachePath(subDirectory), exist_ok=True)
        except Exception as e:
            Debug.print('[BPUIController.__init__] Unable to create directory {0}: {1}', self.cachePath(subDirectory), str(e))

        BPSettings.load()
        UITheme.load()
        BPThemes.load()

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

        # toolbars
        self.__toolbarsTmpSession = []

        # document manager, initialised when starting plugin UI
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
        self.__documents.fileExternallyChanged.connect(self.__documentModificationChanged)
        self.__documents.textChanged.connect(self.__delayedDocumentSaveCache)
        self.__documents.redoAvailable.connect(self.__invalidateMenu)
        self.__documents.undoAvailable.connect(self.__invalidateMenu)
        self.__documents.selectionChanged.connect(self.__delayedDocumentSaveCache)
        self.__documents.copyAvailable.connect(self.__invalidateMenu)
        self.__documents.languageDefChanged.connect(self.__documentLanguageDefChanged)
        self.__documents.fontSizeChanged.connect(self.__documentFontSizeChanged)

        # current active document
        self.__currentDocument = None

        self.__initialised = False

        # dockers
        self.__dwConsoleOutput = None
        self.__dwColorPicker = None
        self.__dwSearchReplace = None
        self.__dwDocuments = None

        self.__dwConsoleOutputAction = None
        self.__dwColorPickerAction = None
        self.__dwSearchReplaceAction = None
        self.__dwDocumentsAction = None

        # -- misc
        # editor/syntax theme
        self.__theme = ''

        # to save session
        self.__delayedSaveTimer = QTimer()
        self.__delayedSaveTimer.timeout.connect(lambda: self.saveSettings())

        # When invalidated, update of menu is delayed after a short time to avoid multiple call of menu update
        # otherwise if need and immediate update, call updateMenu() method directly
        self.__delayedUpdateMenu = QTimer()
        self.__delayedUpdateMenu.timeout.connect(lambda: self.updateMenu())

    def start(self):
        """Start plugin interface"""
        if self.__bpStarted:
            # user interface is already started, bring to front and exit
            self.commandViewBringToFront()
            return
        elif self.__bpStarting:
            # user interface is already starting, exit
            return

        self.__bpStarting = True

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
        self.__dwConsoleOutput.sourceRefClicked.connect(lambda source, fromPosition, toPosition: self.commandEditGoToLine(fromPosition.y(), source, True))
        self.__dwConsoleOutput.consoleClear.connect(self.commandToolsShowVersion)

        self.__dwColorPicker = BPDockWidgetColorPicker(self.__window, self.__documents)
        self.__dwColorPicker.setObjectName('__dwColorPicker')
        self.__dwColorPicker.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.__dwColorPicker.apply.connect(self.commandToolsColorCodeInsert)
        self.__dwColorPickerAction = self.__dwColorPicker.toggleViewAction()
        self.__dwColorPickerAction.setText(i18n("Color picker"))
        self.__dwColorPickerAction.toggled.connect(self.commandToolsDockColorPickerVisible)
        self.__window.addDockWidget(Qt.RightDockWidgetArea, self.__dwColorPicker)

        # mode can be set only when initialised
        if BPSettings.get(BPSettingsKey.CONFIG_TOOLS_DOCKERS_ICONSELECTOR_MODE) == 0:
            iconSelectorConfig = WIconSelector.OPTIONS_SHOW_SOURCE_KRITA
        else:
            iconSelectorConfig = WIconSelector.OPTIONS_SHOW_SOURCE_KRITA | WIconSelector.OPTIONS_SHOW_SOURCE_PKTK
        self.__dwIconSelector = BPDockWidgetIconSelector(self.__window, self.__documents, iconSelectorConfig)
        self.__dwIconSelector.setObjectName('__dwIconSelector')
        self.__dwIconSelector.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.__dwIconSelector.apply.connect(self.commandToolsIconCodeInsert)
        self.__dwIconSelectorAction = self.__dwIconSelector.toggleViewAction()
        self.__dwIconSelectorAction.setText(i18n("Icon selector"))
        self.__dwIconSelectorAction.toggled.connect(self.commandToolsDockIconSelectorVisible)
        self.__window.addDockWidget(Qt.RightDockWidgetArea, self.__dwIconSelector)

        self.__dwSearchReplace = BPDockWidgetSearchReplace(self.__window, self.__documents)
        self.__dwSearchReplace.setObjectName('__dwSearchReplace')
        self.__dwSearchReplaceAction = self.__dwSearchReplace.toggleViewAction()
        self.__dwSearchReplaceAction.setText(i18n("Search & Replace"))
        self.__window.addDockWidget(Qt.BottomDockWidgetArea, self.__dwSearchReplace)

        self.__dwDocuments = BPDockWidgetDocuments(self.__window, self.__documents)
        self.__dwDocuments.setObjectName('__dwDocuments')
        self.__dwDocumentsAction = self.__dwDocuments.toggleViewAction()
        self.__dwDocumentsAction.setText(i18n("Documents"))
        self.__window.addDockWidget(Qt.RightDockWidgetArea, self.__dwDocuments)

        self.__window.setWindowTitle(self.__bpTitle)
        self.__window.show()
        self.__window.activateWindow()

        # after window is visible to let switch automatically to the tab
        self.commandScriptDockOutputConsoleVisible(True)

    def __initSettings(self):
        """There's some visual settings that need to have the window visible
        (ie: the widget size are known) to be applied
        """
        if self.__initialised:
            self.__bpStarted = True
            self.bpWindowShown.emit()
            # already initialised, do nothing
            return

        # avoid multiple update of opened documents during initialisation
        self.__documents.setMassUpdate(True)

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

        self.commandViewMainWindowGeometry(BPSettings.get(BPSettingsKey.SESSION_MAINWINDOW_WINDOW_GEOMETRY))
        self.commandViewMainWindowMaximized(BPSettings.get(BPSettingsKey.SESSION_MAINWINDOW_WINDOW_MAXIMIZED))

        # initialise toolbar reset checked values?
        # - initialise option after toolbar...
        self.commandViewWrapLines(BPSettings.get(BPSettingsKey.SESSION_EDITOR_WRAPLINES_ACTIVE))
        self.commandViewShowRightLimit(BPSettings.get(BPSettingsKey.SESSION_EDITOR_RIGHTLIMIT_VISIBLE))
        self.commandViewShowLineNumber(BPSettings.get(BPSettingsKey.SESSION_EDITOR_LINE_NUMBER_VISIBLE))
        self.commandViewShowSpaces(BPSettings.get(BPSettingsKey.SESSION_EDITOR_SPACES_VISIBLE))
        self.commandViewShowIndent(BPSettings.get(BPSettingsKey.SESSION_EDITOR_INDENT_VISIBLE))
        self.commandViewHighlightClassesFunctionDeclaration(BPSettings.get(BPSettingsKey.SESSION_EDITOR_HIGHTLIGHT_FCTCLASSDECL_ACTIVE))
        self.commandViewSetFontSize(BPSettings.get(BPSettingsKey.SESSION_EDITOR_FONT_SIZE))

        qtlayoutNfoB64 = BPSettings.get(BPSettingsKey.SESSION_MAINWINDOW_VIEW_DOCKERS_LAYOUT)
        if qtlayoutNfoB64 != '':
            qtLayoutNfo = base64.b64decode(qtlayoutNfoB64.encode())
            self.__window.restoreState(qtLayoutNfo)

        self.__lastDocumentDirectoryOpen = BPSettings.get(BPSettingsKey.SESSION_PATH_LASTOPENED)
        self.__lastDocumentDirectorySave = BPSettings.get(BPSettingsKey.SESSION_PATH_LASTSAVED)

        # no ui controller command for dockers
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BTN_BUTTONSHOW, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_VISIBLE))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BTN_REGEX, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_REGEX_CHECKED))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BTN_CASESENSITIVE, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_CASESENSITIVE_CHECKED))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BTN_WHOLEWORD, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_WHOLEWORD_CHECKED))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BTN_BACKWARD, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_BACKWARD_CHECKED))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BTN_HIGHLIGHT, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_HIGHLIGHTALL_CHECKED))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_TXT_SEARCH, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_TEXT))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_FILTER_TYPES, [WConsoleType.fromStr(type) for type in BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_OPTIONS_FILTER_TYPES)])
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_FILTER_SEARCH, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_OPTIONS_FILTER_SEARCH))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_OPTIONS_AUTOCLEAR))
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_FONTSIZE, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_OUTPUT_FONT_SIZE))

        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_BUFFER_SIZE, BPSettings.get(BPSettingsKey.CONFIG_TOOLS_DOCKERS_CONSOLE_BUFFERSIZE))

        self.__dwColorPicker.setOptions(BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_COLORPICKER_MENU_SELECTED))
        self.__dwColorPicker.setColor('#ffffffff')

        self.__dwIconSelector.setIconSizeIndex(BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_ICONSELECTOR_ICONSIZE))
        self.__dwIconSelector.setViewMode(BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_ICONSELECTOR_VIEWMODE))

        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_BTN_REGEX, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_REGEX_CHECKED))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_BTN_CASESENSITIVE, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_CASESENSITIVE_CHECKED))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_BTN_WHOLEWORD, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_WHOLEWORD_CHECKED))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_BTN_BACKWARD, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_BACKWARD_CHECKED))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_BTN_HIGHLIGHT, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_HIGHLIGHTALL_CHECKED))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_TXT_SEARCH, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_TEXT))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_TXT_REPLACE, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_REPLACE_TEXT))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_FONTSIZE, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_OUTPUT_FONT_SIZE))

        self.__dwDocuments.setOption(BPDockWidgetDocuments.OPTION_SORT_COLUMN, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_DOCUMENTS_SORT_COLUMN))
        self.__dwDocuments.setOption(BPDockWidgetDocuments.OPTION_SORT_ORDER, BPSettings.get(BPSettingsKey.SESSION_TOOLS_DOCKERS_DOCUMENTS_SORT_ORDER))

        # do not load from here, already loaded from BPDocuments() initialisation
        # for fileName in BPSettings.get(BPSettingsKey.SESSION_DOCUMENTS_OPENED):
        #     self.__documents.openDocument(fileName)

        self.__historyFiles.setMaxItems(BPSettings.get(BPSettingsKey.CONFIG_SESSION_DOCUMENTS_RECENTS_COUNT))
        self.__historyFiles.setItems(BPSettings.get(BPSettingsKey.SESSION_DOCUMENTS_RECENTS))
        self.__historyFiles.removeMissingFiles()

        self.__documents.initialise(BPSettings.get(BPSettingsKey.SESSION_DOCUMENTS_OPENED), BPSettings.get(BPSettingsKey.SESSION_DOCUMENTS_ACTIVE))

        self.__window.initMenu()

        # toolbar settings MUST be initialized after menu :-)
        self.__toolbarsTmpSession = BPSettings.get(BPSettingsKey.SESSION_TOOLBARS)
        self.commandSettingsToolbars(BPSettings.get(BPSettingsKey.CONFIG_TOOLBARS), self.__toolbarsTmpSession)

        self.__initialised = True
        self.__bpStarted = True
        self.__bpStarting = False

        self.bpWindowShown.emit()

        self.__currentDocument = self.__documents.document()

        self.__updateUiFromSettings()
        self.__documents.setMassUpdate(False)
        self.updateMenu()

    def __themeChanged(self):
        """Theme has been changed, reload resources"""
        UITheme.reloadResources()

    def __updateUiFromSettings(self):
        """Update UI from settings"""
        self.__documents.updateSettings(True)

        # use same font than one choosen for editor
        self.__dwConsoleOutput.setOption(BPDockWidgetConsoleOutput.OPTION_FONTNAME, BPSettings.get(BPSettingsKey.CONFIG_EDITOR_FONT_NAME))
        self.__dwSearchReplace.setOption(BPDockWidgetSearchReplace.OPTION_FONTNAME, BPSettings.get(BPSettingsKey.CONFIG_EDITOR_FONT_NAME))

    def __invalidateMenu(self):
        """Invalidate menu..."""
        # When invalidated, update of menu is delayed after a short time to avoid multiple call of menu update
        # otherwise if need and immediate update, call updateMenu() method directly
        self.__delayedUpdateMenu.start(25)

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

        currentToken = document.codeEditor().cursorToken()
        if currentToken:
            if document.languageDefinition().name() == 'Python':
                if currentToken.type() in (BPLanguageDefPython.ITokenType.STRING,
                                           BPLanguageDefPython.ITokenType.BSTRING,
                                           BPLanguageDefPython.ITokenType.STRING_LONG_S,
                                           BPLanguageDefPython.ITokenType.STRING_LONG_D,
                                           BPLanguageDefPython.ITokenType.FSTRING_LONG_S,
                                           BPLanguageDefPython.ITokenType.FSTRING_LONG_D,
                                           BPLanguageDefPython.ITokenType.BSTRING_LONG_S,
                                           BPLanguageDefPython.ITokenType.BSTRING_LONG_D):
                    if results := re.search(r'''^(["'])(#(?:[A-F0-9]{6}|[A-F0-9]{8}))(\1)$''', currentToken.value(), flags=re.I):
                        # color code
                        self.__dwColorPicker.setColor(results.groups()[1])
                        self.__dwColorPicker.setMode(BPDockWidgetColorPicker.MODE_UPDATE)
                        return
                    elif previous := currentToken.previous():
                        # icon reference?
                        if previous.type() == BPLanguageDefPython.ITokenType.DELIMITER_PARENTHESIS_OPEN:
                            if previousFct := previous.previous():
                                if previousFct.type() == BPLanguageDefPython.ITokenType.IDENTIFIER:
                                    if previousFct.value() == 'icon':
                                        # probably from Krita.instance().icon()
                                        if results := re.search(r'''^(["'])([^\1]+)(\1)$''', currentToken.value(), flags=re.I):
                                            value = f'krita:{results.groups()[1]}'
                                            if value in getIconList(['krita']):
                                                self.__dwIconSelector.setIcon(value)
                                                self.__dwIconSelector.setMode(BPDockWidgetIconSelector.MODE_UPDATE)
                                                return
                                    elif previousFct.value() == 'buildIcon':
                                        # a buildIcon use a "pktk:" or "krita:" uri
                                        if results := re.search(r'''^(["'])((?:pktk|krita):[^\1]+)(\1)$''', currentToken.value(), flags=re.I):
                                            self.__dwIconSelector.setIcon(results.groups()[1])
                                            self.__dwIconSelector.setMode(BPDockWidgetIconSelector.MODE_UPDATE)
                                            return

            elif (document.languageDefinition().name() == 'XML' and currentToken.type() == LanguageDefXML.ITokenType.STRING or
                  document.languageDefinition().name() == 'JSON' and currentToken.type() == LanguageDefJSON.ITokenType.STRING):
                if results := re.search(r'''^(["'])(#(?:[A-F0-9]{6}|[A-F0-9]{8}))(\1)$''', currentToken.value(), flags=re.I):
                    self.__dwColorPicker.setColor(results.groups()[1])
                    self.__dwColorPicker.setMode(BPDockWidgetColorPicker.MODE_UPDATE)
                    return

        self.__dwColorPicker.setMode(BPDockWidgetColorPicker.MODE_INSERT)
        self.__dwIconSelector.setMode(BPDockWidgetIconSelector.MODE_INSERT)

    def __documentModificationChanged(self, document):
        """A document status has been changed"""
        self.__updateStatusUiModified(document)
        self.__delayedDocumentSaveCache(document)

    def __documentLanguageDefChanged(self, document):
        """A document language definition has been changed"""
        self.__updateStatusUiLanguageDef(document)
        self.__delayedDocumentSaveCache(document)

    def __documentFontSizeChanged(self, document):
        """A document font size definition has been changed"""
        self.commandViewSetFontSize(document.codeEditor().optionFontSize())

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
            self.__window.actionEditPaste.setEnabled(self.__currentDocument.codeEditor().canPaste() and not (self.scriptIsRunning() or self.__currentDocument.readOnly()))

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

        if self.__currentDocument.modifiedExternally():
            self.__window.setStatusBarText(self.__window.STATUSBAR_MODIFICATIONSTATUS, 'E')
        elif self.__currentDocument.modified():
            self.__window.setStatusBarText(self.__window.STATUSBAR_MODIFICATIONSTATUS, 'I')
        else:
            self.__window.setStatusBarText(self.__window.STATUSBAR_MODIFICATIONSTATUS, 'N')
        self.__invalidateMenu()

    def __delayedDocumentSaveCache(self, document):
        self.__invalidateMenu()
        document.saveCache(delayedSave=BPUIController.__DELAYED_SAVECACHE_TIMEOUT)
        self.saveSettings(BPUIController.__DELAYED_SAVECACHE_TIMEOUT)

    def __updateToolbarTmpSession(self):
        """Update current toolbar temporary session variable from current toolbars state"""
        if self.__bpStarted:
            # update toolbars session only if self.__bpStarted is True (BC is started)
            # if not True this means main window is closed and then, toolbar are not visible
            # in this case we don't want to save toolbar status/visiblity are they're not
            # representative of real state

            # get current toolbar configuration from settings as dict for which key is toolbar id
            toolbarSettings = {toolbar['id']: toolbar for toolbar in BPSettings.get(BPSettingsKey.CONFIG_TOOLBARS)}
            self.__toolbarsTmpSession = []
            # loop over toolbar to update settings: visibility, area, position
            for toolbar in self.__window.toolbarList():
                id = toolbar.objectName()
                if id in toolbarSettings:
                    geometry = toolbar.geometry()
                    self.__toolbarsTmpSession.append({
                            'id': id,
                            'visible': toolbar.isVisible(),
                            'area': self.__window.toolBarArea(toolbar),
                            'break': self.__window.toolBarBreak(toolbar),
                            'rect': [geometry.left(), geometry.top(), geometry.width(), geometry.height()]
                        })

    def updateMenu(self):
        """Update menu for current active document"""
        if not self.__currentDocument:
            # no active document? does nothing
            return

        scriptIsRunning = self.scriptIsRunning()
        cursor = self.__currentDocument.codeEditor().cursorPosition()

        extensions = self.__currentDocument.languageDefinition().extensions()

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

        self.__window.menuFileRecent.setEnabled(not scriptIsRunning)
        self.__window.actionFileQuit.setEnabled(not scriptIsRunning)

        # Menu EDIT
        # ----------------------------------------------------------------------
        self.__window.actionEditUndo.setEnabled(self.__currentDocument.codeEditor().document().isUndoAvailable() and not (scriptIsRunning or self.__currentDocument.readOnly()))
        self.__window.actionEditRedo.setEnabled(self.__currentDocument.codeEditor().document().isRedoAvailable() and not (scriptIsRunning or self.__currentDocument.readOnly()))
        self.__window.actionEditCut.setEnabled(cursor[3] > 0 and not (scriptIsRunning or self.__currentDocument.readOnly()))
        self.__window.actionEditCopy.setEnabled(cursor[3] > 0 and not (scriptIsRunning or self.__currentDocument.readOnly()))
        self.__updateMenuEditPaste()

        self.__window.actionEditSelectAll.setEnabled(not scriptIsRunning)
        self.__window.actionEditSearchReplace.setEnabled(not scriptIsRunning)

        self.__window.actionEditCodeComment.setEnabled(not scriptIsRunning and '.py' in extensions)
        self.__window.actionEditCodeIndent.setEnabled(not scriptIsRunning)
        self.__window.actionEditCodeDedent.setEnabled(not scriptIsRunning)
        self.__window.actionEditDeleteLine.setEnabled(not scriptIsRunning)
        self.__window.actionEditDuplicateLine.setEnabled(not scriptIsRunning)

        self.__window.actionEditReadOnlyMode.setChecked(self.__currentDocument.codeEditor().overwriteMode())
        self.__window.actionEditOverwriteMode.setEnabled(not scriptIsRunning)

        self.__window.actionEditReadOnlyMode.setChecked(self.__currentDocument.readOnly())
        self.__window.actionEditReadOnlyMode.setEnabled(self.__currentDocument.writeable() and not scriptIsRunning)

        # Menu VIEW
        # ----------------------------------------------------------------------
        self.__window.actionViewHighlightClassesFunctionDeclaration.setEnabled('.py' in extensions)

        # Menu SCRIPT
        # ----------------------------------------------------------------------
        self.__window.actionScriptExecute.setEnabled(not scriptIsRunning and '.py' in extensions)
        self.__window.actionScriptBreakPause.setEnabled(scriptIsRunning)
        self.__window.actionScriptStop.setEnabled(scriptIsRunning)

        # Menu TOOLS
        # ----------------------------------------------------------------------
        self.__window.actionToolsCopyFullPathFileName.setEnabled(self.__currentDocument.fileName() is not None)
        self.__window.actionToolsCopyPathName.setEnabled(self.__currentDocument.fileName() is not None)
        self.__window.actionToolsCopyFileName.setEnabled(self.__currentDocument.fileName() is not None)

        self.__window.actionToolsMDocSortAscending.setEnabled(len(extensions) == 0 or '.txt' in extensions)
        self.__window.actionToolsMDocSortDescending.setEnabled(len(extensions) == 0 or '.txt' in extensions)
        self.__window.actionToolsMDocRemoveDuplicateLines.setEnabled(len(extensions) == 0 or '.txt' in extensions)
        self.__window.actionToolsMDocRemoveEmptyLines.setEnabled(len(extensions) == 0 or '.txt' in extensions)
        self.__window.actionToolsMDocTrimSpaces.setEnabled('.py' not in extensions)
        self.__window.actionToolsMDocTrimLeadingSpaces.setEnabled('.py' not in extensions)
        self.__window.actionToolsMDocPrettify.setEnabled('.json' in extensions or '.xml' in extensions)

        # Menu SETTINGS
        # ----------------------------------------------------------------------
        self.__window.actionSettingsPreferences.setEnabled(not scriptIsRunning)

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
        return self.__bpStarted

    def version(self):
        """Return BuliPy plugin version"""
        return self.__bpVersion

    def title(self):
        """Return BuliPy plugin title"""
        return self.__bpTitle

    def window(self):
        """Return main window attached to uiController"""
        return self.__window

    def languageDef(self, extension=None):
        """Return BuliPy language definition"""
        if extension is None:
            extension = '.py'
        return BPThemes.languageDef(extension)

    def cachePath(self, subDirectory=None):
        """Return BuliPy cache directory

        If a `subDirectory` name is provided, return cache path for subdirectory
        """
        if subDirectory is None or subDirectory == '':
            return self.__bpCachePath
        elif isinstance(subDirectory, str):
            return os.path.join(self.__bpCachePath, subDirectory)
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

        if delayedSave > 0:
            self.__delayedSaveTimer.start(delayedSave)
        else:
            # if save immediately, cancel any delayedSave
            self.__delayedSaveTimer.stop()

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

        BPSettings.set(BPSettingsKey.SESSION_EDITOR_WRAPLINES_ACTIVE, self.__window.actionViewWrapLines.isChecked())
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_RIGHTLIMIT_VISIBLE, self.__window.actionViewShowRightLimit.isChecked())
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_LINE_NUMBER_VISIBLE, self.__window.actionViewShowLineNumber.isChecked())
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_SPACES_VISIBLE, self.__window.actionViewShowSpaces.isChecked())
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_INDENT_VISIBLE, self.__window.actionViewShowIndent.isChecked())
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_HIGHTLIGHT_FCTCLASSDECL_ACTIVE, self.__window.actionViewHighlightClassesFunctionDeclaration.isChecked())

        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_VISIBLE, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_BTN_BUTTONSHOW))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_REGEX_CHECKED, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_BTN_REGEX))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_CASESENSITIVE_CHECKED, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_BTN_CASESENSITIVE))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_WHOLEWORD_CHECKED, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_BTN_WHOLEWORD))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_BACKWARD_CHECKED, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_BTN_BACKWARD))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_HIGHLIGHTALL_CHECKED, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_BTN_HIGHLIGHT))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_TEXT, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_TXT_SEARCH))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_OPTIONS_FILTER_TYPES, [WConsoleType.toStr(type) for type in self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_FILTER_TYPES)])
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_OPTIONS_FILTER_SEARCH, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_FILTER_SEARCH))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_OPTIONS_AUTOCLEAR, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_AUTOCLEAR))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_OUTPUT_FONT_SIZE, self.__dwConsoleOutput.option(BPDockWidgetConsoleOutput.OPTION_FONTSIZE))

        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_COLORPICKER_MENU_SELECTED, self.__dwColorPicker.options())

        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_ICONSELECTOR_ICONSIZE, self.__dwIconSelector.iconSizeIndex())
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_ICONSELECTOR_VIEWMODE, self.__dwIconSelector.viewMode())

        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_REGEX_CHECKED, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_BTN_REGEX))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_CASESENSITIVE_CHECKED, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_BTN_CASESENSITIVE))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_WHOLEWORD_CHECKED, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_BTN_WHOLEWORD))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_BACKWARD_CHECKED, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_BTN_BACKWARD))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_HIGHLIGHTALL_CHECKED, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_BTN_HIGHLIGHT))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_TEXT, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_TXT_SEARCH))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_REPLACE_TEXT, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_TXT_REPLACE))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_OUTPUT_FONT_SIZE, self.__dwSearchReplace.option(BPDockWidgetSearchReplace.OPTION_FONTSIZE))

        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_DOCUMENTS_SORT_COLUMN, self.__dwDocuments.option(BPDockWidgetDocuments.OPTION_SORT_COLUMN))
        BPSettings.set(BPSettingsKey.SESSION_TOOLS_DOCKERS_DOCUMENTS_SORT_ORDER, self.__dwDocuments.option(BPDockWidgetDocuments.OPTION_SORT_ORDER))

        return BPSettings.save()

    def close(self):
        """When window is about to be closed, execute some cleanup/backup/stuff before exiting BuliPy"""
        # save current settings
        if not self.__bpStarted:
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

        self.__documents.cleanup()

        self.__bpStarted = False
        self.__bpStarting = False
        self.__initialised = False
        self.__window = None

        self.__toolbarsTmpSession = []

        self.__currentDocument = None

        self.bpWindowClosed.emit()

    def optionIsMaximized(self):
        """Return current option value"""
        return self.__window.isMaximized()

    def scriptIsRunning(self):
        """Return is script is running"""
        if self.__dwConsoleOutput:
            return self.__dwConsoleOutput.scriptIsRunning()
        return False

    def commandQuit(self):
        """Close BuliPy"""
        if self.__window:
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
            if WDialogBooleanInput.display(i18n("Close document"),
                                           f'<p>{i18n("Document has been modified without being saved.")}</p>'
                                           f'<p><b>{i18n("Close without saving?")}</b></p>') is False:
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
            if WDialogBooleanInput.display(i18n("Reload document"),
                                           f'<p>{i18n("Document has been modified without being saved.")}</p>'
                                           f'<p><b>{i18n("Reload document?")}</b></p>') is False:
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

                        documentName = f"<i><span style='font-family: consolas, monospace;'>{html.escape(document.tabName(False))}</span></i>"
                        choice = WDialogRadioButtonChoiceInput.display(i18n("Close document"),
                                                                       f'<p>{i18n(f"Document {documentName} has been modified without being saved.")}</p>'
                                                                       f'<p><b>{i18n("Close without saving?")}</b></p>',
                                                                       choicesValue=[i18n('Yes'),
                                                                                     i18n('Yes to all'),
                                                                                     i18n('No'),
                                                                                     i18n('No to all')
                                                                                     ],
                                                                       defaultIndex=2,
                                                                       minSize=QSize(450, 250))
                        if choice is None:
                            # Cancel
                            return
                        elif choice == 1:
                            # yes to all
                            defaultChoice = 1
                        elif choice == 2:
                            # No
                            closeDocument = False
                        elif choice == 3:
                            defaultChoice = 3
                            closeDocument = False
                    elif defaultChoice == 3:
                        # No to all
                        closeDocument = False

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

    def commandEditComment(self):
        """Comment selected lines or current line from active document"""
        if self.__currentDocument:
            self.__currentDocument.codeEditor().doToggleComment()

    def commandEditIndent(self):
        """Indent selected lines or current line from active document"""
        if self.__currentDocument:
            self.__currentDocument.codeEditor().doIndent()

    def commandEditDedent(self):
        """Dedent selected lines or current line from active document"""
        if self.__currentDocument:
            self.__currentDocument.codeEditor().doDedent()

    def commandEditDeleteLine(self):
        """Delete selected lines or current line from active document"""
        if self.__currentDocument:
            self.__currentDocument.codeEditor().doDeleteLine()

    def commandEditDuplicateLine(self):
        """Duplicate selected lines or current line from active document"""
        if self.__currentDocument:
            self.__currentDocument.codeEditor().doDuplicateLine()

    def commandEditOverwriteMode(self, value=None):
        """Set document in overwrite/insert mode

        If `value` is None, invert current state
        """
        if self.__currentDocument:
            self.__currentDocument.codeEditor().doOverwriteMode(value)
            self.__invalidateMenu()

    def commandEditReadOnlyMode(self, value=None):
        """set/unset active document as read-only

        If `value` is None, invert current state
        """
        if self.__currentDocument and not self.scriptIsRunning():
            self.__currentDocument.setReadOnly(value)
            self.__invalidateMenu()

    def commandEditDockSearchAndReplaceVisible(self, visible=True):
        """Display search and replace docker"""
        if not isinstance(visible, bool):
            raise EInvalidValue('Given `visible` must be a <bool>')

        if self.__dwSearchReplace:
            if visible:
                self.__dwSearchReplace.show()
                self.__dwSearchReplace.setActive()
            else:
                self.__dwSearchReplace.hide()

    def commandEditGoToLine(self, toLine=None, document=None, setFocus=False):
        """Scroll to line number of given document

        Note: given `toLine` start from 1 (not from 0)
        """
        if isinstance(document, WBPDocument):
            self.__documents.setActiveDocument(document)

        if toLine is None:
            toLine = WDialogIntInput.display(i18n("Go to line"), minValue=1, maxValue=self.__currentDocument.codeEditor().blockCount(), minSize=QSize(450, 0))
            if toLine is None:
                return

        if not isinstance(toLine, int):
            raise EInvalidType("Given `toLine` must be <int>")

        if toLine < 1:
            toLine = 1
        if toLine > self.__currentDocument.codeEditor().blockCount():
            toLine = self.__currentDocument.codeEditor().blockCount()

        if self.__currentDocument:
            self.__currentDocument.codeEditor().scrollToLine(toLine)
            cursor = self.__currentDocument.codeEditor().textCursor()
            cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, toLine - 1)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            self.__currentDocument.codeEditor().setTextCursor(cursor)
            if setFocus:
                self.__currentDocument.setFocus()

    def commandViewWrapLines(self, active):
        """Set/unset wrap mode for ALL documents"""
        self.__window.actionViewWrapLines.setChecked(active)
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_WRAPLINES_ACTIVE, self.__window.actionViewWrapLines.isChecked())
        self.__documents.updateSettings()

    def commandViewShowRightLimit(self, active):
        """Set/unset right  mode for ALL documents"""
        self.__window.actionViewShowRightLimit.setChecked(active)
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_RIGHTLIMIT_VISIBLE, self.__window.actionViewShowRightLimit.isChecked())
        self.__documents.updateSettings()

    def commandViewShowLineNumber(self, active):
        """show/hide lines number for ALL documents"""
        self.__window.actionViewShowLineNumber.setChecked(active)
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_LINE_NUMBER_VISIBLE, self.__window.actionViewShowLineNumber.isChecked())
        self.__documents.updateSettings()

    def commandViewShowSpaces(self, active):
        """show/hide spaces for ALL documents"""
        self.__window.actionViewShowSpaces.setChecked(active)
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_SPACES_VISIBLE, self.__window.actionViewShowSpaces.isChecked())
        self.__documents.updateSettings()

    def commandViewShowIndent(self, active):
        """show/hide indents for ALL documents"""
        self.__window.actionViewShowIndent.setChecked(active)
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_INDENT_VISIBLE, self.__window.actionViewShowIndent.isChecked())
        self.__documents.updateSettings()

    def commandViewHighlightClassesFunctionDeclaration(self, active):
        """show/hide class/function definition for ALL Python documents"""
        self.__window.actionViewHighlightClassesFunctionDeclaration.setChecked(active)
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_HIGHTLIGHT_FCTCLASSDECL_ACTIVE, self.__window.actionViewHighlightClassesFunctionDeclaration.isChecked())
        self.__documents.updateSettings()

    def commandViewSetFontSize(self, size):
        """Set font size for ALL document"""
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_FONT_SIZE, size)
        self.__documents.updateSettings()

    def commandScriptExecute(self):
        """Execute script"""
        if self.__currentDocument:
            if self.__dwConsoleOutput:
                self.__invalidateMenu()
                runner = BPPyRunner(self.__currentDocument, self.__dwConsoleOutput)
                runner.run()
                self.__invalidateMenu()

    def commandScriptBreakPause(self):
        """Made Break/Pause in script execution"""
        print("TODO: implement commandScriptBreakPause")

    def commandScriptStop(self):
        """Stop script execution"""
        print("TODO: implement commandScriptStop")

    def commandScriptDockOutputConsoleVisible(self, visible=True):
        """Display/Hide Console output docker"""
        if not isinstance(visible, bool):
            raise EInvalidValue('Given `visible` must be a <bool>')

        if self.__dwConsoleOutput:
            if visible:
                self.__dwConsoleOutput.show()
                self.__dwConsoleOutput.setActive()
            else:
                self.__dwConsoleOutput.hide()

    def commandToolsDockColorPickerVisible(self, visible=None):
        """Display/Hide Color Picker docker"""
        if visible is None:
            visible = self.__dwColorPickerAction.isChecked()
        elif not isinstance(visible, bool):
            raise EInvalidValue('Given `visible` must be a <bool>')

        if self.__dwColorPicker:
            if visible:
                self.__dwColorPicker.show()
                self.__dwColorPicker.setActive()
            else:
                self.__dwColorPicker.hide()
        if self.__window:
            self.__window.actionToolsColorPicker.setChecked(visible)

    def commandToolsDockColorPickerSetColor(self, color):
        """Set color for color picker

        Given `color` can be a QColor or a string
        """
        if self.__dwColorPicker:
            self.__dwColorPicker.setColor(color)

    def commandToolsDockColorPickerSetMode(self, mode=BPDockWidgetColorPicker.MODE_INSERT):
        """Set mode for color picker"""
        if self.__dwColorPicker:
            self.__dwColorPicker.setMode(mode)

    def commandToolsDockIconSelectorVisible(self, visible=None):
        """Display/Hide Icon Selector docker"""
        if visible is None:
            visible = self.__dwIconSelectorAction.isChecked()
        elif not isinstance(visible, bool):
            raise EInvalidValue('Given `visible` must be a <bool>')

        if self.__dwIconSelector:
            if visible:
                self.__dwIconSelector.show()
                self.__dwIconSelector.setActive()
            else:
                self.__dwIconSelector.hide()

        if self.__window:
            self.__window.actionToolsIconsSelector.setChecked(visible)

    def commandToolsDockDocumentsVisible(self, visible=None):
        """Display/Hide Documents docker"""
        if visible is None:
            visible = self.__dwDocumentsAction.isChecked()
        elif not isinstance(visible, bool):
            raise EInvalidValue('Given `visible` must be a <bool>')

        if self.__dwDocuments:
            if visible:
                self.__dwDocuments.show()
                self.__dwDocuments.setActive()
            else:
                self.__dwDocuments.hide()

        if self.__window:
            self.__window.actionToolsDocuments.setChecked(visible)

    def commandToolsShowVersion(self, forceDisplayConsole=False):
        """Clear console and display BuliPy, Krita, Qt, ..., versions"""
        if forceDisplayConsole:
            self.commandScriptDockOutputConsoleVisible(True)

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

        if forceDisplayConsole:
            self.__dwConsoleOutput.setActive()

    def commandToolsTextInsert(self, text, setFocus=True):
        """Insert given `text` at current position in active document

        If `setFocus` is True, current document got focus
        """
        if self.__currentDocument:
            self.__currentDocument.codeEditor().insertLanguageText(text)
            if setFocus:
                self.__currentDocument.codeEditor().setFocus()

    def commandToolsColorCodeInsert(self, color, mode=BPDockWidgetColorPicker.MODE_INSERT, setFocus=True):
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

            if mode == BPDockWidgetColorPicker.MODE_INSERT:
                self.__currentDocument.codeEditor().insertLanguageText(colorCode)
            elif mode == BPDockWidgetColorPicker.MODE_UPDATE:
                currentToken = self.__currentDocument.codeEditor().cursorToken()
                charQuote = currentToken.value()[0]
                self.__currentDocument.codeEditor().replaceTokenText(f"{charQuote}{colorCode}{charQuote}")
            else:
                raise EInvalidValue("Given `mode` value is not valid")

            if setFocus:
                self.__currentDocument.codeEditor().setFocus()

    def commandToolsIconCodeInsert(self, icon, mode=BPDockWidgetIconSelector.MODE_INSERT, setFocus=True):
        """According to `mode
            - Insert given `icon` at current position in document
            - Update icon at current position in document with given `icon`

        If `setFocus` is True, current document got focus
        """
        if self.__currentDocument:
            if not isinstance(icon, str):
                raise EInvalidType("Given `icon` must be a <str>")

            # need to determinate what to insert
            # - if in udpate mode: update icon uri for str token
            #   otherwsise insert function to call
            #   . Krita.instance().icon("xxxxxx")   ==> if Krita mode set (default, BPSettingsKey.CONFIG_TOOLS_DOCKERS_ICONSELECTOR_MODE == 0)
            #   . buildIcon("xxx:xxxxxx")           ==> if PkTk mode set (default, BPSettingsKey.CONFIG_TOOLS_DOCKERS_ICONSELECTOR_MODE == 1)

            if mode == BPDockWidgetIconSelector.MODE_INSERT:
                if BPSettings.get(BPSettingsKey.CONFIG_TOOLS_DOCKERS_ICONSELECTOR_MODE) == 0:
                    text = f'''Krita.instance().icon("{icon.replace('krita:', '')}")'''
                else:
                    text = f'''buidIcon("{icon}")'''
                self.__currentDocument.codeEditor().insertLanguageText(text)
            elif mode == BPDockWidgetIconSelector.MODE_UPDATE:
                currentToken = self.__currentDocument.codeEditor().cursorToken()
                charQuote = currentToken.value()[0]
                if BPSettings.get(BPSettingsKey.CONFIG_TOOLS_DOCKERS_ICONSELECTOR_MODE) == 0:
                    text = icon.replace('krita:', '')
                else:
                    text = icon
                self.__currentDocument.codeEditor().replaceTokenText(f"{charQuote}{text}{charQuote}")
            else:
                raise EInvalidValue("Given `mode` value is not valid")

            if setFocus:
                self.__currentDocument.codeEditor().setFocus()

    def commandToolsCopyFullPathFileName(self):
        """Copy current document full/path file name in clipboard

        If document don't have path/file defined, does nothing
        """
        pass

    def commandToolsCopyPathName(self):
        """Copy current document path name in clipboard

        If document don't have path/file defined, does nothing
        """
        pass

    def commandToolsCopyFileName(self):
        """Copy current document file name in clipboard"""
        pass

    def commandToolsMDocSortAscending(self):
        """Sort current document lines ascending"""
        pass

    def commandToolsMDocSortDescending(self):
        """Sort current document lines descending"""
        pass

    def commandToolsMDocRemoveDuplicateLines(self):
        """Remove all duplicates lines"""
        pass

    def commandToolsMDocRemoveEmptyLines(self):
        """Remove all empty lines (even lines with only spaces)"""
        pass

    def commandToolsMDocTrimSpaces(self):
        """Remove all leading&trailing spaces"""
        pass

    def commandToolsMDocTrimLeadingSpaces(self):
        """Remove all leading spaces"""
        pass

    def commandToolsMDocTrimTrailingSpaces(self):
        """Remove all trailing spaces"""
        pass

    def commandToolsMDocPrettify(self):
        """Prettify current JSON/XML document"""
        pass

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

    def commandSettingsOpen(self):
        """Open dialog box settings"""
        self.__updateToolbarTmpSession()
        if BPSettingsDialogBox.open(f'{self.__bpName}::Settings', self):
            self.__updateUiFromSettings()
            self.saveSettings()

    def commandSettingsToolbars(self, config=None, session=None):
        """Set toolbars definition"""
        if config is None:
            return (BPSettings.get(BPSettingsKey.CONFIG_TOOLBARS), BPSettings.get(BPSettingsKey.SESSION_TOOLBARS))
        else:
            BPSettings.set(BPSettingsKey.CONFIG_TOOLBARS, config)
            if session is not None:
                BPSettings.set(BPSettingsKey.SESSION_TOOLBARS, session)
                self.__toolbarsTmpSession = session
            self.__window.initToolbar(config, self.__toolbarsTmpSession)

    def commandAboutBp(self):
        """Display 'About BuliPy' dialog box"""
        WAboutWindow(self.__bpName,
                     self.__bpVersion,
                     os.path.join(os.path.dirname(__file__), 'resources', 'png', 'buli-powered-big.png'),
                     None,
                     ':BuliPy',
                     icon=buildIcon([(':/bp/images/normal/bulipy', QIcon.Normal)]))


# Debug.setEnabled(True)

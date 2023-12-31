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

import krita
import os
import re
import sys
import time
import uuid
import hashlib
import html
from pathlib import Path

from PyQt5.Qt import *
from PyQt5.QtGui import (
        QFont,
        QTextCursor,
        QColor
    )
from PyQt5.QtCore import (
        pyqtSignal as Signal,
        QFileSystemWatcher
    )

from .bpthemes import BPThemes
from .bplanguagedef import (
        BPLanguageDefPython,
        BPCodeEditorHighlightLineRulePython
    )
from .bpdwcolorpicker import BPDockWidgetColorPicker

from .bpsettings import (
        BPSettings,
        BPSettingsKey
    )

from ..pktk.modules.languagedef import LanguageDef
from ..pktk.modules.tokenizer import TokenizerRule
from ..pktk.modules.utils import Debug
from ..pktk.modules.timeutils import tsToStr
from ..pktk.modules.strutils import (
        strDefault,
        trimLinesRight
    )
from ..pktk.modules.uitheme import UITheme
from ..pktk.modules.bytesrw import BytesRW
from ..pktk.widgets.wtabbar import WTabBar
from ..pktk.widgets.wcodeeditor import WCodeEditor
from ..pktk.widgets.wmultisplitter import WMultiSplitter
from ..pktk.widgets.wmsgbuttonbar import (
        WMessageButton,
        WMessageButtonBar
    )

from ..pktk.pktk import *


class WBPDocumentBase(QWidget):
    pass


class WBPDocument(WBPDocumentBase):
    """An embedded code editor to get an easier integration in BuliPy user interface

    Provide high level methods to manage open,save, reload, alert on file modified outside editor, ...
    """
    readOnlyModeChanged = Signal(WBPDocumentBase)
    overwriteModeChanged = Signal(WBPDocumentBase)
    cursorCoordinatesChanged = Signal(WBPDocumentBase)
    modificationChanged = Signal(WBPDocumentBase)
    textChanged = Signal(WBPDocumentBase)
    redoAvailable = Signal(WBPDocumentBase)
    undoAvailable = Signal(WBPDocumentBase)
    selectionChanged = Signal(WBPDocumentBase)
    copyAvailable = Signal(WBPDocumentBase)
    languageDefChanged = Signal(WBPDocumentBase)
    fontSizeChanged = Signal(WBPDocumentBase)
    fileExternallyChanged = Signal(WBPDocumentBase)
    textCopyToClipboard = Signal(WBPDocumentBase, str)
    textCutToClipboard = Signal(WBPDocumentBase, str)

    ALERT_FILE_DELETED =        0x01
    ALERT_FILE_MODIFIED =       0x02
    ALERT_FILE_TIMESTAMP =      0x03
    ALERT_FILE_CANTOPEN =       0x04
    ALERT_FILE_CANTSAVE =       0x05

    ACTION_CLOSE =              0x01
    ACTION_SAVE =               0x02
    ACTION_SAVEAS =             0x03
    ACTION_CANCEL =             0x04
    ACTION_RELOAD =             0x05
    ACTION_RELOADAUTO =         0x06
    ACTION_RELOADAUTO_STOP =    0x07

    def __init__(self, parent=None, languageDef=None, uiController=None):
        def emitFontSizeChanged():
            self.__delayedFontSizeTimer.stop()
            self.fontSizeChanged.emit(self)

        super(WBPDocument, self).__init__(parent)

        self.__layout = QVBoxLayout(self)
        self.__layout.setContentsMargins(3, 3, 3, 3)

        self.__msgButtonBar = WMessageButtonBar(self)
        self.__codeEditor = WCodeEditor(self, languageDef)

        self.__layout.addWidget(self.__msgButtonBar)
        self.__layout.addWidget(self.__codeEditor)

        self.__msgButtonBar.buttonClicked.connect(self.__msgAlertBtnClicked)
        self.setStyleSheet(f".bg {{ {UITheme.style('warning-box')} }}")

        self.__highlightLinesRule = None
        self.__lastUpdateTime = None
        self.__lastSavedTime = None

        # code editor properties
        self.__codeEditor.setLanguageDefinition(languageDef)
        self.__codeEditor.setOptionCommentCharacter('#')
        self.__codeEditor.setOptionMultiLine(True)
        self.__codeEditor.setOptionShowLineNumber(True)
        self.__codeEditor.setOptionAllowWheelSetFontSize(True)
        self.__codeEditor.setOptionAutoCompletion(False)

        # code editor signals to manage actions
        self.__codeEditor.readOnlyModeChanged.connect(lambda: self.readOnlyModeChanged.emit(self))
        self.__codeEditor.overwriteModeChanged.connect(lambda: self.overwriteModeChanged.emit(self))
        self.__codeEditor.cursorCoordinatesChanged.connect(lambda: self.cursorCoordinatesChanged.emit(self))
        self.__codeEditor.modificationChanged.connect(self.__modificationChanged)
        self.__codeEditor.textChanged.connect(self.__textChanged)
        self.__codeEditor.redoAvailable.connect(lambda: self.redoAvailable.emit(self))
        self.__codeEditor.undoAvailable.connect(lambda: self.undoAvailable.emit(self))
        self.__codeEditor.selectionChanged.connect(lambda: self.selectionChanged.emit(self))
        self.__codeEditor.copyAvailable.connect(lambda: self.copyAvailable.emit(self))
        self.__codeEditor.fontSizeChanged.connect(lambda: self.__delayedFontSizeTimer.start(75))
        self.__codeEditor.textCopyToClipboard.connect(lambda text: self.textCopyToClipboard.emit(self, text))
        self.__codeEditor.textCutToClipboard.connect(lambda text: self.textCutToClipboard.emit(self, text))

        # File watcher on document; allows to check if file is modified outside editor
        self.__fsWatcher = QFileSystemWatcher()
        self.__fsWatcher.fileChanged.connect(self.__externalFileModification)
        self.__delayedFsWatcherTimer = QTimer()
        self.__delayedFsWatcherTimer.timeout.connect(self.__externalFileModificationApply)
        self.__delayedFsWatcherList = []

        self.__alerts = []
        self.__currentAlert = None
        self.__newDocNumber = 0
        self.__uiController = uiController
        self.__documentFileName = None
        self.__documentCacheUuid = str(uuid.uuid4())
        self.__autoReload = False
        self.__autoReloadCount = 0
        self.__fileExternallyModified = False
        self.__invalidate = 0

        self.__delayedSaveTimer = QTimer()
        self.__delayedSaveTimer.timeout.connect(lambda: self.saveCache())

        # flag to inform if file is read only
        self.__fileIsReadOnly = False

        self.__trimBeforeSave = False

        # when font size is changed, signal will require to change font size on ALL documents
        # then to avoid lag due too to many signal sent (and editor to update), emit signal few milliseconds after the font size has been changed
        self.__delayedFontSizeTimer = QTimer()
        self.__delayedFontSizeTimer.timeout.connect(lambda: emitFontSizeChanged())
        self.applySettings(True)

    def __repr__(self):
        return f"<WBPDocument({self.tabName(True)}, {self.modified()})>"

    def __stopWatcher(self):
        """Stop watching file"""
        files = self.__fsWatcher.files()
        if len(files) > 0:
            self.__fsWatcher.removePaths(files)

    def __initWatcher(self):
        """Initialise QFileSystemWatcher()"""
        def init():
            self.__stopWatcher()
            if self.__documentFileName is not None:
                self.__fsWatcher.addPath(self.__documentFileName)

        # note:
        #   Some text editor don't save modifications on an existing file but recreate a new one
        #   (then delete+create instead of modify....)
        #
        # when file is deleted, watcher stops to watch it (even if recreated)
        # solution is initialise watcher with a few delay (250ms here) to be sure file is
        # watched in this case
        QTimer.singleShot(250, init)

    def __externalFileModificationApply(self):
        """File has been modified by an external process, apply change"""
        self.__delayedFsWatcherTimer.stop()
        self.__checkFileIsReadOnly()
        if os.path.isfile(self.__documentFileName):
            # file still exists, then modified alert
            self.__addAlert(WBPDocument.ALERT_FILE_MODIFIED)
        else:
            # file doesn't exists anymore, then deleted alert
            self.__addAlert(WBPDocument.ALERT_FILE_DELETED)

        # reinitialise watcher to be sure watch is not lost in case file has been deleted/recreated
        self.__initWatcher()

        self.fileExternallyChanged.emit(self)

    def __externalFileModification(self, fileName):
        """File has been modified by an external process"""
        Debug.print('[WBPDocument.__externalFileModification] File has been modified {0}', fileName)
        self.__fileExternallyModified = True
        # delayed update, in case file has been deleted/recreated (2 event may occurs)
        self.__delayedFsWatcherTimer.start(125)

    def __addAlert(self, alertCode):
        """Add alert to list, update alert messages"""
        if alertCode in self.__alerts or self.__currentAlert == alertCode:
            # no need to add same alert more than once
            return

        self.__alerts.append(alertCode)
        self.__updateAlerts()

    def __updateAlerts(self):
        """Update alerts if any"""
        def formatMessage(msg, question):
            return f'<html><p><b>{msg}</b><br><i>{question}</i></p></html>'

        if len(self.__alerts) == 0:
            # if no alerts do nothing
            self.__currentAlert = None
            return
        elif self.__currentAlert is not None:
            # if already wait for user action on a previous alert, do nothing
            return
        else:
            # get current alert
            self.__currentAlert = self.__alerts[0]

            # replace it with a waiting action
            # display alert

            if self.__currentAlert == WBPDocument.ALERT_FILE_DELETED:
                # document is open in editor, and version on disk has been deleted
                self.setReadOnly(True)
                if self.modified():
                    self.__msgButtonBar.message(formatMessage(i18n("File has been deleted on disk!"), i18n("Close document?")),
                                                WMessageButton(i18n('Close'),     WBPDocument.ACTION_CLOSE,    i18n('Close current document\nAs file has been deleted on disk, current modified content will be lost')),
                                                WMessageButton(i18n('Save'),      WBPDocument.ACTION_SAVE,     i18n('Save current modified document using current location')),
                                                WMessageButton(i18n('Save as'),   WBPDocument.ACTION_SAVEAS,   i18n('Save current modified document using a different location')),
                                                WMessageButton(i18n('Cancel'),    WBPDocument.ACTION_CANCEL,   i18n('Ignore alert and let current modified document opened in editor')),
                                                )
                else:
                    self.__msgButtonBar.message(formatMessage(i18n("File has been deleted on disk!"), i18n("Close document?")),
                                                WMessageButton(i18n('Close'),     WBPDocument.ACTION_CLOSE,    i18n('Close current document\nAs file has been deleted on disk, current content will be lost')),
                                                WMessageButton(i18n('Save'),      WBPDocument.ACTION_SAVE,     i18n('Save current document using current location')),
                                                WMessageButton(i18n('Save as'),   WBPDocument.ACTION_SAVEAS,   i18n('Save current document using a different location')),
                                                WMessageButton(i18n('Cancel'),    WBPDocument.ACTION_CANCEL,   i18n('Ignore alert and let current document opened in editor')),
                                                )
            elif self.__currentAlert == WBPDocument.ALERT_FILE_MODIFIED:
                # document is open in editor, and version on disk has been modified
                if self.__autoReload:
                    # auto reload active for document, then reload without asking
                    self.__autoReloadCount += 1
                    autoReloadCount = self.__autoReloadCount
                    self.__msgAlertBtnClicked(WBPDocument.ACTION_RELOAD)

                    self.__msgButtonBar.message(formatMessage(i18n('File has been reloaded automatically')+' '+i18n(f'({autoReloadCount} times)'),
                                                              f"{i18n('Last automatically reloaded at:')} {tsToStr(time.time(), 'full')}"
                                                              ),
                                                WMessageButton(i18n('Stop Auto-Reload'),
                                                               WBPDocument.ACTION_RELOADAUTO_STOP,
                                                               i18n('Stop Automatic reload of document from disk when modified')
                                                               )
                                                )
                    return

                self.setReadOnly(True)

                if self.modified():
                    self.__msgButtonBar.message(formatMessage(i18n("File has been modified outside editor!"), i18n("Reload document?")),
                                                WMessageButton(i18n('Auto-Reload'), WBPDocument.ACTION_RELOADAUTO,   i18n('Automatically reload document from disk when modified\nAs your document is'
                                                                                                                          ' modified, current modifications will be lost')),
                                                WMessageButton(i18n('Reload'),      WBPDocument.ACTION_RELOAD,       i18n('Reload document from disk\nAs your document is modified, current'
                                                                                                                          ' modifications will be lost')),
                                                WMessageButton(i18n('Overwrite'),   WBPDocument.ACTION_SAVE,         i18n('Save current modified document using current location\nModifications made by'
                                                                                                                          ' an external process to file will be lost')),
                                                WMessageButton(i18n('Save as'),     WBPDocument.ACTION_SAVEAS,       i18n('Save current modified document using a different location')),
                                                WMessageButton(i18n('Cancel'),      WBPDocument.ACTION_CANCEL,       i18n('Ignore alert and let current document opened in editor')),
                                                )
                else:
                    self.__msgButtonBar.message(formatMessage(i18n("File has been modified outside editor!"), i18n("Reload document?")),
                                                WMessageButton(i18n('Auto-Reload'), WBPDocument.ACTION_RELOADAUTO,   i18n('Automatically reload document from disk when modified')),
                                                WMessageButton(i18n('Reload'),      WBPDocument.ACTION_RELOAD,       i18n('Reload document from disk')),
                                                WMessageButton(i18n('Overwrite'),   WBPDocument.ACTION_SAVE,         i18n('Save current document using current location\nModifications made by an'
                                                                                                                          ' external process to file will be lost')),
                                                WMessageButton(i18n('Save as'),     WBPDocument.ACTION_SAVEAS,       i18n('Save current document using a different location')),
                                                WMessageButton(i18n('Cancel'),      WBPDocument.ACTION_CANCEL,       i18n('Ignore alert and let current document opened in editor'))
                                                )
            elif self.__currentAlert == WBPDocument.ALERT_FILE_TIMESTAMP:
                # document opened from cache (then from a restore session)
                # cache version is modified ad then there's might be a mismatch between version in editor and version on disk
                self.setReadOnly(True)
                self.__msgButtonBar.message(formatMessage(i18n("Document has been restored from last session with unsaved modifications, but document on disk has also been modified outside editor"), i18n("Reload document?")),
                                            WMessageButton(i18n('Reload'),        WBPDocument.ACTION_RELOAD,   i18n('Reload document from current location\nCurrent modifications will be lost')),
                                            WMessageButton(i18n('Overwrite'),     WBPDocument.ACTION_SAVE,     i18n('Save current modified document using current location\nModifications applied to file will be lost')),
                                            WMessageButton(i18n('Save as'),       WBPDocument.ACTION_SAVEAS,   i18n('Save current modified document using a different location')),
                                            WMessageButton(i18n('Cancel'),        WBPDocument.ACTION_CANCEL,   i18n('Ignore alert and let current document opened in editor'))
                                            )
            elif self.__currentAlert == WBPDocument.ALERT_FILE_CANTOPEN:
                self.setReadOnly(True)
                if os.path.isfile(self.__documentFileName):
                    self.__msgButtonBar.message(formatMessage(i18n("File can't be opened!"), i18n('Close document?')),
                                                WMessageButton(i18n('Close'),         WBPDocument.ACTION_CLOSE,    i18n('Close current document')),
                                                WMessageButton(i18n('Cancel'),        WBPDocument.ACTION_CANCEL,   i18n('Ignore alert and let current document opened in editor'))
                                                )
                else:
                    self.__msgButtonBar.message(formatMessage(i18n("File doesn't exists anymore!"), i18n('Close document?')),
                                                WMessageButton(i18n('Close'),         WBPDocument.ACTION_CLOSE,    i18n('Close current document')),
                                                WMessageButton(i18n('Cancel'),        WBPDocument.ACTION_CANCEL,   i18n('Ignore alert and let current document opened in editor'))
                                                )
            elif self.__currentAlert == WBPDocument.ALERT_FILE_CANTSAVE:
                self.setReadOnly(True)
                self.__msgButtonBar.message(formatMessage(i18n("File can't be saved!"), i18n('Save document to an another location?')),
                                            WMessageButton(i18n('Save as'),       WBPDocument.ACTION_SAVEAS,   i18n('Save current modified document using a different location')),
                                            WMessageButton(i18n('Close'),         WBPDocument.ACTION_CLOSE,    i18n('Close current modified document\nModifications will be lost')),
                                            WMessageButton(i18n('Cancel'),        WBPDocument.ACTION_CANCEL,   i18n('Ignore alert and let current modified document opened in editor'))
                                            )

    def __msgAlertBtnClicked(self, value):
        """Button from message alert has been clicked

        manage action to execute
        """
        if len(self.__alerts) == 0:
            self.__currentAlert = None
            self.__fileExternallyModified = False

            if value == WBPDocument.ACTION_RELOADAUTO_STOP:
                self.__autoReload = False
                self.__autoReloadCount = 0
            return
        elif self.__currentAlert is not None:
            # remove waiting action from alerts
            self.__alerts.pop(0)

            self.setReadOnly(False)

            if value == WBPDocument.ACTION_CLOSE:
                # close document, ignore current modifications
                self.__uiController.commandFileClose(askIfNotSaved=False)
            elif value == WBPDocument.ACTION_SAVE:
                self.__uiController.commandFileSaveAs(newFileName=self.__documentFileName)
            elif value == WBPDocument.ACTION_SAVEAS:
                self.__uiController.commandFileSaveAs()
            elif value == WBPDocument.ACTION_CANCEL:
                # do nothing, just hide message
                self.setModified(True)
            elif value == WBPDocument.ACTION_RELOAD:
                self.__uiController.commandFileReload(askIfNotSaved=False)
            elif value == WBPDocument.ACTION_RELOADAUTO:
                self.__uiController.commandFileReload(askIfNotSaved=False)
                self.__autoReload = True
            else:
                # shouldn't occurs
                raise EInvalidValue(f"Unknown action code: {value}")

            self.__currentAlert = None
            self.__updateAlerts()

    def __checkFileIsReadOnly(self):
        self.__fileIsReadOnly = False
        if self.__documentFileName is not None:
            if os.path.isfile(self.__documentFileName):
                if not os.access(self.__documentFileName, os.W_OK):
                    self.__fileIsReadOnly = True
                    self.__codeEditor.setReadOnly(True)

    def __textChanged(self):
        """Text has been changed, update dates, emit signal"""
        self.__lastUpdateTime = time.time()
        self.textChanged.emit(self)

    def __modificationChanged(self, changed):
        """Status has been changed, update dates, emit signal"""
        if changed is False:
            # last saved version
            self.__lastUpdateTime = self.__lastSavedTime

        self.modificationChanged.emit(self)

    def __fileTimeStamp(self):
        """Return timestamp of file

        If file hasn't been saved yet, return None
        """
        if self.__documentFileName is not None:
            try:
                return os.path.getmtime(self.__documentFileName)
            except Exception:
                return None
        return None

    def showEvent(self, event):
        """Widget become visible, need updates?"""
        if self.__invalidate:
            self.applySettings(self.__invalidate == 2)

    def applySettings(self, includeConfig=False):
        """Apply global BuliPy editor settings

        If `includeConfig`, will apply ALL settings (ie: take in account change from BuliPy configuration)
        Otherwise only session settings are taken in account
        """
        if not self.isVisible():
            if includeConfig:
                self.__invalidate = 2
            else:
                self.__invalidate = 1
            return

        lastUpdateTime = self.__lastUpdateTime
        self.__codeEditor.setUpdatesEnabled(False)

        font = QFont()
        font.setFamily(BPSettings.get(BPSettingsKey.CONFIG_EDITOR_FONT_NAME))
        font.setPointSize(BPSettings.get(BPSettingsKey.SESSION_EDITOR_FONT_SIZE))
        font.setFixedPitch(True)
        self.__codeEditor.setOptionFont(font)

        if includeConfig:
            for themeId in BPThemes.themes():
                self.__codeEditor.addTheme(BPThemes.theme(themeId))
                self.__codeEditor.setCurrentTheme(BPSettings.get(BPSettingsKey.CONFIG_EDITOR_THEME_SELECTED))

            self.__codeEditor.setOptionIndentWidth(BPSettings.get(BPSettingsKey.CONFIG_EDITOR_INDENT_WIDTH))
            self.__codeEditor.setOptionRightLimitPosition(BPSettings.get(BPSettingsKey.CONFIG_EDITOR_RIGHTLIMIT_WIDTH))
            self.__codeEditor.setOptionEnclosingCharacters(BPSettings.get(BPSettingsKey.CONFIG_EDITOR_ENCLOSINGCHARS).split(' '))
            self.__codeEditor.setOptionAutoClose(BPSettings.get(BPSettingsKey.CONFIG_EDITOR_AUTOCLOSE))
            self.__trimBeforeSave = BPSettings.get(BPSettingsKey.CONFIG_DOCUMENT_PY_TRIMONSAVE)

        self.__codeEditor.setOptionShowSpaces(BPSettings.get(BPSettingsKey.SESSION_EDITOR_SPACES_VISIBLE))
        self.__codeEditor.setOptionShowIndentLevel(BPSettings.get(BPSettingsKey.SESSION_EDITOR_INDENT_VISIBLE))
        self.__codeEditor.setOptionShowLineNumber(BPSettings.get(BPSettingsKey.SESSION_EDITOR_LINE_NUMBER_VISIBLE))
        self.__codeEditor.setOptionShowRightLimit(BPSettings.get(BPSettingsKey.SESSION_EDITOR_RIGHTLIMIT_VISIBLE))

        if BPSettings.get(BPSettingsKey.SESSION_EDITOR_WRAPLINES_ACTIVE):
            self.__codeEditor.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        else:
            self.__codeEditor.setLineWrapMode(QPlainTextEdit.NoWrap)

        if BPSettings.get(BPSettingsKey.SESSION_EDITOR_HIGHTLIGHT_FCTCLASSDECL_ACTIVE):
            if self.__highlightLinesRule is None:
                self.__highlightLinesRule = BPCodeEditorHighlightLineRulePython(None)
                self.__codeEditor.setHighlightedLineRule(self.__highlightLinesRule)
        else:
            self.__codeEditor.delHighlightedLineRule(self.__highlightLinesRule)
            self.__highlightLinesRule = None

        self.__codeEditor.setUpdatesEnabled(True)
        self.__lastUpdateTime = lastUpdateTime
        self.__invalidate = 0

    def modified(self):
        """Return if document is modified or not"""
        return self.__codeEditor.document().isModified()

    def setModified(self, value):
        """Set if document is modified or not"""
        return self.__codeEditor.document().setModified(value)

    def modifiedExternally(self):
        """Return if document is externally modifiedf or not"""
        return self.__fileExternallyModified

    def writeable(self):
        """Return if document (file on disk) is writeable

        Notes:
        - a document writeable can be flagged as readOnly
        - a document that is not writeable is flagged as readOnly
        """
        return not self.__fileIsReadOnly

    def readOnly(self):
        """Return if document is in read only mode"""
        return self.__codeEditor.isReadOnly() or self.__fileIsReadOnly

    def setReadOnly(self, value=None):
        """Set if document is in read only mode"""
        if self.__fileIsReadOnly:
            # if file on disk is read-only, then force read only mode for document
            self.__codeEditor.setReadOnly(True)
            return

        if value is None:
            value = not self.__codeEditor.isReadOnly()
        self.__codeEditor.setReadOnly(value)

    def close(self, deleteCache=True):
        """Close document"""
        self.__stopWatcher()

        try:
            self.__codeEditor.readOnlyModeChanged.disconnect()
        except Exception:
            pass

        try:
            self.__codeEditor.overwriteModeChanged.disconnect()
        except Exception:
            pass

        try:
            self.__codeEditor.cursorCoordinatesChanged.disconnect()
        except Exception:
            pass

        try:
            self.__codeEditor.modificationChanged.disconnect()
        except Exception:
            pass

        try:
            self.__codeEditor.textChanged.disconnect()
        except Exception:
            pass

        try:
            self.__codeEditor.redoAvailable.disconnect()
        except Exception:
            pass

        try:
            self.__codeEditor.undoAvailable.disconnect()
        except Exception:
            pass

        try:
            self.__codeEditor.selectionChanged.disconnect()
        except Exception:
            pass

        try:
            self.__codeEditor.copyAvailable.disconnect()
        except Exception:
            pass

        try:
            self.__codeEditor.fontSizeChanged.disconnect()
        except Exception:
            pass

        try:
            self.__codeEditor.textCopyToClipboard.disconnect()
        except Exception:
            pass

        try:
            self.__codeEditor.textCutToClipboard.disconnect()
        except Exception:
            pass

        if deleteCache:
            self.deleteCache()

    def open(self, fileName):
        """Open document from given `fileName`

        If document can't be opened (doesn't exists or no read access) return False
        otherwise returns True
        """
        try:
            self.__documentFileName = fileName
            with open(self.__documentFileName, "r") as fHandle:
                self.__codeEditor.setPlainText(fHandle.read())
            self.setModified(False)
            self.__checkFileIsReadOnly()
            self.__lastSavedTime = self.__fileTimeStamp()
            self.__lastUpdateTime = self.__lastSavedTime
            self.__fileExternallyModified = False
            self.__initWatcher()
        except Exception as e:
            self.__addAlert(WBPDocument.ALERT_FILE_CANTOPEN)
            Debug.print('[WBPDocument.open] unable to open file {0}: {1}', fileName, str(e))
            return False

        return True

    def reload(self):
        """Force document content to reloaded from disk

        If document can't be reloaded (doesn't exists anymore or no read access) return False
        otherwise returns True
        """
        if self.__documentFileName is None:
            return

        return self.open(self.__documentFileName)

    def save(self, forceSave=False):
        """Save document

        If document don't have fileName, return False (ie: the saveAs() must be explicitely called)
        If document can't be saved, raise an exception
        """
        if self.__documentFileName is None:
            return False

        docText = self.__codeEditor.toPlainText()
        if self.__trimBeforeSave:
            if re.search(r"\s+$", docText, flags=re.M):
                editorState = self.__codeEditor.editorState()
                self.__codeEditor.setUpdatesEnabled(False)
                self.__codeEditor.setPlainText(trimLinesRight(docText))
                self.__codeEditor.restoreEditorState(editorState)
                self.__codeEditor.setUpdatesEnabled(True)
                self.setModified(True)

        if self.modified() or forceSave:
            # save only if has been modified
            try:
                # as the file will be modified, stop to watch on it
                self.__stopWatcher()
                with open(self.__documentFileName, "w") as fHandle:
                    fHandle.write(docText)
                self.__fileExternallyModified = False
                self.setModified(False)
                # now can watch it again
                self.__initWatcher()

                self.saveCache()
                self.__lastSavedTime = self.__fileTimeStamp()
            except Exception as e:
                self.__addAlert(WBPDocument.ALERT_FILE_CANTSAVE)
                Debug.print('[WBPDocument.save] unable to save file {0}: {1}', self.__documentFileName, str(e))
                return False

        return True

    def saveAs(self, fileName):
        """Save document with given `fileName`

        If document can't be saved, raise an exception (and fileName is not modified!)
        """
        # save only if has been modified
        docText = self.__codeEditor.toPlainText()
        if self.__trimBeforeSave:
            if re.search(r"\s+$", docText, flags=re.M):
                editorState = self.__codeEditor.editorState()
                self.__codeEditor.setUpdatesEnabled(False)
                self.__codeEditor.setPlainText(trimLinesRight(docText))
                self.__codeEditor.restoreEditorState(editorState)
                self.__codeEditor.setUpdatesEnabled(True)

        try:
            self.__stopWatcher()
            with open(fileName, "w") as fHandle:
                fHandle.write(docText)
            self.setModified(False)
            self.__documentFileName = fileName
            self.__newDocNumber = 0
            self.saveCache()
            self.__initWatcher()
        except Exception as e:
            self.__addAlert(WBPDocument.ALERT_FILE_CANTSAVE)
            Debug.print('[WBPDocument.saveAs] unable to save file {0}: {1}', self.__documentFileName, str(e))
            return False

        return True

    def fileName(self):
        """Return document file name, or None if not yet defined"""
        return self.__documentFileName

    def tabName(self, full=False):
        """Return expected name to display for document in a tab

        - File name (without path) if filename is available
        - "<New document X>" otherwise
        """
        if self.__documentFileName is None:
            return f"<{i18n('New document')} {self.__newDocNumber}>"
        elif full:
            return self.__documentFileName
        else:
            return os.path.basename(self.__documentFileName)

    def cacheFileName(self):
        """Return document file name from cache"""
        return os.path.join(self.__uiController.cachePath('documents'), self.__documentCacheUuid)

    def cacheFileNameConsole(self):
        """Return console autosave document file name from cache"""
        return os.path.join(self.__uiController.cachePath('documents'), f"{self.__documentCacheUuid}.console")

    def cacheUuid(self):
        """Return document uuid"""
        return self.__documentCacheUuid

    def saveCache(self, delayedSave=0):
        """Save current content to cache

        A cache file is a binary file made of:
            32bits Flags
            0000 0000 0000 0000 0000 0000 0000 0001: document has a selection
            0000 0000 0000 0000 0000 0000 0000 0010: document is modified
            0000 0000 0000 0000 0000 0000 0000 0100: document have a file name
            0000 0000 0000 0000 0000 0000 0000 1000: document is read-only mode
            0000 0000 0000 0000 0000 0000 0001 0000: document is in overwrite mode

            . a UInt2 integer (cache file format version = 0x0001)
            . a UInt4 integer (contains flags)
            . a UInt2 integer (contains new document number)
            . a UInt4 integer (contains selection position start, from cursor in document)
            . a UInt4 integer (contains selection position end, from cursor in document; 0 if no selection)
            . a PStr2 string (contains full path/name of original document, empty if none)
            . a Float8 timestamp (contain timestamp of last *file* modification, 0 if no file)
            . a PStr4 string (contains document content, empty if not modified)
            . a Float8 timestamp (contain timestamp of last *document* modification)

        The `delayedSave` value is provided in milliseconds
        If `delayedSave` equal 0, save cache immediately
        Otherwise, start a counter of `delayedSave`ms before saving
            - If another `delayedSave` is requested before timeout is reached, cancel timeout and start new one
              This allows to save content in cache while user type code, without generate lag due to save process
        """
        if delayedSave > 0:
            self.__delayedSaveTimer.start(delayedSave)
        else:
            # if save immediately, cancel any delayedSave
            self.__delayedSaveTimer.stop()

        cursor = self.__codeEditor.textCursor()
        dataWrite = BytesRW()

        flags = 0x00

        if cursor.selectionStart() != cursor.selectionEnd():
            flags |= 0b0000_0001

        if self.modified():
            flags |= 0b0000_0010

        if not (self.__documentFileName is None or self.__documentFileName == ''):
            flags |= 0b0000_0100

        if self.readOnly():
            flags |= 0b0000_1000

        if self.__codeEditor.overwriteMode():
            flags |= 0b0001_0000

        dataWrite.writeUInt2(0x0001)
        dataWrite.writeUInt4(flags)
        dataWrite.writeUInt2(self.__newDocNumber)

        if cursor.selectionStart() == cursor.selectionEnd():
            dataWrite.writeUInt4(max(0, cursor.position()))
            dataWrite.writeUInt4(0)
        else:
            dataWrite.writeUInt4(cursor.selectionStart())
            dataWrite.writeUInt4(cursor.selectionEnd())

        if not (self.__documentFileName is None or self.__documentFileName == ''):
            dataWrite.writePStr2(self.__documentFileName)
            if os.path.isfile(self.__documentFileName):
                dataWrite.writeFloat8(os.path.getmtime(self.__documentFileName))
            else:
                dataWrite.writeFloat8(0.0)
        else:
            dataWrite.writePStr2('')
            dataWrite.writeFloat8(0.0)

        if self.modified():
            dataWrite.writePStr4(self.__codeEditor.toPlainText())
        else:
            dataWrite.writePStr4('')

        dataWrite.writeFloat8(self.__lastUpdateTime)

        try:
            with open(self.cacheFileName(), "wb") as fHandle:
                fHandle.write(dataWrite.getvalue())
            dataWrite.close()
        except Exception as e:
            Debug.print('[WBPDocument.saveCache] unable to save file {0}: {1}', self.cacheFileName(), str(e))
            if dataWrite:
                dataWrite.close()
            return False

        return True

    def openCache(self, uuid):
        """Open content from cache

        Force to modified when opened
        """
        self.__documentCacheUuid = uuid

        try:
            dataRead = None
            with open(self.cacheFileName(), "rb") as fHandle:
                dataRead = BytesRW(fHandle.read())
        except Exception as e:
            Debug.print('[WBPDocument.openCache] unable to open file {0}: {1}', self.cacheFileName(), str(e))
            if dataRead:
                dataRead.close()
            return False

        # version, ignore it
        dataRead.readUInt2()

        flags = dataRead.readUInt4()
        newDocNumber = dataRead.readUInt2()

        cursorSelStart = dataRead.readUInt4()
        cursorSelEnd = dataRead.readUInt4()

        fullPathFileName = dataRead.readPStr2()
        timestamp = dataRead.readFloat8()
        docContent = dataRead.readPStr4()
        lastUpdateTime = dataRead.readFloat8()

        dataRead.close()

        if flags & 0b0000_0100 == 0b0000_0100 and fullPathFileName != '':
            # document name a file name, read file content
            newDocNumber = 0
            if not self.open(fullPathFileName):
                # force document to keep file name
                self.__documentFileName = fullPathFileName
                # alert already defined by open() method, so none to add here
                self.__initWatcher()
            else:
                if os.path.getmtime(self.__documentFileName) != timestamp:
                    self.__addAlert(WBPDocument.ALERT_FILE_TIMESTAMP)

        self.__newDocNumber = newDocNumber

        if flags & 0b0000_0010 == 0b0000_0010:
            # document has been modified
            # apply last modified version
            # => can't use setPlainText() as it clear undo/redo stack
            # self.setPlainText(docContent)
            # self.setModified(True)
            cursor = self.__codeEditor.textCursor()
            cursor.select(QTextCursor.Document)
            cursor.insertText(docContent)

        # manage cursor position
        cursor = self.__codeEditor.textCursor()
        cursor.setPosition(cursorSelStart, QTextCursor.MoveAnchor)
        if flags & 0b0000_0001 == 0b0000_0001:
            # there a selection, go selection end
            cursor.setPosition(cursorSelEnd, QTextCursor.KeepAnchor)
        self.__codeEditor.setTextCursor(cursor)

        self.__checkFileIsReadOnly()

        if flags & 0b0000_1000 == 0b0000_1000:
            # file is flagged as read-only mode
            self.setReadOnly(True)

        if flags & 0b0001_0000 == 0b0001_0000:
            # file is flagged as in overwrite mode
            self.__codeEditor.setOverwriteMode(True)

        self.__updateAlerts()
        self.__lastUpdateTime = lastUpdateTime
        return True

    def deleteCache(self):
        """Delete cache file, if exists"""
        fileName = self.cacheFileName()
        if os.path.isfile(fileName):
            try:
                os.remove(fileName)
            except Exception as e:
                pass

    def newDocNumber(self):
        """Return document number

        =0: document has been opened from a file
        >0: document is a new created document
        """
        return self.__newDocNumber

    def setNewDocNumber(self, number):
        """Set document number """
        self.__newDocNumber = number

    def codeEditor(self):
        """Return codeEditor instance"""
        return self.__codeEditor

    def setFocus(self):
        """Set focus to code editor"""
        self.__codeEditor.setFocus()

    def content(self):
        """Return document content"""
        return self.__codeEditor.toPlainText()

    def setContent(self, content, undoable=True):
        """Return document content"""
        if isinstance(content, list):
            content = os.linesep.join(content)
        if undoable:
            cursor = self.__codeEditor.textCursor()
            cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(content)
            cursor.endEditBlock()
        else:
            self.__codeEditor.setPlainText(content)

    def languageDefinition(self):
        """return document languageDef"""
        return self.__codeEditor.languageDefinition()

    def setLanguageDefinition(self, languageDef):
        """set document languageDef"""
        if not isinstance(languageDef, LanguageDef):
            raise EInvalidType("Given `languageDef` must be a <LanguageDef>")

        if self.__codeEditor.languageDefinition() is None or self.__codeEditor.languageDefinition().name() != languageDef.name():
            # changing language def use cursor and seems to trigger 'textChanged' signal
            # in this case don't want to change the last updateTime of document
            lastUpdateTime = self.__lastUpdateTime
            self.__codeEditor.setLanguageDefinition(languageDef)
            self.__lastUpdateTime = lastUpdateTime
            self.languageDefChanged.emit(self)

    def lastModificationTime(self):
        """Return last modification time"""
        return self.__lastUpdateTime

    def lastSavedTime(self):
        """Return last file save time"""
        return self.__lastSavedTime

    def alerts(self):
        """Return alerts list, mostly contains alert related to external file modifications"""
        return self.__alerts


class BPDocuments(QObject):
    """Document manager

    The BPDocuments manage documents:
    - open
    - close
    - saved/unsaved
    - ...

    It will emit signal to update dockers, status bar, tabbar, ...
    """
    # active document has been modified
    # note: when active document is modified, none of the "something on active document has been changed" signal are
    #       emitted, considering this one implies all signal are emitted
    activeDocumentChanged = Signal(WBPDocument)

    # a document has been added
    documentAdded = Signal(WBPDocument)

    # a document has been removed
    documentRemoved = Signal(WBPDocument)

    # document has been reloaded
    documentReloaded = Signal(WBPDocument)

    # document has been saved
    documentSaved = Signal(WBPDocument)

    # something on active document has been changed
    readOnlyModeChanged = Signal(WBPDocument)
    overwriteModeChanged = Signal(WBPDocument)
    cursorCoordinatesChanged = Signal(WBPDocument)
    modificationChanged = Signal(WBPDocument)
    textChanged = Signal(WBPDocument)
    redoAvailable = Signal(WBPDocument)
    undoAvailable = Signal(WBPDocument)
    selectionChanged = Signal(WBPDocument)
    copyAvailable = Signal(WBPDocument)
    languageDefChanged = Signal(WBPDocument)
    fontSizeChanged = Signal(WBPDocument)
    fileExternallyChanged = Signal(WBPDocumentBase)
    textCopyToClipboard = Signal(WBPDocumentBase, str)
    textCutToClipboard = Signal(WBPDocumentBase, str)

    def __init__(self, uiController, parent=None):
        super(BPDocuments, self).__init__(parent)

        self.__counterNewDocument = 0
        self.__documents = []

        self.__uiController = uiController

        self.__currentDocument = None
        self.__currentCursorToken = None

        # define if there's currently a mass update and we need to avoid to updated all opened documents
        self.__massUpdate = 0

    def __readOnlyModeChanged(self, document):
        """Need to update status of read-only mode"""
        self.readOnlyModeChanged.emit(document)

    def __overwriteModeChanged(self, document):
        """Need to update status of INSERT/OVERWRITE mode"""
        self.overwriteModeChanged.emit(document)

    def __cursorCoordinatesChanged(self, document):
        """Need to update status of cursor position"""
        self.cursorCoordinatesChanged.emit(document)

    def __modificationChanged(self, document):
        """need to update status modified/saved"""
        self.modificationChanged.emit(document)

    def __textChanged(self, document):
        """content of document changed"""
        self.textChanged.emit(document)

    def __redoAvailable(self, document):
        """content of document changed"""
        self.redoAvailable.emit(document)

    def __undoAvailable(self, document):
        """content of document changed"""
        self.undoAvailable.emit(document)

    def __selectionChanged(self, document):
        """content of document changed"""
        self.selectionChanged.emit(document)

    def __copyAvailable(self, document):
        """content of document changed"""
        self.copyAvailable.emit(document)

    def __languageDefChanged(self, document):
        """language definition document changed"""
        self.languageDefChanged.emit(document)

    def __fontSizeChanged(self, document):
        """font size of document changed"""
        self.fontSizeChanged.emit(document)

    def __fileExternallyChanged(self, document):
        """file has been modified outside bulipy"""
        self.fileExternallyChanged.emit(document)

    def __textCopyToClipboard(self, document, text):
        """text from document has been copied to clipboard"""
        self.textCopyToClipboard.emit(document, text)

    def __textCutToClipboard(self, document, text):
        """text from document has been cut to clipboard"""
        self.textCutToClipboard.emit(document, text)

    def __addDocument(self, document, counterNewDocument=0):
        """Add a new document"""
        # append new document to document list
        self.__documents.append(document)

        # set document number according to current one available in document manager
        document.setNewDocNumber(counterNewDocument)

        # all documents signal are managed by current document manager
        # this allows to simplify management of ui: just connect document manager to update ui whichever active document is
        # currently managed
        document.readOnlyModeChanged.connect(self.__readOnlyModeChanged)
        document.overwriteModeChanged.connect(self.__overwriteModeChanged)
        document.cursorCoordinatesChanged.connect(self.__cursorCoordinatesChanged)
        document.modificationChanged.connect(self.__modificationChanged)
        document.textChanged.connect(self.__textChanged)
        document.redoAvailable.connect(self.__redoAvailable)
        document.undoAvailable.connect(self.__undoAvailable)
        document.selectionChanged.connect(self.__selectionChanged)
        document.copyAvailable.connect(self.__copyAvailable)
        document.languageDefChanged.connect(self.__languageDefChanged)
        document.fontSizeChanged.connect(self.__fontSizeChanged)
        document.fileExternallyChanged.connect(self.__fileExternallyChanged)
        document.textCopyToClipboard.connect(self.__textCopyToClipboard)
        document.textCutToClipboard.connect(self.__textCutToClipboard)

        # emit signal the new document has been added
        self.documentAdded.emit(document)
        self.setActiveDocument(document)

    def initialise(self, documentsList, activeDocument):
        """Initialise document manager with list of documents to load"""
        self.__counterNewDocument = 0
        self.__documents = []

        for fileName in documentsList:
            # can be a filename or @uuid
            self.openDocument(fileName)
            document = self.document()

            if document and document.newDocNumber() > self.__counterNewDocument:
                self.__counterNewDocument = document.newDocNumber()

        if len(self.__documents) == 0:
            # if no document opened (from previous session) then automatically create a new one
            # (always have a document)
            self.newDocument()
        else:
            self.setActiveDocument(activeDocument)

    def cleanup(self):
        """Cleanup current opened document list"""
        while len(self.__documents):
            document = self.__documents.pop()
            document.readOnlyModeChanged.disconnect()
            document.overwriteModeChanged.disconnect()
            document.cursorCoordinatesChanged.disconnect()
            document.modificationChanged.disconnect()
            document.fileExternallyChanged.disconnect()
            document.textChanged.disconnect()
            document.redoAvailable.disconnect()
            document.undoAvailable.disconnect()
            document.selectionChanged.disconnect()
            document.copyAvailable.disconnect()
            document.languageDefChanged.disconnect()
            document.fontSizeChanged.disconnect()
            document.textCopyToClipboard.disconnect()
            document.textCutToClipboard.disconnect()
            document.close(False)

        self.__currentDocument = None
        self.__counterNewDocument = 0

    def updateSettings(self, includeConfig=False):
        """Global settings has been modified, update documents according to settings"""
        if self.__massUpdate > 0:
            return

        # update active document first (first visible)
        self.__currentDocument.applySettings(includeConfig)
        for document in self.__documents:
            if document != self.__currentDocument:
                document.applySettings(includeConfig)

    def count(self):
        """Return number of documents"""
        return len(self.__documents)

    def documents(self):
        """Return a list of WBPDocument"""
        return self.__documents

    def document(self, documentId=None):
        """Return document from given `documentId`

        If `documentId` is None, return current active document
        If document is not found, return None
        """
        if documentId is None:
            # no documentId, use current document
            return self.__currentDocument
        elif isinstance(documentId, WBPDocument):
            # a document, get id
            documentId = documentId.cacheUuid()
        elif isinstance(documentId, int):
            # an index, get id at index
            if documentId >= 0 and documentId < len(self.__documents):
                documentId = self.__documents[documentId].cacheUuid()
            else:
                return None

        for document in self.__documents:
            if documentId == document.cacheUuid():
                return document

        return None

    def setActiveDocument(self, documentId):
        """Set given document as active document

        Given `documentId` is:
        - a BPDocument
        - a BPDocument cacheUuid()
        - a BPDocument fileName()

        If document is not found in list of managed documents, does nothing and return False
        """
        if isinstance(documentId, WBPDocument):
            documentId = documentId.cacheUuid()
        elif not isinstance(documentId, str):
            raise EInvalidType("Given `documentId` must be <str> or <BPDocument>")

        if document := self.document(documentId):
            # found!
            if document != self.__currentDocument:
                self.__currentDocument = document
                self.__currentDocument.codeEditor().setFocus(Qt.OtherFocusReason)
                self.activeDocumentChanged.emit(self.__currentDocument)
                return True

        return False

    def newDocument(self):
        """Create a new empty document

        - New tab
        - New WBPDocument
        """
        self.__counterNewDocument += 1

        document = WBPDocument(None, self.__uiController.languageDef(), self.__uiController)
        self.__addDocument(document, self.__counterNewDocument)
        return True

    def openDocument(self, fileName):
        """open a document from given `fileName`

        if `fileName` start with a "@" file is opened as a cache file information

        Return False if document can't be opened
        Return True if document has been opened OR is already opened
        """
        fromCache = False
        if result := re.match('@(.*)', fileName):
            fileName = result.groups()[0]
            fromCache = True

        if not fromCache:
            for document in self.__documents:
                if fileName == document.fileName():
                    # document is already opened
                    self.setActiveDocument(document.cacheUuid())
                    return True

        document = WBPDocument(None, None, self.__uiController)

        if fromCache:
            opened = document.openCache(fileName)
        else:
            opened = document.open(fileName)

        if opened:
            if not document.fileName():
                # if no file ,name (from cache...) assume document is a python document
                extension = '.py'
            else:
                extension = Path(document.fileName()).suffix

            document.setLanguageDefinition(self.__uiController.languageDef(extension))

            # Document has been opened, add it
            self.__addDocument(document, document.newDocNumber())
            return True
        else:
            # unable to open document
            return False

    def reloadDocument(self, documentId=None):
        """reload content of opened document defined by given `documentId`

        If `documentId` is None, reload current document

        If can't reload (ie: a new document never saved), does nothing
        """
        if document := self.document(documentId):
            if document.fileName() is None:
                # no file name, can't reload it :-)
                return False

            returned = document.reload()

            if returned:
                self.documentReloaded.emit(document)

            return returned
        return False

    def closeDocument(self, documentId=None):
        """Close document defined by given `documentReloaded`

        If `documentReloaded` is None, close current document
        """
        if document := self.document(documentId):
            index = 0
            for index, documentToDelete in enumerate(self.__documents):
                if documentToDelete.cacheUuid() == document.cacheUuid():
                    self.__documents.pop(index)
                    document.readOnlyModeChanged.disconnect()
                    document.overwriteModeChanged.disconnect()
                    document.cursorCoordinatesChanged.disconnect()
                    document.modificationChanged.disconnect()
                    document.fileExternallyChanged.disconnect()
                    document.textChanged.disconnect()
                    document.redoAvailable.disconnect()
                    document.undoAvailable.disconnect()
                    document.selectionChanged.disconnect()
                    document.copyAvailable.disconnect()
                    document.languageDefChanged.disconnect()
                    document.fontSizeChanged.disconnect()
                    document.textCopyToClipboard.disconnect()
                    document.textCutToClipboard.disconnect()
                    document.close()
                    self.documentRemoved.emit(document)

                    if index > 0:
                        # set previous document active
                        self.setActiveDocument(self.__documents[index-1])

                    # no need to continue to search
                    break

            if len(self.__documents) == 0:
                self.__counterNewDocument = 0
                # can't have no document opened; create a new one (will be active)
                self.newDocument()

            return True
        return False

    def saveDocument(self, documentId=None, fileName=None):
        """Save document defined by given `documentId` with given `fileName`

        If `documentId` is None, save current document
        """
        if document := self.document(documentId):
            if fileName is None:
                # no file name provided
                # save document, considering a name is already defined on document
                returned = document.save()
            else:
                returned = document.saveAs(fileName)

            if returned:
                if fileExtension := re.search(r"(\.[^\.]*)$", document.fileName()):
                    # check if language for file extension has been modidied
                    if fileExtension.groups()[0] not in document.languageDefinition().extensions():
                        document.setLanguageDefinition(self.__uiController.languageDef(fileExtension.groups()[0]))

                self.documentSaved.emit(document)
            return returned
        return False

    def setCompletionHelpEnabled(self, value):
        """Change option setOptionAutoCompletionHelp() on all code editor"""
        if isinstance(value, bool) and self.__optionAutoCompletionHelp != value:
            self.__optionAutoCompletionHelp = value
            for document in self.__documents:
                document.codeEditor().setOptionAutoCompletionHelp(self.__optionAutoCompletionHelp)

    def isMassUpdate(self):
        """return if a mass update is ongoing"""
        return (self.__massUpdate > 0)

    def setMassUpdate(self, value):
        """set mass update mode"""
        if value:
            self.__massUpdate += 1
        else:
            self.__massUpdate -= 1

            if self.__massUpdate < 0:
                self.__massUpdate = 0

            if self.__massUpdate == 0:
                self.updateSettings()


class WBPDocumentTabs(QTabWidget):
    """Interface to manage documents tabs"""

    def __init__(self, parent=None):
        super(WBPDocumentTabs, self).__init__(parent)

        self.__uiController = None

        # use a customized QTabBar, to display unsaved document differently than
        # saved documents
        self.__tabBar = WTabBar(self)
        self.setTabBar(self.__tabBar)

        self.currentChanged.connect(self.__tabChanged)
        self.tabCloseRequested.connect(self.__tabRequestClose)

        self.setStyleSheet("""
            WBPDocumentTabs>* {
                padding: 4px 0 0 0;
                margin: -2px;
                border: 0px none;
                background: palette(Window);

            }
            WBPDocumentTabs::pane {
                padding: 0px;
                margin: 0px;
                border: 0px none;
                background: palette(Window);
            }
        """)

    def __tabChanged(self, index):
        """Active tab has been changed"""
        if index == -1:
            return
        self.__uiController.documents().setActiveDocument(self.document(index))

    def __tabRequestClose(self, index):
        """Trying to close a document"""
        self.__uiController.commandFileClose(index)

    def setUiController(self, uiController):
        """Define uiController for widget"""
        self.__uiController = uiController

    def document(self, index=None):
        """Return document from index

        If `index` is None, return current document
        """
        if index is None:
            return self.currentWidget()
        elif index >= 0 and index < self.count():
            return self.widget(index)
        else:
            raise EInvalidValue(f'Given `index` is not valid: {index}')

    def addDocument(self, document):
        """Add a tab for given `document` and activate tab"""
        newTabIndex = self.addTab(document, document.tabName())

        # switch to new opened/created document
        self.setCurrentIndex(newTabIndex)

        return newTabIndex

    def removeDocument(self, document):
        """Close given `document`"""
        if isinstance(document, WBPDocument):
            index = self.indexOf(document)
            if index > -1:
                self.removeTab(index)
                return True
        return False

    def updateDocument(self, document):
        """Update tab status for document"""
        if isinstance(document, WBPDocument):
            index = self.indexOf(document)
            if index > -1:
                self.setTabText(index, document.tabName())

                isModified = document.modified()
                if document.modifiedExternally():
                    color = QColor("#d02f3a")
                    isModified = True
                else:
                    color = None

                self.__tabBar.setTabModified(index, isModified, color)
                return True
        return False

    def setTab(self, document):
        """Switch to tab containing given document"""
        if isinstance(document, WBPDocument):
            index = self.indexOf(document)
            if index > -1:
                self.setCurrentIndex(index)
                return True
        return False


class WBPDocuments(QWidget):
    """Document manager

    Manage documents in splitted ared+tabs
    """
    def __init__(self, parent=None):
        super(WBPDocuments, self).__init__(parent)
        # default controller not yet initialised
        self.__uiController = None

        # a default tab manager is needed
        self.__defaultTabManager = self.__newWBPDocumentTabs()

        self.__msplitter = WMultiSplitter()
        self.__msplitter.setOrientation(Qt.Horizontal)
        self.__msplitter.addWidget(self.__defaultTabManager)

        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(4, 4, 4, 4)
        self.__layout.addWidget(self.__msplitter)

        self.setLayout(self.__layout)

    def __newWBPDocumentTabs(self):
        """create and return a new WBPDocumentTabs"""
        widget = WBPDocumentTabs()
        widget.setUiController(self.__uiController)
        widget.setTabPosition(QTabWidget.North)
        widget.setTabShape(QTabWidget.Rounded)
        widget.setElideMode(Qt.ElideNone)
        widget.setUsesScrollButtons(True)
        widget.setDocumentMode(False)
        widget.setTabsClosable(True)
        widget.setMovable(True)
        return widget

    def __getTabManager(self, document):
        """Return tab manager for document"""
        parent = document.parentWidget()
        while parent:
            if isinstance(parent, WBPDocumentTabs):
                return parent
            parent = parent.parentWidget()
        return None

    def setUiController(self, uiController):
        """Define uiController for widget"""
        self.__uiController = uiController
        self.__defaultTabManager.setUiController(self.__uiController)

    def setActive(self, document):
        """Set document as active:
        - set tab active
        - set focus to code editor
        """
        tabManager = self.__getTabManager(document)
        if tabManager:
            tabManager.setTab(document)
            document.setFocus()
            return True
        return False

    def addDocument(self, document):
        """Add `document` in current active tab manager"""
        # get current active document: new document will be added in same tab manager
        currentDocument = self.__uiController.currentDocument()
        if currentDocument:
            tabManager = self.__getTabManager(currentDocument)
            if tabManager:
                # tab manager found for current document
                # => add document to tab manager
                return tabManager.addDocument(document)

        # use default tabmaanger otherwise
        return self.__defaultTabManager.addDocument(document)

    def removeDocument(self, document):
        """Remove `document` from current active tab manager"""
        # get current active document: new document will be added in same tab manager
        tabManager = self.__getTabManager(document)
        if tabManager:
            # tab manager found for current document
            # => add document to tab manager
            return tabManager.removeDocument(document)
        return False

    def updateDocument(self, document):
        """Update `document` from current active tab manager"""
        # get current active document: new document will be updted in same tab manager
        tabManager = self.__getTabManager(document)
        if tabManager:
            # tab manager found for current document
            # => add document to tab manager
            return tabManager.updateDocument(document)
        return False

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

import re
import hashlib
import time

from PyQt5.Qt import *
from PyQt5.QtGui import (
        QColor,
        QFontMetrics,
        QFont,
        QBrush,
        QPen,
        QPainter,
        QTextCharFormat,
        QClipboard
    )
from PyQt5.QtWidgets import (
        QDockWidget,
        QTreeWidget
    )
from PyQt5.QtCore import (
        pyqtSignal as Signal
    )
from PyQt5.QtGui import (
        QFont,
        QPalette,
        QIcon,
        QSyntaxHighlighter,
        QTextDocument,
        QTextCursor
    )

from .bpdocument import WBPDocument

from ..pktk.modules.tokenizer import Tokenizer
from ..pktk.modules.languagedef import LanguageDef
from ..pktk.modules.strutils import wildcardToRegEx
from ..pktk.modules.timeutils import tsToStr
from ..pktk.modules.imgutils import buildIcon
from ..pktk.modules.utils import (
        regExIsValid,
        Debug
    )
from ..pktk.modules.bytesrw import BytesRW
from ..pktk.widgets.wseparator import WVLine
from ..pktk.widgets.wdockwidget import WDockWidget
from ..pktk.widgets.wsearchinput import (
        WSearchInput,
        SearchOptions
    )

from ..pktk.pktk import *


class BPDockWidgetClipboard(WDockWidget):
    """A dock widget to display opened clipboardContents (also, the closed one)"""

    OPTION_BTN_REGEX =               0b00000000000_00001
    OPTION_BTN_CASESENSITIVE =       0b00000000000_00010
    OPTION_BTN_WHOLEWORD =           0b00000000000_00100
    OPTION_BTN_BACKWARD =            0b00000000000_01000
    OPTION_BTN_HIGHLIGHT =           0b00000000000_10000
    # available bits:                        <--->
    OPTION_TXT_SEARCH =              0b10000000000_00000
    OPTION_FONTSIZE =                0b01000000000_00000
    OPTION_FONTNAME =                0b00100000000_00000
    OPTION_SORT_COLUMN =             0b00010000000_00000
    OPTION_SORT_ORDER =              0b00001000000_00000
    # available bits:                        <--->

    ROLE_HASH =             Qt.UserRole + 1
    ROLE_TOKENS =           Qt.UserRole + 2
    ROLE_SIZE =             Qt.UserRole + 3
    ROLE_MISSING_LINES =    Qt.UserRole + 4
    ROLE_RAWTEXT =          Qt.UserRole + 5
    ROLE_LANGUAGE =         Qt.UserRole + 6
    ROLE_FOUNDTEXT =        Qt.UserRole + 7

    SIZE_MARGINS = QSize(8, 16)
    SIZE_MAXLINES = 8

    @staticmethod
    def asDocument(text, languageDef, tokens, foundText, foundTextFmt):
        """Return a formatted QTextDocument"""
        textDocument = QTextDocument(text)
        cursor = QTextCursor(textDocument)

        if tokens and languageDef:
            tokens.resetIndex()
            while not (token := tokens.next()) is None:
                pStart = token.positionStart()
                if pStart <= len(text):
                    cursor.setPosition(pStart, QTextCursor.MoveAnchor)
                    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, token.length())
                    cursor.setCharFormat(languageDef.style(token))
                else:
                    # no need to continue as outside visible text
                    break

        if foundText:
            for found in foundText:
                if found[0] <= len(text):
                    cursor.setPosition(found[0], QTextCursor.MoveAnchor)
                    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, found[1])
                    cursor.setCharFormat(foundTextFmt)
                else:
                    # no need to continue as outside visible text
                    break

        return textDocument

    def __init__(self, parent, documents, name='Clipboard'):
        super(BPDockWidgetClipboard, self).__init__(name, parent)

        self.__cacheFile = os.path.join(parent.uiController().cachePath('clipboard'), "clipboard")

        self.__documents = documents
        self.__filteredFound = None
        self.__fontMetrics = None

        self.__foundTextFmt = QTextCharFormat()
        self.__foundTextFmt.setBackground(QBrush(QColor('#2b961f')))
        self.__foundTextFmt.setForeground(QBrush(QColor('#f5eb00')))

        self.__documents.textCopyToClipboard.connect(self.__addText)
        self.__documents.textCutToClipboard.connect(self.__addText)

        self.__widget = QWidget(self)
        self.__widget.setMinimumWidth(200)

        self.__layout = QVBoxLayout(self.__widget)
        self.__layout.setContentsMargins(4, 4, 4, 0)
        self.__widget.setLayout(self.__layout)

        self.__siSearch = WSearchInput(WSearchInput.OPTION_SHOW_BUTTON_REGEX |
                                       WSearchInput.OPTION_SHOW_BUTTON_CASESENSITIVE |
                                       WSearchInput.OPTION_SHOW_BUTTON_WHOLEWORD |
                                       WSearchInput.OPTION_SHOW_BUTTON_SHOWHIDE, self)
        self.__siSearch.searchOptionModified.connect(self.__searchOptionModified)
        self.__siSearch.searchActivated.connect(self.__searchActivated)
        self.__siSearch.searchModified.connect(self.__searchModified)

        self.__twClipboard = QTreeWidget(self.__widget)
        self.__twClipboard.itemDoubleClicked.connect(self.__insertInCurrentDocument)
        self.__twClipboard.itemSelectionChanged.connect(self.__currentSelectionChanged)
        self.__twClipboard.setAlternatingRowColors(True)
        self.__twClipboard.setColumnCount(2)
        self.__twClipboard.setAllColumnsShowFocus(True)
        self.__twClipboard.setUniformRowHeights(False)
        self.__twClipboard.setItemsExpandable(False)
        self.__twClipboard.setRootIsDecorated(False)
        self.__twClipboard.setSortingEnabled(True)
        self.__twClipboard.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.__twClipboard.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.__twClipboard.setSelectionMode(QAbstractItemView.SingleSelection)
        self.__twClipboard.setHeaderLabels([i18n('Content'),
                                            i18n('Date/Time')
                                            ])
        font = self.__twClipboard.font()
        font.setStyleHint(QFont.Monospace)
        font.setFamily('DejaVu Sans Mono, Consolas, Courier New')
        self.__twClipboard.setFont(font)

        self.__btClear = QToolButton(self)
        self.__btClear.setAutoRaise(True)
        self.__btClear.setIcon(buildIcon('pktk:clear'))
        self.__btClear.setToolTip(i18n('Clear clipboard'))
        self.__btClear.clicked.connect(self.__clipboardClear)

        self.__btRemove = QToolButton(self)
        self.__btRemove.setAutoRaise(True)
        self.__btRemove.setIcon(buildIcon('pktk:delete'))
        self.__btRemove.setToolTip(i18n('Remove selected content'))
        self.__btRemove.clicked.connect(self.__clipboardRemoveSelected)

        self.__btPushBack = QToolButton(self)
        self.__btPushBack.setAutoRaise(True)
        self.__btPushBack.setIcon(buildIcon('pktk:clipboard_pushback'))
        self.__btPushBack.setToolTip(i18n('Push back to clipboard'))
        self.__btPushBack.clicked.connect(self.__clipboardPushBack)

        self.__lbNfo = QLabel()

        self.__tbLayout = QHBoxLayout(self.__widget)
        self.__tbLayout.setContentsMargins(0, 0, 0, 0)

        self.__tbLayout.addWidget(self.__btClear)
        self.__tbLayout.addWidget(self.__btRemove)
        self.__tbLayout.addWidget(WVLine(self))
        self.__tbLayout.addWidget(self.__btPushBack)
        self.__tbLayout.addWidget(self.__siSearch)
        self.__layout.addLayout(self.__tbLayout)
        self.__layout.addWidget(self.__twClipboard)
        self.__layout.addWidget(self.__lbNfo)

        self.__setFontSize(font.pointSize())

        self.__twClipboardItemDelegate = BPDockWidgetClipboardItemDelegate(self.__avgLineHeight, font, self)
        self.__twClipboard.setItemDelegate(self.__twClipboardItemDelegate)

        self.updateStatus()
        self.setWidget(self.__widget)
        self.__loadCache()
        self.__updateNfo()

    def __textHash(self, text):
        """calculate hash for given text"""
        return hashlib.sha256(text.encode()).digest()

    def __buildTooltip(self, text, languageDef, tokens, foundText, foundTextFmt):
        """Build tooltip"""
        ttFont = self.__twClipboard.font()
        ttFont.setPointSize(9)

        tooltipDoc = BPDockWidgetClipboard.asDocument(text, languageDef, tokens, foundText, foundTextFmt)
        tooltipDoc.setDefaultFont(ttFont)
        if tooltipDoc.blockCount() > 1:
            lines = i18n('lines')
        else:
            lines = i18n('line')
        tooltipNfo = f"<div style='background: {self.palette().toolTipText().color().name()}; color: {self.palette().toolTipBase().color().name()};'><i><b>{languageDef.name()}</b>, {tooltipDoc.blockCount()} {lines}</i></div>"
        tooltip = tooltipDoc.toHtml()
        tooltip = re.sub(r"<body([^>]+)>", fr"<body\1>{tooltipNfo}", tooltip)

        return tooltip

    def __buildSize(self, text):
        """Calculate sizes for item"""
        sizeText = self.__fontMetrics.size(0, text)
        if sizeText.height() > self.__maxLinesHeight:
            sizeText.setHeight(self.__maxLinesHeight)
        return sizeText

    def __setFont(self, font):
        """Update font size for clipboard list"""
        self.setUpdatesEnabled(False)
        self.__fontMetrics = QFontMetrics(font)
        self.__twClipboard.setFont(font)

        self.__avgLineHeight = self.__fontMetrics.size(0, "W").height()
        self.__maxLinesHeight = self.__avgLineHeight * BPDockWidgetClipboard.SIZE_MAXLINES

        sizeDate = self.__fontMetrics.size(0, "9999-99-99 99:99:99")

        for index in range(self.__twClipboard.topLevelItemCount()):
            item = self.__twClipboard.topLevelItem(index)
            sizeText = self.__buildSize(item.data(0, Qt.DisplayRole))
            item.setData(0, BPDockWidgetClipboard.ROLE_SIZE, sizeText + BPDockWidgetClipboard.SIZE_MARGINS)

        self.__twClipboard.setColumnWidth(0, self.__twClipboard.width() - sizeDate.width() - 2 * BPDockWidgetClipboard.SIZE_MARGINS.width())
        self.__twClipboard.setColumnWidth(1, sizeDate.width())

        self.setUpdatesEnabled(True)

    def __setFontSize(self, value):
        """Update font size for clipboard list"""
        font = self.__twClipboard.font()
        font.setPointSize(value)
        self.__setFont(font)

    def __setFontFamily(self, value):
        """Update font fazmily for clipboard list"""
        font = self.__twClipboard.font()
        font.setFamily(value)
        self.__setFont(font)

    def __itemIndexFromHash(self, hash):
        """Return item index from given hash, None if not found"""
        for index in range(self.__twClipboard.topLevelItemCount()):
            if self.__twClipboard.topLevelItem(index).data(0, BPDockWidgetClipboard.ROLE_HASH) == hash:
                return index
        return None

    def __updateButtons(self):
        """Update buttons according to current items & selection"""
        self.__btClear.setEnabled(self.__twClipboard.topLevelItemCount() > 0)
        self.__btRemove.setEnabled(len(self.__twClipboard.selectedItems()) > 0)
        self.__btPushBack.setEnabled(len(self.__twClipboard.selectedItems()) > 0)
        self.__updateNfo()
        self.__saveCache()

    def __updateNfo(self):
        """Update information"""
        nbTotal = self.__twClipboard.topLevelItemCount()
        if nbTotal == 0:
            self.__lbNfo.setVisible(False)
            self.__lbNfo.setText('')
        else:
            nbFound = ''

            if isinstance(self.__filteredFound, int):
                nbFound = f"{self.__filteredFound}/"

            self.__lbNfo.setText(f"{i18n('Items:')} {nbFound}{nbTotal}")
            self.__lbNfo.setVisible(True)

    def __searchActivated(self, text, options, searchAll=False):
        """Ask to search for text in clipboard items"""
        if text != '':
            regEx = text
            if options & SearchOptions.REGEX != SearchOptions.REGEX:
                # provided a a wildcard string; convert to REGEX
                regEx = wildcardToRegEx(regEx)

            flags = re.MULTILINE
            if options & SearchOptions.CASESENSITIVE != SearchOptions.CASESENSITIVE:
                flags |= re.IGNORECASE

            if options & SearchOptions.WHOLEWORD == SearchOptions.WHOLEWORD:
                regEx = fr"\b({regEx})\b"
            else:
                regEx = fr"({regEx})"

            if not regExIsValid(regEx):
                return

            self.__filteredFound = 0
            for index in range(self.__twClipboard.topLevelItemCount()):
                item = self.__twClipboard.topLevelItem(index)

                text = item.data(0, BPDockWidgetClipboard.ROLE_RAWTEXT)
                foundText = []
                for matchPattern in re.finditer(regEx, text, flags=flags):
                    # match found, memorize start + length
                    foundText.append((matchPattern.start(), matchPattern.end() - matchPattern.start()))

                if len(foundText):
                    self.__filteredFound += 1
                    item.setHidden(False)
                    item.setData(0, Qt.ToolTipRole, self.__buildTooltip(text,
                                                                        item.data(0, BPDockWidgetClipboard.ROLE_LANGUAGE),
                                                                        item.data(0, BPDockWidgetClipboard.ROLE_TOKENS),
                                                                        foundText,
                                                                        self.__foundTextFmt))
                    item.setData(0, BPDockWidgetClipboard.ROLE_FOUNDTEXT, foundText)
                else:
                    item.setHidden(True)
                    item.setData(0, BPDockWidgetClipboard.ROLE_FOUNDTEXT, None)
        elif self.__filteredFound is not None:
            # no search, no filter result to store
            self.__filteredFound = None
            for index in range(self.__twClipboard.topLevelItemCount()):
                item = self.__twClipboard.topLevelItem(index)
                item.setData(0, Qt.ToolTipRole, self.__buildTooltip(text,
                                                                    item.data(0, BPDockWidgetClipboard.ROLE_LANGUAGE),
                                                                    item.data(0, BPDockWidgetClipboard.ROLE_TOKENS),
                                                                    None,
                                                                    None))
                item.setData(0, BPDockWidgetClipboard.ROLE_FOUNDTEXT, None)
                item.setHidden(False)

        self.__updateButtons()

    def __searchModified(self, text, options):
        """option have been modified -- refresh search"""
        self.__searchActivated(text, options)

    def __searchOptionModified(self, text, options):
        """option have been modified -- refresh search"""
        self.__searchActivated(text, options)

    def __clipboardClear(self):
        """Remove all items"""
        self.__twClipboard.clear()
        self.__updateButtons()

    def __clipboardRemoveSelected(self):
        """Remove selected items"""
        selectedItems = self.__twClipboard.selectedItems()
        for item in selectedItems:
            index = self.__twClipboard.indexOfTopLevelItem(item)
            if index >= 0:
                self.__twClipboard.takeTopLevelItem(index)
        self.__updateButtons()

    def __clipboardPushBack(self):
        """Push back selected items to clipboard"""
        item = self.__twClipboard.currentItem()
        if item:
            mimeData = QMimeData()
            mimeData.setData('text/plain', item.data(0, BPDockWidgetClipboard.ROLE_RAWTEXT).encode())
            clipBoard = QApplication.clipboard()
            clipBoard.setMimeData(mimeData, QClipboard.Clipboard)

    def __insertInCurrentDocument(self, item, column):
        """Selected items content is inserted into current active document"""
        editor = self.__documents.document().codeEditor()
        editor.insertText(item.data(0, BPDockWidgetClipboard.ROLE_RAWTEXT))
        editor.setFocus()

    def __currentSelectionChanged(self):
        """Selected item changed"""
        self.__updateButtons()

    def __addText(self, document, text, dateTime=None):
        """Add/Update text in clipboard list"""
        textHash = self.__textHash(text)
        index = self.__itemIndexFromHash(textHash)
        if index is not None:
            item = self.__twClipboard.topLevelItem(index)
            item.setData(1, Qt.DisplayRole, tsToStr(time.time(), 'full'))
        else:
            tokens = None
            if isinstance(document, WBPDocument):
                languageDef = document.languageDefinition()
            elif isinstance(document, str):
                # language definition provided as an extension
                languageDef = self.parent().uiController().languageDef(document)

            splittedText = text.split("\n")

            # Keep only lines visible
            visibleText = "\n".join(splittedText[0:BPDockWidgetClipboard.SIZE_MAXLINES])

            tokens = languageDef.tokenizer().tokenize(text)

            # determinate geometries
            sizeText = self.__buildSize(text)

            # check if there's no visible line
            missingLines = max(0, len(splittedText) - BPDockWidgetClipboard.SIZE_MAXLINES)

            if dateTime is None:
                dateTime = tsToStr(time.time(), 'full')
            item = QTreeWidgetItem(None, [visibleText, dateTime])
            item.setData(0, Qt.ToolTipRole, self.__buildTooltip(text, languageDef, tokens, None, None))
            item.setData(0, BPDockWidgetClipboard.ROLE_HASH, textHash)
            item.setData(0, BPDockWidgetClipboard.ROLE_TOKENS, tokens)
            item.setData(0, BPDockWidgetClipboard.ROLE_SIZE, sizeText + BPDockWidgetClipboard.SIZE_MARGINS)
            item.setData(0, BPDockWidgetClipboard.ROLE_MISSING_LINES, missingLines)
            item.setData(0, BPDockWidgetClipboard.ROLE_RAWTEXT, text)
            item.setData(0, BPDockWidgetClipboard.ROLE_LANGUAGE, languageDef)
            item.setData(0, BPDockWidgetClipboard.ROLE_FOUNDTEXT, None)
            item.setData(1, Qt.TextAlignmentRole, Qt.AlignTop | Qt.AlignLeft)

            self.__twClipboard.insertTopLevelItem(0, item)

        self.__siSearch.applySearch()
        self.__twClipboard.scrollToItem(item, QAbstractItemView.EnsureVisible)
        self.__updateButtons()

    def __saveCache(self):
        """Save current clipboard to cache file

        A cache file is a binary file made of:
            32bits Flags (all zero, reserved values)
                0000 0000 0000 0000 0000 0000 0000 0000

            . a UInt2 integer (cache file format version = 0x0001)
            . a UInt4 integer (contains flags)
            . a UInt2 integer (contains number of clipboard content)
            . clipboard items

        Each clipboard item is:
            . a UInt2 integer = 0xF999 -- start of clipboard item
            . a PStr2 string (contains date-time as str YYYY-MM-DD HH:MI:SS)
            . a PStr2 string (contains content language first extension)
            . a PStr4 string (contains clipboard text)
        """
        dataWrite = BytesRW()

        flags = 0x00

        # version
        dataWrite.writeUInt2(0x0001)
        # flags
        dataWrite.writeUInt4(flags)
        # number of item in clipboard
        dataWrite.writeUInt2(self.__twClipboard.topLevelItemCount())

        for index in range(self.__twClipboard.topLevelItemCount()):
            item = item = self.__twClipboard.topLevelItem(index)
            if extension := item.data(0, BPDockWidgetClipboard.ROLE_LANGUAGE).extensions():
                extension = extension[0]
            else:
                extension = ''

            dataWrite.writeUInt2(0xF999)
            dataWrite.writePStr2(item.data(1, Qt.DisplayRole))
            dataWrite.writePStr2(extension)
            dataWrite.writePStr4(item.data(0, BPDockWidgetClipboard.ROLE_RAWTEXT))

        try:
            with open(self.__cacheFile, "wb") as fHandle:
                fHandle.write(dataWrite.getvalue())
            dataWrite.close()
        except Exception as e:
            Debug.print('[BPDockWidgetClipboard.saveCache] unable to save file {0}: {1}', self.__cacheFile, str(e))
            if dataWrite:
                dataWrite.close()
            return False

        return True

    def __loadCache(self):
        """Load clipboard from cache file"""
        if not os.path.exists(self.__cacheFile):
            return False

        self.setUpdatesEnabled(False)
        self.__twClipboard.clear()

        try:
            dataRead = None
            with open(self.__cacheFile, "rb") as fHandle:
                dataRead = BytesRW(fHandle.read())
        except Exception as e:
            Debug.print('[BPDockWidgetClipboard.loadCache] unable to open file {0}: {1}', self.__cacheFile, str(e))
            if dataRead:
                dataRead.close()
            return False

        canRead = True

        # version, ignore it
        dataRead.readUInt2()

        flags = dataRead.readUInt4()
        nbItems = dataRead.readUInt2()

        for index in range(nbItems):
            soi = dataRead.readUInt2()
            if soi != 0xF999:
                canRead = False
                break
            dateTime = dataRead.readPStr2()
            languageExtension = dataRead.readPStr2()
            rawText = dataRead.readPStr4()
            self.__addText(languageExtension, rawText, dateTime)

        self.__updateButtons()
        self.setUpdatesEnabled(True)
        return canRead

    def option(self, optionId):
        """Return current option value

        Option Id refer to:                                     Returned Value
            BPDockWidgetClipboard.OPTION_BTN_REGEX              Boolean
            BPDockWidgetClipboard.OPTION_BTN_CASESENSITIVE      Boolean
            BPDockWidgetClipboard.OPTION_BTN_WHOLEWORD          Boolean
            BPDockWidgetClipboard.OPTION_TXT_SEARCH             String
            BPDockWidgetClipboard.OPTION_FONTSIZE               Integer
            BPDockWidgetClipboard.OPTION_FONTNAME               String
            BPDockWidgetClipboard.OPTION_SORT_COLUMN            Integer
            BPDockWidgetClipboard.OPTION_SORT_ORDER             Integer
        """
        if optionId & BPDockWidgetClipboard.OPTION_BTN_REGEX == BPDockWidgetClipboard.OPTION_BTN_REGEX:
            return self.__siSearch.options() & SearchOptions.REGEX == SearchOptions.REGEX
        elif optionId & BPDockWidgetClipboard.OPTION_BTN_CASESENSITIVE == BPDockWidgetClipboard.OPTION_BTN_CASESENSITIVE:
            return self.__siSearch.options() & SearchOptions.CASESENSITIVE == SearchOptions.CASESENSITIVE
        elif optionId & BPDockWidgetClipboard.OPTION_BTN_WHOLEWORD == BPDockWidgetClipboard.OPTION_BTN_WHOLEWORD:
            return self.__siSearch.options() & SearchOptions.WHOLEWORD == SearchOptions.WHOLEWORD
        elif optionId & BPDockWidgetClipboard.OPTION_BTN_BACKWARD == BPDockWidgetClipboard.OPTION_BTN_BACKWARD:
            return self.__siSearch.options() & SearchOptions.BACKWARD == SearchOptions.BACKWARD
        elif optionId & BPDockWidgetClipboard.OPTION_BTN_HIGHLIGHT == BPDockWidgetClipboard.OPTION_BTN_HIGHLIGHT:
            return self.__siSearch.options() & SearchOptions.HIGHLIGHT == SearchOptions.HIGHLIGHT
        elif optionId & BPDockWidgetClipboard.OPTION_TXT_SEARCH == BPDockWidgetClipboard.OPTION_TXT_SEARCH:
            return self.__siSearch.searchText()
        elif optionId & BPDockWidgetClipboard.OPTION_FONTSIZE == BPDockWidgetClipboard.OPTION_FONTSIZE:
            return self.__twClipboard.font().pointSize()
        elif optionId & BPDockWidgetClipboard.OPTION_FONTNAME == BPDockWidgetClipboard.OPTION_FONTNAME:
            return self.__twClipboard.font().family()
        elif optionId & BPDockWidgetClipboard.OPTION_SORT_COLUMN == BPDockWidgetClipboard.OPTION_SORT_COLUMN:
            return self.__twClipboard.sortColumn()
        elif optionId & BPDockWidgetClipboard.OPTION_SORT_ORDER == BPDockWidgetClipboard.OPTION_SORT_ORDER:
            return self.__twClipboard.header().sortIndicatorOrder()

    def setOption(self, optionId, value):
        """Set option value

        Option Id refer to:                                     Value
            BPDockWidgetClipboard.OPTION_BTN_REGEX              Boolean
            BPDockWidgetClipboard.OPTION_BTN_CASESENSITIVE      Boolean
            BPDockWidgetClipboard.OPTION_BTN_WHOLEWORD          Boolean
            BPDockWidgetClipboard.OPTION_TXT_SEARCH             String
            BPDockWidgetClipboard.OPTION_FONTSIZE               Integer
            BPDockWidgetClipboard.OPTION_FONTNAME               String
            BPDockWidgetClipboard.OPTION_SORT_COLUMN            Integer
            BPDockWidgetClipboard.OPTION_SORT_ORDER             Integer
        """
        if optionId & BPDockWidgetClipboard.OPTION_BTN_REGEX == BPDockWidgetClipboard.OPTION_BTN_REGEX:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.REGEX)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.REGEX))
        elif optionId & BPDockWidgetClipboard.OPTION_BTN_CASESENSITIVE == BPDockWidgetClipboard.OPTION_BTN_CASESENSITIVE:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.CASESENSITIVE)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.CASESENSITIVE))
        elif optionId & BPDockWidgetClipboard.OPTION_BTN_WHOLEWORD == BPDockWidgetClipboard.OPTION_BTN_WHOLEWORD:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.WHOLEWORD)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.WHOLEWORD))
        elif optionId & BPDockWidgetClipboard.OPTION_BTN_BACKWARD == BPDockWidgetClipboard.OPTION_BTN_BACKWARD:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.BACKWARD)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.BACKWARD))
        elif optionId & BPDockWidgetClipboard.OPTION_BTN_HIGHLIGHT == BPDockWidgetClipboard.OPTION_BTN_HIGHLIGHT:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.HIGHLIGHT)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.HIGHLIGHT))
        elif optionId & BPDockWidgetClipboard.OPTION_TXT_SEARCH == BPDockWidgetClipboard.OPTION_TXT_SEARCH:
            self.__siSearch.setSearchText(value)
        elif optionId & BPDockWidgetClipboard.OPTION_FONTSIZE == BPDockWidgetClipboard.OPTION_FONTSIZE:
            self.__setFontSize(value)
        elif optionId & BPDockWidgetClipboard.OPTION_FONTNAME == BPDockWidgetClipboard.OPTION_FONTNAME:
            self.__setFontFamily(value)
        elif optionId & BPDockWidgetClipboard.OPTION_SORT_COLUMN == BPDockWidgetClipboard.OPTION_SORT_COLUMN:
            self.__twClipboard.sortItems(value, self.__twClipboard.header().sortIndicatorOrder())
        elif optionId & BPDockWidgetClipboard.OPTION_SORT_ORDER == BPDockWidgetClipboard.OPTION_SORT_ORDER:
            self.__twClipboard.sortItems(self.__twClipboard.sortColumn(), value)


class BPDockWidgetClipboardItemDelegate(QStyledItemDelegate):
    """Render clipboard item content"""

    def __init__(self, avgLineHeight, font, parent=None):
        super(BPDockWidgetClipboardItemDelegate, self).__init__(parent)
        self.__fontMissingLines = font
        self.__fontMissingLines.setPointSize(round(self.__fontMissingLines.pointSize() * 0.8))
        self.__fontMetricsMissingLines = QFontMetrics(self.__fontMissingLines)
        self.__avgLineHeight = avgLineHeight

        self.__foundTextFmt = QTextCharFormat()
        self.__foundTextFmt.setBackground(QBrush(QColor('#2b961f')))
        self.__foundTextFmt.setForeground(QBrush(QColor('#f5eb00')))

    def paint(self, painter, option, index):
        """Paint item"""
        if option.state & QStyle.State_HasFocus == QStyle.State_HasFocus:
            # remove focus style if active
            option.state = option.state & ~QStyle.State_HasFocus

        # use default constructor to paint item
        if index.column() == 0:
            # display clipboard content; sepecific render
            self.initStyleOption(option, index)

            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QPen(option.palette.color(QPalette.Text)))

            if (option.state & QStyle.State_Selected) == QStyle.State_Selected:
                painter.fillRect(option.rect, QBrush(option.palette.color(QPalette.Highlight)))
            else:
                painter.fillRect(option.rect, option.backgroundBrush)

            text = index.data(Qt.DisplayRole)

            if (option.state & QStyle.State_Selected) == QStyle.State_Selected:
                # item selected, no format
                tokens = None
                languageDef = None
            else:
                # not selected, format content
                tokens = index.data(BPDockWidgetClipboard.ROLE_TOKENS)
                languageDef = index.data(BPDockWidgetClipboard.ROLE_LANGUAGE)
            foundText = index.data(BPDockWidgetClipboard.ROLE_FOUNDTEXT)

            painter.save()
            painter.setClipRect(option.rect)
            painter.translate(QPointF(option.rect.topLeft()))

            textDocument = BPDockWidgetClipboard.asDocument(text, languageDef, tokens, foundText, self.__foundTextFmt)
            textDocument.setDocumentMargin(1)
            textDocument.setDefaultFont(option.font)
            textDocument.setPageSize(QSizeF(option.rect.size()))
            textDocument.drawContents(painter, QRectF())

            painter.restore()

            missingLines = index.data(BPDockWidgetClipboard.ROLE_MISSING_LINES)
            if missingLines > 0:
                # Initialise painter
                if (option.state & QStyle.State_Selected) == QStyle.State_Selected:
                    colorBg = option.palette.color(QPalette.Window)
                    colorFg = option.palette.color(QPalette.WindowText)
                else:
                    colorBg = option.palette.color(QPalette.Inactive, QPalette.Highlight)
                    colorFg = option.palette.color(QPalette.HighlightedText)
                colorBg.setAlphaF(0.9)

                hMargin = BPDockWidgetClipboard.SIZE_MARGINS.width()
                text = f"+{missingLines} additional hidden rows"
                textWidth = self.__fontMetricsMissingLines.size(0, text).width() + hMargin * 2

                bgRect = QRectF(option.rect.right() - textWidth, option.rect.bottom() - self.__avgLineHeight, textWidth, self.__avgLineHeight)

                painter.setFont(self.__fontMissingLines)
                painter.setBrush(QBrush(colorBg))
                painter.setPen(QPen(colorBg))
                painter.drawRoundedRect(bgRect, 2.5, 2.5)
                painter.setPen(QPen(colorFg))
                painter.drawText(bgRect, Qt.AlignHCenter | Qt.AlignVCenter, text)
            painter.restore()
        else:
            super(BPDockWidgetClipboardItemDelegate, self).paint(painter, option, index)

    def sizeHint(self, option, index):
        """calculate size for content"""
        if index.column() == 0:
            # clipboard content
            return index.data(BPDockWidgetClipboard.ROLE_SIZE)
        else:
            return QStyledItemDelegate.sizeHint(self, option, index)

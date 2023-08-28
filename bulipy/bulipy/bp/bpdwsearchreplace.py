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
from PyQt5.QtGui import (
        QTextCursor
    )
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtCore import (
        pyqtSignal as Signal
    )


from ..pktk.modules.imgutils import buildIcon
from ..pktk.widgets.wdockwidget import WDockWidget
from ..pktk.widgets.wseparator import WVLine
from ..pktk.widgets.wsearchinput import (
        WSearchInput,
        SearchOptions
    )
from ..pktk.widgets.wconsole import (
        WConsole,
        WConsoleType
    )

from ..pktk.pktk import *


class BPDockWidgetSearchReplace(WDockWidget):
    """A dock widget to provide search/replace methods like Atom editor"""

    OPTION_BTN_REGEX =               0b00000000000_00001
    OPTION_BTN_CASESENSITIVE =       0b00000000000_00010
    OPTION_BTN_WHOLEWORD =           0b00000000000_00100
    OPTION_BTN_BACKWARD =            0b00000000000_01000
    OPTION_BTN_HIGHLIGHT =           0b00000000000_10000
    # available bits:                     <------>
    OPTION_TXT_SEARCH =              0b10000000000_00000
    OPTION_TXT_REPLACE =             0b01000000000_00000
    OPTION_FONTSIZE =                0b00100000000_00000
    #                                     <------>

    def __init__(self, parent, documents, name='Search and Replace'):
        super(BPDockWidgetSearchReplace, self).__init__(name, parent)

        # used when options are modified, to compare current and previous options
        self.__currentOptions = 0
        self.__editor = None

        documents.activeDocumentChanged.connect(self.__documentChanged)
        documents.textChanged.connect(self.__documentContentChanged)

        self.__widget = QWidget(self)

        self.__layout = QVBoxLayout(self.__widget)
        self.__widget.setLayout(self.__layout)

        self.__cResults = WConsole(self)
        self.__cResults.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.__origResultsMouseEvent = self.__cResults.mousePressEvent
        self.__cResults.mousePressEvent = self.__resultsMouseClick

        self.__siSearch = WSearchInput(WSearchInput.OPTION_ALL_BUTTONS | WSearchInput.OPTION_SHOW_REPLACE, self)
        self.__siSearch.searchOptionModified.connect(self.__searchOptionModified)
        self.__siSearch.searchActivated.connect(self.__searchActivated)
        self.__siSearch.searchModified.connect(self.__searchModified)
        self.__siSearch.replaceActivated.connect(self.__replaceActivated)
        # self.__siSearch.replaceModified.connect(self.__replaceModified)

        self.__layout.addWidget(self.__siSearch)
        self.__layout.addWidget(self.__cResults)
        self.setWidget(self.__widget)

    def __documentChanged(self, document):
        """Current document has changed, get current editor"""
        self.__editor = document.codeEditor()
        self.__searchModified(self.__siSearch.searchText(), self.__siSearch.options())

    def __documentContentChanged(self, document):
        """Current document content has changed, update search results"""
        if self.__editor:
            self.__editor.search().clearCurrent()
            self.__searchModified(self.__siSearch.searchText(), self.__siSearch.options())

    def __resultsMouseClick(self, event):
        """Clicked on console"""
        if self.__origResultsMouseEvent:
            self.__origResultsMouseEvent(event)

        if self.__editor:
            cursor = self.__cResults.cursorForPosition(event.pos())
            if cursor:
                data = cursor.block().userData()
                if data is None:
                    return
                row = data.data('row')
                if row is not None:
                    self.__editor.scrollToLine(row)
                    self.__editor.setFocus()

    def __updateInformations(self, info):
        """Update information label"""
        if isinstance(info, int):
            if self.__siSearch.options() & SearchOptions.REGEX == SearchOptions.REGEX:
                searchType = i18n("regular expression")
            else:
                searchType = i18n("pattern")

            self.__siSearch.setResultsInformation(f"{i18n('Occurences matching given')} {searchType} "
                                                  f"<b><span style='font-family: consolas, monospace; color: palette(Highlight);'>{html.escape(self.__siSearch.searchText())}</span></b>: {info}")
        elif isinstance(info, str):
            self.__siSearch.setResultsInformation(info)

    def __searchActivated(self, text, options, searchAll=False):
        """Ask to search for text"""
        if not self.__editor:
            return

        all = self.__editor.search().searchAll(text, options)
        # if searchAll or options & SearchOptions.HIGHLIGHT == SearchOptions.HIGHLIGHT:
        #    # select all occurences
        #    all = self.__editor.search().searchAll(text, options)
        # else:
        #    # deselect all highlighted occurences
        #    self.__editor.search().searchAll(None, SearchOptions.HIGHLIGHT)

        nbOccurences = len(all)
        self.__updateInformations(nbOccurences)

        if nbOccurences > 1:
            txtOccurences = i18n("occurences")
        else:
            txtOccurences = i18n("occurence")

        if self.__siSearch.options() & SearchOptions.REGEX == SearchOptions.REGEX:
            searchType = i18n("regular expression")
        else:
            searchType = i18n("pattern")

        if searchAll:
            self.__cResults.clear()

            if nbOccurences == 0:
                self.__cResults.appendLine(f"#y#**{i18n('No occurences found in document for')} {searchType}**# #ly#*{text}*#", WConsoleType.WARNING)
            else:
                self.__cResults.appendLine(f"#y#**{nbOccurences}**# #g#**{txtOccurences} {i18n('found in document and matching')} {searchType}**# #lg#*{text}*#", WConsoleType.VALID)
                replaceWith = self.__siSearch.replaceText()
                replaceRegEx = options & SearchOptions.REGEX == SearchOptions.REGEX

                if replaceWith != '':
                    replaceWith = f"**##b#***{replaceWith}*"

                for occurence in all:
                    text = occurence.cursor.block().text()

                    selStart = occurence.cursor.selectionStart()-occurence.cursor.block().position()
                    selEnd = occurence.cursor.selectionEnd()-occurence.cursor.block().position()

                    replaceWithValue = replaceWith
                    if replaceRegEx:
                        if reResult := re.search(self.__siSearch.searchText(), text[selStart:selEnd]):
                            for index, replace in enumerate(reResult.groups()):
                                replaceWithValue = replaceWithValue.replace(f'${index+1}', replace)

                    text = WConsole.escape(text[:selStart]) + '*##g#**' + WConsole.escape(text[selStart:selEnd]) + replaceWithValue + '**##lk#*' + WConsole.escape(text[selEnd:])

                    self.__cResults.appendLine(f"{i18n('Line')} #y#**{occurence.cursor.blockNumber()+1}**#, #lk#*{text}*#", WConsoleType.NORMAL, {'row': occurence.cursor.blockNumber()+1})

            cursor = self.__cResults.textCursor()
            cursor.setPosition(0, QTextCursor.MoveAnchor)
            self.__cResults.setTextCursor(cursor)
            self.__cResults.ensureCursorVisible()
        else:
            # force highlight option when searching a text
            found = self.__editor.search().searchNext(text, options | SearchOptions.HIGHLIGHT)
            if found is None:
                self.__cResults.clear()
                self.__cResults.appendLine(f"#y#**{i18n('No occurences found in document for')} {searchType}**# #ly#*{text}*#", WConsoleType.WARNING)

        self.__currentOptions = options

    def __searchModified(self, text, options):
        """Ask to search for text -- search made only for highlighted text"""
        if not self.__editor:
            return

        if options & SearchOptions.REGEX == SearchOptions.REGEX:
            try:
                re.compile(text)
            except Exception as e:
                self.__updateInformations(i18n("Invalid regular expression!"))
                return

        nbOccurences = len(self.__editor.search().searchAll(text, options))
        self.__updateInformations(nbOccurences)

        self.__currentOptions = options

    def __searchOptionModified(self, text, options):
        """option have been modified, ask to search for text taking in account new options"""
        if not self.__editor:
            return

        nbOccurences = len(self.__editor.search().searchAll(text, options))
        self.__updateInformations(nbOccurences)

        if (self.__currentOptions ^ options) & SearchOptions.HIGHLIGHT != SearchOptions.HIGHLIGHT:
            # search only if modified option is not highlight all

            # force highlight option when searching a text
            self.__editor.search().searchNext(text, options | SearchOptions.HIGHLIGHT)

        self.__currentOptions = options

    def __replaceActivated(self, searchText, replaceText, options, replaceAll=False):
        """Ask to replace text"""
        if not self.__editor:
            return

        if options & SearchOptions.REGEX == SearchOptions.REGEX:
            searchType = "regular expression"
        else:
            searchType = "pattern"

        self.__editor.search().searchAll(searchText, options)
        # if replaceAll or options & SearchOptions.HIGHLIGHT == SearchOptions.HIGHLIGHT:
        #    # select all occurences
        #    all = self.__editor.search().searchAll(searchText, options)
        # else:
        #    # deselect all highlighted occurences
        #    self.__editor.search().searchAll(None, SearchOptions.HIGHLIGHT)

        if replaceAll:
            self.__cResults.clear()
            replaced = self.__editor.search().replaceAll(searchText, replaceText, options)

            if replaced > 1:
                txtOccurences = "occurences"
                textReplaced = i18n("have been replaced")
            else:
                txtOccurences = "occurence"
                textReplaced = i18n("has been replaced")

            if replaced == 0:
                self.__cResults.appendLine(f"#y#**{i18n('No occurences found in document for')} {searchType}**# #ly#*{searchText}*#\n#y#**{i18n('Nothing has been replaced')}**#", WConsoleType.WARNING)
            else:
                self.__cResults.appendLine(f"#y#**{replaced}**# #g#**{txtOccurences} {i18n('found in document and matching')} {searchType}**# #lg#*{searchText}*# #g#**{textReplaced}**#", WConsoleType.VALID)

        else:
            # force highlight option when searching a text
            replaced = self.__editor.search().replaceNext(searchText, replaceText, options | SearchOptions.HIGHLIGHT)
            if not replaced:
                self.__cResults.clear()
                self.__cResults.appendLine(f"#y#**{i18n('No occurences found in document for')} {searchType}**# #ly#*{searchText}*#\n#y#**{i18n('Nothing has been replaced')}**#", WConsoleType.WARNING)

        self.__currentOptions = options

    def onActivate(self):
        """When activated, set focus to search field"""
        self.__siSearch.qLineEditSearch().setFocus()

    def option(self, optionId):
        """Return current option value

        Option Id refer to:                                                 Returned Value
            BPDockWidgetSearchReplace.OPTION_BTN_REGEX                      Boolean
            BPDockWidgetSearchReplace.OPTION_BTN_CASESENSITIVE              Boolean
            BPDockWidgetSearchReplace.OPTION_BTN_WHOLEWORD                  Boolean
            BPDockWidgetSearchReplace.OPTION_BTN_BACKWARD                   Boolean
            BPDockWidgetSearchReplace.OPTION_BTN_HIGHLIGHT                  Boolean
            BPDockWidgetSearchReplace.OPTION_TXT_SEARCH                     String
            BPDockWidgetSearchReplace.OPTION_TXT_REPLACE                    String
            BPDockWidgetSearchReplace.OPTION_FONTSIZE                       Integer
        """
        if optionId & BPDockWidgetSearchReplace.OPTION_BTN_REGEX == BPDockWidgetSearchReplace.OPTION_BTN_REGEX:
            return self.__siSearch.options() & SearchOptions.REGEX == SearchOptions.REGEX
        elif optionId & BPDockWidgetSearchReplace.OPTION_BTN_CASESENSITIVE == BPDockWidgetSearchReplace.OPTION_BTN_CASESENSITIVE:
            return self.__siSearch.options() & SearchOptions.CASESENSITIVE == SearchOptions.CASESENSITIVE
        elif optionId & BPDockWidgetSearchReplace.OPTION_BTN_WHOLEWORD == BPDockWidgetSearchReplace.OPTION_BTN_WHOLEWORD:
            return self.__siSearch.options() & SearchOptions.WHOLEWORD == SearchOptions.WHOLEWORD
        elif optionId & BPDockWidgetSearchReplace.OPTION_BTN_BACKWARD == BPDockWidgetSearchReplace.OPTION_BTN_BACKWARD:
            return self.__siSearch.options() & SearchOptions.BACKWARD == SearchOptions.BACKWARD
        elif optionId & BPDockWidgetSearchReplace.OPTION_BTN_HIGHLIGHT == BPDockWidgetSearchReplace.OPTION_BTN_HIGHLIGHT:
            return self.__siSearch.options() & SearchOptions.HIGHLIGHT == SearchOptions.HIGHLIGHT
        elif optionId & BPDockWidgetSearchReplace.OPTION_TXT_SEARCH == BPDockWidgetSearchReplace.OPTION_TXT_SEARCH:
            return self.__siSearch.searchText()
        elif optionId & BPDockWidgetSearchReplace.OPTION_TXT_REPLACE == BPDockWidgetSearchReplace.OPTION_TXT_REPLACE:
            return self.__siSearch.replaceText()
        elif optionId & BPDockWidgetSearchReplace.OPTION_FONTSIZE == BPDockWidgetSearchReplace.OPTION_FONTSIZE:
            return self.__cResults.optionFontSize()

    def setOption(self, optionId, value):
        """Set option value

        Option Id refer to:                                                 Value
            BPDockWidgetSearchReplace.OPTION_BTN_REGEX                      Boolean
            BPDockWidgetSearchReplace.OPTION_BTN_CASESENSITIVE              Boolean
            BPDockWidgetSearchReplace.OPTION_BTN_WHOLEWORD                  Boolean
            BPDockWidgetSearchReplace.OPTION_BTN_BACKWARD                   Boolean
            BPDockWidgetSearchReplace.OPTION_BTN_HIGHLIGHT                  Boolean
            BPDockWidgetSearchReplace.OPTION_TXT_SEARCH                     String
            BPDockWidgetSearchReplace.OPTION_TXT_REPLACE                    String
            BPDockWidgetSearchReplace.OPTION_FONTSIZE                       Integer
        """
        if optionId & BPDockWidgetSearchReplace.OPTION_BTN_REGEX == BPDockWidgetSearchReplace.OPTION_BTN_REGEX:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.REGEX)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.REGEX))
        elif optionId & BPDockWidgetSearchReplace.OPTION_BTN_CASESENSITIVE == BPDockWidgetSearchReplace.OPTION_BTN_CASESENSITIVE:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.CASESENSITIVE)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.CASESENSITIVE))
        elif optionId & BPDockWidgetSearchReplace.OPTION_BTN_WHOLEWORD == BPDockWidgetSearchReplace.OPTION_BTN_WHOLEWORD:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.WHOLEWORD)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.WHOLEWORD))
        elif optionId & BPDockWidgetSearchReplace.OPTION_BTN_BACKWARD == BPDockWidgetSearchReplace.OPTION_BTN_BACKWARD:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.BACKWARD)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.BACKWARD))
        elif optionId & BPDockWidgetSearchReplace.OPTION_BTN_HIGHLIGHT == BPDockWidgetSearchReplace.OPTION_BTN_HIGHLIGHT:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.HIGHLIGHT)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.HIGHLIGHT))
        elif optionId & BPDockWidgetSearchReplace.OPTION_TXT_SEARCH == BPDockWidgetSearchReplace.OPTION_TXT_SEARCH:
            self.__siSearch.setSearchText(value)
        elif optionId & BPDockWidgetSearchReplace.OPTION_TXT_REPLACE == BPDockWidgetSearchReplace.OPTION_TXT_REPLACE:
            self.__siSearch.setReplaceText(value)
        elif optionId & BPDockWidgetSearchReplace.OPTION_FONTSIZE == BPDockWidgetSearchReplace.OPTION_FONTSIZE:
            self.__cResults.setOptionFontSize(value)

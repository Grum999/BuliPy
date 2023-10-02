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
import json

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

from .bplanguagedef import BPLanguageDefPython

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


class BPDockWidgetQuickKritaApi(WDockWidget):
    """A dock widget to display opened clipboardContents (also, the closed one)"""

    OPTION_BTN_REGEX =               0b00000000000_00001
    OPTION_BTN_CASESENSITIVE =       0b00000000000_00010
    # available bits:                    <------->
    OPTION_TXT_SEARCH =              0b10000000000_00000
    OPTION_SPLITTER =                0b01000000000_00000
    # available bits:                    <------->

    ROLE_CLASS_NAME = Qt.UserRole + 1
    ROLE_METHOD_NAME = Qt.UserRole + 2

    def __init__(self, parent, documents, name='Clipboard'):
        super(BPDockWidgetQuickKritaApi, self).__init__(name, parent)

        self.__filteredFound = None
        self.__pyKritaApiRef = {}

        self.__tag = None
        self.__tagName = ''
        self.__lastTagRef = ''

        self.__widget = QWidget(self)
        self.__widget.setMinimumWidth(200)

        self.__layout = QVBoxLayout(self.__widget)
        self.__layout.setContentsMargins(4, 4, 4, 0)
        self.__widget.setLayout(self.__layout)

        self.__siSearch = WSearchInput(WSearchInput.OPTION_SHOW_BUTTON_REGEX |
                                       WSearchInput.OPTION_SHOW_BUTTON_CASESENSITIVE |
                                       WSearchInput.OPTION_SHOW_BUTTON_SHOWHIDE, self)
        self.__siSearch.searchOptionModified.connect(self.__searchOptionModified)
        self.__siSearch.searchActivated.connect(self.__searchActivated)
        self.__siSearch.searchModified.connect(self.__searchModified)

        self.__twPyKritaApi = QTreeWidget(self.__widget)
        self.__twPyKritaApi.itemSelectionChanged.connect(self.__currentSelectionChanged)
        self.__twPyKritaApi.expanded.connect(lambda: self.__twPyKritaApi.resizeColumnToContents(0))
        self.__twPyKritaApi.setColumnCount(2)
        self.__twPyKritaApi.setHeaderHidden(True)
        self.__twPyKritaApi.setAllColumnsShowFocus(True)
        self.__twPyKritaApi.setUniformRowHeights(True)
        self.__twPyKritaApi.setItemsExpandable(True)
        self.__twPyKritaApi.setRootIsDecorated(True)
        self.__twPyKritaApi.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.__twPyKritaApi.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.__twPyKritaApi.setSelectionMode(QAbstractItemView.SingleSelection)
        self.__twPyKritaApi.header().setStretchLastSection(True)
        font = self.__twPyKritaApi.font()
        font.setStyleHint(QFont.Monospace)
        font.setFamily('DejaVu Sans Mono, Consolas, Courier New')
        self.__twPyKritaApi.setFont(font)

        self.__tbNfo = QTextBrowser(self)
        self.__tbNfo.setOpenExternalLinks(True)

        self.__splitter = QSplitter(self)
        self.__splitter.setOrientation(Qt.Vertical)
        self.__splitter.addWidget(self.__twPyKritaApi)
        self.__splitter.addWidget(self.__tbNfo)

        self.__btExpandAll = QToolButton(self)
        self.__btExpandAll.setAutoRaise(True)
        self.__btExpandAll.setIcon(buildIcon('pktk:list_tree_expand'))
        self.__btExpandAll.setToolTip(i18n('Expand all'))
        self.__btExpandAll.clicked.connect(lambda: self.__twPyKritaApi.expandAll())

        self.__btCollapseAll = QToolButton(self)
        self.__btCollapseAll.setAutoRaise(True)
        self.__btCollapseAll.setIcon(buildIcon('pktk:list_tree_collapse'))
        self.__btCollapseAll.setToolTip(i18n('Collapse all'))
        self.__btCollapseAll.clicked.connect(lambda: self.__twPyKritaApi.collapseAll())

        self.__tbLayout = QHBoxLayout(self.__widget)
        self.__tbLayout.setContentsMargins(0, 0, 0, 0)

        self.__tbLayout.addWidget(self.__btExpandAll)
        self.__tbLayout.addWidget(self.__btCollapseAll)
        self.__tbLayout.addWidget(self.__siSearch)

        self.__layout.addLayout(self.__tbLayout)
        self.__layout.addWidget(self.__splitter)

        self.updateStatus()
        self.setWidget(self.__widget)
        self.__buildRef()

    def __buildRef(self):
        """Load referential, build treeview reference"""
        refFileName = os.path.join(os.path.dirname(__file__), 'resources', 'docs', 'krita.json')
        try:
            with open(refFileName, 'r') as fHandle:
                self.__pyKritaApiRef = json.loads(fHandle.read())
        except Exception as e:
            print("Can't load referential")
            print(e)
            return

        self.__twPyKritaApi.clear()
        for className in sorted(self.__pyKritaApiRef['classes'].keys()):
            classNfo = self.__pyKritaApiRef['classes'][className]

            classItem = QTreeWidgetItem(None, [className, ''])
            classItem.setFirstColumnSpanned(True)
            classItem.setData(0, BPDockWidgetQuickKritaApi.ROLE_CLASS_NAME, className)
            classItem.setData(0, BPDockWidgetQuickKritaApi.ROLE_METHOD_NAME, None)

            for classMethod in sorted(classNfo['methods'], key=lambda m: m['name']):
                nfo = []
                if classMethod['isStatic']:
                    nfo.append(i18n('Static'))
                if classMethod['isVirtual']:
                    nfo.append(i18n('Virtual'))
                if classMethod['isSignal']:
                    nfo.append(i18n('Signal'))
                parameters = ''
                if len(classMethod['parameters']):
                    parameters = '...'

                classMethodItem = QTreeWidgetItem(classItem, [f"{classMethod['name']}({parameters})", ', '.join(nfo)])
                classMethodItem.setTextAlignment(1, Qt.AlignRight)
                classMethodItem.setData(0, BPDockWidgetQuickKritaApi.ROLE_CLASS_NAME, className)
                classMethodItem.setData(0, BPDockWidgetQuickKritaApi.ROLE_METHOD_NAME, classMethod['name'])
                classItem.addChild(classMethodItem)

            self.__twPyKritaApi.addTopLevelItem(classItem)
        self.__twPyKritaApi.resizeColumnToContents(0)

        self.__lastTagRef = sorted(self.__pyKritaApiRef['tags'].keys())[-1]
        self.__tag = self.__pyKritaApiRef['tags'][self.__lastTagRef]
        self.__tagName = f"{int(self.__lastTagRef[0:2])}.{int(self.__lastTagRef[2:4])}.{int(self.__lastTagRef[4:6])}"

    def __updateNfo(self):
        """Update information"""
        def getTagName(tagRef):
            """Return normalized version of tag"""
            return f"{int(tagRef[0:2])}.{int(tagRef[2:4])}.{int(tagRef[4:6])}"

        def codeToHtml(code):
            # return given code syntax highlighted
            languageDef = BPLanguageDefPython()
            tokens = languageDef.tokenizer().tokenize(code)

            textDocument = QTextDocument(code)
            cursor = QTextCursor(textDocument)

            tokens.resetIndex()
            while not (token := tokens.next()) is None:
                pStart = token.positionStart()
                cursor.setPosition(pStart, QTextCursor.MoveAnchor)
                cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, token.length())
                cursor.setCharFormat(languageDef.style(token))

            docHtml = textDocument.toHtml()
            docHtml = re.sub(r"^<!DOCTYPE.*<body[^>]*>(.*)</body></html>$", r"\1", docHtml, flags=re.I | re.S)
            docHtml = docHtml.replace('<p style="', '<p style="font-family: consolas, monospace; white-space: pre;')
            return f"<div style='baroder-left: 4px solid #888;'>{docHtml}</div>"

        def formatRefTags(refTags):
            # return ref tags: first Implemented, last updated
            implementedFrom = refTags["available"][0]
            lastUpdatedFrom = refTags["updated"][-1]

            styleRefTag="style='background-color: #2f4555;'"
            styleRefTagSymbol="style='background-color: #417496; font-family: consolas, monospace;'"
            # Qt HTML support is like hell :-/
            returned = f"<span title='First implemented version' {styleRefTagSymbol}>&nbsp;&#65291;&nbsp;</span><span {styleRefTag} title='First implemented version'>&nbsp;Krita {getTagName(implementedFrom)}&nbsp;</span>"
            if implementedFrom != lastUpdatedFrom:
                returned += f" <span title='Last updated version' {styleRefTagSymbol}>&nbsp;&#8635;&nbsp;</span><span {styleRefTag} title='Last updated version'>&nbsp;Krita {getTagName(lastUpdatedFrom)}&nbsp;</span>"

            return returned

        def formatDescription(description, method=None):
            # reformat description for HTML
            # Recognized tags
            #  @brief
            #  @code - @endcode
            #  @param
            #  @return
            def fixLines(text):
                returned = re.sub(r"([^\s])\n([^\s])", r"\1 \2", text)
                returned = re.sub(r"^\n|\n$", "", returned)
                return returned

            def getCodeBlocks(text):
                returnedText = ''
                returnedBlocks = {}
                blocks = re.split("\x01", text)
                codeBlockNumber = 0
                for index in range(len(blocks)):
                    if index % 2 == 0:
                        returnedText += blocks[index]
                    else:
                        codeBlockNumber += 1
                        blockId = f"$codeBlock{codeBlockNumber}$"
                        returnedText += blockId
                        returnedBlocks[blockId] =  re.sub(r"^\n|\n$", "", blocks[index])
                return (returnedText, returnedBlocks)

            def asParagraph(text, codeBlocks):
                returned = []
                for line in text.split("\n"):
                    if blocks := re.findall(r"(\$codeBlock\d+\$)", line):
                        for block in blocks:
                            if block in codeBlocks:
                                line = line.replace(block, codeToHtml(codeBlocks[block]))

                    returned.append(f"<p>{line}</p>")
                return ''.join(returned)

            returnedNfo = {}

            if method:
                if len(method['parameters']):
                    returnedNfo['@param'] = {}
                if method['returned'] != 'void':
                    returnedNfo['@return'] = "<span style='font-style: italic; opacity: 0.35;'>(no description provided)</span>"

            description = re.sub("^@@", "@", description, flags=re.I)
            description = re.sub("@code", "\x01", description, flags=re.I)
            description = re.sub("@endcode", "\x01", description, flags=re.I)
            description = re.sub(r"@[cp]\s", "", description, flags=re.I)
            description, codeBlocks = getCodeBlocks(description)
            splitted = re.split(r"^(@[a-z0-9]+\s)", description, flags=re.M | re.I)

            while len(splitted) and splitted[0].strip() == '':
                splitted.pop(0)

            if len(splitted) and re.search("^@", splitted[0]) is None:
                # a description without any tag?
                splitted.insert(0, "@brief")
                if method and {method['name']}:
                    splitted[1] = f"{method['name']} {splitted[1]}"

            index = 0
            while index < len(splitted):
                if splitted[index].strip() == '':
                    # expected a @xxx tag; skip empty lines
                    index += 1
                    continue

                docTag = splitted[index].lower().strip()
                docValue = splitted[index+1]

                if found := re.findall(r"(@param\s+[^\s]+)", docValue, flags=re.I):
                    for foundItem in found:
                        paramName = re.sub(r'@param\s+', '', foundItem, flags=re.I)
                        splitted.append('@param')
                        splitted.append(f"{paramName} ")
                        docValue = docValue.replace(foundItem, paramName)

                if docTag == '@brief':
                    if method and method['name']:
                        returnedNfo['@brief'] = fixLines(re.sub(fr"^{method['name']}\s+", "", docValue))
                    else:
                        returnedNfo['@brief'] = fixLines(docValue)
                elif docTag == '@param':
                    if '@param' not in returnedNfo:
                        returnedNfo['@param'] = {}

                    if nfo := re.search(r"^([a-z0-9_]+)\s+(.*)", docValue, flags=re.S | re.I):
                        paramName = nfo.groups()[0]
                        paramDescription = nfo.groups()[1]
                        if paramName not in returnedNfo['@param']:
                            if paramDescription == '':
                                paramDescription = '<span style="font-style: italic; opacity: 0.35;">(no description provided)</span>'
                            returnedNfo['@param'][paramName] = fixLines(paramDescription)
                        else:
                            if returnedNfo['@param'][paramName] == '' and paramDescription != '':
                                returnedNfo['@param'][paramName] = fixLines(paramDescription)

                elif docTag in ('@return', '@returns'):
                    returnedNfo['@return'] = fixLines(docValue)
                else:
                    if method and method['name']:
                        print(f"WARNING: unknown docTag {docTag} in function {method['name']}")
                    else:
                        print(f"WARNING: unknown docTag {docTag}")

                index += 2

            if len(codeBlocks):
                returnedNfo['@code'] = codeBlocks
            else:
                returnedNfo['@code'] = []

            # order:
            # - brief
            # - param
            # - return

            returned = []

            if '@brief' in returnedNfo:
                returned.append(asParagraph(returnedNfo['@brief'], returnedNfo['@code']))

            if '@param' in returnedNfo:
                paramTableTr = []
                styleTd = "style='border-bottom: 1px dotted #888;'"
                if method and len(method['parameters']):
                    # manage parameters in priority, using method parameters order
                    for parameter in method['parameters']:
                        parameterName = parameter['name']
                        if parameterName in returnedNfo['@param']:
                            paramTableTr.append(f"<tr><td {styleTd} width='25%'><span style='font-family: consolas, monospace;'>{parameterName}</span></td><td {styleTd}>{asParagraph(returnedNfo['@param'][parameterName], returnedNfo['@code'])}</td></tr>")
                        else:
                            paramTableTr.append(f"<tr><td {styleTd} width='25%'><span style='font-family: consolas, monospace;'>{parameterName}</span></td><td {styleTd}><span style='font-style: italic; opacity: 0.35;'>(no description provided)</span></td></tr>")
                else:
                    for parameterName, parameterDescription in returnedNfo['@param'].items():
                        paramTableTr.append(f"<tr><td {styleTd} width='25%'><span style='font-family: consolas, monospace;'>{parameterName}</span></td><td {styleTd}>{asParagraph(parameterDescription, returnedNfo['@code'])}</td></tr>")

                returned.append(f"""<h3>Parameters</h3>
                    <table class='paramList'>
                        {''.join(paramTableTr)}
                    </table>
                    """)

            if '@return' in returnedNfo:
                returned.append(f"""<h3>Return</h3>
                    <table class='paramList'>
                        <tr><td>{asParagraph(returnedNfo['@return'], returnedNfo['@code'])}</td></tr>
                    </table>
                    """)

            return "\n".join(returned)

        def htmlClass(className):
            classNfo = self.__pyKritaApiRef['classes'][className]
            return f"""
            <div class='buildFrom'>Build from <a target='_blank' style='text-decoration: none; font-family: consolas, monospace;' href='https://invent.kde.org/graphics/krita/-/blob/{self.__tag['hash']}/libs/libkis/{classNfo["fileName"]}'>{classNfo["fileName"]}</a></div>
            <div class='docRefTags'>{formatRefTags(classNfo["tagRef"])}</div>
            <div class='docString'>{formatDescription(classNfo["description"])}</div>
            """

        def htmlClassMethod(className, methodName):
            classNfo = self.__pyKritaApiRef['classes'][className]

            for methodNfo in classNfo['methods']:
                if methodNfo['name'] == methodName:
                    break

            styleMethodParamName = "style='color: #bdc3c7;'"
            styleMethodSep = "style='color: #e83e8c;'"
            styleMethodParameterType = "style=' color: #20c997;'"
            styleMethodParameterDefault = "style='color: #17a2b8;'"

            parameters = []
            for parameter in methodNfo['parameters']:
                if methodNfo['isSignal']:
                    parameters.append(f"<span {styleMethodParameterType}>{parameter['type']}</span>")
                else:
                    param = f"<span {styleMethodParamName}>{parameter['name']}</span>"
                    if parameter['type']:
                        param = f"{param}<span {styleMethodSep}>: </span><span {styleMethodParameterType}>{parameter['type']}</span>"
                    if parameter['default']:
                        param = f"{param}<span {styleMethodSep}> = </span><span {styleMethodParameterDefault}>{parameter['default']}</span>"
                    parameters.append(param)

            returnedType = ''
            if methodNfo["returned"] != 'void' and methodNfo["returned"] != className:
                returnedType = f"<span {styleMethodSep}> &#10142; </span><span {styleMethodParameterType}>{methodNfo['returned']}</span>"

            if len(parameters) > 1:
                spaces = ' ' * (len(methodNfo['name']) + 1)
                fctDef = f"""<div style='font-family: consolas, monospace; white-space: pre; font-size: medium;'><span style='color: #54a3d8; margin-bottom: 4px; padding-bottom: 4px;'>{methodNfo['name']}</span>""" \
                         f"""<span {styleMethodSep}>(</span>"""
                fctDef += f'<span {styleMethodSep}>,\n{spaces}</span>'.join(parameters)
                fctDef += f"\n{spaces}<span {styleMethodSep}>)</span>{returnedType}</div>"
            else:
                fctDef = f"""<div style='font-family: consolas, monospace; white-space: pre; font-size: medium;'><span style='color: #54a3d8;'>{methodNfo['name']}</span>""" \
                         f"""<span {styleMethodSep}>(</span>{f'<span {styleMethodSep}>, </span>'.join(parameters)}<span {styleMethodSep}>)</span>{returnedType}</div>"""


            flags = []
            if methodNfo['isVirtual']:
                flags.append(f"<span style='background-color: #007bff;'>&nbsp;Virtual&nbsp;</span>")
            if methodNfo['isStatic']:
                flags.append(f"<span style='background-color: #28a745;'>&nbsp;Static&nbsp;</span>")
            if methodNfo['isSignal']:
                flags.append(f"<span style='background-color: #e83e8c;'>&nbsp;Signal&nbsp;</span>")

            return f"""
            <div class='buildFrom'>Build from <a target='_blank' style='text-decoration: none; font-family: consolas, monospace;' href='https://invent.kde.org/graphics/krita/-/blob/{self.__tag['hash']}/libs/libkis/{classNfo["fileName"]}#L{methodNfo['sourceCodeLine']}'>{classNfo["fileName"]}</a></div>
            <h2 style='font-family: consolas, monospace; margin-bottom: 1px;'>{methodName}</h2>
            <div class='docRefTags'><table width='100%'><tr><td>{formatRefTags(methodNfo["tagRef"])}</td><td><div style='text-align: right;'>{'&nbsp;'.join(flags)}</div></td></tr></table></div>
            <div class='docString'><table width='100%'><tr><td style='border-bottom: 1px dotted #888;'>{fctDef}</td></tr><tr><td>{formatDescription(methodNfo["description"])}</td></tr></table></div>
            """

        item = self.__twPyKritaApi.currentItem()
        if item:
            className = item.data(0, BPDockWidgetQuickKritaApi.ROLE_CLASS_NAME)
            methodName = item.data(0, BPDockWidgetQuickKritaApi.ROLE_METHOD_NAME)

            if methodName is None:
                content = htmlClass(className)
            else:
                content = htmlClassMethod(className, methodName)

            html = f"""<!DOCTYPE HTML>
            <html>
                <body>
                    <h1>{className}</h1>
                    <div>
                        {content}
                    </div>
                </body>
            </html>
            """
            self.__tbNfo.setHtml(html)

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
            for index in range(self.__twPyKritaApi.topLevelItemCount()):
                itemClass = self.__twPyKritaApi.topLevelItem(index)
                className = itemClass.data(0, Qt.DisplayRole)

                if matchPattern := re.findall(regEx, className, flags=flags):
                    itemClass.setExpanded(False)
                    itemClass.setHidden(False)
                    for index in range(itemClass.childCount()):
                        itemClass.child(index).setHidden(False)
                else:
                    found = False
                    for index in range(itemClass.childCount()):
                        itemClassMethod = itemClass.child(index)
                        classMethodName = itemClassMethod.data(0, Qt.DisplayRole)

                        if matchPattern := re.findall(regEx, classMethodName, flags=flags):
                            itemClassMethod.setHidden(False)
                            found = True
                        else:
                            itemClassMethod.setHidden(True)

                    if found:
                        itemClass.setExpanded(True)
                        itemClass.setHidden(False)
                    else:
                        itemClass.setHidden(True)

        else:
            # no filter, display everything
            for index in range(self.__twPyKritaApi.topLevelItemCount()):
                itemClass = self.__twPyKritaApi.topLevelItem(index)
                className = itemClass.data(0, Qt.DisplayRole)
                itemClass.setHidden(False)
                for index in range(itemClass.childCount()):
                    itemClass.child(index).setHidden(False)

    def __searchModified(self, text, options):
        """option have been modified -- refresh search"""
        self.__searchActivated(text, options)

    def __searchOptionModified(self, text, options):
        """option have been modified -- refresh search"""
        self.__searchActivated(text, options)

    def __currentSelectionChanged(self):
        """Selected item has changed"""
        self.__updateNfo()

    def option(self, optionId):
        """Return current option value

        Option Id refer to:                                     Returned Value
            BPDockWidgetQuickKritaApi.OPTION_BTN_REGEX              Boolean
            BPDockWidgetQuickKritaApi.OPTION_BTN_CASESENSITIVE      Boolean
            BPDockWidgetQuickKritaApi.OPTION_TXT_SEARCH             String
            BPDockWidgetQuickKritaApi.OPTION_SPLITTER               List
        """
        if optionId & BPDockWidgetQuickKritaApi.OPTION_BTN_REGEX == BPDockWidgetQuickKritaApi.OPTION_BTN_REGEX:
            return self.__siSearch.options() & SearchOptions.REGEX == SearchOptions.REGEX
        elif optionId & BPDockWidgetQuickKritaApi.OPTION_BTN_CASESENSITIVE == BPDockWidgetQuickKritaApi.OPTION_BTN_CASESENSITIVE:
            return self.__siSearch.options() & SearchOptions.CASESENSITIVE == SearchOptions.CASESENSITIVE
        elif optionId & BPDockWidgetQuickKritaApi.OPTION_TXT_SEARCH == BPDockWidgetQuickKritaApi.OPTION_TXT_SEARCH:
            return self.__siSearch.searchText()
        elif optionId & BPDockWidgetQuickKritaApi.OPTION_SPLITTER == BPDockWidgetQuickKritaApi.OPTION_SPLITTER:
            return self.__splitter.sizes()

    def setOption(self, optionId, value):
        """Set option value

        Option Id refer to:                                     Value
            BPDockWidgetQuickKritaApi.OPTION_BTN_REGEX              Boolean
            BPDockWidgetQuickKritaApi.OPTION_BTN_CASESENSITIVE      Boolean
            BPDockWidgetQuickKritaApi.OPTION_BTN_WHOLEWORD          Boolean
            BPDockWidgetQuickKritaApi.OPTION_TXT_SEARCH             String
            BPDockWidgetQuickKritaApi.OPTION_SPLITTER               List
        """
        if optionId & BPDockWidgetQuickKritaApi.OPTION_BTN_REGEX == BPDockWidgetQuickKritaApi.OPTION_BTN_REGEX:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.REGEX)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.REGEX))
        elif optionId & BPDockWidgetQuickKritaApi.OPTION_BTN_CASESENSITIVE == BPDockWidgetQuickKritaApi.OPTION_BTN_CASESENSITIVE:
            if value:
                self.__siSearch.setOptions(self.__siSearch.options() | SearchOptions.CASESENSITIVE)
            else:
                self.__siSearch.setOptions(self.__siSearch.options() & (WSearchInput.OPTION_ALL ^ SearchOptions.CASESENSITIVE))
        elif optionId & BPDockWidgetQuickKritaApi.OPTION_TXT_SEARCH == BPDockWidgetQuickKritaApi.OPTION_TXT_SEARCH:
            self.__siSearch.setSearchText(value)
        elif optionId & BPDockWidgetQuickKritaApi.OPTION_SPLITTER == BPDockWidgetQuickKritaApi.OPTION_SPLITTER:
            self.__splitter.setSizes(value)

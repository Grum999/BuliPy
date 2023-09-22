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

from PyQt5.Qt import *
from PyQt5.QtGui import (
        QColor
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
        QIcon
    )

from ..pktk.modules.imgutils import bullet
from ..pktk.modules.timeutils import tsToStr
from ..pktk.widgets.wdockwidget import WDockWidget

from ..pktk.pktk import *


class BPDockWidgetDocuments(WDockWidget):
    """A dock widget to display opened documents (also, the closed one)"""

    __BULLET_SIZE = 12

    OPTION_SORT_COLUMN =    0b00000000000_00001
    OPTION_SORT_ORDER =     0b00000000000_00010

    def __init__(self, parent, documents, name='Documents'):
        super(BPDockWidgetDocuments, self).__init__(name, parent)

        self.__documents = documents
        self.__documents.documentAdded.connect(self.__documentAdded)
        self.__documents.documentRemoved.connect(self.__documentRemoved)
        self.__documents.documentSaved.connect(self.__documentSaved)
        self.__documents.textChanged.connect(self.__documentModified)
        self.__documents.modificationChanged.connect(self.__documentModified)
        self.__documents.fileExternallyChanged.connect(self.__documentModified)
        self.__documents.activeDocumentChanged.connect(self.__activeDocumentChanged)

        self.__widget = QWidget(self)
        self.__widget.setMinimumWidth(200)

        self.__layout = QVBoxLayout(self.__widget)
        self.__layout.setContentsMargins(4, 4, 4, 0)
        self.__widget.setLayout(self.__layout)

        self.__twDocuments = QTreeWidget(self.__widget)
        self.__twDocuments.setColumnCount(4)
        self.__twDocuments.setAllColumnsShowFocus(True)
        self.__twDocuments.setUniformRowHeights(True)
        self.__twDocuments.setItemsExpandable(True)
        self.__twDocuments.setRootIsDecorated(False)
        self.__twDocuments.setSortingEnabled(True)
        self.__twDocuments.setSelectionMode(QAbstractItemView.SingleSelection)
        self.__twDocuments.setHeaderLabels([i18n('Document'),
                                            i18n('File name'),
                                            i18n('Last modification'),
                                            i18n('Last saved')
                                            ])
        font = self.__twDocuments.font()
        font.setStyleHint(QFont.Monospace)
        font.setFamily('DejaVu Sans Mono, Consolas, Courier New')
        self.__twDocuments.setFont(font)
        self.__twDocuments.currentItemChanged.connect(self.__currentItemChanged)

        self.__layout.addWidget(self.__twDocuments)

        self.__iconBulletModified = QIcon(bullet(BPDockWidgetDocuments.__BULLET_SIZE, self.palette().color(QPalette.Active, QPalette.Highlight), 'circle'))
        self.__iconBulletExternalyModified = QIcon(bullet(BPDockWidgetDocuments.__BULLET_SIZE, QColor("#d02f3a"), 'circle'))
        self.__iconBulletNone = QIcon(bullet(BPDockWidgetDocuments.__BULLET_SIZE, QColor(Qt.transparent), 'square'))

        self.updateStatus()
        self.setWidget(self.__widget)

        self.__changeActiveDocument = False

        # to update modified date/time
        self.__delayedUpdateDict = {}
        self.__delayedUpdateTimer = QTimer()
        self.__delayedUpdateTimer.timeout.connect(lambda: self.__documentModified(None))

    def __currentItemChanged(self, current, previous):
        """Selected item changed, need to activate document"""
        self.__changeActiveDocument = True
        self.__documents.setActiveDocument(current.data(0, Qt.UserRole))
        self.__changeActiveDocument = False

    def __activeDocumentChanged(self, document):
        """Active document has changed"""
        if self.__changeActiveDocument is False:
            docItemIndex = self.__documentItem(document)
            if docItemIndex is not None:
                self.__twDocuments.setCurrentItem(self.__twDocuments.topLevelItem(docItemIndex))

    def __documentItem(self, document):
        """Return QTreeWidgetItem index for document, or None if not found"""
        uuid = document.cacheUuid()
        for index in range(self.__twDocuments.topLevelItemCount()):
            if self.__twDocuments.topLevelItem(index).data(0, Qt.UserRole) == uuid:
                return index
        return None

    def __documentAdded(self, document):
        """A document has been created/opened, add it to document list"""
        item = QTreeWidgetItem(None,
                               [document.tabName(False),
                                document.tabName(True),
                                tsToStr(document.lastModificationTime(), 'full')+' ',
                                tsToStr(document.lastSavedTime(), 'full')+' '
                                ])
        item.setData(0, Qt.UserRole, document.cacheUuid())
        self.__twDocuments.insertTopLevelItem(0, item)
        self.__twDocuments.resizeColumnToContents(0)
        self.__twDocuments.resizeColumnToContents(1)
        self.__twDocuments.resizeColumnToContents(2)
        self.__twDocuments.resizeColumnToContents(3)
        self.__documentModified(document)

    def __documentRemoved(self, document):
        """A document has been closed, remove it from list"""
        itemIndex = self.__documentItem(document)
        if itemIndex is not None:
            self.__twDocuments.takeTopLevelItem(itemIndex)

    def __documentSaved(self, document):
        """A document has been saved, update it in list"""
        itemIndex = self.__documentItem(document)
        if itemIndex is not None:
            item = self.__twDocuments.topLevelItem(itemIndex)
            item.setData(3, Qt.DisplayRole, tsToStr(document.lastSavedTime(), 'full')+' ')

    def __documentModified(self, document):
        """A document has been modified, update it in list"""
        if document is None:
            for documentToUpdate in self.__delayedUpdateDict.values():
                itemIndex = self.__documentItem(documentToUpdate)
                if itemIndex is not None:
                    item = self.__twDocuments.topLevelItem(itemIndex)
                    item.setData(2, Qt.DisplayRole, tsToStr(documentToUpdate.lastModificationTime(), 'full')+' ')

                    if len(documentToUpdate.alerts()):
                        item.setIcon(0, self.__iconBulletExternalyModified)
                    elif documentToUpdate.modified():
                        item.setIcon(0, self.__iconBulletModified)
                    else:
                        item.setIcon(0, self.__iconBulletNone)
            self.__delayedUpdateDict = {}
        else:
            # delay update, no need to spent cpu resouche to search document/update list each time document content is modified
            self.__delayedUpdateDict[document.cacheUuid()] = document
            self.__delayedUpdateTimer.start(125)

    def option(self, optionId):
        """Return current option value

        Option Id refer to:                                     Returned Value
            BPDockWidgetDocuments.OPTION_SORT_COLUMN            Integer
            BPDockWidgetDocuments.OPTION_SORT_ORDER             Integer
        """
        if optionId & BPDockWidgetDocuments.OPTION_SORT_COLUMN == BPDockWidgetDocuments.OPTION_SORT_COLUMN:
            return self.__twDocuments.sortColumn()
        elif optionId & BPDockWidgetDocuments.OPTION_SORT_ORDER == BPDockWidgetDocuments.OPTION_SORT_ORDER:
            return self.__twDocuments.header().sortIndicatorOrder()

    def setOption(self, optionId, value):
        """Set option value

        Option Id refer to:                                     Value
            BPDockWidgetDocuments.OPTION_SORT_COLUMN            Integer
            BPDockWidgetDocuments.OPTION_SORT_ORDER             Integer
        """
        if optionId & BPDockWidgetDocuments.OPTION_SORT_COLUMN == BPDockWidgetDocuments.OPTION_SORT_COLUMN:
            self.__twDocuments.sortItems(value, self.__twDocuments.header().sortIndicatorOrder())
        elif optionId & BPDockWidgetDocuments.OPTION_SORT_ORDER == BPDockWidgetDocuments.OPTION_SORT_ORDER:
            self.__twDocuments.sortItems(self.__twDocuments.sortColumn(), value)

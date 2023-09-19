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
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtCore import (
        pyqtSignal as Signal
    )

from ..pktk.widgets.wiconselector import WIconSelector
from ..pktk.widgets.wdockwidget import WDockWidget

from ..pktk.pktk import *


class BPDockWidgetIconSelector(WDockWidget):
    """A dock widget to display icons"""
    apply = Signal(str, int)       # upsert button cliked, apply color according to mode

    MODE_INSERT = 0x01
    MODE_UPDATE = 0x02

    def __init__(self, parent, documents, options, name='Icon Selector'):
        super(BPDockWidgetIconSelector, self).__init__(name, parent)

        self.__mode = None

        self.__widget = QWidget(self)
        self.__widget.setMinimumWidth(200)

        self.__layout = QVBoxLayout(self.__widget)
        self.__layout.setContentsMargins(4, 4, 4, 0)
        self.__widget.setLayout(self.__layout)

        self.__wIconSelector = WIconSelector(WIconSelector.OPTIONS_SHOW_STATUSBAR | options)
        self.__wIconSelector.doubleClicked.connect(self.__doubleClicked)

        self.__btnUpsert = QPushButton("xx")
        self.__btnUpsert.clicked.connect(self.__clicked)
        self.setMode(BPDockWidgetIconSelector.MODE_INSERT)

        self.__layout.addWidget(self.__wIconSelector)
        self.__layout.addWidget(self.__btnUpsert)

        self.updateStatus()
        self.setWidget(self.__widget)

    def __clicked(self):
        """Button has been clicked"""
        self.apply.emit(self.icon(), self.__mode)

    def __doubleClicked(self, value):
        """Button has been double-clicked"""
        self.apply.emit(value, self.__mode)

    def iconSizeIndex(self):
        """Return current iconSize Index value"""
        return self.__wIconSelector.iconSizeIndex()

    def setIconSizeIndex(self, value):
        """Set icon size index value"""
        self.__wIconSelector.setIconSizeIndex(value)

    def viewMode(self):
        """Return current icon view mode"""
        return self.__wIconSelector.viewMode()

    def setViewMode(self, mode):
        """Set icon view mode"""
        self.__wIconSelector.setViewMode(mode)

    def iconSelector(self):
        """Return icon selector instance"""
        return self.__wIconSelector

    def icon(self):
        """Return current color from color picker"""
        return self.__wIconSelector.icon()

    def setIcon(self, iconId):
        """Set current color"""
        return self.__wIconSelector.setIcon(iconId)

    def mode(self):
        """Return current mode: INSERT or UPDATE"""
        return self.__mode

    def setMode(self, mode):
        """Set button mode INSERT or REPLACE"""
        if self.__mode != mode:
            if mode == BPDockWidgetIconSelector.MODE_INSERT:
                self.__btnUpsert.setText(i18n('Insert icon'))
                self.__btnUpsert.setToolTip(i18n('Insert current icon in script'))
                self.__mode = mode
            elif mode == BPDockWidgetIconSelector.MODE_UPDATE:
                self.__btnUpsert.setText(i18n('Update icon'))
                self.__btnUpsert.setToolTip(i18n('Update current icon in script'))
                self.__mode = mode

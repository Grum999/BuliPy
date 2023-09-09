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

from ..pktk.widgets.wcolorselector import WColorPicker
from ..pktk.widgets.wdockwidget import WDockWidget

from ..pktk.pktk import *


class BPDockWidgetColorPicker(WDockWidget):
    """A dock widget to display color selector, to insert/update a color code in script"""
    apply = Signal(QColor, int)       # upsert button cliked, apply color according to mode

    MODE_INSERT = 0x01
    MODE_UPDATE = 0x02

    def __init__(self, parent, documents, name='Color Picker'):
        super(BPDockWidgetColorPicker, self).__init__(name, parent)

        self.__mode = BPDockWidgetColorPicker.MODE_INSERT

        self.__widget = QWidget(self)
        self.__widget.setMinimumWidth(200)

        self.__layout = QVBoxLayout(self.__widget)
        self.__layout.setContentsMargins(4, 4, 4, 0)
        self.__widget.setLayout(self.__layout)

        self.__cColorPicker = WColorPicker(self)
        self.__cColorPicker.setOptionMenu(WColorPicker.OPTION_MENU_RGB |
                                          WColorPicker.OPTION_MENU_CMYK |
                                          WColorPicker.OPTION_MENU_HSV |
                                          WColorPicker.OPTION_MENU_HSL |
                                          WColorPicker.OPTION_MENU_ALPHA |
                                          WColorPicker.OPTION_MENU_CSSRGB |
                                          WColorPicker.OPTION_MENU_COLCOMP |
                                          WColorPicker.OPTION_MENU_COLWHEEL |
                                          WColorPicker.OPTION_MENU_PALETTE |
                                          WColorPicker.OPTION_MENU_UICOMPACT |
                                          WColorPicker.OPTION_MENU_COLPREVIEW)
        self.__cColorPicker.setOptionLayout(['colorRGB', 'colorHSV', 'colorAlpha', 'colorCssRGB', 'colorWheel', 'colorPreview'])

        self.__btnUpsert = QPushButton("xx")
        self.__btnUpsert.clicked.connect(self.__clicked)
        self.setMode(self.__mode)

        self.__layout.addWidget(self.__cColorPicker)
        self.__layout.addWidget(self.__btnUpsert)

        self.updateStatus()
        self.setWidget(self.__widget)

    def __clicked(self):
        """Button has been clicked"""
        self.apply.emit(self.color(), self.__mode)

    def options(self):
        """Return current option value"""
        return self.__cColorPicker.optionLayout()

    def setOptions(self, value):
        """Set option value"""
        if "layoutOrientation:2" in value:
            value.remove('layoutOrientation:2')
        self.__cColorPicker.setOptionLayout(value)

    def colorPicker(self):
        """Return color picker instance"""
        return self.__cColorPicker

    def color(self):
        """Return current color from color picker"""
        return self.__cColorPicker.color()

    def setColor(self, color):
        """Set current color"""
        if isinstance(color, str):
            if r := re.search(r"^#([A-F0-9]{2})?([A-F0-9]{6})$", color, re.IGNORE):
                color = QColor(color)

        if not isinstance(color, QColor):
            raise EInvalidType("Given `color` must be a <QColor> or a valid <str> color value")

        self.__cColorPicker.setColor(color)

    def mode(self):
        """Return current mode: INSERT or UPDATE"""
        return self.__mode

    def setMode(self, mode):
        """Set button mode INSERT or REPLACE"""
        if mode == BPDockWidgetColorPicker.MODE_INSERT:
            self.__btnUpsert.setText(i18n('Insert color'))
            self.__btnUpsert.setToolTip(i18n('Insert current color in script'))
            self.__mode = mode
        elif mode == BPDockWidgetColorPicker.MODE_UPDATE:
            self.__btnUpsert.setText(i18n('Update color'))
            self.__btnUpsert.setToolTip(i18n('Update current color in script'))
            self.__mode = mode

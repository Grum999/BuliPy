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
# The bpopensavedialog module provides extended open/save dialog box with file preview
#


import re

from PyQt5.Qt import *

from ..pktk.modules.utils import Debug
from ..pktk.widgets.wcodeeditor import WCodeEditor
from ..pktk.widgets.wiodialog import WDialogFile
from ..pktk.pktk import *


class WBuliPyOpenSavePreview(WDialogFile.WSubWidget):
    """Preview used in open/save dialog box"""

    def __init__(self, uiController, parent=None):
        super(WBuliPyOpenSavePreview, self).__init__(parent)

        self.__uiController = uiController

        self.__codeEditor = WCodeEditor(self)
        self.__codeEditor.setOptionMultiLine(True)
        self.__codeEditor.setOptionShowLineNumber(True)
        self.__codeEditor.setOptionAllowWheelSetFontSize(True)
        self.__codeEditor.setReadOnly(True)
        self.__codeEditor.setOptionFontSize(8)
        self.__codeEditor.setOptionHighlightedLineColor(True)
        self.__codeEditor.setOptionShowRightLimit(True)
        self.__codeEditor.setOptionRightLimitPosition(80)
        self.__codeEditor.setOptionShowSpaces(True)

        self.__codeEditor.setMinimumHeight(650)

        layout = QVBoxLayout()
        layout.addWidget(self.__codeEditor)
        self.setLayout(layout)
        self.setMinimumWidth(800)

    def setFile(self, fileName):
        """When fileName is provided, update content preview"""
        if fileName == '' or not os.path.isfile(fileName):
            self.__codeEditor.clear()
            return False
        else:
            try:
                with open(fileName, 'r', encoding='utf-8') as fhandle:
                    content = fhandle.read()
                    self.__codeEditor.setPlainText(content)

                if fileExtension := re.search(r"(\.[^\.]*)$", fileName):
                    if self.__uiController:
                        languageDef = self.__uiController.languageDef(fileExtension.groups()[0])
                        self.__codeEditor.setLanguageDefinition(languageDef)

            except Exception as e:
                Debug.print("Unable to read file content:", fileName, e)
                self.__codeEditor.setPlainText(i18n("Can't read file!"))
                return False

            return True


class BPWOpenSave:
    """Provide methods to open/save files"""

    @staticmethod
    def openFiles(caption, directory, filter, uiController):
        return WDialogFile.openFiles(caption,
                                     directory,
                                     filter,
                                     options={WDialogFile.OPTION_PREVIEW_WIDTH: 650,
                                              WDialogFile.OPTION_PREVIEW_WIDGET: WBuliPyOpenSavePreview(uiController)})

    @staticmethod
    def saveFile(caption, directory, filter, uiController):
        return WDialogFile.saveFile(caption,
                                    directory,
                                    filter,
                                    options={WDialogFile.OPTION_PREVIEW_WIDTH: 650,
                                             WDialogFile.OPTION_PREVIEW_WIDGET: WBuliPyOpenSavePreview(uiController)})

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

from enum import Enum


import PyQt5.uic
from PyQt5.Qt import *
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtCore import (
        pyqtSignal,
        QSettings,
        QStandardPaths
    )

import os
import json
import re
import sys
import shutil

from .bpthemes import BPThemes

from ..pktk.modules.imgutils import buildIcon
from ..pktk.modules.utils import (
        checkKritaVersion,
        Debug
    )
from ..pktk.modules.uitheme import UITheme
from ..pktk.modules.settings import (
                        Settings,
                        SettingsFmt,
                        SettingsKey,
                        SettingsRule
                    )

from ..pktk.widgets.worderedlist import OrderedItem
from ..pktk.widgets.wcodeeditor import (
        WCodeEditor,
        WCodeEditorTheme
    )
from ..pktk.widgets.wtabbar import WTabBar
from ..pktk.widgets.wiodialog import WDialogFile
from ..pktk.pktk import *

# -----------------------------------------------------------------------------


class BPSettingsKey(SettingsKey):

    # -- from settings dialogbox

    CONFIG_SESSION_DOCUMENTS_RECENTS_COUNT =                          'config.session.documents.recents.count'

    CONFIG_DOCUMENT_DEFAULTTYPE =                                     'config.documents.default.type'
    CONFIG_DOCUMENT_PY_TRIMONSAVE =                                   'config.documents.type.python.trimOnSave'

    CONFIG_EDITOR_FONT_NAME =                                         'config.editor.appearance.font.name'
    CONFIG_EDITOR_THEME_SELECTED =                                    'config.editor.appearance.theme.selected'
    CONFIG_EDITOR_INDENT_WIDTH =                                      'config.editor.editing.indent.width'
    CONFIG_EDITOR_RIGHTLIMIT_WIDTH =                                  'config.editor.editing.rightLimit.width'
    CONFIG_EDITOR_ENCLOSINGCHARS =                                    'config.editor.editing.enclosingCharacters'
    CONFIG_EDITOR_AUTOCLOSE =                                         'config.editor.editing.autoclose'

    CONFIG_TOOLS_DOCKERS_ICONSELECTOR_MODE =                          'config.tools.dockers.iconSelector.mode'

    CONFIG_SCRIPTEXECUTION_SYSPATH_PATHS =                            'config.scriptExecution.syspath.paths'
    CONFIG_SCRIPTEXECUTION_SYSPATH_SCRIPT =                           'config.scriptExecution.syspath.script'

    CONFIG_TOOLS_DOCKERS_CONSOLE_BUFFERSIZE =                         'config.tools.dockers.console.bufferSize'

    CONFIG_TOOLBARS =                                                 'config.toolbars'

    # -- session

    SESSION_TOOLBARS =                                                'session.toolbars'

    SESSION_EDITOR_WRAPLINES_ACTIVE =                                 'session.editor.wrapLines.active'
    SESSION_EDITOR_INDENT_VISIBLE =                                   'session.editor.indent.visible'
    SESSION_EDITOR_SPACES_VISIBLE =                                   'session.editor.spaces.visible'
    SESSION_EDITOR_RIGHTLIMIT_VISIBLE =                               'session.editor.rightLimit.visible'
    SESSION_EDITOR_LINE_NUMBER_VISIBLE =                              'session.editor.lineNumber.visible'
    SESSION_EDITOR_HIGHTLIGHT_FCTCLASSDECL_ACTIVE =                   'session.editor.highlightClassFctDecl.active'
    SESSION_EDITOR_FONT_SIZE =                                        'session.editor.font.size'

    SESSION_MAINWINDOW_WINDOW_GEOMETRY =                              'session.mainwindow.window.geometry'
    SESSION_MAINWINDOW_WINDOW_MAXIMIZED =                             'session.mainwindow.window.maximized'

    SESSION_MAINWINDOW_VIEW_DOCKERS_LAYOUT =                          'session.mainwindow.view.dockers.layout'

    SESSION_DOCUMENTS_ACTIVE =                                        'session.documents.active'
    SESSION_DOCUMENTS_OPENED =                                        'session.documents.opened'
    SESSION_DOCUMENTS_RECENTS =                                       'session.documents.recents'

    # keep in memory last path used in open/save dialog box
    SESSION_PATH_LASTOPENED =                                         'session.paths.last.opened'
    SESSION_PATH_LASTSAVED =                                          'session.paths.last.saved'

    # docker "console output"; keep in memory filter/search options
    SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_VISIBLE =                'session.tools.dockers.console.search.buttons.visible'
    SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_REGEX_CHECKED =          'session.tools.dockers.console.search.buttons.regex.checked'
    SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_CASESENSITIVE_CHECKED =  'session.tools.dockers.console.search.buttons.caseSensitive.checked'
    SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_WHOLEWORD_CHECKED =      'session.tools.dockers.console.search.buttons.wholeWord.checked'
    SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_BACKWARD_CHECKED =       'session.tools.dockers.console.search.buttons.backward.checked'
    SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_HIGHLIGHTALL_CHECKED =   'session.tools.dockers.console.search.buttons.highlightAll.checked'
    SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_TEXT =                       'session.tools.dockers.console.search.text'
    SESSION_TOOLS_DOCKERS_CONSOLE_OPTIONS_AUTOCLEAR =                 'session.tools.dockers.console.options.autoClear'
    SESSION_TOOLS_DOCKERS_CONSOLE_OPTIONS_FILTER_TYPES =              'session.tools.dockers.console.options.filter.types'
    SESSION_TOOLS_DOCKERS_CONSOLE_OPTIONS_FILTER_SEARCH =             'session.tools.dockers.console.options.filter.search'
    SESSION_TOOLS_DOCKERS_CONSOLE_OUTPUT_FONT_SIZE =                  'session.tools.dockers.console.output.fontSize'

    # docker "color picker"
    SESSION_TOOLS_DOCKERS_COLORPICKER_MENU_SELECTED =                 'session.tools.dockers.colorPicker.menu.selected'

    # docker "icon selector"
    SESSION_TOOLS_DOCKERS_ICONSELECTOR_ICONSIZE =                     'session.tools.dockers.iconSelector.iconSize'
    SESSION_TOOLS_DOCKERS_ICONSELECTOR_VIEWMODE =                     'session.tools.dockers.iconSelector.viewMode'

    # docker "search and replace"; keep in memory search options
    SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_REGEX_CHECKED =              'session.tools.dockers.searchAndReplace.search.buttons.regex.checked'
    SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_CASESENSITIVE_CHECKED =      'session.tools.dockers.searchAndReplace.search.buttons.caseSensitive.checked'
    SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_WHOLEWORD_CHECKED =          'session.tools.dockers.searchAndReplace.search.buttons.wholeWord.checked'
    SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_BACKWARD_CHECKED =           'session.tools.dockers.searchAndReplace.search.buttons.backward.checked'
    SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_HIGHLIGHTALL_CHECKED =       'session.tools.dockers.searchAndReplace.search.buttons.highlightAll.checked'
    SESSION_TOOLS_DOCKERS_SAR_SEARCH_TEXT =                           'session.tools.dockers.searchAndReplace.search.text'
    SESSION_TOOLS_DOCKERS_SAR_REPLACE_TEXT =                          'session.tools.dockers.searchAndReplace.replace.text'
    SESSION_TOOLS_DOCKERS_SAR_OUTPUT_FONT_SIZE =                      'session.tools.dockers.searchAndReplace.output.fontSize'

    # docker "documents"
    SESSION_TOOLS_DOCKERS_DOCUMENTS_SORT_COLUMN =                     'session.tools.dockers.documents.sort.column'
    SESSION_TOOLS_DOCKERS_DOCUMENTS_SORT_ORDER =                      'session.tools.dockers.documents.sort.order'

    # docker "clipboard"; keep in memory search options
    SESSION_TOOLS_DOCKERS_CLIPBRD_SEARCH_BTN_REGEX_CHECKED =          'session.tools.dockers.clipboard.search.buttons.regex.checked'
    SESSION_TOOLS_DOCKERS_CLIPBRD_SEARCH_BTN_CASESENSITIVE_CHECKED =  'session.tools.dockers.clipboard.search.buttons.caseSensitive.checked'
    SESSION_TOOLS_DOCKERS_CLIPBRD_SEARCH_BTN_WHOLEWORD_CHECKED =      'session.tools.dockers.clipboard.search.buttons.wholeWord.checked'
    SESSION_TOOLS_DOCKERS_CLIPBRD_SEARCH_TEXT =                       'session.tools.dockers.clipboard.search.text'
    SESSION_TOOLS_DOCKERS_CLIPBRD_OUTPUT_FONT_SIZE =                  'session.tools.dockers.clipboard.output.fontSize'
    SESSION_TOOLS_DOCKERS_CLIPBRD_SORT_COLUMN =                       'session.tools.dockers.clipboard.sort.column'
    SESSION_TOOLS_DOCKERS_CLIPBRD_SORT_ORDER =                        'session.tools.dockers.clipboard.sort.order'
    SESSION_TOOLS_DOCKERS_CLIPBRD_ACTIVE =                            'session.tools.dockers.clipboard.active'
    SESSION_TOOLS_DOCKERS_CLIPBRD_STARTUPCLEAR =                      'session.tools.dockers.clipboard.clear.startup'

    # docker "PyKritaApi"; keep in memory search options
    SESSION_TOOLS_DOCKERS_PYKRITAAPI_SEARCH_BTN_REGEX_CHECKED =          'session.tools.dockers.pyKritaApi.search.buttons.regex.checked'
    SESSION_TOOLS_DOCKERS_PYKRITAAPI_SEARCH_BTN_CASESENSITIVE_CHECKED =  'session.tools.dockers.pyKritaApi.search.buttons.caseSensitive.checked'
    SESSION_TOOLS_DOCKERS_PYKRITAAPI_SEARCH_TEXT =                       'session.tools.dockers.pyKritaApi.search.text'
    SESSION_TOOLS_DOCKERS_PYKRITAAPI_SPLITTER =                          'session.tools.dockers.pyKritaApi.splitter'


class BPSettings(Settings):
    """Manage all BuliPy settings with open&save options

    Configuration is saved as JSON file
    """
    def __init__(self, pluginId=None):
        """Initialise settings"""
        if pluginId is None or pluginId == '':
            pluginId = 'bulipy'

        # define current rules for options
        rules = [
            # values are tuples:
            # [0]       = default value
            # [1..n]    = values types & accepted values
            SettingsRule(BPSettingsKey.CONFIG_SESSION_DOCUMENTS_RECENTS_COUNT,                     25,                       SettingsFmt(int, (1, 100))),

            SettingsRule(BPSettingsKey.CONFIG_DOCUMENT_DEFAULTTYPE,                                ".py",                    SettingsFmt(str)),
            SettingsRule(BPSettingsKey.CONFIG_DOCUMENT_PY_TRIMONSAVE,                              True,                     SettingsFmt(bool)),

            SettingsRule(BPSettingsKey.CONFIG_EDITOR_FONT_NAME,                                    "DejaVu Sans Mono",       SettingsFmt(str)),
            SettingsRule(BPSettingsKey.CONFIG_EDITOR_THEME_SELECTED,                               "",                       SettingsFmt(str)),

            SettingsRule(BPSettingsKey.CONFIG_EDITOR_INDENT_WIDTH,                                 4,                        SettingsFmt(int, (1, 8))),
            SettingsRule(BPSettingsKey.CONFIG_EDITOR_RIGHTLIMIT_WIDTH,                             120,                      SettingsFmt(int, (40, 240))),
            SettingsRule(BPSettingsKey.CONFIG_EDITOR_ENCLOSINGCHARS,                               "() {} [] '' \"\" ``",    SettingsFmt(str)),
            SettingsRule(BPSettingsKey.CONFIG_EDITOR_AUTOCLOSE,                                    True,                     SettingsFmt(bool)),

            SettingsRule(BPSettingsKey.CONFIG_TOOLS_DOCKERS_ICONSELECTOR_MODE,                     0,                        SettingsFmt(int, [0, 1])),

            SettingsRule(BPSettingsKey.CONFIG_SCRIPTEXECUTION_SYSPATH_PATHS,                       [],                       SettingsFmt(list)),
            SettingsRule(BPSettingsKey.CONFIG_SCRIPTEXECUTION_SYSPATH_SCRIPT,                      True,                     SettingsFmt(bool)),

            SettingsRule(BPSettingsKey.CONFIG_TOOLS_DOCKERS_CONSOLE_BUFFERSIZE,                    0,                        SettingsFmt(int)),

            SettingsRule(BPSettingsKey.SESSION_EDITOR_FONT_SIZE,                                   9,                        SettingsFmt(int, (5, 96))),
            SettingsRule(BPSettingsKey.SESSION_EDITOR_INDENT_VISIBLE,                              True,                     SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_EDITOR_SPACES_VISIBLE,                              True,                     SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_EDITOR_RIGHTLIMIT_VISIBLE,                          True,                     SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_EDITOR_LINE_NUMBER_VISIBLE,                         True,                     SettingsFmt(bool)),

            SettingsRule(BPSettingsKey.SESSION_EDITOR_HIGHTLIGHT_FCTCLASSDECL_ACTIVE,              True,                     SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_EDITOR_WRAPLINES_ACTIVE,                            True,                     SettingsFmt(bool)),

            SettingsRule(BPSettingsKey.SESSION_MAINWINDOW_WINDOW_GEOMETRY,                         [-1, -1, -1, -1],         SettingsFmt(int), SettingsFmt(int), SettingsFmt(int), SettingsFmt(int)),
            SettingsRule(BPSettingsKey.SESSION_MAINWINDOW_WINDOW_MAXIMIZED,                        False,                    SettingsFmt(bool)),

            # dockers layout use QMainWindow.saveState()/QMainWindow.restoreState()
            # Don't really like this solution as methods return binary data through a byte array rather than a human readable structure
            # but there's not really other choice to be able to save/restore dockers state (available methods doesn't allows to save/restore
            # all layout properties...)
            # byte array is base64 encoded in configuration file
            SettingsRule(BPSettingsKey.SESSION_MAINWINDOW_VIEW_DOCKERS_LAYOUT,                     '',                       SettingsFmt(str)),

            SettingsRule(BPSettingsKey.SESSION_DOCUMENTS_ACTIVE,                                   "",                       SettingsFmt(str)),
            SettingsRule(BPSettingsKey.SESSION_DOCUMENTS_OPENED,                                   [],                       SettingsFmt(list)),
            SettingsRule(BPSettingsKey.SESSION_DOCUMENTS_RECENTS,                                  [],                       SettingsFmt(list)),

            SettingsRule(BPSettingsKey.SESSION_PATH_LASTOPENED,                                    "",                       SettingsFmt(str)),
            SettingsRule(BPSettingsKey.SESSION_PATH_LASTSAVED,                                     "",                       SettingsFmt(str)),

            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_VISIBLE,           True,                     SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_REGEX_CHECKED,     False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_CASESENSITIVE_CHECKED, False,                SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_WHOLEWORD_CHECKED, False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_BACKWARD_CHECKED,  False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_BTN_HIGHLIGHTALL_CHECKED, False,                 SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_SEARCH_TEXT,                  '',                       SettingsFmt(str)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_OPTIONS_AUTOCLEAR,            True,                     SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_OPTIONS_FILTER_SEARCH,        False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_OPTIONS_FILTER_TYPES,         ['error', 'warning', 'info', 'valid'],
                                                                                                                             SettingsFmt(list, ['error', 'warning', 'info', 'valid'])),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CONSOLE_OUTPUT_FONT_SIZE,             12,                       SettingsFmt(int)),

            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_COLORPICKER_MENU_SELECTED,            ['colorRGB', 'colorHSV', 'colorAlpha', 'colorCssRGB', 'colorCssRGBAlphaChecked', 'colorWheel', 'colorPreview'],
                                                                                                                             SettingsFmt(list)),  # list is not fixed as palette names are not known

            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_ICONSELECTOR_ICONSIZE,                3,                        SettingsFmt(int, [0, 1, 2, 3, 4, 5, 6])),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_ICONSELECTOR_VIEWMODE,                QListView.ListMode,       SettingsFmt(int, [QListView.ListMode, QListView.IconMode])),

            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_REGEX_CHECKED,         False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_CASESENSITIVE_CHECKED, False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_WHOLEWORD_CHECKED,     False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_BACKWARD_CHECKED,      False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_BTN_HIGHLIGHTALL_CHECKED,  False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_SEARCH_TEXT,                      '',                       SettingsFmt(str)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_REPLACE_TEXT,                     '',                       SettingsFmt(str)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_SAR_OUTPUT_FONT_SIZE,                 12,                       SettingsFmt(int)),

            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_DOCUMENTS_SORT_COLUMN,                0,                        SettingsFmt(int, [0, 1, 2, 3])),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_DOCUMENTS_SORT_ORDER,                 Qt.AscendingOrder,        SettingsFmt(int, [Qt.AscendingOrder, Qt.DescendingOrder])),

            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CLIPBRD_SEARCH_BTN_REGEX_CHECKED,         False,                SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CLIPBRD_SEARCH_BTN_CASESENSITIVE_CHECKED, False,                SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CLIPBRD_SEARCH_BTN_WHOLEWORD_CHECKED,     False,                SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CLIPBRD_SEARCH_TEXT,                      '',                   SettingsFmt(str)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CLIPBRD_OUTPUT_FONT_SIZE,                 12,                   SettingsFmt(int)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CLIPBRD_SORT_COLUMN,                      0,                    SettingsFmt(int, [0, 1])),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CLIPBRD_SORT_ORDER,                       Qt.AscendingOrder,    SettingsFmt(int, [Qt.AscendingOrder, Qt.DescendingOrder])),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CLIPBRD_ACTIVE,                           True,                 SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_CLIPBRD_STARTUPCLEAR,                     False,                SettingsFmt(bool)),

            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_PYKRITAAPI_SEARCH_BTN_REGEX_CHECKED,         False,             SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_PYKRITAAPI_SEARCH_BTN_CASESENSITIVE_CHECKED, False,             SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_PYKRITAAPI_SEARCH_TEXT,                      '',                SettingsFmt(str)),
            SettingsRule(BPSettingsKey.SESSION_TOOLS_DOCKERS_PYKRITAAPI_SPLITTER,                         [1000, 1000],      SettingsFmt(list)),

            SettingsRule(BPSettingsKey.CONFIG_TOOLBARS,                                            [],                       SettingsFmt(list, dict)),
            SettingsRule(BPSettingsKey.SESSION_TOOLBARS,                                           [],                       SettingsFmt(list, dict))
        ]

        super(BPSettings, self).__init__(pluginId, rules)


class BPSettingsDialogBox(QDialog):
    """User interface fo settings"""

    CATEGORY_DOCUMENTS = 0
    CATEGORY_EDITOR = 1
    CATEGORY_SCRIPTEXEC = 2
    CATEGORY_TOOLBAR_CONFIG = 3
    CATEGORY_CACHE = 3

    __CODE_EXAMPLE = {'.py': '''# Python file example to check font & theme selection
# {0}
# {1}

import krita

class HelloWorld(object):
    """A really simple class

    You can copy/paste content to test it!
    """
    @staticmethod
    def hello(name):
        """Just print hello to standard output"""
        print(f"Hello {name}!")

    def __init__(self):
        self.__version = b'\\x01\\x01'
        self.__name = None

    def setName(self, name):
        """Set user name"""
        if isinstance(name, str) or name is None:
            self.__name = name

    def helloWorld(self, repeat=0):
        """Print hello to standard output"""
        for index in range(repeat + 1):
            print('Hello world!')

        if self.__name is None:
            print(f'How are you?')
        else:
            print(f'How are you {self.__name}?')


hw = HelloWorld()
hw.setName('Buli')
hw.helloWorld(2)''',
                      '.xml': '''<?xml version="1.0" encoding = "UTF-8" standalone = "yes" ?>
<!DOCTYPE test>
<!-- XML file example to check font & theme selection
     {0}
     {1}
-->
<root>
    <node index='0'>
        <type value="test"/>
        <content>This is a normal content with some special characters like: &apos;&lt;&apos; and &quot;&gt;&quot;</content>
    </node>
    <node index='1'>
        <type value="test"/>
        <content><![CDATA[
            This is a content & an example with some specific '<' and ">" characters &amp;
            This is a normal content with some special characters like: '<' and ">"
        ]]>
        </content>
</root>''',
                      '.json': '''{
    "comment": [
        "JSON file example to check font & theme selection",
        "{0}",
        "{1}"
    ],
    "items": [
        "string": "A string",
        "special values": [null, true, false],
        "numbers":  {
            "examples 1": [12, 34.56, -7, -8.99],
            "examples 2": [12e-1, 34.56e+2, -7e1, -8.99e2]
        }
    ]
}''',
                      '.txt': '''Text file example to check font & theme selection
{0}
{1}






Vote Buli!'''}

    def __init__(self, title, uicontroller, parent=None):
        super(BPSettingsDialogBox, self).__init__(parent)

        self.__title = title

        uiFileName = os.path.join(os.path.dirname(__file__), 'resources', 'bpsettings.ui')
        PyQt5.uic.loadUi(uiFileName, self)

        self.setWindowTitle(self.__title)
        self.lwPages.itemSelectionChanged.connect(self.__categoryChanged)

        self.__itemCatDocuments = QListWidgetItem(buildIcon("pktk:file_copy"), i18n("Documents"))
        self.__itemCatDocuments.setData(Qt.UserRole, BPSettingsDialogBox.CATEGORY_DOCUMENTS)
        self.__itemCatEditor = QListWidgetItem(buildIcon("pktk:process_edit"), i18n("Editor"))
        self.__itemCatEditor.setData(Qt.UserRole, BPSettingsDialogBox.CATEGORY_EDITOR)
        self.__itemCatScriptExecution = QListWidgetItem(buildIcon("pktk:process_output_info"), i18n("Script execution"))
        self.__itemCatScriptExecution.setData(Qt.UserRole, BPSettingsDialogBox.CATEGORY_SCRIPTEXEC)
        self.__itemCatToolbarConfiguration = QListWidgetItem(buildIcon("pktk:tune_toolbar"), i18n("Toolbars"))
        self.__itemCatToolbarConfiguration.setData(Qt.UserRole, BPSettingsDialogBox.CATEGORY_TOOLBAR_CONFIG)

        self.__uiController = uicontroller

        self.__tabBar = WTabBar(self, self.twEditorSetup.tabBar())
        self.__tabBar.setStyleSheet(self.__tabBar.styleSheet() + """
            WTabBar::tab:selected {
                background: palette(Light);
            }
        """)

        self.twEditorSetup.setTabBar(self.__tabBar)
        self.twEditorSetup.setStyleSheet("""
            QTabWidget>* {
                padding: 0;
                margin: -2px;
                border: 0px none;
                background: palette(Window);

            }
            QTabWidget::pane {
                padding: 0px;
                margin: 0px;
                border: 0px none;
                background: palette(Window);
            }
        """)

        self.bbOkCancel.accepted.connect(self.__applySettings)

        self.__initialise()

    def __initialise(self):
        """Initialise interface"""
        self.lwPages.addItem(self.__itemCatDocuments)
        self.lwPages.addItem(self.__itemCatEditor)
        self.lwPages.addItem(self.__itemCatScriptExecution)
        self.lwPages.addItem(self.__itemCatToolbarConfiguration)
        self.__setCategory(BPSettingsDialogBox.CATEGORY_DOCUMENTS)

        # --- DOCUMENTS category -----------------------------------------------------
        self.cbCDocNewDocumentType.clear()
        self.cbCDocNewDocumentType.addItem(i18n("Python document"), '.py')
        self.cbCDocNewDocumentType.addItem(i18n("Text document"), '.txt')

        # -- values from config file
        defaultDocType = BPSettings.get(BPSettingsKey.CONFIG_DOCUMENT_DEFAULTTYPE)
        for index in range(self.cbCDocNewDocumentType.count()):
            if self.cbCDocNewDocumentType.itemData(index) == defaultDocType:
                self.cbCDocNewDocumentType.setCurrentIndex(index)
                break

        self.cbCDocPythonTrimOnSave.setChecked(BPSettings.get(BPSettingsKey.CONFIG_DOCUMENT_PY_TRIMONSAVE))

        # --- EDITOR Category -----------------------------------------------------
        self.__database = QFontDatabase()

        self.cbCEAppearanceFontName.clear()
        for family in self.__database.families(QFontDatabase.Latin):
            if self.__database.isFixedPitch(family):
                self.cbCEAppearanceFontName.addItem(family)

        self.cbCEAppearanceFontName.currentIndexChanged.connect(self.__updateCEAppearanceFontNameChanged)
        self.sbCEAppearanceFontSize.valueChanged.connect(self.__updateCEAppearanceFontSizeChanged)

        self.ceCEAppearancePreview.setOptionMultiLine(True)
        self.ceCEAppearancePreview.setOptionCommentCharacter('#')
        self.ceCEAppearancePreview.setOptionShowLineNumber(True)
        self.ceCEAppearancePreview.setOptionShowIndentLevel(True)
        self.ceCEAppearancePreview.setOptionShowRightLimit(True)
        self.ceCEAppearancePreview.setOptionShowSpaces(True)
        self.ceCEAppearancePreview.setOptionAutoCompletion(False)
        self.ceCEAppearancePreview.setOptionAutoCompletionHelp(False)
        self.ceCEAppearancePreview.setOptionAllowWheelSetFontSize(True)
        self.ceCEAppearancePreview.setLanguageDefinition(self.__uiController.languageDef('.py'))
        # a default source code in preview
        self.cbFileExample.clear()
        self.cbFileExample.addItem("Python", '.py')
        self.cbFileExample.addItem("XML", '.xml')
        self.cbFileExample.addItem("JSON", '.json')
        self.cbFileExample.addItem("Text", '.txt')
        self.cbFileExample.setCurrentIndex(0)
        self.cbFileExample.currentIndexChanged.connect(self.__updateCEFileExampleChanged)

        # load themes
        self.cbCEAppearanceTheme.clear()
        for theme in BPThemes.themes(True):
            # 0: id
            # 1: name
            self.cbCEAppearanceTheme.addItem(theme[1], theme[0])
            self.ceCEAppearancePreview.addTheme(BPThemes.theme(theme[0]))

        self.cbCEAppearanceTheme.currentIndexChanged.connect(self.__updateCEAppearanceTheme)

        self.ceCEAppearancePreview.fontSizeChanged.connect(self.__updateCEAppearancePreviewFontSizeChanged)

        self.leCEEditingEnclosingCharacters.textChanged.connect(self.__enclosingCharactersChanged)

        # -- values from config file
        fontName = BPSettings.get(BPSettingsKey.CONFIG_EDITOR_FONT_NAME)
        for index in range(self.cbCEAppearanceFontName.count()):
            if self.cbCEAppearanceFontName.itemText(index) == fontName:
                self.cbCEAppearanceFontName.setCurrentIndex(index)
                break

        self.__updateCEFileExampleChanged(0)

        self.sbCEAppearanceFontSize.setValue(BPSettings.get(BPSettingsKey.SESSION_EDITOR_FONT_SIZE))

        selectedTheme = BPSettings.get(BPSettingsKey.CONFIG_EDITOR_THEME_SELECTED)
        for index in range(self.cbCEAppearanceTheme.count()):
            if self.cbCEAppearanceTheme.itemData(index) == selectedTheme:
                self.cbCEAppearanceTheme.setCurrentIndex(index)
                break

        self.sbCEEditingRightLimit.setValue(BPSettings.get(BPSettingsKey.CONFIG_EDITOR_RIGHTLIMIT_WIDTH))
        self.sbCEEditingIndentSize.setValue(BPSettings.get(BPSettingsKey.CONFIG_EDITOR_INDENT_WIDTH))

        self.leCEEditingEnclosingCharacters.setText(BPSettings.get(BPSettingsKey.CONFIG_EDITOR_ENCLOSINGCHARS))

        self.cbCEEditingAutoClose.setChecked(BPSettings.get(BPSettingsKey.CONFIG_EDITOR_AUTOCLOSE))

        # --- SCRIPT EXECUTION Category -----------------------------------------------------
        self.lwCSEAutomaticallyAddedSysPath.setSortOptionAvailable(False)
        self.lwCSEAutomaticallyAddedSysPath.setCheckOptionAvailable(True)
        self.lwCSEAutomaticallyAddedSysPath.setReorderOptionAvailable(True)

        for item in BPSettings.get(BPSettingsKey.CONFIG_SCRIPTEXECUTION_SYSPATH_PATHS):
            # label = value
            path = os.path.abspath(os.path.expanduser(item[0]))
            if not os.path.isdir(path):
                # path doesn't exist? force to uncheck it
                item[1] = False
            self.lwCSEAutomaticallyAddedSysPath.addItem(item[0], item[0], item[1])

        self.cbCSEAutomaticallyAddedScriptPath.setChecked(BPSettings.get(BPSettingsKey.CONFIG_SCRIPTEXECUTION_SYSPATH_SCRIPT))

        self.tbCSEAutomaticallyAddedAddPath.clicked.connect(self.__automaticallyAddedScriptAddPath)
        self.tbCSEAutomaticallyAddedRemovePath.clicked.connect(self.__automaticallyAddedScriptRemovePath)
        self.lwCSEAutomaticallyAddedSysPath.itemSelectionChanged.connect(self.__automaticallyAddedScriptSelectionChanged)
        self.tbCSEAutomaticallyAddedRemovePath.setEnabled(False)

        # --- TOOLBAR CONFIGURATION categeory ----------------------------------------------
        self.wToolbarConfiguration.beginAvailableActionUpdate()
        self.wToolbarConfiguration.addAvailableActionSeparator()
        self.wToolbarConfiguration.initialiseAvailableActionsFromMenubar(self.__uiController.window().menuBar())
        self.wToolbarConfiguration.endAvailableActionUpdate()
        self.wToolbarConfiguration.availableActionsExpandAll()
        self.wToolbarConfiguration.toolbarsImport(BPSettings.get(BPSettingsKey.CONFIG_TOOLBARS))

    def __applySettings(self):
        """Apply current settings"""

        # --- DOCUMENTS category -----------------------------------------------------
        BPSettings.set(BPSettingsKey.CONFIG_DOCUMENT_DEFAULTTYPE, self.cbCDocNewDocumentType.currentData())
        BPSettings.set(BPSettingsKey.CONFIG_DOCUMENT_PY_TRIMONSAVE, self.cbCDocPythonTrimOnSave.isChecked())

        # --- EDITOR Category --------------------------------------------------------
        BPSettings.set(BPSettingsKey.SESSION_EDITOR_FONT_SIZE, self.sbCEAppearanceFontSize.value())
        BPSettings.set(BPSettingsKey.CONFIG_EDITOR_FONT_NAME, self.cbCEAppearanceFontName.currentText())
        BPSettings.set(BPSettingsKey.CONFIG_EDITOR_THEME_SELECTED, self.cbCEAppearanceTheme.currentData())

        BPSettings.set(BPSettingsKey.CONFIG_EDITOR_RIGHTLIMIT_WIDTH, self.sbCEEditingRightLimit.value())
        BPSettings.set(BPSettingsKey.CONFIG_EDITOR_INDENT_WIDTH, self.sbCEEditingIndentSize.value())
        BPSettings.set(BPSettingsKey.CONFIG_EDITOR_ENCLOSINGCHARS, self.leCEEditingEnclosingCharacters.text())
        BPSettings.set(BPSettingsKey.CONFIG_EDITOR_AUTOCLOSE, self.cbCEEditingAutoClose.isChecked())

        # --- SCRIPT EXECUTION Category -----------------------------------------------------
        BPSettings.set(BPSettingsKey.CONFIG_SCRIPTEXECUTION_SYSPATH_PATHS, [(item.value(), item.checked()) for item in self.lwCSEAutomaticallyAddedSysPath.items(False)])
        BPSettings.set(BPSettingsKey.CONFIG_SCRIPTEXECUTION_SYSPATH_SCRIPT, self.cbCSEAutomaticallyAddedScriptPath.isChecked())

        # --- TOOLBAR CONFIGURATION categeory ----------------------------------------------
        self.__uiController.commandSettingsToolbars(self.wToolbarConfiguration.toolbarsExport(), None)

    def __categoryChanged(self):
        """Set page according to category"""
        self.swCatPages.setCurrentIndex(self.lwPages.currentItem().data(Qt.UserRole))

    def __setCategory(self, value):
        """Set category setting

        Select icon, switch to panel
        """
        self.lwPages.setCurrentRow(value)

    def __updateTextExample(self):
        """Update texte example accordoing to selected them & file example"""
        themeComments = BPThemes.theme(self.cbCEAppearanceTheme.currentData()).comments()
        text = BPSettingsDialogBox.__CODE_EXAMPLE[self.cbFileExample.currentData()]
        text = text.replace('{0}', themeComments[0]).replace('{1}', themeComments[1])
        self.ceCEAppearancePreview.setPlainText(text)

    def __updateCEAppearanceFontNameChanged(self, index):
        """A font has been selected, update editor preview"""
        font = self.ceCEAppearancePreview.optionFont()
        font.setFamily(self.cbCEAppearanceFontName.itemText(index))
        self.ceCEAppearancePreview.setOptionFont(font)

    def __updateCEFileExampleChanged(self, index):
        """File type example modified"""
        self.ceCEAppearancePreview.setLanguageDefinition(BPThemes.languageDef(self.cbFileExample.currentData()))
        self.ceCEAppearancePreview.setCurrentTheme(self.cbCEAppearanceTheme.currentData())
        self.__updateTextExample()

    def __updateCEAppearancePreviewFontSizeChanged(self, value):
        """Font size has been modified from editor preview, update spinbox"""
        self.sbCEAppearanceFontSize.setValue(value)

    def __updateCEAppearanceFontSizeChanged(self, value):
        """Font size has been modified from spinbox, update editor preview"""
        self.ceCEAppearancePreview.setOptionFontSize(value)

    def __updateCEAppearanceTheme(self, value):
        """Theme has been changed"""
        # update code editor theme
        self.ceCEAppearancePreview.setCurrentTheme(self.cbCEAppearanceTheme.currentData())
        self.__updateTextExample()

    def __enclosingCharactersChanged(self, text):
        """Enclosing characters definition has been modified; check if valid"""
        cursorPosition = self.leCEEditingEnclosingCharacters.cursorPosition()

        btOk = self.bbOkCancel.button(QDialogButtonBox.Ok)
        strippedText = re.sub(r'\s+', '', text)
        if len(strippedText) % 2 != 0:
            # need tuples -> even number of characters)
            btOk.setEnabled(False)
            self.leCEEditingEnclosingCharacters.setToolTip(i18n("Invalid enclosing characters definition"))
            self.leCEEditingEnclosingCharacters.setStyleSheet(UITheme.style('error-bg'))
            return
        else:
            btOk.setEnabled(True)
            self.leCEEditingEnclosingCharacters.setToolTip(f"<html><head/><body><p>{i18n('When typed, selected text will be enclosed by defined characters tuple')}</p></body></html>")
            self.leCEEditingEnclosingCharacters.setStyleSheet('')

        # reformat: separate tuples with a space
        formattedText = ' '.join(re.findall('..', strippedText))
        self.leCEEditingEnclosingCharacters.setText(formattedText)

        newCursorPosition = len(' '.join(re.findall('..', re.sub(r'\s+', '', text[0:cursorPosition + 1]))))
        self.leCEEditingEnclosingCharacters.setCursorPosition(newCursorPosition)

    def __automaticallyAddedScriptAddPath(self, value):
        """Add a path to list"""
        currentPath = os.path.dirname(__file__)
        selectedItem = self.lwCSEAutomaticallyAddedSysPath.currentItem()
        if selectedItem:
            currentPath = selectedItem.value()

        selectedPath = WDialogFile.openDirectory(i18n("Add path to Python sys.path"), currentPath)
        if selectedPath:
            normPath = os.path.abspath(os.path.expanduser(selectedPath['directory']))
            for item in self.lwCSEAutomaticallyAddedSysPath.items(False):
                if os.path.abspath(os.path.expanduser(item.value())) == normPath:
                    # path already in list, cancel
                    return
            self.lwCSEAutomaticallyAddedSysPath.addItem(selectedPath['directory'], selectedPath['directory'])

    def __automaticallyAddedScriptRemovePath(self, value):
        """Remove selected path from list"""
        items = self.lwCSEAutomaticallyAddedSysPath.selectedItems()
        for item in items:
            self.lwCSEAutomaticallyAddedSysPath.takeItem(self.lwCSEAutomaticallyAddedSysPath.row(item))

    def __automaticallyAddedScriptSelectionChanged(self):
        """Selected items changed in list, update buttons"""
        self.tbCSEAutomaticallyAddedRemovePath.setEnabled(len(self.lwCSEAutomaticallyAddedSysPath.selectedItems()) > 0)

    @staticmethod
    def open(title, uicontroller):
        """Open dialog box"""
        db = BPSettingsDialogBox(title, uicontroller)
        return db.exec()

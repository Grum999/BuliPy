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
from PyQt5.QtCore import (
        pyqtSignal,
        QSettings,
        QStandardPaths
    )

from os.path import (join, getsize)
import json
import re
import sys
import shutil

from ..pktk.modules.utils import (
        checkKritaVersion,
        Debug
    )
from ..pktk.modules.settings import (
                        Settings,
                        SettingsFmt,
                        SettingsKey,
                        SettingsRule
                    )
from ..pktk.pktk import *

# -----------------------------------------------------------------------------


class BPSettingsKey(SettingsKey):

    # -- from settings dialogbox

    CONFIG_OPEN_ATSTARTUP =                                  'config.open.atStartup'

    CONFIG_SESSION_DOCUMENTS_RECENTS_COUNT =                 'config.session.documents.recents.count'

    CONFIG_EDITOR_FONT_NAME =                                'config.editor.font.name'
    CONFIG_EDITOR_INDENT_WIDTH =                             'config.editor.indent.width'
    CONFIG_EDITOR_SPACES_COLOR =                             'config.editor.spaces.color'
    CONFIG_EDITOR_RIGHTLIMIT_WIDTH =                         'config.editor.rightLimit.width'

    CONFIG_DOCKER_CONSOLE_BUFFERSIZE =                       'session.docker.console.bufferSize'

    # -- session

    SESSION_EDITOR_WRAPLINES_ACTIVE =                        'session.editor.wrapLines.active'
    SESSION_EDITOR_INDENT_VISIBLE =                          'session.editor.indent.visible'
    SESSION_EDITOR_SPACES_VISIBLE =                          'session.editor.spaces.visible'
    SESSION_EDITOR_RIGHTLIMIT_VISIBLE =                      'session.editor.rightLimit.visible'
    SESSION_EDITOR_LINE_NUMBER_VISIBLE =                     'session.editor.lineNumber.visible'
    SESSION_EDITOR_HIGHTLIGHT_FCTCLASSDECL_ACTIVE =          'session.editor.highlightClassFctDecl.active'
    SESSION_EDITOR_FONT_SIZE =                               'session.editor.font.size'

    SESSION_MAINWINDOW_WINDOW_GEOMETRY =                     'session.mainwindow.window.geometry'
    SESSION_MAINWINDOW_WINDOW_MAXIMIZED =                    'session.mainwindow.window.maximized'

    SESSION_MAINWINDOW_VIEW_DOCKERS_LAYOUT =                 'session.mainwindow.view.dockers.layout'

    SESSION_DOCUMENTS_ACTIVE =                               'session.documents.active'
    SESSION_DOCUMENTS_OPENED =                               'session.documents.opened'
    SESSION_DOCUMENTS_RECENTS =                              'session.documents.recents'

    # keep in memory last path used in open/save dialog box
    SESSION_PATH_LASTOPENED =                                'session.paths.last.opened'
    SESSION_PATH_LASTSAVED =                                 'session.paths.last.saved'

    # docker "console output"; keep in memory filter/search options
    SESSION_DOCKER_CONSOLE_SEARCH_BTN_VISIBLE =                 'session.dockers.console.search.buttons.visible'
    SESSION_DOCKER_CONSOLE_SEARCH_BTN_REGEX_CHECKED =           'session.dockers.console.search.buttons.regex.checked'
    SESSION_DOCKER_CONSOLE_SEARCH_BTN_CASESENSITIVE_CHECKED =   'session.dockers.console.search.buttons.caseSensitive.checked'
    SESSION_DOCKER_CONSOLE_SEARCH_BTN_WHOLEWORD_CHECKED =       'session.dockers.console.search.buttons.wholeWord.checked'
    SESSION_DOCKER_CONSOLE_SEARCH_BTN_BACKWARD_CHECKED =        'session.dockers.console.search.buttons.backward.checked'
    SESSION_DOCKER_CONSOLE_SEARCH_BTN_HIGHLIGHTALL_CHECKED =    'session.dockers.console.search.buttons.highlightAll.checked'
    SESSION_DOCKER_CONSOLE_SEARCH_TEXT =                        'session.dockers.console.search.text'
    SESSION_DOCKER_CONSOLE_OPTIONS_AUTOCLEAR =                  'session.dockers.console.options.autoClear'
    SESSION_DOCKER_CONSOLE_OPTIONS_FILTER_TYPES =               'session.dockers.console.options.filter.types'
    SESSION_DOCKER_CONSOLE_OPTIONS_FILTER_SEARCH =              'session.dockers.console.options.filter.search'
    SESSION_DOCKER_CONSOLE_OUTPUT_FONT_SIZE =                   'session.dockers.console.output.fontSize'

    # docker "color picker"
    SESSION_DOCKER_COLORPICKER_MENU_SELECTED =                  'session.dockers.colorPicker.menu.selected'

    # docker "search and replace"; keep in memory search options
    SESSION_DOCKER_SAR_SEARCH_BTN_REGEX_CHECKED =               'session.dockers.searchAndReplace.search.buttons.regex.checked'
    SESSION_DOCKER_SAR_SEARCH_BTN_CASESENSITIVE_CHECKED =       'session.dockers.searchAndReplace.search.buttons.caseSensitive.checked'
    SESSION_DOCKER_SAR_SEARCH_BTN_WHOLEWORD_CHECKED =           'session.dockers.searchAndReplace.search.buttons.wholeWord.checked'
    SESSION_DOCKER_SAR_SEARCH_BTN_BACKWARD_CHECKED =            'session.dockers.searchAndReplace.search.buttons.backward.checked'
    SESSION_DOCKER_SAR_SEARCH_BTN_HIGHLIGHTALL_CHECKED =        'session.dockers.searchAndReplace.search.buttons.highlightAll.checked'
    SESSION_DOCKER_SAR_SEARCH_TEXT =                            'session.dockers.searchAndReplace.search.text'
    SESSION_DOCKER_SAR_REPLACE_TEXT =                           'session.dockers.searchAndReplace.replace.text'
    SESSION_DOCKER_SAR_OUTPUT_FONT_SIZE =                       'session.dockers.searchAndReplace.output.fontSize'


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
            SettingsRule(BPSettingsKey.CONFIG_OPEN_ATSTARTUP,                               False,                    SettingsFmt(bool)),

            SettingsRule(BPSettingsKey.CONFIG_SESSION_DOCUMENTS_RECENTS_COUNT,              25,                       SettingsFmt(int, (1, 100))),

            SettingsRule(BPSettingsKey.CONFIG_EDITOR_FONT_NAME,                             "DejaVu Sans Mono",       SettingsFmt(str)),
            SettingsRule(BPSettingsKey.CONFIG_EDITOR_INDENT_WIDTH,                          4,                        SettingsFmt(int, (1, 8))),
            SettingsRule(BPSettingsKey.CONFIG_EDITOR_RIGHTLIMIT_WIDTH,                      120,                      SettingsFmt(int, (40, 240))),

            SettingsRule(BPSettingsKey.CONFIG_DOCKER_CONSOLE_BUFFERSIZE,                    0,                        SettingsFmt(int)),

            SettingsRule(BPSettingsKey.SESSION_EDITOR_FONT_SIZE,                            9,                        SettingsFmt(int, (5, 96))),
            SettingsRule(BPSettingsKey.SESSION_EDITOR_INDENT_VISIBLE,                       True,                     SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_EDITOR_SPACES_VISIBLE,                       True,                     SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_EDITOR_RIGHTLIMIT_VISIBLE,                   True,                     SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_EDITOR_LINE_NUMBER_VISIBLE,                  True,                     SettingsFmt(bool)),

            SettingsRule(BPSettingsKey.SESSION_EDITOR_HIGHTLIGHT_FCTCLASSDECL_ACTIVE,       True,                     SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_EDITOR_WRAPLINES_ACTIVE,                     True,                     SettingsFmt(bool)),

            SettingsRule(BPSettingsKey.SESSION_MAINWINDOW_WINDOW_GEOMETRY,                  [-1, -1, -1, -1],         SettingsFmt(int), SettingsFmt(int), SettingsFmt(int), SettingsFmt(int)),
            SettingsRule(BPSettingsKey.SESSION_MAINWINDOW_WINDOW_MAXIMIZED,                 False,                    SettingsFmt(bool)),

            # dockers layout use QMainWindow.saveState()/QMainWindow.restoreState()
            # Don't really like this solution as methods return binary data through a byte array rather than a human readable structure
            # but there's not really other choice to be able to save/restore dockers state (available methods doesn't allows to save/restore
            # all layout properties...)
            # byte array is base64 encoded in configuration file
            SettingsRule(BPSettingsKey.SESSION_MAINWINDOW_VIEW_DOCKERS_LAYOUT,              '',                       SettingsFmt(str)),

            SettingsRule(BPSettingsKey.SESSION_DOCUMENTS_ACTIVE,                            "",                       SettingsFmt(str)),
            SettingsRule(BPSettingsKey.SESSION_DOCUMENTS_OPENED,                            [],                       SettingsFmt(list)),
            SettingsRule(BPSettingsKey.SESSION_DOCUMENTS_RECENTS,                           [],                       SettingsFmt(list)),

            SettingsRule(BPSettingsKey.SESSION_PATH_LASTOPENED,                             "",                       SettingsFmt(str)),
            SettingsRule(BPSettingsKey.SESSION_PATH_LASTSAVED,                              "",                       SettingsFmt(str)),

            SettingsRule(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_VISIBLE,           True,                     SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_REGEX_CHECKED,     False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_CASESENSITIVE_CHECKED, False,                SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_WHOLEWORD_CHECKED, False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_BACKWARD_CHECKED,  False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_BTN_HIGHLIGHTALL_CHECKED, False,                 SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_CONSOLE_SEARCH_TEXT,                  '',                       SettingsFmt(str)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_CONSOLE_OPTIONS_AUTOCLEAR,            True,                     SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_CONSOLE_OPTIONS_FILTER_SEARCH,        False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_CONSOLE_OPTIONS_FILTER_TYPES,         ['error', 'warning', 'info', 'valid'],
                                                                                                                      SettingsFmt(list, ['error', 'warning', 'info', 'valid'])),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_CONSOLE_OUTPUT_FONT_SIZE,             12,                       SettingsFmt(int)),

            SettingsRule(BPSettingsKey.SESSION_DOCKER_COLORPICKER_MENU_SELECTED,            ['colorRGB', 'colorHSV', 'colorAlpha', 'colorCssRGB', 'colorWheel', 'colorPreview'],
                                                                                                                      SettingsFmt(list)),  # list is not fixed as palette names are not known

            SettingsRule(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_REGEX_CHECKED,         False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_CASESENSITIVE_CHECKED, False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_WHOLEWORD_CHECKED,     False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_BACKWARD_CHECKED,      False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_BTN_HIGHLIGHTALL_CHECKED,  False,                    SettingsFmt(bool)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_SAR_SEARCH_TEXT,                      '',                       SettingsFmt(str)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_SAR_REPLACE_TEXT,                     '',                       SettingsFmt(str)),
            SettingsRule(BPSettingsKey.SESSION_DOCKER_SAR_OUTPUT_FONT_SIZE,                 12,                       SettingsFmt(int))
        ]

        super(BPSettings, self).__init__(pluginId, rules)

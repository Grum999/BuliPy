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

from PyQt5.Qt import *
from PyQt5.QtCore import (
        pyqtSignal,
        QSettings,
        QStandardPaths
    )

import os
import json
import re

from .bplanguagedef import (
        BPLanguageDefPython,
        BPLanguageDefText,
        BPLanguageDefUnmanaged
    )

from ..pktk.modules.languagedef import (
        LanguageDefXML,
        LanguageDefJSON
    )
from ..pktk.modules.utils import Debug
from ..pktk.modules.uitheme import UITheme
from ..pktk.widgets.wcodeeditor import (
        WCodeEditorTheme,
        WCodeEditor
    )

from ..pktk.pktk import *

# -----------------------------------------------------------------------------

class BPThemes:
    """Manage all BuliPy settings with open&save options

    Configuration is saved as JSON file
    """

    __themes = {}
    __languageDef = []

    @staticmethod
    def load():
        """Load all themes, initialise language definition

        - internal (dark, light)
        - from plugin resources/themes
        - from plugin cache customThemes
        """
        BPThemes.__languageDef = [BPLanguageDefPython(),
                                  LanguageDefXML(),
                                  LanguageDefJSON(),
                                  BPLanguageDefText(),
                                  # -- unmanaged must be the last one
                                  BPLanguageDefUnmanaged()]

        BPThemes.__themes = {UITheme.DARK_THEME: WCodeEditor.DEFAULT_DARK,
                             UITheme.LIGHT_THEME: WCodeEditor.DEFAULT_LIGHT,
                             }

        pluginThemePath = os.path.join(os.path.dirname(__file__), 'resources', 'themes')
        pluginCachePath = os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "bulipy", "themes")
        jsonFiles = [os.path.join(pluginThemePath, fileName) for fileName in os.listdir(pluginThemePath) if re.search(r"\.json$", fileName) and os.path.isfile(os.path.join(pluginThemePath, fileName))]
        jsonFiles += [os.path.join(pluginCachePath, fileName) for fileName in os.listdir(pluginCachePath) if re.search(r"\.json$", fileName) and os.path.isfile(os.path.join(pluginCachePath, fileName))]

        for jsonFile in jsonFiles:
            BPThemes.loadTheme(jsonFile)

    @staticmethod
    def loadTheme(fileName):
        """Load given file theme

        Return False if theme can't be loaded
        True otherwise
        """
        fContent = ''
        try:
            with open(fileName, 'r') as fHandle:
                fContent = fHandle.read()
        except Exception as e:
            Debug.print(f"BPSettings.loadTheme: can't read file {fileName}")
            Debug.print(e)
            return False

        if fContent == '':
            return False

        themeDefinition = None
        try:
            themeDefinition = json.loads(fContent)
        except Exception as e:
            Debug.print(f"BPSettings.loadTheme: can't parse file {fileName}")
            Debug.print(e)
            return False

        if themeDefinition is None:
            return False

        try:
            theme = WCodeEditorTheme(themeDefinition['id'], themeDefinition['name'], themeDefinition['colors'], themeDefinition['base'], themeDefinition['comments'])

            for languageId in themeDefinition['languages'].keys():
                # loop languages in file
                for languageIndex, languageDef in enumerate(BPThemes.__languageDef):
                    # check if languages is managed
                    if languageId in languageDef.extensions():
                        # apply theme
                        BPThemes.__languageDef[languageIndex].setStyles(themeDefinition['id'], themeDefinition['languages'][languageId])
                        break

        except Exception as e:
            Debug.print(f"BPSettings.loadTheme: {fileName} is not a theme file ")
            Debug.print(str(e))
            return False

        BPThemes.__themes[theme.id()] = theme
        return True

    @staticmethod
    def themes(withName=False):
        """Return list of available themes identifier

        If `withName` is True, insted of return a list of Identifier, return a list of tuples (id, name)
        """
        if withName is False:
            return list(BPThemes.__themes.keys())
        else:
            return [(theme.id(), theme.name()) for theme in BPThemes.__themes.values()]

    @staticmethod
    def theme(id):
        """Return theme from given identifier

        If theme not foudn, return None
        """
        if id in BPThemes.__themes:
            return BPThemes.__themes[id]
        return None

    @staticmethod
    def languageDef(extension):
        """Return language defition for given extension

        Return BPLanguageDefUnmanaged() language if no language definition found for extension
        """
        for languageDef in BPThemes.__languageDef:
            if extension in languageDef.extensions():
                return languageDef
        # unmanaged extension
        return BPThemes.__languageDef[-1]

    @staticmethod
    def languageDefAvailable():
        """Return list of language defition available"""
        return BPThemes.__languageDef

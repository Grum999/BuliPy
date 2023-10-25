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

import os
import re
import sys
import time

import PyQt5.uic

from krita import (
        Extension,
        Krita
    )

from PyQt5.Qt import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
        pyqtSlot
    )

if __name__ != '__main__':
    # script is executed from Krita, loaded as a module
    __PLUGIN_EXEC_FROM__ = 'KRITA'

    from .pktk.pktk import (
            EInvalidStatus,
            EInvalidType,
            EInvalidValue,
            PkTk
        )

    from .bp.bpuicontroller import BPUIController
    from bulipy.pktk.modules.imgutils import buildIcon
    from bulipy.pktk.modules.uitheme import UITheme
    from bulipy.pktk.modules.utils import checkKritaVersion
else:
    # Execution from 'Scripter' plugin?
    __PLUGIN_EXEC_FROM__ = 'SCRIPTER_PLUGIN'

    from importlib import reload

    print("======================================")
    print(f'Execution from {__PLUGIN_EXEC_FROM__}')

    for module in list(sys.modules.keys()):
        if not re.search(r'^bulipy\.', module) is None:
            print('Reload module {0}: {1}', module, sys.modules[module])
            reload(sys.modules[module])

    from bulipy.pktk.pktk import (
            EInvalidStatus,
            EInvalidType,
            EInvalidValue,
            PkTk
        )

    from bulipy.bp.bpuicontroller import BPUIController
    from bulipy.pktk.modules.imgutils import buildIcon
    from bulipy.pktk.modules.uitheme import UITheme
    from bulipy.pktk.modules.utils import checkKritaVersion

    print("======================================")


EXTENSION_ID = 'pykrita_bulipy'
PLUGIN_VERSION = '0.1.1b'
PLUGIN_MENU_ENTRY = 'BuliPy'

REQUIRED_KRITA_VERSION = (5, 2, 0)


class BuliPy(Extension):

    def __init__(self, parent):
        # Default options

        # Always initialise the superclass.
        # This is necessary to create the underlying C++ object
        super().__init__(parent)
        self.parent = parent
        self.__uiController = None
        self.__isKritaVersionOk = checkKritaVersion(*REQUIRED_KRITA_VERSION)

    def __initUiController(self, kritaIsStarting=False):
        """Initialise UI controller

        `kritaIsStarting` set to True if UiConbtroller is intialised during Krita's startup,
        otherwise set to False (initialised on first manual execution)
        """
        try:
            Krita.instance().notifier().applicationClosing.disconnect()
        except Exception as e:
            pass

        if self.__uiController is None:
            # no controller, create it
            # (otherwise, with Krita 5.x, can be triggered more than once time - on each new window)
            self.__uiController = BPUIController(PLUGIN_MENU_ENTRY, PLUGIN_VERSION, kritaIsStarting)

    def setup(self):
        """Is executed at Krita's startup"""
        @pyqtSlot()
        def windowCreated():
            # the best place to initialise controller (just after main window is created)
            self.__initUiController(True)

        if not self.__isKritaVersionOk:
            return

        if checkKritaVersion(5, 2, 0):
            # windowCreated signal has been implemented with krita 5.2.0
            Krita.instance().notifier().setActive(True)
            Krita.instance().notifier().windowCreated.connect(windowCreated)

        UITheme.load()
        UITheme.load(os.path.join(os.path.dirname(__file__), 'bp', 'resources'))

    def createActions(self, window):
        action = window.createAction(EXTENSION_ID, PLUGIN_MENU_ENTRY, "tools")
        action.triggered.connect(self.start)
        action.setIcon(buildIcon([(':/bp/images/normal/bulipy', QIcon.Normal),
                                  (':/bp/images/disabled/compositionhelper', QIcon.Disabled)]))

    def start(self):
        """Execute BuliPy"""
        # ----------------------------------------------------------------------
        # Create dialog box
        if not self.__isKritaVersionOk:
            QMessageBox.information(QWidget(),
                                    PLUGIN_MENU_ENTRY,
                                    i18n("At least, Krita version {0} is required to use plugin...").format('.'.join([str(v) for v in REQUIRED_KRITA_VERSION]))
                                    )
            return

        if self.__uiController is None:
            # with krita 5.0.0, might be created at krita startup
            self.__initUiController(False)
        self.__uiController.start()


if __PLUGIN_EXEC_FROM__ == 'SCRIPTER_PLUGIN':
    sys.stdout = sys.__stdout__

    # Disconnect signals if any before assigning new signals

    pb = BuliPy(Krita.instance())
    pb.setup()
    pb.start()

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

from os.path import (join, getsize)

from ..pktk.modules.hlist import HList

from ..pktk.pktk import *

# -----------------------------------------------------------------------------


class BPHistory(HList):

    def removeMissingFiles(self):
        """Remove missing directories from history"""
        modified = False
        tmpList = []
        for path in self.list():
            if isinstance(path, str) and os.path.isfile(path):
                tmpList.append(path)
            else:
                modified = True

        if modified:
            self.setItems(tmpList)

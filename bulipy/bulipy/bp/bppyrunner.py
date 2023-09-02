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
import json
import traceback

from PyQt5.Qt import *
import PyQt5.QtCore as QtCore

from .bpdwconsole import BPDockWidgetConsoleOutput

from ..pktk.modules.utils import (JsonQObjectEncoder, JsonQObjectDecoder)
from ..pktk.modules.timeutils import (tsToStr, secToStrTime)
from ..pktk.widgets.wconsole import (WConsoleType, WConsole, WConsoleUserData)


class BPLogger(object):
    """Redirect stdout/stderr to console + file"""

    # Flush buffer content after 250ms or 2000 rows
    __BUFFER_FLUSH_MAXDELAY = 0.25
    __BUFFER_FLUSH_MAXSIZE = 2000

    __BUFFER_FLUSH_MODE_APPENDLINE = 0x00
    __BUFFER_FLUSH_MODE_APPEND = 0x01

    __LOGFILE_MODE_APPENDLINE = 0x00
    __LOGFILE_MODE_APPEND = 0x01

    @staticmethod
    def reloadCacheConsole(console, fileName):
        """If filename is a console dump file, reload it

        return True if loaded, otherwise False
        """
        if not isinstance(fileName, str) or fileName == '':
            return False

        console.setUpdatesEnabled(False)
        console.console().clear()
        consoleLoaded = False
        try:
            with open(fileName, 'r') as fHandle:
                content = fHandle.read()

                for block in content.split('\x00\x00')[1:]:
                    raw = (block[0] == 'T')
                    consoleType = WConsoleType(int(block[1]))

                    if jsonData := re.search(r'\x01\x01(.*?)\x01\x02', block, re.M | re.S):
                        data = jsonData.groups()[0]
                        if len(data) > 0:
                            data = json.loads(data, cls=JsonQObjectDecoder)
                        else:
                            data = None
                    else:
                        data = None

                    if text := re.search(r'\x01\x02(.*)', block, re.M | re.S):
                        text = text.groups()[0]
                    else:
                        text = ''

                    lines = text.split("\n")
                    if lines[-1] == '':
                        lines = lines[0:-1]

                    console.append(lines, consoleType, data, True, raw)
            consoleLoaded = True
        except Exception as e:
            # can't read console cache file
            # print(e)
            pass

        console.setUpdatesEnabled(True)
        console.updateSearchAndFilter()
        return consoleLoaded

    def __init__(self, console, filename):
        super(BPLogger, self).__init__()

        # For performance, as console is slow, put console content in a buffer that will
        # be flushed
        self.__buffer = []
        self.__bufferLastFlush = time.time()

        self.__console = console

        self.__fileLog = open(filename, "w")

        self.__flushMode = BPLogger.__BUFFER_FLUSH_MODE_APPENDLINE
        self.__logfileMode = BPLogger.__LOGFILE_MODE_APPEND

        # redirect outputs
        sys.stdout = self
        sys.stderr = self

    def append(self, text, type=WConsoleType.NORMAL, data=None, cReturn=True, raw=False):
        """Append content to console without buffering"""
        def tf(v):
            if v:
                return 'T'
            return 'F'

        def lf(v):
            if v:
                return '\n'
            return ''

        def dump(data):
            returned = '\x01\x01'
            if data is not None:
                returned += json.dumps(data, cls=JsonQObjectEncoder)
            returned += '\x01\x02'
            return returned

        self.flush(stripLastNL=True)

        if isinstance(text, list):
            text = "\n".join(text)
        self.__console.append(text, type, data, cReturn, raw)

        if self.__fileLog:
            self.__fileLog.write('\x00\x00' +
                                 tf(raw) +
                                 str(type.value) +
                                 dump(data) +
                                 text
                                 )

        self.__flushMode = BPLogger.__BUFFER_FLUSH_MODE_APPENDLINE
        self.__logfileMode = BPLogger.__LOGFILE_MODE_APPENDLINE

    def flush(self, force=True, stripLastNL=False):
        """Flush buffer to console"""
        if (force or (time.time() - self.__bufferLastFlush) > BPLogger.__BUFFER_FLUSH_MAXDELAY or len(self.__buffer) > BPLogger.__BUFFER_FLUSH_MAXSIZE) and len(self.__buffer):
            # create a big string to flush
            toFlush = ''.join(self.__buffer)

            if stripLastNL and toFlush[-1] == '\n':
                toFlush = toFlush[0:-1]

            # flush buffer
            self.__console.append(toFlush, WConsoleType.NORMAL, None, (self.__flushMode == BPLogger.__BUFFER_FLUSH_MODE_APPENDLINE), True)
            self.__buffer = []
            self.__bufferLastFlush = time.time()
            # update console
            self.__console.setUpdatesEnabled(True)
            QApplication.processEvents(QEventLoop.ExcludeUserInputEvents, 10)
            self.__console.setUpdatesEnabled(False)
            # flag method for next flush
            self.__flushMode = BPLogger.__BUFFER_FLUSH_MODE_APPEND
            self.__logfileMode = BPLogger.__LOGFILE_MODE_APPEND

    def close(self):
        """Close logger

        Do cleanup
        Restore initial states
        """
        self.flush()
        self.__console.scrollToLastRow()
        self.__console.setUpdatesEnabled(True)

        # restore default outputs
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        # close log file
        if self.__fileLog:
            self.__fileLog.close()

    def write(self, message):
        """Write provided `message` to output (buffer + log file)"""
        self.__buffer.append(message)
        if self.__fileLog:
            if self.__logfileMode == BPLogger.__LOGFILE_MODE_APPENDLINE:
                self.__fileLog.write('\x00\x00T' +
                                     str(WConsoleType.NORMAL.value) +
                                     '\x01\x01\x01\x02')
                self.__logfileMode = BPLogger.__LOGFILE_MODE_APPEND
            self.__fileLog.write(message)

        self.flush(False)


class BPPyRunner:
    """Python script runner"""

    def __init__(self, document, console):
        super(BPPyRunner, self).__init__()

        self.__document = document
        self.__console = console

        self.__pythonCompiled = None

        self.__uuid = f"@{self.__document.cacheUuid()}"
        self.__fullFileName = self.__document.tabName(True)
        self.__scriptPath = None

        self.__isRunning = False

        self.__separator = f"================{'=' * (max(len(self.__fullFileName), 19))}"

        self.__startTime = None
        self.__endTime = None
        self.__duration = None

        self.__logger = None

        if os.path.exists(self.__fullFileName):
            # execution is from a file
            self.__scriptPath = os.path.dirname(os.path.abspath(os.path.expanduser(self.__fullFileName)))

    def __qtMessageHandler(self, msgType, logContext, message):
        """Message handler for Qt (qDebug, qInfo, ...)"""
        match msgType:
            case QtCore.QtInfoMsg:
                consoleType = WConsoleType.INFO
            case  QtCore.QtWarningMsg:
                consoleType = WConsoleType.WARNING
            case QtCore.QtCriticalMsg:
                consoleType = WConsoleType.ERROR
            case  QtCore.QtFatalMsg:
                consoleType = WConsoleType.ERROR
            case _:
                consoleType = WConsoleType.NORMAL

        self.__logger.append(message,
                             consoleType,
                             {'fromPosition': QPoint(1, logContext.line),
                              'toPosition': QPoint(),
                              'function': logContext.function,
                              'source': logContext.file
                              })

    def __loggerAddSeparator(self):
        """Add a separator in console"""
        self.__logger.append(f"#lc#{self.__separator}#", WConsoleType.INFO)

    def __formatCodePosition(self, codeLine, position=0):
        """Return a formatted line to indicate position in line code

            Example:
                __formatCodePosition("def test(p1, p1):", 14) will return string:
                "  ├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤"
                "  def test(p1, p1):"
                " •╌╌╌╌╌╌╌╌╌╌╌╌╌┘"
        """
        if not codeLine:
            return ''

        maxLen = 0
        codeLines = codeLine.split("\n")
        for line in codeLines:
            if len(line) > maxLen:
                maxLen = len(line)
        maxLen -= 2

        if isinstance(position, int) and position >= 0:
            return '\n'.join([f"#ly#  ╓{'┈' * maxLen}╖#",
                              f"#y#*  {WConsole.escape(codeLine)}*#",
                              f"#ly# •{'╌' * position}┘#"
                              ])
        else:

            return '\n'.join([f"#ly#  ╓{'┈' * maxLen}╖#",
                              f"#y#*  {WConsole.escape(codeLine)}*#",
                              f"#ly#  ╙{'┈' * maxLen}╜#"
                              ])

    def __compile(self):
        """Compile script"""
        def formatException(message, exception):
            # lineno
            #   > Which line number in the file the error occurred in. This is 1-indexed: the first line in the file has a lineno of 1.
            # offset
            #   > The column in the line where the error occurred. This is 1-indexed: the first character in the line has an offset of 1.
            # text
            #   > The source code text involved in the error.
            # end_lineno
            #   > Which line number in the file the error occurred ends in. This is 1-indexed: the first line in the file has a lineno of 1.
            # end_offset
            #   > The column in the end line where the error occurred finishes. This is 1-indexed: the first character in the line has an offset of 1.
            NL = '\n'
            JOINNL = '#\n#y#'

            exceptionText = exception.text
            if exceptionText is None:
                exceptionText = ''

            if exceptionText == '' and exception.lineno is not None and exception.filename == self.__document.tabName(False):
                # line not provided?
                # get it from source code
                exceptionText = self.__document.content().split('\n')[exception.lineno - 1]

            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            errorType = traceback.format_exception_only(exceptionType, exceptionValue)[-1].split(':', 1)

            returnedMsg = [f"**#lr#Compilation failed#**",
                           f"#r#- In file:#  #y#{exception.filename.replace(self.__uuid, self.__fullFileName)}#",
                           f"#r#  Line:#     #ly#{exception.lineno}#",
                           f"#r#  Position:# #ly#{exception.offset}#"
                           ]

            if exceptionText != '':
                returnedMsg.append("#y#" + self.__formatCodePosition(JOINNL.join(exceptionText.strip(NL).split(NL)), exception.offset - 1) + "#")

            returnedMsg += [" ",
                            f"#lr#**{message}:**#",
                            f"  #r#{WConsole.escape(errorType[1].strip(NL).strip())} #"
                            ]

            returnedData = {'fromPosition': QPoint(exception.offset, exception.lineno),
                            'toPosition': QPoint(exception.end_offset, exception.end_lineno),
                            'source': exception.filename
                            }

            return (returnedMsg, returnedData)

        self.__isRunning = True
        self.__console.setScriptIsRunning(True)
        if not self.__console.autoClear():
            self.__loggerAddSeparator()

        self.__logger.append(f"#lc#**Compile script:**# #c#{self.__fullFileName}#", WConsoleType.INFO)

        errorMsg = []
        errorData = None

        try:
            self.__pythonCompiled = compile(self.__document.content(), self.__uuid, 'exec')
        except TabError as e:
            errorMsg, errorData = formatException(f"Inconsistent use of tabs and spaces", e)
        except IndentationError as e:
            errorMsg, errorData = formatException(f"Incorrect indentation", e)
        except SyntaxError as e:
            # https://docs.python.org/3.10/library/exceptions.html#SyntaxError
            errorMsg, errorData = formatException(f"Syntax error", e)

        if len(errorMsg):
            self.__loggerAddSeparator()
            self.__logger.append(errorMsg, WConsoleType.ERROR, errorData)

            self.__console.setScriptIsRunning(False)
            self.__isRunning = False
            return False

        return True

    def __start(self):
        """Initialize start execution"""
        self.__startTime = time.time()

        # --- start information
        self.__logger.append(f"#lc#**Started at:**#     #c#{tsToStr(self.__startTime)}#", WConsoleType.INFO)
        self.__loggerAddSeparator()

        # force console update before starting python script execution
        self.__logger.flush()

    def __end(self):
        """Finalize execution"""
        self.__endTime = time.time()
        self.__duration = self.__endTime - self.__startTime

        self.__logger.append([f"#lc#{self.__separator}#",
                              f"#lc#**Finished at:**#    #c#{tsToStr(self.__endTime)}#",
                              f"#lc#**Duration:**#       #c#{secToStrTime(self.__duration, True)}#"
                              ],
                             WConsoleType.INFO)
        self.__console.setScriptIsRunning(False)
        self.__isRunning = False

    def __run(self):
        """Run script"""
        self.__console.setUpdatesEnabled(False)

        if self.__scriptPath:
            # execution from a saved file

            if self.__scriptPath not in sys.path:
                # add current file directory in sys.path
                # => make easier to load relative modules of files
                sys.path.append(self.__scriptPath)

            for moduleName in [name for name in sys.modules.keys()]:
                if hasattr(sys.modules[moduleName], '__file__') and sys.modules[moduleName].__file__ and self.__scriptPath in sys.modules[moduleName].__file__:
                    # a 'local' module was previously imported by executed script
                    # remove module
                    del sys.modules[moduleName]

        initialQtMessageHandler = qInstallMessageHandler(self.__qtMessageHandler)

        try:
            result = exec(self.__pythonCompiled, {"__name__": '__main__',
                                                  "__package__": 'bulipy'})
        except SystemExit as e:
            # quit() or exit()
            self.__logger.append(f"**#y#Script execution stopped with exit code# #ly#{e.code}#**", WConsoleType.WARNING)
        except Exception as e:

            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()

            errorType = traceback.format_exception_only(exceptionType, exceptionValue)[0].split(":", 1)
            errorTraceBack = traceback.extract_tb(exceptionTraceback)[1:]

            NL = '\n'
            self.__logger.append([f"**#lr#Script execution stopped#**",
                                  f"**#lr#Traceback:#**"
                                  ],
                                 WConsoleType.ERROR)

            sourceLines = self.__document.content().split('\n')
            for traceBack in errorTraceBack:
                exceptionText = traceBack[3]
                if traceBack[1] > 0:
                    if exceptionText != '':
                        exceptionText = self.__formatCodePosition(exceptionText, None)
                    elif traceBack[0] == self.__uuid and exceptionText == '':
                        # get line from source code
                        exceptionText = self.__formatCodePosition(sourceLines[traceBack[1] - 1], None)

                consoleText = [f"#r#- In file:#  #y#{traceBack[0].replace(self.__uuid, self.__fullFileName)}#",
                               f"#r#  Function:# #y#{traceBack[2]}#",
                               f"#r#  Line:#     #ly#{traceBack[1]}#"
                               ]
                if exceptionText:
                    consoleText.append(exceptionText)

                consoleText.append('')
                self.__logger.append(consoleText,
                                     WConsoleType.ERROR,
                                     {'fromPosition': QPoint(1, traceBack[1]),
                                      'toPosition': QPoint(),
                                      'source': traceBack[0]
                                      })

            self.__logger.append([" ",
                                  f"**#lr#{errorType[0]}:#**",
                                  f"  #r#{WConsole.escape(errorType[1].strip(NL).strip())} #"
                                  ])

        qInstallMessageHandler(initialQtMessageHandler)

        if self.__scriptPath and self.__scriptPath in sys.path:
            # remove current file directory from sys.path
            sys.path.remove(self.__scriptPath)

    def run(self):
        # initialise logger
        self.__logger = BPLogger(self.__console, self.__document.cacheFileNameConsole())

        if self.__compile():
            self.__start()
            self.__run()
            self.__end()

        self.__logger.close()
        self.__logger = None

    def isRunning(self):
        """return is currently running"""
        return self.__isRunning


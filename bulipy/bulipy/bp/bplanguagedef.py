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

# Python language definition, used for syntax highlighting

from PyQt5.Qt import *
from PyQt5.QtGui import QColor

from enum import Enum
import re

from ..pktk.modules.uitheme import UITheme
from ..pktk.modules.languagedef import LanguageDef
from ..pktk.widgets.wcodeeditor import WCodeEditorHighlightLineRule

from ..pktk.modules.tokenizer import (
        Token,
        Tokenizer,
        TokenizerRule,
        TokenType
    )


class BPLanguageDefPython(LanguageDef):
    # define token types

    class ITokenType(TokenType):
        STRING = ('str', 'A String value')
        FSTRING = ('fstr', 'A F-String value')
        BSTRING = ('bstr', 'A Binary String value')
        STRING_LONG = ('strl', 'A long String value')
        FSTRING_LONG = ('fstrl', 'A long F-String value')
        BSTRING_LONG = ('bstrl', 'A long Binary String value')

        NUMBER = ('number', 'A NUMBER value')

        KEYWORD = ('kwrd', 'A keyword identifier')
        KEYWORD_CONSTANT = ('kwrd_const', 'A keyword constant')
        KEYWORD_OPERATOR = ('kwrd_operator', 'A keyword operator')

        BUILTIN_FUNC = ('builtin_fct', 'Built-in function')
        # BUILTIN_EXCEPTION = ('builtin_except', 'Built-in exception')

        OPERATORS = ('operators', 'Operators like plus, minus, divide, ...')

        DELIMITER = ('delim', 'Miscellaneous delimiters')

        DECL_CLASS = ('declC', 'Declare a class')
        DECL_FUNC = ('declF', 'Declare a Function')

        IDENTIFIER = ('identifier', 'An identifier')
        DECORATOR = ('decorator', 'A decorator')

        LINE_JOIN = ('linejoin', 'Line join')

    def __init__(self):
        """Initialise language & styles"""
        super(BPLanguageDefPython, self).__init__([
            # ---
            #
            TokenizerRule(BPLanguageDefPython.ITokenType.COMMENT,  r'#[^\n]*'),

            # ---
            # https://docs.python.org/3.10/reference/lexical_analysis.html#string-and-bytes-literals
            #
            # Need to make distinction between all possibles string for syntax highlighting
            TokenizerRule(BPLanguageDefPython.ITokenType.STRING_LONG,
                          r'''(?:rf|fr|rb|br|b|f|u|r)?(?:'{3}(?:.|\s|\n)*?'{3}|"{3}(?:.|\s|\n)*?"{3})''',
                          multiLineStart=(r"""(rf|fr|rb|br|b|f|u|r)?(?:'{3})""", r'''(rf|fr|rb|br|b|f|u|r)?(?:"{3})'''),
                          multiLineEnd=(r"""(?:'{3})""", r'''(?:"{3})'''),
                          subTypes=[(BPLanguageDefPython.ITokenType.BSTRING_LONG, '^(?:br|rb|b)'),
                                    (BPLanguageDefPython.ITokenType.FSTRING_LONG, '^(?:fr|rf|f)')
                                    ],
                          caseInsensitive=True,
                          ignoreIndent=True),

            TokenizerRule(BPLanguageDefPython.ITokenType.STRING,
                          r'''(?:rf|fr|rb|br|b|f|u|r)?(?:"(?:(?:.?\\"|[^"])*(?:\.(?:\\"|[^"]*))*")|(?:'(?:.?\\'|[^'])*(?:\.(?:\\'|[^']*))*'))''',
                          subTypes=[(BPLanguageDefPython.ITokenType.BSTRING, '^(?:br|rb|b)'),
                                    (BPLanguageDefPython.ITokenType.FSTRING, '^(?:fr|rf|f)')
                                    ],
                          caseInsensitive=True,
                          ignoreIndent=True),

            # --
            # https://peps.python.org/pep-0318/
            TokenizerRule(BPLanguageDefPython.ITokenType.DECORATOR,
                          r"(?:@[a-z_][a-z0-9_]*)\b",
                          caseInsensitive=True,
                          ignoreIndent=True),

            # ---
            # https://docs.python.org/3.10/reference/lexical_analysis.html#keywords
            TokenizerRule(BPLanguageDefPython.ITokenType.KEYWORD,
                          r"\b(?:"
                          r"yield|"
                          r"with|while|"
                          r"try|"
                          r"return|raise|"
                          r"pass|"
                          r"nonlocal|"
                          r"lambda|"
                          r"import|if|"
                          r"global|"
                          r"from|for|finally|"
                          r"except|else|elif|"
                          r"del|def|"
                          r"continue|class|"
                          r"break|"
                          r"await|async|assert|as"
                          r")\b",
                          caseInsensitive=False,
                          ignoreIndent=True),
            TokenizerRule(BPLanguageDefPython.ITokenType.KEYWORD_OPERATOR,
                          r"\b(?:and|in|is|or|not)\b",
                          caseInsensitive=False,
                          ignoreIndent=True),

            # --
            # https://docs.python.org/3.10/library/functions.html
            TokenizerRule(BPLanguageDefPython.ITokenType.BUILTIN_FUNC,
                          r"\b(?:"
                          r"zip|"
                          r"vars|"
                          r"type|tuple|"
                          r"super|sum|str|staticmethod|sorted|slice|setattr|set|"
                          r"round|reversed|repr|range|"
                          r"property|print|pow|"
                          r"ord|open|oct|object|"
                          r"next|"
                          r"min|memoryview|max|map|"
                          r"locals|list|len|"
                          r"iter|issubclass|isinstance|int|input|id|"
                          r"hex|help|hash|hasattr|"
                          r"globals|getattr|"
                          r"frozenset|format|float|filter|"
                          r"exec|eval|enumerate|"
                          r"divmod|dir|dict|delattr|"
                          r"complex|compile|classmethod|chr|callable|"
                          r"bytes|bytearray|breakpoint|bool|bin|"
                          r"ascii|any|anext|all|aiter|abs|"
                          r"__import__"
                          r")\b(?=\()",
                          caseInsensitive=False,
                          ignoreIndent=True),

            # --
            # https://docs.python.org/3.10/library/exceptions.html
            # TokenizerRule(BPLanguageDefPython.ITokenType.BUILTIN_EXCEPTION,
            #              r"\b(?:"
            #              r"ZeroDivisionError|"
            #              r"Warning|"
            #              r"ValueError|"
            #              r"UserWarning|UnicodeWarning|UnicodeTranslateError|UnicodeError|UnicodeEncodeError|UnicodeDecodeError|UnboundLocalError|"
            #              r"TypeError|TimeoutError|TabError|"
            #              r"SystemExit|SystemError|SyntaxWarning|SyntaxError|StopIteration|StopAsyncIteration|"
            #              r"RuntimeWarning|RuntimeError|ResourceWarning|ReferenceError|RecursionError|"
            #              r"ProcessLookupError|PermissionError|PendingDeprecationWarning|"
            #              r"OverflowError|OSError|"
            #              r"NotImplementedError|NotADirectoryError|NameError|"
            #              r"ModuleNotFoundError|MemoryError|"
            #              r"LookupError|"
            #              r"KeyboardInterrupt|KeyError|"
            #              r"IsADirectoryError|InterruptedError|IndexError|IndentationError|ImportWarning|ImportError|"
            #              r"GeneratorExit|"
            #              r"FutureWarning|FloatingPointError|FileNotFoundError|FileExistsError|"
            #              r"Exception|EncodingWarning|EOFError|"
            #              r"DeprecationWarning|"
            #              r"ConnectionResetError|ConnectionRefusedError|ConnectionError|ConnectionAbortedError|ChildProcessError|"
            #              r"BytesWarning|BufferError|BrokenPipeError|BlockingIOError|BaseException|"
            #              r"AttributeError|AssertionError|ArithmeticError"
            #              r")\b",
            #              caseInsensitive=False),

            # --
            # https://docs.python.org/3.10/library/constants.html
            # https://docs.python.org/3.10/reference/lexical_analysis.html#soft-keywords
            TokenizerRule(BPLanguageDefPython.ITokenType.KEYWORD_CONSTANT,
                          r"\b(?:Ellipsis|False|None|True|NotImplemented|case|match|_)\b",
                          caseInsensitive=False,
                          ignoreIndent=True),

            # ---
            # https://docs.python.org/3.10/reference/lexical_analysis.html#integer-literals (+Imaginary literals)
            # https://docs.python.org/3.10/reference/lexical_analysis.html#floating-point-literals (+Imaginary literals)
            TokenizerRule(BPLanguageDefPython.ITokenType.NUMBER,
                          r"(?:[1-9](?:_?\d+)*|(?:\.|\d(?:_?\d)*\.)(?:\d(?:_?\d)*)?(?:e[+-]?\d(?:_?\d)*)?|[1-9]\d*(?:e[+-]?\d(?:_?\d)*)|0o(?:_?[0-7]+)*|0b(?:_?[01]+)*|0x(?:_?[0-9A-F]+)*|0+)j?\b",
                          caseInsensitive=True,
                          ignoreIndent=True),

            # ---
            TokenizerRule(BPLanguageDefPython.ITokenType.DECL_CLASS,
                          r"(?<=class\s+)(?:[a-zA-Z_][a-zA-Z0-9_]*)(?=\s*[\(:])",
                          caseInsensitive=True,
                          ignoreIndent=True),
            TokenizerRule(BPLanguageDefPython.ITokenType.DECL_FUNC,
                          r"(?<=def\s+)(?:[a-z_][a-z0-9_]*)(?=\s*\()",
                          caseInsensitive=True,
                          ignoreIndent=True),

            # --
            # https://docs.python.org/3.10/reference/lexical_analysis.html#identifiers
            TokenizerRule(BPLanguageDefPython.ITokenType.IDENTIFIER,
                          r"\b(?:[a-zA-Z_][a-zA-Z0-9_]*)\b",
                          caseInsensitive=False,
                          ignoreIndent=True),

            # ---
            TokenizerRule(BPLanguageDefPython.ITokenType.LINE_JOIN, r"\s\\$"),

            # ---
            # https://docs.python.org/3.10/reference/lexical_analysis.html#delimiters
            # https://docs.python.org/3.10/reference/lexical_analysis.html#operators
            TokenizerRule(BPLanguageDefPython.ITokenType.OPERATORS,
                          r"(?:->|\+=|-=|\*\*=|\*=|//=|/=|%=|@=\@|&=|\|=|\^=|>>=|<<=|\+|\*\*|\*|//|/|%|<<|>>|&|\||\^|~|:=|<=|<>|<|>=|>|==|!=|-|=)",
                          caseInsensitive=False,
                          ignoreIndent=True),

            # ---
            # https://docs.python.org/3.10/reference/lexical_analysis.html#delimiters
            TokenizerRule(BPLanguageDefPython.ITokenType.DELIMITER,
                          r"[,;\.:\(\)\[\]\{\}]",
                          caseInsensitive=False,
                          ignoreIndent=True),

            # all spaces except line feed
            TokenizerRule(BPLanguageDefPython.ITokenType.SPACE,  r"(?:(?!\n)\s)+",
                          caseInsensitive=False,
                          ignoreIndent=True),

            # line feed
            TokenizerRule(BPLanguageDefPython.ITokenType.NEWLINE,  r"(?:^\s*\r?\n|\r?\n?\s*\r?\n)+",
                          caseInsensitive=False,
                          ignoreIndent=True),

            # Unknown --> everything else
            TokenizerRule(BPLanguageDefPython.ITokenType.UNKNOWN,  r"[^\s]+",
                          caseInsensitive=False,
                          ignoreIndent=True),
            ],
            BPLanguageDefPython.ITokenType)

        self.tokenizer().setSimplifyTokenSpaces(False)
        # self.tokenizer().setIndent(4)
        # print(self.tokenizer())

        self.setStyles(UITheme.DARK_THEME, [
            (BPLanguageDefPython.ITokenType.STRING, '#98c379', False, False),
            (BPLanguageDefPython.ITokenType.STRING_LONG, '#aed095', False, False),

            (BPLanguageDefPython.ITokenType.FSTRING, '#98c379', False, True),
            (BPLanguageDefPython.ITokenType.FSTRING_LONG, '#aed095', False, True),

            (BPLanguageDefPython.ITokenType.BSTRING, '#56b6c2', False, False),
            (BPLanguageDefPython.ITokenType.BSTRING_LONG, '#7cc6d0', False, False),

            (BPLanguageDefPython.ITokenType.NUMBER, '#c9986a', False, False),

            (BPLanguageDefPython.ITokenType.KEYWORD, '#c678dd', True, False),
            (BPLanguageDefPython.ITokenType.KEYWORD_CONSTANT, '#dd7892', True, False),
            (BPLanguageDefPython.ITokenType.KEYWORD_OPERATOR, '#ff99ff', True, False),

            (BPLanguageDefPython.ITokenType.BUILTIN_FUNC, '#80bfff', False, False),

            (BPLanguageDefPython.ITokenType.OPERATORS, '#ff99ff', False, False),

            (BPLanguageDefPython.ITokenType.DELIMITER, '#ff66d9', False, False),

            (BPLanguageDefPython.ITokenType.LINE_JOIN, '#ff66d9', True, False, '#FDFF9E'),

            (BPLanguageDefPython.ITokenType.DECL_CLASS, '#ffe066', True, False),
            (BPLanguageDefPython.ITokenType.DECL_FUNC, '#ffe066', True, False),

            (BPLanguageDefPython.ITokenType.IDENTIFIER, '#e6e6e6', False, False),
            (BPLanguageDefPython.ITokenType.DECORATOR, '#ffffe6', True, True),

            (BPLanguageDefPython.ITokenType.COMMENT, '#5c6370', False, True)
        ])
        self.setStyles(UITheme.LIGHT_THEME, [
            (BPLanguageDefPython.ITokenType.STRING, '#238800', False, False),
            (BPLanguageDefPython.ITokenType.STRING_LONG, '#5D8C00', False, False),

            (BPLanguageDefPython.ITokenType.FSTRING, '#238800', False, True),
            (BPLanguageDefPython.ITokenType.FSTRING_LONG, '#5D8C00', False, True),

            (BPLanguageDefPython.ITokenType.BSTRING, '#008878', False, False),
            (BPLanguageDefPython.ITokenType.BSTRING_LONG, '#00B5A0', False, False),

            (BPLanguageDefPython.ITokenType.NUMBER, '#D97814', False, False),

            (BPLanguageDefPython.ITokenType.KEYWORD, '#9B0F83', True, False),
            (BPLanguageDefPython.ITokenType.KEYWORD_CONSTANT, '#CC427B', True, False),
            (BPLanguageDefPython.ITokenType.KEYWORD_OPERATOR, '#DF0BEA', True, False),

            (BPLanguageDefPython.ITokenType.BUILTIN_FUNC, '#2677CC', True, False),

            (BPLanguageDefPython.ITokenType.OPERATORS, '#DF0BEA', False, False),

            (BPLanguageDefPython.ITokenType.DELIMITER, '#D953B5', False, False),

            (BPLanguageDefPython.ITokenType.LINE_JOIN, '#D953B5', False, False, '#FDFF9E'),

            (BPLanguageDefPython.ITokenType.DECL_CLASS, '#00019C', True, False),
            (BPLanguageDefPython.ITokenType.DECL_FUNC, '#00019C', True, False),

            (BPLanguageDefPython.ITokenType.IDENTIFIER, '#333333', False, True),
            (BPLanguageDefPython.ITokenType.DECORATOR, '#8D8D7F', True, True),

            (BPLanguageDefPython.ITokenType.COMMENT, '#686D9C', False, True)

        ])

    def name(self):
        """Return language name"""
        return "Python"

    def extensions(self):
        """Return language file extension as list"""
        return ['.py']


class BPLanguageDefText(LanguageDef):
    # Empty language definition

    def __init__(self):
        """Initialise language & styles"""
        super(BPLanguageDefText, self).__init__()
        self.clearStyles()

    def name(self):
        """Return language name"""
        return "Text"

    def extensions(self):
        """Return language file extension as list"""
        return ['.txt']


class BPLanguageDefUnmanaged(LanguageDef):
    # Empty language definition

    def __init__(self):
        """Initialise language & styles"""
        super(BPLanguageDefUnmanaged, self).__init__()
        self.clearStyles()

    def name(self):
        """Return language name"""
        return "Unmanaged"

    def extensions(self):
        """Return language file extension as list"""
        return []


class BPCodeEditorHighlightLineRulePython(WCodeEditorHighlightLineRule):
    """Extend WCodeEditorHighlightLineRule to manage highlighting lines rules specific to python"""

    RULEID_PYFCTCLASS = 0x0100

    def __init__(self, theme):
        pass

    def ruleId(self):
        """Return rule identifier"""
        return BPCodeEditorHighlightLineRulePython.RULEID_PYFCTCLASS

    def highlight(self, block, tokens, lineNumber, isCurrentLine):
        """Return highlight properties, or None

        When called, are provided:
        - text `block` (QTextBlock)
        - `tokens` list (Tokens)
        - `lineNumber` (int)
        - is the current line (bool)

        Method returns:
        - None if line don't have to be highlighted
        - A tuple if line have to be highlighted
            0: int      Define priority (0xFF is current line color select; lower values are rendered before, higher value are rendered after)
            1: QColor   Define color for highlighting
            2: Boolean  Define if gutter have to be highlighted too
        """
        if tokens is None:
            return None

        for token in tokens.list():
            if token.type() in (BPLanguageDefPython.ITokenType.DECL_FUNC, BPLanguageDefPython.ITokenType.DECL_CLASS):
                return (BPCodeEditorHighlightLineRulePython.RULEID_PYFCTCLASS, QColor('#0affea00'), True)

        return None

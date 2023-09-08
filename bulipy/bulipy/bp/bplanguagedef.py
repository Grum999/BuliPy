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

from enum import Enum
import re

from ..pktk.modules.uitheme import UITheme
from ..pktk.modules.languagedef import LanguageDef

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
        STRING_LONG_S = ('str_l_s', 'A long String value (single quote)')
        STRING_LONG_D = ('str_l_d', 'A long String value (double quotes)')
        FSTRING_LONG_S = ('fstr_l_s', 'A long F-String value (single quote)')
        FSTRING_LONG_D = ('fstr_l_d', 'A long F-String value (double quotes)')
        BSTRING_LONG_S = ('bstr_l_s', 'A long Binary String value (single quote)')
        BSTRING_LONG_D = ('bstr_l_d', 'A long Binary String value (double quotes)')

        NUMBER_INT = ('number_int', 'An INTEGER NUMBER value')
        NUMBER_FLT = ('number_flt', 'An FLOAT NUMBER value')

        KEYWORD = ('kwrd', 'A keyword identifier')
        KEYWORD_SOFT = ('kwrd_soft', 'A soft keyword identifier')
        KEYWORD_CONSTANT = ('kwrd_const', 'A keyword constant')
        KEYWORD_OPERATOR = ('kwrd_operator', 'A keyword operator')

        BUILTIN_FUNC = ('builtin_fct', 'Built-in function')
        BUILTIN_EXCEPTION = ('builtin_except', 'Built-in exception')

        OPERATOR_BINARY = ('boperators', 'Operators like plus, minus, divide, ...')
        OPERATOR_DUAL = ('doperators', 'Operators like "-" can be unary or binary operator ')

        DELIMITER = ('delim', 'Miscellaneous delimiters')
        DELIMITER_OPERATOR = ('delim_operator', 'Operators considered as delimiters in Python')
        DELIMITER_SEPARATOR = ('delim_separator', 'Separator like comma')
        DELIMITER_PARENTHESIS_OPEN = ('delim_parO', 'Parenthesis (open)')
        DELIMITER_PARENTHESIS_CLOSE = ('delim_parC', 'Parenthesis (close)')
        DELIMITER_BRACKET_OPEN = ('delim_brackO', 'Bracket (open)')
        DELIMITER_BRACKET_CLOSE = ('delim_brackC', 'Bracket (close)')
        DELIMITER_CURLYBRACE_OPEN = ('delim_curlbO', 'Curly brace (open)')
        DELIMITER_CURLYBRACE_CLOSE = ('delim_curlbC', 'Curly brace (close)')

        DECL_FUNC = ('function_decl', 'Declare a Function')
        DECL_CLASS = ('class_decl', 'Declare a Class')

        IDENTIFIER = ('identifier', 'An identifier')
        DECORATOR = ('decorator', 'A decorator')

        LINE_JOIN = ('linejoin', 'Line join')

    def __init__(self):
        """Initialise language & styles"""
        super(BPLanguageDefPython, self).__init__([
            # ---
            # https://docs.python.org/3.10/reference/lexical_analysis.html#string-and-bytes-literals
            #
            # Need to make distinction between all possibles string for syntax highlighting
            TokenizerRule(BPLanguageDefPython.ITokenType.BSTRING_LONG_S,
                          r'''(?:RB|Rb|rB|rb|BR|bR|Br|br|B|b)(?:'{3}(?:.|\s|\n)*?'{3})''',
                          multiLineStart=r"""(RB|Rb|rB|rb|BR|bR|Br|br|B|b)(?:'{3})""",
                          multiLineEnd=r"""(?:'{3})"""),
            TokenizerRule(BPLanguageDefPython.ITokenType.BSTRING_LONG_D,
                          r'''(?:RB|Rb|rB|rb|BR|bR|Br|br|B|b)(?:"{3}(?:.|\s|\n)*?"{3})''',
                          multiLineStart=r'''(RB|Rb|rB|rb|BR|bR|Br|br|B|b)(?:"{3})''',
                          multiLineEnd=r'''(?:"{3})'''),

            TokenizerRule(BPLanguageDefPython.ITokenType.FSTRING_LONG_S,
                          r'''(?:RF|Rf|rF|rf|FR|fR|Fr|fr|F|f)(?:'{3}(?:.|\s|\n)*?'{3})''',
                          multiLineStart=r"""(RF|Rf|rF|rf|FR|fR|Fr|fr|F|f)(?:'{3})""",
                          multiLineEnd=r"""(?:'{3})"""),
            TokenizerRule(BPLanguageDefPython.ITokenType.FSTRING_LONG_D,
                          r'''(?:RF|Rf|rF|rf|FR|fR|Fr|fr|F|f)(?:"{3}(?:.|\s|\n)*?"{3})''',
                          multiLineStart=r'''(RF|Rf|rF|rf|FR|fR|Fr|fr|F|f)(?:"{3})''',
                          multiLineEnd=r'''(?:"{3})'''),

            TokenizerRule(BPLanguageDefPython.ITokenType.STRING_LONG_S,
                          r'''(?:U|u|R|r)?(?:'{3}(?:.|\s|\n)*?'{3})''',
                          multiLineStart=r"""(U|u|R|r)?(?:'{3})""",
                          multiLineEnd=r"""(?:'{3})"""),
            TokenizerRule(BPLanguageDefPython.ITokenType.STRING_LONG_D,
                          r'''(?:U|u|R|r)?(?:"{3}(?:.|\s|\n)*?"{3})''',
                          multiLineStart=r'''(U|u|R|r)?(?:"{3})''',
                          multiLineEnd=r'''(?:"{3})'''),

            TokenizerRule(BPLanguageDefPython.ITokenType.BSTRING,
                          r'''(?:RB|Rb|rB|rb|BR|bR|Br|br|B|b)(?:(?:"(?:.?\\"|[^"])*(?:\.(?:\\"|[^"]*))*")|(?:'(?:.?\\'|[^'])*(?:\.(?:\\'|[^']*))*'))'''),
            TokenizerRule(BPLanguageDefPython.ITokenType.FSTRING,
                          r'''(?:RF|Rf|rF|rf|FR|fR|Fr|fr|F|f)(?:(?:"(?:.?\\"|[^"])*(?:\.(?:\\"|[^"]*))*")|(?:'(?:.?\\'|[^'])*(?:\.(?:\\'|[^']*))*'))'''),
            TokenizerRule(BPLanguageDefPython.ITokenType.STRING,
                          r'''(?:U|u|R|r)?(?:"(?:(?:.?\\"|[^"])*(?:\.(?:\\"|[^"]*))*")|(?:'(?:.?\\'|[^'])*(?:\.(?:\\'|[^']*))*'))'''),

            # ---
            #
            TokenizerRule(BPLanguageDefPython.ITokenType.COMMENT,  r'#[^\n]*'),

            # --
            # https://peps.python.org/pep-0318/
            TokenizerRule(BPLanguageDefPython.ITokenType.DECORATOR,
                          r"(?:@[a-z_][a-z0-9_]*)\b",
                          caseInsensitive=True),

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
                          caseInsensitive=False),
            TokenizerRule(BPLanguageDefPython.ITokenType.KEYWORD_OPERATOR,
                          r"\b(?:and|in|is|or|not)\b",
                          caseInsensitive=False),

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
                          caseInsensitive=False),

            # --
            # https://docs.python.org/3.10/library/exceptions.html
            TokenizerRule(BPLanguageDefPython.ITokenType.BUILTIN_EXCEPTION,
                          r"\b(?:"
                          r"ZeroDivisionError|"
                          r"Warning|"
                          r"ValueError|"
                          r"UserWarning|UnicodeWarning|UnicodeTranslateError|UnicodeError|UnicodeEncodeError|UnicodeDecodeError|UnboundLocalError|"
                          r"TypeError|TimeoutError|TabError|"
                          r"SystemExit|SystemError|SyntaxWarning|SyntaxError|StopIteration|StopAsyncIteration|"
                          r"RuntimeWarning|RuntimeError|ResourceWarning|ReferenceError|RecursionError|"
                          r"ProcessLookupError|PermissionError|PendingDeprecationWarning|"
                          r"OverflowError|OSError|"
                          r"NotImplementedError|NotADirectoryError|NameError|"
                          r"ModuleNotFoundError|MemoryError|"
                          r"LookupError|"
                          r"KeyboardInterrupt|KeyError|"
                          r"IsADirectoryError|InterruptedError|IndexError|IndentationError|ImportWarning|ImportError|"
                          r"GeneratorExit|"
                          r"FutureWarning|FloatingPointError|FileNotFoundError|FileExistsError|"
                          r"Exception|EncodingWarning|EOFError|"
                          r"DeprecationWarning|"
                          r"ConnectionResetError|ConnectionRefusedError|ConnectionError|ConnectionAbortedError|ChildProcessError|"
                          r"BytesWarning|BufferError|BrokenPipeError|BlockingIOError|BaseException|"
                          r"AttributeError|AssertionError|ArithmeticError"
                          r")\b",
                          caseInsensitive=False),

            # --
            # https://docs.python.org/3.10/library/constants.html
            TokenizerRule(BPLanguageDefPython.ITokenType.KEYWORD_CONSTANT,
                          r"\b(?:Ellipsis|False|None|True|NotImplemented)\b",
                          caseInsensitive=False),

            # ---
            # https://docs.python.org/3.10/reference/lexical_analysis.html#soft-keywords
            TokenizerRule(BPLanguageDefPython.ITokenType.KEYWORD_SOFT,
                          r"\b(?:case|match|_)\b",
                          caseInsensitive=False),

            # ---
            # https://docs.python.org/3.10/reference/lexical_analysis.html#floating-point-literals (+Imaginary literals)
            TokenizerRule(BPLanguageDefPython.ITokenType.NUMBER_FLT,
                          r"\b(?:(?:\d(?:_?\d)*\.|\.)(?:\d(?:_?\d)*)?(?:e[+-]?\d(?:_?\d)*)?|[1-9]\d*(?:e[+-]?\d(?:_?\d)*))j?\b",
                          caseInsensitive=True),

            # ---
            # https://docs.python.org/3.10/reference/lexical_analysis.html#integer-literals (+Imaginary literals)
            TokenizerRule(BPLanguageDefPython.ITokenType.NUMBER_INT,
                          r"\b(?:[1-9](?:_?\d+)*|0o(?:_?[0-7]+)*|0b(?:_?[01]+)*|0x(?:_?[0-9A-F]+)*|0+)j?\b",
                          caseInsensitive=True),

            # ---
            TokenizerRule(BPLanguageDefPython.ITokenType.DECL_FUNC,
                          r"(?<=def\s+)(?:[a-z_][a-z0-9_]*)(?=\s*\()",
                          caseInsensitive=True),
            TokenizerRule(BPLanguageDefPython.ITokenType.DECL_CLASS,
                          r"(?<=class\s+)(?:[a-zA-Z_][a-zA-Z0-9_]*)(?=\s*[\(:])",
                          caseInsensitive=True),

            # --
            # https://docs.python.org/3.10/reference/lexical_analysis.html#identifiers
            TokenizerRule(BPLanguageDefPython.ITokenType.IDENTIFIER,
                          r"\b(?:[a-zA-Z_][a-zA-Z0-9_]*)\b",
                          caseInsensitive=False),

            # ---
            TokenizerRule(BPLanguageDefPython.ITokenType.LINE_JOIN, r"\s\\$"),

            # ---
            # https://docs.python.org/3.10/reference/lexical_analysis.html#delimiters
            # => must be defined before Operators to let regex catch them properly
            TokenizerRule(BPLanguageDefPython.ITokenType.DELIMITER,
                          r"->"),

            TokenizerRule(BPLanguageDefPython.ITokenType.DELIMITER_OPERATOR,
                          r"(?:\+=|-=|\*\*=|\*=|//=|/=|%=|@=\@|&=|\|=|\^=|>>=|<<=|=)"),

            # ---
            # https://docs.python.org/3.10/reference/lexical_analysis.html#operators
            TokenizerRule(BPLanguageDefPython.ITokenType.OPERATOR_BINARY,
                          r"\+|\*\*|\*|//|/|%|<<|>>|&|\||\^|~|:=|<=|<>|<|>=|>|==|!=",
                          caseInsensitive=False,
                          ignoreIndent=True),

            TokenizerRule(BPLanguageDefPython.ITokenType.OPERATOR_DUAL,
                          r"-",
                          ignoreIndent=True),

            # ---
            # https://docs.python.org/3.10/reference/lexical_analysis.html#delimiters
            TokenizerRule(BPLanguageDefPython.ITokenType.DELIMITER_SEPARATOR,
                          r"[,;\.:]"),

            TokenizerRule(BPLanguageDefPython.ITokenType.DELIMITER_PARENTHESIS_OPEN,
                          r"\("),

            TokenizerRule(BPLanguageDefPython.ITokenType.DELIMITER_PARENTHESIS_CLOSE,
                          r"\)",
                          ignoreIndent=True),

            TokenizerRule(BPLanguageDefPython.ITokenType.DELIMITER_BRACKET_OPEN,
                          r"\["),

            TokenizerRule(BPLanguageDefPython.ITokenType.DELIMITER_BRACKET_CLOSE,
                          r"\]",
                          ignoreIndent=True),

            TokenizerRule(BPLanguageDefPython.ITokenType.DELIMITER_CURLYBRACE_OPEN,
                          r"\{"),

            TokenizerRule(BPLanguageDefPython.ITokenType.DELIMITER_CURLYBRACE_CLOSE,
                          r"\}",
                          ignoreIndent=True),

            # all spaces except line feed
            TokenizerRule(BPLanguageDefPython.ITokenType.SPACE,  r"(?:(?!\n)\s)+"),

            # line feed
            TokenizerRule(BPLanguageDefPython.ITokenType.NEWLINE,  r"(?:^\s*\r?\n|\r?\n?\s*\r?\n)+"),

            # Unknown --> everything else
            TokenizerRule(BPLanguageDefPython.ITokenType.UNKNOWN,  r"[^\s]+"),
            ],
            BPLanguageDefPython.ITokenType)

        self.tokenizer().setSimplifyTokenSpaces(True)
        self.tokenizer().setIndent(4)
        # print(self.tokenizer())

        self.setStyles(UITheme.DARK_THEME, [
            (BPLanguageDefPython.ITokenType.STRING, '#98c379', False, False),
            (BPLanguageDefPython.ITokenType.STRING_LONG_S, '#aed095', False, False),
            (BPLanguageDefPython.ITokenType.STRING_LONG_D, '#aed095', False, False),

            (BPLanguageDefPython.ITokenType.FSTRING, '#98c379', False, True),
            (BPLanguageDefPython.ITokenType.FSTRING_LONG_S, '#aed095', False, True),
            (BPLanguageDefPython.ITokenType.FSTRING_LONG_D, '#aed095', False, True),

            (BPLanguageDefPython.ITokenType.BSTRING, '#56b6c2', False, False),
            (BPLanguageDefPython.ITokenType.BSTRING_LONG_S, '#7cc6d0', False, False),
            (BPLanguageDefPython.ITokenType.BSTRING_LONG_D, '#7cc6d0', False, False),

            (BPLanguageDefPython.ITokenType.NUMBER_INT, '#c9986a', False, False),
            (BPLanguageDefPython.ITokenType.NUMBER_FLT, '#c9986a', False, False),

            (BPLanguageDefPython.ITokenType.KEYWORD, '#c678dd', True, False),
            (BPLanguageDefPython.ITokenType.KEYWORD_SOFT, '#c678dd', True, False),
            (BPLanguageDefPython.ITokenType.KEYWORD_CONSTANT, '#dd7892', True, False),
            (BPLanguageDefPython.ITokenType.KEYWORD_OPERATOR, '#ff99ff', True, False),

            (BPLanguageDefPython.ITokenType.BUILTIN_FUNC, '#80bfff', False, False),
            (BPLanguageDefPython.ITokenType.BUILTIN_EXCEPTION, '#e83030', True, False),

            (BPLanguageDefPython.ITokenType.OPERATOR_BINARY, '#ff99ff', False, False),
            (BPLanguageDefPython.ITokenType.OPERATOR_DUAL, '#ff99ff', False, False),

            (BPLanguageDefPython.ITokenType.DELIMITER, '#ff66d9', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_OPERATOR, '#ff99ff', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_SEPARATOR, '#ff66d9', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_PARENTHESIS_OPEN, '#ff66d9', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_PARENTHESIS_CLOSE, '#ff66d9', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_BRACKET_OPEN, '#ff66d9', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_BRACKET_CLOSE, '#ff66d9', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_CURLYBRACE_OPEN, '#ff66d9', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_CURLYBRACE_CLOSE, '#ff66d9', False, False),

            (BPLanguageDefPython.ITokenType.LINE_JOIN, '#ff66d9', True, False, '#FDFF9E'),

            (BPLanguageDefPython.ITokenType.DECL_FUNC, '#ffe066', True, False),
            (BPLanguageDefPython.ITokenType.DECL_CLASS, '#ffe066', True, False),

            (BPLanguageDefPython.ITokenType.IDENTIFIER, '#e6e6e6', False, False),
            (BPLanguageDefPython.ITokenType.DECORATOR, '#ffffe6', True, True),

            (BPLanguageDefPython.ITokenType.COMMENT, '#5c6370', False, True)
        ])
        self.setStyles(UITheme.LIGHT_THEME, [
            (BPLanguageDefPython.ITokenType.STRING, '#238800', False, False),
            (BPLanguageDefPython.ITokenType.STRING_LONG_S, '#5D8C00', False, False),
            (BPLanguageDefPython.ITokenType.STRING_LONG_D, '#5D8C00', False, False),

            (BPLanguageDefPython.ITokenType.FSTRING, '#238800', False, True),
            (BPLanguageDefPython.ITokenType.FSTRING_LONG_S, '#5D8C00', False, True),
            (BPLanguageDefPython.ITokenType.FSTRING_LONG_D, '#5D8C00', False, True),

            (BPLanguageDefPython.ITokenType.BSTRING, '#008878', False, False),
            (BPLanguageDefPython.ITokenType.BSTRING_LONG_S, '#00B5A0', False, False),
            (BPLanguageDefPython.ITokenType.BSTRING_LONG_D, '#00B5A0', False, False),

            (BPLanguageDefPython.ITokenType.NUMBER_INT, '#D97814', False, False),
            (BPLanguageDefPython.ITokenType.NUMBER_FLT, '#D97814', False, False),

            (BPLanguageDefPython.ITokenType.KEYWORD, '#9B0F83', True, False),
            (BPLanguageDefPython.ITokenType.KEYWORD_SOFT, '#9B0F83', True, False),
            (BPLanguageDefPython.ITokenType.KEYWORD_CONSTANT, '#CC427B', True, False),
            (BPLanguageDefPython.ITokenType.KEYWORD_OPERATOR, '#DF0BEA', True, False),

            (BPLanguageDefPython.ITokenType.BUILTIN_FUNC, '#2677CC', True, False),
            (BPLanguageDefPython.ITokenType.BUILTIN_EXCEPTION, '#BF2727', True, False),

            (BPLanguageDefPython.ITokenType.OPERATOR_BINARY, '#DF0BEA', False, False),
            (BPLanguageDefPython.ITokenType.OPERATOR_DUAL, '#DF0BEA', False, False),

            (BPLanguageDefPython.ITokenType.DELIMITER, '#D953B5', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_OPERATOR, '#DF0BEA', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_SEPARATOR, '#D953B5', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_PARENTHESIS_OPEN, '#D953B5', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_PARENTHESIS_CLOSE, '#D953B5', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_BRACKET_OPEN, '#D953B5', False, False),
            (BPLanguageDefPython.ITokenType.DELIMITER_BRACKET_CLOSE, '#D953B5', False, False),

            (BPLanguageDefPython.ITokenType.LINE_JOIN, '#D953B5', False, False, '#FDFF9E'),

            (BPLanguageDefPython.ITokenType.DECL_FUNC, '#00019C', True, False),
            (BPLanguageDefPython.ITokenType.DECL_CLASS, '#00019C', True, False),

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


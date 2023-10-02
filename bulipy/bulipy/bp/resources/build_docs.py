#!/usr/bin/python3

# ---------- how to use ----------
# . pre-requisite
#   1) Need GIT
#   2) Need krita source code
#           ```
#           cd /home/xxxx
#           git clone git@invent.kde.org:graphics/krita.git
#           ```
#      Then assuming now source code is available in directory /home/xxxx/krita
#
# . build docs
#   1) Go in ./bulipy/bp/resources directory
#   2) Execute script
#           ```
#           ./build_docs.py -kritaSrc "/home/xxxx/krita"
#           ```
#

import sys
import os
import re
import argparse
import subprocess
import json
import hashlib
import textwrap

from PyQt5.QtGui import (QTextDocument, QTextCursor)

try:
    # add plugin path to python sys.path to let pktk modules being loaded
    pluginPath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(pluginPath)
except Exception:
    pass


from pktk.modules.languagedef import LanguageDef
from pktk.modules.tokenizer import (Tokenizer, TokenizerRule, Token, Tokens, TokenType)
from pktk.modules.uitheme import UITheme


class LanguageDefCpp(LanguageDef):
    # Define token types for C++ header
    # Not a complete c++ language definition, a subset normally enough to parse headers
    # and get interesting information

    class ITokenType(TokenType):
        STRING = ('str', 'A String value')
        COMMENT = ('comment', 'A comment line')
        COMMENT_BLOCK = ('comments', 'A comment block')
        DELIMITER_SEPARATOR = ('delim_separator', 'Separator like comma')
        DELIMITER_OPERATOR = ('delim_operator', 'Operator like comma')
        DELIMITER_PARENTHESIS_OPEN = ('delim_parO', 'Parenthesis (open)')
        DELIMITER_PARENTHESIS_CLOSE = ('delim_parC', 'Parenthesis (close)')
        DELIMITER_CURLYBRACE_OPEN = ('delim_curbO', 'Curly Brace (open)')
        DELIMITER_CURLYBRACE_CLOSE = ('delim_curbC', 'Curly Brace (close)')
        IGNORED = ('ignore_operator', 'Ignored token')

        IDENTIFIER = ('identifier', 'An identifier')

    def __init__(self):
        """Initialise language & styles"""
        super(LanguageDefCpp, self).__init__([
            # ---
            TokenizerRule(LanguageDefCpp.ITokenType.STRING,
                          r'''(?:"(?:(?:.?\\"|[^"])*(?:\.(?:\\"|[^"]*))*")|(?:'(?:.?\\'|[^'])*(?:\.(?:\\'|[^']*))*'))'''),

            TokenizerRule(LanguageDefCpp.ITokenType.COMMENT_BLOCK,  r'(?:/\*(?:.|\s|\n)*?\*/)'),
            TokenizerRule(LanguageDefCpp.ITokenType.COMMENT,  r'//[^\n]*'),


            TokenizerRule(LanguageDefCpp.ITokenType.IDENTIFIER,
                          r"QList<[^>]+>|QMap<[^>]+>",
                          caseInsensitive=False),

            TokenizerRule(LanguageDefCpp.ITokenType.IGNORED,
                          r"^\s*~[^;]+;|^\s*explicit[^;]*;|#[^\n]*$|[\*\-&~]|const|override|Q_SLOTS"),

            TokenizerRule(LanguageDefCpp.ITokenType.IDENTIFIER,
                          r"\d+|\b(?:[a-zA-Z_][a-zA-Z0-9_]*)(?:\<(?:[a-zA-Z_][a-zA-Z0-9_]*\*?)(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*\*?)*\>)?",
                          caseInsensitive=False),

            TokenizerRule(LanguageDefCpp.ITokenType.DELIMITER_OPERATOR,
                          r"="),

            TokenizerRule(LanguageDefCpp.ITokenType.DELIMITER_SEPARATOR,
                          r"[,:;]"),

            TokenizerRule(LanguageDefCpp.ITokenType.DELIMITER_PARENTHESIS_OPEN,
                          r"\("),

            TokenizerRule(LanguageDefCpp.ITokenType.DELIMITER_PARENTHESIS_CLOSE,
                          r"\)",
                          ignoreIndent=True),

            TokenizerRule(LanguageDefCpp.ITokenType.DELIMITER_CURLYBRACE_OPEN,
                          r"\{"),

            TokenizerRule(LanguageDefCpp.ITokenType.DELIMITER_CURLYBRACE_CLOSE,
                          r"\}",
                          ignoreIndent=True),

            TokenizerRule(LanguageDefCpp.ITokenType.SPACE,  r"(?:(?!\n)\s)+"),

            TokenizerRule(LanguageDefCpp.ITokenType.NEWLINE,  r"(?:^\s*\r?\n|\r?\n?\s*\r?\n)+")

            ],
            LanguageDefCpp.ITokenType
        )
        # print(self.tokenizer())

    def name(self):
        """Return language name"""
        return "Header C++"

    def extensions(self):
        """Return language file extension as list"""
        return ['.h']


class BPLanguageDefPython(LanguageDef):
    # define token types
    # ---> COPIED FROM pblanguagedef.py
    #      ImportError: attempted relative import beyond top-level package blahblahblah

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


class KritaApiMethod:

    @staticmethod
    def toPythonType(value):
        """Return matching python type for C++ type"""
        # normalize value
        nValue = re.sub(r"[\*\s]+", "", value)

        if nValue in ('string', 'char', 'QString'):
            return 'str'
        elif nValue in ('double', 'qreal', 'float'):
            return 'float'
        elif nValue in 'QStringList':
            return 'list[str]'
        elif matched := re.search(r'^(?:QList|QVector)<(.*)>$', nValue):
            return f"list[{KritaApiMethod.toPythonType(matched.groups()[0])}]"
        elif matched := re.search(r'^QMap<(.*),(.*)>$', nValue):
            k = KritaApiMethod.toPythonType(matched.groups()[0])
            v = KritaApiMethod.toPythonType(matched.groups()[1])
            return f"dict[{k}: {v}]"

        return value

    def __init__(self):
        self.__name = ''
        self.__returned = ''
        self.__description = ''
        self.__line = 0
        self.__access = ''
        self.__static = False
        self.__virtual = False
        self.__signal = False
        self.__parameters = []

    def __repr__(self):
        returned = f"{self.__name}({', '.join([p[0] for p in self.__parameters])}) -> {self.__returned}"
        return returned

    def toDict(self):
        """Return dict for method"""
        returned = {
                'hash': '',
                'name': self.__name,
                'description': self.__description,
                'returned': self.__returned,
                'sourceCodeLine': self.__line,
                'accesType': self.__access,
                'isStatic': self.__static,
                'isVirtual': self.__virtual,
                'isSignal': self.__signal,
                'parameters': [],
                'tagRef': {
                        'available': [],
                        'updated': []
                    }
            }

        for parameter in self.__parameters:
            returned['parameters'].append({
                    'name': parameter[0],
                    'type': parameter[1],
                    'default': parameter[2]
                })

        # calculate hash for given method
        m = hashlib.sha256()
        for property in ['name', 'description', 'returned', 'accesType', 'isStatic', 'isVirtual']:
            m.update(f"{returned[property]}".encode())
        for parameter in returned['parameters']:
            for property in ['name', 'type', 'default']:
                m.update(f"{parameter[property]}".encode())
        returned['hash'] = m.hexdigest()

        return returned

    def returned(self):
        return self.__returned

    def setReturned(self, value):
        self.__returned = KritaApiMethod.toPythonType(value)

    def name(self):
        return self.__name

    def setName(self, value):
        self.__name = value

    def line(self):
        return self.__line

    def setLine(self, value):
        self.__line = value

    def description(self):
        return self.__description

    def setDescription(self, description):
        self.__description = description

    def parameters(self):
        return self.__parameters

    def addParameter(self, name, type, default):
        if name is not None and type is not None:
            if isinstance(default, str):
                if g := re.match(r'''QString\(["'](.*)["']\)''', default):
                    default = f'"{g.groups()[0]}"'
                elif g := re.match(r'''QString\(\s*\)''', default):
                    default = f'""'
                elif default == '0':
                    if KritaApiMethod.toPythonType(type) != 'int':
                        default = 'None'
                elif default == 'true':
                    default = 'True'
                elif default == 'false':
                    default = 'False'
            self.__parameters.append((name, KritaApiMethod.toPythonType(type), default))

    def access(self):
        return self.__access

    def setAccess(self, value):
        self.__access = value

    def static(self):
        return self.__static

    def setStatic(self, value):
        self.__static = value

    def virtual(self):
        return self.__virtual

    def setVirtual(self, value):
        self.__virtual = value

    def signal(self):
        return self.__signal

    def setSignal(self, value):
        self.__signal = value


class KritaApiClass:

    def __init__(self, fileName):
        self.__fileName = fileName
        self.__name = ""
        self.__description = ""
        self.__extend = ""
        self.__line = 0
        self.__methods = []

    def toDict(self):
        """Return dict for class"""
        returned = {
                'fileName': self.__fileName,
                'name': self.__name,
                'description': self.__description,
                'extend': self.__extend,
                'sourceCodeLine': self.__line,
                'methods': [method.toDict() for method in self.__methods],
                'tagRef': {
                        'available': [],
                        'updated': []
                    }
            }
        return returned

    def name(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def extend(self):
        return self.__extend

    def setExtend(self, extend):
        self.__extend = extend

    def description(self):
        return self.__description

    def setDescription(self, description):
        self.__description = description

    def methods(self):
        return self.__methods

    def addMethod(self, method):
        self.__methods.append(method)

    def line(self):
        return self.__line

    def setLine(self, value):
        self.__line = value


class KritaApiAnalysis:
    """Do an analysis of current source code"""

    def __init__(self, kritaSrcLibKisPath):
        self.__libkisPath = kritaSrcLibKisPath
        self.__headerFiles = sorted([fileName for fileName in os.listdir(self.__libkisPath) if re.search(r'\.h$', fileName) and fileName not in ('libkis.h', 'LibKisUtils.h')])

        self.__languageDef = LanguageDefCpp()
        self.__classes = {}
        self.__tokens = None

        # print(self.__headerFiles)
        totalKo = 0
        for fileName in self.__headerFiles:
            nbKo = self.__processFile(fileName)
            if nbKo:
                totalKo += 1

        if totalKo > 0:
            print(f"!!!! WARNING: invalid files({totalKo}/{len(self.__headerFiles)})!")

    def __reformatDescription(self, description):
        description = re.sub(r"^\s*(/\*\*.*|\*/|\*[ \t]|\*|///?\s)", "", description, flags=re.M)
        description = re.sub(r"^\n", "", description)
        return description

    def __moveNext(self):
        """Move to next non space/newline token"""
        while not self.__tokens.eol():
            nextToken = self.__tokens.next()
            if nextToken and nextToken.type() not in (LanguageDefCpp.ITokenType.IGNORED, LanguageDefCpp.ITokenType.SPACE, LanguageDefCpp.ITokenType.NEWLINE):
                return nextToken
        return None

    def __skipStatement(self):
        """Skip current statement: ignore all token until found separator ';' """
        while not self.__tokens.eol():
            token = self.__moveNext()
            if token and token.type() == LanguageDefCpp.ITokenType.DELIMITER_SEPARATOR and token.value() == ';':
                return

    def __nextToken(self, token):
        """Return next non space/newline token from given `token` or None"""
        if nextToken := token.next():
            if nextToken.type() in (LanguageDefCpp.ITokenType.IGNORED, LanguageDefCpp.ITokenType.SPACE, LanguageDefCpp.ITokenType.NEWLINE):
                return self.__nextToken(nextToken)
            return nextToken
        return None

    def __previousToken(self, token):
        """Return previous non space/newline token from given `token` or None"""
        if previousToken := token.previous():
            if previousToken.type() in (LanguageDefCpp.ITokenType.IGNORED, LanguageDefCpp.ITokenType.SPACE, LanguageDefCpp.ITokenType.NEWLINE):
                return self.__previousToken(previousToken)
            return previousToken
        return None

    def __processClass(self, fileName):
        """Current token from given `tokens` is start of a class

        manage class
        """
        def exitClass():
            countCBraces = None
            while not self.__tokens.eol():
                token = self.__tokens.next()
                if token:
                    if token.type() == LanguageDefCpp.ITokenType.DELIMITER_CURLYBRACE_OPEN:
                        if countCBraces is None:
                            countCBraces = 0
                        countCBraces += 1
                    elif token.type() == LanguageDefCpp.ITokenType.DELIMITER_CURLYBRACE_CLOSE:
                        countCBraces -= 1
                    elif countCBraces == 0 and token.type() == LanguageDefCpp.ITokenType.DELIMITER_SEPARATOR and token.value() == ';':
                        # exit class!
                        break

            if countCBraces is None or countCBraces > 0:
                # not a normal case but nothing to do except print a warning
                print("---> WARNING/0001: invalid class definition?")

        # normally, token preceding class is a comment to describe class
        tokenDescription = self.__previousToken(self.__tokens.value())
        if not tokenDescription or not tokenDescription.type() == LanguageDefCpp.ITokenType.COMMENT_BLOCK:
            tokenDescription = None

        classLineNumber = self.__tokens.value().row()

        # get next token
        token = self.__moveNext()
        if not token:
            print("---> WARNING/0002: invalid class definition?")
            print(token)
            # can occurs!?
            return False

        if token.value() != 'KRITALIBKIS_EXPORT':
            # we're not in 'valid' class to process, continue to parse until exit class
            nextToken = self.__nextToken(token)
            if nextToken.type() == LanguageDefCpp.ITokenType.DELIMITER_SEPARATOR and nextToken.value() == ';':
                # case of class like
                #   class Xxxxx;
                #
                # nothing to do, exit
                return

            # case of class like
            #   class Xxxxx : ... { ... };
            exitClass()
            return

        # from here we can consider the class should like:
        #   class KRITALIBKIS_EXPORT Xxxxx : public XXXXX { ... };

        # this token is class name
        token = self.__moveNext()

        # start to manage krita class
        kritaClass = KritaApiClass(fileName)
        kritaClass.setName(token.value())
        kritaClass.setLine(classLineNumber)
        if tokenDescription:
            kritaClass.setDescription(self.__reformatDescription(tokenDescription.value()))

        nextToken = self.__nextToken(token)
        if nextToken.type() == LanguageDefCpp.ITokenType.DELIMITER_SEPARATOR and nextToken.value() == ':':
            token = self.__moveNext()
            token = self.__moveNext()
            if token.value() != 'public':
                # if class is not public, need to exit...
                print("---> WARNING/0006: invalid class definition?")
                print(token)
                return False

            # this token define object from which class inherits
            token = self.__moveNext()
            kritaClass.setExtend(token.value())

        # enter in class
        # only declaration in public/public Q_SLOTS managed
        #   class KRITALIBKIS_EXPORT Xxxx : public QObject
        #       {
        #           Q_OBJECT
        #
        #           public:
        #               ....
        #
        #           public Q_SLOTS:
        #               ....
        #
        #           private:
        #               ....
        #       };
        #   Note: consider to enter class if curly brace count is greater than 0
        kritaMethod = None
        methodName = None
        methodComment = None
        methodReturned = None
        methodVirtual = None
        methodStatic = None
        methodAccess = None
        countCBraces = None
        asSignal = False
        while not self.__tokens.eol():
            token = self.__moveNext()
            if not token:
                break

            if token.type() == LanguageDefCpp.ITokenType.DELIMITER_CURLYBRACE_OPEN:
                if countCBraces is None:
                    countCBraces = 0
                countCBraces += 1
            elif token.type() == LanguageDefCpp.ITokenType.DELIMITER_CURLYBRACE_CLOSE:
                countCBraces -= 1
            elif countCBraces == 0 and token.type() == LanguageDefCpp.ITokenType.DELIMITER_SEPARATOR and token.value() == ';':
                # exit class!
                break
            elif token.value() in ('public', 'protected'):
                asSignal = False
                nextToken = self.__nextToken(token)
                if nextToken.type() == LanguageDefCpp.ITokenType.DELIMITER_SEPARATOR and nextToken.value() == ':':
                    nextToken = self.__nextToken(nextToken)
                    if nextToken.type() in (LanguageDefCpp.ITokenType.COMMENT, LanguageDefCpp.ITokenType.COMMENT_BLOCK) and re.search(r"\bkrita\s+api", nextToken.value(), flags=re.I):
                        methodAccess = 'private'
                        # skip comment
                        self.__moveNext()
                    else:
                        methodAccess = token.value()
                        # skip :
                        self.__moveNext()
                        if nextToken.type() in (LanguageDefCpp.ITokenType.COMMENT, LanguageDefCpp.ITokenType.COMMENT_BLOCK) and re.search(r"krita\s+api", nextToken.value(), flags=re.I):
                            self.__moveNext()

            elif token.value() == 'private':
                asSignal = False
                nextToken = self.__nextToken(token)
                if nextToken.type() == LanguageDefCpp.ITokenType.DELIMITER_SEPARATOR and nextToken.value() == ':':
                    methodAccess = 'private'
                    # skip :
                    self.__moveNext()
            elif token.value() == 'Q_SIGNALS':
                nextToken = self.__nextToken(token)
                if nextToken.type() == LanguageDefCpp.ITokenType.DELIMITER_SEPARATOR and nextToken.value() == ':':
                    asSignal = True
                    # skip :
                    self.__moveNext()
            elif methodAccess in ('public', 'protected'):
                # analyse token only if in public Q_SLOT
                # should be a method declaration maybe preceded by a comment
                # examples:
                #   QList<Node*> childNodes() const;
                #   QList<Node*> findChildNodes(const QString &name = QString(), bool recursive = false, bool partialMatch = false, const QString &type = QString(), int colorLabelIndex = 0) const;
                #   bool setPixelData(QByteArray value, int x, int y, int w, int h);
                #   virtual void canvasChanged(Canvas *canvas) = 0;
                if token.type() in (LanguageDefCpp.ITokenType.COMMENT_BLOCK, LanguageDefCpp.ITokenType.COMMENT):
                    # memorize comment
                    methodComment = self.__reformatDescription(token.value())
                else:
                    methodVirtual = False
                    if token.value() == 'virtual':
                        methodVirtual = True
                        token = self.__moveNext()

                    methodStatic = False
                    if token.value() == 'static':
                        methodStatic = True
                        token = self.__moveNext()

                    nextToken = self.__nextToken(token)
                    if nextToken:
                        if nextToken.type() == LanguageDefCpp.ITokenType.DELIMITER_PARENTHESIS_OPEN:
                            # constructor
                            methodReturned = token
                            methodName = token
                        elif nextToken.value() == 'operator':
                            # something like
                            #   bool operator==(const Canvas &other) const;
                            self.__skipStatement()
                            continue
                        else:
                            methodReturned = token
                            methodName = self.__moveNext()
                    else:
                        continue

                    kritaMethod = KritaApiMethod()
                    kritaMethod.setName(methodName.value())
                    kritaMethod.setReturned(methodReturned.value())
                    kritaMethod.setAccess(methodAccess)
                    kritaMethod.setLine(methodName.row())
                    kritaMethod.setStatic(methodStatic)
                    kritaMethod.setVirtual(methodVirtual)
                    kritaMethod.setSignal(asSignal)
                    if methodComment:
                        kritaMethod.setDescription(methodComment)

                    token = self.__moveNext()
                    if not(token and token.type() == LanguageDefCpp.ITokenType.DELIMITER_PARENTHESIS_OPEN):
                        # !!??
                        print("---> WARNING/0003: invalid class definition?")
                        print(kritaMethod)
                        print(token)
                        return False

                    parametersOk = True
                    parameterType = None
                    parameterName = None
                    parameterDefault = None
                    # we are managing method parameters
                    while not self.__tokens.eol():
                        token = self.__moveNext()
                        if token:
                            if token.type() == LanguageDefCpp.ITokenType.DELIMITER_PARENTHESIS_CLOSE:
                                # no more parameters, add method to class
                                kritaMethod.addParameter(parameterName, parameterType, parameterDefault)

                                if parametersOk and re.match("^K(is|o).*", methodReturned.value()) is None:
                                    # KisXxxxx and KoXxxxx class are internal Krita classe not available in PyKrita API
                                    # then exclude it from available method
                                    kritaClass.addMethod(kritaMethod)

                                kritaMethod = None
                                methodName = None
                                methodComment = None
                                methodReturned = None
                                methodStatic = None
                                methodVirtual = None
                                parameterType = None
                                parameterName = None
                                parameterDefault = None
                            elif token.type() == LanguageDefCpp.ITokenType.DELIMITER_SEPARATOR and token.value() == ';':
                                # end of method definition
                                break
                            elif token.type() == LanguageDefCpp.ITokenType.DELIMITER_SEPARATOR and token.value() == ',':
                                # add parameter
                                kritaMethod.addParameter(parameterName, parameterType, parameterDefault)

                                parameterType = None
                                parameterName = None
                                parameterDefault = None
                            elif kritaMethod and token.type() == LanguageDefCpp.ITokenType.DELIMITER_OPERATOR and token.value() == '=':
                                # default value
                                token = self.__moveNext()
                                parameterDefault = token.value()

                                pOpen = 0
                                while True:
                                    nextToken = self.__nextToken(token)

                                    if nextToken.value() == '(':
                                        pOpen += 1
                                    elif nextToken.value() == ')':
                                        if pOpen == 0:
                                            break
                                        else:
                                            pOpen -= 1
                                    elif nextToken.value() == ',':
                                        if pOpen == 0:
                                            break

                                    parameterDefault += nextToken.value()
                                    token = self.__moveNext()
                            else:
                                if parameterType is None:
                                    parameterType = token.value()
                                    if re.match("^K(is|o).*", parameterType) is not None:
                                        # KisXxxxx and KoXxxxx class are internal Krita classe not available in PyKrita API
                                        # then exclude it from available method
                                        parametersOk = False
                                elif parameterName is None:
                                    parameterName = token.value()

                    if kritaMethod is not None:
                        # !!??
                        print("---> WARNING/0004: invalid class definition?")
                        print(token)
                        print(kritaMethod)
                        return False

        if countCBraces is None or countCBraces > 0:
            # not a normal case but nothing to do except print a warning?
            # at least do not add class in class list...
            print("---> WARNING/0005: invalid class definition?")
            print(countCBraces)
            return False

        self.__classes[kritaClass.name()] = kritaClass

        return True

    def __processFile(self, fileName):
        fullFileName = os.path.join(self.__libkisPath, fileName)
        with open(fullFileName, 'r') as fHandle:
            content = ''.join(fHandle.readlines())

        # print(content)

        self.__tokens = self.__languageDef.tokenizer().tokenize(content)

        nbKo = 0
        while token := self.__tokens.next():
            if token.value() == 'class':
                # entering a class, process it
                if self.__processClass(fileName) is False:
                    nbKo += 1
        if nbKo:
            print(f"---- Processed file: {fileName}")
            print(f"     ==> KO!")

        return nbKo

    def classes(self):
        """Return krita classes"""
        return self.__classes


class KritaBuildDoc:

    __cssContent = """
        :root {
            --blue: #007bff;
            --indigo: #6610f2;
            --purple: #6f42c1;
            --pink: #e83e8c;
            --red: #dc3545;
            --orange: #fd7e14;
            --yellow: #ffc107;
            --green: #28a745;
            --teal: #20c997;
            --cyan: #17a2b8;
            --white: #fff;
            --gray: #bdc3c7;
            --gray-dark: #343a40;
            --primary: #54a3d8;
            --secondary: #bdc3c7;
            --success: #28a745;
            --info: #17a2b8;
            --warning: #ffc107;
            --danger: #dc3545;
            --light: #f8f9fa;
            --dark: #343a40;

            --body-color: #eff0f1;
            --body-bg: #232629;
            --border-color: #16181b;
        }

        body {
            color: var(--body-color);
            background-color: var(--body-bg);
            font-family: sans-serif;
        }

        body.index {
            margin: 0;
        }

        body.class {
            margin: 0.5em;
        }

        a {
            text-decoration: none;
            color: var(--primary);
        }

        a:visited {
            color: var(--orange);
        }

        body h1:first-child {
            margin-top: 0;
        }

        h1, h2, h3 {
            background-color: rgba(255,255,255,0.125);
            padding: 0.15em 0.25em;
            border-radius: 0.1em;
        }

        div.methodList span.methodList:first-child {
            border-top: 1px dotted rgba(128,128,128,0.25);
        }
        div.methodList span.methodList {
            display: block;
            margin-left: 1em;
            line-height: 1.5em;
            border-bottom: 1px dotted rgba(128,128,128,0.25);
            font-family: monospace;
        }
        div.methodList span.methodList:hover {
            background-color: var(--dark);
        }

        .className {
            font-weight: bold;
            font-family: monospace;
        }
        .buildFrom a {
            font-family: monospace;
        }
        .docRefTags {
            padding: 0.15em;
        }
        .refTag::after {
            content: "\a";
            white-space: pre;
        }
        .refTag {
            background-color: rgba(84, 163, 216, 0.25);
            font-size: 85%;
            border-radius: 0.2em;
            margin-right: 0.25em;
            overflow: hidden;
            display: inline-block;
            line-height: 1.5em;
        }
        .refTag .refTagTag {
            font-weight: bold;
            padding: 0.15em 0.35em;
        }
        .refTag .refTagSymbol {
            padding: 0.15em;
            background: rgba(84, 163, 216, 0.5);
        }
        .methodDef {
            margin-left: 1em;
            background-color: rgba(128,128,128,0.05);
            margin-bottom: 2em;
            border-radius: 0.15em;
            overflow: hidden;
        }
        .methodDef:hover {
            background-color: rgba(255,255,255,0.05);
        }
        .methodDef .def {
            font-family: monospace;
            font-size: 110%;
            background-color: rgba(255,255,255,0.075);
            padding: 0.15em;
        }
        .methodSep {
            color: var(--pink);
        }
        .methodParameterType {
            color: var(--teal);
        }
        .methodParameterDefault {
            color: var(--cyan);
        }
        .methodParamName {
            color: var(--gray);
        }
        .rightTag::after {
            float: right;
            display: block;
            font-size: 70%;
            padding: 0.15em;
            border-radius: 0.15em;
            line-height: 1em;
            margin: 2px 2px 2px 0px;
        }
        .rightTag.isStatic::after {
            background-color: var(--green);
            content: "Static";
        }
        .rightTag.isSignal::after {
            background-color: var(--pink);
            content: "Signal";
        }
        .rightTag.isVirtual::after {
            background-color: var(--blue);
            content: "Virtual";
        }
        .docString {
            padding: 0.5em 0.5em 0.5em 2em;
        }
        .docString p {
            margin: 0;
        }
        .docString p + p,
        .docString p + h3,
        .docString table + h3 {
            margin-top: 0.5em;
        }
        .docString h3 {
            margin: 0;
            max-width: 150px;
            background-color: rgba(128,128,128,0.1);
        }
        .docString ul {
            margin-top: 0.25em;
            margin-bottom: 0.25em;
        }
        table.paramList {
            border: 1px solid rgba(128,128,128,0.1);
            width: 100%;
            border-collapse: collapse;
        }
        table.paramList tr {
            border-bottom: 1px dotted rgba(128,128,128,0.25);
            vertical-align: top;
        }
        table td.paramName {
            font-family: monospace;
            width: 250px;
        }

        .noDescriptionProvided {
            font-style: italic;
            opacity: 0.35;
        }

        .code {
            font-family: mono;
            border: 2px dashed rgba(128,128,128,0.45);
            padding: 0.5em;
            margin: 0.5em 0;
        }
        .code p {
            white-space: pre;
        }

        .leftMenu {
            display: inline-block;
            position: absolute;
            width: 16vw;
            background: var(--dark);
            height: 100vh;
        }
        .leftMenu ul {
            padding: 0 1.25em;
            margin: 0.25em 0;
        }
        .leftMenu ul li {
            list-style-type: disclosure-closed;
        }
        .frameContent {
            width: 84vw;
            height: 100vh;
            display: block;
            padding: 0;
            margin: 0 0 0 16vw;
            border: none;
        }
        .leftMenu h3 {
            margin: 0;
        }

        .bulipy {
            font-size: 65%;
            display: block;
            text-align: right;
            font-style: italic;
        }
    """

    def __init__(self, kritaSrcLibKisPath, pluginPathDocs, updateRepo, showTypes, buildPython, buildHtml):
        self.__updateRepo = updateRepo
        self.__showTypes = showTypes
        self.__buildPython = buildPython
        self.__buildHtml = buildHtml
        self.__kritaSrcLibKisPath = kritaSrcLibKisPath
        self.__kritaReferential = {
                'tags': {},
                'classes': {}
            }
        self.__jsonFile = os.path.join(pluginPathDocs, 'krita.json')

        if not self.__gitTags():
            return

        self.__updateGitRepository()
        self.__loadJson()
        self.__analyseSources()
        self.__saveJson()
        self.__buildPythonDoc()
        self.__buildHtmlDoc()
        self.__showFoundTypes()

    def __getTag(self, tagRef):
        """Return tag from given tag ref"""
        if tagRef in self.__kritaReferential['tags']:
            return self.__kritaReferential['tags'][tagRef]
        return None

    def __getTagName(self, tagRef):
        """Return normalized version of tag"""
        return f"{int(tagRef[0:2])}.{int(tagRef[2:4])}.{int(tagRef[4:6])}"

    def __loadJson(self):
        """Load Json documentation file"""
        if os.path.exists(self.__jsonFile):
            try:
                print("LOAD REFERENTIAL")
                with open(self.__jsonFile, 'r') as fHandle:
                    self.__kritaReferential = json.loads(fHandle.read())
            except Exception as e:
                print("Can't load referential, rebuild from scratch")
                print(e)

    def __saveJson(self):
        """Save Json documentation file"""
        try:
            print("SAVE REFERENTIAL")
            with open(self.__jsonFile, 'w') as fHandle:
                fHandle.write(json.dumps(self.__kritaReferential, indent=1, sort_keys=True))
        except Exception as e:
            print("ERROR: Can't save referential!")
            print(e)

    def __gitTags(self):
        """Get, filter & sort git tags to process

        Build self.__tagList:
            normalised krita version;tag name;commit hash

            example:
                005.001.006;5.1.6;6a72b3503238bdfbc72f903b41cc2c97064da469;2023-01-01
        """
        def fixVersion(reflog):
            values = reflog.split(';')
            values[0] = values[0].replace('v', '')
            return ''.join([f"{int(v):02}" for v in values[0].split('.')])

        def validVersion(reflog):
            if result := re.search(r"^v?(\d)\.\d+\.\d+;", reflog):
                if int(result.groups()[0]) >= 4:
                    return True
            return False

        def tagData(reflog):
            values = reflog.split(';')
            return {
                    'tag': values[1],
                    'hash': values[2],
                    'date': values[3],
                    'processed': False
                }

        try:
            cmdResult = subprocess.run(["git",
                                        "-C", self.__kritaSrcLibKisPath,
                                        "for-each-ref", '--format=%(refname:short);%(refname:short);%(objectname);%(creatordate:short)', "refs/tags"
                                        ],
                                       capture_output=True)
        except Exception as e:
            print("Unable to retrieve git tags", e)
            return False

        if cmdResult.returncode != 0:
            print("Unable to retrieve git tags")
            print(cmdResult.stderr.decode().split("\n"))
            return False

        for tag in cmdResult.stdout.decode().split("\n"):
            if validVersion(tag):
                fVersion = fixVersion(tag)
                if fVersion not in self.__kritaReferential['tags']:
                    self.__kritaReferential['tags'][fVersion] = tagData(tag)

        return True

    def __gitCheckout(self, hash):
        """Git checkout to hash
        Return True if checkout is OK, otherwise False
        """
        try:
            cmdResult = subprocess.run(["git",
                                        "-C", self.__kritaSrcLibKisPath,
                                        "checkout", hash], capture_output=True)
            # print(cmdResult)
            return True
        except Exception:
            return False

    def __updateGitRepository(self):
        if self.__updateRepo:
            print("UPDATE REPOSITORY")
            self.__gitCheckout('master')

            try:
                cmdResult = subprocess.run(["git",
                                            "-C", self.__kritaSrcLibKisPath,
                                            "pull",
                                            "--tags",
                                            "--all"], capture_output=True)
                # print(cmdResult)
                return True
            except Exception:
                return False

    def __updateClasses(self, tagRef, classNfo):
        """Update self.__kritaReferential classes"""
        name = classNfo['name']
        if name not in self.__kritaReferential['classes']:
            # class doesn't exist yet in referential, add it
            self.__kritaReferential['classes'][name] = classNfo
            self.__kritaReferential['classes'][name]['tagRef']['available'].append(tagRef)
            self.__kritaReferential['classes'][name]['tagRef']['updated'].append(tagRef)
            for updateMethod in self.__kritaReferential['classes'][name]['methods']:
                updateMethod['tagRef']['available'].append(tagRef)
                updateMethod['tagRef']['updated'].append(tagRef)
            return

        # ensure to get last version
        self.__kritaReferential['classes'][name]['extend'] = classNfo['extend']
        self.__kritaReferential['classes'][name]['description'] = classNfo['description']
        self.__kritaReferential['classes'][name]['sourceCodeLine'] = classNfo['sourceCodeLine']

        isUpdated = False
        currentMethods = self.__kritaReferential['classes'][name]['methods']
        for method in classNfo['methods']:
            found = False
            for updateMethod in self.__kritaReferential['classes'][name]['methods']:
                if updateMethod["name"] == method['name']:
                    found = True
                    updateMethod['tagRef']['available'].append(tagRef)
                    if updateMethod["hash"] != method['hash']:
                        # method has been modified
                        # get new one
                        for property in [k for k in method.keys() if k != 'tagRef']:
                            updateMethod[property] = method[property]

                        updateMethod['tagRef']['updated'].append(tagRef)
                    else:
                        updateMethod['sourceCodeLine'] = method['sourceCodeLine']

                if found:
                    break

            if found is False:
                self.__kritaReferential['classes'][name]['methods'].append(method)
                method['tagRef']['available'].append(tagRef)
                method['tagRef']['updated'].append(tagRef)
                isUpdated = True

        if isUpdated:
            self.__kritaReferential['classes'][name]['tagRef']['updated'].append(tagRef)

    def __analyseSources(self):
        """Loop over tags

        if tags hasn't been processed:
        - checkout tag
        - do analysis
        - store results
        """
        for tagRef in sorted(self.__kritaReferential['tags'].keys()):
            tag = self.__kritaReferential['tags'][tagRef]
            if tag['processed'] is False:
                print(f"PROCESS TAG: {tag['tag']} [{tag['hash']}]")
                if self.__gitCheckout(tag['hash']):
                    buildApiDoc = KritaApiAnalysis(kritaSrcLibKisPath)
                    for classNfo in [classNfo.toDict() for className, classNfo in buildApiDoc.classes().items()]:
                        self.__updateClasses(tagRef, classNfo)
                    tag['processed'] = True
                else:
                    print("             ==> Can't checkout!!!")

        # switch back to master branch
        self.__gitCheckout('master')

    def __showFoundTypes(self):
        if self.__showTypes:
            print("FOUND TYPES:")
            t = []
            for cName, c in self.__kritaReferential['classes'].items():
                for m in c['methods']:
                    t.append(m["returned"])
                    for p in m['parameters']:
                        t.append(p["type"])

            print('- ' + "\n- ".join(sorted(set(t))))

    def __buildPythonDoc(self):

        def formatMethod(methodNfo, className=None):
            # return formatted method string
            indent = ' ' * 4

            parameters = methodNfo["parameters"]
            description = methodNfo["description"].strip('\n')
            if description:
                description += "\n"

            implementedFrom = methodNfo["tagRef"]["available"][0]
            lastUpdatedFrom = methodNfo["tagRef"]["updated"][-1]

            if methodNfo['isVirtual']:
                description += "@Virtual\n"

            description += f"@Implemented with: {self.__getTagName(implementedFrom)}"
            if implementedFrom != lastUpdatedFrom:
                description += f"\n@Last updated with: {self.__getTagName(lastUpdatedFrom)}"

            returned = []
            if methodNfo['isSignal']:
                if description:
                    description = textwrap.indent(description, '# ')
                    returned.append(description)

                sigParam = ''
                if parameters:
                    sigParam = ", ".join([parameter['type'] for parameter in parameters])

                returned.append(f'{methodNfo["name"]} = pyqtSignal({sigParam})')
            else:
                if methodNfo['isStatic']:
                    returned.append('@staticmethod')
                    fctParam = []
                else:
                    fctParam = ['self']

                if parameters:
                    for parameter in parameters:
                        param = parameter['name']
                        if parameter['type']:
                            param = f"{param}: {parameter['type']}"
                        if parameter['default']:
                            param = f"{param} = {parameter['default']}"
                        fctParam.append(param)

                returnedType = ''
                if methodNfo["returned"] != 'void' and methodNfo["returned"] != className:
                    returnedType = f" -> {methodNfo['returned']}"

                if len(description.split("\n")) > 1:
                    description += "\n"

                returned.append(f'# Source location, line {methodNfo["sourceCodeLine"]}')
                returned.append(f'def {methodNfo["name"]}({", ".join(fctParam)}){returnedType}:')
                returned.append(textwrap.indent(f'"""{description}"""', indent))
                returned.append(f"{indent}pass")

            return "\n".join(returned)

        def formatClass(classNfo):
            # return formatted class string
            className = classNfo['name']
            indent = ' ' * 4
            returned = []

            returned.append(f"# Source")
            returned.append(f"# - File: {classNfo['fileName']}")
            returned.append(f"# - Line: {classNfo['sourceCodeLine']}")

            if classNfo['extend'] and re.search("^K(is|o).*", classNfo['extend']) is None:
                # do not extend Kis* and Ko* class as their not available in Pykrita API
                returned.append(f"class {className}({classNfo['extend']}):")
            else:
                returned.append(f"class {className}:")

            if classNfo['description']:
                description = classNfo["description"]

                implementedFrom = classNfo["tagRef"]["available"][0]
                lastUpdatedFrom = classNfo["tagRef"]["updated"][-1]

                description += f"\n@Implemented with: {self.__getTagName(implementedFrom)}\n"
                if implementedFrom != lastUpdatedFrom:
                    description += f"@Updated with: {self.__getTagName(lastUpdatedFrom)}\n"

                returned.append(textwrap.indent(f'"""{description}"""', indent))

            if classNfo['methods']:
                methodsSignal = []
                methodsStatic = []
                methods = []

                for methodNfo in sorted(classNfo['methods'], key=lambda x: x['name']):
                    if methodNfo['isSignal']:
                        methodsSignal.append(formatMethod(methodNfo))
                    elif methodNfo['isStatic']:
                        methodsStatic.append(formatMethod(methodNfo))
                    else:
                        methods.append(formatMethod(methodNfo, className))

                if methodsSignal:
                    returned.append(textwrap.indent("\n\n".join(methodsSignal), indent))

                if methodsStatic:
                    returned.append(textwrap.indent("\n\n".join(methodsStatic), indent))

                if methods:
                    returned.append(textwrap.indent("\n\n".join(methods), indent))
            else:
                returned.append(textwrap.indent('pass', indent))

            return "\n".join(returned)

        if self.__buildPython:
            print("BUILD PYTHON DOC")
            lastTagRef = sorted(self.__kritaReferential['tags'].keys())[-1]
            tag = self.__getTag(lastTagRef)
            fileContent = [f"# {'-' * 80}",
                           "# File generated from BuliPy/build_docs.py",
                           "# Can be used by IDE for auto-complete",
                           "# Build from header files from Krita's libkis source code folder",
                           "# ",
                           f"# Git tag:  {tag['tag']} ({tag['date']})",
                           f"# Git hash: {tag['hash']}",
                           f"# {'-' * 80}",
                           "",
                           "from PyQt5.Qt import *"
                           "",
                           "",
                           "# Declare empty classes to avoid inter-dependencies failure",
                           ]

            for className in sorted(self.__kritaReferential['classes'].keys()):
                fileContent.append(f"class {className}: pass")
            # tweak
            fileContent.append(f"class DockPosition: pass")

            for className in sorted(self.__kritaReferential['classes'].keys()):
                fileContent.append("")
                fileContent.append("")
                fileContent.append(formatClass(self.__kritaReferential['classes'][className]))

            pythonFile = os.path.join(pluginPathDocs, 'krita.py')
            try:
                with open(pythonFile, 'w') as fHandle:
                    fHandle.write("\n".join(fileContent))
            except Exception as e:
                print("ERROR: Can't save python file!")
                print(e)

    def __buildHtmlDoc(self):

        def codeToHtml(code):
            # return given code syntax highlighted
            languageDef = BPLanguageDefPython()
            tokens = languageDef.tokenizer().tokenize(code)

            textDocument = QTextDocument(code)
            cursor = QTextCursor(textDocument)

            tokens.resetIndex()
            while not (token := tokens.next()) is None:
                pStart = token.positionStart()
                cursor.setPosition(pStart, QTextCursor.MoveAnchor)
                cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, token.length())
                cursor.setCharFormat(languageDef.style(token))

            docHtml = textDocument.toHtml()
            docHtml = re.sub(r"^<!DOCTYPE.*<body[^>]*>(.*)</body></html>$", r"\1", docHtml, flags=re.I | re.S)
            return f"<div class='code'>{docHtml}</div>"

        def docMethodsList(methodType, classNfo):
            # format method list
            methodList = []

            for method in sorted(classNfo['methods'], key=lambda x: x['name']):
                if methodType == 'static' and method['isStatic'] or \
                   methodType == 'virtual' and method['isVirtual'] or \
                   methodType == 'signals' and method['isSignal'] or \
                   methodType == '' and not (method['isSignal'] or method['isVirtual'] or method['isStatic']):
                    methodList.append(method)

            if len(methodList) == 0:
                # nothing to return
                return ""

            # build method list
            returned = []
            for method in methodList:
                parameters = []
                for parameter in method['parameters']:
                    if method['isSignal']:
                        parameters.append(f"<span class='methodParameterType'>{parameter['type']}</span>")
                    else:
                        param = f"<span class='methodParamName'>{parameter['name']}</span>"
                        if parameter['type']:
                            param = f"{param}<span class='methodSep'>: </span><span class='methodParameterType'>{parameter['type']}</span>"
                        if parameter['default']:
                            param = f"{param}<span class='methodSep'> = </span><span class='methodParameterDefault'>{parameter['default']}</span>"
                        parameters.append(param)

                returnedType = ''
                if method["returned"] != 'void' and method["returned"] != className:
                    returnedType = f"<span class='methodSep'> &#10142; </span><span class='methodParameterType'>{method['returned']}</span>"

                returned.append(f"""<span class='methodList'>
                                        <a href='#{method['name']}'>
                                            <span class='methodName'>{method['name']}</span><span class='methodSep'>(</span>{'<span class="methodSep">, </span>'.join(parameters)}<span class='methodSep'>)</span>{returnedType}
                                        </a>
                                    </span>""")

            returned = '\n'.join(returned)

            if methodType == 'static':
                title = "Static methods"
            elif methodType == 'virtual':
                title = "Re-implemented methods"
            elif methodType == 'signals':
                title = "Signals"
            else:
                title = "Methods"

            return f"""<h2>{title}</h2>
                <div class='methodList'>
                    {returned}
                </div>
                """

        def docMethods(classNfo):
            # format methods
            returned = []
            for method in sorted(classNfo['methods'], key=lambda x: x['name']):
                parameters = []
                for parameter in method['parameters']:
                    if method['isSignal']:
                        parameters.append(f"<span class='methodParameterType'>{parameter['type']}</span>")
                    else:
                        param = f"<span class='methodParamName'>{parameter['name']}</span>"
                        if parameter['type']:
                            param = f"{param}<span class='methodSep'>: </span><span class='methodParameterType'>{parameter['type']}</span>"
                        if parameter['default']:
                            param = f"{param}<span class='methodSep'> = </span><span class='methodParameterDefault'>{parameter['default']}</span>"
                        parameters.append(param)

                returnedType = ''
                if method["returned"] != 'void' and method["returned"] != className:
                    returnedType = f"<span class='methodSep'> &#10142; </span><span class='methodParameterType'>{method['returned']}</span>"

                isVirtual = ""
                if method['isVirtual']:
                    isVirtual = "<span class='rightTag isVirtual'></span>"
                isStatic = ""
                if method['isStatic']:
                    isStatic = "<span class='rightTag isStatic'></span>"
                isSignal = ""
                if method['isSignal']:
                    isSignal = "<span class='rightTag isSignal'></span>"

                methodContent = f"""<div class='methodDef'>
                    <div class='def'>
                        <a class='className' id="{method['name']}">{method['name']}</a><span class='methodSep'>(</span>{'<span class="methodSep">, </span>'.join(parameters)}<span class='methodSep'>)</span>{returnedType}
                        {isVirtual}{isStatic}{isSignal}
                    </div>
                    <div class='docRefTags'>{formatRefTags(method["tagRef"])}</div>
                    <div class='docString'>
                        {formatDescription(method['description'], method)}
                    </div>
                </div>
                """
                returned.append(methodContent)

            returned = '\n'.join(returned)
            return returned

        def formatDescription(description, method=None):
            # reformat description for HTML
            # Recognized tags
            #  @brief
            #  @code - @endcode
            #  @param
            #  @return
            def fixLines(text):
                returned = re.sub(r"([^\s])\n([^\s])", r"\1 \2", text)
                returned = re.sub(r"^\n|\n$", "", returned)
                return returned

            def getCodeBlocks(text):
                returnedText = ''
                returnedBlocks = {}
                blocks = re.split("\x01", text)
                codeBlockNumber = 0
                for index in range(len(blocks)):
                    if index % 2 == 0:
                        returnedText += blocks[index]
                    else:
                        codeBlockNumber += 1
                        blockId = f"$codeBlock{codeBlockNumber}$"
                        returnedText += blockId
                        returnedBlocks[blockId] =  re.sub(r"^\n|\n$", "", blocks[index])
                return (returnedText, returnedBlocks)

            def asParagraph(text, codeBlocks):
                returned = []
                for line in text.split("\n"):
                    if blocks := re.findall(r"(\$codeBlock\d+\$)", line):
                        for block in blocks:
                            if block in codeBlocks:
                                line = line.replace(block, codeToHtml(codeBlocks[block]))

                    returned.append(f"<p>{line}</p>")
                return ''.join(returned)

            returnedNfo = {}

            if method:
                if len(method['parameters']):
                    returnedNfo['@param'] = {}
                if method['returned'] != 'void':
                    returnedNfo['@return'] = "<span class='noDescriptionProvided'>(no description provided)</span>"

            description = re.sub("^@@", "@", description, flags=re.I)
            description = re.sub("@code", "\x01", description, flags=re.I)
            description = re.sub("@endcode", "\x01", description, flags=re.I)
            description = re.sub(r"@[cp]\s", "", description, flags=re.I)
            description, codeBlocks = getCodeBlocks(description)
            splitted = re.split(r"^(@[a-z0-9]+\s)", description, flags=re.M | re.I)

            while len(splitted) and splitted[0].strip() == '':
                splitted.pop(0)

            if len(splitted) and re.search("^@", splitted[0]) is None:
                # a description without any tag?
                splitted.insert(0, "@brief")
                if method and {method['name']}:
                    splitted[1] = f"{method['name']} {splitted[1]}"

            index = 0
            while index < len(splitted):
                if splitted[index].strip() == '':
                    # expected a @xxx tag; skip empty lines
                    index += 1
                    continue

                docTag = splitted[index].lower().strip()
                docValue = splitted[index+1]

                if found := re.findall(r"(@param\s+[^\s]+)", docValue, flags=re.I):
                    for foundItem in found:
                        paramName = re.sub(r'@param\s+', '', foundItem, flags=re.I)
                        splitted.append('@param')
                        splitted.append(f"{paramName} ")
                        docValue = docValue.replace(foundItem, paramName)

                if docTag == '@brief':
                    if method and method['name']:
                        returnedNfo['@brief'] = fixLines(re.sub(fr"^{method['name']}\s+", "", docValue))
                    else:
                        returnedNfo['@brief'] = fixLines(docValue)
                elif docTag == '@param':
                    if '@param' not in returnedNfo:
                        returnedNfo['@param'] = {}

                    if nfo := re.search(r"^([a-z0-9_]+)\s+(.*)", docValue, flags=re.S | re.I):
                        paramName = nfo.groups()[0]
                        paramDescription = nfo.groups()[1]
                        if paramName not in returnedNfo['@param']:
                            if paramDescription == '':
                                paramDescription = '<span class="noDescriptionProvided">(no description provided)</span>'
                            returnedNfo['@param'][paramName] = fixLines(paramDescription)
                        else:
                            if returnedNfo['@param'][paramName] == '' and paramDescription != '':
                                returnedNfo['@param'][paramName] = fixLines(paramDescription)

                elif docTag in ('@return', '@returns'):
                    returnedNfo['@return'] = fixLines(docValue)
                else:
                    if method and method['name']:
                        print(f"WARNING: unknown docTag {docTag} in function {method['name']}")
                    else:
                        print(f"WARNING: unknown docTag {docTag}")

                index += 2

            if len(codeBlocks):
                returnedNfo['@code'] = codeBlocks
            else:
                returnedNfo['@code'] = []

            # order:
            # - brief
            # - param
            # - return

            returned = []

            if '@brief' in returnedNfo:
                returned.append(asParagraph(returnedNfo['@brief'], returnedNfo['@code']))

            if '@param' in returnedNfo:
                paramTableTr = []

                if method and len(method['parameters']):
                    # manage parameters in priority, using method parameters order
                    for parameter in method['parameters']:
                        parameterName = parameter['name']
                        if parameterName in returnedNfo['@param']:
                            paramTableTr.append(f"<tr><td class='paramName'><span class='methodParamName'>{parameterName}</span></td><td>{asParagraph(returnedNfo['@param'][parameterName], returnedNfo['@code'])}</td></tr>")
                        else:
                            paramTableTr.append(f"<tr><td class='paramName'><span class='methodParamName'>{parameterName}</span></td><td><span class='noDescriptionProvided'>(no description provided)</span></td></tr>")
                else:
                    for parameterName, parameterDescription in returnedNfo['@param'].items():
                        paramTableTr.append(f"<tr><td class='paramName'><span class='methodParamName'>{parameterName}</span></td><td>{asParagraph(parameterDescription, returnedNfo['@code'])}</td></tr>")

                returned.append(f"""<h3>Parameters</h3>
                    <table class='paramList'>
                        {''.join(paramTableTr)}
                    </table>
                    """)

            if '@return' in returnedNfo:
                returned.append(f"""<h3>Return</h3>
                    <table class='paramList'>
                        <tr><td>{asParagraph(returnedNfo['@return'], returnedNfo['@code'])}</td></tr>
                    </table>
                    """)

            return "\n".join(returned)

        def formatRefTags(refTags):
            # return ref tags: first Implemented, last updated
            implementedFrom = refTags["available"][0]
            lastUpdatedFrom = refTags["updated"][-1]

            returned = f"<span class='refTag' title='First implemented version'><span class='refTagSymbol'>&#65291;</span><span class='refTagTag'>Krita {self.__getTagName(implementedFrom)}</span></span>"
            if implementedFrom != lastUpdatedFrom:
                returned += f"<span class='refTag' title='Last updated version'><span class='refTagSymbol'>&#128472;</span><span class='refTagTag'>Krita {self.__getTagName(lastUpdatedFrom)}</span></span>"

            return returned

        def formatMethod(methodNfo, className=None):
            # return formatted method string
            indent = ' ' * 4

            parameters = methodNfo["parameters"]
            description = methodNfo["description"].strip('\n')
            if description:
                description += "\n"

            implementedFrom = methodNfo["tagRef"]["available"][0]
            lastUpdatedFrom = methodNfo["tagRef"]["updated"][-1]

            if methodNfo['isVirtual']:
                description += "@Virtual\n"

            description += f"@Implemented with: {self.__getTagName(implementedFrom)}"
            if implementedFrom != lastUpdatedFrom:
                description += f"\n@Last updated with: {self.__getTagName(lastUpdatedFrom)}"

            returned = []
            if methodNfo['isSignal']:
                if description:
                    description = textwrap.indent(description, '# ')
                    returned.append(description)

                sigParam = ''
                if parameters:
                    sigParam = ", ".join([parameter['type'] for parameter in parameters])

                returned.append(f'{methodNfo["name"]} = pyqtSignal({sigParam})')
            else:
                if methodNfo['isStatic']:
                    returned.append('@staticmethod')
                    fctParam = []
                else:
                    fctParam = ['self']

                if parameters:
                    for parameter in parameters:
                        param = parameter['name']
                        if parameter['type']:
                            param = f"{param}: {parameter['type']}"
                        if parameter['default']:
                            param = f"{param} = {parameter['default']}"
                        fctParam.append(param)

                returnedType = ''
                if methodNfo["returned"] != 'void' and methodNfo["returned"] != className:
                    returnedType = f" -> {methodNfo['returned']}"

                if len(description.split("\n")) > 1:
                    description += "\n"

                returned.append(f'# Source location, line {methodNfo["sourceCodeLine"]}')
                returned.append(f'def {methodNfo["name"]}({", ".join(fctParam)}){returnedType}:')
                returned.append(textwrap.indent(f'"""{description}"""', indent))
                returned.append(f"{indent}pass")

            return "\n".join(returned)

        def buildHtmlClass(classNfo, tag):
            # build html file for given class
            className = classNfo["name"]
            fileName = f'kritaDoc_Class-{classNfo["name"]}.html'

            fileContent = f"""<!DOCTYPE HTML>
            <html>
                <head>
                    <meta charset="utf-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                    <meta name="generator" content="BuliPy/build_docs.py"/>
                    <meta name="buildDoc:git:tagName" content="{tag['tag']}"/>
                    <meta name="buildDoc:git:tagDate" content="{tag['date']}"/>
                    <meta name="buildDoc:git:tagHash" content="{tag['hash']}"/>

                    <title>Krita {tag['nTagName']} API - Class {className}</title>
                    <style>{KritaBuildDoc.__cssContent}</style>
                </head>
                <body class='class'>
                    <h1>Class description - <span class='className'>{className}</span></h1>
                    <div class='buildFrom'>Build from <a target='_blank' href='https://invent.kde.org/graphics/krita/-/blob/{tag['hash']}/libs/libkis/{classNfo["fileName"]}'>{classNfo["fileName"]}</a></div>
                    <div class='docRefTags'>{formatRefTags(classNfo["tagRef"])}</div>
                    <div class='docString'>{formatDescription(classNfo["description"])}</div>
                    {docMethodsList('static', classNfo)}
                    {docMethodsList('', classNfo)}
                    {docMethodsList('virtual', classNfo)}
                    {docMethodsList('signals', classNfo)}
                    <h1>Member documentation</h1>
                    {docMethods(classNfo)}
                </body>
            </html>
            """

            # dedent
            fileContent = re.sub(r"^[ ]{12}", "", fileContent, flags=re.M)
            htmlFile = os.path.join(pluginPathDocs, fileName)
            try:
                with open(htmlFile, 'w') as fHandle:
                    fHandle.write(fileContent)
            except Exception as e:
                print(f"ERROR: Can't save html file: {fileName}")
                print(e)

        def buildHtmlIndex(classNfo, tag):
            # build html file for given class

            classList = []
            for className in sorted(classNfo.keys()):
                classList.append(f"<li><a href='kritaDoc_Class-{className}.html' target='iframeClass'>{className}</a></li>")

            fileName = f'kritaDoc_Classes-Index.html'
            fileContent = f"""<!DOCTYPE HTML>
            <html>
                <head>
                    <meta charset="utf-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                    <meta name="generator" content="BuliPy/build_docs.py"/>
                    <meta name="buildDoc:git:tagName" content="{tag['tag']}"/>
                    <meta name="buildDoc:git:tagDate" content="{tag['date']}"/>
                    <meta name="buildDoc:git:tagHash" content="{tag['hash']}"/>

                    <title>Krita {tag['nTagName']} API - Classes</title>
                    <style>{KritaBuildDoc.__cssContent}</style>
                </head>
                <body class='index'>
                    <div class='leftMenu'>
                        <h3>Krita Classes<span class='bulipy'>Documentation built from plugin <a href='https://github.com/Grum999/BuliPy'>BuliPy</a></span></h3>
                        <ul>{''.join(classList)}</ul>
                    </div>
                    <iframe class='frameContent' src="kritaDoc_Class-Krita.html" name="iframeClass"></iframe>
                </body>
            </html>
            """

            # dedent
            fileContent = re.sub(r"^[ ]{12}", "", fileContent, flags=re.M)
            htmlFile = os.path.join(pluginPathDocs, fileName)
            try:
                with open(htmlFile, 'w') as fHandle:
                    fHandle.write(fileContent)
            except Exception as e:
                print(f"ERROR: Can't save html file: {fileName}")
                print(e)

        if self.__buildHtml:
            print("BUILD HTML DOC")

            lastTagRef = sorted(self.__kritaReferential['tags'].keys())[-1]
            tag = self.__getTag(lastTagRef)
            tag['nTagName'] = self.__getTagName(lastTagRef)

            for className in sorted(self.__kritaReferential['classes'].keys()):
                buildHtmlClass(self.__kritaReferential['classes'][className], tag)

            buildHtmlIndex(self.__kritaReferential['classes'], tag)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build krita documentation')
    parser.add_argument('--kritaSrc',
                        dest='KRITA_SOURCE_PATH',
                        action='store',
                        help='Krita source code path')

    parser.add_argument('--reset',
                        dest='reset',
                        action='store_true',
                        help='Rebuild from scratch')

    parser.add_argument('--showTypes',
                        dest='showTypes',
                        action='store_true',
                        help='List found types')

    parser.add_argument('--updateRepo',
                        dest='updateRepo',
                        action='store_true',
                        help='Update repository')

    parser.add_argument('--buildPython',
                        dest='buildPython',
                        action='store_true',
                        help='Build krita.py file, that can be used by IDE')

    parser.add_argument('--buildHtml',
                        dest='buildHtml',
                        action='store_true',
                        help='Build krita.html file')

    args = parser.parse_args()
    argsVar = vars(args)

    if argsVar['KRITA_SOURCE_PATH'] is None:
        parser.print_help()
        exit()

    kritaSrcPath = os.path.expanduser(os.path.abspath(argsVar['KRITA_SOURCE_PATH']))
    if not os.path.exists(kritaSrcPath):
        print(f"Given Krita source path seems to not be a valid Krita source repository: {kritaSrcPath}")
        print(f"--> Path not found")
        exit()

    kritaSrcLibKisPath = os.path.join(kritaSrcPath, 'libs', 'libkis')
    if not os.path.exists(kritaSrcLibKisPath):
        print(f"Given Krita source path seems to not be a valid Krita source repository: {kritaSrcPath}")
        print(f"--> Unable to find libs/libkis")
        exit()

    try:
        cmdResult = subprocess.run(["git", "--version"], capture_output=True)
    except Exception:
        print(f"Git is not installed on your system")
        print(f"Git is required")

    pluginPathDocs = os.path.join(pluginPath, 'bp', 'resources', 'docs')
    if argsVar['reset'] is True:
        for file in [fileName for fileName in os.listdir(pluginPathDocs) if re.search(r'\.(html|py|json)$', fileName)]:
            docFile = os.path.join(pluginPathDocs, file)
            if os.path.exists(docFile):
                try:
                    os.remove(docFile)
                except Exception:
                    pass

    KritaBuildDoc(kritaSrcLibKisPath,
                  pluginPathDocs,
                  argsVar['updateRepo'],
                  argsVar['showTypes'],
                  argsVar['buildPython'],
                  argsVar['buildHtml'])

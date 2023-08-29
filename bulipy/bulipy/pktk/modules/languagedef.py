# -----------------------------------------------------------------------------
# PyKritaToolKit
# Copyright (C) 2019-2022 - Grum999
# -----------------------------------------------------------------------------
# SPDX-License-Identifier: GPL-3.0-or-later
#
# https://spdx.org/licenses/GPL-3.0-or-later.html
# -----------------------------------------------------------------------------
# A Krita plugin framework
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# The languagedef module provides base class used to defined a language
# (that can be tokenized and parsed --> tokenizer + parser modules)
#
# Main class from this module
#
# - LanguageDef:
#       Base class to use to define language
#
# - LanguageDefXML
#       Basic XML language definition
#
# -----------------------------------------------------------------------------

from PyQt5.Qt import *

import re

from .tokenizer import (
            Token,
            TokenType,
            TokenStyle,
            Tokenizer,
            TokenizerRule
        )
from .uitheme import UITheme

from ..pktk import *


class LanguageDef:

    SEP_PRIMARY_VALUE = '\x01'              # define bounds for <value> and cursor position
    SEP_SECONDARY_VALUE = '\x02'            # define bounds for other values

    def __init__(self, rules=[], styles=[]):
        """Initialise language & styles"""
        self.__tokenizer = Tokenizer(rules)
        self.__tokenStyle = TokenStyle()

    def __repr__(self):
        return f"<{self.__class__.name}({self.name()}, {self.extensions()})>"

    def name(self):
        """Return language name"""
        return "None"

    def extensions(self):
        """Return language file extension as list

        For example:
            ['.htm', '.html']

        """
        return []

    def tokenizer(self):
        """Return tokenizer for language"""
        return self.__tokenizer

    def setStyles(self, theme, styles):
        for style in styles:
            self.__tokenStyle.setStyle(theme, *style)

    def style(self, item):
        """Return style for given token and/or rule"""
        return self.__tokenStyle.style(item.type())

    def getTextProposal(self, text, full=False):
        """Return a list of possible values for given text

        return list of tuple (str, str, rule)
            str: autoCompletion value
            str: description
            rule: current rule
        """
        if not isinstance(text, str):
            raise EInvalidType('Given `text` must be str')

        rePattern = re.compile(re.escape(re.sub(r'\s+', '\x02', text)).replace('\x02', r'\s+')+'.*')
        returned = []
        for rule in self.__tokenizer.rules():
            values = rule.matchText(rePattern, full)
            if len(values) > 0:
                returned += values
        # return list without any duplicate values
        return list(set(returned))


class LanguageDefXML(LanguageDef):
    """Extent language definition for XML markup language"""

    class ITokenType(TokenType):
        STRING =        ('String', 'A STRING value')
        MARKUP =        ('Markup', 'A XML Markup')
        ATTRIBUTE =     ('Attribute', 'A node attribute')
        SETATTR =       ('=', 'Set attribute')
        CDATA =         ('Data', 'A CDATA value')
        VALUE =         ('Value', 'A VALUE value')
        COMMENTS =      ('Comments', 'A COMMENT value')
        SPECIALCHAR =   ('Special character', 'A SPECIAL CHARACTER value')

    def __init__(self):
        super(LanguageDefXML, self).__init__([
            TokenizerRule(LanguageDefXML.ITokenType.COMMENTS,
                          r'<!--(.*?)-->',
                          multiLineStart=r'<!--',
                          multiLineEnd=r'-->'),
            TokenizerRule(LanguageDefXML.ITokenType.CDATA,
                          r'<!\[CDATA\[.*\]\]>',
                          multiLineStart=r'<!\[CDATA\[',
                          multiLineEnd=r'\]\]>'),
            TokenizerRule(LanguageDefXML.ITokenType.STRING, r'"[^"\\]*(?:\\.[^"\\]*)*"'),
            TokenizerRule(LanguageDefXML.ITokenType.STRING, r"'[^'\\]*(?:\\.[^'\\]*)*'"),
            TokenizerRule(LanguageDefXML.ITokenType.MARKUP, r'<(?:\?xml|!DOCTYPE|!ELEMENT|\w[\w:-]*\b)'),
            TokenizerRule(LanguageDefXML.ITokenType.MARKUP, r'</\w[\w:-]*>'),
            TokenizerRule(LanguageDefXML.ITokenType.MARKUP, r'/?>|\?>'),
            TokenizerRule(LanguageDefXML.ITokenType.ATTRIBUTE, r'(?<=<[^>]*)\b\w[\w:-]*'),
            TokenizerRule(LanguageDefXML.ITokenType.ATTRIBUTE, r'\b\w[\w:-]*(?=\s*=)'),
            TokenizerRule(LanguageDefXML.ITokenType.SPECIALCHAR, r'&(?:amp|gt|lt|quot|apos|#\d+|#x[a-fA-F0-9]+);'),
            TokenizerRule(LanguageDefXML.ITokenType.SETATTR, r'='),
            TokenizerRule(LanguageDefXML.ITokenType.SPACE, r'\s+'),
            TokenizerRule(LanguageDefXML.ITokenType.VALUE, r'''[^<>'"&]*'''),
        ])

        self.setStyles(UITheme.DARK_THEME, [
            (LanguageDefXML.ITokenType.STRING, '#98c379', False, False),
            (LanguageDefXML.ITokenType.MARKUP, '#c678dd', True, False),
            (LanguageDefXML.ITokenType.ATTRIBUTE, '#80bfff', False, False),
            (LanguageDefXML.ITokenType.SETATTR, '#ff66d9', False, False),
            (LanguageDefXML.ITokenType.CDATA, '#ffe066', False, True),
            (LanguageDefXML.ITokenType.VALUE, '#cccccc', False, False),
            (LanguageDefXML.ITokenType.SPECIALCHAR, '#ddc066', False, False),
            (LanguageDefXML.ITokenType.COMMENTS, '#5c6370', False, True),
            (LanguageDefXML.ITokenType.SPACE, None, False, False)
        ])
        self.setStyles(UITheme.LIGHT_THEME, [
            (LanguageDefXML.ITokenType.STRING, '#9ac07c', False, False),
            (LanguageDefXML.ITokenType.MARKUP, '#e5dd82', True, False),
            (LanguageDefXML.ITokenType.ATTRIBUTE, '#e18890', False, False),
            (LanguageDefXML.ITokenType.SETATTR, '#c278da', False, False),
            (LanguageDefXML.ITokenType.CDATA, '#78dac2', False, False),
            (LanguageDefXML.ITokenType.VALUE, '#82dde5', False, False),
            (LanguageDefXML.ITokenType.SPACE, None, False, False)
        ])

    def name(self):
        """Return language name"""
        return "XML"

    def extensions(self):
        """Return language file extension as list"""
        return ['.xml', '.svg']


class LanguageDefJSON(LanguageDef):
    """Extent language definition for XML markup language"""

    class ITokenType(TokenType):
        OBJECT_ID =         ('Object Id', 'Object identifier')
        OBJECT_DEFINITION = ('Object definition', 'Separator')
        OBJECT_SEPARATOR =  ('Object separator', 'Separator')
        OBJECT_MARKER_S =   ('Object marker start', 'Start of Object')
        OBJECT_MARKER_E =   ('Object marker end', 'End of Object')
        ARRAY_MARKER_S =    ('Array marker start', 'Start of Array')
        ARRAY_MARKER_E =    ('Array marker end', 'End of Array')
        STRING =            ('Value String', 'A STRING value')
        NUMBER =            ('Value Number', 'A NUMBER value')
        SPECIAL_VALUE =     ('special value', 'A special value')

    def __init__(self):
        super(LanguageDefJSON, self).__init__([
            TokenizerRule(LanguageDefJSON.ITokenType.OBJECT_ID, r'"[^"\\]*(?:\\.[^"\\]*)*"(?=\s*:)'),
            TokenizerRule(LanguageDefJSON.ITokenType.STRING, r'"[^"\\]*(?:\\.[^"\\]*)*"'),
            TokenizerRule(LanguageDefJSON.ITokenType.NUMBER,
                          # float
                          r"-?(?:0\.|[1-9](?:\d*)\.)\d+(?:e[+-]?\d+)?",
                          caseInsensitive=True),
            TokenizerRule(LanguageDefJSON.ITokenType.NUMBER,
                          # integer
                          r"-?(?:[1-9]\d*)(?:e[+-]?\d+)?",
                          caseInsensitive=True),
            TokenizerRule(LanguageDefJSON.ITokenType.OBJECT_DEFINITION, r':'),
            TokenizerRule(LanguageDefJSON.ITokenType.OBJECT_SEPARATOR, r','),
            TokenizerRule(LanguageDefJSON.ITokenType.SPECIAL_VALUE, r'(?:true|false|null)'),
            TokenizerRule(LanguageDefJSON.ITokenType.OBJECT_MARKER_S, r'\{'),
            TokenizerRule(LanguageDefJSON.ITokenType.OBJECT_MARKER_E, r'\}'),
            TokenizerRule(LanguageDefJSON.ITokenType.ARRAY_MARKER_S, r'(?:\[)'),
            TokenizerRule(LanguageDefJSON.ITokenType.ARRAY_MARKER_E, r'(?:\])'),
            TokenizerRule(LanguageDefJSON.ITokenType.SPACE, r'\s+')
        ])

        self.setStyles(UITheme.DARK_THEME, [
            (LanguageDefJSON.ITokenType.OBJECT_ID, '#79c3cc', True, False),
            (LanguageDefJSON.ITokenType.STRING, '#98c379', False, False),
            (LanguageDefJSON.ITokenType.NUMBER, '#ffe066', False, True),
            (LanguageDefJSON.ITokenType.OBJECT_DEFINITION, '#ff66d9', True, False),
            (LanguageDefJSON.ITokenType.OBJECT_SEPARATOR, '#ff66d9', False, False),
            (LanguageDefJSON.ITokenType.OBJECT_MARKER_S, '#ff66d9', False, False),
            (LanguageDefJSON.ITokenType.OBJECT_MARKER_E, '#ff66d9', False, False),
            (LanguageDefJSON.ITokenType.ARRAY_MARKER_S, '#ff66d9', False, False),
            (LanguageDefJSON.ITokenType.ARRAY_MARKER_E, '#ff66d9', False, False),
            (LanguageDefJSON.ITokenType.SPECIAL_VALUE, '#c678dd', False, False),
            (LanguageDefJSON.ITokenType.SPACE, None, False, False)
        ])
        self.setStyles(UITheme.LIGHT_THEME, [
            (LanguageDefJSON.ITokenType.OBJECT_ID, '#79c398', True, False),
            (LanguageDefJSON.ITokenType.STRING, '#98c379', False, False),
            (LanguageDefJSON.ITokenType.NUMBER, '#ffe066', False, True),
            (LanguageDefJSON.ITokenType.OBJECT_DEFINITION, '#ff66d9', True, False),
            (LanguageDefJSON.ITokenType.OBJECT_SEPARATOR, '#ff66d9', False, False),
            (LanguageDefJSON.ITokenType.OBJECT_MARKER_S, '#ff66d9', False, False),
            (LanguageDefJSON.ITokenType.OBJECT_MARKER_E, '#ff66d9', False, False),
            (LanguageDefJSON.ITokenType.SPECIAL_VALUE, '#c678dd', False, False),
            (LanguageDefJSON.ITokenType.SPACE, None, False, False)
        ])

    def name(self):
        """Return language name"""
        return "JSON"

    def extensions(self):
        """Return language file extension as list"""
        return ['.json']

# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
import warnings

try:
    import pygments
except ImportError, e:
    warnings.warn("Pygments not installed")
    pygments = None
else:
    from pygments import highlight
    from pygments.lexers import PythonLexer, LlvmLexer
    from pygments.formatters import HtmlFormatter, TerminalFormatter

# ______________________________________________________________________

lexers = {
    "python": PythonLexer,
    "llvm": LlvmLexer,
}

formatters = {
    "html": HtmlFormatter,
    "console": TerminalFormatter,
}

def lex_source(code, lexer="python", output='html', inline_css=True):
    Lexer = lexers[lexer]
    Formatter = formatters[output]
    return highlight(code, Lexer(), Formatter(noclasses=inline_css))
import typing, random
from .README import LONG_DESCRIPTION
from textwrap import wrap
from os import get_terminal_size

osprint = print # Save original print...

# Reference: https://en.wikipedia.org/wiki/ANSI_escape_code
# https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_(Control_Sequence_Introducer)_sequences
BEL = '\a'
CSI = '\033['
ESC = '\033'
OSC = '\033]'
RESET = CSI + '0m'
ERROR_CODE = CSI + '31m'
CLEAR_SCREEN = CSI + '2J'
DEFAULT_CURSOR_POS = CSI + '1;1H'

ATTRIBUTES = {
                'BOLD': 1, 'DIM': 2, 'ITALIC': 3, 'UNDERLINE': 4,
                'BLINK': 5, 'INVERT': 7, 'HIDE': 8, 'STRIKE': 9,
                'DOUBLE-UNDERLINE': 21, 'FOREGROUND': 38, 'BACKGROUND': 48,
                'OVERLINED': 53, 'UNDERLINE-COLOR': 58, 'CLEAR': 0
            }

DEFAULT_COLORS = {
                    'BLACK': 30, 'RED': 31, 'GREEN': 32, 'YELLOW': 33, 'BLUE': 34,
                    'MAGENTA': 35, 'CYAN': 36, 'BRIGHT_GRAY': 37, 'DEFAULT': 39,
                    'DARK_GRAY': 90, 'BRIGHT_RED': 91, 'BRIGHT_GREEN': 92, 'BRIGHT_YELLOW': 93,
                    'BRIGHT_BLUE': 94,'BRIGHT_MAGENTA': 95, 'BRIGHT_CYAN': 96, 'WHITE': 97,
                }

EXTRA_COLORS = {
                    'PURPLE': (160, 32, 240),
                    'VOILET': (127, 0, 255),
                    'LIME': (50, 205, 50),
                    'ORANGE': (255, 165, 0),
                    'RANDOM': (0, 0, 0)
                }

AVAILABLE_COLORS = {}
AVAILABLE_COLORS.update(DEFAULT_COLORS)
AVAILABLE_COLORS.update(EXTRA_COLORS)

# NOT USING F STRING TO MAKE THIS COMPATIBLE WITH MOST PYTHON VERSIONS...
class MoeColorError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return self.error

class InvalidColor(MoeColorError):
    """
    Raised when the color passed is invalid
    """

class FormatText:
    def __init__(self, text: str='', color: typing.Any='DEFAULT', attr: typing.Iterable=[], usage: bool=False) -> None:
        self._text_width = 120
        self.attr = attr
        self.color = color
        self.text = str(text)
        self.__help() if usage else self.format_text()

    def __str__(self) -> str:
        return self.text

    def __help(self) -> None:
        osprint(LONG_DESCRIPTION)

    def format_text(self) -> None:
        self.sanitize_attr()
        self.build_string()

    def build_string(self) -> None:
        formatted_attrs = ''
        clear = ''
        if 'CLEAR' in self.attr:
            self.attr.remove('CLEAR')
            clear = CLEAR_SCREEN + DEFAULT_CURSOR_POS
        for t in self.attr:
            if t not in ATTRIBUTES:
                continue
            formatted_attrs += self.build_code(ATTRIBUTES[t])
        self.text = clear + formatted_attrs + self.build_color() + self.text + RESET

    def build_color(self) -> str:
        self.validate_color()
        offset = 0
        if {'INVERT', 'BACKGROUND'}.intersection(set(self.attr)):
            offset = 10
        if isinstance(self.color, list) or isinstance(self.color, tuple):
            code = '5' if len(self.color) == 1 else '2'
            self.color = [str(c) for c in self.color]
            color = ';'.join(self.color)
            color_code = '58' if 'UNDERLINE-COLOR' in self.attr else str(38 + offset)
            self.color = color_code + ';' + code + ';' + color
        else:
            self.color = '58'  if 'UNDERLINE-COLOR' in self.attr else str(self.color + offset)
        for t in ['INVERT', 'BACKGROUND', 'UNDERLINE-COLOR']:
            try:
                self.attr.remove(t)
            except:
                pass
        return self.build_code(self.color)

    def build_code(self, code) -> str:
        return CSI + str(code) + 'm'

    def validate_color(self) -> None:
        wrapped_colors = '\n     '.join(wrap(str(list(AVAILABLE_COLORS.keys())), width=self._text_width))
        err_msg = 'Expecting a color from the following options:\n' + \
                  '  - ' + wrapped_colors + '\n' + \
                  '  - ' + 'a hex code, e.g. \'#FFFFFF\'\n' + \
                  '  - ' + 'a tuple/list of RGB colors (R,G,B)/[R,G,B]\n' + \
                  '  - ' + 'an integer COLOR/[COLOR]\n' \
                  'but received [' + str(self.color) + '].'
        if isinstance(self.color, str):
            self.color = self.color.upper()
            if self.color == 'RANDOM':
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            elif self.color.startswith('#'):
                color = self.color.lstrip('#')
                color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            else:
                color = AVAILABLE_COLORS.get(self.color, -1)
                if color == -1:
                    color = self.close_match(self.color)
                if color == -1:
                    raise InvalidColor(self.build_err_msg(err_msg))
            self.color = color
        elif isinstance(self.color, list) or isinstance(self.color, tuple):
            if len(self.color) != 3 and len(self.color) != 1:
                err_msg = 'Expecting a tuple/list of RGB colors (R,G,B)/[R,G,B] ' + \
                          'or an integer COLOR/[COLOR], but received ' + str(self.color) + '.'
                raise InvalidColor(self.build_err_msg(err_msg))
            else:
                try:
                    self.color = [int(c) for c in self.color]
                except ValueError:
                    err_msg = 'Expecting a tuple/list integers, but received ' + str(self.color) + '.'
                    raise ValueError(self.build_err_msg(err_msg))
                else:
                    for c in self.color:
                        if c > 255 or c < 0:
                            err_msg = 'Expecting an integer between [0, 255], but received [' + str(c) +'].'
                            raise InvalidColor(self.build_err_msg(err_msg))
        elif isinstance(self.color, int):
            if self.color > 255 or self.color < 0:
                err_msg = 'Expecting an integer between [0, 255], but received [' + str(c) +'].'
                raise InvalidColor(self.build_err_msg(err_msg))
            else:
                self.color = [self.color]
        else:
            raise InvalidColor(self.build_err_msg(err_msg))

    def sanitize_attr(self) -> None:
        for i, t in enumerate(self.attr):
            attribute = str(t).lower()
            attribute = attribute.replace(' ', '-')
            if attribute in ['b', 'bold', 'thick']:
                self.attr[i] = 'BOLD'
            elif attribute in ['dim', 'dark', 'd']:
                self.attr[i] = 'DIM'
            elif attribute in ['i', 'italic']:
                self.attr[i] = 'ITALIC'
            elif attribute in ['u', 'underline']:
                self.attr[i] = 'UNDERLINE'
            elif attribute in ['blink', 'blinking', 'flash']:
                self.attr[i] = 'BLINK'
            elif attribute in ['reverse', 'invert', 'switch']:
                self.attr[i] = 'INVERT'
            elif attribute in ['conceal', 'hide', 'invisible']:
                self.attr[i] = 'HIDE'
            elif attribute in ['crossed-out', 'cross-out', 'crossed-out', 'strike', 's']:
                self.attr[i] = 'STRIKE'
            elif attribute in ['double-underline', '2u', 'uu', 'du']:
                self.attr[i] = 'DOUBLE-UNDERLINE'
            elif attribute in ['foreground', 'fg', 'fore-ground']:
                self.attr[i] = 'FOREGROUND'
            elif attribute in ['background' ,'bg', 'back-ground']:
                self.attr[i] = 'BACKGROUND'
            elif attribute in ['overlined', 'o', 'over-lined']:
                self.attr[i] = 'OVERLINED'
            elif attribute in ['underline-color', 'ucolor', 'u-color', 'uc']:
                self.attr[i] = 'UNDERLINE-COLOR'
            elif attribute in ['reset', 'reset-position', 'clear', 'clear-screen']:
                self.attr[i] = 'CLEAR'
            else:
                pass

    def build_err_msg(self, err_msg) -> str:
            return ERROR_CODE + '\n' + err_msg + RESET

    def close_match(self, word):
        scores = {}
        available_colors = list(AVAILABLE_COLORS.keys())
        from collections import Counter
        def word2vec(word):
            # count characters in word
            cw = Counter(word)
            sw = set(cw)
            # calculate word length
            lw = sum(c*c for c in cw.values())**0.5
            return (sw, cw, lw)

        v1 = word2vec(word)
        for color in available_colors:
            try:
                v2 = word2vec(color)
                shared = v1[0].intersection(v2[0])
                # Cos(x, y) = x . y / ||x|| * ||y||
                score = sum(v1[1][ch]*v2[1][ch] for ch in shared) / v1[2]/v2[2]
            except Exception:
                score = 0.5
            scores[color] = score
        scores = sorted(scores.items(), key=lambda item:item[1], reverse=True)
        return AVAILABLE_COLORS[scores[0][0]] if scores[0][1] > 0.5 else -1

def print(text: str='', *args, color: typing.Any='', attr: typing.Iterable=[], **kwargs):
    possible_help = ['h', 'usage', 'show_help', 'help_me', 'use', 'help']
    if set(possible_help).intersection(kwargs):
        osprint(LONG_DESCRIPTION)
        return
    try:
        text = (str(text) + ' ' + ' '.join(args)).strip()
        ft = FormatText(text, color, attr=attr) if color or attr else text
    except:
        osprint(text, **kwargs)
    else:
        osprint(ft, **kwargs)

print.__doc__ = LONG_DESCRIPTION
FormatText.__doc__ = LONG_DESCRIPTION

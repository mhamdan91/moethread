LONG_DESCRIPTION="""
Moecolor (Flexible terminal text coloring and styling)
=======================================================
## Table of Contents

 * [Overview](#overview)
 * [Library Installalion](#library-installalion)
 * [Library Usage](#library-usage)


## Overview
This lightweight tool allows you to color terminal text and style it based on predefined attributes. The tool works very much like the `print` function.
Except it is a fancier `print` that you can do a lot more with to control text color and style.

## Library Installalion
To install the library simply run the following command in a cmd, shell or whatever...

```bash
# It's recommended to create a virtual environment

# Windows
pip install moecolor

# Linux
pip3 install moecolor
```

## Library usage?

### Example usage
The following examples shows how to print text in `green` in so many different ways:
```python
from moecolor import print
print('My example text as green', color='green')
print('My example text as green', color='grreenn') # This is obviously not green, but we got you.
print('My example text as green', color='#00FF00')
print('My example text as green', color=(0, 255, 0))
print('My example text as green', color=(10,))
print('My example text as green', color=10)
```

The following example shows how to underline, cross-out, bold, italize, a red text:
```python
from moecolor import print
print('My example text as green', color='red', attr=['bold', 'italic', 'strike', 'underline'])
```

Do you want more fine-grained control over your text? Sure, the following example prints per word coloring. It will print RED GREEN BLUE TEXT, using various colour configurations.
```python
from moecolor import print # This is an optional import, you can still use the original print function.
from moecolor import FormatText as ft
print("{} {} {}".format(ft('RED TEXT', color='#ff0000'), ft('GREEN TEXT', color='green'), ft('BLUE TEXT', color=12)))
```

### Usage Guidelines
The tool simply overloads the `print` function, so you can use it as a normal print and if you'd like to color and style text you can provide extra arguments.
The tool accepts the following arguments in addition to the kwargs accepted by the builtin `print` function.
- color
- attr
- usage

There are many options to choose from to color your text. You can:
- Choose a color string from a list of pre-defined colors ['BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'BRIGHT_GRAY', 'DEFAULT', 'DARK_GRAY',
  'BRIGHT_RED', 'BRIGHT_GREEN', 'BRIGHT_YELLOW', 'BRIGHT_BLUE', 'BRIGHT_MAGENTA', 'BRIGHT_CYAN','WHITE', 'PURPLE', 'VOILET', 'LIME', 'ORANGE', 'RANDOM']
- If you wish to generate a random color, you can supply the word: 'RANDOM'.
- If you wish to pick a color from 256-color mode scale based on `https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit`, you can provide an integer between [0-255]
- If you wish to provide an RGB value for a specific 24-bit color, you provide a tuple/list of RGB values: (R, G, B) and numbers must be integers between [0-255]
- If you wish to provide a hex-code for an 24-bit RGB equivelent color, you can provide a string like `#FFFFFF`.

To style your text, you can use a set of pre-defined attributes:
- 'BOLD': **bold text** (synonymous options: 'b', 'bold', 'thick')
- 'DIM': dim text a little (synonymous options: 'dim', 'dark', 'd')
- 'ITALIC': *italize text* (synonymous options: 'i', 'italic')
- 'UNDERLINE': underline text, (synonymous options: 'u', 'underline')
- 'BLINK': make text blink at less than 150 times per minute (synonymous options: 'blink', 'blinking', 'flash')
- 'INVERT': invert text (synonymous options: 'reverse', 'invert', 'switch')
- 'HIDE': hide text from terminal (synonymous options: 'conceal', 'hide', 'invisible')
- 'STRIKE': ~~make text crossed-out~~, (synonymous options: 'crossed-out', 'cross-out', 'crossed-out', 'strike', 's')
- 'DOUBLE-UNDERLINE': underline text with double lines, (synonymous options: 'double-underline', '2u', 'uu', 'du')
- 'FOREGROUND': control foreground color [default behavior], (synonymous options: 'foreground', 'fg', 'fore-ground')
- 'BACKGROUND': control background color [to apply color the background instead of the foreground], (synonymous options: 'background' ,'bg', 'back-ground')
- 'OVERLINED': overline text (synonymous options: 'overlined', 'o', 'over-lined')
- 'UNDERLINE-COLOR': apply color to underlined text, used along with underlining, otherwise no effect (synonymous options: underline-color', 'ucolor', 'u-color', 'uc')
- 'CLEAR': clear screen, then print text. (synonymous options: 'reset', 'reset-position', 'clear', 'clear-screen')

To show tool usage, or this README, i.e., you supply the keyword `usage` or one of its synonymous ('h', 'usage', 'show_help', 'help_me', 'use') as follows:
```python
print(usage=True)
```
You can also display tool usage/docs using the following command:
```python
help(print)
```


```python
# Note, all strings are case insensitive, so don't worry. Not just that, even if you misspell a color, we will guess it for you ;)
# Just do NOT type `regrlue' and expect it to be blue for example, it might come up as green though.

\"""
Some attributes may not be supported in all terminals. So, if a specific attribute does not work, that means the
terminal you are using does not support it.

Windows terminals (CMD, PS) support most of attributes, but the following ['blink', 'dim']
LINUX terminals support all AFAIK
\"""
```

----------------------------------------
Author: Hamdan, Muhammad (@mhamdan91 - ©)

"""
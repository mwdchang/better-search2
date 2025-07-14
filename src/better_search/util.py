import textwrap

def indent_wrap(text, width=120, indent=4):
    indentation = " " * indent  # Create an indent of 4 spaces
    wrapped_text = textwrap.fill(text, width=width, initial_indent=indentation, subsequent_indent=indentation)
    print(wrapped_text)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def print_hex_color(text, hex_color):
    r, g, b = hex_to_rgb(hex_color)
    print(f"\033[38;2;{r};{g};{b}m{text}\033[0m")

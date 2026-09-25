import ctypes
import os
import random
import sys
import time

TITLE = "Life Is My Teacher"
COLS = 160
ROWS = 48
FRAME = 0.05             # note: seconds per animation step
CORNER_WINDOW = (10, 20) # note: seconds until the guaranteed corner hit
HOLD = 2.0               # note: seconds to hold the corner frame / proverb
FADE_STEPS = 24          # note: grayscale levels 232 to 255

BORDER_WORD = "LIFE"
FILL_WORD = "ME" # note: every pixel of the box is one "ME"
BORDER_SHADE = 244
FULL = 255
DARK = 232

# note: 12x12 glyphs; '#' marks the stroke that is cut out of the "ME" box
GLYPHS = {
    "三": """
............
.##########.
............
............
............
...######...
............
............
............
############
............
............""",
    "人": """
.....#......
.....#......
.....#......
.....#......
.....##.....
....#.#.....
....#..#....
...#...#....
..#.....#...
.#......##..
#........##.
............""",
    "行": """
...#........
..#...######
.#..........
#...........
...#........
..#..#######
.##.......#.
#.#.......#.
..#.......#.
..#.......#.
..#.......#.
..#.....###.""",
    "必": """
.....#......
......#.....
..........#.
.........#..
..#.....#...
..#....#....
#.#...#..#..
#.#..#....#.
..#.#......#
..##........
.#.#........
...#######..""",
    "有": """
....#.......
############
...#........
..#######...
.##.....#...
#.#######...
..#.....#...
..#######...
..#.....#...
..#.....#...
..#...###...
............""",
    "我": """
.....#.#....
..###..#.#..
....#..#..#.
.####..#....
....#..#....
############
....#...#.#.
..###...##..
....#...#...
....#..#.#.#
....#.#...##
..##........""",
    "师": """
..#.########
..#.....#...
#.#..#######
#.#..#..#..#
#.#..#..#..#
#.#..#..#..#
#.#..#..#..#
..#..#..#.##
..#.....#...
.#......#...
.#......#...
#.......#...""",
}

def glyph(char):
    drawing = GLYPHS[char]
    drawing = drawing.strip("\n")
    rows = drawing.splitlines()
    return rows

def block(text):
    glyphs = []
    for char in text:
        glyphs.append(glyph(char))

    glyph_height = len(glyphs[0])
    block_height = glyph_height + 2
    top_row = 0
    bottom_row = block_height - 1

    # note: True = filled with "ME", False = hollow (part of a character)
    pixels = []
    for i in range(block_height):
        row = [True]
        
        for j in glyphs:
            glyph_width = len(j[0])

            if i == top_row or i == bottom_row:
                for k in range(glyph_width):
                    row.append(True)
            else:
                glyph_row = j[i - 1]

                for mark in glyph_row:
                    is_filled = mark != "#"
                    row.append(is_filled)

            row.append(True)

        pixels.append(row)

    hollow = " " * len(FILL_WORD)

    lines = []
    for row in pixels:
        line = ""

        for is_filled in row:
            if is_filled:
                line += FILL_WORD
            else:
                line += hollow

        lines.append(line)

    return lines

def border():
    word_length = len(BORDER_WORD)
    top_row = 0
    bottom_row = ROWS - 1
    left_col = 0
    right_col = COLS - 1
    cells = {}

    for i in range(COLS):
        letter = BORDER_WORD[i % word_length]
        cells[(top_row, i)] = letter
        cells[(bottom_row, i)] = letter

    for i in range(1, ROWS - 1):
        letter = BORDER_WORD[i % word_length]
        cells[(i, left_col)] = letter
        cells[(i, right_col)] = letter

    # note: title sits in the middle of the bottom edge
    label = " " + TITLE.upper() + " "
    start = (COLS - len(label)) // 2

    for i in range(len(label)):
        cells[(bottom_row, start + i)] = label[i]

    return cells

BORDER = border()
BOUNCER = block("三人行")
PROVERB = block("必有我师")

def render(block=None, pos=(0, 0), shade=FULL):
    border_colour = f"\x1b[38;5;{BORDER_SHADE}m"
    block_colour = f"\x1b[38;5;{shade}m"
    inner_width = COLS - 2
    block_x = pos[0]
    block_y = pos[1]

    if block:
        block_width = len(block[0])
        block_height = len(block)
    else:
        block_width = 0
        block_height = 0

    lines = []
    for i in range(ROWS):
        is_top_or_bottom = i == 0 or i == ROWS - 1

        if is_top_or_bottom:
            edge = ""

            for j in range(COLS):
                edge += BORDER[(i, j)]

            line = border_colour + edge
        else:
            block_row = i - 1 - block_y
            block_on_this_row = block and 0 <= block_row < block_height

            if block_on_this_row:
                left_gap = " " * block_x
                right_gap = " " * (inner_width - block_x - block_width)
                inside = left_gap + block_colour + block[block_row] + right_gap
            else:
                inside = " " * inner_width

            left_edge = border_colour + BORDER[(i, 0)]
            right_edge = border_colour + BORDER[(i, COLS - 1)]
            line = left_edge + inside + right_edge

        lines.append(line)

    frame = "\x1b[H" + "\n".join(lines)
    sys.stdout.write(frame)
    sys.stdout.flush()

def fade(block, pos, rising):
    if rising:
        levels = range(DARK, FULL + 1)
    else:
        levels = range(FULL, DARK - 1, -1)

    for shade in levels:
        render(block, pos, shade)
        time.sleep(1.5 / FADE_STEPS)

    if not rising:
        render()

def plan():
    # note: positions are in units of "ME"
    max_x = (COLS - 2 - len(BOUNCER[0])) // 2
    max_y = ROWS - 2 - len(BOUNCER)
    min_steps = int(CORNER_WINDOW[0] / FRAME)
    max_steps = int(CORNER_WINDOW[1] / FRAME)

    while True:
        start_x = random.randint(1, max_x - 1)
        start_y = random.randint(1, max_y - 1)
        start_dx = random.choice((-1, 1))
        start_dy = random.choice((-1, 1))

        x = start_x
        y = start_y
        dx = start_dx
        dy = start_dy

        # note: simulate this start and see when it first hits a corner
        for step in range(1, max_steps + 1):
            x = x + dx
            y = y + dy
            hit_side = x == 0 or x == max_x
            hit_top_or_bottom = y == 0 or y == max_y

            if hit_side:
                dx = -dx

            if hit_top_or_bottom:
                dy = -dy

            if hit_side and hit_top_or_bottom:
                if step >= min_steps:
                    return start_x, start_y, start_dx, start_dy, step
                
                break

def bounce():
    x, y, dx, dy, steps = plan()
    max_x = (COLS - 2 - len(BOUNCER[0])) // 2
    max_y = ROWS - 2 - len(BOUNCER)
    fade(BOUNCER, (x * 2, y), rising=True)
    
    for _ in range(steps):
        x = x + dx
        y = y + dy

        if x == 0 or x == max_x:
            dx = -dx

        if y == 0 or y == max_y:
            dy = -dy

        render(BOUNCER, (x * 2, y))
        time.sleep(FRAME)

    time.sleep(HOLD)
    fade(BOUNCER, (x * 2, y), rising=False)

def proverb():
    center_x = (COLS - 2 - len(PROVERB[0])) // 2
    center_y = (ROWS - 2 - len(PROVERB)) // 2
    pos = (center_x, center_y)

    fade(PROVERB, pos, rising=True)
    time.sleep(HOLD)
    fade(PROVERB, pos, rising=False)

def setup():
    if os.name != "nt":
        return
    
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    STD_OUTPUT_HANDLE = -11
    ENABLE_VT_SEQUENCES = 0x0004
    SWP_NOSIZE = 0x0001
    SWP_NOZORDER = 0x0004

    user32.SetProcessDPIAware()
    kernel32.SetConsoleTitleW(TITLE)
    handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    mode = ctypes.c_uint32()
    kernel32.GetConsoleMode(handle, ctypes.byref(mode))
    kernel32.SetConsoleMode(handle, mode.value | ENABLE_VT_SEQUENCES)

    class COORD(ctypes.Structure):
        _fields_ = [
            ("X", ctypes.c_short),
            ("Y", ctypes.c_short),
        ]

    class FONT(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("nFont", ctypes.c_ulong),
            ("dwFontSize", COORD),
            ("FontFamily", ctypes.c_uint),
            ("FontWeight", ctypes.c_uint),
            ("FaceName", ctypes.c_wchar * 32),
        ]

    # note: largest consolas size that fits the screen (a character is ~half as wide as tall)
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    size_by_height = int(screen_height * 0.85 / ROWS)
    size_by_width = int(screen_width * 0.9 / COLS * 2)
    size = min(size_by_height, size_by_width)
    size = max(8, size)

    font = FONT()
    font.cbSize = ctypes.sizeof(FONT)
    font.nFont = 0
    font.dwFontSize = COORD(0, size)
    font.FontFamily = 54
    font.FontWeight = 400
    font.FaceName = "Consolas"
    kernel32.SetCurrentConsoleFontEx(handle, False, ctypes.byref(font))

    os.system(f"mode con cols={COLS} lines={ROWS}")
    kernel32.SetConsoleMode(handle, mode.value | ENABLE_VT_SEQUENCES)

    window = kernel32.GetConsoleWindow()
    rect = (ctypes.c_long * 4)()
    user32.GetWindowRect(window, rect)
    window_width = rect[2] - rect[0]
    window_height = rect[3] - rect[1]
    left = (screen_width - window_width) // 2
    top = (screen_height - window_height) // 2
    user32.SetWindowPos(window, 0, left, top, 0, 0, SWP_NOSIZE | SWP_NOZORDER)

def main():
    setup()
    sys.stdout.write("\x1b[?25l\x1b[2J") # note: hide cursor, clear
    
    try:
        while True:
            bounce()
            proverb()
    except KeyboardInterrupt:
        pass

    finally:
        sys.stdout.write("\x1b[0m\x1b[?25h\x1b[2J\x1b[H")

if __name__ == "__main__":
    main()
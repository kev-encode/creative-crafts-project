import random
import sys
import time
from console import setup
from glyphs import GLYPHS

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
TITLE_SHADE = 255
FULL = 255
DARK = 232

# note: title sits in the middle of the bottom edge
LABEL = " " + TITLE.upper() + " "
LABEL_START = (COLS - len(LABEL)) // 2
LABEL_END = LABEL_START + len(LABEL)

def make_glyph(char):
    glyph = GLYPHS[char]
    glyph = glyph.strip("\n")
    rows = glyph.splitlines()
    return rows

def make_block(text):
    glyphs = []
    for char in text:
        glyphs.append(make_glyph(char))

    glyph_height = len(glyphs[0])
    block_height = glyph_height + 2
    top_row = 0
    bottom_row = block_height - 1

    # note: True = filled with "ME", False = hollow (part of a character)
    pixels = []
    for r in range(block_height):
        row = [True]
        
        for glyph in glyphs:
            glyph_width = len(glyph[0])

            if r == top_row or r == bottom_row:
                for c in range(glyph_width):
                    row.append(True)
            else:
                glyph_row = glyph[r - 1]

                for mark in glyph_row:
                    is_filled = mark != "#"
                    row.append(is_filled)

            row.append(True)

        pixels.append(row)

    hollow = " " * len(FILL_WORD)

    lines = []
    for r in pixels:
        line = ""

        for is_filled in r:
            if is_filled:
                line += FILL_WORD
            else:
                line += hollow

        lines.append(line)

    return lines

def make_border():
    word_len = len(BORDER_WORD)
    top_row = 0
    bottom_row = ROWS - 1
    left_col = 0
    right_col = COLS - 1
    cells = {}

    for c in range(COLS):
        letter = BORDER_WORD[c % word_len]
        cells[(top_row, c)] = letter
        cells[(bottom_row, c)] = letter

    for r in range(1, ROWS - 1):
        letter = BORDER_WORD[r % word_len]
        cells[(r, left_col)] = letter
        cells[(r, right_col)] = letter

    for i in range(len(LABEL)):
        cells[(bottom_row, LABEL_START + i)] = LABEL[i]

    return cells

BORDER = make_border()
BOUNCER = make_block("三人行")
PROVERB = make_block("必有我师")

def render(block=None, pos=(0, 0), shade=FULL):
    border_color = f"\x1b[38;5;{BORDER_SHADE}m"
    block_color = f"\x1b[38;5;{shade}m"
    title_color = f"\x1b[38;5;{TITLE_SHADE}m"
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
    for r in range(ROWS):
        is_edge_row = (r == 0) or (r == ROWS - 1)

        if is_edge_row:
            edge = ""

            for c in range(COLS):
                if r == ROWS - 1 and c == LABEL_START:
                    edge += title_color

                if r == ROWS - 1 and c == LABEL_END:
                    edge += border_color

                edge += BORDER[(r, c)]

            line = border_color + edge

        else:
            block_row = r - 1 - block_y
            is_block_row = block and (0 <= block_row < block_height)

            if is_block_row:
                left_gap = " " * block_x
                right_gap = " " * (inner_width - block_x - block_width)
                inside = left_gap + block_color + block[block_row] + right_gap
            else:
                inside = " " * inner_width

            left_edge = border_color + BORDER[(r, 0)]
            right_edge = border_color + BORDER[(r, COLS - 1)]
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
        for i in range(1, max_steps + 1):
            x = x + dx
            y = y + dy
            hit_side = (x == 0) or (x == max_x)
            hit_top_or_bottom = y == 0 or y == max_y

            if hit_side:
                dx = -dx

            if hit_top_or_bottom:
                dy = -dy

            if hit_side and hit_top_or_bottom:
                if i >= min_steps:
                    return start_x, start_y, start_dx, start_dy, i
                
                break

def bounce():
    x, y, dx, dy, steps = plan()
    max_x = (COLS - 2 - len(BOUNCER[0])) // 2
    max_y = ROWS - 2 - len(BOUNCER)
    fade(BOUNCER, (x * 2, y), rising=True)
    
    for i in range(steps):
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

def make_proverb():
    center_x = (COLS - 2 - len(PROVERB[0])) // 2
    center_y = (ROWS - 2 - len(PROVERB)) // 2
    pos = (center_x, center_y)

    fade(PROVERB, pos, rising=True)
    time.sleep(HOLD)
    fade(PROVERB, pos, rising=False)

def main():
    setup(TITLE, COLS, ROWS)
    sys.stdout.write("\x1b[?25l\x1b[2J") # note: hide cursor, clear
    
    try:
        while True:
            bounce()
            make_proverb()
    except KeyboardInterrupt:
        pass

    finally:
        sys.stdout.write("\x1b[0m\x1b[?25h\x1b[2J\x1b[H")

if __name__ == "__main__":
    main()
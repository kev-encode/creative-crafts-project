import ctypes
import os

def setup(title, cols, rows):
    if os.name != "nt":
        return

    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    STD_OUTPUT_HANDLE = -11
    ENABLE_VT_SEQUENCES = 0x0004
    SWP_NOSIZE = 0x0001
    SWP_NOZORDER = 0x0004

    user32.SetProcessDPIAware()
    kernel32.SetConsoleTitleW(title)
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
    size_by_height = int(screen_height * 0.65 / rows)
    size_by_width = int(screen_width * 0.7 / cols * 2)
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

    os.system(f"mode con cols={cols} lines={rows}")
    kernel32.SetConsoleMode(handle, mode.value | ENABLE_VT_SEQUENCES)

    window = kernel32.GetConsoleWindow()
    rect = (ctypes.c_long * 4)()
    user32.GetWindowRect(window, rect)
    window_width = rect[2] - rect[0]
    window_height = rect[3] - rect[1]
    left = (screen_width - window_width) // 2
    top = (screen_height - window_height) // 2
    user32.SetWindowPos(window, 0, left, top, 0, 0, SWP_NOSIZE | SWP_NOZORDER)
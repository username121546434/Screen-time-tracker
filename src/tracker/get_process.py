import psutil
import win32ui
import win32process
import win32gui
import win32api


def get_app_process(hwnd):
    """Get the app process information from hwnd

    Args:
        hwnd (int): The hwnd

    Returns:
        `psutil.Process | None`: The process, or `None` if it wasn't found
    """
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
    except Exception as e:
        print(e)
    else:
        return proc


def get_app_path(hwnd):
    """Get application path given hwnd."""
    process = get_app_process(hwnd)
    if process:
        return process.exe()


def get_app_name(hwnd):
    """Get application filename given hwnd."""
    process = get_app_process(hwnd)
    if process:
        return process.name()


def get_active_window_hwnd():
    try:
        window = win32ui.GetForegroundWindow()
        (left, top, right, bottom) = window.GetWindowRect()

        if (
            not window.IsWindowVisible() or
            not window or
            win32gui.GetClassName(window.GetSafeHwnd()) == "Shell_TrayWnd" or
            win32gui.GetClassName(window.GetSafeHwnd()) == "Progman" or # Desktop
            len(window.GetWindowText()) <= 0 or
            left == right or top == bottom # the window takes 0 space
        ):
            return None
        return window.GetSafeHwnd()
    except Exception as e:
        print(e)

def get_active_window_app_name():
    return get_app_name(get_active_window_hwnd())


def get_active_window_app_path():
    return get_app_path(get_active_window_hwnd())


def get_app_name_from_exe(windows_exe: str) -> str | None:
    """Returns the application name of a windows executable path

    Args:
        windows_exe (str): The path to the executable, ie: ``C:\...\Programs\Microsoft VS Code\Code.exe``

    Returns:
        `str | None`: The app name. ie: Visual Studio Code
    """
    try:
        language, codepage = win32api.GetFileVersionInfo(windows_exe, '\\VarFileInfo\\Translation')[0]
        stringFileInfo = u'\\StringFileInfo\\%04X%04X\\%s' % (language, codepage, "FileDescription")
        description = win32api.GetFileVersionInfo(windows_exe, stringFileInfo)
    except Exception as e:
        description = "unknown"
        print(e)
    
        
    return description


get_active_window_process_name = get_active_window_app_path

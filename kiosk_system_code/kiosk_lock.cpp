#include <windows.h>

int main() {
    // Hide Taskbar
    HWND taskbar = FindWindow("Shell_TrayWnd", NULL);
    ShowWindow(taskbar, SW_HIDE);

    // Hide Start Button (optional for older Windows)
    HWND startButton = FindWindow("Button", NULL);
    ShowWindow(startButton, SW_HIDE);

    MessageBox(NULL, "Taskbar Hidden. Press OK to show it again.", "Kiosk Mode", MB_OK);

    // Show Taskbar again after message box
    ShowWindow(taskbar, SW_SHOW);
    ShowWindow(startButton, SW_SHOW);

    return 0;
}

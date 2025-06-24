#include <windows.h>
#include <iostream>

HHOOK keyboardHook;

LRESULT CALLBACK LowLevelKeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode == HC_ACTION) {
        KBDLLHOOKSTRUCT* p = (KBDLLHOOKSTRUCT*)lParam;

        // Block Alt+Tab, Ctrl+Esc, WinKey (left and right)
        bool altPressed = GetAsyncKeyState(VK_MENU) & 0x8000;
        bool ctrlPressed = GetAsyncKeyState(VK_CONTROL) & 0x8000;

        if (
            (p->vkCode == VK_TAB && altPressed) ||          // Alt+Tab
            (p->vkCode == VK_ESCAPE && ctrlPressed) ||      // Ctrl+Esc
            (p->vkCode == VK_LWIN || p->vkCode == VK_RWIN)  // Win Key
        ) {
            return 1; // Block the key
        }
    }

    return CallNextHookEx(keyboardHook, nCode, wParam, lParam);
}

int main() {
    MSG msg;

    // Install hook
    keyboardHook = SetWindowsHookEx(WH_KEYBOARD_LL, LowLevelKeyboardProc, NULL, 0);
    if (keyboardHook == NULL) {
        std::cerr << "Failed to install keyboard hook!" << std::endl;
        return 1;
    }

    std::cout << "Keyboard hook active. Press Ctrl+C in this terminal to stop." << std::endl;

    // Message loop (hook lives here)
    while (GetMessage(&msg, NULL, 0, 0)) {}

    UnhookWindowsHookEx(keyboardHook);
    return 0;
}

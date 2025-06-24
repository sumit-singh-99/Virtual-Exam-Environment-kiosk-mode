#include <windows.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <csignal>
#include <cstdlib>

HHOOK keyboardHook;
bool cleanupDone = false;

// ----- Block Task Manager -----
bool SetTaskManager(bool disable) {
    HKEY hKey;
    LPCSTR keyPath = "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System";

    if (RegCreateKeyExA(HKEY_CURRENT_USER, keyPath, 0, NULL, 0, KEY_WRITE, NULL, &hKey, NULL) != ERROR_SUCCESS)
        return false;

    DWORD value = disable ? 1 : 0;

    if (RegSetValueExA(hKey, "DisableTaskMgr", 0, REG_DWORD, (const BYTE*)&value, sizeof(value)) != ERROR_SUCCESS) {
        RegCloseKey(hKey);
        return false;
    }

    RegCloseKey(hKey);
    return true;
}

// ----- Cleanup -----
void PerformCleanup() {
    if (!cleanupDone) {
        cleanupDone = true;
        std::cout << "Performing cleanup..." << std::endl;
        UnhookWindowsHookEx(keyboardHook);
        SetTaskManager(false);
        std::cout << "Cleanup completed." << std::endl;
    }
}

// ----- Exit/Crash Handlers -----
BOOL WINAPI ConsoleHandler(DWORD signal) {
    PerformCleanup();
    return FALSE;
}

// ----- Keyboard Hook -----
LRESULT CALLBACK LowLevelKeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode == HC_ACTION) {
        KBDLLHOOKSTRUCT* p = (KBDLLHOOKSTRUCT*)lParam;
        bool alt = GetAsyncKeyState(VK_MENU) & 0x8000;
        bool ctrl = GetAsyncKeyState(VK_CONTROL) & 0x8000;

        if (
            (p->vkCode == VK_TAB && alt) ||
            (p->vkCode == VK_ESCAPE && ctrl) ||
            (p->vkCode == VK_LWIN || p->vkCode == VK_RWIN) ||
            (p->vkCode == VK_F4 && alt) ||
            (p->vkCode == 'C' && ctrl) ||
            (p->vkCode == 'V' && ctrl) ||
            (p->vkCode == 'X' && ctrl) ||
            (p->vkCode == VK_INSERT && ctrl) ||
            (p->vkCode == VK_SNAPSHOT) ||
            (p->vkCode == VK_APPS)
        ) {
            return 1; // Block these keys
        }
    }

    return CallNextHookEx(keyboardHook, nCode, wParam, lParam);
}

// ----- Timer Thread -----
void ExamTimerThread(int durationMinutes) {
    std::this_thread::sleep_for(std::chrono::minutes(durationMinutes));
    MessageBox(NULL, "Exam time is over. System is now unlocked.", "Exam Over", MB_OK);
    PerformCleanup();
    PostQuitMessage(0);
}

// ----- Window Procedure -----
LRESULT CALLBACK DummyWndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    if (msg == WM_CLOSE || msg == WM_DESTROY || msg == WM_QUERYENDSESSION) {
        PerformCleanup();
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProc(hwnd, msg, wParam, lParam);
}

// ----- Main -----
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE, LPSTR lpCmdLine, int) {
    int durationMinutes = atoi(lpCmdLine);
    if (durationMinutes <= 0) {
        MessageBox(NULL, "Usage: exam_kiosk.exe <duration_in_minutes>", "Error", MB_OK | MB_ICONERROR);
        return 1;
    }

    SetConsoleCtrlHandler(ConsoleHandler, TRUE);
    atexit(PerformCleanup);

    HWND console = GetConsoleWindow();
    if (console) ShowWindow(console, SW_MINIMIZE);

    SetTaskManager(true);

    keyboardHook = SetWindowsHookEx(WH_KEYBOARD_LL, LowLevelKeyboardProc, NULL, 0);
    if (!keyboardHook) {
        MessageBox(NULL, "Failed to install keyboard hook.", "Error", MB_OK | MB_ICONERROR);
        return 1;
    }

    // Register dummy window
    WNDCLASS wc = {};
    wc.lpfnWndProc = DummyWndProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = "KioskDummyWindowClass";
    RegisterClass(&wc);

    HWND hwnd = CreateWindowEx(
        WS_EX_TOOLWINDOW,
        "KioskDummyWindowClass",
        "HiddenKioskWindow",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 100, 100,
        NULL, NULL, hInstance, NULL
    );
    ShowWindow(hwnd, SW_HIDE);

    std::thread timerThread(ExamTimerThread, durationMinutes);
    timerThread.detach();

    MSG msg = {};
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    PerformCleanup();
    return 0;
}

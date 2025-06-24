#include <windows.h>
#include <iostream>
#include <chrono>
#include <thread>

// Global flag to control window closing after timeout
bool allowExit = false;

// Window Procedure
LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_KEYDOWN:
            if (wParam == VK_ESCAPE && allowExit) {
                PostQuitMessage(0);
                return 0;
            }
            break;

        case WM_CLOSE:
            // Block closing window unless timeout has passed
            if (allowExit) {
                DestroyWindow(hwnd);
            }
            return 0;

        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;
    }

    return DefWindowProc(hwnd, msg, wParam, lParam);
}

// Thread to monitor duration
DWORD WINAPI TimerThread(LPVOID lpParam) {
    int durationMinutes = *(int*)lpParam;
    std::this_thread::sleep_for(std::chrono::minutes(durationMinutes));
    allowExit = true;

    MessageBox(NULL, "Exam time over. You may now press ESC to exit.", "Time's Up", MB_OK | MB_ICONINFORMATION);

    return 0;
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
                   LPSTR lpCmdLine, int nCmdShow) {

    // Parse time from command line
    int durationMinutes = atoi(lpCmdLine);
    if (durationMinutes <= 0) {
        MessageBox(NULL, "Usage: exam_window.exe <duration_in_minutes>", "Invalid Input", MB_OK | MB_ICONERROR);
        return 1;
    }

    const char CLASS_NAME[] = "ExamWindowClass";

    // Register Window Class
    WNDCLASS wc = {};
    wc.lpfnWndProc   = WndProc;
    wc.hInstance     = hInstance;
    wc.lpszClassName = CLASS_NAME;
    wc.hCursor       = LoadCursor(NULL, IDC_ARROW); // Show mouse cursor

    RegisterClass(&wc);

    // Get screen dimensions
    int width = GetSystemMetrics(SM_CXSCREEN);
    int height = GetSystemMetrics(SM_CYSCREEN);

    // Create fullscreen, always-on-top window
    HWND hwnd = CreateWindowEx(
        WS_EX_TOPMOST,
        CLASS_NAME, "Virtual Exam Window",
        WS_POPUP,
        0, 0, width, height,
        NULL, NULL, hInstance, NULL
    );

    if (!hwnd) return 0;

    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);

    // Start timer thread
    CreateThread(NULL, 0, TimerThread, &durationMinutes, 0, NULL);

    // Message loop
    MSG msg = {};
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return 0;
}

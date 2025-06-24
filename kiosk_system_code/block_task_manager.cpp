#include <windows.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <cstdlib>

bool SetTaskManagerState(bool disable) {
    HKEY hKey;
    LPCSTR keyPath = "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System";

    if (RegCreateKeyExA(HKEY_CURRENT_USER, keyPath, 0, NULL, 0, KEY_WRITE, NULL, &hKey, NULL) != ERROR_SUCCESS) {
        std::cerr << "Failed to open registry key!" << std::endl;
        return false;
    }

    DWORD value = disable ? 1 : 0;

    if (RegSetValueExA(hKey, "DisableTaskMgr", 0, REG_DWORD, (const BYTE*)&value, sizeof(value)) != ERROR_SUCCESS) {
        std::cerr << "Failed to set registry value!" << std::endl;
        RegCloseKey(hKey);
        return false;
    }

    RegCloseKey(hKey);
    return true;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <duration_in_minutes>" << std::endl;
        return 1;
    }

    int durationMinutes = std::atoi(argv[1]);
    if (durationMinutes <= 0) {
        std::cerr << "Please provide a valid duration (positive integer)." << std::endl;
        return 1;
    }

    std::cout << "Disabling Task Manager for " << durationMinutes << " minutes..." << std::endl;

    if (!SetTaskManagerState(true)) {
        std::cerr << "Failed to disable Task Manager." << std::endl;
        return 1;
    }

    std::cout << "Task Manager disabled. Exam started..." << std::endl;

    // Sleep for given duration
    std::this_thread::sleep_for(std::chrono::minutes(durationMinutes));

    std::cout << "Exam ended. Re-enabling Task Manager..." << std::endl;

    if (SetTaskManagerState(false)) {
        std::cout << "Task Manager re-enabled successfully." << std::endl;
    } else {
        std::cerr << "Failed to re-enable Task Manager." << std::endl;
    }

    return 0;
}

/*
 * Minimal native launcher for the pyemsi Windows portable runtime.
 *
 * Compile with MSVC (the builder does this automatically):
 *
 *   GUI app launcher (no console window):
 *     cl /nologo /O2 /DNO_CONSOLE launcher.c /Fe:pyemsi.exe
 *        /link /SUBSYSTEM:WINDOWS /ENTRY:wmainCRTStartup
 *
 *   Script runner (console window):
 *     cl /nologo /O2 /DSCRIPT_MODE launcher.c /Fe:run_script.exe
 */

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <stdio.h>

#ifndef APP_MODULE
#define APP_MODULE "pyemsi.gui"
#endif
#define _WIDEN2(s) L##s
#define _WIDEN(s) _WIDEN2(s)

static BOOL get_base_dir(wchar_t *buf, DWORD len) {
    DWORD n = GetModuleFileNameW(NULL, buf, len);
    if (n == 0 || n >= len) return FALSE;
    wchar_t *sep = wcsrchr(buf, L'\\');
    if (sep) *(sep + 1) = L'\0';
    return TRUE;
}

static void setup_environment(const wchar_t *base) {
    wchar_t val[4096];

    _snwprintf_s(val, 4096, _TRUNCATE, L"%sruntime", base);
    SetEnvironmentVariableW(L"PYTHONHOME", val);

    _snwprintf_s(val, 4096, _TRUNCATE, L"%sapp", base);
    SetEnvironmentVariableW(L"PYTHONPATH", val);

    wchar_t old_path[4096] = {0};
    GetEnvironmentVariableW(L"PATH", old_path, 4096);
    _snwprintf_s(val, 4096, _TRUNCATE,
                 L"%sruntime;%sruntime\\Scripts;%s",
                 base, base, old_path);
    SetEnvironmentVariableW(L"PATH", val);
}

int wmain(int argc, wchar_t *argv[]) {
    wchar_t base[MAX_PATH];
    if (!get_base_dir(base, MAX_PATH)) {
        fwprintf(stderr, L"Failed to resolve launcher directory.\n");
        return 1;
    }
    setup_environment(base);

    wchar_t python[MAX_PATH];
    _snwprintf_s(python, MAX_PATH, _TRUNCATE, L"%sruntime\\python.exe", base);

    /* ── Build command line ──────────────────────────────── */
    wchar_t cmdline[8192];
    int pos;

#ifdef SCRIPT_MODE
    if (argc < 2) {
        fwprintf(stderr, L"Usage: %s <script.py> [args...]\n", argv[0]);
        return 1;
    }
    pos = _snwprintf_s(cmdline, 8192, _TRUNCATE,
                       L"\"%s\" \"%s\"", python, argv[1]);
    for (int i = 2; i < argc && pos > 0 && pos < 8191; i++)
        pos += _snwprintf_s(cmdline + pos, 8192 - pos, _TRUNCATE,
                            L" \"%s\"", argv[i]);
#else
    pos = _snwprintf_s(cmdline, 8192, _TRUNCATE,
                       L"\"%s\" -m %s", python, _WIDEN(APP_MODULE));
    for (int i = 1; i < argc && pos > 0 && pos < 8191; i++)
        pos += _snwprintf_s(cmdline + pos, 8192 - pos, _TRUNCATE,
                            L" \"%s\"", argv[i]);
#endif

    /* ── Spawn python and wait ──────────────────────────── */
    STARTUPINFOW si = { .cb = sizeof(si) };
    PROCESS_INFORMATION pi = {0};

    /* Create a job object so that all child processes (LSP servers, etc.)
       are automatically terminated when the launcher exits.              */
    HANDLE job = CreateJobObjectW(NULL, NULL);
    if (job) {
        JOBOBJECT_EXTENDED_LIMIT_INFORMATION jeli = {0};
        jeli.BasicLimitInformation.LimitFlags =
            JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        SetInformationJobObject(job, JobObjectExtendedLimitInformation,
                                &jeli, sizeof(jeli));
    }

    DWORD flags = CREATE_SUSPENDED;
#ifdef NO_CONSOLE
    flags |= CREATE_NO_WINDOW;
#endif

    if (!CreateProcessW(python, cmdline, NULL, NULL, TRUE,
                        flags, NULL, NULL, &si, &pi)) {
        fwprintf(stderr, L"Failed to start Python (error %lu).\n",
                 GetLastError());
        if (job) CloseHandle(job);
        return 1;
    }

    if (job) AssignProcessToJobObject(job, pi.hProcess);
    ResumeThread(pi.hThread);

    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD exit_code = 1;
    GetExitCodeProcess(pi.hProcess, &exit_code);
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    if (job) CloseHandle(job);   /* kills all remaining child processes */
    return (int)exit_code;
}

# Evidence Checklist

Use this checklist to gather Windows stability evidence before recommending repairs.

## Minimum Timeline

- Ask for the exact local time of each crash or restart.
- Note the workload: downloading, gaming, idle, boot, model loading, browser, file copy, or install.
- Note recent changes: new app, driver update, Windows update, BIOS setting, new RAM/SSD/GPU, overclock, undervolt, EXPO/XMP/PBO/Curve Optimizer.

## Built-In Evidence Sources

- Reliability Monitor: `perfmon /rel`
- Event Viewer:
  - System log around the crash time.
  - Application log around the crash time.
  - Look for `Kernel-Power`, `BugCheck`, `WHEA-Logger`, `Disk`, `stornvme`, `nvlddmkm`, `amdkmdag`, `Display`, `volmgr`, `Ntfs`.
- Dump files:
  - `C:\Windows\Minidump\*.dmp`
  - `C:\Windows\MEMORY.DMP`
  - Copy dumps to a working folder before heavy analysis if prior reads caused freezes.
- Windows Memory Diagnostic:
  - Event Viewer -> System -> `MemoryDiagnostics-Results`
- Storage health:
  - `Get-PhysicalDisk`
  - `Get-Disk`
  - vendor tools when available, such as Samsung Magician, WD Dashboard, Crucial Storage Executive.
- Driver inventory:
  - Device Manager for warning icons.
  - `driverquery /v /fo csv`
  - GPU, chipset, storage controller, network, and USB drivers.
- Startup and services:
  - Task Manager Startup tab.
  - `Get-CimInstance Win32_StartupCommand`
  - `Get-Service | Where-Object Status -eq Running`

## Evidence Table Columns

Use this table shape:

| Time | Source | Signal | Possible meaning | Confidence |
| --- | --- | --- | --- | --- |

Confidence guide:

- High: repeated signal, timestamp matches, same component appears in multiple sources.
- Medium: timestamp matches but component could be victim rather than cause.
- Low: generic crash signal, no correlation yet.

## Red Flags

- Repeated WHEA errors or cache hierarchy errors.
- NVMe resets, storage controller timeouts, or disk warnings around download/file-write workloads.
- Memory corruption bugchecks naming random unrelated drivers.
- Crashes only after enabling EXPO/XMP/PBO/undervolt.
- Kernel-Power without BugCheck can indicate hard power loss, firmware reset, PSU, thermal shutdown, or an abrupt hang.

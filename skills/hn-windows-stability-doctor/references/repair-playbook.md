# Repair Playbook

Choose repairs from evidence. Prefer reversible, low-risk actions first.

## Driver Or Software Layer

Use when evidence points to a specific driver, app, or service.

- Update or clean reinstall the implicated driver.
- Remove recently installed low-level software: download accelerators, VPN/network filters, RGB tools, anti-cheat, disk tools, virtual devices.
- Disable startup items linked to the crash window and verify.
- Run Windows Update after vendor-critical drivers are handled.

Verification:

- Reboot.
- Recheck Event Viewer for new errors.
- Replay the workload that triggered the crash.

## Storage Layer

Use when there are NVMe resets, disk warnings, file-write/download correlation, or SMART warnings.

- Back up important files first if disk health is uncertain.
- Update NVMe/chipset/storage drivers from the motherboard or SSD vendor.
- Update SSD firmware with the vendor tool only when evidence supports it.
- Check cable/slot/thermal issues for SATA or add-in cards.
- Avoid stress-writing a suspicious disk before backup.

Verification:

- Confirm no new `Disk`, `stornvme`, `Ntfs`, or controller warnings during workload replay.

## Memory Or CPU Stability

Use when bugchecks are random, WHEA appears, memory diagnostics fail, or EXPO/PBO/Curve Optimizer is enabled.

- Return BIOS performance settings to stock first.
- Disable EXPO/XMP temporarily.
- Disable PBO and Curve Optimizer temporarily.
- Test memory one stick at a time only when basic software checks point to hardware.
- Consider BIOS update only after documenting current version, board model, release notes, BitLocker status, and rollback constraints.

Verification:

- Re-run the triggering workload.
- Run a memory test appropriate to the user's tolerance.
- Compare crash frequency and WHEA/memory signals.

## BIOS And Firmware

Treat BIOS flashing as high-risk.

Before recommending:

- Confirm exact motherboard/laptop model.
- Check current BIOS version.
- Check BitLocker status and recovery key availability.
- Read release notes for stability, AGESA, memory compatibility, storage, or GPU fixes.
- Ensure stable power.

Recommend BIOS only when:

- The evidence points to firmware/memory/platform instability, or
- The current BIOS is known problematic and release notes match the symptom, or
- Lower-risk driver/config repairs failed.

## Response Discipline

Never say "fixed" until verification passes. Say "the evidence now supports..." or "no new crashes were observed during...".

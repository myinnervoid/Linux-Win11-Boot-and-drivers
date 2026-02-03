# 🐧 WinUSB Creator Ultimate

**The Swiss Army Knife for flashing ISOs on Linux.**

Create bootable USBs for Windows (UEFI/Secure Boot), Linux, and other systems, verify ISO integrity, and fix driver issues—all in one modern app.

![Logo](logo.png)

## ✨ Key Features

*   **🔥 Windows Mode (UEFI & Secure Boot):**
    *   Bypasses the FAT32 4GB limit by automatically splitting the `install.wim` file.
    *   **Driver Injection (VMD/RST):** Fixes "No drive found" errors on modern Intel laptops by injecting storage drivers into the USB.

*   **🐧 Universal Mode (DD):**
    *   Flash Linux distros (Ubuntu, Fedora, Mint), Raspberry Pi images, or generic raw images reliably.

*   **🛡️ Integrity Verifier:**
    *   Check your ISO checksums (MD5, SHA1, SHA256) before flashing to avoid corrupted installations.

*   **🎨 Modern UI:**
    *   Dark mode, real-time progress bars, and detailed status logs.

## 🚀 Quick Install

Open your terminal and run:

1.  **Clone & Enter**
    ```bash
    git clone https://github.com/myinnervoid/Linux-Win11-Boot-and-drivers.git
    cd Linux-Win11-Boot-and-drivers
    ```

2.  **One-Click Setup**
    This script installs dependencies and creates a desktop shortcut.
    ```bash
    sudo ./setup.sh
    ```

3.  **Run**
    Search for "WinUSB Creator" in your app menu or run:
    ```bash
    sudo python3 src/main.py
    ```

## ⚠️ Permissions

This tool requires root (`sudo`) permissions to format USB drives and write boot sectors.

## 📄 License

Open Source. Built with ❤️ by myinnervoid.

# 🐧 WinUSB Creator Ultimate

**La navaja suiza para grabar ISOs en Linux.**

Crea USBs booteables de Windows (UEFI/Secure Boot), Linux y otros sistemas, verifica la integridad de tus descargas y soluciona problemas de drivers, todo en una sola App.

![Logo](logo.png)

## ✨ Características Principales

*   **🔥 Modo Windows (UEFI & Secure Boot):**
    *   Soluciona el límite de 4GB de FAT32 dividiendo automáticamente el archivo `install.wim`.
    *   **Inyección de Drivers (VMD/RST):** ¿Tu laptop Intel de 11ª/12ª/13ª gen no detecta el disco al instalar? Esta herramienta inyecta los drivers automáticamente.

*   **🐧 Modo Universal (DD):**
    *   Graba distros de Linux (Ubuntu, Fedora, Mint), imágenes de Raspberry Pi, o incluso imágenes RAW de macOS de forma segura.

*   **🛡️ Verificador de Integridad (Checksum):**
    *   Antes de grabar, comprueba que tu ISO no esté corrupta. Soporta MD5, SHA1, SHA256 y SHA512 automáticamente.

*   **🎨 Interfaz Moderna:**
    *   Modo oscuro nativo, barras de progreso reales y logs detallados.

## 🚀 Instalación Rápida (Para Principiantes)

Abre tu terminal (Ctrl+Alt+T) y pega estos comandos uno por uno:

1.  **Descargar**
    ```bash
    git clone https://github.com/myinnervoid/Linux-Win11-Boot-and-drivers.git
    cd Linux-Win11-Boot-and-drivers
    ```

2.  **Instalar todo (Dependencias + Icono en Menú)**
    Este script instalará lo necesario y creará el acceso directo en tu menú de aplicaciones.
    ```bash
    sudo ./setup.sh
    ```

3.  **¡Listo!**
    Busca "WinUSB Creator" en tu menú de inicio o ejecútalo desde la terminal con:
    ```bash
    sudo python3 src/main.py
    ```

## 🛠️ Requisitos Manuales

Si prefieres no usar el script automático, necesitas instalar:
*   **Sistema:** `wimtools`, `parted`, `dosfstools`, `ntfs-3g`, `python3-tk`, `python3-pip`.
*   **Python:** `customtkinter`, `psutil`.

## ⚠️ Nota sobre Permisos

Esta aplicación requiere contraseña de administrador (`sudo`) porque necesita formatear discos USB y modificar particiones. Es completamente seguro y el código es abierto.

## 📄 Licencia

Open Source. Creado para la comunidad ❤️ por myinnervoid + Gemini Pro + Antigravity


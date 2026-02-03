#!/bin/bash

# Obtener la ruta absoluta del directorio actual
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ICON_PATH="$DIR/logo.png"
EXEC_PATH="$DIR/src/main.py"

echo "Configurando acceso directo..."
echo "Directorio del proyecto: $DIR"

# Verificar si existe el logo, si no, intentar usar uno del sistema o descargar
if [ ! -f "$ICON_PATH" ]; then
    echo "⚠️ No se encontró logo.png. Usando icono genérico."
    ICON_NAME="system-run"
else
    ICON_NAME="$ICON_PATH"
fi

# Crear contenido del archivo .desktop
# Usamos 'sh -c' para pedir sudo gráficamente o en terminal
DESKTOP_ENTRY="[Desktop Entry]
Version=1.0
Name=WinUSB Creator Ultimate
Comment=Graba ISOs de Windows y Linux fácilmente
Exec=sudo python3 \"$EXEC_PATH\"
Icon=$ICON_NAME
Terminal=true
Type=Application
Categories=Utility;System;
Actions=RunAsRoot

[Desktop Action RunAsRoot]
Name=Ejecutar como Root
Exec=sudo python3 \"$EXEC_PATH\"
"

# Escribir en la carpeta de aplicaciones del usuario
echo "$DESKTOP_ENTRY" > ~/.local/share/applications/winusb-creator.desktop

# Dar permisos de ejecución
chmod +x ~/.local/share/applications/winusb-creator.desktop

# Copiar también al escritorio si existe la carpeta Desktop o Escritorio
if [ -d ~/Desktop ]; then
    cp ~/.local/share/applications/winusb-creator.desktop ~/Desktop/
    chmod +x ~/Desktop/winusb-creator.desktop
elif [ -d ~/Escritorio ]; then
    cp ~/.local/share/applications/winusb-creator.desktop ~/Escritorio/
    chmod +x ~/Escritorio/winusb-creator.desktop
fi

echo "✅ ¡Acceso directo creado! Busca 'WinUSB Creator' en tu menú."

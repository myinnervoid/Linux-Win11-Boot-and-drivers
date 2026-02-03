#!/bin/bash

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Instalador Todo-en-Uno WinUSB Creator ===${NC}"

# 1. Verificar si es root para instalar dependencias
if [ "$EUID" -ne 0 ]; then 
  echo -e "${RED}Por favor, ejecuta este script con sudo:${NC}"
  echo "sudo ./setup.sh"
  exit 1
fi

echo -e "${YELLOW}[1/4] Actualizando lista de paquetes...${NC}"
apt-get update

echo -e "${YELLOW}[2/4] Instalando herramientas del sistema (wimtools, parted, etc)...${NC}"
apt-get install -y wimtools parted dosfstools python3-tk python3-pip ntfs-3g python3-psutil git

echo -e "${YELLOW}[3/4] Instalando librerías gráficas de Python...${NC}"
# Instalar dependencias de Python
pip3 install customtkinter psutil --break-system-packages

# Ajustar permisos para que el usuario normal pueda ejecutar el script de acceso directo
echo -e "${YELLOW}[4/4] Creando accesos directos...${NC}"

# Obtenemos el usuario real (no root) para instalar el icono en su home
REAL_USER=${SUDO_USER:-$USER}
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Ejecutar el script de acceso directo como el usuario normal (no root)
# para que el icono quede en /home/usuario/.local/share/applications
sudo -u $REAL_USER bash "$DIR/install_shortcut.sh"

echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}      ¡INSTALACIÓN COMPLETADA CON ÉXITO!     ${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo "1. Puedes buscar 'WinUSB Creator' en tu menú de inicio."
echo "2. O ejecutarlo ahora mismo con: sudo python3 src/main.py"
echo ""

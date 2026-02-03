import customtkinter as ctk
from tkinter import filedialog, messagebox
import hashlib
import os
import threading
import time
import subprocess
import shutil
import sys

# Configuración visual
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class WinUSBCreatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WinUSB Creator Ultimate")
        self.geometry("750x650")
        
        # Layout principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Contenedor de vistas
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Instanciar las vistas
        self.vista_grabador = FrameGrabador(self.container, self)
        self.vista_verificador = FrameVerificador(self.container, self)

        # Mostrar inicial
        self.mostrar_grabador()
        
        # Validar dependencias al inicio
        self.check_dependencies()

    def mostrar_grabador(self):
        self.vista_verificador.grid_forget()
        self.vista_grabador.grid(row=0, column=0, sticky="nsew")

    def mostrar_verificador(self):
        self.vista_grabador.grid_forget()
        self.vista_verificador.grid(row=0, column=0, sticky="nsew")

    def check_dependencies(self):
        """Verifica si las herramientas del sistema necesarias están instaladas."""
        required_tools = ["wimsplit", "parted", "mkfs.fat", "rsync"]
        # dd usually exists, but we can check it
        if subprocess.call("which dd", shell=True, stdout=subprocess.DEVNULL) != 0:
             required_tools.append("dd")

        missing = []
        tool_package_map = {
            "wimsplit": "wimtools",
            "parted": "parted",
            "mkfs.fat": "dosfstools",
            "rsync": "rsync",
            "dd": "coreutils"
        }
        for tool in required_tools:
            if shutil.which(tool) is None:
                missing.append(tool)
        
        if missing:
            pkg_names = [tool_package_map.get(t, t) for t in missing]
            msg = f"Faltan herramientas: {', '.join(missing)}.\nInstala: {', '.join(pkg_names)}"
            messagebox.showwarning("Dependencias Faltantes", msg)


class FrameGrabador(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.is_working = False
        
        # --- ENCABEZADO ---
        self.lbl_titulo = ctk.CTkLabel(self, text="WinUSB Creator", font=("Roboto", 26, "bold"))
        self.lbl_titulo.pack(pady=(20, 5))
        self.lbl_sub = ctk.CTkLabel(self, text="Multi-Boot: Windows, Linux & Más", text_color="gray")
        self.lbl_sub.pack(pady=(0, 20))

        # --- SELECTOR DE MODO ---
        self.frame_modo = ctk.CTkFrame(self)
        self.frame_modo.pack(fill="x", padx=30, pady=5)
        
        ctk.CTkLabel(self.frame_modo, text="Modo de Grabación:", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        self.combo_modo = ctk.CTkComboBox(self.frame_modo, 
                                          values=["Windows (UEFI/SecureBoot)", "Linux / Otros (Modo DD)"],
                                          command=self.cambiar_modo, width=250)
        self.combo_modo.set("Windows (UEFI/SecureBoot)")
        self.combo_modo.pack(side="left", padx=10)

        # --- SELECCIÓN DE ISO ---
        ctk.CTkLabel(self, text="1. Imagen de Disco (ISO):", anchor="w").pack(fill="x", padx=30, pady=(15,0))
        self.frame_iso = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_iso.pack(fill="x", padx=30, pady=5)
        
        self.entry_iso = ctk.CTkEntry(self.frame_iso, placeholder_text="Selecciona tu archivo .iso")
        self.entry_iso.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.btn_iso = ctk.CTkButton(self.frame_iso, text="📂 Buscar ISO", width=100, command=self.seleccionar_iso)
        self.btn_iso.pack(side="right")

        # --- SELECCIÓN DE USB ---
        ctk.CTkLabel(self, text="2. Dispositivo USB:", anchor="w").pack(fill="x", padx=30, pady=(15,0))
        self.frame_usb = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_usb.pack(fill="x", padx=30, pady=5)
        
        self.combo_usb = ctk.CTkComboBox(self.frame_usb, values=["Escaneando..."])
        self.combo_usb.pack(side="left", fill="x", expand=True, padx=(0,10))
        self.btn_refresh = ctk.CTkButton(self.frame_usb, text="🔄", width=40, command=self.escanear_usbs)
        self.btn_refresh.pack(side="right")

        # --- DRIVERS (Solo visible en modo Windows) ---
        self.frame_drivers = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_drivers.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(self.frame_drivers, text="3. Drivers VMD/RST (Opcional):", anchor="w").pack(fill="x")
        self.entry_drivers = ctk.CTkEntry(self.frame_drivers, placeholder_text="Carpeta de drivers extraídos...")
        self.entry_drivers.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.btn_drivers = ctk.CTkButton(self.frame_drivers, text="Elegir", width=80, command=self.seleccionar_drivers)
        self.btn_drivers.pack(side="right")

        # --- CONSOLA Y PROGRESO ---
        self.textbox = ctk.CTkTextbox(self, height=100)
        self.textbox.pack(fill="x", padx=30, pady=10)
        
        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(fill="x", padx=30, pady=5)
        self.progress.set(0)

        # --- BOTONES DE ACCIÓN ---
        self.btn_grabar = ctk.CTkButton(self, text="🔥 QUEMAR USB 🔥", 
                                        fg_color="#e74c3c", hover_color="#c0392b", 
                                        height=45, font=("Arial", 14, "bold"),
                                        command=self.iniciar_grabacion)
        self.btn_grabar.pack(fill="x", padx=30, pady=10)

        # Botón para ir al verificador (Fijo abajo)
        self.btn_verificar = ctk.CTkButton(self, text="🛡️ Ir al Verificador de ISOs", 
                                           command=self.controller.mostrar_verificador,
                                           fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
        self.btn_verificar.pack(side="bottom", pady=20)
        
        # Inicializar
        self.escanear_usbs()

    def log(self, mensaje):
        self.after(0, lambda: self._log_internal(mensaje))
    
    def _log_internal(self, msg):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", f"> {msg}\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def cambiar_modo(self, eleccion):
        if "Windows" in eleccion:
            self.frame_drivers.pack(fill="x", padx=30, pady=10) # Mostrar drivers
            self.log("Modo seleccionado: Windows (Descomprimir + WIM Split)")
        else:
            self.frame_drivers.pack_forget() # Ocultar drivers
            self.log("Modo seleccionado: Linux/Raw (Copia directa DD)")

    def escanear_usbs(self):
        try:
            cmd = "lsblk -d -o NAME,SIZE,MODEL,TRAN,TYPE | grep usb"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            devices = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 1:
                        dev_name = parts[0]
                        size = parts[1] if len(parts) > 1 else "?"
                        model = " ".join(parts[2:]) if len(parts) > 2 else "USB"
                        info = f"/dev/{dev_name} ({size} - {model})"
                        devices.append(info)
            
            if not devices: devices = ["No se detectaron USBs"]
            self.combo_usb.configure(values=devices)
            self.combo_usb.set(devices[0])
        except Exception as e:
            self.combo_usb.configure(values=[f"Error: {str(e)}"])

    def seleccionar_iso(self):
        filename = filedialog.askopenfilename(filetypes=[("Archivos ISO", "*.iso"), ("Imágenes", "*.img")])
        if filename:
            self.entry_iso.delete(0, "end")
            self.entry_iso.insert(0, filename)
    
    def seleccionar_drivers(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_drivers.delete(0, "end")
            self.entry_drivers.insert(0, folder)
            self.log(f"Carpeta de drivers: {os.path.basename(folder)}")

    def iniciar_grabacion(self):
        if self.is_working: return

        iso = self.entry_iso.get()
        usb_display = self.combo_usb.get()
        usb_device = usb_display.split()[0] # Obtener /dev/sdx
        modo = self.combo_modo.get()
        
        if "No" in usb_display or not iso:
            messagebox.showwarning("Faltan datos", "Selecciona ISO y USB.")
            return
        
        if not os.path.exists(iso):
            messagebox.showerror("Error", "El archivo ISO no existe.")
            return

        if messagebox.askyesno("¡ADVERTENCIA DE DATOS!", 
                               f"SE BORRARÁ TODO EN:\n{usb_device}\n\n¿Estás seguro de continuar?"):
            
            if os.geteuid() != 0:
                messagebox.showerror("Error de Permisos", "Debes ejecutar con sudo.")
                return

            self.is_working = True
            self.btn_grabar.configure(state="disabled", text="PROCESANDO...", fg_color="#7f8c8d")
            threading.Thread(target=self.proceso_grabacion, args=(iso, usb_device, self.entry_drivers.get(), modo), daemon=True).start()

    def run_command(self, cmd):
        self.log(f"CMD: {cmd[:40]}...")
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise Exception(f"Fallo comando: {cmd}\n{stderr}")
        return stdout

    def cleanup_temp_dirs(self, *dirs):
        for d in dirs:
            if os.path.exists(d):
                try: os.rmdir(d)
                except: pass

    def proceso_grabacion(self, iso, device, driver_path, modo):
        try:
            if "Windows" in modo:
                self.proceso_windows(iso, device, driver_path)
            else:
                self.proceso_linux_dd(iso, device)

            self.log("✅ ¡PROCESO FINALIZADO CON ÉXITO!")
            self.after(0, lambda: messagebox.showinfo("Éxito", "Tu USB está listo."))

        except Exception as e:
            self.log(f"❌ ERROR: {str(e)}")
            self.after(0, lambda: messagebox.showerror("Error Crítico", str(e)))
        finally:
            self.is_working = False
            self.after(0, self.reset_ui)

    def reset_ui(self):
        self.btn_grabar.configure(state="normal", text="🔥 QUEMAR USB 🔥", fg_color="#e74c3c")
        self.progress.stop()
        self.progress.set(0)
        self.progress.configure(mode="determinate")

    def proceso_windows(self, iso_path, usb_device, driver_path):
        mnt_iso = "/tmp/winusb_iso_mnt"
        mnt_usb = "/tmp/winusb_target_mnt"
        
        try:
            self.progress.configure(mode="indeterminate")
            self.progress.start()

            self.log("--- MODO WINDOWS UEFI ---")
            self.log("Limpiando USB (gdisk/parted)...")
            subprocess.run(f"umount {usb_device}* 2>/dev/null", shell=True)
            self.run_command(f"mkdir -p {mnt_iso}")
            self.run_command(f"mkdir -p {mnt_usb}")

            self.log("Creando tabla particiones GPT...")
            self.run_command(f"parted -s {usb_device} mklabel gpt")
            self.run_command(f"parted -s {usb_device} mkpart primary fat32 1MiB 100%")
            time.sleep(1)
            
            usb_part = f"{usb_device}1"
            if not os.path.exists(usb_part):
                subprocess.run("partprobe", shell=True)
                time.sleep(2)

            self.log("Formateando FAT32...")
            self.run_command(f"mkfs.fat -F 32 -n 'WIN_BOOT' {usb_part}")

            self.log("Montando imágenes...")
            self.run_command(f"mount -o loop,ro '{iso_path}' {mnt_iso}")
            self.run_command(f"mount {usb_part} {mnt_usb}")

            self.log("Copiando archivos (Rsync)...")
            # Excluir install.wim/esd
            rsync_cmd = f"rsync -r --info=progress2 --exclude='sources/install.wim' --exclude='sources/install.esd' '{mnt_iso}/' '{mnt_usb}/'"
            if subprocess.call(rsync_cmd, shell=True) != 0:
                raise Exception("Error copiando archivos base.")

            # Manejo WIM
            wim_source = f"{mnt_iso}/sources/install.wim"
            if not os.path.exists(wim_source): wim_source = f"{mnt_iso}/sources/install.esd"
            
            wim_target_dir = f"{mnt_usb}/sources"
            
            if os.path.exists(wim_source):
                size_gb = os.path.getsize(wim_source) / (1024**3)
                self.log(f"Imagen sistema: {size_gb:.2f} GB")

                if size_gb > 4.0:
                    self.log("Dividiendo WIM (Split) para FAT32...")
                    wim_target_swm = f"{wim_target_dir}/install.swm"
                    self.run_command(f"wimsplit '{wim_source}' '{wim_target_swm}' 3800")
                else:
                    self.log("Copiando WIM directo...")
                    shutil.copy2(wim_source, f"{wim_target_dir}/{os.path.basename(wim_source)}")
            else:
                self.log("⚠️ No se encontró install.wim/esd.")

            # Drivers
            if driver_path and os.path.exists(driver_path):
                self.log("Inyectando Drivers VMD...")
                dest = f"{mnt_usb}/Drivers/VMD"
                self.run_command(f"mkdir -p '{dest}'")
                subprocess.call(f"cp -r '{driver_path}/.' '{dest}/'", shell=True)

            self.log("Sincronizando disco (Sync)...")
            self.run_command("sync")
            self.log("Desmontando...")
            subprocess.run(f"umount {mnt_iso}", shell=True)
            subprocess.run(f"umount {mnt_usb}", shell=True)
            self.cleanup_temp_dirs(mnt_iso, mnt_usb)

        except Exception as e:
            self.cleanup_temp_dirs(mnt_iso, mnt_usb)
            raise e

    def proceso_linux_dd(self, iso, device):
        self.log("--- MODO LINUX / RAW (DD) ---")
        self.log(f"Target: {device}")
        
        subprocess.run(f"umount {device}* 2>/dev/null", shell=True)
        
        # DD Visual
        cmd = f"dd if='{iso}' of={device} bs=4M status=progress oflag=sync"
        self.log(f"Comando: {cmd}")
        self.log("Escribiendo imagen... Por favor espera.")

        # Usamos Popoen para que no bloquee totalmente, aunque leer stderr es complejo en loop simple
        process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, text=True)
        
        self.progress.configure(mode="indeterminate")
        self.progress.start()
        
        # Esperar finish
        while process.poll() is None:
            time.sleep(0.5)
            # Podríamos leer process.stderr.readline() para parsear progreso, 
            # pero 'status=progress' ensucia mucho el output buffer.
            # Nos conformamos con la animación.

        if process.returncode != 0:
            raise Exception("DD falló. Verifica el log/terminal.")

        self.log("Sincronizando cache...")
        subprocess.run("sync", shell=True)


class FrameVerificador(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Título
        ctk.CTkLabel(self, text="Verificador de Integridad ISO", font=("Roboto", 22, "bold")).pack(pady=20)
        
        # Input Archivo
        frame_f = ctk.CTkFrame(self, fg_color="transparent")
        frame_f.pack(fill="x", padx=40)
        self.entry_file = ctk.CTkEntry(frame_f, placeholder_text="Archivo a verificar")
        self.entry_file.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(frame_f, text="Buscar", width=80, command=self.buscar).pack(side="right", padx=5)

        # Input Hash
        ctk.CTkLabel(self, text="Hash Esperado (SHA256, MD5...):", anchor="w").pack(fill="x", padx=40, pady=(20,0))
        self.entry_hash = ctk.CTkEntry(self, placeholder_text="Pega el código aquí")
        self.entry_hash.pack(fill="x", padx=40, pady=5)

        # Estado
        self.lbl_status = ctk.CTkLabel(self, text="Esperando...", text_color="gray")
        self.lbl_status.pack(pady=20)
        
        self.progreso = ctk.CTkProgressBar(self)
        self.progreso.pack(fill="x", padx=40)
        self.progreso.set(0)

        # Botón Verificar
        self.btn_verificar = ctk.CTkButton(self, text="VERIFICAR", command=self.verificar, fg_color="#2ecc71")
        self.btn_verificar.pack(pady=20)

        # Botón Volver (Fijo abajo)
        ctk.CTkButton(self, text="← Volver al Grabador USB", 
                      command=self.controller.mostrar_grabador,
                      fg_color="transparent", border_width=1).pack(side="bottom", pady=20)

    def buscar(self):
        f = filedialog.askopenfilename()
        if f: 
            self.entry_file.delete(0, "end")
            self.entry_file.insert(0, f)

    def verificar(self):
        threading.Thread(target=self.logica_hash).start()

    def logica_hash(self):
        ruta = self.entry_file.get()
        esperado = self.entry_hash.get().strip().lower()

        if not ruta or not esperado:
            self.lbl_status.configure(text="Faltan datos.")
            return

        longitudes = {32: "md5", 40: "sha1", 64: "sha256", 128: "sha512"}
        algo = longitudes.get(len(esperado))
        
        if not algo:
            self.lbl_status.configure(text="Hash desconocido.")
            return

        self.btn_verificar.configure(state="disabled")
        try:
            sz = os.path.getsize(ruta)
            h = hashlib.new(algo)
            leido = 0
            
            with open(ruta, "rb") as f:
                while True:
                    chunk = f.read(1024*1024)
                    if not chunk: break
                    h.update(chunk)
                    leido += len(chunk)
                    self.progreso.set(leido / sz)

            res = h.hexdigest()
            if res == esperado:
                self.lbl_status.configure(text="✅ COINCIDE", text_color="#2ecc71")
                messagebox.showinfo("OK", "El archivo es auténtico.")
            else:
                self.lbl_status.configure(text="❌ NO COINCIDE", text_color="red")
                messagebox.showerror("Error", f"Difiere.\nReal: {res}")

        except Exception as e:
           self.lbl_status.configure(text=f"Error: {e}")
        finally:
            self.btn_verificar.configure(state="normal")


if __name__ == "__main__":
    app = WinUSBCreatorApp()
    app.mainloop()

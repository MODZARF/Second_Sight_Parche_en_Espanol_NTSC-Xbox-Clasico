import os
import sys
import time
import zlib
import lzma
import hashlib
import struct
import json
import shutil
import ipaddress
from ftplib import FTP
import tkinter as tk
from tkinter import filedialog

#Sistema de parcheo basado en deltas.
#Este parche es un beta, no trate de usarlo con otros "parche.ZARF"

os.system('')

print(r"""
            ________      ________      ________      ________ 
---------- |\_____  \    |\   __  \    |\   __  \    |\  _____\----------------
----------  \|___/  /|   \ \  \|\  \   \ \  \|\  \   \ \  \__/ ---------------
--------------  /  / /    \ \   __  \   \ \   _  _\   \ \   __\--------------
-------------- /  /_/__    \ \  \ \  \   \ \  \\  \|   \ \  \_|----------------
------------- |\________\   \ \__\ \__\   \ \__\\ _\    \ \__\ ----------------
-------------- \|_______|    \|__|\|__|    \|__|\|__|    \|__| -----------------
""")

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_red(msg):
    print(f"{Colors.RED}{msg}{Colors.RESET}")

def print_green(msg):
    print(f"{Colors.GREEN}{msg}{Colors.RESET}")

def print_cyan(msg):
    print(f"{Colors.CYAN}{msg}{Colors.RESET}")

print_green("Parche textos en español en NTSC Second Sight - Xbox Clásico")

def calcular_crc32(filepath):
    crc = 0
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            crc = zlib.crc32(chunk, crc)
    return crc & 0xFFFFFFFF


def aplicar_parche_zarf():
    patch_path = "parche.ZARF"

    if not os.path.exists(patch_path):
        print_red("Parche ZARF no existe")
        input("\nPresione ENTER para salir...")
        return

    # Menú de selección de modo
    while True:
        print("\nSelecciona el modo de parcheo")
        print("1 Local")
        print("2 FTP")
        opcion = input("Ingrese opción (1 o 2): ").strip()

        if opcion == "1":
            modo_ftp = False
            break
        elif opcion == "2":
            modo_ftp = True
            break
        else:
            print_red("Opción invalida")

    target_dir = ""
    temp_dir = "temp_ftp_zarf"
    ftp_conexion = None
    ruta_remota_dir = ""
    archivo_remoto_nombre = "ss_ntsc.xbe"

    if modo_ftp:
        # Validación de IP
        while True:
            ip_input = input("Introduce la IP de la consola [192.168.0.3]: ").strip()
            if not ip_input:
                ip_input = "192.168.0.3"
            try:
                ipaddress.ip_address(ip_input)
                ip_consola = ip_input
                break
            except ValueError:
                print_red("IP invalida")

        usuario = input("Introduce el usuario [xbox]: ").strip()
        if not usuario:
            usuario = "xbox"

        password = input("Introduce la contraseña [xbox]: ").strip()
        if not password:
            password = "xbox"

        while True:
            print("¿En qué partición tienes el juego?\n (sólo válidas E, F, G)")
            particion = input("Partición: ").strip().upper()
            if particion in ["E", "F", "G"]:
                break
            print_red("Opción de partición inválida. Intente de nuevo.")

        ruta_remota_dir = f"{particion}:/games/Second Sight"

        print_cyan(f"Conectando a {ip_consola} vía FTP...")
        try:
            ftp_conexion = FTP()
            ftp_conexion.connect(ip_consola, 21, timeout=10)
            ftp_conexion.login(usuario, password)
        except Exception as e:
            print_red(f"Error al conectar o autenticar con el servidor FTP: {e}")
            input("\nPresione ENTER para salir...")
            return

        # Verificar y cambiar a la ruta remota
        try:
            ftp_conexion.cwd(ruta_remota_dir)
        except Exception:
            print_red("No se encuentra la ruta\nasegurate de tener el juego guardado en games\\second sight")
            ftp_conexion.quit()
            input("\nPresione ENTER para salir...")
            return

        # Verificar si ss_ntsc.xbe existe en el directorio remoto
        archivos_remotos = ftp_conexion.nlst()
        if archivo_remoto_nombre not in [f.lower() for f in archivos_remotos]:
            print_red("No se encuentra la ruta\nasegurate de tener el juego guardado en games\\second sight")
            ftp_conexion.quit()
            input("\nPresione ENTER para salir...")
            return

        # Crear carpeta temporal y descargar ss_ntsc.xbe
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        ruta_temporal_archivo = os.path.join(temp_dir, archivo_remoto_nombre)
        print_cyan("Descargando ss_ntsc.xbe desde la consola...")
        try:
            with open(ruta_temporal_archivo, 'wb') as f:
                ftp_conexion.retrbinary(f"RETR {archivo_remoto_nombre}", f.write)
        except Exception as e:
            print_red(f"Error al descargar el archivo por FTP: {e}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            ftp_conexion.quit()
            input("\nPresione ENTER para salir...")
            return

        target_dir = temp_dir
    else:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        target_dir = filedialog.askdirectory(title="Seleccione la carpeta con los archivos a parchear")
        root.destroy()

        if not target_dir:
            print_red("No se seleccionó ninguna carpeta.")
            input("\nPresione ENTER para salir...")
            return

    if not os.path.exists(target_dir):
        print_red("No existe la ruta del juego")
        if modo_ftp and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        input("\nPresione ENTER para salir...")
        return

    print_cyan("Analizando parche, esto puede tomar un momento...")
    try:
        with open(patch_path, 'rb') as f:
            zarf_comprimido = f.read()
        payload_con_hash = lzma.decompress(zarf_comprimido)
    except Exception:
        print_red("Parche corrupto o incompatible")
        if modo_ftp and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        input("\nPresione ENTER para salir...")
        return

    payload = payload_con_hash[:-16]
    expected_md5 = payload_con_hash[-16:]
    if hashlib.md5(payload).digest() != expected_md5:
        print_red("ERROR DE COMPROBACIÓN (MD5 Incorrecto)")
        if modo_ftp and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        input("\nPresione ENTER para salir...")
        return

    if not payload.startswith(b'ZARF\x00\x06'):
        print_red("Formato de parche incompatible")
        if modo_ftp and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        input("\nPresione ENTER para salir...")
        return

    num_punteros = struct.unpack('<I', payload[6:10])[0]
    offset_json = struct.unpack('<I', payload[0x0A:0x0E])[0]

    try:
        json_bytes = payload[offset_json:]
        lista_nombres = json.loads(json_bytes.decode('utf-8'))
    except Exception:
        print_red("Error al leer la tabla de nombres JSON")
        if modo_ftp and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        input("\nPresione ENTER para salir...")
        return

    print("Mapeando e indexando archivos de la carpeta de destino...")
    mapa_por_nombre_y_crc = {}

    for root_path, _, files in os.walk(target_dir):
        for file_name in files:
            full_path = os.path.join(root_path, file_name)
            crc_val = calcular_crc32(full_path)
            clave = (file_name, crc_val)
            if clave not in mapa_por_nombre_y_crc:
                mapa_por_nombre_y_crc[clave] = []
            mapa_por_nombre_y_crc[clave].append(full_path)

    punteros = []
    for i in range(num_punteros):
        ptr_offset = 0x10 + (i * 4)
        punteros.append(struct.unpack('<I', payload[ptr_offset:ptr_offset + 4])[0])

    print(f"Aplicando parche a {num_punteros} archivos...\n")
    start_time = time.time()

    for idx, (ptr, nombre_archivo) in enumerate(zip(punteros, lista_nombres), start=1):
        curr_offset = ptr

        crc_orig = struct.unpack('<I', payload[curr_offset:curr_offset + 4])[0]
        curr_offset += 4

        crc_mod = struct.unpack('<I', payload[curr_offset:curr_offset + 4])[0]
        curr_offset += 4

        tamano_archivo_mod = struct.unpack('<I', payload[curr_offset:curr_offset + 4])[0]
        curr_offset += 4

        num_bloques = struct.unpack('<I', payload[curr_offset:curr_offset + 4])[0]
        curr_offset += 4

        target_files = mapa_por_nombre_y_crc.get((nombre_archivo, crc_orig))

        if not target_files:
            print_red(f"\n[ERROR] No se encontró el archivo '{nombre_archivo}' con CRC32 0x{crc_orig:08X}")
            if modo_ftp and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
                if ftp_conexion:
                    ftp_conexion.quit()
            input("\nPresione ENTER para salir...")
            return

        rel_path = os.path.relpath(target_files[0], target_dir)

        info_text = f"Aplicando a {rel_path} " + f"{Colors.CYAN}[{idx}/{num_punteros}]{Colors.RESET}"
        print(f"\r{info_text:<80}", end='', flush=True)

        bloques_datos = []
        block_offset = curr_offset
        for _ in range(num_bloques):
            tamano_bloque = int.from_bytes(payload[block_offset:block_offset + 3], byteorder='little')
            block_offset += 3

            offset_absoluto = struct.unpack('<I', payload[block_offset:block_offset + 4])[0]
            block_offset += 4

            modo = payload[block_offset]
            block_offset += 1

            bytes_bloque = payload[block_offset:block_offset + tamano_bloque]
            block_offset += tamano_bloque

            bloques_datos.append((tamano_bloque, offset_absoluto, modo, bytes_bloque))

        for target_file in target_files:
            with open(target_file, 'rb') as f:
                file_data = bytearray(f.read())

            for tamano_bloque, offset_absoluto, modo, bytes_bloque in bloques_datos:
                if modo == 0x01:
                    if len(file_data) < offset_absoluto:
                        file_data.extend(b'\x00' * (offset_absoluto - len(file_data)))
                    file_data[offset_absoluto:offset_absoluto] = bytes_bloque
                else:
                    tamano_necesario = offset_absoluto + tamano_bloque
                    if len(file_data) < tamano_necesario:
                        file_data.extend(b'\x00' * (tamano_necesario - len(file_data)))
                    file_data[offset_absoluto:offset_absoluto + tamano_bloque] = bytes_bloque

            if len(file_data) > tamano_archivo_mod:
                file_data = file_data[:tamano_archivo_mod]
            elif len(file_data) < tamano_archivo_mod:
                file_data.extend(b'\x00' * (tamano_archivo_mod - len(file_data)))

            with open(target_file, 'wb') as f:
                f.write(file_data)

            # Validación de CRC del archivo modificado
            crc_calculado = calcular_crc32(target_file)
            if crc_calculado != crc_mod:
                print()
                print_red(f"\nError de CRC en {os.path.relpath(target_file, target_dir)}")
                if modo_ftp and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    if ftp_conexion:
                        ftp_conexion.quit()
                input("\nPresione ENTER para salir...")
                return

    # Si es modo FTP, subir el archivo modificado de vuelta a la consola
    if modo_ftp:
        print_cyan("\nSubiendo el archivo ss_ntsc.xbe parcheado a la consola...")
        try:
            ruta_temporal_archivo = os.path.join(temp_dir, archivo_remoto_nombre)
            with open(ruta_temporal_archivo, 'rb') as f:
                ftp_conexion.storbinary(f"STOR {archivo_remoto_nombre}", f)
            ftp_conexion.quit()
        except Exception as e:
            print_red(f"Error al subir el archivo por FTP: {e}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            input("\nPresione ENTER para salir...")
            return

        # Limpiar carpeta temporal local de FTP
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

    elapsed_time = time.time() - start_time
    print()
    if modo_ftp:
        print_green(f"\n¡Parche aplicado con éxito y subido por FTP en {elapsed_time:.2f} segundos! :)")
    else:
        print_green(f"\n¡Parche aplicado con éxito a {num_punteros} archivos en {elapsed_time:.2f} segundos! :)")
    
    input("\nPresione ENTER para salir...")


if __name__ == "__main__":
    aplicar_parche_zarf()

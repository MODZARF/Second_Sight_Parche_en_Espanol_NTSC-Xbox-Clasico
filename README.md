# 🎮 Second Sight - Parche en Español NTSC
### Para Xbox Clásico

Herramienta en **Python** para que el juego **Second Sight** cargue el idioma **español por defecto** en la región **NTSC**.

> ⚠️ **Solo textos.** El juego no incluye audio en español, por eso recuerda activar los **subtítulos** en opciones, que por defecto vienen desactivados.

---

### 🧐 ¿Cómo funciona?

El programa funciona a través de un archivo **`parche.ZARF`** que aplica las ediciones necesarias al archivo **`ss_ntsc.xbe`** para forzar la carga del español.

> ✅ **El parche NO contiene ningún archivo del juego**, solo la diferencia hexadecimal a aplicar (deltas).

---

### 📋 Requisitos

- **Si usas el script:** Tener **Python instalado**
- Tener una **copia original y legal** del juego **Second Sight - Xbox Clásico**

---

### 🚀 Cómo se usa

Tienes 2 opciones:

**Opción 1 - Script:**
1. Descarga el archivo **`aplicar.py`**
2. Descarga el archivo **`parche.ZARF`**
3. Ponlos en la misma carpeta

**Opción 2 - Ejecutable:**
- En **Releases** está el script compilado en un **`.exe`** que ya incorpora el **`.ZARF`**, así que **no necesitas poner el archivo ZARF al lado.**

### ▶️ Ejecutar

1. Ejecuta el **`aplicar.py`** o el **`.exe`**
2. El programa te preguntará si quieres aplicar el parche de manera local o por FTP:
   - Escribe **`1`** para hacerlo **Local**
   - Escribe **`2`** para hacerlo por **FTP**

**🖥️ Si usas el modo Local:**
- Se abrirá una ventana para que selecciones la **carpeta raíz del juego**
- La seleccionas, esperas unos segundos y **¡listo!**

**🌐 Si usas el modo FTP:**
1. Ingresa la información para conectar a tu consola Xbox, por defecto saldrá estas configuraciones:
   - **IP:** `192.168.0.3`
   - **Usuario:** `xbox`
   - **Contraseña:** `xbox`
    
2. Finalmente especifica con "E", "F" y "G" la partición donde tienes el juego en la consola.

Solo funciona con estas 3 rutas:

> 
E:/games/Second Sight
F:/games/Second Sight
G:/games/Second Sight

---

**Hecho por ZARF**

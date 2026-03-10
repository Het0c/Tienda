# Tienda

Aplicación de gestión para una tienda, con módulos de escritorio (PyQt5) y un módulo web en Flask para tareas administrativas.

## Introducción

Este proyecto reúne funcionalidades como:

- gestión de ventas,
- control de inventario,
- administración de clientes,
- generación/lectura de códigos de barras,
- utilidades de dashboard y reportes.

La ejecución principal del sistema se hace desde `app.py`, que inicia el frontend de escritorio en `frontend.main`.

## Requisitos previos

Antes de instalar, asegúrate de tener:

- **Python 3.10+** (recomendado),
- **pip** actualizado,
- **MySQL Server** activo y accesible,
- sistema operativo con soporte para interfaz gráfica (por PyQt5).

## Instalación

### 1) Clonar o descargar el proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd Tienda
```

### 2) Crear y activar entorno virtual

En Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Instalar requerimientos y dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Esto instalará dependencias como:

- `PyQt5` (interfaz gráfica),
- `mysql-connector-python` / `mysqlclient` (conexión a base de datos),
- `opencv-python` y `pyzbar` (lectura de códigos),
- `python-barcode` (generación de códigos),
- `matplotlib` y `numpy` (gráficos/procesamiento).

## Configuración básica

- Revisa las credenciales de base de datos en los archivos de conexión (por ejemplo, en el módulo Flask se define en `flask/app.py`).
- Crea la base de datos y tablas necesarias antes de ejecutar.
- Si aplica, usa los scripts SQL del proyecto (`backup_file.sql` o archivos en `backend/db/`) para cargar estructura y datos iniciales.

## Ejecución

### Aplicación principal (escritorio)

```bash
python app.py
```

### Módulo web Flask (opcional)

```bash
python flask/app.py
```

Luego abre en tu navegador: `http://127.0.0.1:5000`.

## Estructura general

- `app.py`: punto de entrada principal.
- `frontend/`: interfaz de escritorio (PyQt5).
- `backend/`: lógica de negocio, conexión a base de datos y utilidades.
- `flask/`: módulo web y templates HTML.
- `requirements.txt`: listado de dependencias Python.

## Notas

- Si tienes errores con paquetes de MySQL (`mysqlclient`), instala primero las bibliotecas del sistema requeridas por tu SO.
- Para evitar conflictos, trabaja siempre dentro del entorno virtual.

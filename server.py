"""API local para exponer la lógica Python existente a React/Tauri.

Este módulo conserva `backend/` como fuente de verdad y actúa como una capa
adaptadora HTTP/WebSocket. En producción Tauri lo ejecuta como sidecar.
"""
from __future__ import annotations

import asyncio
import importlib
import os
import sys
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Permite que el binario PyInstaller encuentre backend/ al ejecutarse como sidecar.
ROOT_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.logica import arqueo, inventario, user, ventas  # noqa: E402

TAURI_DEV_ORIGIN = os.getenv("TAURI_DEV_ORIGIN", "http://localhost:1420")
REACT_DEV_ORIGIN = os.getenv("REACT_DEV_ORIGIN", "http://localhost:5173")

app = FastAPI(title="Tienda Local API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[TAURI_DEV_ORIGIN, REACT_DEV_ORIGIN, "tauri://localhost", "http://tauri.localhost", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    rut: str
    password: str


class LoginResponse(BaseModel):
    authenticated: bool
    rut: str
    is_admin: bool = False


class InventoryCreateRequest(BaseModel):
    nombre: str
    tipo: str | None = None
    marca: str | None = None
    precio: int = Field(ge=0)
    stock: int = Field(ge=0)
    barcode: str | None = None


class SaleItem(BaseModel):
    id: int | str | None = None
    nombre: str
    cantidad: int = Field(gt=0)
    precio: int = Field(ge=0)
    merma: int = Field(default=0, ge=0)


class SaleRequest(BaseModel):
    subtotal: int = Field(ge=0)
    productos: list[SaleItem]
    descuento_total: int = Field(default=0, ge=0)
    metodo_pago: Literal["efectivo", "debito", "credito", "transferencia", "otro"] = "efectivo"
    rut_empleado: str
    registrar_arqueo: bool = False


class ArqueoRequest(BaseModel):
    fecha: str
    subtotal_ventas: int = Field(ge=0)
    total_efectivo: int = Field(ge=0)
    gastos_dia: int = Field(default=0, ge=0)


class PrintRequest(BaseModel):
    payload: dict[str, Any]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login", response_model=LoginResponse)
def login(data: LoginRequest) -> LoginResponse:
    authenticated = user.verificar_contraseña(data.rut, data.password)
    if not authenticated:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return LoginResponse(
        authenticated=True,
        rut=data.rut,
        is_admin=user.verificacion_admin(data.rut),
    )


@app.get("/inventory")
def list_inventory(search: str = "") -> list[dict[str, Any]]:
    return inventario.consultar_inventario_ropa(search)


@app.get("/inventory/barcode/{barcode}")
def get_product_by_barcode(barcode: str) -> dict[str, Any]:
    product = inventario.obtener_producto_por_codigo(barcode)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    nombre, precio = product
    return {"nombre": nombre, "precio": precio, "barcode": barcode}


@app.post("/inventory")
def create_inventory_item(data: InventoryCreateRequest) -> dict[str, Any]:
    """Ejemplo de punto de entrada para altas de inventario.

    Si `backend.logica.inventario` gana una función `crear_prenda`, esta ruta la
    usa sin cambiar React. Mientras tanto devuelve 501 para evitar escribir SQL
    duplicado fuera de la capa de negocio existente.
    """
    crear_prenda = getattr(inventario, "crear_prenda", None)
    if crear_prenda is None:
        raise HTTPException(status_code=501, detail="Implementar crear_prenda en backend.logica.inventario")
    return crear_prenda(**data.model_dump())


@app.post("/sales")
def create_sale(data: SaleRequest) -> dict[str, Any]:
    sale_result = ventas.registrar_venta(
        subtotal=data.subtotal,
        productos=[item.model_dump() for item in data.productos],
        descuento_total=data.descuento_total,
        metodo_pago=data.metodo_pago,
        rut_empleado=data.rut_empleado,
    )
    if not sale_result:
        raise HTTPException(status_code=500, detail="No se pudo registrar la venta")
    return {"ok": True, "sale": sale_result}


@app.get("/cash-register/{fecha}")
def get_cash_register(fecha: str) -> dict[str, Any]:
    result = arqueo.consultar_arqueo_fecha(fecha)
    if result is None:
        raise HTTPException(status_code=404, detail="Arqueo no encontrado")
    return result


@app.post("/cash-register")
def create_cash_register(data: ArqueoRequest) -> dict[str, bool]:
    arqueo.registrar_arqueo(**data.model_dump())
    return {"ok": True}


@app.post("/peripherals/print")
def print_receipt(data: PrintRequest) -> dict[str, bool]:
    printer = importlib.import_module("backend.printer_test")
    printer.imprimir_boleta_abono(**data.payload)
    return {"ok": True}


@app.websocket("/ws/scanner")
async def scanner_events(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            # Adaptador inicial: el frontend puede enviar códigos capturados por un lector HID.
            # Luego puede reemplazarse por una cola alimentada desde backend.scanner.testScanner.
            barcode = await websocket.receive_text()
            await websocket.send_json({"type": "barcode", "barcode": barcode})
    except WebSocketDisconnect:
        return


async def wait_until_cancelled() -> None:
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("TIENDA_API_PORT", "8765")))

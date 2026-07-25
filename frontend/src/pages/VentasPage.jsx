import React from 'react';
import { inventoryService, salesService, scannerWsUrl } from '../services/api.js';

export function VentasPage({ session }) {
  const [barcode, setBarcode] = React.useState('');
  const [items, setItems] = React.useState([]);
  const [metodoPago, setMetodoPago] = React.useState('efectivo');

  React.useEffect(() => {
    const ws = new WebSocket(scannerWsUrl());
    ws.onmessage = event => setBarcode(JSON.parse(event.data).barcode);
    return () => ws.close();
  }, []);

  async function addByBarcode(code = barcode) {
    const product = await inventoryService.byBarcode(code);
    setItems(current => [...current, { ...product, cantidad: 1 }]);
    setBarcode('');
  }

  const subtotal = items.reduce((sum, item) => sum + item.precio * item.cantidad, 0);

  async function registrarVenta() {
    await salesService.create({ subtotal, productos: items, descuento_total: 0, metodo_pago: metodoPago, rut_empleado: session.rut });
    setItems([]);
  }

  return <section className="grid gap-4 p-6">
    <h2 className="text-xl font-bold">Punto de venta</h2>
    <div className="card flex gap-2">
      <input value={barcode} onChange={e => setBarcode(e.target.value)} placeholder="Código de barra" />
      <button onClick={() => addByBarcode()}>Agregar</button>
      <select value={metodoPago} onChange={e => setMetodoPago(e.target.value)}><option value="efectivo">Efectivo</option><option value="debito">Débito</option><option value="credito">Crédito</option></select>
    </div>
    <div className="card">
      {items.map((item, index) => <div key={`${item.barcode}-${index}`} className="flex justify-between border-b py-2"><span>{item.nombre} x {item.cantidad}</span><strong>${item.precio}</strong></div>)}
      <p className="mt-4 text-right text-2xl font-bold">Total: ${subtotal}</p>
      <button onClick={registrarVenta} disabled={!items.length} className="bg-green-500">Registrar venta</button>
    </div>
  </section>;
}

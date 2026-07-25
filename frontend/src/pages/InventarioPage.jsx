import React from 'react';
import { inventoryService } from '../services/api.js';

export function InventarioPage() {
  const [search, setSearch] = React.useState('');
  const [rows, setRows] = React.useState([]);

  React.useEffect(() => { inventoryService.list(search).then(setRows); }, [search]);

  return <section className="grid gap-4 p-6">
    <h2 className="text-xl font-bold">Inventario</h2>
    <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Buscar prenda" />
    <div className="card overflow-auto">
      <table className="w-full text-left"><thead><tr><th>Prenda</th><th>Tipo</th><th>Marca</th><th>Precio</th><th>Stock</th></tr></thead>
      <tbody>{rows.map(row => <tr key={row.id}><td>{row.Prenda}</td><td>{row.tipo}</td><td>{row.Marca}</td><td>${row.Precio}</td><td>{row['Total Stock']}</td></tr>)}</tbody></table>
    </div>
  </section>;
}

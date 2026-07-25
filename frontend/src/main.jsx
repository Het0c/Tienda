import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
import { LoginPage } from './pages/LoginPage.jsx';
import { VentasPage } from './pages/VentasPage.jsx';
import { InventarioPage } from './pages/InventarioPage.jsx';

function App() {
  const [session, setSession] = React.useState(null);
  const [page, setPage] = React.useState('ventas');

  if (!session) return <LoginPage onLogin={setSession} />;

  return <main className="min-h-screen bg-slate-100 text-slate-900">
    <nav className="flex gap-3 bg-yellow-500 p-4 font-semibold">
      <button onClick={() => setPage('ventas')}>Ventas</button>
      <button onClick={() => setPage('inventario')}>Inventario</button>
      <span className="ml-auto">RUT: {session.rut}</span>
    </nav>
    {page === 'ventas' ? <VentasPage session={session} /> : <InventarioPage />}
  </main>;
}

createRoot(document.getElementById('root')).render(<App />);

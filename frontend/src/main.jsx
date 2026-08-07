import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
import { MainMenu } from './pages/MainMenu.jsx';
import { InventarioPage } from './pages/InventarioPage.jsx';
import { VentasPage } from './pages/VentasPage.jsx';
import { ArqueoPage } from './pages/ArqueoPage.jsx';
import { IngresoMercaderiaPage } from './pages/IngresoMercaderiaPage.jsx';
import { ClientesPage } from './pages/ClientesPage.jsx';

function App() {
  const [page, setPage] = React.useState('menu');
  const [dark, setDark] = React.useState(false);

  const navigate = (destination) => {
    const routes = { inventario: '/inventario', ventas: '/ventas', informes: '/informes', clientes: '/clientes', arqueo: '/arqueo', 'ingreso-mercaderia': '/ingreso-mercaderia', menu: '/' };
    window.history.pushState({}, '', routes[destination] ?? '/');
    setPage(destination);
  };

  const common = { dark, onToggleTheme: () => setDark(v => !v), onNavigate: navigate, onLogout: () => window.dispatchEvent(new CustomEvent('girasol:logout')) };
  if (page === 'inventario') return <InventarioPage {...common} />;
  if (page === 'ventas') return <VentasPage session={{ rut: '' }} {...common} />;
  if (page === 'arqueo') return <ArqueoPage {...common} />;
  if (page === 'clientes') return <ClientesPage {...common} />;
  if (page === 'ingreso-mercaderia') return <IngresoMercaderiaPage {...common} />;

  return <MainMenu dark={dark} onToggleTheme={() => setDark((value) => !value)} onNavigate={navigate} onLogout={() => window.dispatchEvent(new CustomEvent('girasol:logout'))} />;
}

createRoot(document.getElementById('root')).render(<App />);

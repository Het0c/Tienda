import React from 'react';
import { authService } from '../services/api.js';

export function LoginPage({ onLogin }) {
  const [rut, setRut] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState('');

  async function submit(event) {
    event.preventDefault();
    setError('');
    try { onLogin(await authService.login(rut, password)); }
    catch { setError('Credenciales inválidas o servidor no disponible'); }
  }

  return <section className="grid min-h-screen place-items-center bg-yellow-50">
    <form onSubmit={submit} className="card grid w-96 gap-4">
      <h1 className="text-2xl font-bold">Tienda Girasol</h1>
      <input value={rut} onChange={e => setRut(e.target.value)} placeholder="RUT" required />
      <input value={password} onChange={e => setPassword(e.target.value)} placeholder="Contraseña" type="password" required />
      {error && <p className="text-red-600">{error}</p>}
      <button className="bg-yellow-500" type="submit">Ingresar</button>
    </form>
  </section>;
}

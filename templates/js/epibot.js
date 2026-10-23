// Filtro simple de la lista de centros (centros.html)
const q = document.getElementById('q');
if (q) {
  const filas = [...document.querySelectorAll('.row')].filter(r => r.querySelector('a.m'));
  q.addEventListener('input', () => {
    const t = q.value.trim().toLowerCase();
    filas.forEach(r => { r.style.display = r.textContent.toLowerCase().includes(t) ? '' : 'none'; });
  });
}

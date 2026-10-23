// Pequeño script compartido: hace que los grupos de botones
// (filtros y capas del mapa) funcionen como "elige uno".
document.querySelectorAll('[data-grupo]').forEach(function (grupo) {
  grupo.addEventListener('click', function (e) {
    var boton = e.target.closest('button[aria-pressed]');
    if (!boton || !grupo.contains(boton)) return;
    grupo.querySelectorAll('button[aria-pressed]').forEach(function (b) {
      b.setAttribute('aria-pressed', 'false');
    });
    boton.setAttribute('aria-pressed', 'true');
  });
});

// Interruptores de fuentes (encender / apagar)
document.querySelectorAll('.interruptor').forEach(function (sw) {
  sw.addEventListener('click', function () {
    var activo = sw.getAttribute('aria-pressed') === 'true';
    sw.setAttribute('aria-pressed', activo ? 'false' : 'true');
  });
});

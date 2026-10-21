// EpiBot Colombia — interacciones del one-page
const menuToggle = document.querySelector(".menu-toggle");
const mainNav = document.querySelector(".main-nav");

if (menuToggle && mainNav) {
  menuToggle.addEventListener("click", () => {
    const isOpen = mainNav.classList.toggle("open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Cerrar menú" : "Abrir menú");
  });
  mainNav.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
    mainNav.classList.remove("open");
    menuToggle.setAttribute("aria-expanded", "false");
  }));
}

// Búsqueda local en la página: desplaza al primer contenido coincidente.
const siteSearch = document.getElementById("siteSearch");
const searchInput = document.getElementById("searchInput");
const toast = document.getElementById("toast");
let toastTimer;

function showToast(message) {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2800);
}

if (siteSearch && searchInput) {
  siteSearch.addEventListener("submit", event => {
    event.preventDefault();
    const query = searchInput.value.trim().toLocaleLowerCase("es");
    if (!query) {
      showToast("Escribe un tema para buscar en esta página.");
      return;
    }
    const candidates = [...document.querySelectorAll("main h1, main h2, main h3, main p, main li")];
    const match = candidates.find(el => el.textContent.toLocaleLowerCase("es").includes(query));
    if (match) {
      match.scrollIntoView({ behavior: "smooth", block: "center" });
      match.setAttribute("tabindex", "-1");
      match.focus({ preventScroll: true });
    } else {
      showToast("No encontramos esa palabra en esta página.");
    }
  });
}

// Filtros de ejemplo del directorio. Los centros son datos ilustrativos, no un directorio validado.
const clinicSearch = document.getElementById("clinicSearch");
const departmentFilter = document.getElementById("departmentFilter");
const serviceFilter = document.getElementById("serviceFilter");
const clinics = [...document.querySelectorAll(".clinic")];

function filterClinics() {
  const q = (clinicSearch?.value || "").toLocaleLowerCase("es").trim();
  const department = departmentFilter?.value || "";
  const service = serviceFilter?.value || "";
  let visible = 0;
  clinics.forEach(clinic => {
    const matchesText = !q || clinic.dataset.city.includes(q) || clinic.textContent.toLocaleLowerCase("es").includes(q);
    const matchesDepartment = !department || clinic.dataset.department === department;
    const matchesService = !service || clinic.dataset.type === service;
    const show = matchesText && matchesDepartment && matchesService;
    clinic.hidden = !show;
    if (show) visible++;
  });
  let empty = document.getElementById("noClinics");
  if (!visible) {
    if (!empty) {
      empty = document.createElement("p");
      empty.id = "noClinics";
      empty.className = "disclaimer";
      empty.textContent = "No hay resultados para esos filtros. Prueba otra búsqueda o consulta a la Secretaría de Salud local.";
      document.getElementById("clinicList").appendChild(empty);
    }
  } else if (empty) empty.remove();
}
[clinicSearch, departmentFilter, serviceFilter].forEach(el => {
  if (el) el.addEventListener(el.tagName === "INPUT" ? "input" : "change", filterClinics);
});

// El formulario de suscripción es solo visual; no recopila ni envía datos.
const newsletterForm = document.getElementById("newsletterForm");
if (newsletterForm) {
  newsletterForm.addEventListener("submit", event => {
    event.preventDefault();
    const message = document.getElementById("newsletterMessage");
    if (message) message.textContent = "Demostración: conecta un servicio de correo antes de habilitar suscripciones.";
    newsletterForm.reset();
  });
}

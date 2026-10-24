/* ============ ESTADO ============ */
const S = {zona:null, fiebre:null, pIdx:0, pReintento:false, volver:null, ficha:"dengue"};
const app = document.getElementById("app");
const $ = (h)=>{const t=document.createElement("template");t.innerHTML=h.trim();return t.content;};
const zonaPor = id => ZONAS.find(z=>z[0]===id);
const peor = z => Object.entries(z[5]).sort((a,b)=>ORDEN.indexOf(b[1][0])-ORDEN.indexOf(a[1][0]))[0];
const store = {get(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
const agente = k => k==="malaria"?"parasito":"virus";
const AVISO = `<p class="aviso-pie">Esta información no reemplaza la consulta médica. Fuentes: MinSalud, INS y OPS.</p>`;

function toast(t){const el=document.getElementById("toast");el.textContent=t;el.hidden=false;clearTimeout(toast.t);toast.t=setTimeout(()=>el.hidden=true,3400);}
function chip(n){return `<span class="chip n-${n}">${NIVEL[n].txt}</span>`;}

/* Barra de pasos: solo se ve durante el recorrido */
const NOMBRES_PASOS=["Tu zona","Tu situación","Revisión","Práctica","Tu plan"];
function pasos(n){
  const bar=document.getElementById("recorrido");
  if(!n){bar.hidden=true;return;}
  bar.hidden=false;
  bar.querySelector("ol").innerHTML=NOMBRES_PASOS.map((t,i)=>`<li class="${i<n?"on":""} ${i===n-1?"actual":""}"><span>${i+1}. ${t}</span></li>`).join("");
}
function ir(fn, ancla){
  app.innerHTML=""; if(fn!==ficha) S.vistaActual=fn; fn();
  if(ancla){const el=document.getElementById(ancla); if(el){el.scrollIntoView(); return;}}
  window.scrollTo(0,0);
}

/* Datos reales: /api/zonas arma las zonas desde la base de datos (alertas de la IA).
   Si el servidor no responde, se quedan los datos de ejemplo de datos.js */
async function cargarZonas(){
  try{
    const r=await fetch("/api/zonas");
    if(!r.ok) throw 0;
    const j=await r.json();
    if(Array.isArray(j.zonas) && j.zonas.length){ ZONAS=j.zonas; DATOS_REALES=true; }
  }catch(e){}
}
const num = v => (v===null || v===undefined) ? "Sin dato" : Number(v).toLocaleString("es-CO");
const ETIQUETA_EJEMPLO = () => DATOS_REALES ? "" : `<span class="ejemplo">Datos de ejemplo</span>`;

/* Intenta la API real; si falla, usa los datos de ejemplo */
async function cargarAlertas(z){
  try{
    const hoy=new Date(), desde=`${hoy.getFullYear()}-${String(hoy.getMonth()+1).padStart(2,"0")}-01`;
    const r=await fetch(`/api/alertas?departamento=${encodeURIComponent(z[1])}&desde=${desde}`);
    if(!r.ok) throw 0;
    await r.json(); // Conectar aquí el contrato real de alerta
  }catch(e){}
  return z;
}

/* ============ SECCIONES (cada página arma las suyas) ============ */
const SEC={
 hero:()=>`
  <section class="hero" id="consulta"><div class="wrap hero-grid">
    <div class="pila">
      <p class="eyebrow">Dengue · Chikungunya · Malaria</p>
      <h1>Conoce cómo está <em>tu zona</em> y qué hacer esta semana</h1>
      <p class="lead">En 2 minutos te decimos, en palabras simples, si en tu departamento hay más casos de lo normal, qué hacer si alguien tiene fiebre y tres acciones para proteger a tu familia.</p>
      <div class="botones" style="max-width:520px">
        <a class="btn btn-2" href="enfermedades.html">Conoce las enfermedades</a>
        <a class="btn btn-2" href="mapa.html">Ver el mapa del país</a>
      </div>
      <div class="privacidad"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/></svg>
        <p>No pedimos cuenta ni guardamos tu ubicación. Se usa solo en tu celular.</p></div>
    </div>
    <div class="consulta">
      <h2>¿Cómo está tu zona?</h2>
      <button class="btn btn-1 btn-full" id="mi-zona">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>
        Usar mi ubicación</button>
      <div class="separador">o elige de la lista</div>
      <div class="campo"><label for="dep">Departamento</label>
        <select id="dep"><option value="">Selecciona tu departamento</option>${ZONAS.map(z=>`<option value="${z[0]}">${z[1]}</option>`).join("")}</select></div>
      <button class="btn btn-2 btn-full" id="ver">Ver mi zona</button>
      <p class="nota" id="geo-msg" hidden></p>
    </div>
  </div></section>`,

 enfermedades:(banda=true)=>`
  <section class="seccion ${banda?"banda":""}"><div class="wrap">
    <div class="seccion-cab"><p class="eyebrow">Conoce las enfermedades</p>
      <h2>Tres enfermedades, dos mosquitos</h2>
      <p class="lead">Las tres empiezan con fiebre y se confunden al inicio. Conocer sus síntomas te ayuda a saber cuándo ir a urgencias.</p></div>
    <div class="grid-3">${Object.entries(PATOGENOS).map(([k,v])=>`
      <a class="carta carta-enf" href="enfermedades.html?p=${k}" data-f="${k}">
        ${mosquito(FICHAS[k].transmite)}
        <div class="cuerpo">
          <div class="etiquetas"><span class="etq">${v.tipo}</span><span class="etq"><i>${FICHAS[k].transmite}</i></span></div>
          <h3>${v.nombre}</h3>
          <p class="nota">${FICHAS[k].sintomas.slice(0,3).map(s=>s[1]).join(" · ")}</p>
          <span class="ver">Síntomas y cuidados →</span>
        </div></a>`).join("")}
    </div>
  </div></section>`,

 mapa:(banda=false)=>{
  const ranking=ZONAS.slice().sort((a,b)=>ORDEN.indexOf(peor(b)[1][0])-ORDEN.indexOf(peor(a)[1][0])).map(z=>{
    const [p,d]=peor(z);
    return `<a href="zona.html?zona=${z[0]}"><b>${z[1]}</b>${chip(d[0])}<span class="nota">${d[0]==="sin"?"Sin reportes recientes":PATOGENOS[p].nombre+(d[1]==null?"":" · "+num(d[1])+" casos")}</span></a>`;}).join("");
  return `<section class="seccion ${banda?"banda":""}"><div class="wrap">
    <div class="seccion-cab"><p class="eyebrow">El mapa de esta semana ${ETIQUETA_EJEMPLO()}</p>
      <h2>¿Dónde hay más casos de lo normal?</h2>
      <p class="lead">Cada punto muestra la enfermedad con el nivel más alto en el departamento. Toca un departamento para ver el detalle.</p></div>
    <div class="grid-2">${mapa()}<div class="ranking">${ranking}</div></div>
  </div></section>`;},

 prevencion:(banda=false)=>`
  <section class="seccion ${banda?"banda":""}"><div class="wrap">
    <div class="seccion-cab"><p class="eyebrow">Prevención</p>
      <h2>Lo que más sirve se hace en casa</h2>
      <p class="lead">El mosquito del dengue y el chikungunya pone sus huevos en agua quieta y limpia. Sin agua quieta, no hay mosquitos nuevos.</p></div>
    <div class="grid-3">${[
      ["tanque","Lava el tanque cada semana","Restriega las paredes: los huevos del mosquito se pegan ahí."],
      ["tapar","Tapa el agua guardada","Baldes, botellas y canecas siempre con tapa."],
      ["llanta","Vacía lo que junte agua","Llantas, floreros, tapas y materas, dentro y fuera de la casa."],
      ["repelente","Usa repelente","Al amanecer y al atardecer, y en la noche donde hay malaria."],
      ["toldillo","Duerme con toldillo","Sobre todo bebés, niños y personas enfermas."],
      ["ropa","Ropa que cubra","Manga larga y pantalón en las horas de más picadura."]
    ].map(([i,t,d])=>`<div class="carta" style="flex-direction:row;align-items:flex-start;gap:16px">${ico(i,"ico ico-g")}<div class="pila-s" style="gap:4px"><h3>${t}</h3><p class="nota">${d}</p></div></div>`).join("")}</div>
  </div></section>`,

 fiebreResumen:()=>`
  <section class="seccion banda"><div class="wrap grid-2">
    <div class="pila">
      <p class="eyebrow">Si alguien tiene fiebre</p>
      <h2>Qué no tomar y cuándo ir a urgencias</h2>
      <div class="no-tomar"><h3>No tomar sin consultar:</h3><p>Ibuprofeno, aspirina, naproxeno ni diclofenaco. Si es dengue, pueden aumentar el riesgo de sangrado. Para la fiebre se suele indicar acetaminofén, siempre con consulta médica.</p></div>
    </div>
    <div class="alarma"><h3>Ve a urgencias si aparece:</h3>
      <ul class="lista"><li>Dolor fuerte de barriga</li><li>Vómito que no para</li><li>Sangrado de encías o nariz</li><li>Mucho sueño o le cuesta despertar</li><li>Confusión, piel u ojos amarillos u orina oscura</li></ul></div>
  </div></section>`,

 como:(banda=false)=>`
  <section class="seccion ${banda?"banda":""}"><div class="wrap">
    <div class="seccion-cab"><p class="eyebrow">Cómo funciona</p>
      <h2>De boletines técnicos a un mensaje claro</h2>
      <p class="lead">La información oficial llega en boletines en PDF, cada semana y con retraso. EpiBot la junta con las noticias y te la explica.</p></div>
    <ol class="pasos-como">
      <li><h3>Leemos las fuentes</h3><p class="nota">Una IA revisa noticias, boletines del INS y avisos de la OMS.</p></li>
      <li><h3>Validamos los datos</h3><p class="nota">Un programa en Python revisa que cada dato tenga fecha, lugar y fuente.</p></li>
      <li><h3>Una regla fija el nivel</h3><p class="nota">Se comparan los casos con lo esperado para esta época. No lo decide la IA.</p></li>
      <li><h3>Tú ves la fuente</h3><p class="nota">Cada alerta dice si está confirmada por el INS o si solo hay noticias.</p></li>
    </ol>
  </div></section>`,

 niveles:()=>`
  <section class="seccion banda"><div class="wrap">
    <div class="seccion-cab"><p class="eyebrow">Los niveles</p><h2>Qué significa cada color</h2></div>
    <div class="grid-2">${ORDEN.slice().reverse().map(n=>`<div class="carta" style="flex-direction:row;align-items:center;gap:14px">${chip(n)}<p>${n==="sin"?NIVEL.sin.que:"Hay "+NIVEL[n].frase+". "+NIVEL[n].que}</p></div>`).join("")}</div>
    <p class="nota" style="margin-top:16px">Nunca decimos "libre de dengue": que no haya reportes no significa que no haya casos.</p>
  </div></section>`,

 porque:(banda=false)=>`
  <section class="seccion ${banda?"banda":""}"><div class="wrap">
    <div class="seccion-cab"><p class="eyebrow">¿Por qué importa?</p><h2>El dengue afecta sobre todo a niños y jóvenes</h2></div>
    <div class="grid-3">
      <div class="carta cifra"><b>117.789</b><p>casos de dengue en 2025; el 57,8 % en personas de 0 a 19 años.</p><p class="nota">Portafolio, 2025</p></div>
      <div class="carta cifra"><b>14</b><p>territorios por encima de lo esperado a la semana 26 de 2026.</p><p class="nota">ConsultorSalud, 2026</p></div>
      <div class="carta cifra"><b>&lt;10 %</b><p>de los casos capta SIVIGILA en algunas ciudades: las cifras oficiales se quedan cortas.</p><p class="nota">Carabali et al., 2021</p></div>
    </div>
    <p class="nota" style="margin-top:16px">La malaria de 2023 a 2025 está incompleta en SIVIGILA: solo se registra la complicada.</p>
  </div></section>`,

 cta:(titulo,texto)=>`
  <section class="seccion"><div class="wrap"><div class="carta" style="flex-direction:row;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px;padding:28px">
    <div class="pila-s"><h2 style="font-size:1.5rem">${titulo}</h2><p class="nota">${texto}</p></div>
    <a class="btn btn-1" href="index.html#consulta">Consultar mi zona</a></div></div></section>`
};

/* ============ PÁGINAS ============ */
function cabecera(eyebrow,titulo,lead){
  return `<section class="cabecera"><div class="wrap pila-s"><p class="eyebrow">${eyebrow}</p><h1>${titulo}</h1>${lead?`<p class="lead">${lead}</p>`:""}</div></section>`;
}
function inicio(){
  pasos(0);
  app.append($(SEC.hero()+SEC.enfermedades(true)+SEC.cta("¿Quieres ver todo el país?","Mira el mapa con el nivel de cada departamento.").replace('href="index.html#consulta">Consultar mi zona','href="mapa.html">Ver el mapa')));
  enlazarConsulta();
}
function paginaMapa(){
  app.append($(cabecera("Mapa","Cómo está el país esta semana","Los departamentos ordenados de más a menos alerta.")+SEC.mapa()+SEC.niveles()+SEC.cta("¿Y en tu zona?","Mira tu departamento y recibe tu plan de la semana.")));
}
function paginaPrevencion(){
  app.append($(cabecera("Prevención","Cómo proteger a tu familia","Acciones simples que se hacen en casa, cada semana.")+SEC.prevencion()+SEC.fiebreResumen()+SEC.cta("Recibe tu plan de la semana","Tres acciones según el nivel de tu zona, para enviar por WhatsApp.")));
}
function paginaComo(){
  app.append($(cabecera("Cómo funciona","Así trabaja EpiBot","Qué fuentes usamos y cómo decidimos el nivel de cada zona.")+SEC.como()+SEC.porque(true)+SEC.cta("Pruébalo con tu zona","Toma unos 2 minutos.")));
}
function paginaEnfermedades(){
  const p=new URLSearchParams(location.search).get("p");
  S.ficha = PATOGENOS[p]?p:"dengue"; S.volver=null;
  ficha();
}
function paginaZona(){
  const id=new URLSearchParams(location.search).get("zona")||location.hash.slice(1);
  if(!zonaPor(id)){ location.replace("index.html#consulta"); return; }
  cargarAlertas(zonaPor(id)).then(z=>{S.zona=z; ir(resultado);});
}
function enlazarConsulta(){
  document.getElementById("ver").onclick=()=>{const v=document.getElementById("dep").value; if(v) elegir(v); else {toast("Elige un departamento de la lista.");document.getElementById("dep").focus();}};
  document.getElementById("mi-zona").onclick=miZona;
}

function miZona(){
  const msg=document.getElementById("geo-msg");
  const falla=()=>{msg.hidden=false;msg.textContent="No pudimos usar tu ubicación. Elige tu departamento en la lista.";document.getElementById("dep").focus();};
  if(!navigator.geolocation) return falla();
  navigator.geolocation.getCurrentPosition(p=>{
    // En el proyecto: buscar el departamento con static/data/colombia.geojson (punto en polígono).
    // Por ahora: la capital más cercana, como aproximación.
    const {latitude:a,longitude:b}=p.coords;
    const z=ZONAS.slice().sort((m,n)=>Math.hypot(m[2]-a,m[3]-b)-Math.hypot(n[2]-a,n[3]-b))[0];
    elegir(z[0]);
  },falla,{timeout:8000,maximumAge:600000});
}
function elegir(id){ location.href="zona.html?zona="+encodeURIComponent(id); }

/* ============ PASO 2 · RESULTADO ============ */
function resultado(){
  pasos(2);
  const z=S.zona, [p,d]=peor(z), n=d[0];
  const msg = n==="sin" ? `En ${z[1]} no hay alertas reportadas este mes.`
    : n==="bajo" ? `En ${z[1]} hay reportes de ${PATOGENOS[p].nombre.toLowerCase()}, pero dentro de lo normal para esta época.`
    : `En ${z[1]} hay ${NIVEL[n].frase} de ${PATOGENOS[p].nombre.toLowerCase()} para esta época.`;
  const guardado=store.get("epibot-ultimo-"+z[0]), visto=NIVEL[guardado]?guardado:(NIVEL[z[6]]?z[6]:"sin");
  const cambio = visto!==n ? `Desde tu última visita el nivel pasó de <b>${NIVEL[visto].txt}</b> a <b>${NIVEL[n].txt}</b>.` : `El nivel sigue igual que en tu última visita.`;
  store.set("epibot-ultimo-"+z[0], n);
  const tarjetas=Object.entries(z[5]).sort((a,b)=>ORDEN.indexOf(b[1][0])-ORDEN.indexOf(a[1][0])).map(([k,v])=>{
    const [nv,c,e,f,of,fe]=v;
    return `<article class="tarjeta l-${nv}">
      <div class="tarjeta-top"><h3 style="display:flex;align-items:center;gap:10px">${ico(agente(k))}${PATOGENOS[k].nombre}</h3>${chip(nv)}</div>
      ${nv==="sin"?`<p class="nota">${NIVEL.sin.que}</p>`:`
      <div class="cifras"><div><b>${num(c)}</b><span>casos</span></div><div><b>${num(e)}</b><span>esperados</span></div></div>
      <p>${NIVEL[nv].que}</p>
      <div class="fuente"><span class="conf ${of?"ok":""}">${of?"Confirmado por el INS":"Solo noticias, pendiente de confirmación"}</span><span>${f}${fe?" · "+new Date(fe+"T12:00").toLocaleDateString("es-CO",{day:"numeric",month:"short"}):""}</span></div>`}
      <button class="mini-enlace" data-f="${k}">Síntomas y cuidados de ${PATOGENOS[k].nombre.toLowerCase()}</button>
    </article>`;}).join("");
  app.append($(`<section class="vista"><div class="wrap">
    <div class="vista-cab">
      <p class="eyebrow">Tu zona · ${z[1]} ${ETIQUETA_EJEMPLO()}</p>
      <p class="mensaje">${msg}</p>
      <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">${chip(n)}<span class="nota">${NIVEL[n].que}</span></div>
    </div>
    <div class="res-grid">
      <div class="pila">
        <div class="cambio">${cambio}</div>
        ${tarjetas}
        ${z[4].length?`<p class="nota">Municipios mencionados en las alertas: ${z[4].join(", ")}. El nivel es del departamento.</p>`:""}
        <button class="btn btn-1" id="seguir">Seguir: revisión rápida →</button>
      </div>
      <aside class="lateral">
        ${mapa(z[0])}
        <div class="botones"><a class="btn btn-2" href="panel.html">Consultar otra zona</a><a class="btn btn-2" href="fuentes.html">Ver la evidencia</a></div>
      </aside>
    </div>
  </div></section>`));
  document.getElementById("seguir").onclick=()=>ir(revision);
  app.querySelectorAll("[data-f]").forEach(b=>b.onclick=()=>abrirFicha(b.dataset.f,resultado));
}

/* ============ PASO 3 · REVISIÓN RÁPIDA ============ */
function revision(){
  pasos(3);
  app.append($(`<section class="vista"><div class="wrap estrecho">
    <div class="pregunta">
      ${ESCENA_FIEBRE}
      <div class="pila">
        <p class="eyebrow">Revisión rápida</p>
        <h1 style="font-size:clamp(1.8rem,3.4vw,2.5rem)">¿Alguien en casa tiene fiebre?</h1>
        <p class="nota">Según tu respuesta, te mostramos qué vigilar o cómo prevenir.</p>
        <div class="botones"><button class="btn btn-1" id="si">Sí, hay fiebre</button><button class="btn btn-2" id="no">No</button></div>
      </div>
    </div>
  </div></section>`));
  document.getElementById("no").onclick=()=>{S.fiebre=false;S.pIdx=0;S.pReintento=false;ir(practica);};
  document.getElementById("si").onclick=()=>{S.fiebre=true;S.pIdx=0;S.pReintento=false;ir(fiebre);};
}
function fiebre(){
  pasos(3);
  app.append($(`<section class="vista"><div class="wrap">
    <div class="vista-cab"><p class="eyebrow">Si hay fiebre en casa</p><h1 style="font-size:clamp(1.8rem,3.4vw,2.5rem)">Vigila estas señales</h1></div>
    <div class="grid-2">
      <div class="pila">
        <div class="alarma"><h3>Ve a urgencias si aparece:</h3>
          <ul class="lista"><li>Dolor fuerte de barriga</li><li>Vómito que no para</li><li>Sangrado de encías o nariz</li><li>Mucho sueño o le cuesta despertar</li><li>Fiebre en bebés, adultos mayores o embarazadas</li><li>Confusión, piel u ojos amarillos u orina oscura</li></ul></div>
        <div class="no-tomar"><h3>No le des:</h3>
          <p>Ibuprofeno, aspirina, naproxeno ni diclofenaco. Pueden aumentar el riesgo de sangrado si es dengue. Para la fiebre se suele indicar acetaminofén, siempre con consulta médica.</p></div>
      </div>
      <div class="pila">
        <div class="carta"><div style="display:flex;align-items:center;gap:12px">${ico("consultar","ico ico-g")}<h3>Dónde consultar</h3></div>
          <p>Acude al centro de salud más cercano y cuenta desde cuándo empezó la fiebre.</p>
          <a class="btn btn-2" href="centros.html">Ver centros de salud</a></div>
        <div class="carta"><h3>¿Dengue, chikungunya o malaria?</h3><p class="nota">Al inicio se parecen. Compara sus síntomas.</p>
          <div class="pila-s">${Object.entries(PATOGENOS).map(([k,v])=>`<button class="btn btn-2" data-f="${k}" style="justify-content:flex-start">${ico(agente(k))}${v.nombre}</button>`).join("")}</div></div>
      </div>
    </div>
    <div style="margin-top:28px" class="pila">${AVISO}<button class="btn btn-1" id="seguir" style="align-self:flex-start">Seguir a la práctica →</button></div>
  </div></section>`));
  document.getElementById("seguir").onclick=()=>ir(practica);
  app.querySelectorAll("[data-f]").forEach(b=>b.onclick=()=>abrirFicha(b.dataset.f,fiebre));
}

/* ============ PASO 4 · PRÁCTICA ============ */
function practica(){
  pasos(4);
  const PRACTICA = S.fiebre ? PRACTICA_FIEBRE : PRACTICA_SIN_FIEBRE;
  const base=PRACTICA[S.pIdx], it=S.pReintento?base.otra:base;
  app.append($(`<section class="vista"><div class="wrap estrecho">
    <div class="practica">
      <div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap">
        <p class="eyebrow">${S.fiebre?"Practica con tu situación":"Aprende a prevenir"}</p>
        <span class="nota" style="font-variant-numeric:tabular-nums">Situación ${S.pIdx+1} de ${PRACTICA.length}</span></div>
      ${base.nuevo?`<p class="nota">Ahora, una situación nueva.</p>`:""}
      ${S.pReintento?`<p class="nota">Probemos con una parecida.</p>`:""}
      <h2>${it.q}</h2>
      <div class="opciones">${it.ops.map((o,i)=>`<button class="opcion" data-i="${i}">${o[0]}</button>`).join("")}</div>
      <div id="retro"></div>
    </div>
  </div></section>`));
  app.querySelectorAll(".opcion").forEach(b=>b.onclick=()=>{
    const ok=it.ops[b.dataset.i][1];
    app.querySelectorAll(".opcion").forEach(x=>{x.disabled=true; if(it.ops[x.dataset.i][1]) x.classList.add("bien");});
    if(!ok) b.classList.add("mal");
    const reintentar=!ok && !S.pReintento && base.otra;
    document.getElementById("retro").innerHTML=`<div class="pila"><p class="retro ${ok?"bien":"mal"}">${ok?it.bien:it.mal}</p>
      <button class="btn btn-1" id="sig" style="align-self:flex-start">${reintentar?"Intentar otra parecida":(S.pIdx<PRACTICA.length-1?"Siguiente →":"Ver mi plan →")}</button></div>`;
    document.getElementById("sig").onclick=()=>{
      if(reintentar){S.pReintento=true;} else {S.pReintento=false;S.pIdx++;}
      if(S.pIdx>=PRACTICA.length){S.pIdx=0;ir(plan);} else ir(practica);
    };
    document.getElementById("sig").focus();
  });
}

/* ============ PASO 5 · PLAN ============ */
function plan(){
  pasos(5);
  const z=S.zona, n=peor(z)[1][0], acc=PLAN[n];
  const key=`epibot-plan-${z[0]}-${lunes()}`;
  const hecho=store.get(key)||[];
  const enlace=`${location.origin}${location.pathname}?zona=${z[0]}`;
  app.append($(`<section class="vista"><div class="wrap">
    <div class="vista-cab"><p class="eyebrow">Tu plan de la semana · ${z[1]}</p>
      <h1 style="font-size:clamp(1.8rem,3.4vw,2.5rem)">3 acciones para esta semana</h1>
      <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">${chip(n)}<span class="nota">Elegidas según el nivel de tu zona.</span></div></div>
    <div class="res-grid">
      <div class="pila">
        <div class="pila-s"><div class="progreso" aria-hidden="true"><div id="barra"></div></div><p class="nota" id="cuenta"></p></div>
        ${acc.map((a,i)=>`<label class="accion"><input type="checkbox" id="acc-${i}" ${hecho.includes(i)?"checked":""}>${ico(a[2],"ico ico-g")}<div><b>${a[0]}</b><span>${a[1]}</span></div></label>`).join("")}
        ${AVISO}
      </div>
      <aside class="lateral">
        <div class="carta">
          <h3>Llévate tu plan</h3>
          <a class="btn btn-1" id="wa" target="_blank" rel="noopener">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 20l1.3-3.9A8 8 0 1 1 8 19z"/></svg>Enviar por WhatsApp</a>
          <button class="btn btn-2" id="ics">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>Recordarme cada semana</button>
        </div>
        <div class="carta"><h3>Vuelve la próxima semana</h3><p class="nota">Guarda este enlace para ver si el nivel de tu zona cambió.</p>
          <p class="enlace" id="enlace">${enlace}</p><button class="btn btn-2" id="copiar">Copiar enlace</button></div>
        <button class="mini-enlace" id="otra">Empezar de nuevo</button>
      </aside>
    </div>
  </div></section>`));
  const act=()=>{const h=acc.map((_,i)=>document.getElementById("acc-"+i).checked?i:-1).filter(i=>i>=0);
    store.set(key,h); document.getElementById("barra").style.width=(h.length/3*100)+"%";
    document.getElementById("cuenta").textContent=h.length===3?"¡Plan completo esta semana!":`${h.length} de 3 hechas`;};
  acc.forEach((_,i)=>document.getElementById("acc-"+i).onchange=act); act();
  const txt=`Mi plan EpiBot para esta semana (${z[1]}, nivel ${NIVEL[n].txt}):\n${acc.map((a,i)=>`${i+1}. ${a[0]}`).join("\n")}\nSi hay fiebre: no dar ibuprofeno ni aspirina y consultar.\nVer mi zona: ${enlace}`;
  document.getElementById("wa").href="https://wa.me/?text="+encodeURIComponent(txt);
  document.getElementById("ics").onclick=()=>descargarICS(z,acc);
  document.getElementById("copiar").onclick=async()=>{try{await navigator.clipboard.writeText(enlace);toast("Enlace copiado.");}catch(e){const r=document.createRange();r.selectNodeContents(document.getElementById("enlace"));const s=getSelection();s.removeAllRanges();s.addRange(r);toast("Enlace seleccionado. Cópialo desde el menú.");}};
  document.getElementById("otra").onclick=()=>{location.href="index.html#consulta";};
}
function lunes(){const d=new Date();d.setDate(d.getDate()-((d.getDay()+6)%7));return d.toISOString().slice(0,10);}
function descargarICS(z,acc){
  const d=new Date(); d.setDate(d.getDate()+((8-d.getDay())%7||7)); // próximo lunes
  const f=d.toISOString().slice(0,10).replace(/-/g,"");
  const desc=acc.map((a,i)=>`${i+1}. ${a[0]}`).join("\\n");
  const ics=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//EpiBot Colombia//ES","BEGIN:VEVENT",
    `UID:epibot-${z[0]}-${f}@epibot`,`DTSTAMP:${f}T120000Z`,`DTSTART:${f}T130000Z`,`DTEND:${f}T131500Z`,"RRULE:FREQ=WEEKLY",
    `SUMMARY:EpiBot: 3 acciones contra el mosquito`,`DESCRIPTION:${desc}`,"BEGIN:VALARM","TRIGGER:PT0M","ACTION:DISPLAY","DESCRIPTION:EpiBot","END:VALARM","END:VEVENT","END:VCALENDAR"].join("\r\n");
  try{const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([ics],{type:"text/calendar"}));a.download="epibot-recordatorio.ics";document.body.append(a);a.click();a.remove();}catch(e){}
  toast("Recordatorio listo. Ábrelo para agregarlo a tu calendario.");
}

/* ============ FICHAS DE LAS ENFERMEDADES ============ */
function abrirFicha(pat, desde){ if(PAGINA==="zona"){S.volver=desde; S.ficha=pat; ir(ficha);} else location.href="enfermedades.html?p="+pat; }
function ficha(){
  const k=S.ficha, P=PATOGENOS[k], F=FICHAS[k];
  app.append($(`<section class="vista"><div class="wrap">
    <div class="vista-cab">
      ${S.volver?`<button class="mini-enlace" id="volver">← Volver a tu recorrido</button>`:""}
      <p class="eyebrow">Conoce las enfermedades</p>
      <div class="tabs" role="tablist">${Object.keys(PATOGENOS).map(p=>`<button class="tab" role="tab" data-p="${p}" aria-selected="${p===k}">${PATOGENOS[p].nombre}</button>`).join("")}</div>
    </div>
    <div class="ficha-grid">
      <div class="pila lateral">
        <h1>${P.nombre}</h1>
        ${mosquito(F.transmite)}
        <p class="lead">${F.que}</p>
        <div class="datos">
          <div class="carta"><span class="k">Qué es</span><span class="v">${ico(agente(k))}${P.tipo}</span></div>
          <div class="carta"><span class="k">Mosquito</span><span class="v"><i>${F.transmite}</i></span></div>
          <div class="carta" style="grid-column:1/-1"><span class="k">Cuándo pica</span><span class="v">${F.pica}</span></div>
        </div>
      </div>
      <div class="pila">
        <h2>Síntomas</h2>
        <ul class="sint">${F.sintomas.map(([i,x])=>`<li>${ico(i)}<span>${x}</span></li>`).join("")}</ul>
        <p class="nota">Suelen aparecer ${F.aparecen} después de la picadura.</p>
        <div class="alarma"><h3>Señales de alarma: ve a urgencias</h3><ul class="lista">${F.alarma.map(x=>`<li>${x}</li>`).join("")}</ul></div>
        <div class="no-tomar"><h3>Medicamentos</h3><p>${F.medicamentos}</p></div>
        <div class="carta"><h3>Cómo evitarlo</h3><ul class="prev">${F.evitar.map(([i,x])=>`<li>${ico(i)}<span>${x}</span></li>`).join("")}</ul></div>
        ${AVISO}
      </div>
    </div>
  </div></section>`));
  app.querySelectorAll(".tab").forEach(t=>t.onclick=()=>{S.ficha=t.dataset.p;app.innerHTML="";ficha();
    if(!S.volver){try{history.replaceState(null,"","?p="+S.ficha)}catch(e){}}
    document.querySelector(`.tab[data-p="${S.ficha}"]`).focus();});
  const v=document.getElementById("volver"); if(v) v.onclick=()=>ir(S.volver);
}

/* ============ MENÚ ============ */
const PAGINA=document.body.dataset.pagina||"inicio";
const nav=document.getElementById("nav"), menuBtn=document.getElementById("menu-btn");
menuBtn.onclick=()=>{const a=nav.classList.toggle("abierto");menuBtn.setAttribute("aria-expanded",a);};
nav.querySelectorAll("a[data-pag]").forEach(a=>{ if(a.dataset.pag===PAGINA) a.setAttribute("aria-current","page"); });
document.getElementById("salir").onclick=()=>{location.href="index.html";};
document.getElementById("anio").textContent=new Date().getFullYear();
/* ============ ARRANQUE ============ */
// Primero se piden los datos reales; después se dibuja la página
cargarZonas().then(()=>{
  ({inicio, zona:paginaZona, enfermedades:paginaEnfermedades, mapa:paginaMapa, prevencion:paginaPrevencion, como:paginaComo}[PAGINA]||inicio)();
  if(PAGINA==="inicio" && location.hash==="#consulta") setTimeout(()=>document.getElementById("dep")?.focus(),300);
});
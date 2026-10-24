/* ============ MAPA ============
   Contorno simplificado de Colombia dibujado a mano (aprox.).
   En el proyecto, si existe /static/data/colombia.geojson, se cambia por los departamentos reales. */
const CONTORNO=[[-77.37,8.67],[-76.95,8.5],[-76.75,7.95],[-76.45,8.8],[-75.7,9.42],[-75.6,10.3],[-75.25,10.85],[-74.8,11.1],[-74.2,11.3],[-73.3,11.3],[-72.9,11.6],[-72.2,12.15],[-71.7,12.45],[-71.15,12.15],[-71.32,11.8],[-72.2,11.1],[-72.75,10.45],[-72.95,9.85],[-72.95,9.1],[-72.65,8.6],[-72.4,8.0],[-72.45,7.45],[-72.0,7.0],[-71.0,7.0],[-70.1,6.95],[-69.4,6.15],[-68.6,6.2],[-67.45,6.2],[-67.5,5.55],[-67.85,4.5],[-67.3,3.4],[-67.85,2.85],[-67.2,2.3],[-66.87,1.22],[-67.5,1.95],[-68.2,1.75],[-69.75,1.1],[-69.4,0.75],[-70.05,0.55],[-70.05,-0.15],[-69.6,-0.75],[-69.4,-1.4],[-69.75,-2.7],[-69.95,-4.22],[-70.75,-3.8],[-70.3,-2.6],[-71.4,-2.3],[-72.4,-2.45],[-73.1,-2.3],[-73.65,-1.25],[-74.8,-0.2],[-75.25,-0.1],[-75.6,0.05],[-76.4,0.4],[-77.4,0.82],[-78.1,0.95],[-78.85,1.45],[-78.6,1.85],[-78.3,2.6],[-77.65,3.2],[-77.15,3.85],[-77.45,4.5],[-77.35,5.3],[-77.55,5.55],[-77.35,6.0],[-77.45,6.7],[-77.9,7.22],[-77.6,7.6],[-77.37,8.67]];
const MAPA={lon0:-79.6,lon1:-66.4,lat0:-4.5,lat1:12.8,W:300};
MAPA.H=MAPA.W*(MAPA.lat1-MAPA.lat0)/(MAPA.lon1-MAPA.lon0);
const mx=l=>((l-MAPA.lon0)/(MAPA.lon1-MAPA.lon0))*MAPA.W, my=l=>MAPA.H-((l-MAPA.lat0)/(MAPA.lat1-MAPA.lat0))*MAPA.H;
const anillo=r=>"M"+r.map(([x,y])=>mx(x).toFixed(1)+" "+my(y).toFixed(1)).join("L")+"Z";
const norm=t=>(t||"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[^a-z]/g,"");
let GEO=null, geoPedido=false;
// Punto en el centro aproximado del departamento (no en la capital) para que no se encimen
const CENTRO={cordoba:[8.35,-75.8],meta:[3.3,-72.9],choco:[5.9,-76.75],antioquia:[7.0,-75.45],valle:[3.85,-76.45],atlantico:[10.7,-74.95],santander:[6.75,-73.35],tolima:[3.9,-75.25],narino:[1.6,-77.9],bogota:[4.65,-74.1],
  "san-andres":[12.2,-79.1]}; // San Andrés está fuera del recuadro del mapa: se dibuja en la esquina

function fondoMapa(sel){
  if(!GEO) return `<path d="${anillo(CONTORNO)}" fill="var(--ilus-fondo)" stroke="var(--marca)" stroke-width="1.6" stroke-linejoin="round"/>`;
  const nz=sel?norm(zonaPor(sel)[1]):"";
  return GEO.features.map(f=>{
    // Distintos archivos usan distintos nombres de campo: DANE (DPTO_CNMBR), geoBoundaries (shapeName)...
    const pr=f.properties||{};
    const nombre=pr.NOMBRE_DPT||pr.DPTO_CNMBR||pr.shapeName||pr.name||pr.NOMBRE||pr.NAME_1||"";
    const g=f.geometry; if(!g) return "";
    const polis=g.type==="Polygon"?[g.coordinates]:g.coordinates;
    const d=polis.map(p=>p.map(anillo).join("")).join("");
    // Compara sin tildes ni espacios; "Bogotá D.C." también coincide con "Santafé de Bogotá" y "San Andrés" con "Archipiélago de San Andrés"
    const nn=norm(nombre), on=nz && (nn.startsWith(nz.slice(0,6)) || nn.includes(nz.slice(0,6)));
    return `<path d="${d}" fill="${on?"var(--boton-2)":"var(--ilus-fondo)"}" stroke="var(--marca)" stroke-width="${on?1.8:.6}" stroke-linejoin="round"><title>${esc(nombre)}</title></path>`;
  }).join("");
}
function cargarGeo(){
  if(geoPedido) return; geoPedido=true;
  fetch("/static/data/colombia.geojson").then(r=>r.ok?r.json():Promise.reject()).then(j=>{
    GEO=j; document.querySelectorAll(".mapa svg .fondo").forEach(g=>g.innerHTML=fondoMapa(g.dataset.sel));
  }).catch(()=>{});
}
// esc() (escapar texto) está en app.js; se usa cuando ya cargaron todos los scripts
function mapa(sel){
  const W=MAPA.W,H=MAPA.H;
  // Con 33 departamentos los nombres se encimaban: solo se escribe el nombre de los que tienen alguna alerta (también "bajo")
  // y el de la zona elegida; los demás muestran su nombre al pasar el mouse (title).
  // Tamaño del punto: crece con la raíz cuadrada de los casos y tiene tope, para que un número
  // grande (a veces un acumulado del año) no tape a los vecinos. Va de 5 (sin casos) a 10.
  const radio=(n,casos)=> n==="sin" ? 4.5 : 5+Math.min(5, Math.sqrt(casos||0)/8);
  const datos=ZONAS.map(z=>{const [p,d]=peor(z), n=d[0], r=radio(n,d[1]);
    const s=z[0]===sel, c=CENTRO[z[0]]||[z[2],z[3]], X=mx(c[1]), Y=my(c[0]);
    const izq = X>W*0.62 || ["valle","antioquia","choco","narino"].includes(z[0]); // etiquetas a la izquierda en el oriente para que no se salgan
    return {z,p,n,r,s,X,Y,izq};});
  // 1.º los puntos (los grandes primero, así los pequeños quedan encima y se ven); 2.º todos los nombres encima de los puntos
  const puntos=datos.slice().sort((a,b)=>b.r-a.r).map(({z,p,n,r,s,X,Y})=>{
    const borde=n==="moderado"?"#5E4800":"#FFFFFF";
    return `<g><circle cx="${X}" cy="${Y}" r="${r}" fill="var(--${n}-pt)" fill-opacity="${n==="sin"?1:.92}" stroke="${borde}" stroke-width="1.5"/>
      ${s?`<circle cx="${X}" cy="${Y}" r="${r+4}" fill="none" stroke="var(--titulos)" stroke-width="2"/>`:""}<title>${esc(z[1])}: ${PATOGENOS[p].nombre}, ${NIVEL[n].txt}</title></g>`;}).join("");
  const nombres=datos.filter(d=>d.n!=="sin"||d.s).map(({z,r,s,X,Y,izq})=>
    `<text x="${izq?X-r-4:X+r+4}" y="${Y+4}" text-anchor="${izq?"end":"start"}" font-size="${s?12:9.5}" font-weight="${s?700:400}" fill="var(--${s?"titulos":"suave"})" paint-order="stroke" stroke="var(--superficie)" stroke-width="3" font-family="Atkinson Hyperlegible, sans-serif" pointer-events="none">${esc(z[1])}</text>`).join("");
  const pts=puntos+nombres;
  setTimeout(cargarGeo,0);
  return `<div class="mapa"><svg viewBox="-34 -6 ${W+40} ${H+12}" role="img" aria-label="Mapa de Colombia con el nivel más alto de alerta por departamento">
    <g class="fondo" data-sel="${sel||""}">${fondoMapa(sel)}</g>
    ${pts}</svg>
    <div class="leyenda">${ORDEN.slice().reverse().map(chip).join("")}</div>
    <p class="nota" style="margin-top:6px">Cada punto muestra la enfermedad con el nivel más alto en ese departamento. El punto es un poco más grande si hay más casos.</p></div>`;
}
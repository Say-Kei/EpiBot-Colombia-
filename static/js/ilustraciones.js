/* ============ ILUSTRACIONES (SVG propio, colores del logo) ============ */
const K={m:"var(--marca)",o:"var(--marca-oscura)",a:"var(--antena)",f:"var(--ilus-fondo)",p:"var(--piel)",w:"var(--agua)",b:"#FFFFFF"};
const st=(c,w=2)=>`stroke="${c}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"`;
const ICO={
 fiebre:`<rect x="20.5" y="8" width="7" height="24" rx="3.5" fill="${K.b}" ${st(K.o)}/><rect x="23" y="17" width="2" height="16" fill="${K.a}"/><circle cx="24" cy="35" r="6" fill="${K.a}" ${st(K.o)}/><path d="M31 14h4M31 19h3M31 24h4" ${st(K.o,1.6)}/>`,
 cabeza:`<circle cx="24" cy="27" r="11" fill="${K.p}" ${st(K.o)}/><path d="M19.5 26.5h3M25.5 26.5h3M21 32q3-2 6 0" ${st(K.o,1.8)} fill="none"/><path d="M13 11l3 4.5M24 7.5v5.5M35 11l-3 4.5" ${st(K.a,2.6)}/>`,
 ojos:`<path d="M7 25q17-15 34 0q-17 15-34 0z" fill="${K.b}" ${st(K.o)}/><circle cx="24" cy="25" r="5.5" fill="${K.m}"/><circle cx="24" cy="25" r="2" fill="${K.o}"/><path d="M35 9l-2.5 4.5M41 14l-4 2.5" ${st(K.a,2.6)}/>`,
 articulaciones:`<path d="M17 7v17l9 17" ${st(K.p,8)} fill="none"/><path d="M17 7v17l9 17" ${st(K.o,1.4)} fill="none" opacity=".35"/><circle cx="17" cy="24" r="7" fill="none" ${st(K.a,2.6)} stroke-dasharray="3 3"/><path d="M30 15l3-3M32 22h4" ${st(K.a,2.6)}/>`,
 piel:`<rect x="9" y="14" width="30" height="21" rx="9" fill="${K.p}" ${st(K.o)}/><circle cx="17" cy="21" r="2.2" fill="${K.o}" opacity=".45"/><circle cx="25" cy="27" r="2.6" fill="${K.o}" opacity=".45"/><circle cx="31" cy="20" r="1.8" fill="${K.o}" opacity=".45"/><circle cx="19" cy="29" r="1.6" fill="${K.o}" opacity=".45"/>`,
 escalofrios:`<g ${st(K.m,2.6)}><path d="M24 9v30M11 16.5l26 15M37 16.5l-26 15"/><path d="M20 11l4 4 4-4M20 37l4-4 4 4"/></g>`,
 sudor:`<path d="M18 10c5 7 8 11 8 15a8 8 0 0 1-16 0c0-4 3-8 8-15z" fill="${K.w}" ${st(K.o)}/><path d="M33 22c3 4 5 6.5 5 9a5 5 0 0 1-10 0c0-2.5 2-5 5-9z" fill="${K.w}" ${st(K.o)}/>`,
 cansancio:`<rect x="8" y="17" width="28" height="15" rx="3" fill="${K.b}" ${st(K.o)}/><rect x="36" y="21" width="4" height="7" rx="1.5" fill="${K.o}"/><rect x="11" y="20" width="6" height="9" rx="1" fill="${K.a}"/><path d="M28 6h6l-6 6h6" ${st(K.m,2)} fill="none"/>`,
 decaimiento:`<circle cx="24" cy="18" r="7" fill="${K.p}" ${st(K.o)}/><path d="M12 40q2-13 12-13t12 13" fill="${K.m}" ${st(K.o)}/><path d="M21 18q3 2 6 0" ${st(K.o,1.6)} fill="none"/>`,
 tanque:`<rect x="10" y="10" width="28" height="6" rx="2" fill="${K.o}"/><rect x="12" y="16" width="24" height="23" rx="3" fill="${K.m}"/><path d="M15 26q3-2.5 6 0t6 0t6 0" ${st(K.b,2)} fill="none"/><path d="M15 32q3-2.5 6 0t6 0t6 0" ${st(K.b,2)} fill="none" opacity=".6"/>`,
 tapar:`<path d="M14 19h20l-2.5 20h-15z" fill="${K.m}"/><rect x="11" y="13" width="26" height="6" rx="2.5" fill="${K.o}"/><rect x="21" y="9" width="6" height="4" rx="1.5" fill="${K.o}"/><path d="M38 10l2 2 4-5" ${st(K.a,2.6)} fill="none"/>`,
 repelente:`<rect x="16" y="19" width="15" height="21" rx="4" fill="${K.m}"/><rect x="19" y="13" width="9" height="6" rx="1.5" fill="${K.o}"/><path d="M27 15h5" ${st(K.o,2.4)}/><rect x="19" y="25" width="9" height="8" rx="1.5" fill="${K.b}" opacity=".85"/><g fill="${K.a}"><circle cx="37" cy="12" r="1.8"/><circle cx="40" cy="16" r="1.8"/><circle cx="37" cy="19" r="1.5"/><circle cx="42" cy="11" r="1.4"/></g>`,
 toldillo:`<path d="M9 31Q24 2 39 31" fill="${K.b}" fill-opacity=".55" ${st(K.o,1.6)} stroke-dasharray="2 3"/><path d="M24 6v4" ${st(K.o,1.6)}/><rect x="8" y="29" width="32" height="7" rx="2" fill="${K.m}"/><rect x="11" y="25" width="9" height="5" rx="2.5" fill="${K.b}" ${st(K.o,1.2)}/><path d="M10 36v4M38 36v4" ${st(K.o,2.4)}/>`,
 ropa:`<path d="M18 9l-10 6 3 9 4-2v18h18V22l4 2 3-9-10-6q-6 5-12 0z" fill="${K.m}" ${st(K.o,1.6)}/><path d="M18 9q6 5 12 0" ${st(K.a,2)} fill="none"/>`,
 viaje:`<rect x="9" y="16" width="30" height="22" rx="4" fill="${K.m}"/><path d="M19 16v-4h10v4" ${st(K.o,2.4)} fill="none"/><path d="M16 16v22M32 16v22" ${st(K.o,2)} opacity=".5"/><rect x="34" y="24" width="7" height="9" rx="1.5" fill="${K.a}"/>`,
 agua:`<path d="M15 14h18l-3 25H18z" fill="${K.b}" ${st(K.o)}/><path d="M16.2 24h15.6l-1.9 15H18.1z" fill="${K.w}"/><path d="M24 14V6M24 9q-6-4-8 1M24 9q6-4 8 1" ${st(K.m,2.2)} fill="none"/>`,
 llanta:`<circle cx="24" cy="25" r="15" fill="${K.o}"/><circle cx="24" cy="25" r="7" fill="${K.f}"/><path d="M12 27q12 6 24 0" ${st(K.w,3)} fill="none"/>`,
 consultar:`<rect x="10" y="16" width="28" height="23" rx="2" fill="${K.m}"/><path d="M8 17l16-9 16 9" ${st(K.o,2.4)} fill="none"/><rect x="21" y="19" width="6" height="14" rx="1" fill="${K.b}"/><rect x="17" y="23" width="14" height="6" rx="1" fill="${K.b}"/>`,
 virus:`<g ${st(K.a,2.4)}><path d="M24 8v6M24 34v6M8 24h6M34 24h6M12.7 12.7l4.2 4.2M31.1 31.1l4.2 4.2M12.7 35.3l4.2-4.2M31.1 16.9l4.2-4.2"/></g><circle cx="24" cy="24" r="10" fill="${K.a}"/><circle cx="21" cy="21" r="2" fill="${K.o}" opacity=".35"/><circle cx="27" cy="27" r="2.5" fill="${K.o}" opacity=".35"/>`,
 parasito:`<path d="M10 30q4-16 18-17t12 6q-4 12-18 14t-12-3z" fill="${K.a}" ${st(K.o,1.6)}/><circle cx="22" cy="24" r="2.4" fill="${K.o}" opacity=".5"/><circle cx="29" cy="21" r="2" fill="${K.o}" opacity=".5"/><path d="M40 19q4 2 3 6" ${st(K.o,1.6)} fill="none"/>`
};
function ico(n,cls="ico"){return `<svg class="${cls}" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="23.5" fill="${K.f}"/>${ICO[n]||""}</svg>`;}

/* Mosquito grande: Aedes (patas con rayas blancas) o Anopheles (cuerpo inclinado, alas manchadas) */
function mosquito(tipo){
  const an=tipo==="Anopheles";
  const patas=an
   ? `<path d="M128 92l-22 34M136 94l-6 40M146 92l14 36M120 88l-34 16M150 88l34 10" ${st(K.o,2.4)} fill="none"/>`
   : [ "M120 96l-30 34","M132 98l-10 42","M144 98l8 40","M156 96l30 30","M112 92l-40 4","M162 92l38-8" ]
      .map(d=>`<path d="${d}" ${st(K.o,3.4)} fill="none"/><path d="${d}" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="3 5" fill="none"/>`).join("");
  const cuerpo=an
   ? `<g transform="rotate(-32 138 86)"><ellipse cx="166" cy="86" rx="40" ry="8" fill="${K.o}"/><ellipse cx="124" cy="86" rx="12" ry="10" fill="${K.o}"/><circle cx="106" cy="86" r="8" fill="${K.o}"/><path d="M98 86h-30" ${st(K.o,2.4)}/></g>`
   : `<ellipse cx="170" cy="88" rx="36" ry="9" fill="${K.o}"/><path d="M146 84h40M150 92h36" stroke="#FFFFFF" stroke-width="2" opacity=".85"/><ellipse cx="134" cy="88" rx="12" ry="10" fill="${K.o}"/><path d="M128 82q6 6 0 12" stroke="#FFFFFF" stroke-width="2" fill="none"/><circle cx="116" cy="90" r="8" fill="${K.o}"/><path d="M108 92l-30 10" ${st(K.o,2.4)}/>`;
  const alas=`<path d="M136 80q20-40 64-44q-14 34-58 46z" fill="#FFFFFF" fill-opacity=".75" ${st(K.o,1.6)}/><path d="M140 80q-2-34 26-56q4 30-22 58z" fill="#FFFFFF" fill-opacity=".6" ${st(K.o,1.4)}/>`
    + (an?`<g fill="${K.o}" opacity=".55"><circle cx="160" cy="58" r="3"/><circle cx="176" cy="50" r="3"/><circle cx="190" cy="44" r="2.5"/><circle cx="150" cy="48" r="2.5"/></g>`:"");
  const alasYcuerpo = an ? `<g transform="rotate(-32 138 86)">${alas}</g>${cuerpo}` : alas+cuerpo;
  return `<div class="escena"><svg class="ilus" viewBox="40 10 200 140" role="img" aria-label="Ilustración del mosquito ${tipo}">
    <ellipse cx="140" cy="140" rx="70" ry="5" fill="${K.o}" opacity=".08"/>${alasYcuerpo}${patas}</svg></div>`;
}
/* Escena de la revisión: termómetro y casa */
const ESCENA_FIEBRE=`<div class="escena"><svg class="ilus" viewBox="0 0 240 120" role="img" aria-label="Ilustración de una casa y un termómetro">
  <path d="M30 70l50-38 50 38v42H30z" fill="${K.m}"/><path d="M22 74l58-46 58 46" ${st(K.o,5)} fill="none"/>
  <rect x="68" y="80" width="24" height="32" rx="3" fill="${K.b}"/><rect x="44" y="72" width="16" height="14" rx="2" fill="${K.a}"/><rect x="100" y="72" width="16" height="14" rx="2" fill="${K.a}"/>
  <rect x="164" y="18" width="16" height="72" rx="8" fill="${K.b}" ${st(K.o,3)}/><rect x="169" y="40" width="6" height="52" fill="${K.a}"/><circle cx="172" cy="96" r="15" fill="${K.a}" ${st(K.o,3)}/>
  <path d="M188 30h10M188 44h7M188 58h10M188 72h7" ${st(K.o,2.4)}/><path d="M206 20l8-8M212 32h10" ${st(K.a,3.4)}/></svg></div>`;

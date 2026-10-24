/* ============ DATOS DE EJEMPLO ============
   En el proyecto real, la página intenta primero /api/alertas y /api/historico.
   Si la API no responde (como aquí), usa estos datos de ejemplo. */
const PATOGENOS = {
  dengue:{nombre:"Dengue",tipo:"Virus",mosquito:"Aedes aegypti"},
  chikungunya:{nombre:"Chikungunya",tipo:"Virus",mosquito:"Aedes aegypti"},
  malaria:{nombre:"Malaria",tipo:"Parásito",mosquito:"Anopheles"}
};
const NIVEL = {
  critico:{txt:"Crítico",frase:"muchos más casos de lo normal",que:"Extrema las precauciones y consulta ante fiebre."},
  alto:{txt:"Alto",frase:"más casos de lo normal",que:"Refuerza la prevención esta semana."},
  moderado:{txt:"Moderado",frase:"reportes oficiales de casos",que:"Mantén las medidas básicas."},
  bajo:{txt:"Sin alertas reportadas",frase:"",que:"No hay señales recientes. Que no haya reportes no significa que no haya casos."}
};
// [id, nombre, lat, lon, municipios mencionados, {patogeno:[nivel, casos, esperado, fuente, oficial, fecha]}, nivel semana anterior de dengue]
const ZONAS = [
 ["cordoba","Córdoba",8.75,-75.88,["Montería","Lorica"],{dengue:["alto",412,290,"Boletín INS",true,"2026-10-20"],chikungunya:["bajo",0,0,"",false,""],malaria:["moderado",38,35,"Boletín INS",true,"2026-10-20"]},"moderado"],
 ["meta","Meta",4.14,-73.63,["Villavicencio","Granada"],{dengue:["critico",655,340,"Boletín INS + prensa regional",true,"2026-10-20"],chikungunya:["moderado",12,9,"Boletín INS",true,"2026-10-20"],malaria:["bajo",0,0,"",false,""]},"alto"],
 ["choco","Chocó",5.69,-76.66,["Quibdó","Tadó"],{dengue:["moderado",96,88,"Boletín INS",true,"2026-10-20"],chikungunya:["bajo",0,0,"",false,""],malaria:["critico",1240,700,"Boletín INS",true,"2026-10-20"]},"moderado"],
 ["antioquia","Antioquia",6.25,-75.56,["Medellín","Apartadó"],{dengue:["moderado",380,360,"Boletín INS",true,"2026-10-20"],chikungunya:["bajo",0,0,"",false,""],malaria:["alto",310,220,"Boletín INS",true,"2026-10-20"]},"moderado"],
 ["valle","Valle del Cauca",3.45,-76.53,["Cali","Buenaventura"],{dengue:["alto",520,400,"Prensa local",false,"2026-10-21"],chikungunya:["bajo",0,0,"",false,""],malaria:["moderado",44,40,"Boletín INS",true,"2026-10-20"]},"alto"],
 ["atlantico","Atlántico",10.96,-74.80,["Barranquilla","Soledad"],{dengue:["moderado",140,130,"Boletín INS",true,"2026-10-20"],chikungunya:["bajo",0,0,"",false,""],malaria:["bajo",0,0,"",false,""]},"moderado"],
 ["santander","Santander",7.12,-73.12,["Bucaramanga"],{dengue:["alto",290,200,"Boletín INS",true,"2026-10-20"],chikungunya:["bajo",0,0,"",false,""],malaria:["bajo",0,0,"",false,""]},"alto"],
 ["tolima","Tolima",4.44,-75.23,["Ibagué"],{dengue:["moderado",160,150,"Boletín INS",true,"2026-10-20"],chikungunya:["bajo",0,0,"",false,""],malaria:["bajo",0,0,"",false,""]},"bajo"],
 ["narino","Nariño",1.21,-77.28,["Tumaco"],{dengue:["bajo",0,0,"",false,""],chikungunya:["bajo",0,0,"",false,""],malaria:["alto",260,180,"Boletín INS",true,"2026-10-20"]},"bajo"],
 ["bogota","Bogotá D.C.",4.71,-74.07,[],{dengue:["bajo",0,0,"",false,""],chikungunya:["bajo",0,0,"",false,""],malaria:["bajo",0,0,"",false,""]},"bajo"]
];
const ORDEN = ["bajo","moderado","alto","critico"];

const FICHAS = {
 dengue:{aparecen:"entre 4 y 10 días",transmite:"Aedes aegypti", pica:"De día, sobre todo al amanecer y al atardecer",
  que:"Un virus que transmite el mosquito Aedes aegypti, que vive cerca de las casas y se cría en agua quieta y limpia.",
  sintomas:[["fiebre","Fiebre alta"],["cabeza","Dolor de cabeza"],["ojos","Dolor detrás de los ojos"],["articulaciones","Dolor de músculos y articulaciones"],["piel","Manchas en la piel"]],
  alarma:["Dolor fuerte de barriga","Vómito que no para","Sangrado de encías o nariz","Mucho sueño o le cuesta despertar"],
  evitar:[["tanque","Lavar y restregar el tanque cada semana"],["tapar","Tapar los recipientes con agua"],["repelente","Usar repelente"],["toldillo","Dormir con toldillo"],["ropa","Ropa que cubra brazos y piernas"]],
  medicamentos:"No tomar ibuprofeno, aspirina, naproxeno ni diclofenaco: aumentan el riesgo de sangrado. Para la fiebre se suele indicar acetaminofén, siempre con consulta médica."},
 chikungunya:{aparecen:"entre 3 y 7 días",transmite:"Aedes aegypti", pica:"De día, igual que el dengue",
  que:"Un virus que transmite el mismo mosquito del dengue. Su señal más clara es el dolor fuerte en las articulaciones.",
  sintomas:[["fiebre","Fiebre"],["articulaciones","Dolor fuerte de articulaciones"],["cansancio","Dolor que puede durar semanas"],["cabeza","Dolor de cabeza"],["piel","Manchas en la piel"]],
  alarma:["Fiebre en bebés, adultos mayores o embarazadas","Dolor que no cede","Mucho decaimiento"],
  evitar:[["agua","Lo mismo que para el dengue: es el mismo mosquito"],["tanque","Lavar y tapar el agua guardada"],["repelente","Repelente y toldillo"]],
  medicamentos:"Las mismas precauciones que el dengue, porque al inicio se confunden: no tomar ibuprofeno ni aspirina hasta que un médico descarte el dengue."},
 malaria:{aparecen:"desde 7 días hasta un mes o más",transmite:"Anopheles", pica:"Al atardecer y en la noche",
  que:"Un parásito (Plasmodium) que transmite el mosquito Anopheles. Es más común en zonas rurales y selváticas, como el Pacífico y la Orinoquía.",
  sintomas:[["escalofrios","Fiebre con escalofríos"],["sudor","Sudor intenso"],["cabeza","Dolor de cabeza"],["cansancio","Cansancio"]],
  alarma:["Confusión","Dificultad para respirar","Piel u ojos amarillos","Orina oscura"],
  evitar:[["toldillo","Dormir con toldillo"],["repelente","Repelente al atardecer y en la noche"],["viaje","Consultar antes de viajar a zona de malaria"]],
  medicamentos:"No automedicarse. Necesita diagnóstico (gota gruesa o prueba rápida) y un tratamiento que formula el médico."}
};


const PLAN = {
  critico:[["Lava y cepilla el tanque","Restriega las paredes: los huevos del mosquito se pegan ahí.","tanque"],["Tapa todo recipiente con agua","Baldes, botellas, llantas y floreros. Revisa el patio dos veces.","tapar"],["Repelente y toldillo","Repelente al amanecer y al atardecer. Toldillo para dormir, sobre todo niños.","toldillo"]],
  alto:[["Lava el tanque","Una vez esta semana, restregando las paredes.","tanque"],["Tapa los recipientes con agua","Baldes, botellas y floreros, dentro y fuera de la casa.","tapar"],["Usa repelente al atardecer","Es una de las horas en que más pica el mosquito.","repelente"]],
  moderado:[["Revisa el agua quieta","Vacía floreros, llantas y tapas que junten agua.","llanta"],["Tapa el tanque","Mantenlo cerrado toda la semana.","tanque"],["Ten repelente a mano","Úsalo si sales al atardecer.","repelente"]],
  bajo:[["Revisa el agua quieta","Una revisión rápida del patio y la casa.","agua"],["Tapa el tanque","Es la medida más simple y la más útil.","tanque"],["Si viajas, infórmate","Consulta tu destino en EpiBot antes de salir.","viaje"]]
};

const VIAJE={q:"Vas de viaje a Villavicencio la próxima semana con tus hijos. ¿Qué haces?",
  ops:[["Nada, el dengue solo está en mi barrio",false],["Reviso cómo está el Meta y llevo repelente y toldillo",true],["Llevo ibuprofeno por si hay fiebre",false]],
  bien:"Muy bien. Aplicaste lo aprendido a un lugar nuevo. Antes de viajar, consulta la zona de destino.",
  mal:"El mosquito está en muchas zonas cálidas. Antes de viajar, revisa el destino y lleva repelente y toldillo.",
  nuevo:true};

const PRACTICA_SIN_FIEBRE = [
 {q:"Esta semana en tu zona hay más casos de dengue. ¿Qué haces primero en casa?",
  ops:[["Esperar a que pase la fumigación",false],["Lavar el tanque y tapar los recipientes con agua",true],["Echar insecticida solo en la sala",false]],
  bien:"Correcto. El mosquito pone sus huevos en agua quieta y limpia. Sin agua quieta, no hay mosquitos nuevos.",
  mal:"La fumigación y el insecticida matan mosquitos adultos, pero los huevos siguen en el agua. Lo que más sirve es lavar y tapar.",
  otra:{q:"Encuentras una llanta vieja en el patio con agua de lluvia. ¿Qué haces?",
   ops:[["La dejo, es agua de lluvia",false],["La vacío y la guardo bajo techo",true],["Le echo un poco de cloro y la dejo",false]],
   bien:"Bien. Sin agua acumulada, el mosquito no tiene dónde poner huevos.",
   mal:"El agua de lluvia también sirve de criadero. Vacíala y guárdala donde no vuelva a llenarse."}},
 {q:"Si algún día alguien en casa tiene fiebre alta y dolor de cuerpo, ¿qué medicamento NO le das sin consultar?",
  ops:[["Ibuprofeno o aspirina",true],["Suero oral",false],["Agua y líquidos",false]],
  bien:"Correcto. Si es dengue, el ibuprofeno y la aspirina pueden aumentar el riesgo de sangrado. Para la fiebre se suele indicar acetaminofén, con consulta médica.",
  mal:"Los líquidos ayudan. Los que se evitan son el ibuprofeno y la aspirina, porque si es dengue pueden aumentar el riesgo de sangrado.",
  otra:{q:"Si algún día alguien con fiebre empieza a sangrar por las encías, ¿qué haces?",
   ops:[["Ir a urgencias ese mismo día",true],["Esperar a que pase",false],["Darle aspirina",false]],
   bien:"Bien. El sangrado de encías o nariz con fiebre es una señal de alarma.",
   mal:"El sangrado de encías o nariz con fiebre es una señal de alarma: hay que ir a urgencias."}},
 VIAJE
];
const PRACTICA_FIEBRE = [
 {q:"La persona con fiebre en tu casa tiene también dolor de cuerpo. En tu zona hay dengue. ¿Qué le das mientras consultas?",
  ops:[["Ibuprofeno",false],["Acetaminofén, según indique el médico",true],["Aspirina",false]],
  bien:"Correcto. Ante sospecha de dengue se suele indicar acetaminofén, siempre con consulta médica.",
  mal:"El ibuprofeno y la aspirina pueden aumentar el riesgo de sangrado si es dengue. Mejor acetaminofén, con consulta médica.",
  otra:{q:"Tu vecina tiene fiebre y dolor detrás de los ojos. Te pide algo para el dolor. ¿Qué le recomiendas?",
   ops:[["Naproxeno o diclofenaco",false],["Que consulte y no tome antiinflamatorios",true],["Aspirina para bajar la fiebre",false]],
   bien:"Bien. Naproxeno, diclofenaco, ibuprofeno y aspirina se evitan ante sospecha de dengue.",
   mal:"Naproxeno, diclofenaco y aspirina también son antiinflamatorios. Se evitan ante sospecha de dengue."}},
 {q:"Al tercer día de fiebre, empieza con dolor fuerte de barriga y vomita varias veces. ¿Qué haces?",
  ops:[["Esperar a que baje la fiebre",false],["Ir a urgencias ya",true],["Darle suero casero y esperar a mañana",false]],
  bien:"Correcto. El dolor fuerte de abdomen y el vómito persistente son señales de alarma.",
  mal:"El dolor fuerte de abdomen y el vómito persistente son señales de alarma: hay que ir a urgencias ese mismo día.",
  otra:{q:"Tu sobrina tiene fiebre y le sangran las encías al cepillarse. ¿Qué haces?",
   ops:[["Ir a urgencias ya",true],["Cambiarle el cepillo",false],["Esperar dos días",false]],
   bien:"Bien. El sangrado de encías o nariz con fiebre es una señal de alarma.",
   mal:"El sangrado de encías o nariz con fiebre es una señal de alarma: ve a urgencias."}},
 VIAJE
];

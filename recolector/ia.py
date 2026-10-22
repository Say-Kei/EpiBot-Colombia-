"""Le pide a la IA que saque de cada noticia: patógeno, departamento, municipios, casos y fecha."""
import json
import os
import ssl

import httpx
import truststore
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
truststore.inject_into_ssl()  # usa los certificados de Windows (antivirus o red de la universidad)
cliente = OpenAI(base_url=os.getenv("IA_URL"), api_key=os.getenv("IA_KEY"),
                 http_client=httpx.Client(verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)))
MODELO = os.getenv("IA_MODELO")

INSTRUCCIONES = """Eres un asistente de vigilancia epidemiológica en Colombia.
Del texto, extrae SOLO lo que dice explícitamente. Responde únicamente un JSON con:
patogeno, departamento, municipios (lista), casos (número), fecha (AAAA-MM-DD).
Si un dato no aparece, escribe null. No adivines ni calcules.
Si el texto menciona una ciudad, escribe también su departamento (ej. Cali -> Valle del Cauca).
Patógenos válidos: dengue, malaria, tosferina, fiebre amarilla, oropouche, chikungunya.
Si el patógeno no es uno de esos, escribe null en patogeno.
Si el texto NO informa casos, contagios, muertes o un brote en un lugar concreto
(por ejemplo: congresos, campañas de vacunación, consejos de prevención), responde todo null."""

EJEMPLOS = [
    {"role": "user", "content": "Cali reporta 340 casos de dengue en la última semana, dijo la Secretaría de Salud del Valle."},
    {"role": "assistant", "content": '{"patogeno": "dengue", "departamento": "Valle del Cauca", "municipios": ["Cali"], "casos": 340, "fecha": null}'},
    {"role": "user", "content": "Aumentan las consultas por fiebre en el país, según expertos."},
    {"role": "assistant", "content": '{"patogeno": null, "departamento": null, "municipios": [], "casos": null, "fecha": null}'},
    {"role": "user", "content": "El 3 de octubre de 2026 la gobernación de Córdoba confirmó 12 casos de chikunguña en Montería y Lorica."},
    {"role": "assistant", "content": '{"patogeno": "chikungunya", "departamento": "Córdoba", "municipios": ["Montería", "Lorica"], "casos": 12, "fecha": "2026-10-03"}'},
    {"role": "user", "content": "Bogotá será sede de un congreso internacional sobre malaria y fiebre amarilla."},
    {"role": "assistant", "content": '{"patogeno": null, "departamento": null, "municipios": [], "casos": null, "fecha": null}'},
]


def extraer(texto):
    try:
        r = cliente.chat.completions.create(
            model=MODELO, temperature=0,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": INSTRUCCIONES}, *EJEMPLOS,
                      {"role": "user", "content": texto}])
        return json.loads(r.choices[0].message.content)
    except Exception as e:
        print("La IA no respondió bien:", e)
        return None
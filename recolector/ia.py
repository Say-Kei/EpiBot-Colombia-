"""Le pide a la IA que saque de cada noticia: patógeno, departamento, municipios, casos y fecha."""
import json
import os
import ssl
import time

import httpx
import truststore
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, APIError

LIMITE_TPM = 1000               # tokens por minuto de la cuenta de Groq
PRESUPUESTO_EJECUCION = 45000   # 200.000 al día / 4 ejecuciones, con margen
MAX_TOKENS_SALIDA = 300
MAX_REINTENTOS = 3
ESPERA_MAXIMA = 90              # si Groq pide esperar más, es el límite del día
tokens_usados = 0               # contador de esta ejecución

load_dotenv()
truststore.inject_into_ssl()  # usa los certificados de Windows (antivirus o red de la universidad)
cliente = OpenAI(base_url=os.getenv("IA_URL"), api_key=os.getenv("IA_KEY"),
                 http_client=httpx.Client(verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)),
                 max_retries=0)  # los reintentos los controlamos nosotros
MODELO = os.getenv("IA_MODELO")


class LimiteAgotado(Exception):
    """Se acabó la cuota de Groq: hay que parar y guardar lo que se tenga."""


INSTRUCCIONES = """Eres un asistente de vigilancia epidemiológica en Colombia.
Del texto, extrae SOLO lo que dice explícitamente. Responde únicamente un JSON con:
patogeno, departamento, municipios (lista), casos (número), fecha (AAAA-MM-DD).
Si un dato no aparece, escribe null (y [] en municipios). No adivines ni calcules.
Si el texto menciona una ciudad, escribe también su departamento (ej. Cali -> Valle del Cauca).
Patógenos válidos: dengue, malaria, tosferina, fiebre amarilla, oropouche, chikungunya.
Si el patógeno no es uno de esos, escribe null en patogeno.
Si el texto NO informa casos, contagios, muertes o un brote en un lugar concreto
(por ejemplo: congresos, campañas de vacunación, consejos de prevención), responde todo null."""

EJEMPLOS = [
    {"role": "user", "content": "Cali reporta 340 casos de dengue en la última semana, dijo la Secretaría de Salud del Valle."},
    {"role": "assistant", "content": '{"patogeno": "dengue", "departamento": "Valle del Cauca", "municipios": ["Cali"], "casos": 340, "fecha": null}'},
]


def segundos_de_espera(error, intento):
    """Lee cuántos segundos pide esperar Groq; si no lo dice, espera 5, 10, 20."""
    try:
        return float(error.response.headers.get("retry-after"))
    except (TypeError, ValueError, AttributeError):
        return 5 * (2 ** intento)


def extraer(texto):
    global tokens_usados
    for intento in range(MAX_REINTENTOS):
        try:
            r = cliente.chat.completions.create(
                model=MODELO, temperature=0,
                max_completion_tokens=MAX_TOKENS_SALIDA,
                reasoning_effort="low",
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": INSTRUCCIONES}, *EJEMPLOS,
                          {"role": "user", "content": texto}])

            gastados = r.usage.total_tokens if r.usage else LIMITE_TPM
            tokens_usados += gastados
            print(f"  tokens: {gastados} | en esta ejecución: {tokens_usados}")
            if tokens_usados >= PRESUPUESTO_EJECUCION:
                raise LimiteAgotado("Se alcanzó el presupuesto de tokens de esta ejecución")
            time.sleep(gastados / LIMITE_TPM * 60 + 1)   # pausa proporcional a lo gastado

            return json.loads(r.choices[0].message.content or "")

        except RateLimitError as e:
            espera = segundos_de_espera(e, intento)
            if espera > ESPERA_MAXIMA:
                raise LimiteAgotado(f"Groq pide esperar {espera:.0f} s: cuota agotada")
            print(f"  429 de Groq: espero {espera:.0f} s (intento {intento + 1}/{MAX_REINTENTOS})")
            time.sleep(espera)

        except json.JSONDecodeError:
            print("  La respuesta no era JSON válido (quizá se cortó); salto este texto")
            return None

        except APIError as e:
            print("  Error de la API:", e)
            return None

    print("  Se agotaron los reintentos; salto este texto")
    return None


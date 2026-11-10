# Bot de Gastos por WhatsApp

Asistente financiero personal desarrollado con **Python, FastAPI, SQLAlchemy, SQLite, n8n y WhatsApp Cloud API**.

El sistema permite registrar ingresos y gastos mediante mensajes de WhatsApp, consultar resúmenes financieros, agrupar gastos por categoría y exportar la información a un archivo Excel.

---

## 1. Funcionalidades actuales

El bot permite:

- Registrar gastos.
- Registrar ingresos.
- Detectar categorías automáticamente.
- Detectar algunos medios de pago.
- Consultar un resumen de ingresos, gastos y saldo.
- Consultar gastos agrupados por categoría.
- Consultar movimientos según períodos.
- Exportar movimientos a Excel.
- Generar una hoja de resumen dentro del Excel.
- Generar un gráfico de gastos por categoría.
- Responder mediante WhatsApp.
- Manejar mensajes que no pueden interpretarse.

Ejemplos de mensajes:

```text
Gaste 5000 en comida

Gaste 3500 en nafta con debito

Ingrese 20000 de sueldo

Resumen

Resumen de hoy

Cuanto gaste el mes pasado

Categorias

En que gaste este mes

Categorias del mes pasado

Exportar Excel
```

Actualmente la interpretación de mensajes utiliza reglas, palabras clave y expresiones regulares. No se utiliza todavía un modelo de Inteligencia Artificial externo.

---

# 2. Arquitectura

El flujo general del sistema es:

```text
Usuario
   │
   ▼
WhatsApp
   │
   ▼
WhatsApp Cloud API - Meta
   │
   ▼
FastAPI
/whatsapp/webhook
   │
   ▼
n8n
   │
   ├── Webhook
   ├── If
   ├── HTTP Request
   │       │
   │       ▼
   │   FastAPI
   │   /movimientos/mensaje
   │       │
   │       ▼
   │     SQLite
   │
   └── HTTP Request2
           │
           ▼
      Meta Graph API
           │
           ▼
        WhatsApp
```

FastAPI contiene la lógica del dominio.

n8n se utiliza principalmente para orquestar el flujo entre WhatsApp, FastAPI y Meta.

---

# 3. Tecnologías utilizadas

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- HTTPX
- openpyxl
- Uvicorn
- n8n
- Docker
- Meta WhatsApp Cloud API
- GitHub Codespaces durante desarrollo

---

# 4. Requisitos previos

Para ejecutar el proyecto se necesita:

```text
Python 3.12 recomendado
Git
Docker
Una cuenta de Meta Developers
Una aplicación configurada con WhatsApp Cloud API
```

Si se utiliza GitHub Codespaces, Docker y Git ya se encuentran disponibles normalmente en el entorno.

---

# 5. Clonar el proyecto

```bash
git clone https://github.com/maybran04/bot-gastos-whatsapp.git

cd bot-gastos-whatsapp
```

---

# 6. Crear el entorno virtual de Python

Python incluye el módulo estándar `venv`, utilizado para aislar las dependencias del proyecto.

Crear el entorno:

```bash
python -m venv .venv
```

En Linux, macOS o GitHub Codespaces:

```bash
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Una vez activado debería aparecer algo similar a:

```text
(.venv)
```

al comienzo de la terminal.

---

# 7. Instalar dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

Entre las principales dependencias se encuentran:

```text
fastapi
uvicorn
sqlalchemy
httpx
openpyxl
pydantic
```

---

# 8. Base de datos

El proyecto utiliza actualmente SQLite.

La base se genera en:

```text
gastos.db
```

No es necesario crearla manualmente.

Al iniciar FastAPI se ejecuta:

```python
Base.metadata.create_all(bind=engine)
```

por lo que las tablas necesarias se crean automáticamente.

El archivo:

```text
gastos.db
```

está excluido de Git mediante `.gitignore`.

Por lo tanto, cada nueva instalación comienza con su propia base de datos local.

---

# 9. Variables de entorno

El proyecto utiliza variables de entorno para datos que no deben escribirse directamente en el código.

Las principales son:

```text
WHATSAPP_VERIFY_TOKEN
N8N_WEBHOOK_URL
PUBLIC_BASE_URL
```

## WHATSAPP_VERIFY_TOKEN

Token utilizado por Meta para verificar el webhook.

Ejemplo:

```bash
export WHATSAPP_VERIFY_TOKEN="un_token_elegido_por_el_desarrollador"
```

El mismo valor debe configurarse posteriormente en Meta Developers.

---

## N8N_WEBHOOK_URL

URL hacia el webhook de producción de n8n.

Cuando n8n se ejecuta localmente exponiendo el puerto `5678`:

```bash
export N8N_WEBHOOK_URL="http://127.0.0.1:5678/webhook/whatsapp-verificacion"
```

---

## PUBLIC_BASE_URL

URL pública de FastAPI.

Se utiliza, por ejemplo, para generar el enlace de descarga del Excel.

En GitHub Codespaces normalmente tendrá una forma similar a:

```bash
export PUBLIC_BASE_URL="https://NOMBRE-CODESPACE-8000.app.github.dev"
```

No agregar `/` al final.

---

## Uso opcional de archivo `.env`

Se puede crear un archivo:

```text
.env
```

con:

```env
WHATSAPP_VERIFY_TOKEN=mi_token_verificacion
N8N_WEBHOOK_URL=http://127.0.0.1:5678/webhook/whatsapp-verificacion
PUBLIC_BASE_URL=https://mi-url-publica-8000.app.github.dev
```

El archivo `.env` ya está excluido mediante `.gitignore`.

IMPORTANTE: la aplicación actualmente utiliza `os.getenv()`. Por lo tanto, si se utiliza un `.env`, las variables deben cargarse en la terminal antes de iniciar FastAPI:

```bash
set -a
source .env
set +a
```

Nunca subir tokens reales al repositorio.

---

# 10. Levantar FastAPI

Con el entorno virtual activado:

```bash
python -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
```

Durante desarrollo se utiliza `--reload` para reiniciar automáticamente el servidor cuando cambia el código.

La terminal debe quedar abierta mientras se utiliza el bot.

---

# 11. Verificar FastAPI

En otra terminal ejecutar:

```bash
curl http://127.0.0.1:8000/health
```

Respuesta esperada:

```json
{
  "estado": "ok"
}
```

También se puede probar:

```bash
curl http://127.0.0.1:8000/
```

Respuesta esperada:

```json
{
  "mensaje": "El bot de gastos está funcionando"
}
```

---

# 12. Documentación automática de la API

FastAPI genera automáticamente documentación interactiva.

Con el backend iniciado:

```text
http://127.0.0.1:8000/docs
```

Desde ahí se pueden probar los endpoints sin utilizar `curl`.

---

# 13. Levantar n8n

El proyecto utiliza n8n dentro de Docker.

## Si el contenedor ya existe

Ejecutar:

```bash
docker start n8n
```

Verificar:

```bash
docker ps
```

Debería aparecer:

```text
n8n
```

con estado:

```text
Up
```

---

## Si n8n todavía no fue creado

Se puede crear mediante:

```bash
docker run -d \
  --name n8n \
  --restart unless-stopped \
  --add-host=host.docker.internal:host-gateway \
  -p 5678:5678 \
  -e TZ=America/Argentina/Tucuman \
  -e GENERIC_TIMEZONE=America/Argentina/Tucuman \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

El volumen:

```text
n8n_data
```

permite conservar workflows y credenciales aunque el contenedor se reinicie.

---

# 14. Verificar comunicación n8n → FastAPI

Ejecutar:

```bash
docker exec n8n node -e "fetch('http://host.docker.internal:8000/health').then(r=>r.text()).then(console.log).catch(console.error)"
```

Resultado esperado:

```json
{"estado":"ok"}
```

Si esto funciona, n8n puede comunicarse correctamente con FastAPI.

---

# 15. Abrir n8n

Localmente:

```text
http://127.0.0.1:5678
```

En GitHub Codespaces se debe abrir la URL pública correspondiente al puerto:

```text
5678
```

desde la pestaña:

```text
Puertos
```

de VS Code.

---

# 16. Configuración del workflow de n8n

El workflow principal se denomina:

```text
Mensajes WhatsApp
```

Su estructura es:

```text
Webhook
   │
   ▼
If
   │ true
   ▼
HTTP Request
   │
   ▼
HTTP Request2
```

La rama `false` del nodo `If` puede permanecer vacía.

Esto permite ignorar eventos de Meta que no correspondan a mensajes, por ejemplo estados:

```text
sent
delivered
read
```

---

# 17. Nodo Webhook

Configurar un webhook POST.

Path:

```text
whatsapp-verificacion
```

La Production URL debe terminar aproximadamente en:

```text
/webhook/whatsapp-verificacion
```

FastAPI enviará los eventos recibidos desde Meta hacia esta URL.

---

# 18. Nodo If

El nodo `If` debe permitir continuar solamente cuando el evento recibido contiene un mensaje de WhatsApp.

Los eventos que contienen únicamente estados de entrega deben dirigirse por la rama `false` y finalizar el flujo.

---

# 19. Primer HTTP Request

Este nodo envía el texto recibido a FastAPI.

Método:

```text
POST
```

URL:

```text
http://host.docker.internal:8000/movimientos/mensaje
```

Body Content Type:

```text
JSON
```

Campo:

```text
mensaje
```

Valor:

```text
{{ $json.body.entry[0].changes[0].value.messages[0].text.body }}
```

FastAPI devuelve un objeto que contiene principalmente:

```json
{
  "respuesta": "...",
  "intencion": "..."
}
```

---

# 20. HTTP Request2

Este nodo envía la respuesta generada por FastAPI nuevamente hacia WhatsApp.

Método:

```text
POST
```

URL:

```text
https://graph.facebook.com/v26.0/PHONE_NUMBER_ID/messages
```

Reemplazar:

```text
PHONE_NUMBER_ID
```

por el identificador del número proporcionado por Meta.

---

## Autenticación

Seleccionar:

```text
Generic Credential Type
Bearer Auth
```

Crear una credencial con el Access Token proporcionado por Meta.

En el campo se debe pegar solamente el token.

NO escribir:

```text
Bearer TOKEN
```

porque n8n agrega automáticamente el encabezado correspondiente.

---

# 21. Body de HTTP Request2

Se recomienda utilizar:

```text
Body Content Type: JSON
Specify Body: Using Fields Below
```

Agregar:

### messaging_product

```text
whatsapp
```

### to

Para números argentinos, el webhook puede entregar el número en formato `549...` mientras que Meta puede requerir `54...`.

La expresión utilizada actualmente es:

```text
{{ $('Webhook').item.json.body.entry[0].changes[0].value.messages[0].from.replace(/^549/, '54') }}
```

### type

```text
text
```

### text

Utilizar una expresión que devuelva un objeto:

```text
{{ { "body": $('HTTP Request').item.json.respuesta } }}
```

No construir este campo mediante JSON escrito manualmente, ya que las respuestas pueden contener saltos de línea y emojis.

---

# 22. Publicar el workflow

Después de realizar modificaciones en n8n se debe utilizar:

```text
Publish
```

La ejecución real proveniente de WhatsApp utiliza la versión publicada del workflow.

Una ejecución histórica conserva la configuración que tenía el workflow en ese momento.

Por lo tanto, una ejecución antigua puede mostrar una credencial o configuración anterior aunque el workflow actual haya cambiado.

---

# 23. Configuración de Meta Developers

Crear una aplicación en Meta Developers y agregar:

```text
WhatsApp
```

Configurar WhatsApp Cloud API.

Meta proporcionará principalmente:

```text
Phone Number ID
WhatsApp Business Account ID
Access Token
```

---

# 24. Hacer público FastAPI en Codespaces

Meta necesita acceder al webhook desde Internet.

En GitHub Codespaces:

```bash
gh codespace ports visibility 8000:public -c "$CODESPACE_NAME"
```

También hacer público n8n si se necesita acceder desde el navegador:

```bash
gh codespace ports visibility 5678:public -c "$CODESPACE_NAME"
```

Se puede verificar desde la pestaña:

```text
Puertos
```

de VS Code.

---

# 25. Callback URL de Meta

La URL de callback debe ser la URL pública del puerto 8000 seguida por:

```text
/whatsapp/webhook
```

Ejemplo:

```text
https://NOMBRE-CODESPACE-8000.app.github.dev/whatsapp/webhook
```

El Verify Token debe coincidir con:

```text
WHATSAPP_VERIFY_TOKEN
```

configurado en FastAPI.

---

# 26. Suscripción a mensajes

Dentro de la configuración de Webhooks de WhatsApp se debe suscribir el campo:

```text
messages
```

Sin esta suscripción, los mensajes enviados por el usuario pueden no llegar al webhook.

---

# 27. Suscribir la aplicación a la cuenta de WhatsApp

Si los mensajes reales no llegan aunque el webhook esté correctamente verificado, comprobar las aplicaciones suscriptas al WhatsApp Business Account.

Consultar:

```bash
curl -s \
  "https://graph.facebook.com/v26.0/WABA_ID/subscribed_apps" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  | python -m json.tool
```

Si la aplicación no aparece, suscribirla:

```bash
curl -s -X POST \
  "https://graph.facebook.com/v26.0/WABA_ID/subscribed_apps" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  | python -m json.tool
```

Resultado esperado:

```json
{
  "success": true
}
```

---

# 28. Verificar un Access Token de Meta

Antes de cargar un token en n8n se puede comprobar directamente mediante:

```bash
read -s -p "Access Token de Meta: " WHATSAPP_ACCESS_TOKEN
echo
export WHATSAPP_ACCESS_TOKEN
```

Luego:

```bash
curl -s \
  "https://graph.facebook.com/v26.0/PHONE_NUMBER_ID?fields=display_phone_number,verified_name" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  | python -m json.tool
```

Si el token funciona se obtendrá información similar a:

```json
{
  "display_phone_number": "...",
  "verified_name": "...",
  "id": "..."
}
```

Si aparece:

```text
OAuthException
code 190
```

el token no es válido o venció.

---

# 29. Probar el procesamiento sin WhatsApp

El backend puede probarse directamente.

## Registrar movimiento

```bash
curl -X POST \
  "http://127.0.0.1:8000/movimientos/mensaje" \
  -H "Content-Type: application/json" \
  -d '{"mensaje":"Gaste 5000 en comida"}'
```

---

## Consultar resumen

```bash
curl -X POST \
  "http://127.0.0.1:8000/movimientos/mensaje" \
  -H "Content-Type: application/json" \
  -d '{"mensaje":"Resumen"}'
```

---

## Consultar categorías

```bash
curl -X POST \
  "http://127.0.0.1:8000/movimientos/mensaje" \
  -H "Content-Type: application/json" \
  -d '{"mensaje":"Categorias"}'
```

---

## Consultar mes pasado

```bash
curl -X POST \
  "http://127.0.0.1:8000/movimientos/mensaje" \
  -H "Content-Type: application/json" \
  -d '{"mensaje":"Cuanto gaste el mes pasado"}'
```

---

# 30. Consultas temporales soportadas

Actualmente pueden reconocerse períodos como:

```text
hoy
ayer
esta semana
este mes
mes pasado
enero
febrero
marzo
abril
mayo
junio
julio
agosto
septiembre
octubre
noviembre
diciembre
```

Si una consulta no especifica período, por defecto se utiliza:

```text
este mes
```

---

# 31. Exportación a Excel

Endpoint:

```text
GET /movimientos/exportar/excel
```

Ejemplo local:

```text
http://127.0.0.1:8000/movimientos/exportar/excel
```

Exportar un mes específico:

```text
/movimientos/exportar/excel?mes=11&anio=2026
```

El archivo contiene dos hojas:

```text
Movimientos
Resumen
```

La hoja `Movimientos` incluye:

```text
ID
Tipo
Monto
Categoría
Descripción
Medio de pago
Fecha
```

La hoja `Resumen` incluye:

```text
Total de ingresos
Total de gastos
Saldo
Cantidad de movimientos
Gastos por categoría
Gráfico de gastos por categoría
```

---

# 32. Exportar Excel desde WhatsApp

Enviar:

```text
Exportar Excel
```

FastAPI genera una respuesta utilizando:

```text
PUBLIC_BASE_URL
```

y devuelve un enlace similar a:

```text
https://URL-PUBLICA/movimientos/exportar/excel
```

---

# 33. Endpoints principales

## Estado

```text
GET /health
```

## Crear movimiento

```text
POST /movimientos/
```

## Listar movimientos

```text
GET /movimientos/
```

Filtros disponibles:

```text
tipo
categoria
mes
anio
```

## Obtener movimiento

```text
GET /movimientos/{id}
```

## Eliminar movimiento

```text
DELETE /movimientos/{id}
```

## Resumen general

```text
GET /movimientos/resumen/general
```

## Resumen por categorías

```text
GET /movimientos/resumen/categorias
```

## Interpretar mensaje

```text
POST /movimientos/interpretar
```

## Procesar mensaje completo

```text
POST /movimientos/mensaje
```

## Exportar Excel

```text
GET /movimientos/exportar/excel
```

## Webhook WhatsApp

```text
GET /whatsapp/webhook
POST /whatsapp/webhook
```

---

# 34. Respuestas ante mensajes no reconocidos

Cuando el mensaje no permite determinar si corresponde a un gasto o un ingreso, el backend devuelve:

```text
No pude determinar si es un gasto o un ingreso
```

Esto se devuelve como una respuesta válida para evitar que n8n interrumpa el workflow con un error HTTP.

---

# 35. Solución de problemas

## FastAPI no responde

Error:

```text
Failed to connect to 127.0.0.1 port 8000
```

Verificar que Uvicorn esté iniciado:

```bash
python -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
```

---

## Puerto 8000 ocupado

Error:

```text
Address already in use
```

Buscar el proceso:

```bash
lsof -i :8000
```

o:

```bash
ss -ltnp | grep :8000
```

Finalizar el proceso correspondiente antes de volver a iniciar FastAPI.

---

## n8n no está iniciado

Ejecutar:

```bash
docker start n8n
```

Verificar:

```bash
docker ps
```

---

## n8n no puede acceder a FastAPI

Probar:

```bash
docker exec n8n node -e "fetch('http://host.docker.internal:8000/health').then(r=>r.text()).then(console.log).catch(console.error)"
```

Debe responder:

```json
{"estado":"ok"}
```

---

## Meta devuelve 401

Si `HTTP Request2` muestra:

```text
Authorization failed
Authentication Error
OAuthException
code 190
```

verificar el Access Token de Meta.

Se recomienda probar primero el token mediante `curl` antes de modificar otras partes del sistema.

---

## El mensaje llega a FastAPI pero no aparece en n8n

Revisar:

```text
N8N_WEBHOOK_URL
```

También comprobar la Production URL del nodo Webhook.

---

## No aparece nada en FastAPI al enviar WhatsApp

Verificar el Callback URL configurado en Meta.

En Codespaces la URL puede cambiar cuando se crea un Codespace diferente.

La URL debe apuntar al puerto público `8000`.

---

## n8n indica JSON Body inválido

No construir manualmente un JSON que contenga la respuesta de FastAPI.

Utilizar:

```text
Specify Body → Using Fields Below
```

y para `text`:

```text
{{ { "body": $('HTTP Request').item.json.respuesta } }}
```

Esto permite manejar correctamente saltos de línea y emojis.

---

## Meta indica que el destinatario no está permitido

Durante las pruebas con el número de Meta, el destinatario debe estar agregado a la lista de números autorizados.

Para números de Argentina también puede existir una diferencia entre:

```text
549...
```

recibido en el webhook y:

```text
54...
```

utilizado como destinatario.

El workflow actual normaliza este caso.

---

# 36. Consideraciones sobre GitHub Codespaces

Codespaces se utiliza actualmente como entorno de desarrollo.

Cuando el Codespace se detiene:

```text
FastAPI se detiene
n8n se detiene
Meta deja de alcanzar el webhook
el bot deja de responder
```

Al volver a abrirlo se debe iniciar nuevamente:

### FastAPI

```bash
source .venv/bin/activate

python -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
```

### n8n

```bash
docker start n8n
```

### Puertos públicos

```bash
gh codespace ports visibility 8000:public -c "$CODESPACE_NAME"

gh codespace ports visibility 5678:public -c "$CODESPACE_NAME"
```

Codespaces resulta adecuado para desarrollo y demostraciones, pero no es la infraestructura definitiva recomendada para producción.

---

# 37. Seguridad

Nunca subir al repositorio:

```text
Access Tokens de Meta
Verify Tokens privados
contraseñas
credenciales de n8n
archivos .env con secretos
```

El proyecto ya excluye:

```text
.env
.venv
gastos.db
```

mediante `.gitignore`.

---

# 38. Estado actual del proyecto

Actualmente se encuentran implementados:

```text
Registro de gastos
Registro de ingresos
Clasificación por categoría
Detección de medios de pago
Consultas de resumen
Consultas por período
Consultas por categoría
Exportación a Excel
Gráfico por categoría
Integración con WhatsApp
Integración con n8n
Persistencia con SQLite
```

Funcionalidades consideradas para etapas posteriores:

```text
Google Sheets
Alertas automáticas
Múltiples usuarios
Categorías personalizadas
Edición de movimientos desde WhatsApp
Migración a una base de datos productiva
Despliegue permanente fuera de Codespaces
```

---

# 39. Importante: workflow de n8n

El código Python se encuentra versionado en Git, pero n8n mantiene sus workflows dentro de su propio almacenamiento.

Para que otra persona pueda reconstruir el sistema exactamente, se recomienda exportar el workflow:

```text
Mensajes WhatsApp
```

desde n8n como archivo JSON y agregarlo al repositorio, por ejemplo:

```text
n8n/
└── mensajes-whatsapp.json
```

No incluir credenciales ni Access Tokens dentro del archivo exportado.

Una vez incorporado, un nuevo desarrollador podrá importar el workflow en su propia instancia de n8n y únicamente configurar sus credenciales de Meta.

---

# 40. Puesta en marcha rápida

Para un entorno ya configurado:

```bash
cd bot-gastos-whatsapp

source .venv/bin/activate

python -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
```

En otra terminal:

```bash
docker start n8n
```

Comprobar:

```bash
curl http://127.0.0.1:8000/health
```

y:

```bash
docker exec n8n node -e "fetch('http://host.docker.internal:8000/health').then(r=>r.text()).then(console.log).catch(console.error)"
```

Si ambos responden correctamente, el backend y n8n están listos para procesar mensajes.

---

# Autores

Proyecto desarrollado en el marco de la carrera **Analista Desarrollador Universitario de Sistemas de Información** de la Universidad Tecnológica Nacional — Facultad Regional Tucumán.

**Facundo Agustín Albertus**

**Mayra Magalí Brandan**

2026

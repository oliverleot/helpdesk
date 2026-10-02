# HelpDesk

Sistema web interno de gestión de tickets de soporte: empleados reportan problemas, y agentes de soporte los reciben, los asignan, les cambian estado/prioridad y los resuelven. Cada cambio relevante queda registrado en un historial.

Proyecto de portafolio enfocado en demostrar una base backend sólida con Flask: autenticación real, autorización por roles aplicada en el servidor (no solo ocultando botones), separación de responsabilidades por capas, interacciones dinámicas con HTMX, tests automatizados y CI.

## Características

- Registro, login y logout con sesiones de Flask-Login.
- Tres roles: `USER`, `AGENT`, `ADMIN`, con permisos verificados en el backend.
- Creación, consulta, cambio de estado y cambio de prioridad de tickets.
- Comentarios en tickets.
- Asignación y desasignación de tickets a agentes.
- Historial de cambios por ticket (estado, prioridad, asignación).
- Dashboard con métricas: total de tickets, por estado, urgentes, y asignados al usuario actual. Un `USER` solo ve métricas de sus propios tickets; `AGENT`/`ADMIN` ven métricas globales.
- Interacciones sin recarga de página vía HTMX (cambio de estado, prioridad, asignación y comentarios), con *fallback* funcional si JavaScript no está disponible.
- Protección CSRF en todos los formularios que modifican datos (incluidos los que usan HTMX).
- Tests automatizados con pytest (servicios y rutas) y CI con GitHub Actions.
- Dockerfile y Docker Compose para levantar la app junto con PostgreSQL.

## Stack

- Python 3.13+
- Flask
- SQLAlchemy (Flask-SQLAlchemy)
- PostgreSQL
- Flask-Migrate (Alembic)
- Flask-Login
- Flask-WTF (formularios + CSRF)
- HTMX
- Bootstrap (vía CDN)
- pytest
- GitHub Actions
- Docker / Docker Compose

## Arquitectura

```
Browser (HTML + HTMX)
        ↓
     Routes / Blueprints
        ↓
     Services
        ↓
     Models (SQLAlchemy)
        ↓
     PostgreSQL
```

Las responsabilidades están separadas en capas:

- **Routes**: reciben el request, delegan al service correspondiente y deciden qué template (o fragmento) devolver. No contienen reglas de negocio ni cálculos.
- **Services**: toda la lógica de negocio vive acá — validar permisos, decidir qué puede cambiar, registrar el historial, manejar errores de integridad. Son funciones simples, sin frameworks de por medio, fáciles de testear de forma aislada.
- **Models**: definen las tablas y relaciones con SQLAlchemy, sin lógica de negocio.

Esta separación existe para que cada capa se pueda razonar y testear por separado: los tests de servicios no necesitan un servidor HTTP corriendo, y las rutas se mantienen simples y fáciles de leer.

## Roles

| Rol | Puede |
|---|---|
| `USER` | Crear tickets, ver y comentar sus propios tickets. |
| `AGENT` | Ver todos los tickets, cambiar estado/prioridad, asignar/desasignar tickets, comentar. |
| `ADMIN` | Lo mismo que `AGENT`. |

Los permisos se validan en los services y en un decorador (`roles_required`) aplicado a las rutas — nunca dependen únicamente de que la interfaz oculte un botón.

## Instalación local

```bash
git clone <url-de-tu-repositorio>
cd helpdesk
python -m venv venv
source venv/bin/activate   # en Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Editar `.env` con tus propios valores (`SECRET_KEY`, `DATABASE_URL`).

### PostgreSQL

Necesitás un PostgreSQL corriendo y accesible con la URL que pusiste en `DATABASE_URL`. Si no querés instalarlo localmente, podés levantar solo la base con Docker:

```bash
docker compose up -d db
```

Luego aplicar las migraciones:

```bash
export FLASK_APP=run.py
flask db upgrade
```

## Ejecutar

```bash
python run.py
```

La app queda disponible en `http://127.0.0.1:5000`. `FLASK_DEBUG=true` en `.env` activa el modo debug para desarrollo local; en producción debe quedar en `false` (es el valor por defecto si no se define).

## Tests

```bash
pytest
```

Los tests usan una base SQLite en un archivo temporal propio, distinta en cada ejecución — **nunca tocan la base de PostgreSQL de desarrollo**. Esto es posible porque los modelos no usan ningún tipo ni función específica de PostgreSQL. Cubren:

- Servicios (`tests/test_services/`): autenticación, lógica de tickets, asignación, dashboard.
- Rutas (`tests/test_routes/`): auth, tickets, asignación, dashboard, y protección CSRF.

## Docker

```bash
docker compose up --build
```

Levanta la aplicación Flask y PostgreSQL juntos. La primera vez, en otra terminal, aplicar las migraciones dentro del contenedor:

```bash
docker compose exec web flask db upgrade
```

Para detener:

```bash
docker compose down
```

(`docker compose down -v` además borra el volumen de datos de Postgres).

## CI

Cada `push` y `pull request` dispara un workflow de GitHub Actions (`.github/workflows/tests.yml`) que instala las dependencias y corre `pytest`. El resultado (verde/rojo) se ve en la pestaña **Actions** del repositorio.

## Estructura del proyecto

```
helpdesk/
├── app/
│   ├── __init__.py          # application factory
│   ├── config.py            # configuracion via variables de entorno
│   ├── extensions.py        # instancias de SQLAlchemy, Login, CSRF, Migrate
│   ├── forms.py             # formularios WTForms
│   ├── models/              # User, Ticket, Comment, TicketHistory
│   ├── routes/              # blueprints: auth, tickets, dashboard
│   ├── services/            # logica de negocio
│   ├── utils/                # decoradores (roles_required)
│   └── templates/           # Jinja + partials HTMX
├── tests/
│   ├── conftest.py
│   ├── test_services/
│   └── test_routes/
├── .github/workflows/tests.yml
├── run.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Seguridad

- **Passwords**: nunca se guardan en texto plano; se hashean con Werkzeug (`generate_password_hash`/`check_password_hash`).
- **CSRF**: protección global activa (`Flask-WTF` `CSRFProtect`) en todas las rutas que modifican datos, incluyendo las que se usan desde HTMX (viajan con un token oculto en el propio formulario).
- **Permisos**: verificados en el backend (services y decorador `roles_required`), no solo ocultando elementos en el HTML.
- **Configuración por entorno**: `SECRET_KEY` y `DATABASE_URL` se leen de variables de entorno (`.env`, nunca versionado). `.env.example` documenta qué variables hacen falta, sin valores reales.
- **Debug**: `FLASK_DEBUG` es `false` por defecto; nunca queda activado a menos que se declare explícitamente.
- **Transacciones**: operaciones con riesgo real de conflicto (registro de usuario, asignación de ticket) hacen `rollback()` ante un `IntegrityError` en vez de dejar la sesión de base de datos en un estado inconsistente.

## Screenshots

_(pendiente — agregar capturas del dashboard, el detalle de un ticket y el flujo de asignación)_

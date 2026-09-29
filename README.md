# PDF Extract API

# Integrantes: Olivetti Santino, De los Rios Juan Ignacio, De la Rosa Santiago

API REST para extracción de texto desde archivos PDF, con persistencia en MongoDB y validación por checksum SHA-256.

---

## 🛠️ Stack tecnológico

| Componente | Tecnología |
|-----------|-----------|
| Lenguaje | Python 3.11 |
| Framework | FastAPI |
| Base de datos | MongoDB 7.0 |
| Driver async | Motor |
| Gestor de paquetes | UV |
| Extracción PDF | PyMuPDF (fitz) |
| Autenticación | JWT (PyJWT) |
| Contenedores | Docker + Docker Compose |

---

## 📋 Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop) instalado y corriendo
- [UV](https://docs.astral.sh/uv/getting-started/installation/) instalado (para desarrollo local)
- Git

---

## 🚀 Ejecución con Docker (recomendado)

### 1. Clonar el repositorio

```bash
git clone https://github.com/juandelosrios124/pdf_extractext
cd pdf_extractext
```

### 2. Configurar variables de entorno

```bash
# Windows
copy .env.example .env

# Linux / Mac
cp .env.example .env
```

Editá el archivo `.env` con tus valores:

```ini
# Application
APP_NAME=PDF Extract API
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# MongoDB — nombre del servicio en Docker Compose
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=pdf_extract_db

# Auth
SECRET_KEY=tu-clave-secreta-aqui

# Logging
LOG_LEVEL=INFO

# File Upload (bytes) — 50MB por defecto
MAX_UPLOAD_SIZE=52428800
```

### 3. Levantar los servicios

```bash
docker compose up --build
```

> La primera vez tarda unos minutos mientras descarga las imágenes base.

Cuando veas esto, la app está lista:

```
mongodb-1  | Waiting for connections
app-1      | INFO: Application startup complete.
app-1      | INFO: Uvicorn running on http://0.0.0.0:8000
```

### 4. Abrir la documentación interactiva

```
http://localhost:8000/api/docs
```

El mismo comando levanta `extract_service` con 5 réplicas detrás de un reverse proxy
(Caddy) en `http://localhost:8001`. Réplicas, límites de CPU/RAM y timeouts del proxy
se configuran en `.env`; ver [proxy/README.md](proxy/README.md).

---

## 💻 Ejecución local (sin Docker)

> Requiere MongoDB corriendo localmente en `mongodb://localhost:27017`

### 1. Instalar dependencias

```bash
uv sync
```

### 2. Configurar variables de entorno

```bash
copy .env.example .env
```

Cambiá `MONGODB_URL` en el `.env`:

```ini
MONGODB_URL=mongodb://localhost:27017
DEBUG=True
```

### 3. Levantar la aplicación

```bash
uvicorn app.main:app --reload
```

---

## ✅ Comprobar funcionamiento

### 1. Health check

Verificá que la app y MongoDB estén conectados:

```bash
curl http://localhost:8000/api/v1/health/
```

Respuesta esperada:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

### 2. Subir un PDF — Swagger UI (recomendado)

1. Abrí `http://localhost:8000/api/docs`
2. Expandí `POST /api/v1/pdf/upload`
3. Click en **Try it out**
4. Seleccioná un archivo PDF desde tu computadora
5. Click en **Execute**

Respuesta exitosa:

```json
{
  "id": "507f1f77bcf86cd799439011",
  "filename": "mi_documento.pdf",
  "checksum": "e3b0c44298fc1c149afbf4c8996fb924...",
  "text": "Contenido extraído del PDF..."
}
```

### 3. Subir un PDF — curl

```bash
curl -X POST http://localhost:8000/api/v1/pdf/upload \
  -F "file=@ruta/a/tu/archivo.pdf"
```

### 4. Crear un usuario y autenticarse

```bash
# Crear usuario
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@ejemplo.com", "username": "usuario", "password": "mipassword123"}'

# Login — obtener JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario", "password": "mipassword123"}'
```

---

## 🧪 Ejecutar tests

### Unit tests

No requieren MongoDB ni ningún servicio externo:

```bash
pytest tests/ -v --ignore=tests/integration/db
```

Resultado esperado: **99 passed**

### Integration tests

Requieren MongoDB corriendo:

```bash
pytest tests/integration/db/ -v
```

---

## 📁 Estructura del proyecto

```
pdf_extractext/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py           # POST /auth/login, GET /auth/me
│   │       │   ├── health.py         # GET /health
│   │       │   ├── pdf.py            # POST /pdf/upload
│   │       │   └── users.py          # CRUD /users
│   │       └── router.py
│   ├── core/
│   │   ├── config.py                 # Variables de entorno (Pydantic Settings)
│   │   ├── exceptions.py             # Excepciones de la aplicación
│   │   ├── security.py               # Lógica JWT
│   │   └── logging/                  # Logging centralizado con JSON
│   ├── db/
│   │   └── database.py               # Conexión MongoDB con Motor
│   ├── models/
│   │   ├── user.py                   # Modelo de usuario
│   │   └── role.py                   # Modelo de rol
│   ├── repositories/
│   │   ├── document_repo.py          # Acceso a datos de documentos
│   │   ├── user_repository.py        # Acceso a datos de usuarios
│   │   └── role_repository.py        # Acceso a datos de roles
│   ├── services/
│   │   ├── pdf_service.py            # Extracción de texto + checksum SHA-256
│   │   ├── auth_service.py           # Autenticación JWT
│   │   ├── health_service.py         # Estado del sistema
│   │   └── user_service.py           # Lógica de negocio de usuarios
│   ├── schemas/
│   │   ├── document.py               # Schema de respuesta PDF
│   │   ├── user.py                   # Schemas de usuario
│   │   ├── auth.py                   # Schemas de autenticación
│   │   ├── health.py                 # Schema de health check
│   │   └── role.py                   # Schema de roles
│   └── main.py                       # Entry point — factory de la aplicación
├── migrations/
│   ├── versions/                     # Migraciones versionadas
│   ├── runner.py                     # Ejecutor de migraciones
│   ├── registry.py                   # Registro de migraciones aplicadas
│   └── cli.py                        # CLI para gestión de migraciones
├── tests/
│   ├── api/v1/                       # Tests de endpoints HTTP
│   ├── services/                     # Tests de servicios
│   ├── integration/
│   │   ├── core/                     # Tests de middleware y logging
│   │   ├── db/                       # Tests de conexión MongoDB (requiere DB)
│   │   └── test_auth_login_flow.py   # Test end-to-end de autenticación
│   ├── unit/core/                    # Tests unitarios de logging
│   └── conftest.py                   # Fixtures compartidos
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── pyproject.toml
```

---

## 🔌 Endpoints disponibles

### PDF

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/pdf/upload` | Sube un PDF, extrae texto y persiste con checksum |

### Health

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/v1/health/` | Estado general del sistema y MongoDB |
| `GET` | `/api/v1/health/ready` | Readiness probe |
| `GET` | `/api/v1/health/live` | Liveness probe |

### Auth

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/auth/login` | Login con credenciales → JWT token |
| `GET` | `/api/v1/auth/me` | Datos del usuario autenticado |

### Usuarios

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/users/` | Crear usuario |
| `GET` | `/api/v1/users/` | Listar usuarios |
| `GET` | `/api/v1/users/{id}` | Obtener usuario por ID |
| `PUT` | `/api/v1/users/{id}` | Actualizar usuario |
| `DELETE` | `/api/v1/users/{id}` | Eliminar usuario |

---

## ⚙️ Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `APP_NAME` | Nombre de la aplicación | `PDF Extract API` |
| `APP_VERSION` | Versión | `1.0.0` |
| `DEBUG` | Habilita Swagger UI en `/api/docs` | `False` |
| `ENVIRONMENT` | Entorno (`development`, `production`) | `development` |
| `MONGODB_URL` | URL de conexión MongoDB | `mongodb://localhost:27017` |
| `MONGODB_DB_NAME` | Nombre de la base de datos | `pdf_extract_db` |
| `SECRET_KEY` | Clave para firmar tokens JWT | — |
| `LOG_LEVEL` | Nivel de logging (`DEBUG`, `INFO`, `ERROR`) | `INFO` |
| `MAX_UPLOAD_SIZE` | Tamaño máximo de PDF en bytes | `52428800` (50MB) |

---

## 🐳 Comandos Docker útiles

```bash
# Levantar en segundo plano
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Ver logs solo de la app
docker compose logs -f app

# Detener los servicios
docker compose down

# Detener y eliminar datos de MongoDB
docker compose down -v

# Reconstruir la imagen tras cambios en el código
docker compose up --build
```

---

## 🧱 Principios aplicados

- **TDD** — cada feature fue implementada con ciclo Red → Green → Refactor
- **12-Factor App** — configuración por variables de entorno, logs como streams, port binding, stateless
- **Clean Architecture** — separación estricta en capas: api / services / repositories
- **SOLID** — responsabilidad única, inversión de dependencias, inyección via `Depends()`
- **KISS / DRY / YAGNI** — sin abstracciones innecesarias, sin código duplicado
- **SHA-256 checksum** — integridad del archivo y detección de duplicados
- **JWT Auth** — autenticación stateless con tokens firmados

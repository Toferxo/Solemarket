# SoleMarket v1.0

Marketplace de zapatillas para Chile — 100% gratis, sin comisiones.

## Stack
- **Backend:** Python + Django 4.2
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend:** Django Templates + Bootstrap 5 + JS vanilla
- **Almacenamiento:** Sistema de archivos local / S3 (producción)

## Instalación local

### 1. Clonar y entrar al proyecto
```bash
git clone <tu-repo>
cd solemarket
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Migraciones
```bash
python manage.py migrate
```

### 5. Cargar datos de ejemplo (opcional)
```bash
python manage.py shell < seed_data.py
```

### 6. Crear superusuario (admin)
```bash
python manage.py createsuperuser
```

### 7. Correr el servidor
```bash
python manage.py runserver
```

Abre http://localhost:8000

## Estructura del proyecto
```
solemarket/
├── listings/           # App principal: publicaciones y perfiles
│   ├── models.py       # Listing, ListingImage, SellerProfile, Review
│   ├── views.py        # Index, detalle, crear, editar, perfil vendedor
│   ├── forms.py        # Formularios de publicación y registro
│   └── urls.py
├── messaging/          # App de mensajería interna
│   ├── models.py       # Conversation, Message
│   ├── views.py        # Inbox, send, poll (long polling)
│   └── urls.py
├── templates/          # HTML templates
├── static/             # CSS, JS
└── media/              # Imágenes subidas por usuarios
```

## Deploy a producción (Render / Railway)

### Variables de entorno necesarias
```
SECRET_KEY=<clave-segura>
DEBUG=False
DATABASE_URL=<postgresql-url>
ALLOWED_HOSTS=tu-dominio.com
```

### Pasos para Render.com (gratis)
1. Crear cuenta en render.com
2. New → Web Service → conectar GitHub
3. Build command: `pip install -r requirements.txt && python manage.py migrate`
4. Start command: `gunicorn solemarket.wsgi`
5. Agregar PostgreSQL desde el dashboard

## Roadmap v2.0
- [ ] Autenticación por número de teléfono (OTP)
- [ ] WebSockets para mensajería en tiempo real
- [ ] Búsqueda por geolocalización
- [ ] Pagos y comisión (Transbank / Khipu)
- [ ] App móvil (React Native)

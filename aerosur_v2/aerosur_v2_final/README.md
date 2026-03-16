# ✈ AeroSur — Sistema de Gestión de Vuelos

Sistema web desarrollado con **Python + Streamlit + Supabase**.

---

## 🚀 Instalación rápida

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Supabase
Abre el archivo `utils/supabase_client.py` y reemplaza:
```python
SUPABASE_URL = "https://TU-PROYECTO.supabase.co"
SUPABASE_KEY = "TU-ANON-KEY"
```
Estos datos los encuentras en tu proyecto de Supabase:
- **Settings → API → Project URL**
- **Settings → API → anon / public key**

### 3. Ejecutar la app
```bash
streamlit run app.py
```

Se abrirá en tu navegador en: `http://localhost:8501`

---

## 👤 Usuarios de prueba

| Correo                     | Contraseña | Rol           |
|---------------------------|------------|---------------|
| admin@aerosur.com          | 123456     | Administrador |
| operador@aerosur.com       | 123456     | Operador      |
| supervisor@aerosur.com     | 123456     | Supervisor    |

---

## 📁 Estructura del proyecto

```
aerosur/
├── app.py                    ← Punto de entrada principal
├── requirements.txt
├── utils/
│   ├── supabase_client.py    ← Conexión a Supabase (configura aquí)
│   └── auth.py               ← Login y log de accesos
└── pages/
    ├── login.py              ← Pantalla de inicio de sesión
    ├── dashboard.py          ← Vista general con KPIs
    ├── vuelos.py             ← CRUD de vuelos
    ├── pasajeros.py          ← CRUD de pasajeros
    ├── reservas.py           ← Gestión de reservas y asientos
    ├── tripulacion.py        ← Tripulantes y asignación a vuelos
    ├── aviones.py            ← Flota y configuración de asientos
    ├── empleados.py          ← Empleados y usuarios del sistema
    └── logs.py               ← Log de accesos al sistema
```

---

## 📌 Notas importantes

- Las contraseñas en esta versión se guardan en texto plano (igual que en tu BD).
  Para producción, se recomienda usar hashing (bcrypt).
- El sistema registra automáticamente cada intento de login en `tblogacceso`.
- Para crear asientos en un vuelo, debes poblar la tabla `tbAsiento` con los asientos
  del tipo de avión asignado al vuelo. Puedes hacerlo con un trigger en Supabase o
  manualmente.

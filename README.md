# Taller Evaluativo – Informática 1 (Unidades 3 y 4)

**Universidad de Antioquia – Facultad de Ingeniería**
Gestión de información en computación y manejo de bases de datos.

Sistema en Python para generar, ordenar, validar, almacenar y consultar registros de signos vitales
(archivos TXT/CSV/JSON y base de datos NoSQL en MongoDB Atlas).

## Estructura del proyecto

```
taller_informatica1/
├── main.py          # Menú principal (integración)
├── generador.py     # Registros aleatorios + ordenamiento (Merge Sort)
├── validacion.py    # Validación con expresiones regulares
├── archivos.py      # Lectura/escritura TXT, CSV y JSON con excepciones
├── sistema.py       # Carpetas, mover archivos (pathlib/os) y log.txt
├── mongo_db.py      # Conexión y consultas a MongoDB Atlas
├── requirements.txt
├── .env.example     # Plantilla para la cadena de conexión
├── log.txt          # Registro de acciones
└── data/
    ├── txt/
    ├── csv/
    └── json/
```

## Formato de los registros

| Campo  | Descripción                | Formato     | Regex                |
|--------|----------------------------|-------------|----------------------|
| `id`   | Identificación             | `ID-001`    | `^ID-\d{3}$`         |
| `fr`   | Edad (según el enunciado)  | `18 Años`   | `^\d{1,3} Años$`     |
| `fc`   | Frecuencia cardiaca        | `090ppm`    | `^\d{3}ppm$`         |
| `spo2` | Saturación periférica O₂   | `95%`       | `^(100\|\d{2})%$`    |

> Se respeta el nombre `fr` para la edad tal como aparece en el enunciado del taller.

## Instalación y ejecución

```bash
git clone <URL-DEL-REPOSITORIO>
cd taller_informatica1
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configurar MongoDB Atlas

1. Crear un cluster gratuito en [MongoDB Atlas](https://www.mongodb.com/atlas).
2. En *Database Access* crear un usuario; en *Network Access* permitir tu IP.
3. En *Connect → Drivers* copiar la cadena de conexión.
4. Copiar `.env.example` a `.env` y pegar la cadena en `MONGO_URI`
   (el archivo `.env` está en `.gitignore`, no se sube al repositorio).

```bash
python main.py
```

## Menú

| Opción | Acción |
|--------|--------|
| 1 | Generar ≥ 50 registros aleatorios y ordenarlos por frecuencia cardiaca |
| 2 | Ingresar un registro manualmente (validado con regex) |
| 3 | Ver registros en memoria |
| 4 | Validar datos |
| 5 | Guardar en TXT y CSV |
| 6 | Exportar a JSON |
| 7 | Importar desde JSON o CSV (se validan al cargar) |
| 8 | Organizar archivos en `data/` |
| 9 | Conectar a MongoDB e insertar registros validados (colección `signos_vitales`) |
| 10 | Consultas: promedio de FC y documentos con SpO₂ < 94 → `resultados_mongo.json` |
| 11 | Consultar un registro por ID en MongoDB |

## Ítems del taller y dónde se cumplen

1. **Procesamiento y ordenamiento** – `generador.py` (Merge Sort implementado a mano, por FC).
2. **Archivos TXT/CSV/JSON** – `archivos.py`, con `try/except` y verificación de rutas.
3. **Herramientas del sistema** – `sistema.py`: crea `data/txt|csv|json`, mueve archivos y escribe `log.txt`.
4. **Expresiones regulares** – `validacion.py`, usada al ingresar, importar e insertar datos.
5. **MongoDB** – `mongo_db.py`: colección `signos_vitales`, promedio de FC (`$avg`) y `spo2 < 94`.
   Cada documento guarda además `fc_valor`, `spo2_valor` y `edad_valor` (numéricos) para poder consultar.
   Se usa *upsert* por `id`, así que re-insertar no duplica documentos.
6. **Integración** – `main.py`.
7. **GitHub** – repositorio público, este README y más de 5 commits.

## Datos de ejemplo

En `data/` se incluyen archivos de ejemplo generados por el programa.
`resultados_mongo.json` se crea al ejecutar la opción 10 con una conexión real a Atlas.

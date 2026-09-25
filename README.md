# HelpDesk

Sistema web interno para gestion de tickets de soporte. Proyecto en desarrollo, en esta etapa solo esta lista la base del proyecto Flask.

## Requisitos

- Python 3.13

## Como ejecutar localmente

1. Crear un entorno virtual e instalar las dependencias:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Copiar el archivo de variables de entorno:

```bash
cp .env.example .env
```

3. Ejecutar la aplicacion:

```bash
python run.py
```

4. Probar que responde:

```bash
curl http://127.0.0.1:5000/health
```

Deberia devolver:

```json
{"status": "ok"}
```

## Estado actual

Por ahora el proyecto solo tiene la estructura base de Flask, sin base de datos ni funcionalidades de tickets todavia. Se ira actualizando este README a medida que se agreguen nuevas partes.

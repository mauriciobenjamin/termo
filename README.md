# Thermal Fusion Studio 🏗️🔥

Este repositorio contiene una herramienta interactiva basada en Marimo para el procesamiento y fusión de termografías con imágenes de luz visible. El sistema permite extraer datos de temperatura reales a partir de mapas de bits (BMP/PNG) y alinearlos geométricamente para generar reportes visuales precisos.

## 🛠️ Stack Tecnológico

- Runtime/Gestor: uv (Recomendado para un entorno reproducible).
- Core: marimo (Cuadernos reactivos de Python).
- Visión Computacional: OpenCV (opencv-python).
- Procesamiento de Datos: NumPy, SciPy (KDTree para mapeo de color rápido).
- Visualización: Matplotlib, Pillow.

## 🚀 Instalación y Ejecución

Asegúrate de tener uv instalado.

Clonar el repositorio:

git clone <repo-url>
cd thermal-fusion-studio


Ejecutar con uv:

uv run marimo run thermal_marimo_app.py


🧠 Guía para Colaboradores (IA y Humanos)

Lógica de Procesamiento

Mapeo de Datos: No usamos los colores del BMP directamente para la fusión. El script extrae la barra de color (LUT) lateral, construye un KDTree con los perfiles RGB y mapea cada píxel de la imagen a un valor normalizado (0-1) que luego se escala a la temperatura real (°C).

Registro Geométrico: Se utiliza una Matriz de Homografía generada a partir de 4 puntos de control (Source: Térmica, Destination: Visible). Esto corrige errores de paralaje entre cámaras.

Normalización Global: Para evitar saltos de color en mosaicos de un mismo edificio, el sistema permite definir un r_min y r_max maestro.

Estructura del Código

extract_thermal_data_fast: Core de conversión Color -> Temp.

get_aligned_blend: Lógica de OpenCV para transformación de perspectiva y blending.

app: Interfaz reactiva de Marimo.

📋 Roadmap

[ ] Implementación de OCR (Tesseract) para lectura automática de escalas térmicas.

[ ] Soporte para ortomosaicos térmicos (unión de múltiples tomas).

[ ] Exportación a formato TIFF radiométrico (32-bit float).

# Product Requirements Document (PRD) - Thermal Fusion Tool

## 1. Visión General

Una herramienta web/interactiva que permita a técnicos e ingenieros fusionar imágenes térmicas de baja resolución con fotografías de luz visible de alta resolución, corrigiendo distorsiones de perspectiva y normalizando datos térmicos extraídos de archivos no radiométricos (BMP/PNG).

## 2. Problemas a Resolver

- *Pérdida de Radiometría*: Las cámaras térmicas a menudo entregan BMPs donde la temperatura es solo un color. Necesitamos recuperar el valor numérico.
- *Error de Paralaje*: Las cámaras térmicas y visibles están en posiciones distintas, lo que impide una superposición directa perfecta.
- *Inconsistencia Visual*: Diferentes fotos tienen diferentes escalas térmicas, lo que impide comparar visualmente dos partes de un mismo edificio.

## 3. Características Implementadas (v0.1.0)

| Característica | Descripción |
|----------------|-------------|
| Conversión KDTree | Mapeo ultra rápido de RGB a Temperatura usando búsqueda de vecinos cercanos. |
| Alineación por Homografía | Selección manual de 4 puntos para deformar y ajustar la perspectiva. |
| Blending Dinámico | Control de opacidad y selección de Mapas de Color (Inferno, Jet, etc.). |
| Exportación | Descarga de la imagen final procesada en alta resolución. |
| Entorno Marimo | Interfaz reactiva que elimina la necesidad de re-ejecutar scripts manualmente. |

## 4. Requisitos Funcionales

- *RF-01*: El usuario debe poder ingresar manualmente los límites de temperatura de la foto original.
- *RF-02*: El sistema debe normalizar la visualización basándose en un rango maestro global.
- *RF-03*: La herramienta debe funcionar localmente con latencia mínima (logrado mediante uv y marimo).

## 5. Requisitos No Funcionales

- *R-NF-01*: El código debe ser modular para permitir la futura integración de procesos por lotes (batch processing).

## 6. Flujo de trabajo esperado

1. El usuario selecciona el modo de trabajo, imagen sencilla, para un solo par de imagen termográdica (IT) e imagen de luz visible (ILV), o imagen mosaico, en que se formara una imagen mayor con otras imagen más pequeñas.
2. El usuario sube una o mas imágenes termográficas (PNG o BMP) y una o más imágenes de luz visible (JPG o TIFF)
3. El usuario asigna los puntos de ancla que viculan  a las dos imagenes
4. El usuario designa la temperatura maxima y 

## 6. Próximos Pasos (Backlog)

1. Automatización de Escala: Integrar OCR para leer automáticamente los valores t_min y t_max de la imagen.
2. Registro Automático: Implementar detección de características (SIFT/ORB) para intentar alineación automática antes de requerir intervención humana.
3. Gestión de Proyectos: Guardar configuraciones de puntos de control en archivos JSON para repetir procesos rápidamente.

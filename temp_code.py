import marimo as mo
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from PIL import Image
import io

# --- LÓGICA DE PROCESAMIENTO ---


def extract_thermal_data_fast(img_rgb, temp_min, temp_max):
    h, w, _ = img_rgb.shape
    # Localizar barra lateral (último 10%)
    scale_bar_x_start = int(w * 0.90)
    scale_bar = img_rgb[:, scale_bar_x_start:, :]

    lut_profile = np.mean(scale_bar, axis=1)
    tree = KDTree(lut_profile)

    data_area = img_rgb[:, :scale_bar_x_start, :]
    rows, cols, _ = data_area.shape
    flat_data = data_area.reshape(-1, 3)

    _, indices = tree.query(flat_data)
    norm_values = 1.0 - (indices / len(lut_profile))
    temp_matrix = temp_min + \
        (norm_values.reshape(rows, cols) * (temp_max - temp_min))

    return temp_matrix, data_area


def get_aligned_blend(visible_img, thermal_data_matrix, src_pts, dst_pts, alpha, cmap_name, t_range):
    if len(src_pts) < 4 or len(dst_pts) < 4:
        return None

    # Coordenadas de los puntos
    src = np.array([[p['x'], p['y']] for p in src_pts[:4]], dtype=np.float32)
    dst = np.array([[p['x'], p['y']] for p in dst_pts[:4]], dtype=np.float32)

    # Calcular Homografía
    h_matrix, _ = cv2.findHomography(src, dst)

    # Deformar matriz de datos térmicos
    h_vis, w_vis = visible_img.shape[:2]
    aligned_thermal_data = cv2.warpPerspective(
        thermal_data_matrix, h_matrix, (w_vis, h_vis))

    # Normalización para visualización (usando el rango maestro)
    t_min, t_max = t_range
    t_norm = np.clip((aligned_thermal_data - t_min) / (t_max - t_min), 0, 1)

    cmap = plt.get_cmap(cmap_name)
    thermal_colored = (cmap(t_norm)[:, :, :3] * 255).astype(np.uint8)

    # Blend con la imagen visible
    blended = cv2.addWeighted(visible_img, 1-alpha, thermal_colored, alpha, 0)
    return blended

# --- INTERFAZ MARIMO ---


app = mo.App(title="Fusionador Térmico Profesional")


@app.cell
def intro():
    mo.md(
        """
        # 🏗️ Fusionador de Termografías
        Sube tus imágenes, extrae datos térmicos puros y alinea con luz visible.
        """
    )
    return


@app.cell
def file_uploaders():
    mo.md("### 1. Cargar Archivos")
    upload_vis = mo.ui.file(
        label="Sube Imagen Visible (TIFF/JPG)", kind="image")
    upload_therm = mo.ui.file(label="Sube Termografía (BMP/PNG)", kind="image")
    return upload_vis, upload_therm


@app.cell
def load_images(upload_vis, upload_therm):
    vis_img = None
    therm_img_raw = None

    if upload_vis.value:
        vis_img = cv2.cvtColor(cv2.imdecode(np.frombuffer(
            upload_vis.value[0].contents, np.uint8), 1), cv2.COLOR_BGR2RGB)

    if upload_therm.value:
        therm_img_raw = cv2.cvtColor(cv2.imdecode(np.frombuffer(
            upload_therm.value[0].contents, np.uint8), 1), cv2.COLOR_BGR2RGB)

    return vis_img, therm_img_raw


@app.cell
def thermal_params(therm_img_raw):
    mo.md("### 2. Parámetros de la Escala Térmica")
    mo.md("Define el rango que aparece en la barra lateral de la foto original.")

    c1, c2 = mo.columns(2)
    with c1:
        t_min = mo.ui.number(start=-50, stop=500, value=28.5,
                             label="Temp Mín Foto (°C)")
    with c2:
        t_max = mo.ui.number(start=-50, stop=500, value=60.0,
                             label="Temp Máx Foto (°C)")

    if therm_img_raw is None:
        return t_min, t_max, None

    temp_data_matrix, _ = extract_thermal_data_fast(
        therm_img_raw, t_min.value, t_max.value)
    return t_min, t_max, temp_data_matrix


@app.cell
def alignment_ui(vis_img, therm_img_raw):
    if vis_img is None or therm_img_raw is None:
        return None, None

    mo.md("### 3. Alineación por Puntos de Control")
    mo.md("Haz clic en **4 puntos** (esquinas, marcos, etc.) en ambas imágenes en el mismo orden.")

    col1, col2 = mo.columns(2)
    src_selector = mo.ui.image(therm_img_raw, label="Térmica (Origen)")
    dst_selector = mo.ui.image(vis_img, label="Visible (Destino)")

    with col1:
        mo.output.append(src_selector)
    with col2:
        mo.output.append(dst_selector)

    return src_selector, dst_selector


@app.cell
def rendering_controls():
    mo.md("### 4. Estética y Visualización")
    c1, c2, c3 = mo.columns(3)
    with c1:
        alpha = mo.ui.slider(start=0, stop=1, step=0.05,
                             value=0.5, label="Opacidad Térmica")
    with c2:
        cmap = mo.ui.dropdown(options=[
                              'inferno', 'magma', 'jet', 'plasma', 'viridis'], value='inferno', label="Mapa de Color")
    with c3:
        mo.md("**Rango Maestro del Reporte**")
        r_min = mo.ui.number(value=20.0, label="Min Global")
        r_max = mo.ui.number(value=70.0, label="Max Global")
    return alpha, cmap, r_min, r_max


@app.cell
def result_view(vis_img, temp_data_matrix, src_selector, dst_selector, alpha, cmap, r_min, r_max):
    if src_selector is None or dst_selector is None or len(src_selector.value) < 4:
        return mo.md("💡 *Esperando selección de puntos para procesar...*")

    final_img = get_aligned_blend(
        vis_img,
        temp_data_matrix,
        src_selector.value,
        dst_selector.value,
        alpha.value,
        cmap.value,
        (r_min.value, r_max.value)
    )

    if final_img is None:
        return mo.md("❌ Error en la matriz de homografía.")

    # Convertir a bytes para descarga
    pil_img = Image.fromarray(final_img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")

    download_btn = mo.ui.download(
        data=buffer.getvalue(),
        filename="termografia_fusionada.png",
        label="Descargar Imagen Fusionada",
        mimetype="image/png"
    )

    return mo.vstack([
        mo.md("### Resultado Final"),
        mo.image(final_img),
        mo.center(download_btn)
    ])


if __name__ == "__main__":
    app.run()

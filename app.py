from flask import Flask, request, render_template
import time
import os
import urllib
import re  # Importa el módulo 're' aquí

os.environ["LOCAL_MODE"] = "1"

# Solo importa Selenium si se usa localmente
if os.getenv("LOCAL_MODE") == "1":
    import undetected_chromedriver as uc
    from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('formulario.html')

@app.route('/direccion-a-coordenadas', methods=['POST'])
def direccion_a_coordenadas():
    direcciones = request.form.get('direcciones', '').split('\n')
    direcciones = [d.strip() for d in direcciones if d.strip()]
    resultados = []

    if os.getenv("LOCAL_MODE") == "1":
        opciones = Options()
        opciones.headless = True
        opciones.add_argument("--no-sandbox")
        opciones.add_argument("--disable-gpu")
        opciones.add_argument("--disable-dev-shm-usage")
        opciones.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        driver = uc.Chrome(options=opciones)
    else:
        driver = None

    for direccion in direcciones:
        try:
            if driver:
                print(f"📍 Buscando en Google Maps: {direccion}", flush=True)
                direccion_encoded = urllib.parse.quote(direccion)
                driver.get(f"https://www.google.com/maps/place/{direccion_encoded}")
                time.sleep(4)  # Esperar para asegurar que la página se carga correctamente

                # Capturar la URL actual
                url = driver.current_url
                print(f"🌍 URL capturada: {url}", flush=True)

                # Extraer lat y lon del segundo bloque !3d...!4d...
                match = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', url)
                if match:
                    lat, lon = match.groups()
                else:
                    lat, lon = '', ''  # Por si no se encuentra

                resultados.append({
                    "direccion": direccion,
                    "url": url,
                    "lat": lat,
                    "lon": lon
                })
            else:
                resultados.append({"direccion": direccion, "url": "Error: Selenium no está activo", "lat": "N/A", "lon": "N/A"})
        except Exception as e:
            resultados.append({"direccion": direccion, "url": f"Error: {str(e)}", "lat": "N/A", "lon": "N/A"})

        time.sleep(1)

    if driver:
        driver.quit()

    return render_template('resultado.html', resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, request, render_template, jsonify
import time
import urllib
import re
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

    opciones = Options()
    opciones.headless = True
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    driver = uc.Chrome(options=opciones)

    for direccion in direcciones:
        try:
            direccion_encoded = urllib.parse.quote(direccion)
            driver.get(f"https://www.google.com/maps/place/{direccion_encoded}")
            time.sleep(4)

            url = driver.current_url
            match = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', url)
            if match:
                lat, lon = match.groups()
            else:
                lat, lon = '', ''  # Si no se encuentra la coordenada

            resultados.append({
                "direccion": direccion,
                "url": url,
                "lat": lat,
                "lon": lon
            })
        except Exception as e:
            resultados.append({
                "direccion": direccion,
                "url": f"Error: {str(e)}",
                "lat": '',
                "lon": ''
            })

        time.sleep(1)

    driver.quit()

    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


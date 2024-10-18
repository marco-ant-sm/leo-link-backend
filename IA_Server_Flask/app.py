#Librerias para detector imagenes:
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1' #Aseguramos que tensorflow no intente usar la gpu
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

#Librerias para predictor:
from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd


from flask_cors import CORS


app = Flask(__name__)

# Habilitar CORS en todas las rutas
CORS(app)

# Cargamos el modelo de imagenes
modelo_imagenes = load_model('detectorDesnudos.keras')


# Cargar el modelo predictor y el codificador
modelo_predictor = joblib.load('modelo_asistencia.pkl')
encoder_cargado = joblib.load('encoder_asistencia.pkl')


@app.route('/')
def home():
    return render_template('index.html', mensaje="¡Hola desde Flask!")



# Crear una ruta para predecir la asistencia
@app.route('/predecir', methods=['POST'])
def predecir_asistencia():
    # Obtener los datos del evento desde la solicitud POST
    datos = request.get_json()

    # Crear un DataFrame con los datos del evento
    nuevo_evento = pd.DataFrame({
        'categoria': [datos['categoria']],
        'mes': [datos['mes']],
        'dia': [datos['dia']],
        'quienLoRealiza': [datos['quienLoRealiza']],
        'hora': [datos['hora']]
    })

   # Codificar las características categóricas usando el codificador cargado
    nuevo_evento_encoded = encoder_cargado.transform(nuevo_evento[['categoria', 'mes', 'dia', 'quienLoRealiza']])
    # Obtener los nombres de las características codificadas
    feature_names_encoded = encoder_cargado.get_feature_names_out(['categoria', 'mes', 'dia', 'quienLoRealiza'])
    # Crear un DataFrame a partir del arreglo codificado
    nuevo_evento_df = pd.DataFrame(nuevo_evento_encoded, columns=feature_names_encoded)
    # Añadir la columna 'hora' al DataFrame
    nuevo_evento_df['hora'] = nuevo_evento['hora'].values


    # Hacer la predicción con el modelo cargado
    prediccion = modelo_predictor.predict(nuevo_evento_df)

    # Retornar la predicción como un número entero
    return jsonify({'prediccion': int(prediccion[0])})




def preprocess_image_from_array(img_array, target_size):
    # Convertir el array plano a un array con las dimensiones correctas
    img_array = np.array(img_array).reshape((target_size[0], target_size[1], 4))  # 4 canales si incluye el canal alpha
    img_array = img_array[:, :, :3]  # Eliminar el canal alpha si existe, dejando solo RGB

    # Expandir dimensiones para el batch size
    img_array = np.expand_dims(img_array, axis=0)

    return img_array


@app.route('/api', methods=['POST'])
def analyze_image():
    data = request.json

    if 'imageArray' not in data:
        return jsonify({'error': 'No image data provided'}), 400

    # Obtener el array de la imagen desde la solicitud
    img_array = data['imageArray']

    # Preprocesar el array para ajustarlo al modelo
    preprocessed_image = preprocess_image_from_array(img_array, (224, 224))

    # Hacer la predicción
    prediction = modelo_imagenes.predict(preprocessed_image)

    # Interpretar el resultado
    if prediction[0] > 0.55:
        result = "No Desnudos."
    else:
        result = "Desnudos."

    return jsonify({'result': result})





if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

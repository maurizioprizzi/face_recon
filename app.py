import os
import cv2
import numpy as np
from flask import Flask, render_template, Response, request, jsonify
import base64
import threading
from queue import Queue

app = Flask(__name__)

# Initialize the camera
cam = cv2.VideoCapture(0)

# Initialize the LBPHFaceRecognizer with adjusted parameters
recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=8, grid_x=8, grid_y=8)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load the trained model (if it exists)
modelo_path = 'modelo.yml'
if os.path.exists(modelo_path):
    recognizer.read(modelo_path)

# Function to release the camera when the app is closed
def liberar_camera():
    if cam.isOpened():
        cam.release()

@app.route('/')
def index():
    """Renders the initial page."""
    return render_template('index.html')

# Queue for storing recognized student names
recognized_names = Queue(maxsize=1)

def gen_frames():
    """Generates video frames with real-time recognition."""
    while True:
        success, frame = cam.read()
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                roi_gray = gray[y:y + h, x:x + w]
                id_aluno, confianca = recognizer.predict(roi_gray)

                if confianca <= 80:  # Confidence threshold
                    alunos = os.listdir('imagens')
                    nome_aluno = alunos[id_aluno]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, nome_aluno, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    recognized_names.put(nome_aluno)  # Add recognized name to the queue

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video feed for displaying the camera."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_recognized_name')
def get_recognized_name():
    """Returns the most recently recognized student name (if any)."""
    if not recognized_names.empty():
        return jsonify({"status": "sucesso", "aluno": recognized_names.get()})
    else:
        return jsonify({"status": "erro", "mensagem": "Nenhum aluno reconhecido."})

@app.route('/salvar_foto', methods=['POST'])
def salvar_foto():
    """Saves the submitted photo and performs training if necessary."""
    data = request.get_json()
    nome = data['nome'].strip()

    # Validate student name
    if not nome or not nome.isalnum():
        return jsonify({"status": "erro", "mensagem": "Nome do aluno inválido!"})

    # Decode the base64 image
    try:
        imagem_base64 = data['imagem'].split(',')[1]
        img_data = base64.b64decode(imagem_base64)
        np_img = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": f"Erro ao processar imagem: {str(e)}"})

    # Detect face
    faces_detectadas, erro = detectar_rosto(img)
    if erro:
        return jsonify({"status": "erro", "mensagem": erro})

    # Save the image and train if necessary
    status, mensagem = salvar_imagem_e_treinar(faces_detectadas, nome, img) # Pass img as parameter
    return jsonify({"status": status, "mensagem": mensagem})

def detectar_rosto(img):
    """Converts image to grayscale and detects faces."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return None, "Nenhum rosto detectado!"
    return faces, None

def salvar_imagem_e_treinar(faces, nome, img): # Add img as parameter
    """Saves the image and trains the model if 10 images are captured."""
    aluno_dir = os.path.join("imagens", nome)
    if not os.path.exists(aluno_dir):
        os.makedirs(aluno_dir)

    img_count = len([f for f in os.listdir(aluno_dir) if os.path.isfile(os.path.join(aluno_dir, f))])
    img_name = os.path.join(aluno_dir, f"{nome}_{img_count}.jpg")

    # Assuming the face is in position (x, y, w, h)
    for (x, y, w, h) in faces:
        face = cv2.resize(cv2.cvtColor(img[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY), (200, 200))
        cv2.imwrite(img_name, face)

    if img_count + 1 == 10:
        threading.Thread(target=treinar_modelo).start()  # Train the model in the background
        return "sucesso", "Imagem salva com sucesso e modelo em treinamento!"
    return "sucesso", "Imagem salva com sucesso!"

def treinar_modelo():
    """Trains the LBPH model with the saved images."""
    faces = []
    ids = []
    alunos = os.listdir('imagens')

    for aluno in alunos:
        aluno_path = os.path.join('imagens', aluno)
        if os.path.isdir(aluno_path):
            for img_name in os.listdir(aluno_path):
                img_path = os.path.join(aluno_path, img_name)
                # Load the image here
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                id_aluno = alunos.index(aluno)
                faces.append(img)
                ids.append(id_aluno)

    if len(faces) > 0:
        recognizer.train(faces, np.array(ids))
        recognizer.write(modelo_path)
        print("Modelo treinado com sucesso!")
    else:
        print("Nenhuma face foi encontrada para treinamento.")

@app.route('/reconhecer_foto', methods=['POST'])
def reconhecer_foto():
    """Recognizes the student in the submitted image."""
    if not os.path.exists(modelo_path):
        return jsonify({"status": "erro", "mensagem": "O modelo não foi treinado ainda."})

    data = request.get_json()
    try:
        imagem_base64 = data['imagem'].split(',')[1]
        img_data = base64.b64decode(imagem_base64)
        np_img = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": f"Erro ao processar imagem: {str(e)}"})

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces_detectadas, erro = detectar_rosto(img)
    if erro:
        return jsonify({"status": "erro", "mensagem": erro})

    for (x, y, w, h) in faces_detectadas:
        roi_gray = gray[y:y + h, x:x + w]
        id_aluno, confianca = recognizer.predict(roi_gray)

        alunos = os.listdir('imagens')
        nome_aluno = alunos[id_aluno]
        return jsonify({"status": "sucesso", "aluno": nome_aluno, "confianca": round(100 - confianca)})

    return jsonify({"status": "erro", "mensagem": "Não foi possível reconhecer o aluno."})

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        liberar_camera()  # Release the camera when the application ends
import os
import cv2
import numpy as np
from flask import Flask, render_template, Response, request, jsonify
import base64

app = Flask(__name__)

# Inicializar a câmera
cam = cv2.VideoCapture(0)

# Ajustar parâmetros do LBPH
recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=8, grid_x=8, grid_y=8)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Carregar o modelo treinado (se já existir)
if os.path.exists('modelo.yml'):
    recognizer.read('modelo.yml')

# Função para capturar os frames da câmera
def gen_frames():
    while True:
        success, frame = cam.read()
        if not success:
            break
        else:
            # Converter para byte frame para envio ao frontend
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Função para salvar a imagem enviada e treinar o modelo
@app.route('/salvar_foto', methods=['POST'])
def salvar_foto():
    data = request.get_json()
    nome = data['nome'].strip()  # Garantir que não há espaços extras

    # Verificar se o nome do aluno foi fornecido corretamente
    if not nome:
        return jsonify({"status": "erro", "mensagem": "Nome do aluno inválido!"})

    imagem_base64 = data['imagem'].split(',')[1]

    # Decodificar a imagem
    img_data = base64.b64decode(imagem_base64)
    np_img = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # Detectar o rosto e pré-processar a imagem (conversão e alinhamento)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return jsonify({"status": "erro", "mensagem": "Nenhum rosto detectado!"})

    # Criar diretório para salvar as imagens do aluno
    aluno_dir = os.path.join("imagens", nome)
    if not os.path.exists(aluno_dir):
        os.makedirs(aluno_dir)

    # Salvar a imagem
    img_count = len([f for f in os.listdir(aluno_dir) if os.path.isfile(os.path.join(aluno_dir, f))])
    img_name = os.path.join(aluno_dir, f"{nome}_{img_count}.jpg")
    cv2.imwrite(img_name, img)
    
    # Se o aluno já tiver 10 imagens, treina o modelo
    if img_count + 1 == 10:
        treinar_modelo()

    return jsonify({"status": "sucesso", "mensagem": "Imagem salva com sucesso!"})

# Treinar o modelo LBPH com as imagens salvas
def treinar_modelo():
    faces = []
    ids = []
    alunos = os.listdir('imagens')

    for aluno in alunos:
        aluno_path = os.path.join('imagens', aluno)

        # Verificar se o caminho é realmente um diretório (para evitar erros com arquivos)
        if os.path.isdir(aluno_path):
            for img_name in os.listdir(aluno_path):
                img_path = os.path.join(aluno_path, img_name)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                id_aluno = alunos.index(aluno)
                faces.append(img)
                ids.append(id_aluno)
    
    if len(faces) > 0:
        # Treinar o modelo
        recognizer.train(faces, np.array(ids))
        recognizer.write('modelo.yml')
        print("Modelo treinado com sucesso!")
    else:
        print("Nenhuma face foi encontrada para treinamento.")

@app.route('/reconhecer_foto', methods=['POST'])
def reconhecer_foto():
    # Verificar se o modelo foi treinado
    if not os.path.exists('modelo.yml'):
        return jsonify({"status": "erro", "mensagem": "O modelo não foi treinado ainda."})

    data = request.get_json()
    imagem_base64 = data['imagem'].split(',')[1]
    
    # Decodificar a imagem
    img_data = base64.b64decode(imagem_base64)
    np_img = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # Converter para escala de cinza e detectar o rosto
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return jsonify({"status": "erro", "mensagem": "Nenhum rosto detectado!"})

    # Fazer reconhecimento
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        id_aluno, confianca = recognizer.predict(roi_gray)

        alunos = os.listdir('imagens')
        nome_aluno = alunos[id_aluno]
        return jsonify({"status": "sucesso", "aluno": nome_aluno, "confianca": round(100 - confianca)})

    return jsonify({"status": "erro", "mensagem": "Não foi possível reconhecer o aluno."})


if __name__ == '__main__':
    app.run(debug=True)

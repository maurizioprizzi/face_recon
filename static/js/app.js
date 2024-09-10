document.addEventListener("DOMContentLoaded", function () {
    const video = document.createElement('video');
    const canvas = document.getElementById('videoCanvas');
    const ctx = canvas.getContext('2d');
    const capturarBtn = document.getElementById('capturarBtn');
    const feedback = document.getElementById('feedback');
    const cameraClick = document.getElementById('cameraClick');
    const nextStudentBtn = document.getElementById('nextStudentBtn');
    const startRecognitionBtn = document.getElementById('startRecognitionBtn');
    const reconhecimentoMsg = document.getElementById('reconhecimentoMsg');
    const errorMessage = document.getElementById('errorMessage');
    const nomeAlunoInput = document.getElementById('nome');
    let fotosTiradas = 0;
    let modoCaptura = true;
    let currentStudent = 1;
    let totalAlunos = 0;

    // Conectar à fonte de vídeo
    const streamVideo = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.play();
        } catch (err) {
            console.error("Erro ao acessar a webcam:", err);
            errorMessage.textContent = "Erro ao acessar a câmera. Verifique as permissões.";
        }
    };

    // Desenhar vídeo no canvas
    const desenharVideo = () => {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        if (modoCaptura) {
            ctx.font = '20px Arial';
            ctx.fillStyle = 'white';
            ctx.fillText(nomeAlunoInput.value, 10, canvas.height - 20);
        }
        requestAnimationFrame(desenharVideo);
    };

    // Atualizar feedback visual
    const atualizarFeedback = () => {
        feedback.innerHTML = `Fotos tiradas: ${fotosTiradas}/10`;
    };

    // Verificar se o nome foi inserido
    const verificarNome = () => {
        const nome = nomeAlunoInput.value.trim();
        if (nome === '') {
            capturarBtn.disabled = true;
            errorMessage.textContent = 'Por favor, insira o nome do aluno.';
        } else if (!/^[a-zA-Z\s]+$/.test(nome)) {
            capturarBtn.disabled = true;
            errorMessage.textContent = 'O nome do aluno deve conter apenas letras e espaços.';
        } else {
            capturarBtn.disabled = false;
            errorMessage.textContent = '';
        }
    };

    // Iniciar a fase de coleta de fotos
    const iniciarColeta = () => {
        totalAlunos = parseInt(document.getElementById('numAlunos').value);
        if (!totalAlunos || totalAlunos < 1) {
            alert("Por favor, insira um número válido de alunos.");
            return;
        }

        document.getElementById('initialInput').style.display = 'none';
        document.getElementById('fotoSection').style.display = 'block';
        modoCaptura = true;
        streamVideo();
        desenharVideo();
    };

    // Resetar o formulário para o próximo aluno
    const resetarFormulario = () => {
        nomeAlunoInput.value = '';
        fotosTiradas = 0;
        errorMessage.textContent = '';
        reconhecimentoMsg.innerHTML = "Reconhecimento não iniciado";
        capturarBtn.disabled = true;
        atualizarFeedback();
        nextStudentBtn.style.display = 'none';
        capturarBtn.style.display = 'inline';
    };

    // Função para capturar foto com atraso
    const capturarFotoComAtraso = (interval) => {
        return new Promise((resolve) => {
            setTimeout(() => {
                cameraClick.play();
                const dataURL = canvas.toDataURL('image/jpeg', 0.8); // Qualidade 80%
                fetch('/salvar_foto', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ imagem: dataURL, nome: nomeAlunoInput.value })
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Foto salva:', data);
                        resolve();
                    })
                    .catch((error) => {
                        console.error('Erro ao salvar a foto:', error);
                        resolve();
                    });
            }, interval);
        });
    };

    // Função para capturar todas as fotos
    const capturarTodasFotos = async () => {
        capturarBtn.disabled = true;
        for (let i = fotosTiradas; i < 10; i++) {
            await capturarFotoComAtraso(500);
            fotosTiradas++;
            atualizarFeedback();
        }

        if (fotosTiradas === 10) {
            alert(`Fotos do aluno ${nomeAlunoInput.value} completas!`);
            capturarBtn.style.display = 'none';
            if (currentStudent < totalAlunos) {
                nextStudentBtn.style.display = 'inline';
            } else {
                startRecognitionBtn.style.display = 'inline';
            }
        }
        capturarBtn.disabled = false;
    };

    // Capturar todas as fotos ao clicar no botão "Tirar Foto"
    capturarBtn.addEventListener('click', () => {
        capturarTodasFotos();
    });

    // Botão "Próximo Aluno"
    nextStudentBtn.addEventListener('click', () => {
        resetarFormulario();
        currentStudent++;
    });

    // Manter a câmera ativa durante o reconhecimento
    const iniciarReconhecimento = () => {
        modoCaptura = false;
        document.getElementById('fotoSection').style.display = 'none';
        document.getElementById('reconhecimentoSection').style.display = 'block';
        desenharVideo();

        const reconhecimentoLoop = setInterval(() => {
            const dataURL = canvas.toDataURL('image/jpeg', 0.5); // Qualidade 50%
            fetch('/reconhecer_foto', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ imagem: dataURL })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'sucesso') {
                        reconhecimentoMsg.innerHTML = `O aluno ${data.aluno} está na frente da câmera.`;
                    } else {
                        reconhecimentoMsg.innerHTML = 'Nenhum aluno reconhecido.';
                    }
                })
                .catch((error) => {
                    console.error('Erro no reconhecimento:', error);
                    // Handle error gracefully here (e.g., display a message to the user)
                });
        }, 3000); // Intervalo de 3 segundos

        // Clear the recognition loop when the recognition section is hidden
        document.getElementById('reconhecimentoSection').addEventListener('hidden', () => {
            clearInterval(reconhecimentoLoop);
        });
    };

    // Botão "Iniciar Reconhecimento"
    startRecognitionBtn.addEventListener('click', iniciarReconhecimento);

    // Iniciar coleta de fotos
    document.getElementById('iniciarColetaBtn').addEventListener('click', iniciarColeta);

    // Verificar se o nome foi inserido para habilitar o botão de tirar foto
    nomeAlunoInput.addEventListener('input', verificarNome);
});
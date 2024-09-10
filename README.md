
# Projeto de Reconhecimento Facial com Flask e OpenCV

Este projeto realiza o reconhecimento facial de alunos utilizando a biblioteca OpenCV para Python e um aplicativo web desenvolvido com Flask. O sistema permite capturar imagens dos alunos usando a webcam do notebook e treinar um modelo de IA para reconhecer os alunos em tempo real.

## Funcionalidades

- Captura de **10 fotos por aluno** usando a webcam do notebook.
- Treinamento de um modelo de reconhecimento facial usando **LBPHFaceRecognizer** do OpenCV.
- Reconhecimento facial em tempo real, permitindo que os alunos se alternem e vejam seus rostos sendo reconhecidos pelo sistema.
- Interface web interativa com HTML, CSS, e JavaScript.

## Pré-requisitos

Antes de rodar o projeto, certifique-se de ter as seguintes ferramentas instaladas no seu sistema:

- **Python 3.8+**
- **Flask** (`pip install flask`)
- **OpenCV para Python** (`pip install opencv-python opencv-contrib-python`)
- **Bibliotecas adicionais**:
  - `numpy` (`pip install numpy`)
  - `base64`

## Instalação

Siga as etapas abaixo para configurar e rodar o projeto localmente:

**1.** Clone o repositório:
```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
```

**2.** Crie e ative um ambiente virtual Python:
```bash
    python -m venv env
    source env/bin/activate  # Linux/Mac
    .\env\Scripts\activate   # Windows
```

**3.** Instale as dependências:

    pip install -r requirements.txt

**Nota**: Se o arquivo requirements.txt não estiver disponível, instale as dependências manualmente:

    pip install flask opencv-python opencv-contrib-python numpy

## Como Rodar o Projeto
**1.** Inicie o servidor Flask:

    python app.py

**2.** Abra o navegador e acesse o seguinte endereço:

    http://127.0.0.1:5000

**3.** Insira o número de alunos, tire as fotos e, ao final, inicie o reconhecimento facial.

## Fluxo do Projeto:
**1. Fase de Coleta de Fotos**
- O usuário insere o número de alunos que participarão.
- Cada aluno tira 10 fotos usando a webcam.
- As fotos são salvas na pasta *imagens/* com o nome do aluno.
**2. Fase de Reconhecimento Facial**
- Após a coleta de fotos, o sistema permite que os alunos se sentem em frente à câmera.
- O sistema reconhece o aluno baseado nas fotos capturadas e exibe o nome do aluno reconhecido na tela.

## Tecnologias Usadas
- **Flask**: Framework web para criar a API e gerenciar as rotas do projeto.
- **OpenCV**: Biblioteca de visão computacional usada para capturar imagens e realizar o reconhecimento facial.
- **JavaScript (Canvas)**: Utilizado para manipular a webcam no frontend.
- **HTML5 e CSS**: Para construir a interface web interativa.

## Personalização:
Se você quiser ajustar o número de fotos capturadas por aluno, modifique o valor na variável *capturarTodasFotos()* no arquivo **app.js**. Você pode também ajustar o tempo de intervalo entre as capturas para garantir que todas as fotos sejam processadas corretamente.

## Contribuição:
Sinta-se à vontade para fazer fork deste repositório e enviar pull requests. Se você encontrar algum problema, por favor, abra uma issue.

## Licença:
Este projeto está licenciado sob os termos da MIT License.

## Instruções Detalhadas:

- **Explicação Geral**: O projeto e suas funcionalidades são explicados, desde a captura de fotos até o reconhecimento facial.
- **Instalação e Rodagem**: Os passos para instalação do projeto e execução estão claros.
- **Estrutura do Projeto**: Incluímos uma visão da estrutura básica de pastas.
- **Personalização**: Explicação de como modificar a quantidade de fotos capturadas.
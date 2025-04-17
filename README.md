# AutoDub com ElevenLabs

Este projeto dublará vídeos com base em transcrição usando o Whisper e ElevenLabs.

## Como rodar localmente

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o servidor:
```bash
python main.py
```

3. Faça uma requisição POST para `/dub` com um arquivo de vídeo (`video`).

## API Key

Adicione sua API key do ElevenLabs diretamente no `main.py` na função `set_api_key`.
# 5_gerar_narracao_google_cloud.py
from google.cloud import texttospeech
import os
import subprocess

# --- CONFIGURAÇÃO ---
PASTA_ROTEIROS = "roteiro_narracao"
PASTA_NARRACAO = "narracao"

NOME_FINAL_AUDIO = "teste" 

# --- LÓGICA DO SCRIPT ---

# 1. Verificar a pasta de roteiros (lógica igual à anterior)
print(f"Verificando a pasta '{PASTA_ROTEIROS}' por arquivos de roteiro...")
if not os.path.isdir(PASTA_ROTEIROS):
    print(f"ERRO: A pasta '{PASTA_ROTEIROS}' não foi encontrada.")
    exit()
arquivos_roteiro = [f for f in os.listdir(PASTA_ROTEIROS) if f.endswith(".txt")]
if not arquivos_roteiro:
    print(f"ERRO: A pasta '{PASTA_ROTEIROS}' está vazia.")
    exit()
NOME_ARQUIVO_ROTEIRO = arquivos_roteiro[0]
caminho_roteiro = os.path.join(PASTA_ROTEIROS, NOME_ARQUIVO_ROTEIRO)
print(f"--> Roteiro encontrado: '{NOME_ARQUIVO_ROTEIRO}'. Usando este arquivo.")

# 2. Ler o conteúdo do arquivo de roteiro
with open(caminho_roteiro, "r", encoding="utf-8") as f:
    texto_para_narrar = f.read()
print("Conteúdo do roteiro lido com sucesso.")

# 3. Gerar o áudio com a API do Google Cloud
print("Gerando áudio com a API Google Cloud Text-to-Speech...")
try:
    # Inicia o cliente. Ele usará as credenciais que você configurou no Passo 1.
    client = texttospeech.TextToSpeechClient()

    # Define o texto de entrada
    synthesis_input = texttospeech.SynthesisInput(text=texto_para_narrar)

    # Configura a voz. Você pode escolher entre muitas vozes e idiomas.
    # 'es-US-Studio-B' é uma voz de alta qualidade (WaveNet) em espanhol.
    # Para ver outras vozes: https://cloud.google.com/text-to-speech/docs/voices
    voice = texttospeech.VoiceSelectionParams(
        language_code="es-US", name="es-US-Studio-B"
    )

    # Seleciona o tipo de áudio de saída (MP3)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Realiza a chamada à API para sintetizar a fala
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # 4. Salvar o arquivo de áudio
    os.makedirs(PASTA_NARRACAO, exist_ok=True)
    nome_audio= f"{NOME_FINAL_AUDIO}.mp3"
    caminho_saida_audio = os.path.join(PASTA_NARRACAO, nome_audio)

    # O áudio vem em formato binário, então salvamos com 'wb' (write binary)
    with open(caminho_saida_audio, "wb") as out:
        out.write(response.audio_content)
    
    print(f"\nNarração de alta qualidade gerada com sucesso e salva em: '{caminho_saida_audio}'")
    subprocess.run(["python", "criar_videos_base.py"], check=True)

except Exception as e:
    print(f"Ocorreu um erro ao gerar o áudio com a API do Google Cloud: {e}")
    print("Verifique se suas credenciais (arquivo JSON) e a variável de ambiente estão configuradas corretamente.")

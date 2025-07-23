# 1_obter_transcricao.py
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import os
import subprocess

# --- CONFIGURAÇÃO ---
PASTA_SAIDA = "transcricao"

# --- LÓGICA DO SCRIPT ---

# 1. Pedir o ID do vídeo para o usuário
video_id = input("Por favor, insira o ID do vídeo do YouTube que você quer transcrever: ")

if not video_id:
    print("ERRO: Nenhum ID de vídeo foi inserido. Saindo.")
    exit()

try:
    print(f"\nBuscando transcrição para o ID do vídeo: {video_id}...")
    
    # 2. Obter a transcrição (em espanhol)
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['es'])
    full_transcript = " ".join([segment['text'] for segment in transcript_list])
    print("Transcrição encontrada com sucesso!")

    # 3. Salvar a transcrição
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    output_filename = f"transcripcion_espanol_{video_id}.txt"
    caminho_completo = os.path.join(PASTA_SAIDA, output_filename)
    with open(caminho_completo, "w", encoding="utf-8") as f:
        f.write(full_transcript)
    print(f"Transcrição salva em: '{caminho_completo}'")

    # 4. Chamar o próximo script da cadeia
    print("\n----------------------------------------------------")
    print(f"SUCESSO: Transcrição gerada. Passando para a geração de roteiro...")
    print("----------------------------------------------------")
    subprocess.run(["python", "gerar_novo_roteiro.py"], check=True)

except (TranscriptsDisabled, NoTranscriptFound):
    print(f"ERRO: Não foi possível encontrar uma transcrição em espanhol para o vídeo com ID: {video_id}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
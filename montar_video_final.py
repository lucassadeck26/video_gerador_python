# 2_montar_video_com_narracao.py (VERSÃO COMPLETA E VERIFICADA)
import moviepy.editor as mp
import os
import subprocess

# --- CONFIGURAÇÃO ---
PASTA_VIDEOS_BASE = "videos"
ARQUIVO_NARRACAO = "narracao/teste.mp3"  # Verifique se o nome do arquivo de narração está correto
PASTA_SAIDA_INTERMEDIARIA = "video_sem_trilha"
ARQUIVO_SAIDA_INTERMEDIARIA = os.path.join(PASTA_SAIDA_INTERMEDIARIA, "video_sem_trilha.mp4")

# --- LÓGICA PRINCIPAL ---
if not os.path.exists(PASTA_SAIDA_INTERMEDIARIA):
    os.makedirs(PASTA_SAIDA_INTERMEDIARIA)
    print(f"Pasta '{PASTA_SAIDA_INTERMEDIARIA}' criada.")

print(f"Carregando narração '{ARQUIVO_NARRACAO}'...")
try:
    audio_narracao = mp.AudioFileClip(ARQUIVO_NARRACAO)
    duracao_total = audio_narracao.duration
    print(f"Duração da narração: {duracao_total:.2f} segundos.")
except Exception as e:
    print(f"ERRO ao carregar o arquivo de narração: {e}")
    exit()

print(f"Procurando vídeos na pasta '{PASTA_VIDEOS_BASE}'...")
arquivos_videos_base = sorted([f for f in os.listdir(PASTA_VIDEOS_BASE) if f.lower().endswith('.mp4')])

if not arquivos_videos_base:
    print(f"ERRO: Nenhum vídeo base encontrado na pasta '{PASTA_VIDEOS_BASE}'. Execute o script 1 primeiro.")
    exit()

print(f"Encontrados {len(arquivos_videos_base)} vídeos base.")
print("Montando a sequência de vídeo em loop...")
clipes_em_loop = []
duracao_acumulada = 0
while duracao_acumulada < duracao_total:
    for nome_video in arquivos_videos_base:
        caminho_video = os.path.join(PASTA_VIDEOS_BASE, nome_video)
        clipe = mp.VideoFileClip(caminho_video)
        clipes_em_loop.append(clipe)
        duracao_acumulada += clipe.duration
        if duracao_acumulada >= duracao_total:
            break

print("Juntando os clipes...")
video_bruto = mp.concatenate_videoclips(clipes_em_loop)

print("Ajustando duração e adicionando narração...")
video_com_narracao = video_bruto.set_duration(duracao_total).set_audio(audio_narracao)

print(f"Renderizando o vídeo intermediário '{ARQUIVO_SAIDA_INTERMEDIARIA}'...")
video_com_narracao.write_videofile(
    ARQUIVO_SAIDA_INTERMEDIARIA, fps=30, codec="libx264", logger='bar'
)
print("\nMontagem com narração finalizada!")
print("\n----------------------------------------------------")
print("Iniciando a adição da trilha sonora...")
print("----------------------------------------------------")
try:
    subprocess.run(["python3", "adicionar_trilha.py"], check=True)
except Exception as e:
    print(f"Ocorreu um erro ao chamar o script da trilha sonora: {e}")
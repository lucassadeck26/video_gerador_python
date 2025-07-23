# 3_adicionar_trilha.py (VERSÃO CORRIGIDA)
import moviepy.editor as mp
import moviepy.audio.fx.all as afx
import os

# --- CONFIGURAÇÃO ---
PASTA_VIDEO_INTERMEDIARIO = "video_sem_trilha"
ARQUIVO_VIDEO_INTERMEDIARIO = os.path.join(PASTA_VIDEO_INTERMEDIARIO, "video_sem_trilha.mp4")
ARQUIVO_TRILHA = "trilha_sonora/trilha.mp3"
PASTA_SAIDA_FINAL = "video_com_trilha"
ARQUIVO_SAIDA_FINAL = os.path.join(PASTA_SAIDA_FINAL, "video_final_com_trilha.mp4")

# --- LÓGICA PRINCIPAL ---
if not os.path.exists(PASTA_SAIDA_FINAL):
    os.makedirs(PASTA_SAIDA_FINAL)

print(f"Carregando vídeo intermediário '{ARQUIVO_VIDEO_INTERMEDIARIO}'...")
try:
    video_principal = mp.VideoFileClip(ARQUIVO_VIDEO_INTERMEDIARIO)
except Exception as e:
    print(f"ERRO: Não foi possível carregar o vídeo intermediário. Detalhe: {e}")
    exit()

print(f"Carregando trilha sonora '{ARQUIVO_TRILHA}'...")
try:
    trilha_sonora = mp.AudioFileClip(ARQUIVO_TRILHA)
except Exception as e:
    print(f"ERRO: Não foi possível carregar a trilha sonora: {e}")
    exit()

print("Mixando os áudios...")
audio_narracao = video_principal.audio
trilha_em_loop = afx.audio_loop(trilha_sonora, duration=video_principal.duration)

# ==================================================================
# CORREÇÃO DO VOLUME AQUI
# Abaixamos o volume para 10% (0.1). Você pode usar 0.08, 0.05, etc.
# Experimente com este valor até ficar do seu agrado.
# ==================================================================
trilha_volume_baixo = trilha_em_loop.volumex(0.1)

audio_final_mixado = mp.CompositeAudioClip([audio_narracao, trilha_volume_baixo])
video_com_trilha = video_principal.set_audio(audio_final_mixado)

print(f"Renderizando o vídeo final com trilha sonora para '{ARQUIVO_SAIDA_FINAL}'...")
video_com_trilha.write_videofile(
    ARQUIVO_SAIDA_FINAL, fps=30, codec="libx264", audio_codec="aac", logger='bar'
)
print("\n\nPROCESSO COMPLETO FINALIZADO! Seu vídeo com trilha sonora está pronto!")
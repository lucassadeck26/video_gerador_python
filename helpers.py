# helpers.py
import os
import textwrap
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import google.generativeai as genai
from google.cloud import texttospeech
from werkzeug.utils import secure_filename
import moviepy.editor as mp
from PIL import Image
import numpy as np
import moviepy.audio.fx.all as afx 

# Constantes das pastas
PASTA_TRANSCRICAO = "transcricao"
PASTA_ROTEIRO = "roteiro_narracao"
PASTA_NARRACAO = "narracao"
PASTA_IMAGENS = "imagens"
PASTA_TRILHA_SONORA = "trilha_sonora" 
PASTA_VIDEO_SEM_TRILHA = "video_sem_trilha" 
PASTA_VIDEOS_BASE = "videos"
PASTA_VIDEO_FINAL = "video_final"
PASTA_TEMA = "tema"
PASTA_ROTEIRO_PARTES = "roteiro_partes"
PASTA_NARRACAO_PARTES = "narracao_partes"


def verificar_status():
    """Verifica a existência de ficheiros em cada pasta para determinar o estado do projeto."""
    status = {
        'transcricao': None, 'roteiro': None, 'narracao': None,
        'imagens': [], 'videos_base': [], 
        'video_sem_trilha': None, 'trilha_sonora': [], 'video_final': None,
        'tema_novela': None,
        'roteiro_partes': [], # NOVO ESTADO
        'narracao_partes': [] # NOVO ESTADO
    }
    
    
    # Verifica transcrição
    if os.path.exists(PASTA_TRANSCRICAO) and os.listdir(PASTA_TRANSCRICAO):
        arquivos_txt = [f for f in os.listdir(PASTA_TRANSCRICAO) if f.endswith('.txt')]
        if arquivos_txt:
            status['transcricao'] = arquivos_txt[0]
    
    # Verifica roteiro
    if os.path.exists(PASTA_ROTEIRO) and os.listdir(PASTA_ROTEIRO):
        arquivos_txt = [f for f in os.listdir(PASTA_ROTEIRO) if f.endswith('.txt')]
        if arquivos_txt:
            status['roteiro'] = arquivos_txt[0]
    
    # Verifica narração
    if os.path.exists(PASTA_NARRACAO) and os.listdir(PASTA_NARRACAO):
        arquivos_mp3 = [f for f in os.listdir(PASTA_NARRACAO) if f.endswith('.mp3')]
        if arquivos_mp3:
            status['narracao'] = arquivos_mp3[0]
    
    # Verifica imagens
    if os.path.exists(PASTA_IMAGENS):
        status['imagens'] = sorted([f for f in os.listdir(PASTA_IMAGENS) 
                                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    
    # Verifica vídeos base
    if os.path.exists(PASTA_VIDEOS_BASE):
        status['videos_base'] = sorted([f for f in os.listdir(PASTA_VIDEOS_BASE) 
                                       if f.lower().endswith('.mp4')])
    
    # Verifica vídeo sem trilha
    if os.path.exists(PASTA_VIDEO_SEM_TRILHA) and os.listdir(PASTA_VIDEO_SEM_TRILHA):
        arquivos_mp4 = [f for f in os.listdir(PASTA_VIDEO_SEM_TRILHA) if f.endswith('.mp4')]
        if arquivos_mp4:
            status['video_sem_trilha'] = arquivos_mp4[0]
    
    # Verifica trilha sonora
    if os.path.exists(PASTA_TRILHA_SONORA):
        status['trilha_sonora'] = sorted([f for f in os.listdir(PASTA_TRILHA_SONORA) 
                                         if f.lower().endswith('.mp3')])
    
    # Verifica vídeo final
    if os.path.exists(PASTA_VIDEO_FINAL) and os.listdir(PASTA_VIDEO_FINAL):
        arquivos_mp4 = [f for f in os.listdir(PASTA_VIDEO_FINAL) if f.endswith('.mp4')]
        if arquivos_mp4:
            status['video_final'] = arquivos_mp4[0]

    if os.path.exists(PASTA_NARRACAO_PARTES):
        status['narracao_partes'] = sorted([f for f in os.listdir(PASTA_NARRACAO_PARTES) if f.endswith('.mp3')])
    if os.path.exists(PASTA_TEMA) and os.path.exists(os.path.join(PASTA_TEMA, 'tema.txt')):
        with open(os.path.join(PASTA_TEMA, 'tema.txt'), 'r', encoding='utf-8') as f:
            status['tema_novela'] = f.read().strip()        
    if os.path.exists(PASTA_ROTEIRO_PARTES):
        status['roteiro_partes'] = sorted([f for f in os.listdir(PASTA_ROTEIRO_PARTES) if f.endswith('.txt')])
    if os.path.exists(PASTA_NARRACAO) and any(f.endswith('.mp3') for f in os.listdir(PASTA_NARRACAO)):
        status['narracao'] = os.listdir(PASTA_NARRACAO)[0]


    # --- DIAGNÓSTICO DA PASTA DE TEMA ---
    print("\n--- DIAGNÓSTICO DA PASTA DE TEMA ---")
    caminho_absoluto_tema = os.path.abspath(PASTA_TEMA)
    caminho_ficheiro_tema = os.path.join(PASTA_TEMA, 'tema.txt')
    print(f"Procurando pela pasta: {caminho_absoluto_tema}")
    
    if os.path.exists(PASTA_TEMA):
        print("--> SUCESSO: A pasta 'tema' foi encontrada.")
        print(f"Procurando pelo ficheiro: {os.path.abspath(caminho_ficheiro_tema)}")
        if os.path.exists(caminho_ficheiro_tema):
            print("--> SUCESSO: O ficheiro 'tema.txt' foi encontrado.")
            try:
                with open(caminho_ficheiro_tema, 'r', encoding='utf-8') as f:
                    conteudo = f.read().strip()
                    status['tema_novela'] = conteudo
                    print(f"--> Conteúdo lido do ficheiro: '{conteudo}'")
            except Exception as e:
                print(f"--> ERRO ao ler o ficheiro 'tema.txt': {e}")
        else:
            print("--> FALHA: O ficheiro 'tema.txt' NÃO foi encontrado dentro da pasta 'tema'.")
    else:
        print("--> FALHA: A pasta 'tema' NÃO foi encontrada neste local.")
    print("--- FIM DO DIAGNÓSTICO ---\n")
    # --- FIM DO DIAGNÓSTICO ---
            
    return status

def gerar_transcricao(nome_novela, conteudo_transcricao):
    """Salva o nome da novela e o conteúdo da transcrição em ficheiros."""
    try:
        # Salva o nome da novela
        os.makedirs(PASTA_TEMA, exist_ok=True)
        with open(os.path.join(PASTA_TEMA, 'tema.txt'), 'w', encoding='utf-8') as f:
            f.write(nome_novela)
            
        # Salva a transcrição
        os.makedirs(PASTA_TRANSCRICAO, exist_ok=True)
        excluir_arquivo('transcricao') # Limpa a pasta
        with open(os.path.join(PASTA_TRANSCRICAO, 'transcricao.txt'), "w", encoding="utf-8") as f:
            f.write(conteudo_transcricao)
        
        return True, "Nome da novela e transcrição foram salvos com sucesso!"
    except Exception as e:
        return False, f"Ocorreu um erro ao salvar os dados: {e}"


# VERSÃO ATUALIZADA DA FUNÇÃO DE EXCLUSÃO

def excluir_arquivo(etapa, arquivos_especificos=None):
    """Exclui ficheiros de uma determinada etapa."""
    pastas = {
        'transcricao': [PASTA_TRANSCRICAO, PASTA_TEMA],
        'roteiro': [PASTA_ROTEIRO, PASTA_ROTEIRO_PARTES],
        'narracao': [PASTA_NARRACAO, PASTA_NARRACAO_PARTES],
        'imagens': [PASTA_IMAGENS],
        'videos_base': [PASTA_VIDEOS_BASE],
        'video_sem_trilha': [PASTA_VIDEO_SEM_TRILHA],
        'trilha_sonora': [PASTA_TRILHA_SONORA],
        'video_final': [PASTA_VIDEO_FINAL]
    }
    pastas_alvo = pastas.get(etapa, [])
    for pasta in pastas_alvo:
        if os.path.exists(pasta):
            arquivos_a_excluir = arquivos_especificos if arquivos_especificos else os.listdir(pasta)
            for nome_ficheiro in arquivos_a_excluir:
                caminho_ficheiro = os.path.join(pasta, nome_ficheiro)
                if os.path.exists(caminho_ficheiro):
                    os.remove(caminho_ficheiro)
    return True




# ETAPA 2.0-----------------------------------------

def gerar_roteiro():
    """Lê a transcrição, gera o roteiro com a IA, salva o ficheiro completo E o divide em partes."""
    try:
        status = verificar_status()
        if not status['transcricao'] or not status['tema_novela']:
            return False, "ERRO: Transcrição ou nome da novela não encontrados."
            
        caminho_transcricao = os.path.join(PASTA_TRANSCRICAO, status['transcricao'])
        nome_novela = status['tema_novela']
        
        with open(caminho_transcricao, "r", encoding="utf-8") as f:
            conteudo_transcricao = f.read()

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        prompt_template = f"""
        Por favor, crie um texto sobre "{nome_novela}" com as seguintes características:
        - Público-alvo: Fãs da novela {nome_novela}
        - Estilo de escrita: informal
        - Humor: leve
        - Tamanho: 2500 palavras
        - Tonalidade: descontraída
        - Objetivo: informar
        - Referências a considerar: você é uma fã de carteirinha da novela {nome_novela}, reescreva o resumo a seguir, separado por virgula, acrescente detalhes, torne a história original e cativante, deixando o texto o mais real possível, quero ctas naturais, para ser narrada por uma mulher. lembrando que é em espanhol o idioma. pergunte de onde a pessoa está assistindo, gere engagamento para a rede social: 
        {conteudo_transcricao}
        - Não inclua títulos ou subtítulos, apenas o texto do conteúdo.
        O texto deve ser bem estruturado, coerente e adaptado ao público-alvo especificado.
        """
        
        print("Enviando prompt para a IA da Gemini...")
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt_template)
        roteiro_gerado = response.text
        print("Roteiro recebido da IA.")

        # 1. Salva o roteiro completo para download
        os.makedirs(PASTA_ROTEIRO, exist_ok=True)
        excluir_arquivo('roteiro') # Limpa a pasta do roteiro completo e das partes
        nome_arquivo_completo = f"roteiro_completo_{nome_novela.replace(' ', '_')}.txt"
        with open(os.path.join(PASTA_ROTEIRO, nome_arquivo_completo), "w", encoding="utf-8") as f:
            f.write(roteiro_gerado)

        # 2. Divide o roteiro em partes de 500 caracteres
        os.makedirs(PASTA_ROTEIRO_PARTES, exist_ok=True)
        partes = textwrap.wrap(roteiro_gerado, 500, break_long_words=True, break_on_hyphens=False)
        
        for i, parte in enumerate(partes):
            nome_parte = f"parte_{i+1:03d}.txt" # ex: parte_001.txt
            with open(os.path.join(PASTA_ROTEIRO_PARTES, nome_parte), "w", encoding="utf-8") as f:
                f.write(parte)

        return True, f"Roteiro completo e {len(partes)} partes foram criados com sucesso!"

    except Exception as e:
        return False, f"Ocorreu um erro ao gerar o roteiro: {e}"




# ... ETAPA 3...
def listar_vozes():
    """Lista as vozes disponíveis em Português (BR) e Espanhol."""
    try:
        client = texttospeech.TextToSpeechClient()
        response = client.list_voices()
        print("o valor da response dá: ", response)
        
        vozes_disponiveis = {
            'pt-BR': [],
            'es': []
        }

        for voice in response.voices:
            lang_code = voice.language_codes[0]
            
            # CORREÇÃO APLICADA AQUI: Usamos .name em vez de .Name()
            gender_str = voice.ssml_gender.name.capitalize()

            if lang_code == 'pt-BR':
                vozes_disponiveis['pt-BR'].append({
                    'name': voice.name,
                    'gender': gender_str
                })
            elif lang_code.startswith('es-'):
                vozes_disponiveis['es'].append({
                    'name': voice.name,
                    'gender': gender_str
                })
        
        vozes_disponiveis['pt-BR'] = sorted(vozes_disponiveis['pt-BR'], key=lambda x: x['name'])
        vozes_disponiveis['es'] = sorted(vozes_disponiveis['es'], key=lambda x: x['name'])

        return vozes_disponiveis
    except Exception as e:
        print(f"Erro ao listar vozes: {e}")
        return {'pt-BR': [], 'es': []}




# ETAPA 3.0----------------------------------
def gerar_narracao_por_partes(voice_name):
    """Gera um ficheiro de áudio para CADA parte do roteiro."""
    try:
        status = verificar_status()
        if not status['roteiro_partes']:
            return False, "ERRO: Nenhuma parte do roteiro encontrada para gerar os áudios."

        os.makedirs(PASTA_NARRACAO_PARTES, exist_ok=True)
        excluir_arquivo('narracao') # Apaga narração final e partes antigas
        
        client = texttospeech.TextToSpeechClient()
        language_code = '-'.join(voice_name.split('-')[:2])
        voice = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_name)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        
        audios_gerados = 0
        for nome_roteiro_parte in status['roteiro_partes']:
            caminho_roteiro = os.path.join(PASTA_ROTEIRO_PARTES, nome_roteiro_parte)
            with open(caminho_roteiro, "r", encoding="utf-8") as f:
                texto_para_narrar = f.read()

            synthesis_input = texttospeech.SynthesisInput(text=texto_para_narrar)
            response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            
            nome_base, _ = os.path.splitext(nome_roteiro_parte)
            nome_audio = f"{nome_base}.mp3"
            caminho_saida_audio = os.path.join(PASTA_NARRACAO_PARTES, nome_audio)
            with open(caminho_saida_audio, "wb") as out:
                out.write(response.audio_content)
            audios_gerados += 1

        return True, f"{audios_gerados} partes de áudio foram geradas com sucesso!"
    except Exception as e:
        return False, f"Ocorreu um erro ao gerar os áudios: {e}"



# ETAPA 3.1----------------------------------
def juntar_audios(nomes_audios_selecionados):
    """Junta os ficheiros de áudio selecionados numa única narração final."""
    if not nomes_audios_selecionados:
        return False, "ERRO: Nenhum áudio foi selecionado para ser juntado."
    
    try:
        nomes_audios_ordenados = sorted(nomes_audios_selecionados)
        clips_de_audio = [mp.AudioFileClip(os.path.join(PASTA_NARRACAO_PARTES, nome)) for nome in nomes_audios_ordenados]
        
        narracao_final = mp.concatenate_audioclips(clips_de_audio)
        
        os.makedirs(PASTA_NARRACAO, exist_ok=True)
        excluir_arquivo('narracao') # Apaga a narração final antiga, mas não as partes
        caminho_saida = os.path.join(PASTA_NARRACAO, "narracao_final.mp3")
        narracao_final.write_audiofile(caminho_saida)
        
        return True, "Narração final montada com sucesso!"
    except Exception as e:
        return False, f"Ocorreu um erro ao juntar os áudios: {e}"



# --- ETAPA 4  COMEÇA AQUI---
def salvar_imagens_upload(arquivos):
    """Salva os arquivos de imagem enviados pelo formulário."""
    os.makedirs(PASTA_IMAGENS, exist_ok=True)
    nomes_salvos = []
    for arquivo in arquivos:
        if arquivo and arquivo.filename != '':
            nome_seguro = secure_filename(arquivo.filename)
            caminho_salvar = os.path.join(PASTA_IMAGENS, nome_seguro)
            arquivo.save(caminho_salvar)
            nomes_salvos.append(nome_seguro)
    return nomes_salvos

# função de renomear imagens
def renomear_imagens_em_ordem():
    """Renomeia todas as imagens na pasta para um formato sequencial simples (1.png, 2.png, etc.)."""
    status = verificar_status()
    imagens = status['imagens'] # A lista já vem ordenada alfabeticamente
    if not imagens:
        return False, "Nenhuma imagem para renomear."

    # Etapa 1: Renomear para nomes temporários para evitar conflitos (ex: 1.png -> 2.png e 2.png -> 1.png)
    caminhos_temporarios = []
    for nome_arquivo in imagens:
        caminho_antigo = os.path.join(PASTA_IMAGENS, nome_arquivo)
        caminho_temp = caminho_antigo + ".tmp"
        os.rename(caminho_antigo, caminho_temp)
        caminhos_temporarios.append(caminho_temp)

    # Etapa 2: Renomear dos nomes temporários para os nomes finais sequenciais
    for i, caminho_temp in enumerate(caminhos_temporarios):
        # Pega a extensão do nome original (antes de adicionar .tmp)
        _, extensao_original = os.path.splitext(caminho_temp.replace(".tmp", ""))
        
        # Cria o novo nome final (ex: "1.png")
        novo_nome_final = f"{i+1}{extensao_original}"
        caminho_novo_final = os.path.join(PASTA_IMAGENS, novo_nome_final)
        
        os.rename(caminho_temp, caminho_novo_final)

    return True, "Imagens renomeadas para uma sequência numérica simples."


# NOVA FUNÇÃO PARA REDIMENSIONAR
def redimensionar_imagens():
    """Verifica e redimensiona todas as imagens para 1280x720."""
    status = verificar_status()
    imagens = status['imagens']
    if not imagens:
        return False, "Nenhuma imagem para redimensionar."

    tamanho_alvo = (1280, 720)
    imagens_redimensionadas = 0
    for nome_arquivo in imagens:
        caminho_imagem = os.path.join(PASTA_IMAGENS, nome_arquivo)
        try:
            with Image.open(caminho_imagem) as img:
                if img.size != tamanho_alvo:
                    print(f"Redimensionando '{nome_arquivo}' de {img.size} para {tamanho_alvo}...")
                    # Usa LANCZOS para alta qualidade de redimensionamento
                    img_redimensionada = img.resize(tamanho_alvo, Image.Resampling.LANCZOS)
                    # Salva a imagem, sobrescrevendo a original
                    img_redimensionada.save(caminho_imagem)
                    imagens_redimensionadas += 1
        except Exception as e:
            print(f"Não foi possível redimensionar '{nome_arquivo}': {e}")

    if imagens_redimensionadas > 0:
        return True, f"{imagens_redimensionadas} imagem(ns) foram redimensionadas para 1280x720."
    else:
        return True, "Todas as imagens já estavam no formato 1280x720."



def criar_clipe_zoom_para_imagem(caminho_imagem, tipo_zoom, duracao=10):
    """
    Cria um clipe de vídeo com diferentes tipos de zoom e movimento (pan).
    """
    LARGURA_VIDEO = 1280
    ALTURA_VIDEO = 720
    
    img_clip = mp.ImageClip(caminho_imagem).set_duration(duracao)

    def efeito_zoom_pan(get_frame, t):
        # Pega o frame original da imagem
        frame = get_frame(t)
        pil_img = Image.fromarray(frame)

        # Calcula a escala do zoom (de 100% para 135%)
        escala = 1.0 + (t / duracao) * 0.35

        # Redimensiona a imagem para o tamanho do zoom atual
        nova_largura = int(pil_img.width * escala)
        nova_altura = int(pil_img.height * escala)
        img_redimensionada = pil_img.resize(
            (nova_largura, nova_altura),
            resample=Image.Resampling.LANCZOS
        )

        # Calcula a área de corte (a "câmera")
        excesso_largura = nova_largura - LARGURA_VIDEO
        excesso_altura = nova_altura - ALTURA_VIDEO
        fator_tempo = t / duracao # Vai de 0 no início a 1 no final

        if tipo_zoom == 'direita':
            # A câmera se move para a diagonal inferior direita
            left = fator_tempo * excesso_largura
            upper = fator_tempo * excesso_altura
        elif tipo_zoom == 'esquerda':
            # A câmera se move para a diagonal superior esquerda
            left = (1 - fator_tempo) * excesso_largura
            upper = (1 - fator_tempo) * excesso_altura
        else: # 'centro'
            # A câmera fica parada no centro
            left = excesso_largura / 2
            upper = excesso_altura / 2
            
        right = left + LARGURA_VIDEO
        lower = upper + ALTURA_VIDEO

        # Corta a imagem redimensionada para o tamanho do vídeo final
        img_cortada = img_redimensionada.crop((left, upper, right, lower))
        
        return np.array(img_cortada)

    # Aplica a função de transformação ao clipe de imagem
    clipe_final = img_clip.fl(efeito_zoom_pan)
    return clipe_final

# ==================================================================
# FUNÇÃO DE GERAÇÃO DE VÍDEOS ATUALIZADA
# ==================================================================

def gerar_videos_base(task):
    """Gera os vídeos base e reporta o progresso para o Celery."""
    try:
        status = verificar_status()
        imagens = status['imagens']
        if not imagens:
            return {'status': 'Nenhuma imagem encontrada.'}

        os.makedirs(PASTA_VIDEOS_BASE, exist_ok=True)
        tipos_de_zoom = ['direita', 'esquerda', 'centro']
        total_videos = len(imagens)
        
        for i, nome_imagem in enumerate(imagens):
            # --- Relatório de Progresso ---
            mensagem = f"A gerar vídeo {i + 1} de {total_videos} ({nome_imagem})..."
            task.update_state(state='PROGRESS', meta={'current': i, 'total': total_videos, 'status': mensagem})
            print(f"WORKER: {mensagem}")
            
            caminho_imagem = os.path.join(PASTA_IMAGENS, nome_imagem)
            nome_base, _ = os.path.splitext(nome_imagem)
            nome_video = f"{nome_base}.mp4"
            caminho_video = os.path.join(PASTA_VIDEOS_BASE, nome_video)

            if not os.path.exists(caminho_video):
                tipo_zoom_atual = tipos_de_zoom[i % len(tipos_de_zoom)]
                clipe = criar_clipe_zoom_para_imagem(caminho_imagem, tipo_zoom=tipo_zoom_atual)
                if clipe:
                    clipe.write_videofile(caminho_video, fps=30, logger=None) # logger=None para um output mais limpo

        return {'current': total_videos, 'total': total_videos, 'status': 'Geração de vídeos base concluída!'}
    except Exception as e:
        task.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        raise e



"""   
def gerar_videos_base():
    Gera os vídeos de 10 segundos para cada imagem, alternando os efeitos de zoom
    status = verificar_status()
    imagens = status['imagens']
    if not imagens:
        return False, "Nenhuma imagem encontrada para gerar vídeos."

    os.makedirs(PASTA_VIDEOS_BASE, exist_ok=True)
    videos_criados = 0
    
    # Define a sequência de zooms que irá se repetir
    tipos_de_zoom = ['direita', 'esquerda', 'centro']
    
    # Usa enumerate para saber o índice (0, 1, 2, ...) de cada imagem
    for i, nome_imagem in enumerate(imagens):
        caminho_imagem = os.path.join(PASTA_IMAGENS, nome_imagem)
        nome_base, _ = os.path.splitext(nome_imagem)
        nome_video = f"{nome_base}.mp4"
        caminho_video = os.path.join(PASTA_VIDEOS_BASE, nome_video)

        if os.path.exists(caminho_video):
            print(f"Vídeo '{nome_video}' já existe. Pulando.")
            continue
        
        # Escolhe o tipo de zoom baseado no índice da imagem (0, 1, 2, 0, 1, 2, ...)
        tipo_zoom_atual = tipos_de_zoom[i % len(tipos_de_zoom)]
        
        print(f"Gerando vídeo para '{nome_imagem}' com zoom '{tipo_zoom_atual}'...")
        
        # Passa o tipo de zoom para a função de criação do clipe
        clipe = criar_clipe_zoom_para_imagem(caminho_imagem, tipo_zoom=tipo_zoom_atual)
        
        if clipe:
            clipe.write_videofile(caminho_video, fps=30)
            videos_criados += 1

    return True, f"{videos_criados} novos vídeos base foram gerados com sucesso."
"""   

# VERSÃO CORRIGIDA DA FUNÇÃO DE EXCLUSÃO
# ... (outras funções como gerar_transcricao, etc. permanecem as mesmas) ...
def excluir_arquivo(etapa, arquivos_especificos=None):
    """Exclui ficheiros de uma determinada etapa. Pode excluir tudo ou ficheiros específicos."""
    pastas = {
        'transcricao': PASTA_TRANSCRICAO,
        'roteiro': PASTA_ROTEIRO,
        'narracao': PASTA_NARRACAO,
        'imagens': PASTA_IMAGENS,
        'videos_base': PASTA_VIDEOS_BASE,
        'video_sem_trilha': PASTA_VIDEO_SEM_TRILHA,
        'trilha_sonora': PASTA_TRILHA_SONORA,
        'video_final': PASTA_VIDEO_FINAL
    }
    pasta_alvo = pastas.get(etapa)
    if not (pasta_alvo and os.path.exists(pasta_alvo)):
        return False

    if arquivos_especificos:
        for nome_ficheiro in arquivos_especificos:
            caminho_ficheiro = os.path.join(pasta_alvo, nome_ficheiro)
            if os.path.exists(caminho_ficheiro):
                os.remove(caminho_ficheiro)
    else:
        for f in os.listdir(pasta_alvo):
            os.remove(os.path.join(pasta_alvo, f))
    return True



# ==================================================================
# ETAPA 5
# ==================================================================
def montar_video_final(task):
    """Monta o vídeo final e reporta o progresso."""
    try:
        status = verificar_status()
        audio_clip = mp.AudioFileClip(os.path.join(PASTA_NARRACAO, status['narracao']))
        duracao_total = audio_clip.duration
        
        task.update_state(state='PROGRESS', meta={'status': 'A carregar clips de vídeo base...'})
        clips_video = [mp.VideoFileClip(os.path.join(PASTA_VIDEOS_BASE, v)) for v in status['videos_base']]
        
        task.update_state(state='PROGRESS', meta={'status': 'A concatenar e a fazer o loop do vídeo...'})
        video_loop = mp.vfx.loop(mp.concatenate_videoclips(clips_video, method="compose"), duration=duracao_total)
        video_com_audio = video_loop.set_audio(audio_clip)
        
        os.makedirs(PASTA_VIDEO_SEM_TRILHA, exist_ok=True)
        excluir_arquivo('video_sem_trilha')
        caminho_saida = os.path.join(PASTA_VIDEO_SEM_TRILHA, "video_sem_trilha.mp4")
        
        # O logger do MoviePy será usado para reportar o progresso da renderização
        video_com_audio.write_videofile(caminho_saida, fps=30, codec="libx264")

        return {'status': 'Montagem do vídeo (sem trilha) concluída!'}
    except Exception as e:
        task.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        raise e


"""   
def montar_video_final():
    
    Monta o vídeo (SEM TRILHA) juntando os vídeos base com a narração.
   
    status = verificar_status()
    videos_base = status['videos_base']
    arquivo_narracao = status['narracao']

    if not videos_base or not arquivo_narracao:
        return False, "ERRO: É necessário ter os vídeos base e a narração prontos."

    try:
        print("Iniciando a montagem do vídeo (sem trilha)...")
        caminho_narracao = os.path.join(PASTA_NARRACAO, arquivo_narracao)
        audio_clip = mp.AudioFileClip(caminho_narracao)
        duracao_total = audio_clip.duration

        clipes_de_video = [mp.VideoFileClip(os.path.join(PASTA_VIDEOS_BASE, nome)) for nome in videos_base]
        
        video_concatenado = mp.concatenate_videoclips(clipes_de_video, method="compose")
        video_em_loop = mp.vfx.loop(video_concatenado, duration=duracao_total)
        
        video_final_sem_audio = video_em_loop.set_audio(audio_clip)

        # Salva o ficheiro na pasta INTERMEDIÁRIA correta
        os.makedirs(PASTA_VIDEO_SEM_TRILHA, exist_ok=True)
        for f in os.listdir(PASTA_VIDEO_SEM_TRILHA):
            os.remove(os.path.join(PASTA_VIDEO_SEM_TRILHA, f))

        caminho_saida = os.path.join(PASTA_VIDEO_SEM_TRILHA, "video_sem_trilha.mp4")
        video_final_sem_audio.write_videofile(caminho_saida, fps=30, codec="libx264")

        return True, "Vídeo (sem trilha) montado com sucesso! Avance para a Etapa 6."

    except Exception as e:
        print(f"Ocorreu um erro durante a montagem: {e}")
        return False, f"Ocorreu um erro durante a montagem: {e}"
"""

# ==================================================================
# ETAPA 6
# ==================================================================

def salvar_trilhas_upload(arquivos):
    """Salva os ficheiros de áudio enviados pelo formulário."""
    os.makedirs(PASTA_TRILHA_SONORA, exist_ok=True)
    for arquivo in arquivos:
        if arquivo and arquivo.filename != '':
            nome_seguro = secure_filename(arquivo.filename)
            caminho_salvar = os.path.join(PASTA_TRILHA_SONORA, nome_seguro)
            arquivo.save(caminho_salvar)
    return True



# VERSÃO ATUALIZADA DA FUNÇÃO DE ADICIONAR TRILHA
def adicionar_trilha_sonora(nomes_trilhas, volume=0.15):
    """
    Adiciona uma ou mais trilhas sonoras em loop ao vídeo já montado.
    """
    status = verificar_status()
    video_sem_trilha = status['video_sem_trilha']

    if not video_sem_trilha:
        return False, "ERRO: Nenhum vídeo base montado foi encontrado."
    if not nomes_trilhas:
        return False, "ERRO: Nenhuma trilha sonora foi selecionada para a mixagem."

    try:
        caminho_video = os.path.join(PASTA_VIDEO_SEM_TRILHA, video_sem_trilha)
        video_clip = mp.VideoFileClip(caminho_video)

        # Carrega todos os clips de áudio selecionados
        clips_trilha = [mp.AudioFileClip(os.path.join(PASTA_TRILHA_SONORA, nome)) for nome in nomes_trilhas]
        
        # Concatena os clips de áudio em uma única trilha longa
        trilha_completa = mp.concatenate_audioclips(clips_trilha)
        
        # Faz o loop da trilha completa pela duração do vídeo
        trilha_em_loop = afx.audio_loop(trilha_completa, duration=video_clip.duration)
        trilha_volume_baixo = trilha_em_loop.volumex(volume)

        audio_narracao = video_clip.audio
        audio_final_mixado = mp.CompositeAudioClip([audio_narracao, trilha_volume_baixo])
        video_com_trilha = video_clip.set_audio(audio_final_mixado)

        os.makedirs(PASTA_VIDEO_FINAL, exist_ok=True)
        for f in os.listdir(PASTA_VIDEO_FINAL):
            os.remove(os.path.join(PASTA_VIDEO_FINAL, f))

        caminho_saida = os.path.join(PASTA_VIDEO_FINAL, "video_final_com_trilha.mp4")
        video_com_trilha.write_videofile(caminho_saida, fps=30, codec="libx264")

        return True, "Trilha sonora adicionada com sucesso! O vídeo final está pronto."

    except Exception as e:
        print(f"Ocorreu um erro ao adicionar a trilha sonora: {e}")
        return False, f"Ocorreu um erro ao adicionar a trilha sonora: {e}"

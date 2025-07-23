# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import helpers
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (como a SECRET_KEY)
load_dotenv()

app = Flask(__name__)
# Carrega a chave secreta do ambiente, que foi carregada do .env
app.secret_key = os.getenv('SECRET_KEY') 

@app.route('/')
def index():
    """Página inicial que funciona como um painel de controle."""
    status = helpers.verificar_status()
    return render_template('index.html', status=status)

@app.route('/etapa1', methods=['GET', 'POST'])
def etapa1_transcricao():
    """Página para inserir o nome da novela e a transcrição."""
    status = helpers.verificar_status()
    
    if request.method == 'POST':
        nome_novela = request.form.get('nome_novela')
        conteudo_transcricao = request.form.get('conteudo_transcricao')
        
        if nome_novela and conteudo_transcricao:
            sucesso, mensagem = helpers.gerar_transcricao(nome_novela, conteudo_transcricao)
            flash(mensagem)
            if sucesso:
                return redirect(url_for('etapa2_roteiro'))
        else:
            flash("Por favor, preencha ambos os campos.")
    
    return render_template('etapa1_transcricao.html', status=status)


# VERSÃO ÚNICA E CORRETA DA ROTA DE EXCLUSÃO
@app.route('/excluir/<string:etapa>', methods=['POST'])
def excluir(etapa):
    """Rota aprimorada para excluir todos os arquivos ou apenas os selecionados."""
    action = request.form.get('action')

    if action == 'delete_all':
        helpers.excluir_arquivo(etapa)
        flash(f"Todos os arquivos da etapa '{etapa}' foram excluídos.")
    elif action == 'delete_selected':
        arquivos_para_excluir = request.form.getlist('arquivos_selecionados')
        if arquivos_para_excluir:
            helpers.excluir_arquivo(etapa, arquivos_especificos=arquivos_para_excluir)
            flash(f"{len(arquivos_para_excluir)} arquivo(s) selecionado(s) da etapa '{etapa}' foram excluídos.")
        else:
            flash("Nenhum arquivo foi selecionado para exclusão.")
    
    # Retorna o usuário para a página de onde ele veio
    return redirect(request.referrer or url_for('index'))






@app.route('/etapa2', methods=['GET', 'POST'])
def etapa2_roteiro():
    status = helpers.verificar_status()
    if not status['transcricao']:
        flash("Você precisa concluir a Etapa 1 primeiro!")
        return redirect(url_for('etapa1_transcricao'))
    if request.method == 'POST':
        sucesso, mensagem = helpers.gerar_roteiro()
        flash(mensagem)
        if sucesso:
            return redirect(url_for('etapa3_narracao')) # Redireciona para a próxima etapa
    return render_template('etapa2_roteiro.html', status=status)

# Aqui adicionaremos as outras rotas (etapa3, etc.) no futuro.

# --- Rota da Etapa 3 (Versão Única e Correta) ---
@app.route('/etapa3', methods=['GET', 'POST'])
def etapa3_narracao():
    status = helpers.verificar_status()

    if not status['roteiro']:
        flash("Você precisa concluir a Etapa 2 (Roteiro) primeiro!")
        return redirect(url_for('etapa2_roteiro'))

    if request.method == 'POST':
        voice_selection = request.form.get('voice_selection')
        if not voice_selection:
            flash("ERRO: Nenhuma voz foi selecionada.")
            return redirect(url_for('etapa3_narracao'))

        print(f"Iniciando a geração da narração com a voz {voice_selection}...")
        sucesso, mensagem = helpers.gerar_narracao(voice_selection)
        flash(mensagem)
        if sucesso:
            return redirect(url_for('etapa4_videos_base'))
        else:
            return redirect(url_for('etapa3_narracao'))

    # Para a requisição GET, busca a lista de vozes para mostrar no formulário
    vozes = helpers.listar_vozes()
    return render_template('etapa3_narracao.html', status=status, vozes=vozes)


# --- ETAPA 4 ---
@app.route('/etapa4', methods=['GET', 'POST'])
def etapa4_videos_base():
    status = helpers.verificar_status()
    if not status['narracao']:
        flash("Você precisa concluir a Etapa 3 (Narração) primeiro!")
        return redirect(url_for('etapa3_narracao'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'upload':
            arquivos = request.files.getlist('novas_imagens')
            nomes_salvos = helpers.salvar_imagens_upload(arquivos)
            flash(f"{len(nomes_salvos)} imagens foram salvas com sucesso.")
        elif action == 'renomear':
            sucesso, mensagem = helpers.renomear_imagens_em_ordem()
            flash(mensagem)
        # NOVA AÇÃO ADICIONADA
        elif action == 'redimensionar':
            sucesso, mensagem = helpers.redimensionar_imagens()
            flash(mensagem)
        elif action == 'gerar_videos':
            sucesso, mensagem = helpers.gerar_videos_base()
            flash(mensagem)
        return redirect(url_for('etapa4_videos_base'))
        
    return render_template('etapa4_videos_base.html', status=status)



# ROTA DA ETAPA 5 QUE ESTAVA FALTANDO
@app.route('/etapa5', methods=['GET', 'POST'])
def etapa5_montagem_final():
    status = helpers.verificar_status()
    if not status['videos_base']:
        flash("Você precisa concluir a Etapa 4 (Geração de Vídeos Base) primeiro!")
        return redirect(url_for('etapa4_videos_base'))
    if request.method == 'POST':
        sucesso, mensagem = helpers.montar_video_final()
        flash(mensagem)
        return redirect(url_for('etapa5_montagem_final'))
    return render_template('etapa5_montagem_final.html', status=status)


# ---ROTA ETAPA 6 ---
@app.route('/etapa6', methods=['GET', 'POST'])
def etapa6_pos_video():
    status = helpers.verificar_status()

    if not status['video_sem_trilha']:
        flash("Você precisa concluir a Etapa 5 (Montagem do Vídeo) primeiro!")
        return redirect(url_for('etapa5_montagem_final'))

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'upload_trilha':
            arquivos = request.files.getlist('novas_trilhas')
            helpers.salvar_trilhas_upload(arquivos)
            flash(f"{len(arquivos)} nova(s) trilha(s) sonora(s) enviada(s).")

        elif action == 'mixar_video':
            trilhas_selecionadas = request.form.getlist('trilhas_selecionadas')
            sucesso, mensagem = helpers.adicionar_trilha_sonora(trilhas_selecionadas)
            flash(mensagem)

        return redirect(url_for('etapa6_pos_video'))

    return render_template('etapa6_pos_video.html', status=status)


# Rota para servir as imagens da pasta 'imagens'
@app.route('/imagens/<filename>')
def serve_image(filename):
    return send_from_directory('imagens', filename)


# ROTA VIDEO FINAL
@app.route('/video_final/<filename>')
def serve_final_video(filename):
    return send_from_directory('video_final', filename)




if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080, debug=True)

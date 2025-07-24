# app.py
from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash, send_from_directory
import helpers
import os
from dotenv import load_dotenv
from celery_config import celery
from tasks import adicionar_trilha_sonora_task, gerar_videos_base_task, montar_video_final_task

# Carrega as variáveis de ambiente do arquivo .env (como a SECRET_KEY)
load_dotenv()

app = Flask(__name__)
# Carrega a chave secreta do ambiente, que foi carregada do .env
app.secret_key = os.getenv('SECRET_KEY') 


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY_TAREFA')

# VERIFICAÇÃO DE SEGURANÇA: Garante que a chave secreta foi definida.
if not app.secret_key:
    raise ValueError("Nenhuma SECRET_KEY definida! Por favor, crie um ficheiro .env com uma SECRET_KEY.")


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
        sucesso, mensagem = helpers.gerar_narracao_por_partes(voice_selection)
        flash(mensagem)
        if sucesso:
            return redirect(url_for('etapa3_1juntar_audios'))
        else:
            return redirect(url_for('etapa3_narracao'))

    # Para a requisição GET, busca a lista de vozes para mostrar no formulário
    vozes = helpers.listar_vozes()
    return render_template('etapa3_narracao.html', status=status, vozes=vozes)



# NOVA ROTA PARA A ETAPA 3.1
@app.route('/etapa3_1', methods=['GET', 'POST'])
def etapa3_1_juntar_audios():
    status = helpers.verificar_status()
    if not status['narracao_partes']:
        flash("Você precisa concluir a Etapa 3 (Gerar Áudios) primeiro!")
        return redirect(url_for('etapa3_narracao'))
    if request.method == 'POST':
        audios_selecionados = request.form.getlist('audios_selecionados')
        sucesso, mensagem = helpers.juntar_audios(audios_selecionados)
        flash(mensagem)
        if sucesso:
            return redirect(url_for('etapa4_videos_base'))
    # CORREÇÃO DO NOME DO FICHEIRO AQUI
    return render_template('etapa3_1juntar_audios.html', status=status)


# --- ETAPA 4 ---

@app.route('/etapa4', methods=['GET', 'POST'])
def etapa4_videos_base():
    status = helpers.verificar_status()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'gerar_videos':
            # Inicia a tarefa e guarda o seu ID na sessão do utilizador
            task = gerar_videos_base_task.delay()
            session['current_task_id'] = task.id
            session['current_task_name'] = 'Geração de Vídeos Base (Etapa 4)'
            flash("Pedido de geração de vídeos base enviado!")
            return redirect(url_for('monitor')) # Redireciona para o painel de monitorização
        # ... (outras ações da etapa 4) ...
        return redirect(url_for('etapa4_videos_base'))
    return render_template('etapa4_videos_base.html', status=status)

@app.route('/etapa5', methods=['GET', 'POST'])
def etapa5_montagem_final():
    status = helpers.verificar_status()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'montar_video':
            task = montar_video_final_task.delay()
            session['current_task_id'] = task.id
            session['current_task_name'] = 'Montagem Final (Etapa 5)'
            flash("Pedido de montagem final enviado!")
            return redirect(url_for('monitor'))
        return redirect(url_for('etapa5_montagem_final'))
    return render_template('etapa5_montagem_final.html', status=status)

# --- Rotas de Monitorização ---

@app.route('/monitor')
def monitor():
    """Página que mostra a tarefa ativa."""
    task_id = session.get('current_task_id')
    task_name = session.get('current_task_name', 'Tarefa')
    return render_template('monitor.html', task_id=task_id, task_name=task_name)

@app.route('/task_status/<task_id>')
def task_status(task_id):
    """Endpoint para o JavaScript obter o estado de uma tarefa específica."""
    task = celery.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Pendente...'}
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'info': task.info or {'status': 'A iniciar...'}, # Garante que 'info' nunca é nulo
        }
    else: # A tarefa falhou
        response = {
            'state': task.state,
            'info': {'status': str(task.info)}, # Converte a exceção em texto
        }
    return jsonify(response)





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
            adicionar_trilha_sonora_task.delay(trilhas_selecionadas)

        
            flash("Pedido de montagem com trilha sonora enviado! A página irá atualizar.")

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


# NOVA ROTA PARA DOWNLOAD DO ROTEIRO
@app.route('/download_roteiro')
def download_roteiro():
    status = helpers.verificar_status()
    if status['roteiro']:
        return send_from_directory(helpers.PASTA_ROTEIRO, status['roteiro'], as_attachment=True)
    return redirect(url_for('index'))



# ROTA GENÉRICA QUE ESTAVA EM FALTA
@app.route('/data/<path:filepath>')
def serve_data_file(filepath):
    """Serve ficheiros de todas as pastas de dados (imagens, narracao_partes, etc.)."""
    return send_from_directory('.', filepath)



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080, debug=True)

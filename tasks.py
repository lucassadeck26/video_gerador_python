# tasks.py
import helpers
from celery_config import celery

@celery.task(bind=True)
def gerar_videos_base_task(self):
    print("WORKER: A processar pedido para gerar vídeos base...")
    print("WORKER: Geração de vídeos base concluída.")
    return helpers.gerar_videos_base(self)
   



@celery.task
def montar_video_final_task(self):
    print("WORKER: A processar pedido para gerar o video completo montado...")
    print("WORKER: video completo base finalizado.")
    return helpers.montar_video_final(self)
 


@celery.task
def adicionar_trilha_sonora_task(trilhas_selecionadas,self):
    print("WORKER: A processar pedido para gerar o video completo montado...")
    print("WORKER: video completo base finalizado.")
    return helpers.adicionar_trilha_sonora(trilhas_selecionadas,self)
    
# Adicione aqui as outras tarefas pesadas (montar_video_final, etc.)
import os
from celery import Celery
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (como a REDIS_URL)
load_dotenv()

# Cria e configura a instância central do Celery.
celery = Celery(
    'tasks',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    # A MUDANÇA ESTÁ AQUI:
    # Esta linha diz ao Celery para procurar por tarefas no ficheiro 'tasks.py'.
    include=['tasks']
)

# Configurações de compatibilidade
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',)
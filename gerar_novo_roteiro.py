# gerar_novo_roteiro.py (VERSÃO CORRETA PARA LER O ARQUIVO .env)
import os
from dotenv import load_dotenv  # ESTA LINHA É IMPORTANTE
import google.generativeai as genai
import subprocess
# ==================================================================
# ESTA PARTE É A MAIS IMPORTANTE
# Ela diz ao Python para ler o seu arquivo .env e carregar as variáveis
load_dotenv()
# ==================================================================

# --- CONFIGURAÇÃO ---
PASTA_TRANSCRICAO = "transcricao"
PASTA_ROTEIROS = "roteiro_narracao"

# --- LÓGICA DO SCRIPT ---

print(f"Verificando a pasta '{PASTA_TRANSCRICAO}' por arquivos de transcrição...")

if not os.path.isdir(PASTA_TRANSCRICAO):
    print(f"ERRO: A pasta '{PASTA_TRANSCRICAO}' não foi encontrada.")
    exit()

arquivos_txt = [f for f in os.listdir(PASTA_TRANSCRICAO) if f.endswith(".txt")]

if not arquivos_txt:
    print(f"ERRO: A pasta '{PASTA_TRANSCRICAO}' está vazia.")
    exit()

NOME_ARQUIVO_TRANSCRICAO = arquivos_txt[0]
print(f"--> Transcrição encontrada: '{NOME_ARQUIVO_TRANSCRICAO}'. Usando este arquivo.")

# 1. Configurar a API Key que foi carregada pelo load_dotenv()
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        # Se mesmo assim não encontrar, o problema pode ser o arquivo .env não estar na pasta certa
        raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi encontrada! Verifique se o arquivo .env está na mesma pasta que o script.")
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"ERRO: Problema na configuração da API Key. {e}")
    exit()

# 2. Ler o arquivo de transcrição
caminho_transcricao = os.path.join(PASTA_TRANSCRICAO, NOME_ARQUIVO_TRANSCRICAO)
with open(caminho_transcricao, "r", encoding="utf-8") as f:
    conteudo_transcricao = f.read()
print(f"Arquivo de transcrição lido com sucesso.")

# 3. Montar o Prompt Final
prompt_template = f"""
Por favor, crie um texto sobre "Novela Gabriela " com as seguintes características:

- Público-alvo: Fãs da novela Gabriela
- Estilo de escrita: informal
- Humor: leve
- Tamanho: 2500 palavras
- Tonalidade: descontraída
- Objetivo: informar
- Referências a considerar: você é uma fã de carteirinha da novela gabriela, reescreva o resumo a seguir, separado por virgula, acrescente detalhes, torne a história original e cativante, deixando o texto o mais real possível, quero ctas naturais, para ser narrada por uma mulher. lembrando que é em espanhol o idioma. pergunte de onde a pessoa está assistindo, gere engajamento para a rede social: 

{conteudo_transcricao}

- Não inclua títulos ou subtítulos, apenas o texto do conteúdo.

O texto deve ser bem estruturado, coerente e adaptado ao público-alvo especificado. Utilize um vocabulário apropriado e mantenha o tom, estilo e humor consistentes ao longo do texto. Inclua exemplos relevantes ou dados que suportem o conteúdo, se apropriado. O objetivo principal do texto é informar o público-alvo.
"""

# 4. Enviar o prompt para a Gemini
print("Conectando à IA da Gemini e enviando o prompt...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt_template)
    roteiro_gerado = response.text
    print("Roteiro recebido da IA com sucesso!")
except Exception as e:
    print(f"ERRO ao gerar conteúdo com a API da Gemini: {e}")
    exit()

# 5. Salvar o roteiro gerado
os.makedirs(PASTA_ROTEIROS, exist_ok=True)
nome_base_arquivo, _ = os.path.splitext(NOME_ARQUIVO_TRANSCRICAO)
nome_arquivo_roteiro = f"roteiro_{nome_base_arquivo}.txt"
caminho_saida_roteiro = os.path.join(PASTA_ROTEIROS, nome_arquivo_roteiro)
with open(caminho_saida_roteiro, "w", encoding="utf-8") as f:
    f.write(roteiro_gerado)

print(f"\nRoteiro final salvo com sucesso em: '{caminho_saida_roteiro}'")

# Chamar o próximo script da cadeia
print("\n----------------------------------------------------")
print(f"SUCESSO: Roteiro gerado. Passando para a geração de áudio...")
print("----------------------------------------------------")
subprocess.run(["python", "gerador_audio.py"], check=True)

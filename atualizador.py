import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# 1. INICIALIZAÇÃO DO FIREBASE
try:
    firebase_cert = json.loads(os.environ.get('FIREBASE_JSON'))
    cred = credentials.Certificate(firebase_cert)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print("Aviso Firebase:", e)

# 2. DICIONÁRIO DE TRADUÇÃO (BBC -> BOLÃO)
DICIONARIO = {
    'Brazil': 'Brasil', 'South Africa': 'Africa do Sul', 'Germany': 'Alemanha',
    'Saudi Arabia': 'Arabia Saudita', 'Algeria': 'Argelia', 'South Korea': 'Coreia do Sul',
    'Ivory Coast': 'Costa do Marfim', 'Croatia': 'Croacia', 'Egypt': 'Egito',
    'Ecuador': 'Equador', 'Scotland': 'Escocia', 'Spain': 'Espanha',
    'United States': 'Estados Unidos', 'France': 'Franca', 'Netherlands': 'Holanda',
    'England': 'Inglaterra', 'Iran': 'Irã', 'Japan': 'Japao', 'Morocco': 'Marrocos',
    'Mexico': 'Mexico', 'Norway': 'Noruega', 'New Zealand': 'Nova Zelandia',
    'Paraguay': 'Paraguai', 'DR Congo': 'RD Congo', 'Czech Republic': 'Rep Tcheca',
    'Czechia': 'Rep Tcheca', 'Sweden': 'Suecia', 'Switzerland': 'Suica', 
    'Turkey': 'Turquia', 'Uruguay': 'Uruguai', 'Senegal': 'Senegal'
}

def traduzir(nome_ingles):
    return DICIONARIO.get(nome_ingles.strip(), nome_ingles.strip())

# 3. MATEMÁTICA DO RELÓGIO
hoje = datetime.utcnow()
ontem = hoje - timedelta(days=1)

datas_alvo = [
    ontem.strftime('%Y-%m-%d'),
    hoje.strftime('%Y-%m-%d')
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

resultados_extraidos = {}

# 4. A RASPAGEM BLINDADA
for data in datas_alvo:
    url = f"https://www.bbc.com/sport/football/scores-fixtures/{data}"
    resposta = requests.get(url, headers=headers)
    
    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        # Ignora os códigos malucos e busca apenas a raiz da classe
        jogos = soup.find_all('li', class_=lambda c: c and 'HeadToHeadWrapper' in c) 
        
        for jogo in jogos:
            try:
                # Isola os blocos de casa e fora
                time_casa_bloco = jogo.find('div', class_=lambda c: c and 'TeamHome' in c)
                time_fora_bloco = jogo.find('div', class_=lambda c: c and 'TeamAway' in c)

                # Extrai os nomes
                time_casa_en = time_casa_bloco.find('span', class_=lambda c: c and 'DesktopValue' in c).text.strip()
                time_fora_en = time_fora_bloco.find('span', class_=lambda c: c and 'DesktopValue' in c).text.strip()
                
                # Extrai os gols
                placar_casa = jogo.find('div', class_=lambda c: c and 'HomeScore' in c).text.strip()
                placar_fora = jogo.find('div', class_=lambda c: c and 'AwayScore' in c).text.strip()
                
                # Traduz
                time_casa_br = traduzir(time_casa_en)
                time_fora_br = traduzir(time_fora_en)
                
                # Monta a chave combinada (ex: "Franca_Senegal") ou conforme o seu padrão
                chave = f"{time_casa_br}_{time_fora_br}"
                resultados_extraidos[chave] = {
                    "home": placar_casa,
                    "away": placar_fora
                }
                
                print(f"Lido da BBC: {time_casa_br} {placar_casa} x {placar_fora} {time_fora_br}")
                
            except Exception as e:
                # Se for um jogo que ainda não começou, as classes de gol não existem. O robô ignora e segue a vida.
                continue

print("--------------------------------------------------")
print(f"Total de jogos processados e com placar: {len(resultados_extraidos)}")

# =====================================================================
# 5. GRAVAÇÃO NO FIREBASE
# =====================================================================
if resultados_extraidos:
    print("Iniciando gravação no banco de dados...")
    
    # -> COLE AQUI O SEU CÓDIGO ANTIGO QUE GRAVAVA NO FIREBASE <-
    # Geralmente é algo na linha de:
    # doc_ref = db.collection('resultados').document('oficiais')
    # doc_ref.set(resultados_extraidos, merge=True)
    
    print("Atualização concluída com sucesso.")
else:
    print("Nenhum placar para atualizar no momento.")

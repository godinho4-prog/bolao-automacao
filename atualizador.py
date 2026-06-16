import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# 1. INICIALIZAÇÃO DO FIREBASE
firebase_cert = json.loads(os.environ.get('FIREBASE_JSON'))
cred = credentials.Certificate(firebase_cert)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. DICIONÁRIO DE TRADUÇÃO (BBC -> BOLÃO)
# Atenção: Adicione as demais seleções seguindo exatamente as letras maiúsculas/minúsculas do seu index.html
DICIONARIO = {
    'Brazil': 'Brasil', 'South Africa': 'Africa do Sul', 'Germany': 'Alemanha',
    'Saudi Arabia': 'Arabia Saudita', 'Algeria': 'Argelia', 'South Korea': 'Coreia do Sul',
    'Ivory Coast': 'Costa do Marfim', 'Croatia': 'Croacia', 'Egypt': 'Egito',
    'Ecuador': 'Equador', 'Scotland': 'Escocia', 'Spain': 'Espanha',
    'United States': 'Estados Unidos', 'France': 'Franca', 'Netherlands': 'Holanda',
    'England': 'Inglaterra', 'Iran': 'Irã', 'Japan': 'Japao', 'Morocco': 'Marrocos',
    'Mexico': 'Mexico', 'Norway': 'Noruega', 'New Zealand': 'Nova Zelandia',
    'Paraguay': 'Paraguai', 'DR Congo': 'RD Congo', 'Czech Republic': 'Rep Tcheca',
    'Czechia': 'Rep Tcheca', # A BBC pode usar essa variação
    'Sweden': 'Suecia', 'Switzerland': 'Suica', 'Turkey': 'Turquia', 'Uruguay': 'Uruguai'
}

def traduzir(nome_ingles):
    return DICIONARIO.get(nome_ingles.strip(), nome_ingles.strip())

# 3. MATEMÁTICA DO RELÓGIO (ONTEM E HOJE)
hoje = datetime.utcnow()
ontem = hoje - timedelta(days=1)

datas_alvo = [
    ontem.strftime('%Y-%m-%d'),
    hoje.strftime('%Y-%m-%d')
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

novos_resultados = {}

# 4. A RASPAGEM
for data in datas_alvo:
    url = f"https://www.bbc.com/sport/football/scores-fixtures/{data}"
    resposta = requests.get(url, headers=headers)
    
    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        # --- ATENÇÃO: ZONA CEGA ---
        # A BBC mudou a estrutura HTML recentemente. 
        # Precisamos inspecionar a página e substituir 'nome-da-classe-do-jogo'
        # pelas classes reais que eles estão usando hoje para as partidas, times e placares.
        
        jogos = soup.find_all('article', class_='nome-da-classe-do-jogo') 
        
        for jogo in jogos:
            try:
                time_casa_en = jogo.find('span', class_='classe-time-casa').text
                time_fora_en = jogo.find('span', class_='classe-time-fora').text
                placar_casa = jogo.find('span', class_='classe-gol-casa').text
                placar_fora = jogo.find('span', class_='classe-gol-fora').text
                
                time_casa_br = traduzir(time_casa_en)
                time_fora_br = traduzir(time_fora_en)
                
                # A lógica de enviar para o Firebase vai aqui após identificarmos o HTML
                print(f"Lido: {time_casa_br} {placar_casa} x {placar_fora} {time_fora_br}")
                
            except Exception as e:
                continue

print("Varredura finalizada.")

import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# 1. INICIALIZAÇÃO DO FIREBASE E DO BANCO DE DADOS
firebase_cert = json.loads(os.environ.get('FIREBASE_JSON'))
cred = credentials.Certificate(firebase_cert)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. DICIONÁRIOS DE TRADUÇÃO E FILTROS (BBC -> BOLÃO)
DICIONARIO_SELECOES = {
    'Brazil': 'Brasil', 'South Africa': 'Africa do Sul', 'Germany': 'Alemanha',
    'Saudi Arabia': 'Arabia Saudita', 'Algeria': 'Argelia', 'South Korea': 'Coreia do Sul',
    'Ivory Coast': 'Costa do Marfim', 'Croatia': 'Croacia', 'Egypt': 'Egito',
    'Ecuador': 'Equador', 'Scotland': 'Escocia', 'Spain': 'Espanha',
    'United States': 'Estados Unidos', 'USA': 'Estados Unidos', 'France': 'Franca',
    'Netherlands': 'Holanda', 'England': 'Inglaterra', 'Iran': 'Irã',
    'Japan': 'Japao', 'Morocco': 'Marrocos', 'Mexico': 'Mexico',
    'Norway': 'Noruega', 'New Zealand': 'Nova Zelandia', 'Paraguay': 'Paraguai',
    'DR Congo': 'RD Congo', 'Democratic Republic of Congo': 'RD Congo',
    'Czech Republic': 'Rep Tcheca', 'Czechia': 'Rep Tcheca',
    'Sweden': 'Suecia', 'Switzerland': 'Suica', 'Turkey': 'Turquia', 'Uruguai': 'Uruguai',
    'Uruguay': 'Uruguai', 'Belgium': 'Belgica', 'Cape Verde': 'Cabo Verde', 
    'Tunisia': 'Tunisia', 'Argentina': 'Argentina', 'Australia': 'Australia', 
    'Austria': 'Austria', 'Bosnia': 'Bosnia', 'Bosnia and Herzegovina': 'Bosnia', 
    'Canada': 'Canada', 'Qatar': 'Catar', 'Colombia': 'Colombia', 'Curacao': 'Curacau',
    'Ghana': 'Gana', 'Haiti': 'Haiti', 'Iraq': 'Iraque', 'Jordan': 'Jordania',
    'Panama': 'Panama', 'Portugal': 'Portugal', 'Senegal': 'Senegal',
    'Uzbekistan': 'Uzbequistao'
}

DICIONARIO_ARTILHEIROS = {
    'E. Haaland': 'Haaland', 'Erling Haaland': 'Haaland', 'Haaland': 'Haaland',
    'K. Mbappe': 'Mbappé', 'K. Mbappé': 'Mbappé', 'Kylian Mbappe': 'Mbappé', 'Kylian Mbappé': 'Mbappé',
    'H. Kane': 'Kane', 'Harry Kane': 'Kane', 'Kane': 'Kane',
    'C. Ronaldo': 'Cristiano Ronaldo', 'Cristiano Ronaldo': 'Cristiano Ronaldo', 'Ronaldo': 'Cristiano Ronaldo'
}

# Filtro estrito: O robô vai ignorar qualquer jogador que não esteja nesta lista
ALVOS_BOLAO = ['Haaland', 'Mbappé', 'Kane', 'Cristiano Ronaldo']

def traduzir_selecao(nome_ingles):
    return DICIONARIO_SELECOES.get(nome_ingles.strip(), nome_ingles.strip())
    
def traduzir_jogador(nome_ingles):
    return DICIONARIO_ARTILHEIROS.get(nome_ingles.strip(), nome_ingles.strip())

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# ==========================================
# MOTOR 1: RASPAGEM DOS PLACARES DOS JOGOS
# ==========================================
hoje = datetime.utcnow()
ontem = hoje - timedelta(days=1)

datas_alvo = [
    ontem.strftime('%Y-%m-%d'),
    hoje.strftime('%Y-%m-%d')
]

resultados_capturados = []

print("--- INICIANDO VARREDURA DE PLACARES ---")
for data in datas_alvo:
    url_jogos = f"https://www.bbc.com/sport/football/scores-fixtures/{data}"
    resposta = requests.get(url_jogos, headers=headers)
    resposta.encoding = 'utf-8'  # Força a leitura correta de acentos
    
    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text, 'html.parser')
        jogos = soup.find_all('li', class_='ssrcss-18nzily-HeadToHeadWrapper') 
        
        for jogo in jogos:
            try:
                bloco_casa = jogo.find('div', class_='ssrcss-bon2fo-WithInlineFallback-TeamHome')
                bloco_fora = jogo.find('div', class_='ssrcss-nvj22c-WithInlineFallback-TeamAway')
                
                time_casa_en = bloco_casa.find('span', class_='ssrcss-1p14tic-DesktopValue').text.strip()
                time_fora_en = bloco_fora.find('span', class_='ssrcss-1p14tic-DesktopValue').text.strip()
                
                placar_casa_tag = jogo.find('div', class_='ssrcss-qsbptj-HomeScore')
                placar_fora_tag = jogo.find('div', class_='ssrcss-fri5a2-AwayScore')
                
                if not placar_casa_tag or not placar_fora_tag or placar_casa_tag.text.strip() == '':
                    continue
                    
                placar_casa = placar_casa_tag.text.strip()
                placar_fora = placar_fora_tag.text.strip()
                
                time_casa_br = traduzir_selecao(time_casa_en)
                time_fora_br = traduzir_selecao(time_fora_en)
                
                print(f"Jogo: {time_casa_br} {placar_casa} x {placar_fora} {time_fora_br}")
                
                resultados_capturados.append({
                    'home': time_

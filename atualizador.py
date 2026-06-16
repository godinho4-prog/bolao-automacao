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

# 2. DICIONÁRIO COMPLETO DE TRADUÇÃO (BBC -> BOLÃO)
DICIONARIO = {
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
    'Sweden': 'Suecia', 'Switzerland': 'Suica', 'Turkey': 'Turquia', 'Uruguay': 'Uruguai',
    'Belgium': 'Belgica', 'Cape Verde': 'Cabo Verde', 'Tunisia': 'Tunisia',
    'Argentina': 'Argentina', 'Australia': 'Australia', 'Austria': 'Austria',
    'Bosnia': 'Bosnia', 'Bosnia and Herzegovina': 'Bosnia', 'Canada': 'Canada',
    'Qatar': 'Catar', 'Colombia': 'Colombia', 'Curacao': 'Curacau',
    'Ghana': 'Gana', 'Haiti': 'Haiti', 'Iraq': 'Iraque', 'Jordan': 'Jordania',
    'Panama': 'Panama', 'Portugal': 'Portugal', 'Senegal': 'Senegal',
    'Uzbekistan': 'Uzbequistao'
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

resultados_capturados = []

# 4. A RASPAGEM DA BBC
for data in datas_alvo:
    url = f"https://www.bbc.com/sport/football/scores-fixtures/{data}"
    resposta = requests.get(url, headers=headers)
    
    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        # --- ATENÇÃO ---
        # Insere aqui a tua lógica exata de busca (find_all) que testaste e funcionou.
        jogos = soup.find_all('article', class_='INSERE_A_CLASSE_AQUI') 
        
        for jogo in jogos:
            try:
                # Insere as variáveis de extração de equipas e golos aqui
                time_casa_en = jogo.find('span', class_='CLASSE_CASA').text
                time_fora_en = jogo.find('span', class_='CLASSE_FORA').text
                placar_casa = jogo.find('span', class_='GOLO_CASA').text
                placar_fora = jogo.find('span', class_='GOLO_FORA').text
                
                time_casa_br = traduzir(time_casa_en)
                time_fora_br = traduzir(time_fora_en)
                
                print(f"Lido da BBC: {time_casa_br} {placar_casa} x {placar_fora} {time_fora_br}")
                
                resultados_capturados.append({
                    'home': time_casa_br,
                    'away': time_fora_br,
                    'score_home': placar_casa,
                    'score_away': placar_fora
                })
                
            except Exception as e:
                continue

print("-" * 50)
print(f"Total de jogos processados e com placar: {len(resultados_capturados)}")

# 5. GRAVAÇÃO NA BASE DE DADOS
if resultados_capturados:
    print("Iniciando gravação no banco de dados...")
    
    # --- ATENÇÃO ---
    # Insere aqui a tua rotina de gravação no Firebase que fez o cruzamento 
    # dos resultados com o ID dos jogos.
    
    print("Atualização concluída com sucesso.")

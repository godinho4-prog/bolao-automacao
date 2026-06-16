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
    'Sweden': 'Suecia', 'Switzerland': 'Suica', 'Turkey': 'Turquia', 'Uruguai': 'Uruguai',
    'Uruguay': 'Uruguai', 'Belgium': 'Belgica', 'Cape Verde': 'Cabo Verde', 
    'Tunisia': 'Tunisia', 'Argentina': 'Argentina', 'Australia': 'Australia', 
    'Austria': 'Austria', 'Bosnia': 'Bosnia', 'Bosnia and Herzegovina': 'Bosnia', 
    'Canada': 'Canada', 'Qatar': 'Catar', 'Colombia': 'Colombia', 'Curacao': 'Curacau',
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

# 4. A RASPAGEM DA BBC COM AS CLASSES EXATAS DO HTML
for data in datas_alvo:
    url = f"https://www.bbc.com/sport/football/scores-fixtures/{data}"
    resposta = requests.get(url, headers=headers)
    
    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        # Encontra todos os blocos de jogos
        jogos = soup.find_all('li', class_='ssrcss-18nzily-HeadToHeadWrapper') 
        
        for jogo in jogos:
            try:
                # Isola os blocos do time da casa e time de fora
                bloco_casa = jogo.find('div', class_='ssrcss-bon2fo-WithInlineFallback-TeamHome')
                bloco_fora = jogo.find('div', class_='ssrcss-nvj22c-WithInlineFallback-TeamAway')
                
                # Extrai os nomes no formato Desktop
                time_casa_en = bloco_casa.find('span', class_='ssrcss-1p14tic-DesktopValue').text.strip()
                time_fora_en = bloco_fora.find('span', class_='ssrcss-1p14tic-DesktopValue').text.strip()
                
                # Extrai os gols
                placar_casa_tag = jogo.find('div', class_='ssrcss-qsbptj-HomeScore')
                placar_fora_tag = jogo.find('div', class_='ssrcss-fri5a2-AwayScore')
                
                # Se a tag do placar não existir ou estiver vazia, o jogo não começou
                if not placar_casa_tag or not placar_fora_tag or placar_casa_tag.text.strip() == '':
                    continue
                    
                placar_casa = placar_casa_tag.text.strip()
                placar_fora = placar_fora_tag.text.strip()
                
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

# 5. GRAVAÇÃO NO FIREBASE
if resultados_capturados:
    print("Iniciando gravação no banco de dados...")
    
    # Busca a tabela de jogos no Firebase para cruzar os IDs
    resultados_ref = db.collection('config').doc('results')
    
    # Simula a lista de jogos do seu index.html para fazer o "match" do ID
    # (O script precisa saber o ID do jogo para não bagunçar o seu bolão)
    # Como o script roda isolado, a forma mais segura é baixar o documento inteiro, 
    # e nós atualizaremos as chaves (ex: "49") com os novos placares.
    # Nota: No seu app, os nomes estão em BR.
    
    # Para blindar, nós pegamos o documento atual de resultados
    doc_results = resultados_ref.get()
    banco_atual = doc_results.to_dict() if doc_results.exists else {}
    
    # Array espelho do seu index.html com as equipes para acharmos o ID
    # O Python vai procurar a partida "Franca x Senegal" na lista abaixo para achar o ID 49
    GAMES_LIST = [
        {"id": 1, "home": "Mexico", "away": "Africa do Sul"}, {"id": 2, "home": "Coreia do Sul", "away": "Rep Tcheca"},
        {"id": 3, "home": "Rep Tcheca", "away": "Africa do Sul"}, {"id": 4, "home": "Coreia do Sul", "away": "Mexico"},
        {"id": 5, "home": "Rep Tcheca", "away": "Mexico"}, {"id": 6, "home": "Africa do Sul", "away": "Coreia do Sul"},
        {"id": 7, "home": "Canada", "away": "Bosnia"}, {"id": 8, "home": "Catar", "away": "Suica"},
        {"id": 9, "home": "Suica", "away": "Bosnia"}, {"id": 10, "home": "Catar", "away": "Canada"},
        {"id": 11, "home": "Suica", "away": "Canada"}, {"id": 12, "home": "Bosnia", "away": "Catar"},
        {"id": 13, "home": "Brasil", "away": "Marrocos"}, {"id": 14, "home": "Haiti", "away": "Escocia"},
        {"id": 15, "home": "Marrocos", "away": "Escocia"}, {"id": 16, "home": "Haiti", "away": "Brasil"},
        {"id": 17, "home": "Marrocos", "away": "Haiti"}, {"id": 18, "home": "Escocia", "away": "Brasil"},
        {"id": 19, "home": "Estados Unidos", "away": "Paraguai"}, {"id": 20, "home": "Australia", "away": "Turquia"},
        {"id": 21, "home": "Australia", "away": "Estados Unidos"}, {"id": 22, "home": "Paraguai", "away": "Turquia"},
        {"id": 23, "home": "Paraguai", "away": "Australia"}, {"id": 24, "home": "Turquia", "away": "Estados Unidos"},
        {"id": 25, "home": "Alemanha", "away": "Curacau"}, {"id": 26, "home": "Costa do Marfim", "away": "Equador"},
        {"id": 27, "home": "Costa do Marfim", "away": "Alemanha"}, {"id": 28, "home": "Equador", "away": "Curacau"},
        {"id": 29, "home": "Equador", "away": "Alemanha"}, {"id": 30, "home": "Curacau", "away": "Costa do Marfim"},
        {"id": 31, "home": "Holanda", "away": "Japao"}, {"id": 32, "home": "Suecia", "away": "Tunisia"},
        {"id": 33, "home": "Suecia", "away": "Holanda"}, {"id": 34, "home": "Japao", "away": "Tunisia"},
        {"id": 35, "home": "Tunisia", "away": "Holanda"}, {"id": 36, "home": "Japao", "away": "Suecia"},
        {"id": 37, "home": "Belgica", "away": "Egito"}, {"id": 38, "home": "Irã", "away": "Nova Zelandia"},
        {"id": 39, "home": "Belgica", "away": "Irã"}, {"id": 40, "home": "Nova Zelandia", "away": "Egito"},
        {"id": 41, "home": "Egito", "away": "Irã"}, {"id": 42, "home": "Nova Zelandia", "away": "Belgica"},
        {"id": 43, "home": "Espanha", "away": "Cabo Verde"}, {"id": 44, "home": "Arabia Saudita", "away": "Uruguai"},
        {"id": 45, "home": "Espanha", "away": "Arabia Saudita"}, {"id": 46, "home": "Uruguai", "away": "Cabo Verde"},
        {"id": 47, "home": "Uruguai", "away": "Espanha"}, {"id": 48, "home": "Cabo Verde", "away": "Arabia Saudita"},
        {"id": 49, "home": "Franca", "away": "Senegal"}, {"id": 50, "home": "Iraque", "away": "Noruega"},
        {"id": 51, "home": "Franca", "away": "Iraque"}, {"id": 52, "home": "Noruega", "away": "Senegal"},
        {"id": 53, "home": "Noruega", "away": "Franca"}, {"id": 54, "home": "Senegal", "away": "Iraque"},
        {"id": 55, "home": "Argentina", "away": "Argelia"}, {"id": 56, "home": "Austria", "away": "Jordania"},
        {"id": 57, "home": "Jordania", "away": "Argelia"}, {"id": 58, "home": "Argentina", "away": "Austria"},
        {"id": 59, "home": "Argelia", "away": "Austria"}, {"id": 60, "home": "Jordania", "away": "Argentina"},
        {"id": 61, "home": "Portugal", "away": "RD Congo"}, {"id": 62, "home": "Uzbequistao", "away": "Colombia"},
        {"id": 63, "home": "Portugal", "away": "Uzbequistao"}, {"id": 64, "home": "Colombia", "away": "RD Congo"},
        {"id": 65, "home": "Colombia", "away": "Portugal"}, {"id": 66, "home": "RD Congo", "away": "Uzbequistao"},
        {"id": 67, "home": "Inglaterra", "away": "Croacia"}, {"id": 68, "home": "Gana", "away": "Panama"},
        {"id": 69, "home": "Inglaterra", "away": "Gana"}, {"id": 70, "home": "Panama", "away": "Croacia"},
        {"id": 71, "home": "Panama", "away": "Inglaterra"}, {"id": 72, "home": "Gana", "away": "Croacia"}
    ]
    
    atualizacoes = {}
    
    for cap in resultados_capturados:
        # Tenta achar o ID do jogo batendo os times
        jogo_encontrado = next((g for g in GAMES_LIST if g['home'] == cap['home'] and g['away'] == cap['away']), None)
        
        if jogo_encontrado:
            id_str = str(jogo_encontrado['id'])
            atualizacoes[id_str] = {
                'home': cap['score_home'],
                'away': cap['score_away']
            }
            
    if atualizacoes:
        resultados_ref.set(atualizacoes, merge=True)
        print(f"{len(atualizacoes)} placares atualizados no Firebase.")
    else:
        print("Nenhum jogo capturado pertence à lista oficial da fase de grupos.")
        
    print("Atualização concluída com sucesso.")

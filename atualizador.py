import os
import json
import requests
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Conectar ao Firebase usando o segredo do cofre
firebase_cert = json.loads(os.environ.get('FIREBASE_JSON'))
cred = credentials.Certificate(firebase_cert)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. Configurar a chamada para a API-Football
API_KEY = os.environ.get('API_KEY')
headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

# 3. Dicionário de Tradução (Inglês da API -> Seu Padrão)
TRADUCAO = {
    "South Africa": "Africa do Sul", "Germany": "Alemanha", "Saudi Arabia": "Arabia Saudita",
    "Algeria": "Argelia", "Argentina": "Argentina", "Australia": "Australia", "Austria": "Austria",
    "Belgium": "Belgica", "Bosnia": "Bosnia", "Brazil": "Brasil", "Cape Verde": "Cabo Verde",
    "Canada": "Canada", "Qatar": "Catar", "Colombia": "Colombia", "South Korea": "Coreia do Sul",
    "Ivory Coast": "Costa do Marfim", "Croatia": "Croacia", "Curacao": "Curacau", "Egypt": "Egito",
    "Ecuador": "Equador", "Scotland": "Escocia", "Spain": "Espanha", "USA": "Estados Unidos",
    "France": "Franca", "Ghana": "Gana", "Haiti": "Haiti", "Netherlands": "Holanda",
    "England": "Inglaterra", "Iran": "Irã", "Iraq": "Iraque", "Japan": "Japao", "Jordan": "Jordania",
    "Morocco": "Marrocos", "Mexico": "Mexico", "Norway": "Noruega", "New Zealand": "Nova Zelandia",
    "Panama": "Panama", "Paraguay": "Paraguai", "Portugal": "Portugal", "DR Congo": "RD Congo",
    "Czech Republic": "Rep Tcheca", "Senegal": "Senegal", "Sweden": "Suecia", "Switzerland": "Suica",
    "Tunisia": "Tunisia", "Turkey": "Turquia", "Uruguay": "Uruguai", "Uzbekistan": "Uzbequistao"
}

# 4. Mapeamento dos Jogos (Seu Time Casa x Seu Time Fora -> ID do Jogo)
JOGOS_IDS = {
    "Mexico x Africa do Sul": "1", "Coreia do Sul x Rep Tcheca": "2", "Rep Tcheca x Africa do Sul": "3", "Coreia do Sul x Mexico": "4", "Rep Tcheca x Mexico": "5", "Africa do Sul x Coreia do Sul": "6",
    "Canada x Bosnia": "7", "Catar x Suica": "8", "Suica x Bosnia": "9", "Catar x Canada": "10", "Suica x Canada": "11", "Bosnia x Catar": "12",
    "Brasil x Marrocos": "13", "Haiti x Escocia": "14", "Marrocos x Escocia": "15", "Haiti x Brasil": "16", "Marrocos x Haiti": "17", "Escocia x Brasil": "18",
    "Estados Unidos x Paraguai": "19", "Australia x Turquia": "20", "Australia x Estados Unidos": "21", "Paraguai x Turquia": "22", "Paraguai x Australia": "23", "Turquia x Estados Unidos": "24",
    "Alemanha x Curacau": "25", "Costa do Marfim x Equador": "26", "Costa do Marfim x Alemanha": "27", "Equador x Curacau": "28", "Equador x Alemanha": "29", "Curacau x Costa do Marfim": "30",
    "Holanda x Japao": "31", "Suecia x Tunisia": "32", "Suecia x Holanda": "33", "Japao x Tunisia": "34", "Tunisia x Holanda": "35", "Japao x Suecia": "36",
    "Belgica x Egito": "37", "Irã x Nova Zelandia": "38", "Belgica x Irã": "39", "Nova Zelandia x Egito": "40", "Egito x Irã": "41", "Nova Zelandia x Belgica": "42",
    "Espanha x Cabo Verde": "43", "Arabia Saudita x Uruguai": "44", "Espanha x Arabia Saudita": "45", "Uruguai x Cabo Verde": "46", "Uruguai x Espanha": "47", "Cabo Verde x Arabia Saudita": "48",
    "Franca x Senegal": "49", "Iraque x Noruega": "50", "Franca x Iraque": "51", "Noruega x Senegal": "52", "Noruega x Franca": "53", "Senegal x Iraque": "54",
    "Argentina x Argelia": "55", "Austria x Jordania": "56", "Jordania x Argelia": "57", "Argentina x Austria": "58", "Argelia x Austria": "59", "Jordania x Argentina": "60",
    "Portugal x RD Congo": "61", "Uzbequistao x Colombia": "62", "Portugal x Uzbequistao": "63", "Colombia x RD Congo": "64", "Colombia x Portugal": "65", "RD Congo x Uzbequistao": "66",
    "Inglaterra x Croacia": "67", "Gana x Panama": "68", "Inglaterra x Gana": "69", "Panama x Croacia": "70", "Panama x Inglaterra": "71", "Gana x Croacia": "72"
}

def atualizar_jogos():
    # Pega os jogos do dia (UTC-3)
    hoje = datetime.utcnow() - timedelta(hours=3)
    data_str = hoje.strftime('%Y-%m-%d')
    
    url = f"https://v3.football.api-sports.io/fixtures?date={data_str}&league=1&season=2026"
    resposta = requests.get(url, headers=headers)
    
    if resposta.status_code != 200:
        print("Erro ao acessar a API.")
        return

    dados = resposta.json()
    novos_resultados = {}

    for jogo in dados.get("response", []):
        status = jogo["fixture"]["status"]["short"]
        
        # FT = Full Time, AET = After Extra Time, PEN = Penalties
        if status in ["FT", "AET", "PEN"]:
            time_casa_api = jogo["teams"]["home"]["name"]
            time_fora_api = jogo["teams"]["away"]["name"]
            
            # Pega gols do tempo normal + prorrogação (ignora pênaltis)
            gols_casa = jogo["score"]["extratime"]["home"] if jogo["score"]["extratime"]["home"] is not None else jogo["goals"]["home"]
            gols_fora = jogo["score"]["extratime"]["away"] if jogo["score"]["extratime"]["away"] is not None else jogo["goals"]["away"]

            casa_traduzido = TRADUCAO.get(time_casa_api, time_casa_api)
            fora_traduzido = TRADUCAO.get(time_fora_api, time_fora_api)
            
            chave_jogo = f"{casa_traduzido} x {fora_traduzido}"
            jogo_id = JOGOS_IDS.get(chave_jogo)

            if jogo_id:
                novos_resultados[jogo_id] = {"home": gols_casa, "away": gols_fora}
                print(f"Resultado processado: {chave_jogo} ({gols_casa} x {gols_fora}) -> ID: {jogo_id}")

    # Grava tudo de uma vez no Firebase
    if novos_resultados:
        doc_ref = db.collection('config').doc('results')
        doc_ref.set(novos_resultados, merge=True)
        print("Banco de dados atualizado com sucesso!")
    else:
        print("Nenhum jogo finalizado precisando de atualização no momento.")

if __name__ == "__main__":
    atualizar_jogos()

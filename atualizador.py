import os
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Conectar ao Firebase
firebase_cert = json.loads(os.environ.get('FIREBASE_JSON'))
cred = credentials.Certificate(firebase_cert)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. Dicionário de Tradução Completo
TRADUCAO = {
    "South Africa": "Africa do Sul", "Germany": "Alemanha", "Saudi Arabia": "Arabia Saudita",
    "Algeria": "Argelia", "Argentina": "Argentina", "Australia": "Australia", "Austria": "Austria",
    "Belgium": "Belgica", "Bosnia and Herzegovina": "Bosnia", "Brazil": "Brasil", "Cape Verde": "Cabo Verde",
    "Canada": "Canada", "Qatar": "Catar", "Colombia": "Colombia", "South Korea": "Coreia do Sul", 
    "Côte d'Ivoire": "Costa do Marfim", "Ivory Coast": "Costa do Marfim", "Croatia": "Croacia", 
    "Curaçao": "Curacau", "Curacao": "Curacau", "Egypt": "Egito", "Ecuador": "Equador", 
    "Scotland": "Escocia", "Spain": "Espanha", "United States": "Estados Unidos", "USA": "Estados Unidos", 
    "France": "Franca", "Ghana": "Gana", "Haiti": "Haiti", "Netherlands": "Holanda",
    "England": "Inglaterra", "Iran": "Irã", "Iraq": "Iraque", "Japan": "Japao", "Jordan": "Jordania",
    "Morocco": "Marrocos", "Mexico": "Mexico", "Norway": "Noruega", "New Zealand": "Nova Zelandia",
    "Panama": "Panama", "Paraguay": "Paraguai", "Portugal": "Portugal", "DR Congo": "RD Congo",
    "Czech Republic": "Rep Tcheca", "Czechia": "Rep Tcheca", "Senegal": "Senegal", "Sweden": "Suecia", 
    "Switzerland": "Suica", "Tunisia": "Tunisia", "Turkey": "Turquia", "Uruguay": "Uruguai", "Uzbekistan": "Uzbequistao"
}

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
    # URL da API comunitária aberta para 2026
    url = "https://worldcup26.ir/api/v1/matches"
    
    try:
        # Adicionamos um timeout de segurança de 10s para o robô não ficar travado se o servidor deles cair
        resposta = requests.get(url, timeout=10)
        dados = resposta.json()
    except Exception as e:
        print("Erro crítico: Falha ao ler o sinal JSON da comunidade.", e)
        return

    novos_resultados = {}
    lista_jogos = dados.get("matches", []) if isinstance(dados, dict) else dados
    print(f"RADAR LIGADO: Lendo o sinal JSON. {len(lista_jogos)} jogos encontrados no pacote.")

    for jogo in lista_jogos:
        # A API envia status como 'IN_PLAY', 'FINISHED', 'SCHEDULED', etc.
        status_api = str(jogo.get("status", "")).upper()
        
        # Filtramos apenas os que já começaram ou já acabaram
        if status_api in ["IN_PLAY", "LIVE", "FINISHED", "COMPLETED"]:
            time_casa_api = jogo.get("homeTeam", {}).get("name", "")
            time_fora_api = jogo.get("awayTeam", {}).get("name", "")
            
            # Puxa o placar atual (mesmo vazio, tratamos o erro)
            try:
                gols_casa = int(jogo.get("score", {}).get("fullTime", {}).get("home", 0))
                gols_fora = int(jogo.get("score", {}).get("fullTime", {}).get("away", 0))
            except (ValueError, TypeError):
                gols_casa, gols_fora = 0, 0

            casa_traduzido = TRADUCAO.get(time_casa_api, time_casa_api)
            fora_traduzido = TRADUCAO.get(time_fora_api, time_fora_api)
            
            chave_jogo = f"{casa_traduzido} x {fora_traduzido}"
            jogo_id = JOGOS_IDS.get(chave_jogo)

            # Aqui é o pulo do gato: criamos a etiqueta para o seu front-end
            status_bolao = "FINALIZADO" if status_api in ["FINISHED", "COMPLETED"] else "AO_VIVO"

            if jogo_id:
                novos_resultados[jogo_id] = {
                    "home": gols_casa, 
                    "away": gols_fora,
                    "status": status_bolao
                }
                print(f"SUCESSO: {chave_jogo} ({gols_casa} x {gols_fora}) | Status: {status_bolao} | ID: {jogo_id}")

    if novos_resultados:
        try:
            doc_ref = db.collection('config').document('results')
            doc_ref.set(novos_resultados, merge=True)
            print("Operação concluída. Firebase atualizado de forma estruturada!")
        except Exception as e:
            print("Erro ao tentar gravar os dados no Firebase:", e)
    else:
        print("O radar não encontrou nenhum jogo finalizado ou em andamento na base.")

if __name__ == "__main__":
    atualizar_jogos()

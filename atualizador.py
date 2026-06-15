import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from googlesearch import search
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Conectar ao Firebase
firebase_cert = json.loads(os.environ.get('FIREBASE_JSON'))
cred = credentials.Certificate(firebase_cert)
firebase_admin.initialize_app(cred)
db = firestore.client()

TRADUCAO = { "South Africa": "Africa do Sul", "Germany": "Alemanha", "Saudi Arabia": "Arabia Saudita", "Algeria": "Argelia", "Argentina": "Argentina", "Australia": "Australia", "Austria": "Austria", "Belgium": "Belgica", "Bosnia and Herzegovina": "Bosnia", "Brazil": "Brasil", "Cape Verde": "Cabo Verde", "Canada": "Canada", "Qatar": "Catar", "Colombia": "Colombia", "South Korea": "Coreia do Sul", "Côte d'Ivoire": "Costa do Marfim", "Ivory Coast": "Costa do Marfim", "Croatia": "Croacia", "Curaçao": "Curacau", "Egypt": "Egito", "Ecuador": "Equador", "Scotland": "Escocia", "Spain": "Espanha", "United States": "Estados Unidos", "France": "Franca", "Ghana": "Gana", "Haiti": "Haiti", "Netherlands": "Holanda", "England": "Inglaterra", "Iran": "Irã", "Iraq": "Iraque", "Japan": "Japao", "Jordan": "Jordania", "Morocco": "Marrocos", "Mexico": "Mexico", "Norway": "Noruega", "New Zealand": "Nova Zelandia", "Panama": "Panama", "Paraguay": "Paraguai", "Portugal": "Portugal", "DR Congo": "RD Congo", "Czech Republic": "Rep Tcheca", "Senegal": "Senegal", "Sweden": "Suecia", "Switzerland": "Suica", "Tunisia": "Tunisia", "Turkey": "Turquia", "Uruguay": "Uruguai", "Uzbekistan": "Uzbequistao" }
JOGOS_IDS = { "Mexico x Africa do Sul": "1", "Coreia do Sul x Rep Tcheca": "2", "Rep Tcheca x Africa do Sul": "3", "Coreia do Sul x Mexico": "4", "Rep Tcheca x Mexico": "5", "Africa do Sul x Coreia do Sul": "6", "Canada x Bosnia": "7", "Catar x Suica": "8", "Suica x Bosnia": "9", "Catar x Canada": "10", "Suica x Canada": "11", "Bosnia x Catar": "12", "Brasil x Marrocos": "13", "Haiti x Escocia": "14", "Marrocos x Escocia": "15", "Haiti x Brasil": "16", "Marrocos x Haiti": "17", "Escocia x Brasil": "18", "Estados Unidos x Paraguai": "19", "Australia x Turquia": "20", "Australia x Estados Unidos": "21", "Paraguai x Turquia": "22", "Paraguai x Australia": "23", "Turquia x Estados Unidos": "24", "Alemanha x Curacau": "25", "Costa do Marfim x Equador": "26", "Costa do Marfim x Alemanha": "27", "Equador x Curacau": "28", "Equador x Alemanha": "29", "Curacau x Costa do Marfim": "30", "Holanda x Japao": "31", "Suecia x Tunisia": "32", "Suecia x Holanda": "33", "Japao x Tunisia": "34", "Tunisia x Holanda": "35", "Japao x Suecia": "36", "Belgica x Egito": "37", "Irã x Nova Zelandia": "38", "Belgica x Irã": "39", "Nova Zelandia x Egito": "40", "Egito x Irã": "41", "Nova Zelandia x Belgica": "42", "Espanha x Cabo Verde": "43", "Arabia Saudita x Uruguai": "44", "Espanha x Arabia Saudita": "45", "Uruguai x Cabo Verde": "46", "Uruguai x Espanha": "47", "Cabo Verde x Arabia Saudita": "48", "Franca x Senegal": "49", "Iraque x Noruega": "50", "Franca x Iraque": "51", "Noruega x Senegal": "52", "Noruega x Franca": "53", "Senegal x Iraque": "54", "Argentina x Argelia": "55", "Austria x Jordania": "56", "Jordania x Argelia": "57", "Argentina x Austria": "58", "Argelia x Austria": "59", "Jordania x Argentina": "60", "Portugal x RD Congo": "61", "Uzbequistao x Colombia": "62", "Portugal x Uzbequistao": "63", "Colombia x RD Congo": "64", "Colombia x Portugal": "65", "RD Congo x Uzbequistao": "66", "Inglaterra x Croacia": "67", "Gana x Panama": "68", "Inglaterra x Gana": "69", "Panama x Croacia": "70", "Panama x Inglaterra": "71", "Gana x Croacia": "72" }

def validar_status_oficial(casa, fora):
    query = f"{casa} vs {fora} score status"
    try:
        for result in search(query, num_results=1):
            r = requests.get(result, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            if any(x in r.text for x in ["Full Time", "Final", "Encerrado", "FT"]):
                return "FINALIZADO"
    except: pass
    return "AO_VIVO"

def atualizar_jogos():
    url = "https://native-stats.org/competition/WC/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        resposta = requests.get(url, headers=headers)
        soup = BeautifulSoup(resposta.text, 'html.parser')
        texto_puro = soup.get_text(separator=' | ', strip=True)
        partes = texto_puro.split(' | ')
    except Exception as e:
        print("Erro na raspagem:", e)
        return

    novos_resultados = {}
    ano = str(datetime.utcnow().year)

    for i, pedaco in enumerate(partes):
        if pedaco.startswith(ano + "/") and len(partes) > i + 8:
            casa = TRADUCAO.get(partes[i+1], partes[i+1])
            fora = TRADUCAO.get(partes[i+5], partes[i+5])
            placar = partes[i+8]
            
            if ":" in placar:
                jogo_id = JOGOS_IDS.get(f"{casa} x {fora}")
                if jogo_id:
                    status = validar_status_oficial(casa, fora)
                    novos_resultados[jogo_id] = {
                        "home": int(placar.split(":")[0].strip()),
                        "away": int(placar.split(":")[1].strip()),
                        "status": status
                    }
                    print(f"PROCESSADO: {casa} x {fora} | {placar} | Status: {status}")

    if novos_resultados:
        db.collection('config').document('results').set(novos_resultados, merge=True)

if __name__ == "__main__":
    atualizar_jogos()

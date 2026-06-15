import os
import json
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Conectar ao Firebase
firebase_cert = json.loads(os.environ.get('FIREBASE_JSON'))
cred = credentials.Certificate(firebase_cert)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. Dicionário de Tradução
TRADUCAO = {
    "South Africa": "Africa do Sul", "Germany": "Alemanha", "Saudi Arabia": "Arabia Saudita",
    "Algeria": "Argelia", "Argentina": "Argentina", "Australia": "Australia", "Austria": "Austria",
    "Belgium": "Belgica", "Bosnia and Herzegovina": "Bosnia", "Brazil": "Brasil", "Cape Verde": "Cabo Verde",
    "Cape Verde Islands": "Cabo Verde", "Canada": "Canada", "Qatar": "Catar", "Colombia": "Colombia", 
    "South Korea": "Coreia do Sul", "Côte d'Ivoire": "Costa do Marfim", "Ivory Coast": "Costa do Marfim", 
    "Croatia": "Croacia", "Curaçao": "Curacau", "Curacao": "Curacau", "Egypt": "Egito", "Ecuador": "Equador", 
    "Scotland": "Escocia", "Spain": "Espanha", "United States": "Estados Unidos", "USA": "Estados Unidos", 
    "France": "Franca", "Ghana": "Gana", "Haiti": "Haiti", "Netherlands": "Holanda",
    "England": "Inglaterra", "Iran": "Irã", "Iraq": "Iraque", "Japan": "Japao", "Jordan": "Jordania",
    "Morocco": "Marrocos", "Mexico": "Mexico", "Norway": "Noruega", "New Zealand": "Nova Zelandia",
    "Panama": "Panama", "Paraguay": "Paraguai", "Portugal": "Portugal", "DR Congo": "RD Congo",
    "Czech Republic": "Rep Tcheca", "Czechia": "Rep Tcheca", "Senegal": "Senegal", "Sweden": "Suecia", 
    "Switzerland": "Suica", "Tunisia": "Tunisia", "Turkey": "Turquia", "Uruguay": "Uruguai", "Uzbekistan": "Uzbequistao"
}

JOGOS_IDS = {
    "Espanha x Cabo Verde": "43", "Belgica x Egito": "37" # Reduzido para teste focado
}

def atualizar_jogos():
    url = "https://native-stats.org/competition/WC/"
    
    # Camuflagem para o site achar que somos um navegador normal e não bloquear a leitura
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("RADAR LIGADO: Acessando a página pública...")
    try:
        resposta = requests.get(url, headers=headers)
        soup = BeautifulSoup(resposta.text, 'html.parser')
    except Exception as e:
        print("Erro ao tentar raspar a página:", e)
        return

    # Vamos imprimir um pedaço cru da página no terminal para eu ver exatamente como eles montam o placar no HTML
    print("--- RAIO-X DA PÁGINA ---")
    texto_puro = soup.get_text(separator=' | ', strip=True)
    print(texto_puro[:1000]) # Imprime os primeiros 1000 caracteres
    print("------------------------")

if __name__ == "__main__":
    atualizar_jogos()

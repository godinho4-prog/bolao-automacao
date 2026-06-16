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

# 2. Dicionário de Tradução Completo
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

# 3. Mapeamento de todos os jogos do Bolão
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
    url = "https://native-stats.org/competition/WC/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        resposta = requests.get(url, headers=headers)
        soup = BeautifulSoup(resposta.text, 'html.parser')
    except Exception as e:
        print("Erro de rede ao tentar raspar a página:", e)
        return

    texto_puro = soup.get_text(separator=' | ', strip=True)
    partes = texto_puro.split(' | ')
    
    novos_resultados = {}

    # Varredura lógica: procura qualquer placar no formato X:Y e identifica os times ao redor
    for i, pedaco in enumerate(partes):
        placar_limpo = pedaco.strip()
        
        # Confirma se o pedaço é estritamente um placar (ex: "1:2")
        if ":" in placar_limpo and len(placar_limpo) <= 5 and placar_limpo.replace(":", "").isdigit():
            try:
                gols_casa, gols_fora = map(int, placar_limpo.split(":"))
            except ValueError:
                continue
                
            # Olha para os blocos anteriores para capturar os times
            casa = None
            fora = None
            
            # Varre até 10 posições para trás do placar procurando chaves válidas
            for j in range(max(0, i-10), i):
                candidato = partes[j].strip()
                time_traduzido = TRADUCAO.get(candidato, candidato)
                
                # Se o nome traduzido faz parte de algum jogo do nosso dicionário
                if any(time_traduzido in chave for chave in JOGOS_IDS.keys()):
                    if not casa:
                        casa = time_traduzido
                    elif not fora and time_traduzido != casa:
                        fora = time_traduzido
            
            if casa and fora:
                chave_jogo = f"{casa} x {fora}"
                jogo_id = JOGOS_IDS.get(chave_jogo)

                if jogo_id and jogo_id not in novos_resultados:
                    novos_resultados[jogo_id] = {"home": gols_casa, "away": gols_fora}
                    print(f"SUCESSO: {chave_jogo} ({gols_casa} x {gols_fora}) capturado por varredura. ID: {jogo_id}")

    if novos_resultados:
        try:
            doc_ref = db.collection('config').document('results')
            doc_ref.set(novos_resultados, merge=True)
            print("Operação concluída. O Firebase foi atualizado.")
        except Exception as e:
            print("Erro ao gravar os dados no Firebase:", e)
    else:
        print("Nenhum jogo encontrado na estrutura da página atual.")

if __name__ == "__main__":
    atualizar_jogos()

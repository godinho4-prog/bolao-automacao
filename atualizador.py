import requests
from bs4 import BeautifulSoup

url = "https://www.bbc.com/sport/football/scores-fixtures/2026-06-16"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
resposta = requests.get(url, headers=headers)

if resposta.status_code == 200:
    soup = BeautifulSoup(resposta.text, 'html.parser')
    
    # Procura especificamente o texto "France" na página de hoje
    tag_franca = soup.find(string=lambda t: t and 'France' in t)
    
    if tag_franca:
        # Pega a "caixa" principal que engloba o jogo inteiro (volta 5 níveis no HTML)
        caixa_do_jogo = tag_franca.parent.parent.parent.parent.parent
        print("ACHEI O CÓDIGO DA BBC! COPIE TUDO ABAIXO:")
        print("--------------------------------------------------")
        print(caixa_do_jogo.prettify())
        print("--------------------------------------------------")
    else:
        print("A palavra 'France' não foi encontrada. O site pode estar bloqueando a raspagem ou mudou de aba.")
else:
    print(f"Erro ao acessar a BBC. Código: {resposta.status_code}")

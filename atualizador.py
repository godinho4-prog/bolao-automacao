import requests
from bs4 import BeautifulSoup
import re

def raio_x_html():
    url = "https://native-stats.org/competition/WC/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resposta = requests.get(url, headers=headers)
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        print("RADAR HTML LIGADO: Caçando as tags do jogo do Uruguai...")
        
        # Busca qualquer texto que contenha 'Uruguay'
        textos_uruguai = soup.find_all(string=re.compile("Uruguay"))
        
        if textos_uruguai:
            # Pega o contêiner 'avô' para tentar englobar a linha inteira do placar
            container = textos_uruguai[0].parent.parent.parent.parent
            print("--- ESTRUTURA HTML CRUA ---")
            print(container.prettify()[:2000]) # Limita os caracteres para o log não travar
            print("---------------------------")
        else:
            print("Não achei a palavra 'Uruguay' no HTML recebido.")
            
    except Exception as e:
        print("Erro no Raio-X:", e)

if __name__ == "__main__":
    raio_x_html()

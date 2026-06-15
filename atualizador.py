import requests
from bs4 import BeautifulSoup
import re

def raio_x_placar():
    url = "https://native-stats.org/competition/WC/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resposta = requests.get(url, headers=headers)
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        print("RADAR LIGADO: Caçando a etiqueta visual exata dos placares...")
        
        # Caça qualquer pedaço de texto que seja puramente um placar (ex: "0:0", "1:2", "5:1")
        placares = soup.find_all(string=re.compile(r"^\s*\d+\s*:\s*\d+\s*$"))
        
        if placares:
            for p in placares:
                tag_pai = p.parent
                classes = tag_pai.get('class', ['Nenhuma_classe_encontrada'])
                print(f"Placar capturado: {p.strip()} -> Classes visuais: {classes}")
        else:
            print("Não achei os placares no HTML lido.")
            
    except Exception as e:
        print("Erro no Raio-X:", e)

if __name__ == "__main__":
    raio_x_placar()

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
        
        print("RADAR LIGADO: Lendo as cores dos placares...")
        
        # Puxa qualquer texto que seja número:número
        placares = soup.find_all(string=re.compile(r"^\s*\d+\s*:\s*\d+\s*$"))
        
        if placares:
            for p in placares:
                classes = p.parent.get('class', ['Sem_classe'])
                print(f"Placar capturado: {p.strip()} -> Roupa do HTML: {classes}")
        else:
            print("Não achei placares na tela.")
            
    except Exception as e:
        print("Erro no Raio-X:", e)

if __name__ == "__main__":
    raio_x_placar()

import os
import json
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# 1. INICIALIZAÇÃO DO FIREBASE E DO BANCO DE DADOS
firebase_cert = json.loads(os.environ.get('FIREBASE_JSON'))
cred = credentials.Certificate(firebase_cert)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. DICIONÁRIOS E FUNÇÕES DE SUPORTE
DICIONARIO_SELECOES = {
    'Brazil': 'Brasil', 'South Africa': 'Africa do Sul', 'Germany': 'Alemanha',
    'Saudi Arabia': 'Arabia Saudita', 'Algeria': 'Argelia', 'South Korea': 'Coreia do Sul',
    'Ivory Coast': 'Costa do Marfim', 'Croatia': 'Croacia', 'Egypt': 'Egito',
    'Ecuador': 'Equador', 'Scotland': 'Escocia', 'Spain': 'Espanha',
    'United States': 'Estados Unidos', 'USA': 'Estados Unidos', 'France': 'Franca',
    'Netherlands': 'Holanda', 'England': 'Inglaterra', 'Iran': 'Irã',
    'Japan': 'Japao', 'Morocco': 'Marrocos', 'Mexico': 'Mexico',
    'Norway': 'Noruega', 'New Zealand': 'Nova Zelandia', 'Paraguay': 'Paraguai',
    'DR Congo': 'RD Congo', 'Democratic Republic of Congo': 'RD Congo',
    'Congo DR': 'RD Congo', 'Congo RD': 'RD Congo', 'Congo': 'RD Congo',
    'Czech Republic': 'Rep Tcheca', 'Czechia': 'Rep Tcheca',
    'Sweden': 'Suecia', 'Switzerland': 'Suica', 'Turkey': 'Turquia', 'Uruguai': 'Uruguai',
    'Uruguay': 'Uruguai', 'Belgium': 'Belgica', 'Cape Verde': 'Cabo Verde', 
    'Tunisia': 'Tunisia', 'Argentina': 'Argentina', 'Australia': 'Australia', 
    'Austria': 'Austria', 'Bosnia': 'Bosnia', 'Bosnia-Herzegovina': 'Bosnia', 
    'Canada': 'Canada', 'Qatar': 'Catar', 'Colombia': 'Colombia', 'Curaçao': 'Curacau',
    'Ghana': 'Gana', 'Haiti': 'Haiti', 'Iraq': 'Iraque', 'Jordan': 'Jordania',
    'Panama': 'Panama', 'Portugal': 'Portugal', 'Senegal': 'Senegal',
    'Uzbekistan': 'Uzbequistao'
}

DICIONARIO_ARTILHEIROS = {
    'E. Haaland': 'Haaland', 'Erling Haaland': 'Haaland', 'Haaland': 'Haaland',
    'K. Mbappe': 'Mbappé', 'K. Mbappé': 'Mbappé', 'Kylian Mbappe': 'Mbappé', 'Kylian Mbappé': 'Mbappé',
    'H. Kane': 'Kane', 'Harry Kane': 'Kane', 'Kane': 'Kane',
    'C. Ronaldo': 'Cristiano Ronaldo', 'Cristiano Ronaldo': 'Cristiano Ronaldo', 'Ronaldo': 'Cristiano Ronaldo'
}

ALVOS_BOLAO = ['Haaland', 'Mbappé', 'Kane', 'Cristiano Ronaldo']

def traduzir_selecao(nome_ingles):
    return DICIONARIO_SELECOES.get(nome_ingles.strip(), nome_ingles.strip())
    
def traduzir_jogador(nome_ingles):
    return DICIONARIO_ARTILHEIROS.get(nome_ingles.strip(), nome_ingles.strip())

def get_progress_value(status_str):
    s = str(status_str).upper()
    if 'FT' in s or 'FULL' in s: return 999
    if 'AET' in s: return 998
    if 'PEN' in s: return 997
    if 'HT' in s or 'HALF' in s: return 45
    nums = re.findall(r'(\d+)', s)
    if nums: return int(nums[0])
    return 0

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
REQUEST_TIMEOUT = 15

def baixar_pagina(url, descricao):
    """Baixa uma página da BBC com timeout e logs legíveis."""
    try:
        resposta = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resposta.status_code != 200:
            print(f"❌ BBC respondeu {resposta.status_code} ao buscar {descricao}. URL: {url}")
            return None
        resposta.encoding = 'utf-8'
        return resposta
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout ao buscar {descricao} após {REQUEST_TIMEOUT}s. URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de rede ao buscar {descricao}: {type(e).__name__}: {e}. URL: {url}")
        return None


# ==========================================
# MOTOR 1: RASPAGEM DOS PLACARES DOS JOGOS
# ==========================================
hoje = datetime.utcnow()
ontem = hoje - timedelta(days=1)
amanha = hoje + timedelta(days=1)

# 🛠️ MÁQUINA DO TEMPO (TESTE DE PÊNALTIS) 🛠️
datas_alvo = [
    ontem.strftime('%Y-%m-%d'),
    hoje.strftime('%Y-%m-%d'),
    amanha.strftime('%Y-%m-%d')
]

resultados_capturados = []
paginas_ok = 0
blocos_de_jogo_encontrados = 0

print("--- INICIANDO VARREDURA DE PLACARES ---")
for data in datas_alvo:
    timestamp_agora = int(hoje.timestamp())
    url_jogos = f"https://www.bbc.com/sport/football/scores-fixtures/{data}?_={timestamp_agora}"
    resposta = baixar_pagina(url_jogos, f"placares BBC {data}")
    
    if resposta is None:
        continue

    paginas_ok += 1
    soup = BeautifulSoup(resposta.text, 'html.parser')
    jogos = soup.find_all('li', class_='ssrcss-18nzily-HeadToHeadWrapper')
    blocos_de_jogo_encontrados += len(jogos)
    
    print(f"📅 {data}: página OK, {len(jogos)} blocos de jogo encontrados.")
    if len(jogos) == 0:
        print(f"⚠️ Nenhum bloco de jogo encontrado em {data}. Se havia jogo nesse dia, a BBC pode ter mudado o HTML.")
    
    for jogo in jogos:
        try:
                bloco_casa = jogo.find('div', class_='ssrcss-bon2fo-WithInlineFallback-TeamHome')
                bloco_fora = jogo.find('div', class_='ssrcss-nvj22c-WithInlineFallback-TeamAway')
                
                if not bloco_casa or not bloco_fora:
                    continue
                
                time_casa_en = bloco_casa.find('span', class_='ssrcss-1p14tic-DesktopValue').text.strip()
                time_fora_en = bloco_fora.find('span', class_='ssrcss-1p14tic-DesktopValue').text.strip()
                
                placar_casa_tag = jogo.find('div', class_='ssrcss-qsbptj-HomeScore')
                placar_fora_tag = jogo.find('div', class_='ssrcss-fri5a2-AwayScore')
                
                if not placar_casa_tag or not placar_fora_tag or placar_casa_tag.text.strip() == '':
                    continue
                    
                placar_casa = placar_casa_tag.text.strip()
                placar_fora = placar_fora_tag.text.strip()
                
                time_casa_br = traduzir_selecao(time_casa_en)
                time_fora_br = traduzir_selecao(time_fora_en)
                
                # Busca status em múltiplas classes da BBC para não perder jogos finalizados em 0x0
                status_tag = jogo.find(class_=re.compile(r'(MatchProgressWrapper|MatchStatus|StatusWrapper)', re.I))
                status_texto = status_tag.text.strip().upper() if status_tag else ""
                
                                is_extra_time = False
                status_limpo = status_texto.strip().upper()
                
                if (
                    status_limpo == 'ET' or
                    status_limpo.startswith('ET ') or
                    any(x in status_limpo for x in ['AET', 'EXTRA', 'PENS', 'PENALTIES', 'SHOOTOUT'])
                ):
                    is_extra_time = True
                else:
                    tempos = re.findall(r'(\d+)', status_limpo)
                    for t in tempos:
                        if int(t) > 90:
                            is_extra_time = True
                            break
                            
                # --- NOVA LÓGICA: CAÇADOR DE PÊNALTIS CIRÚRGICO (VIA DATA-TESTID) ---
                pen_home = ""
                pen_away = ""
                
                pen_div = jogo.find('div', attrs={"data-testid": "penalties-text"})
                if pen_div:
                    texto_pen = pen_div.text.strip()
                    match_pens = re.search(r'(\d+)\s*-\s*(\d+)', texto_pen)
                    
                    if match_pens:
                        v1 = int(match_pens.group(1))
                        v2 = int(match_pens.group(2))
                        maior = str(max(v1, v2))
                        menor = str(min(v1, v2))
                        
                        span_vencedor = pen_div.find('span')
                        if span_vencedor:
                            vencedor_en = span_vencedor.text.strip()
                            vencedor_br = traduzir_selecao(vencedor_en)
                            
                            if vencedor_br == time_casa_br:
                                pen_home = maior
                                pen_away = menor
                            else:
                                pen_home = menor
                                pen_away = maior
                        else:
                            pen_home = str(v1)
                            pen_away = str(v2)
                            
                        print(f"🎯 Pênaltis capturados na agulha! Casa: {pen_home} x Fora: {pen_away}")

                print(f"Jogo: {time_casa_br} {placar_casa} x {placar_fora} {time_fora_br} | Status: {status_texto}")
                
                resultados_capturados.append({
                    'home': time_casa_br,
                    'away': time_fora_br,
                    'score_home': placar_casa,
                    'score_away': placar_fora,
                    'pen_home': pen_home,
                    'pen_away': pen_away,
                    'is_extra_time': is_extra_time,
                    'status': status_texto
                })
        except Exception as e:
            try:
                resumo_bloco = jogo.get_text(" ", strip=True)[:180]
            except Exception:
                resumo_bloco = "sem resumo disponível"
            print(f"⚠️ Erro ao processar um bloco de jogo em {data}: {type(e).__name__}: {e}. Trecho: {resumo_bloco}")
            continue

print(f"📊 Resumo da varredura de placares: {paginas_ok}/{len(datas_alvo)} páginas OK; {blocos_de_jogo_encontrados} blocos de jogo encontrados; {len(resultados_capturados)} jogos com placar capturados.")
if len(resultados_capturados) == 0:
    print("⚠️ Nenhum placar foi capturado. Se hoje/ontem/amanhã tem jogo da Copa, confira se a BBC mudou o layout ou se houve falha de rede.")

# ==========================================
# MOTOR 2: RASPAGEM DA ARTILHARIA
# ==========================================
print("\n--- INICIANDO VARREDURA DE ARTILHEIROS ---")
url_artilheiros = "https://www.bbc.com/sport/football/world-cup/top-scorers"
resposta_art = baixar_pagina(url_artilheiros, "artilharia BBC")

novos_artilheiros = {}

if resposta_art is not None:
    soup_art = BeautifulSoup(resposta_art.text, 'html.parser')
    nomes_html = soup_art.find_all('div', class_='ssrcss-13lnznp-PlayerName')
    print(f"🎯 Artilharia: {len(nomes_html)} nomes encontrados na página.")
    if len(nomes_html) == 0:
        print("⚠️ Nenhum nome encontrado na artilharia. A BBC pode ter mudado o HTML dessa página.")
    
    for nome_tag in nomes_html:
        nome_bbc = nome_tag.text.strip()
        nome_br = traduzir_jogador(nome_bbc)
        
        gols_tag = nome_tag.find_next('div', class_='ssrcss-nnhz1l-CellWrapper')
        
        if gols_tag:
            try:
                qtde_gols = int(gols_tag.text.strip())
                if nome_br in ALVOS_BOLAO and nome_br not in novos_artilheiros:
                    novos_artilheiros[nome_br] = qtde_gols
                    print(f"Artilheiro alvo lido: {nome_br} com {qtde_gols} gols")
            except ValueError:
                continue

# ==========================================
# GRAVAÇÃO NO FIREBASE
# ==========================================
print("\n--- GRAVANDO NO BANCO DE DADOS ---")

resultados_ref = db.collection('config').document('results')
doc_resultados = resultados_ref.get()
banco_resultados = doc_resultados.to_dict() if doc_resultados.exists else {}

# NOVIDADE: Puxa os times do Mata-Mata que já foram definidos no Admin
ko_ref = db.collection('config').document('ko_games')
doc_ko = ko_ref.get()
banco_ko = doc_ko.to_dict() if doc_ko.exists else {}

if resultados_capturados:
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
        {"id": 71, "home": "Panama", "away": "Inglaterra"}, {"id": 72, "home": "Gana", "away": "Croacia"},
    ]
    
    # INJEÇÃO DO MATA-MATA: Adiciona os jogos na lista de rastreio se o Admin já tiver definido os times!
    for ko_id, ko_data in banco_ko.items():
        if ko_data.get('home') and ko_data.get('away'):
            GAMES_LIST.append({
                "id": int(ko_id),
                "home": ko_data.get('home'),
                "away": ko_data.get('away')
            })
    
    atualizacoes_placares = {}
    for cap in resultados_capturados:
        jogo_encontrado = next((g for g in GAMES_LIST if g['home'] == cap['home'] and g['away'] == cap['away']), None)
        invertido = False
        
        if not jogo_encontrado:
            jogo_encontrado = next((g for g in GAMES_LIST if g['home'] == cap['away'] and g['away'] == cap['home']), None)
            if jogo_encontrado:
                invertido = True

        if jogo_encontrado:
            game_id_str = str(jogo_encontrado['id'])
            
            jogo_no_banco = banco_resultados.get(game_id_str, {})
            # AQUI A GENTE NÃO DÁ MAIS 'CONTINUE'. O SCRIPT CONTINUA LENDO ATÉ O JUIZ IR PRO CHUVEIRO.
                
            if invertido:
                placar_home = cap['score_away']
                placar_away = cap['score_home']
                placar_pen_home = cap.get('pen_away', '')
                placar_pen_away = cap.get('pen_home', '')
            else:
                placar_home = cap['score_home']
                placar_away = cap['score_away']
                placar_pen_home = cap.get('pen_home', '')
                placar_pen_away = cap.get('pen_away', '')

            # 🛡️ BLINDAGEM ANTI-CDN (Efeito Sanfona) 🛡️
            status_novo = cap.get('status', '')
            status_banco = jogo_no_banco.get('status', '')
            
            progresso_novo = get_progress_value(status_novo)
            progresso_banco = get_progress_value(status_banco)
            
            if progresso_novo > 0 and progresso_banco > 0:
                if progresso_novo < progresso_banco:
                    print(f"⚠️ CDN Desatualizado: Ignorando {cap['home']} no tempo {status_novo} (Banco ja tem {status_banco})")
                    continue
                
                if progresso_novo == progresso_banco:
                    try:
                        # Lê os gols do Live para não ser enganado quando a prorrogação começar
                        db_h = int(jogo_no_banco.get('home_live', jogo_no_banco.get('home', 0)) or 0)
                        db_a = int(jogo_no_banco.get('away_live', jogo_no_banco.get('away', 0)) or 0)
                        novo_h = int(placar_home)
                        novo_a = int(placar_away)
                        if (novo_h + novo_a) < (db_h + db_a):
                            print(f"⚠️ CDN Desatualizado: Ignorando reducao de gols {novo_h}x{novo_a} no mesmo minuto.")
                            continue
                    except ValueError:
                        pass

            # O placar VISUAL recebe as atualizações até o apito final absoluto
            payload = {
                'home_live': placar_home,
                'away_live': placar_away,
                'status': status_novo
            }

            # INJEÇÃO DOS PÊNALTIS NO BANCO
            if placar_pen_home and placar_pen_away:
                payload['home_pen'] = placar_pen_home
                payload['away_pen'] = placar_pen_away
            
            ja_travado = jogo_no_banco.get('locked_90', False)

            if not ja_travado:
                # Enquanto não chegar na prorrogação, a matemática acompanha o visual
                payload['home'] = placar_home
                payload['away'] = placar_away

                # O raspador detectou AET ou +90 min
                if cap['is_extra_time']:
                    payload['locked_90'] = True
                    print(f"🔒 GUILHOTINA DESCIDA: Pontos do bolão trancados em {placar_home}x{placar_away}.")
            
            # LÓGICA DOS 15 MINUTOS: Carimba a hora exata da morte da partida
            if any(x in status_novo for x in ['FT', 'FULL', 'AET', 'PEN', 'PENS', 'SHOOTOUT']):
                if 'finished_at' in jogo_no_banco:
                    payload['finished_at'] = jogo_no_banco['finished_at']
                else:
                    payload['finished_at'] = datetime.utcnow().isoformat() + 'Z'
                    print(f"⏱️ FIM DE JOGO DETECTADO: Iniciando 15 min de tolerância na tela.")
                    
            atualizacoes_placares[game_id_str] = payload
            
    if atualizacoes_placares:
        resultados_ref.set(atualizacoes_placares, merge=True)
        print(f"-> {len(atualizacoes_placares)} placares atualizados ou travados.")
    else:
        print("ℹ️ Nenhum placar capturado bateu com a lista de jogos do bolão. Pode ser normal em dia sem jogo relevante; se havia jogo, confira nomes/traduções/confrontos.")

if novos_artilheiros:
    admin_ref = db.collection('config').document('admin_data')
    doc_admin = admin_ref.get()
    banco_admin = doc_admin.to_dict() if doc_admin.exists else {}
    scorers_atuais = banco_admin.get('scorers', {})
    
    for jogador, gols in novos_artilheiros.items():
        if jogador not in scorers_atuais:
            scorers_atuais[jogador] = {'goals': gols, 'isTop': False}
        else:
            scorers_atuais[jogador]['goals'] = gols
            
    admin_ref.set({'scorers': scorers_atuais}, merge=True)
    print(f"-> {len(novos_artilheiros)} artilheiros processados.")

print("\nExecução 100% Finalizada.")

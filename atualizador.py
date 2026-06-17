import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializa o Firebase usando a sua variável de ambiente atual
firebase_cert = json.loads(os.environ.get('FIREBASE_JSON'))
cred = credentials.Certificate(firebase_cert)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# A lista completa com os 72 jogos estruturados
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
    {"id": 71, "home": "Panama", "away": "Inglaterra"}, {"id": 72, "home": "Gana", "away": "Croacia"}
]

print("Enviando lista para o Firestore...")
db.collection('config').document('games').set({'games_list': GAMES_LIST})
print("Sucesso! Documento 'config/games' criado com as 72 partidas.")

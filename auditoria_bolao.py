import os
import csv
import argparse
import json
import firebase_admin
from firebase_admin import credentials, firestore


CAMPOS_CSV = [
    "Participante",
    "UID",
    "Tipo",
    "Fase",
    "Evento ID",
    "Evento",
    "Palpite",
    "Resultado",
    "Regra",
    "Pontos",
]


GAMES_LIST = [
    {"id": 1, "home": "Mexico", "away": "Africa do Sul", "group": "A"},
    {"id": 2, "home": "Coreia do Sul", "away": "Rep Tcheca", "group": "A"},
    {"id": 3, "home": "Rep Tcheca", "away": "Africa do Sul", "group": "A"},
    {"id": 4, "home": "Coreia do Sul", "away": "Mexico", "group": "A"},
    {"id": 5, "home": "Rep Tcheca", "away": "Mexico", "group": "A"},
    {"id": 6, "home": "Africa do Sul", "away": "Coreia do Sul", "group": "A"},

    {"id": 7, "home": "Canada", "away": "Bosnia", "group": "B"},
    {"id": 8, "home": "Catar", "away": "Suica", "group": "B"},
    {"id": 9, "home": "Suica", "away": "Bosnia", "group": "B"},
    {"id": 10, "home": "Catar", "away": "Canada", "group": "B"},
    {"id": 11, "home": "Suica", "away": "Canada", "group": "B"},
    {"id": 12, "home": "Bosnia", "away": "Catar", "group": "B"},

    {"id": 13, "home": "Brasil", "away": "Marrocos", "group": "C"},
    {"id": 14, "home": "Haiti", "away": "Escocia", "group": "C"},
    {"id": 15, "home": "Marrocos", "away": "Escocia", "group": "C"},
    {"id": 16, "home": "Haiti", "away": "Brasil", "group": "C"},
    {"id": 17, "home": "Marrocos", "away": "Haiti", "group": "C"},
    {"id": 18, "home": "Escocia", "away": "Brasil", "group": "C"},

    {"id": 19, "home": "Estados Unidos", "away": "Paraguai", "group": "D"},
    {"id": 20, "home": "Australia", "away": "Turquia", "group": "D"},
    {"id": 21, "home": "Australia", "away": "Estados Unidos", "group": "D"},
    {"id": 22, "home": "Paraguai", "away": "Turquia", "group": "D"},
    {"id": 23, "home": "Paraguai", "away": "Australia", "group": "D"},
    {"id": 24, "home": "Turquia", "away": "Estados Unidos", "group": "D"},

    {"id": 25, "home": "Alemanha", "away": "Curacau", "group": "E"},
    {"id": 26, "home": "Costa do Marfim", "away": "Equador", "group": "E"},
    {"id": 27, "home": "Costa do Marfim", "away": "Alemanha", "group": "E"},
    {"id": 28, "home": "Equador", "away": "Curacau", "group": "E"},
    {"id": 29, "home": "Equador", "away": "Alemanha", "group": "E"},
    {"id": 30, "home": "Curacau", "away": "Costa do Marfim", "group": "E"},

    {"id": 31, "home": "Holanda", "away": "Japao", "group": "F"},
    {"id": 32, "home": "Suecia", "away": "Tunisia", "group": "F"},
    {"id": 33, "home": "Suecia", "away": "Holanda", "group": "F"},
    {"id": 34, "home": "Japao", "away": "Tunisia", "group": "F"},
    {"id": 35, "home": "Tunisia", "away": "Holanda", "group": "F"},
    {"id": 36, "home": "Japao", "away": "Suecia", "group": "F"},

    {"id": 37, "home": "Belgica", "away": "Egito", "group": "G"},
    {"id": 38, "home": "Irã", "away": "Nova Zelandia", "group": "G"},
    {"id": 39, "home": "Belgica", "away": "Irã", "group": "G"},
    {"id": 40, "home": "Nova Zelandia", "away": "Egito", "group": "G"},
    {"id": 41, "home": "Egito", "away": "Irã", "group": "G"},
    {"id": 42, "home": "Nova Zelandia", "away": "Belgica", "group": "G"},

    {"id": 43, "home": "Espanha", "away": "Cabo Verde", "group": "H"},
    {"id": 44, "home": "Arabia Saudita", "away": "Uruguai", "group": "H"},
    {"id": 45, "home": "Espanha", "away": "Arabia Saudita", "group": "H"},
    {"id": 46, "home": "Uruguai", "away": "Cabo Verde", "group": "H"},
    {"id": 47, "home": "Uruguai", "away": "Espanha", "group": "H"},
    {"id": 48, "home": "Cabo Verde", "away": "Arabia Saudita", "group": "H"},

    {"id": 49, "home": "Franca", "away": "Senegal", "group": "I"},
    {"id": 50, "home": "Iraque", "away": "Noruega", "group": "I"},
    {"id": 51, "home": "Franca", "away": "Iraque", "group": "I"},
    {"id": 52, "home": "Noruega", "away": "Senegal", "group": "I"},
    {"id": 53, "home": "Noruega", "away": "Franca", "group": "I"},
    {"id": 54, "home": "Senegal", "away": "Iraque", "group": "I"},

    {"id": 55, "home": "Argentina", "away": "Argelia", "group": "J"},
    {"id": 56, "home": "Austria", "away": "Jordania", "group": "J"},
    {"id": 57, "home": "Jordania", "away": "Argelia", "group": "J"},
    {"id": 58, "home": "Argentina", "away": "Austria", "group": "J"},
    {"id": 59, "home": "Argelia", "away": "Austria", "group": "J"},
    {"id": 60, "home": "Jordania", "away": "Argentina", "group": "J"},

    {"id": 61, "home": "Portugal", "away": "RD Congo", "group": "K"},
    {"id": 62, "home": "Uzbequistao", "away": "Colombia", "group": "K"},
    {"id": 63, "home": "Portugal", "away": "Uzbequistao", "group": "K"},
    {"id": 64, "home": "Colombia", "away": "RD Congo", "group": "K"},
    {"id": 65, "home": "Colombia", "away": "Portugal", "group": "K"},
    {"id": 66, "home": "RD Congo", "away": "Uzbequistao", "group": "K"},

    {"id": 67, "home": "Inglaterra", "away": "Croacia", "group": "L"},
    {"id": 68, "home": "Gana", "away": "Panama", "group": "L"},
    {"id": 69, "home": "Inglaterra", "away": "Gana", "group": "L"},
    {"id": 70, "home": "Panama", "away": "Croacia", "group": "L"},
    {"id": 71, "home": "Panama", "away": "Inglaterra", "group": "L"},
    {"id": 72, "home": "Gana", "away": "Croacia", "group": "L"},
]


def parse_score(v):
    if v is None or v == "":
        return None
    return int(v)


def phase_label(game):
    g = str(game.get("group", "")).lower()
    if "16 avos" in g:
        return "16 Avos"
    if "oitavas" in g:
        return "Oitavas"
    if "quartas" in g:
        return "Quartas"
    if "semi" in g:
        return "Semifinais"
    if "terceiro" in g:
        return "3º Lugar"
    if "final" in g:
        return "Final"
    return "Grupos"


def phase_points(phase):
    p = str(phase).upper()

    if "16 AVOS" in p:
        return {"exact": 12, "win_saldo": 8, "win_gol_perd": 7, "win": 6, "draw": 8}
    if "OITAVAS" in p:
        return {"exact": 14, "win_saldo": 10, "win_gol_perd": 8, "win": 7, "draw": 10}
    if "QUARTAS" in p:
        return {"exact": 16, "win_saldo": 11, "win_gol_perd": 10, "win": 8, "draw": 11}
    if "SEMI" in p or "TERCEIRO" in p:
        return {"exact": 20, "win_saldo": 14, "win_gol_perd": 12, "win": 10, "draw": 14}
    if "FINAL" in p:
        return {"exact": 24, "win_saldo": 17, "win_gol_perd": 14, "win": 12, "draw": 17}

    return {"exact": 10, "win_saldo": 7, "win_gol_perd": 6, "win": 5, "draw": 7}


def calc_game_points(p_home, p_away, r_home, r_away, phase):
    if p_home is None or p_away is None or r_home is None or r_away is None:
        return 0, "Sem dados"

    pts = phase_points(phase)

    if p_home == r_home and p_away == r_away:
        return pts["exact"], "Cravada"

    real_diff = r_home - r_away
    pred_diff = p_home - p_away

    if real_diff == 0 and pred_diff == 0:
        return pts["draw"], "Empate correto"

    real_winner = "H" if real_diff > 0 else ("A" if real_diff < 0 else "D")
    pred_winner = "H" if pred_diff > 0 else ("A" if pred_diff < 0 else "D")

    if real_winner == pred_winner and real_winner != "D":
        if pred_diff == real_diff:
            return pts["win_saldo"], "Vencedor + saldo"

        if real_winner == "H":
            if p_home == r_home:
                return pts["win_saldo"], "Vencedor + gols do vencedor"
            if p_away == r_away:
                return pts["win_gol_perd"], "Vencedor + gols do perdedor"

        if real_winner == "A":
            if p_away == r_away:
                return pts["win_saldo"], "Vencedor + gols do vencedor"
            if p_home == r_home:
                return pts["win_gol_perd"], "Vencedor + gols do perdedor"

        return pts["win"], "Vencedor correto"

    return 0, "Sem pontuação"


def game_ended(game, result, admin_data):
    overrides = admin_data.get("overrides", {})
    gid = str(game["id"])

    if overrides.get(gid) == "ENDED" or overrides.get(game["id"]) == "ENDED":
        return True

    raw = str(result.get("status", "")).upper()

    if result.get("locked_90") is True:
        return True

    return any(x in raw for x in ["FT", "FULL", "AET", "PEN", "PENS", "SHOOTOUT"])


def add_row(rows, participante, uid, tipo, fase, evento_id, evento, palpite, resultado, regra, pontos):
    rows.append({
        "Participante": participante,
        "UID": uid,
        "Tipo": tipo,
        "Fase": fase,
        "Evento ID": evento_id,
        "Evento": evento,
        "Palpite": palpite,
        "Resultado": resultado,
        "Regra": regra,
        "Pontos": int(pontos or 0),
    })


def read_collection(db, name):
    return {doc.id: doc.to_dict() for doc in db.collection(name).stream()}


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def get_firestore():
    firebase_json = os.environ.get("FIREBASE_JSON")
    if not firebase_json:
        raise RuntimeError("FIREBASE_JSON não encontrado no ambiente.")

    cred = credentials.Certificate(json.loads(firebase_json))
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    return firestore.client()


def build_games(ko_games):
    games = list(GAMES_LIST)

    for ko_id, ko_data in ko_games.items():
        if ko_data.get("home") and ko_data.get("away"):
            games.append({
                "id": int(ko_id),
                "home": ko_data.get("home"),
                "away": ko_data.get("away"),
                "group": ko_data.get("group", ko_data.get("label", f"Mata-Mata {ko_id}")),
            })

    return games


def audit():
    db = get_firestore()

    users = read_collection(db, "users")
    bets = read_collection(db, "bets")
    extras = read_collection(db, "extras")

    results = db.collection("config").document("results").get().to_dict() or {}
    ko_games = db.collection("config").document("ko_games").get().to_dict() or {}
    admin_data = db.collection("config").document("admin_data").get().to_dict() or {}

    games = build_games(ko_games)
    rows = []
    resumo = []

    humanos = [(uid, u) for uid, u in users.items() if not u.get("isFake")]

    for uid, user in humanos:
        nome = user.get("name", uid)
        bts = bets.get(uid, {})
        ex = extras.get(uid, {})

        total_jogos = 0
        total_extras = 0

        for game in games:
            gid = str(game["id"])
            b = bts.get(gid) or bts.get(game["id"])
            r = results.get(gid) or results.get(game["id"])

            if not b or not r:
                continue

            if not game_ended(game, r, admin_data):
                continue

            p_home = parse_score(b.get("home"))
            p_away = parse_score(b.get("away"))
            r_home = parse_score(r.get("home"))
            r_away = parse_score(r.get("away"))

            if p_home is None or p_away is None or r_home is None or r_away is None:
                continue

            pts, regra = calc_game_points(p_home, p_away, r_home, r_away, game.get("group", ""))
            total_jogos += pts

            add_row(
                rows, nome, uid, "Jogo", phase_label(game), gid,
                f"{game['home']} x {game['away']}",
                f"{p_home}x{p_away}", f"{r_home}x{r_away}", regra, pts
            )

        scorer = ex.get("scorer")
        scorers = admin_data.get("scorers", {})
        if scorer:
            data = scorers.get(scorer)
            gols = int((data or {}).get("goals", 0) or 0)
            bonus = 7 if (data or {}).get("isTop") else 0
            pts = (gols * 2 + bonus) if data else 0
            total_extras += pts

            add_row(
                rows, nome, uid, "Extra", "Artilheiro", "artilheiro",
                scorer, scorer,
                f"{gols} gol(s)" + (" + bônus" if bonus else "") if data else "Sem dados oficiais",
                "2 pontos por gol" + (" + 7 bônus" if bonus else "") if data else "Sem pontuação ainda",
                pts
            )

        adm_r32 = admin_data.get("r32") if isinstance(admin_data.get("r32"), list) else []
        adm_r32_finished = admin_data.get("r32_finished", {})

        for team in ex.get("r32", []) or []:
            pts = 1 if team in adm_r32 else 0
            total_extras += pts
            add_row(rows, nome, uid, "Extra", "16 Avos", "r32", team, team,
                    "Classificou" if pts else "Não consta no gabarito",
                    "1 ponto por classificado correto", pts)

        for grp in list("ABCDEFGHIJKL"):
            teams_in_grp = set()
            for g in GAMES_LIST:
                if g["group"] == grp:
                    teams_in_grp.add(g["home"])
                    teams_in_grp.add(g["away"])

            user_in_grp = [t for t in (ex.get("r32") or []) if t in teams_in_grp]
            adm_in_grp = [t for t in adm_r32 if t in teams_in_grp]

            if not user_in_grp and not adm_in_grp:
                continue

            match_all = bool(adm_in_grp) and len(user_in_grp) == len(adm_in_grp) and set(user_in_grp) == set(adm_in_grp)
            pts = 1 if match_all and adm_r32_finished.get(grp) else 0
            total_extras += pts

            add_row(rows, nome, uid, "Extra", "Bônus 16 Avos", f"bonus-grupo-{grp}",
                    f"Grupo {grp}", ", ".join(user_in_grp), ", ".join(adm_in_grp),
                    "Bônus por grupo gabaritado" if adm_r32_finished.get(grp) else "Grupo ainda não liberado para bônus",
                    pts)

        for team in ex.get("of", []) or []:
            pts = 3 if team in (admin_data.get("of") or []) else 0
            total_extras += pts
            add_row(rows, nome, uid, "Extra", "Oitavas", "of", team, team,
                    "Chegou às Oitavas" if pts else "Não consta no gabarito",
                    "3 pontos por seleção correta", pts)

        for team in ex.get("qf", []) or []:
            pts = 4 if team in (admin_data.get("qf") or []) else 0
            total_extras += pts
            add_row(rows, nome, uid, "Extra", "Quartas", "qf", team, team,
                    "Chegou às Quartas" if pts else "Não consta no gabarito",
                    "4 pontos por seleção correta", pts)

        top = ex.get("top") or {}
        top_picks = [
            ("Campeão", "t1", top.get("t1")),
            ("Vice", "t2", top.get("t2")),
            ("3º Lugar", "t3", top.get("t3")),
            ("4º Lugar", "t4", top.get("t4")),
        ]

        for pos, field, team in top_picks:
            if not team:
                continue
            pts = 5 if team in (admin_data.get("sf") or []) else 0
            total_extras += pts
            add_row(rows, nome, uid, "Extra", "Semis", f"sf-{field}", f"{pos}: {team}", team,
                    "Chegou às Semis" if pts else "Não consta no gabarito",
                    "5 pontos por semifinalista correto entre os 4 do pódio", pts)

        for pos, field, team in top_picks[:2]:
            if not team:
                continue
            pts = 6 if team in (admin_data.get("fi") or []) else 0
            total_extras += pts
            add_row(rows, nome, uid, "Extra", "Final", f"fi-{field}", f"{pos}: {team}", team,
                    "Chegou à Final" if pts else "Não consta no gabarito",
                    "6 pontos por finalista correto entre campeão e vice", pts)

        top4_rules = [
            ("Campeão", "t1", "top1", top.get("t1"), 20),
            ("Vice", "t2", "top2", top.get("t2"), 5),
            ("3º Lugar", "t3", "top3", top.get("t3"), 5),
            ("4º Lugar", "t4", "top4", top.get("t4"), 5),
        ]
        official_top4 = admin_data.get("top4") or {}

        for pos, field, official_key, team, value in top4_rules:
            if not team:
                continue
            official = official_top4.get(official_key)
            pts = value if official and team == official else 0
            total_extras += pts
            add_row(rows, nome, uid, "Extra", "Colocação Final", f"top4-{field}", pos,
                    team, official or "Sem gabarito",
                    "20 pontos por campeão exato" if pos == "Campeão" else "5 pontos por posição exata",
                    pts)

        total = total_jogos + total_extras

        add_row(rows, nome, uid, "RESUMO", "", "subtotal-jogos", "Subtotal Jogos", "", "", "", total_jogos)
        add_row(rows, nome, uid, "RESUMO", "", "subtotal-extras", "Subtotal Extras", "", "", "", total_extras)
        add_row(rows, nome, uid, "RESUMO", "", "total", "TOTAL", "", "", "", total)

        resumo.append({
            "Participante": nome,
            "UID": uid,
            "Tipo": "RESUMO",
            "Fase": "",
            "Evento ID": "total",
            "Evento": "TOTAL",
            "Palpite": "",
            "Resultado": "",
            "Regra": "",
            "Pontos": total,
        })

    resumo.sort(key=lambda r: (-int(r["Pontos"]), r["Participante"].lower()))

    return rows, resumo


def compare_with_app(app_csv_path, resumo_independente):
    app_totals = {}

    with open(app_csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            if row.get("Tipo") == "RESUMO" and row.get("Evento") == "TOTAL":
                app_totals[row.get("UID")] = int(float(row.get("Pontos") or 0))

    problemas = []
    for row in resumo_independente:
        uid = row["UID"]
        app_total = app_totals.get(uid)
        independente = int(row["Pontos"])

        if app_total is None:
            problemas.append((row["Participante"], uid, "sem total no CSV do app", independente))
        elif app_total != independente:
            problemas.append((row["Participante"], uid, app_total, independente))

    return problemas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compare-app-csv", default="", help="Caminho do CSV exportado pelo botão do app.")
    args = parser.parse_args()

    detalhado, resumo = audit()

    write_csv("auditoria_independente_detalhada.csv", detalhado)
    write_csv("auditoria_independente_resumo.csv", resumo)

    print("✅ Auditoria independente gerada:")
    print(" - auditoria_independente_detalhada.csv")
    print(" - auditoria_independente_resumo.csv")
    print("")
    print("Top 10:")
    for i, row in enumerate(resumo[:10], start=1):
        print(f"{i:02d}. {row['Participante']}: {row['Pontos']}")

    if args.compare_app_csv:
        problemas = compare_with_app(args.compare_app_csv, resumo)
        print("")
        if not problemas:
            print("✅ Comparação com CSV do app: nenhuma divergência encontrada.")
        else:
            print("❌ Divergências encontradas:")
            for nome, uid, app_total, independente in problemas:
                print(f" - {nome} ({uid}): app={app_total}, independente={independente}")


if __name__ == "__main__":
    main()

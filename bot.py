import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("FOOTBALL_API_KEY")

def get_last_5_matches(team_name):
    # Aquí conectas tu API real
    # Debe devolver una lista de 5 partidos con goles/xG/corners/tarjetas
    return [
        {"xg_for": 1.2, "xg_against": 0.8, "goals_for": 2, "goals_against": 1, "corners": 9, "cards": 3},
        {"xg_for": 0.9, "xg_against": 1.1, "goals_for": 1, "goals_against": 1, "corners": 8, "cards": 2},
        {"xg_for": 1.5, "xg_against": 0.7, "goals_for": 3, "goals_against": 0, "corners": 10, "cards": 1},
        {"xg_for": 0.8, "xg_against": 1.0, "goals_for": 0, "goals_against": 1, "corners": 7, "cards": 4},
        {"xg_for": 1.1, "xg_against": 0.9, "goals_for": 1, "goals_against": 0, "corners": 8, "cards": 2},
    ]

def calc_team_stats(matches):
    n = len(matches)
    return {
        "xg_for": sum(m["xg_for"] for m in matches) / n,
        "xg_against": sum(m["xg_against"] for m in matches) / n,
        "goals_for": sum(m["goals_for"] for m in matches) / n,
        "goals_against": sum(m["goals_against"] for m in matches) / n,
        "corners": sum(m["corners"] for m in matches) / n,
        "cards": sum(m["cards"] for m in matches) / n,
    }

def build_prediction(home_stats, away_stats):
    home_strength = home_stats["xg_for"] - away_stats["xg_against"]
    away_strength = away_stats["xg_for"] - home_stats["xg_against"]

    local = 40 + home_strength * 12
    visitante = 30 + away_strength * 12
    empate = 100 - local - visitante

    local = max(10, min(local, 75))
    visitante = max(10, min(visitante, 75))
    empate = max(10, min(empate, 45))

    over25 = (home_stats["goals_for"] + away_stats["goals_for"]) / 4 * 100
    btts = min(80, max(20, (home_stats["goals_for"] + away_stats["goals_for"]) * 18))

    return {
        "local": round(local, 1),
        "empate": round(empate, 1),
        "visitante": round(visitante, 1),
        "over25": round(over25, 1),
        "btts": round(btts, 1),
        "corners": round((home_stats["corners"] + away_stats["corners"]) / 2, 1),
        "cards": round((home_stats["cards"] + away_stats["cards"]) / 2, 1),
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Usa /predict equipo1 vs equipo2\nEjemplo: /predict argentina vs francia"
    )

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if " vs " not in text:
        await update.message.reply_text("Formato: /predict argentina vs francia")
        return

    home, away = [x.strip() for x in text.split(" vs ", 1)]

    home_matches = get_last_5_matches(home)
    away_matches = get_last_5_matches(away)

    home_stats = calc_team_stats(home_matches)
    away_stats = calc_team_stats(away_matches)
    pred = build_prediction(home_stats, away_stats)

    msg = f"""⚽ {home} vs {away}

📊 Últimos 5 partidos
{home}: xG {home_stats["xg_for"]:.2f} | GF {home_stats["goals_for"]:.2f} | GC {home_stats["goals_against"]:.2f}
{away}: xG {away_stats["xg_for"]:.2f} | GF {away_stats["goals_for"]:.2f} | GC {away_stats["goals_against"]:.2f}

🏆 Probabilidades
Local: {pred["local"]}%
Empate: {pred["empate"]}%
Visitante: {pred["visitante"]}%

🔥 Mercados
Over 2.5: {pred["over25"]}%
BTTS: {pred["btts"]}%
Córners esperados: {pred["corners"]}
Tarjetas esperadas: {pred["cards"]}

Confianza del pick: MEDIA
"""
    await update.message.reply_text(msg)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict))
    app.run_polling()

if __name__ == "__main__":
    main() 

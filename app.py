from flask import Flask, request, render_template_string, redirect, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "clave_secreta_prode"

ADMIN_PASS = "admin123"

usuarios_db = {
    "yuke": None, "juan": None, "mauri": None, "fenix": None, 
    "braii": None, "didi": None, "fake": None, "nikotina": None, "rojo": None
}

partidos = [
    {"id": 1, "local": "México", "bandera_local": "https://flagcdn.com/w40/mx.png", "visitante": "Sudáfrica", "bandera_visitante": "https://flagcdn.com/w40/za.png", "goles_local_real": None, "goles_visitante_real": None, "inicio": "2026-06-11 19:00"},
    {"id": 2, "local": "Corea del Sur", "bandera_local": "https://flagcdn.com/w40/kr.png", "visitante": "Rep. Checa", "bandera_visitante": "https://flagcdn.com/w40/cz.png", "goles_local_real": None, "goles_visitante_real": None, "inicio": "2026-06-12 02:00"},
    {"id": 3, "local": "Canadá", "bandera_local": "https://flagcdn.com/w40/ca.png", "visitante": "Bosnia", "bandera_visitante": "https://flagcdn.com/w40/ba.png", "goles_local_real": None, "goles_visitante_real": None, "inicio": "2026-06-12 19:00"},
    {"id": 4, "local": "EE.UU.", "bandera_local": "https://flagcdn.com/w40/us.png", "visitante": "Paraguay", "bandera_visitante": "https://flagcdn.com/w40/py.png", "goles_local_real": None, "goles_visitante_real": None, "inicio": "2026-06-13 01:00"}
]

pronosticos = []

def obtener_ranking():
    usuarios_ranking = {user: {"puntos": 0} for user in usuarios_db.keys()}
    return sorted(usuarios_ranking.items(), key=lambda x: x[1]["puntos"], reverse=True)

TEMPLATE = """
<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>Prode</title>
<style>
    body { font-family: Arial; background-color: #1a1a1a; color: #fff; padding: 20px; }
    .main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
    .caja { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .partido-tarjeta { display: flex; align-items: center; justify-content: space-between; background: #3d3d3d; padding: 10px; margin-bottom: 10px; border-radius: 5px; }
    .input-gol { width: 40px; text-align: center; background: #555; border: none; color: white; padding: 5px; }
    button { padding: 5px 10px; background: #555; border: none; color: white; cursor: pointer; }
</style></head><body>
<div class="caja">Usuario: <strong>{{ usuario_actual|capitalize }}</strong> | <a href="/logout" style="color:red;">Salir</a></div>
<div class="main-grid">
    <div>
        <div class="caja">
            <h2>🗓️ Partidos</h2>
            {% for p in partidos %}
            <form action="/guardar" method="POST" class="partido-tarjeta">
                <input type="hidden" name="partido_id" value="{{ p.id }}">
                <div style="width: 140px;"><img src="{{ p.bandera_local }}" width="20"> {{ p.local }}</div>
                <strong>{{ p.inicio[11:16] }} hs</strong>
                <input type="number" name="goles_local" class="input-gol" required> - 
                <input type="number" name="goles_visitante" class="input-gol" required>
                <div style="width: 140px; text-align: right;">{{ p.visitante }} <img src="{{ p.bandera_visitante }}" width="20"></div>
                <button type="submit">Cargar</button>
            </form>
            {% endfor %}
        </div>
        <div class="caja">
            <h2>📜 Historial</h2>
            {% for prono in pronosticos if prono.usuario == usuario_actual %}
            <div>{{ prono.local }} vs {{ prono.visitante }}: {{ prono.goles_local }} - {{ prono.goles_visitante }}</div>
            {% endfor %}
        </div>
    </div>
    <div class="caja">
        <h2>🏆 Posiciones</h2>
        {% for u, s in ranking %}<div>{{ u|capitalize }}: <strong>{{ s.puntos }} pts</strong></div>{% endfor %}
    </div>
</div></body></html>
"""

@app.route("/")
def index():
    if "usuario" not in session: return redirect("/login")
    return render_template_string(TEMPLATE, partidos=partidos, pronosticos=pronosticos, ranking=obtener_ranking(), usuario_actual=session["usuario"])

@app.route("/login", methods=["POST"])
def login():
    u = request.form["usuario"].strip().lower()
    if u in usuarios_db:
        session["usuario"] = u
        return redirect("/")
    return "Usuario no encontrado"

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect("/")

@app.route("/guardar", methods=["POST"])
def guardar():
    if "usuario" not in session: return redirect("/")
    p_id = int(request.form["partido_id"])
    p_el = next(p for p in partidos if p["id"] == p_id)
    global pronosticos
    pronosticos.append({"usuario": session["usuario"], "local": p_el["local"], "visitante": p_el["visitante"], "goles_local": request.form["goles_local"], "goles_visitante": request.form["goles_visitante"]})
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

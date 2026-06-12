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
    {"id": 1, "local": "México", "bandera_local": "https://flagcdn.com/w40/mx.png", "visitante": "Sudáfrica", "bandera_visitante": "https://flagcdn.com/w40/za.png", "goles_local_real": None, "goles_visitante_real": None, "multiplicador": 1, "inicio": "2026-06-11 19:00"},
    {"id": 2, "local": "Corea del Sur", "bandera_local": "https://flagcdn.com/w40/kr.png", "visitante": "Rep. Checa", "bandera_visitante": "https://flagcdn.com/w40/cz.png", "goles_local_real": None, "goles_visitante_real": None, "multiplicador": 1, "inicio": "2026-06-12 02:00"},
    {"id": 3, "local": "Canadá", "bandera_local": "https://flagcdn.com/w40/ca.png", "visitante": "Bosnia", "bandera_visitante": "https://flagcdn.com/w40/ba.png", "goles_local_real": None, "goles_visitante_real": None, "multiplicador": 1, "inicio": "2026-06-12 19:00"},
    {"id": 4, "local": "EE.UU.", "bandera_local": "https://flagcdn.com/w40/us.png", "visitante": "Paraguay", "bandera_visitante": "https://flagcdn.com/w40/py.png", "goles_local_real": None, "goles_visitante_real": None, "multiplicador": 1, "inicio": "2026-06-13 01:00"}
]

pronosticos = []

def obtener_ranking():
    usuarios_ranking = {user: {"puntos": 0, "plenos": 0} for user in usuarios_db.keys()}
    for p in pronosticos:
        u = p["usuario"]
        if u not in usuarios_ranking: continue
        pr = next((pt for pt in partidos if pt["id"] == p["partido_id"]), None)
        if pr and pr["goles_local_real"] is not None:
            glr, gvr = pr["goles_local_real"], pr["goles_visitante_real"]
            glp, gvp = int(p["goles_local"]), int(p["goles_visitante"])
            p_base = 0
            if glr == glp and gvr == gvp:
                p_base = 3
                usuarios_ranking[u]["plenos"] += 1
            elif (glr == gvr and glp == gvp) or (glr > gvr and glp > gvp) or (glr < gvr and glp < gvp):
                p_base = 1
            usuarios_ranking[u]["puntos"] += (p_base * pr["multiplicador"])
    return sorted(usuarios_ranking.items(), key=lambda x: (x[1]["puntos"], x[1]["plenos"]), reverse=True)

TEMPLATE = """
<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>Prode</title>
<style>
    body { font-family: Arial; margin: 40px; background-color: #1a1a1a; color: #fff; }
    .nav { background: #2d2d2d; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    .caja { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .partido-tarjeta { display: flex; justify-content: space-between; align-items: center; background: #3d3d3d; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .input-gol { width: 50px; text-align: center; padding: 10px; background: #555; color: white; border: none; border-radius: 4px; }
    button { padding: 10px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
</style></head><body>
<div class="nav">Usuario: <strong>{{ usuario_actual|capitalize }}</strong> | <a href="/logout" style="color:red;">Salir</a></div>
<div class="caja">
    <h2>🗓️ Partidos</h2>
    {% for p in partidos %}
    <form action="/guardar" method="POST" class="partido-tarjeta">
        <input type="hidden" name="partido_id" value="{{ p.id }}">
        <div style="width:150px;"><img src="{{ p.bandera_local }}" width="30"> {{ p.local }}</div>
        <strong>{{ p.inicio[11:16] }} hs</strong>
        <input type="number" name="goles_local" class="input-gol" required> - 
        <input type="number" name="goles_visitante" class="input-gol" required>
        <div style="width:150px; text-align:right;">{{ p.visitante }} <img src="{{ p.bandera_visitante }}" width="30"></div>
        <button type="submit">Cargar</button>
    </form>
    {% endfor %}
</div>
<div class="caja">
    <h2>🏆 Posiciones</h2>
    {% for u, s in ranking %}<div>{{ u|capitalize }}: <strong>{{ s.puntos }} pts</strong></div>{% endfor %}
</div>
</body></html>
"""

@app.route("/")
def index():
    if "usuario" not in session: return redirect("/login")
    return render_template_string(TEMPLATE, partidos=partidos, ranking=obtener_ranking(), usuario_actual=session["usuario"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["usuario"].strip().lower()
        p = request.form["password"]
        if request.form["accion"] == "login":
            if u in usuarios_db and usuarios_db[u] == p:
                session["usuario"] = u
                return redirect("/")
        elif request.form["accion"] == "registro" and u in usuarios_db and usuarios_db[u] is None:
            usuarios_db[u] = p
            session["usuario"] = u
            return redirect("/")
    return '<body style="background:#222;color:white;text-align:center;padding:50px;"><h2>⚽ Entrar</h2><form method="POST"><input name="usuario" placeholder="Usuario"><input type="password" name="password" placeholder="Contraseña"><br><br><button name="accion" value="login">Entrar</button> <button name="accion" value="registro">Registrarse</button></form></body>'

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect("/login")

@app.route("/guardar", methods=["POST"])
def guardar():
    if "usuario" not in session: return redirect("/login")
    p_id = int(request.form["partido_id"])
    p_el = next(p for p in partidos if p["id"] == p_id)
    global pronosticos
    pronosticos = [p for p in pronosticos if not (p["usuario"] == session["usuario"] and p["partido_id"] == p_id)]
    pronosticos.append({"usuario": session["usuario"], "partido_id": p_id, "local": p_el["local"], "visitante": p_el["visitante"], "goles_local": request.form["goles_local"], "goles_visitante": request.form["goles_visitante"]})
    return redirect("/")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST" and request.form.get("password") == ADMIN_PASS: session["admin"] = True
    if session.get("admin"):
        return render_template_string('<body style="background:#222;color:white;"><h2>Admin</h2>{% for p in partidos %}<form method="POST" action="/admin/actualizar"><input type="hidden" name="id" value="{{p.id}}">{{p.local}} vs {{p.visitante}} <input name="gl" value="{{p.goles_local_real or 0}}" style="width:40px;">-<input name="gv" value="{{p.goles_visitante_real or 0}}" style="width:40px;"><button>Guardar</button></form>{% endfor %}</body>', partidos=partidos)
    return '<form method="POST">Password: <input type="password" name="password"><button>Entrar</button></form>'

@app.route("/admin/actualizar", methods=["POST"])
def admin_actualizar():
    if not session.get("admin"): return "No"
    p = next(pt for pt in partidos if pt["id"] == int(request.form["id"]))
    p["goles_local_real"] = int(request.form["gl"])
    p["goles_visitante_real"] = int(request.form["gv"])
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, render_template_string, redirect, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "mi_clave_secreta_super_segura_para_el_prode"

usuarios_db = {
    "yuke": None, "juan": None, "mauri": None, "fenix": None, 
    "braii": None, "didi": None, "fake": None, "nikotina": None, "rojo": None
}

partidos = [
    {"id": 1, "local": "México", "bandera_local": "https://flagcdn.com/w40/mx.png", "visitante": "Sudáfrica", "bandera_visitante": "https://flagcdn.com/w40/za.png", "goles_local_real": None, "goles_visitante_real": None, "multiplicador": 1, "inicio": "2026-06-11 16:00"},
    {"id": 2, "local": "Corea del Sur", "bandera_local": "https://flagcdn.com/w40/kr.png", "visitante": "Rep. Checa", "bandera_visitante": "https://flagcdn.com/w40/cz.png", "goles_local_real": None, "goles_visitante_real": None, "multiplicador": 1, "inicio": "2026-06-11 23:00"},
    {"id": 3, "local": "Canadá", "bandera_local": "https://flagcdn.com/w40/ca.png", "visitante": "Bosnia", "bandera_visitante": "https://flagcdn.com/w40/ba.png", "goles_local_real": None, "goles_visitante_real": None, "multiplicador": 1, "inicio": "2026-06-12 16:00"},
    {"id": 4, "local": "EE.UU.", "bandera_local": "https://flagcdn.com/w40/us.png", "visitante": "Paraguay", "bandera_visitante": "https://flagcdn.com/w40/py.png", "goles_local_real": None, "goles_visitante_real": None, "multiplicador": 1, "inicio": "2026-06-12 22:00"}
]

pronosticos = []

def obtener_ranking():
    usuarios_ranking = {user: {"puntos": 0, "plenos": 0} for user in usuarios_db.keys()}
    for p in pronosticos:
        usuario = p["usuario"]
        if usuario not in usuarios_ranking: continue
            
        partido_real = next((partido for partido in partidos if partido["id"] == p["partido_id"]), None)
        
        if partido_real and partido_real["goles_local_real"] is not None:
            g_local_real = partido_real["goles_local_real"]
            g_visitante_real = partido_real["goles_visitante_real"]
            g_local_prono = int(p["goles_local"])
            g_visitante_prono = int(p["goles_visitante"])
            
            puntos_base = 0
            if g_local_real == g_local_prono and g_visitante_real == g_visitante_prono:
                puntos_base = 3
                usuarios_ranking[usuario]["plenos"] += 1
            else:
                es_empate_real = (g_local_real == g_visitante_real)
                es_empate_prono = (g_local_prono == g_visitante_prono)
                gana_local_real = (g_local_real > g_visitante_real)
                gana_local_prono = (g_local_prono > g_visitante_prono)
                
                if (es_empate_real == es_empate_prono) and (gana_local_real == gana_local_prono):
                    puntos_base = 1
                
            usuarios_ranking[usuario]["puntos"] += (puntos_base * partido_real["multiplicador"])
                
    return sorted(usuarios_ranking.items(), key=lambda x: (x[1]["puntos"], x[1]["plenos"]), reverse=True)

TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Prode del Mundial</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #1a1a1a; color: #fff; }
        .nav { display: flex; justify-content: space-between; background: #2d2d2d; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .nav a { color: #ff4d4d; text-decoration: none; font-weight: bold; }
        .contenedor { display: flex; gap: 20px; }
        .columna-izq { flex: 2; } .columna-der { flex: 1; }
        .caja { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.5); }
        .partido-tarjeta { display: flex; justify-content: space-between; align-items: center; background: #3d3d3d; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #4d4d4d; }
        .equipo { display: flex; flex-direction: column; align-items: center; width: 30%; }
        .bandera { width: 45px; height: auto; border-radius: 4px; }
        .nombre-equipo { font-weight: bold; margin-top: 8px; text-align: center; font-size: 15px; color: #e0e0e0; }
        .inputs-goles { display: flex; align-items: center; gap: 10px; }
        .input-gol { width: 50px; text-align: center; font-size: 20px; font-weight: bold; padding: 5px; border: none; border-radius: 4px; background: #555; color: white; }
        .btn-guardar { background-color: #28a745; color: white; border: none; cursor: pointer; border-radius: 4px; padding: 10px 15px; font-weight: bold; height: 100%; }
        .ranking-item { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #4d4d4d; font-size: 18px; }
        .puesto-1 { font-weight: bold; color: #ffd700; }
    </style>
</head>
<body>
    <div class="nav">
        <span>Hola, <strong>{{ usuario_actual|capitalize }}</strong></span>
        <a href="/logout">Cerrar Sesión 🚪</a>
    </div>
    <div class="contenedor">
        <div class="columna-izq">
            <div class="caja">
                <h2>🗓️ Partidos de Hoy</h2>
                {% for p in partidos %}
                    {% if p.inicio > ahora and p.inicio.startswith(hoy) %}
                        <form action="/guardar" method="POST" class="partido-tarjeta">
                            <input type="hidden" name="partido_id" value="{{ p.id }}">
                            <div class="equipo"><img src="{{ p.bandera_local }}" class="bandera"><span class="nombre-equipo">{{ p.local }}</span></div>
                            <div class="inputs-goles"><input type="number" name="goles_local" class="input-gol" min="0" required><span>-</span><input type="number" name="goles_visitante" class="input-gol" min="0" required></div>
                            <div class="equipo"><img src="{{ p.bandera_visitante }}" class="bandera"><span class="nombre-equipo">{{ p.visitante }}</span></div>
                            <button type="submit" class="btn-guardar">Cargar</button>
                        </form>
                    {% endif %}
                {% endfor %}
            </div>
        </div>
        <div class="columna-der">
            <div class="caja">
                <h2>🏆 Tabla de Posiciones</h2>
                {% for usuario, stats in ranking %}
                    <div class="ranking-item {% if loop.first %}puesto-1{% endif %}">
                        <span>{{ loop.index }}. {{ usuario|capitalize }}</span>
                        <strong>{{ stats.puntos }} pts</strong>
                    </div>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""

AUTH_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Ingresar</title>
    <style>
        body { font-family: Arial; background-color: #1a1a1a; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-caja { background: #2d2d2d; padding: 30px; border-radius: 8px; width: 320px; color: white; }
        input, button { margin: 10px 0; padding: 12px; width: 100%; border-radius: 4px; border: none; }
        button { background-color: #28a745; color: white; font-weight: bold; cursor: pointer; }
        .btn-azul { background-color: #007bff; }
    </style>
</head>
<body>
    <div class="login-caja">
        <h2>⚽ Entrar al Prode</h2>
        <form method="POST">
            <input type="text" name="usuario" placeholder="Usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit" name="accion" value="login">Iniciar Sesión</button>
            <button type="submit" name="accion" value="registro" class="btn-azul">Registrarse</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    if "usuario" not in session: return redirect("/login")
    ahora_arg = datetime.utcnow() - timedelta(hours=3)
    return render_template_string(TEMPLATE, partidos=partidos, pronosticos=pronosticos, ranking=obtener_ranking(), ahora=ahora_arg.strftime("%Y-%m-%d %H:%M"), hoy=ahora_arg.strftime("%Y-%m-%d"), usuario_actual=session["usuario"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["usuario"].strip().lower()
        p = request.form["password"]
        if request.form["accion"] == "login":
            if u in usuarios_db and usuarios_db[u] == p:
                session["usuario"] = u
                return redirect("/")
        elif request.form["accion"] == "registro" and u in usuarios_db and usuarios_db[u] is None and len(p) >= 4:
            usuarios_db[u] = p
            session["usuario"] = u
            return redirect("/")
    return render_template_string(AUTH_TEMPLATE)

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

if __name__ == "__main__":
    app.run(debug=True)

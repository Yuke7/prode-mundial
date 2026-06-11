from flask import Flask, request, render_template_string, redirect, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mi_clave_secreta_super_segura_para_el_prode"

# 📋 LISTA BLANCA DE INVITADOS ACTUALIZADA
usuarios_db = {
    "yuke": None,
    "juan": None,
    "mauri": None,
    "fenix": None,
    "braii": None,
    "didi": None,
    "fake": None,
    "nikotina": None,
    "rojo": None
}

partidos = [
    {"id": 1, "local": "Argentina", "visitante": "Brasil", "goles_local_real": None, "goles_visitante_real": None, "multiplicador": 2, "inicio": "2026-07-15 16:00"},
    {"id": 2, "local": "River Plate", "visitante": "Boca Juniors", "goles_local_real": None, "goles_visitante_real": None, "multiplicador": 1, "inicio": "2026-06-10 10:00"},
    {"id": 3, "local": "San Lorenzo", "visitante": "Huracán", "goles_local_real": 0, "goles_visitante_real": 0, "multiplicador": 1, "inicio": "2026-07-20 18:00"}
]

pronosticos = []

def obtener_ranking():
    usuarios_ranking = {user: {"puntos": 0, "plenos": 0} for user in usuarios_db.keys()}
    for p in pronosticos:
        usuario = p["usuario"]
        if usuario not in usuarios_ranking:
            usuarios_ranking[usuario] = {"puntos": 0, "plenos": 0}
            
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
            elif (g_local_real > g_visitante_real and g_local_prono > g_visitante_prono) or \
                 (g_local_real < g_visitante_real and g_local_prono < g_visitante_prono) or \
                 (g_local_real == g_visitante_real and g_local_prono == g_visitante_prono):
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
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
        .nav { display: flex; justify-content: space-between; background: #333; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .nav a { color: #ff4d4d; text-decoration: none; font-weight: bold; }
        .contenedor { display: flex; gap: 20px; }
        .columna-izq { flex: 2; }
        .columna-der { flex: 1; }
        .caja { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
        input, select, button { margin: 5px 0; padding: 10px; font-size: 16px; width: 100%; box-sizing: border-box; }
        .corto { width: 60px; display: inline; }
        button { background-color: #007bff; color: white; border: none; cursor: pointer; border-radius: 4px; }
        button:hover { background-color: #0056b3; }
        .ranking-item { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee; font-size: 18px; }
        .puesto-1 { font-weight: bold; color: #d4af37; }
        .alerta { color: red; font-size: 14px; }
    </style>
</head>
<body>
    <div class="nav">
        <span>Hola, <strong>{{ usuario_actual }}</strong> ⚽ Bienvenido al Prode</span>
        <a href="/logout">Cerrar Sesión 🚪</a>
    </div>

    <div class="contenedor">
        <div class="columna-izq">
            <div class="caja">
                <h2>Cargá tu pronóstico</h2>
                <form action="/guardar" method="POST">
                    <label>Elegí el partido:</label><br>
                    <select name="partido_id">
                        {% for p in partidos %}
                            {% if p.inicio > ahora %}
                                <option value="{{ p.id }}">{{ p.local }} vs {{ p.visitante }} {% if p.multiplicador > 1 %}(Vale x{{ p.multiplicador }}){% endif %}</option>
                            {% endif %}
                        {% endfor %}
                    </select>
                    <p class="alerta">Nota: Los partidos que ya empezaron no aparecen.</p>
                    
                    <label>Goles Local:</label>
                    <input type="number" name="goles_local" min="0" required class="corto">
                    
                    <label>Goles Visitante:</label>
                    <input type="number" name="goles_visitante" min="0" required class="corto"><br><br>
                    
                    <button type="submit">Enviar Jugada</button>
                </form>
            </div>
            
            <div class="caja">
                <h2>Apuestas registradas</h2>
                <ul>
                {% for prono in pronosticos %}
                    <li><strong>{{ prono.usuario }}</strong>: {{ prono.local }} {{ prono.goles_local }} - {{ prono.goles_visitante }} {{ prono.visitante }}</li>
                {% else %}
                    <li>Todavía nadie cargó nada.</li>
                {% endfor %}
                </ul>
            </div>
        </div>
        
        <div class="columna-der">
            <div class="caja" style="background-color: #e9ecef;">
                <h2>🏆 Tabla de Posiciones</h2>
                {% for usuario, stats in ranking %}
                    <div class="ranking-item {% if loop.first %}puesto-1{% endif %}">
                        <span>{{ loop.index }}. {{ usuario }} <small>({{ stats.plenos }} plenos)</small></span>
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
    <title>Ingresar al Prode</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-caja { background: white; padding: 30px; border-radius: 8px; box-shadow: 0px 0px 15px rgba(0,0,0,0.2); width: 320px; }
        h2 { text-align: center; color: #333; margin-top: 0; }
        input, button { margin: 10px 0; padding: 12px; font-size: 16px; width: 100%; box-sizing: border-box; }
        button { background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .btn-azul { background-color: #007bff; }
        .error { color: red; text-align: center; font-weight: bold; }
    </style>
</head>
<body>
    <div class="login-caja">
        <h2>⚽ Entrar al Prode</h2>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <form method="POST">
            <input type="text" name="usuario" placeholder="Tu Nombre de la lista" required>
            <input type="password" name="password" placeholder="Tu Contraseña" required>
            <button type="submit" name="accion" value="login">Iniciar Sesión</button>
            <button type="submit" name="accion" value="registro" class="btn-azul">Registrarse (Primer ingreso)</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    if "usuario" not in session:
        return redirect("/login")
    ranking_actual = obtener_ranking()
    ahora_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    return render_template_string(TEMPLATE, partidos=partidos, pronosticos=pronosticos, ranking=ranking_actual, ahora=ahora_str, usuario_actual=session["usuario"])

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = request.form["usuario"].strip().lower()
        password = request.form["password"]
        accion = request.form["accion"]
        
        if accion == "login":
            if usuario in usuarios_db and usuarios_db[usuario] == password:
                session["usuario"] = usuario
                return redirect("/")
            else:
                error = "Usuario o contraseña incorrectos."
                
        elif accion == "registro":
            if usuario not in usuarios_db:
                error = "🛑 No estás en la lista de invitados de este Prode."
            elif usuarios_db[usuario] is not None:
                error = "⚠️ Este usuario ya generó su contraseña. Poné 'Iniciar Sesión'."
            elif len(password) < 4:
                error = "La contraseña debe tener al menos 4 caracteres."
            else:
                usuarios_db[usuario] = password
                session["usuario"] = usuario
                return redirect("/")
                
    return render_template_string(AUTH_TEMPLATE, error=error)

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect("/login")

@app.route("/guardar", methods=["POST"])
def guardar():
    if "usuario" not in session:
        return redirect("/login")
    partido_id = int(request.form["partido_id"])
    partido_elegido = next(p for p in partidos if p["id"] == partido_id)
    nuevo_pronostico = {
        "usuario": session["usuario"],
        "partido_id": partido_id,
        "local": partido_elegido["local"],
        "visitante": partido_elegido["visitante"],
        "goles_local": request.form["goles_local"],
        "goles_visitante": request.form["goles_visitante"]
    }
    pronosticos.append(nuevo_pronostico)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
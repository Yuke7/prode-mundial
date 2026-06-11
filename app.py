from flask import Flask, request, render_template_string, redirect, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "mi_clave_secreta_super_segura_para_el_prode"

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

# Banderas cambiadas por links a imágenes reales (.png)
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
        if usuario not in usuarios_ranking:
            continue
            
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
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #1a1a1a; color: #fff; }
        .nav { display: flex; justify-content: space-between; background: #2d2d2d; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .nav a { color: #ff4d4d; text-decoration: none; font-weight: bold; }
        .contenedor { display: flex; gap: 20px; }
        .columna-izq { flex: 2; }
        .columna-der { flex: 1; }
        .caja { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.5); }
        h2 { color: #fff; margin-top: 0; }
        
        .partido-tarjeta { display: flex; justify-content: space-between; align-items: center; background: #3d3d3d; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #4d4d4d; }
        .equipo { display: flex; flex-direction: column; align-items: center; width: 30%; }
        .bandera { width: 45px; height: auto; border-radius: 4px; box-shadow: 0px 0px 5px rgba(0,0,0,0.3); }
        .nombre-equipo { font-weight: bold; margin-top: 8px; text-align: center; font-size: 15px; color: #e0e0e0; }
        .inputs-goles { display: flex; align-items: center; gap: 10px; }
        .input-gol { width: 50px; text-align: center; font-size: 20px; font-weight: bold; padding: 5px; border: none; border-radius: 4px; background: #555; color: white; }
        .input-gol:focus { outline: 2px solid #28a745; background: #666; }
        .vs { font-weight: bold; color: #999; }
        .btn-guardar { background-color: #28a745; color: white; border: none; cursor: pointer; border-radius: 4px; padding: 10px 15px; font-weight: bold; height: 100%; transition: background 0.2s; }
        .btn-guardar:hover { background-color: #218838; }
        
        .ranking-item { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #4d4d4d; font-size: 18px; }
        .puesto-1 { font-weight: bold; color: #ffd700; }
        .alerta { color: #aaa; font-style: italic; text-align: center; }
        ul { padding-left: 20px; }
        li { margin-bottom: 8px; font-size: 16px; }
    </style>
</head>
<body>
    <div class="nav">
        <span>Hola, <strong>{{ usuario_actual|capitalize }}</strong> ⚽ Bienvenido al Prode</span>
        <a href="/logout">Cerrar Sesión 🚪</a>
    </div>

    <div class="contenedor">
        <div class="columna-izq">
            <div class="caja">
                <h2>🗓️ Partidos de Hoy</h2>
                {% set cont = namespace(hay=false) %}
                {% for p in partidos %}
                    {% if p.inicio > ahora and p.inicio.startswith(hoy) %}
                        {% set cont.hay = true %}
                        <form action="/guardar" method="POST" class="partido-tarjeta">
                            <input type="hidden" name="partido_id" value="{{ p.id }}">
                            
                            <div class="equipo">
                                <img src="{{ p.bandera_local }}" class="bandera" alt="{{ p.local }}">
                                <span class="nombre-equipo">{{ p.local }}</span>
                            </div>
                            
                            <div class="inputs-goles">
                                <input type="number" name="goles_local" class="input-gol" min="0" required>
                                <span class="vs">-</span>
                                <input type="number" name="goles_visitante" class="input-gol" min="0" required>
                            </div>
                            
                            <div class="equipo">
                                <img src="{{ p.bandera_visitante }}" class="bandera" alt="{{ p.visitante }}">
                                <span class="nombre-equipo">{{ p.visitante }}</span>
                            </div>
                            
                            <button type="submit" class="btn-guardar">Cargar</button>
                        </form>
                    {% endif %}
                {% endfor %}
                
                {% if not cont.hay %}
                    <p class="alerta">No hay más partidos disponibles para apostar en el día de la fecha.</p>
                {% endif %}
            </div>
            
            <div class="caja">
                <h2>Tus apuestas para hoy</h2>
                <ul>
                {% for prono in pronosticos %}
                    {% if prono.usuario == usuario_actual %}
                        <li>{{ prono.local }} <strong>{{ prono.goles_local }} - {{ prono.goles_visitante }}</strong> {{ prono.visitante }}</li>
                    {% endif %}
                {% else %}
                    <li>Todavía no cargaste nada.</li>
                {% endfor %}
                </ul>
            </div>
        </div>
        
        <div class="columna-der">
            <div class="caja">
                <h2>🏆 Tabla de Posiciones</h2>
                {% for usuario, stats in ranking %}
                    <div class="ranking-item {% if loop.first %}puesto-1{% endif %}">
                        <span>{{ loop.index }}. {{ usuario|capitalize }} <small>({{ stats.plenos }} plenos)</small></span>
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
        body { font-family: Arial, sans-serif; background-color: #1a1a1a; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-caja { background: #2d2d2d; padding: 30px; border-radius: 8px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); width: 320px; }
        h2 { text-align: center; color: #fff; margin-top: 0; }
        input, button { margin: 10px 0; padding: 12px; font-size: 16px; width: 100%; box-sizing: border-box; border-radius: 4px; border: none; }
        input { background: #444; color: white; }
        input:focus { outline: 2px solid #007bff; }
        button { background-color: #28a745; color: white; cursor: pointer; font-weight: bold; }
        .btn-azul { background-color: #007bff; }
        .error { color: #ff4d4d; text-align: center; font-weight: bold; }
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
    
    # ⏱️ RELOJ SINCRONIZADO: Forzamos la hora UTC a la hora local de Buenos Aires restando 3 horas
    ahora_arg = datetime.utcnow() - timedelta(hours=3)
    
    ahora_str = ahora_arg.strftime("%Y-%m-%d %H:%M")
    hoy_str = ahora_arg.strftime("%Y-%m-%d")
    
    return render_template_string(TEMPLATE, partidos=partidos, pronosticos=pronosticos, ranking=ranking_actual, ahora=ahora_str, hoy=hoy_str, usuario_actual=session["usuario"])

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
    usuario = session["usuario"]
    
    global pronosticos
    pronosticos = [p for p in pronosticos if not (p["usuario"] == usuario and p["partido_id"] == partido_id)]
    
    nuevo_pronostico = {
        "usuario": usuario,
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

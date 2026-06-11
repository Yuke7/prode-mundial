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
            else:
                if (glr == gvr and glp == gvp) or (glr > gvr and glp > gvp) or (glr < gvr and glp < gvp):
                    p_base = 1
            usuarios_ranking[u]["puntos"] += (p_base * pr["multiplicador"])
    return sorted(usuarios_ranking.items(), key=lambda x: (x[1]["puntos"], x[1]["plenos"]), reverse=True)

TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><title>Prode</title>
    <style>
        body { font-family: Arial; margin: 40px; background-color: #1a1a1a; color: #fff; }
        .nav { display: flex; justify-content: space-between; background: #2d2d2d; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .contenedor { display: flex; gap: 20px; }
        .columna-izq { flex: 2; } .columna-der { flex: 1; }
        .caja { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .partido-tarjeta { display: flex; justify-content: space-between; align-items: center; background: #3d3d3d; padding: 10px; border-radius: 8px; margin-bottom: 10px; }
        .input-gol { width: 40px; text-align: center; padding: 5px; background: #555; color: white; border: none; }
        .historial-item { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #444; }
    </style>
</head>
<body>
    <div class="nav"><span>Usuario: <strong>{{ usuario_actual|capitalize }}</strong></span><a href="/logout" style="color:red;">Salir</a></div>
    <div class="contenedor">
        <div class="columna-izq">
            <div class="caja">
                <h2>🗓️ Partidos</h2>
                {% for p in partidos %}
                    {% if p.inicio > ahora %}
                        <form action="/guardar" method="POST" class="partido-tarjeta">
                            <input type="hidden" name="partido_id" value="{{ p.id }}">
                            <span>{{ p.local }}</span>
                            <input type="number" name="goles_local" class="input-gol" required> - 
                            <input type="number" name="goles_visitante" class="input-gol" required>
                            <span>{{ p.visitante }}</span>
                            <button type="submit">Cargar</button>
                        </form>
                    {% endif %}
                {% endfor %}
            </div>
            <div class="caja">
                <h2>📜 Tus Apuestas (Historial)</h2>
                {% for prono in pronosticos if prono.usuario == usuario_actual %}
                    <div class="historial-item">
                        <span>{{ prono.local }} vs {{ prono.visitante }}</span>
                        <strong>{{ prono.goles_local }} - {{ prono.goles_visitante }}</strong>
                    </div>
                {% endfor %}
            </div>
        </div>
        <div class="columna-der">
            <div class="caja">
                <h2>🏆 Posiciones</h2>
                {% for u, s in ranking %}
                    <div class="historial-item"><span>{{ u|capitalize }}</span><strong>{{ s.puntos }} pts</strong></div>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""
# ... (Mantené el resto del código AUTH_TEMPLATE, app.route "/", "/login", "/logout", "/guardar" igual que antes)
# (Recordá cerrar con el if __name__ == "__main__": app.run(debug=True))

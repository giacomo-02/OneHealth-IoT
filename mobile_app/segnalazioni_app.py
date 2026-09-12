

"""
App segnalazioni acque contaminate - OneHealth Puglia
Flask mobile-first web app

Avvio: python3 segnalazioni_app.py
Accesso da smartphone (stessa rete Wi-Fi): http://<IP_LINUX>:5000

Dipendenze: pip3 install flask pymongo
"""

import math

import requests
from flask import Flask, Response, jsonify, request

# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # max 16 MB per foto

# Backend REST: l'app non accede mai al database direttamente, passa dalle API
BACKEND_URL = "http://127.0.0.1:8000"


def distanza_km(lat1, lon1, lat2, lon2):
    """Distanza in km tra due punti (formula dell'emisenoverso)."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return r * 2 * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# HTML MOBILE-FIRST
# ---------------------------------------------------------------------------
HTML = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#0077b6">
<title>OneHealth Puglia — Segnalazioni</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
     background:#f0f4f8;min-height:100vh;color:#1e293b}

header{
  background:linear-gradient(135deg,#0077b6 0%,#023e8a 100%);
  color:white;padding:22px 16px 18px;text-align:center;
  box-shadow:0 2px 8px rgba(0,0,0,0.2)
}
header h1{font-size:21px;font-weight:700;letter-spacing:-.3px}
header p{font-size:13px;opacity:.88;margin-top:5px}

.container{max-width:480px;margin:0 auto;padding:14px 14px 32px}

.card{
  background:white;border-radius:14px;
  padding:15px 15px 16px;margin-bottom:12px;
  box-shadow:0 1px 5px rgba(0,0,0,0.07)
}
.card-title{
  font-size:13px;font-weight:700;color:#475569;
  text-transform:uppercase;letter-spacing:.6px;margin-bottom:10px
}

/* GPS */
.gps-btn{
  width:100%;padding:14px 12px;
  background:#eff6ff;color:#1d4ed8;
  border:1.5px solid #bfdbfe;border-radius:10px;
  font-size:15px;font-weight:600;cursor:pointer;
  display:flex;align-items:center;justify-content:center;gap:9px;
  transition:all .2s
}
.gps-btn.ok{background:#f0fdf4;color:#15803d;border-color:#86efac}
.gps-btn.err{background:#fef2f2;color:#b91c1c;border-color:#fca5a5}
.coords{font-size:12px;color:#64748b;margin-top:7px;text-align:center;line-height:1.5}
.preset-sep{
  font-size:11px;color:#94a3b8;text-align:center;
  margin:10px 0 7px;letter-spacing:.4px
}
.preset-row{display:flex;flex-wrap:wrap;gap:6px}
.preset-pill{
  padding:6px 11px;border-radius:20px;
  background:#e0f2fe;color:#0369a1;
  border:1px solid #bae6fd;font-size:12px;font-weight:600;cursor:pointer;
  transition:background .15s
}
.preset-pill:active,.preset-pill.sel{background:#bae6fd;border-color:#7dd3fc}

/* SELECT */
select{
  width:100%;padding:13px 14px;
  border:1.5px solid #e2e8f0;border-radius:10px;
  font-size:15px;color:#1e293b;background:#f8fafc;
  appearance:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%2364748b' d='M6 8L0 0h12z'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 14px center
}
select:focus{outline:none;border-color:#0077b6;background-color:white}

/* GRAVITA' */
.grav-row{display:flex;gap:8px;margin-top:2px}
.grav-btn{
  flex:1;padding:11px 4px;border-radius:9px;
  border:1.5px solid #e2e8f0;background:#f8fafc;
  font-size:13px;font-weight:600;cursor:pointer;text-align:center;
  transition:all .15s
}
.grav-btn[data-v="bassa"].sel{background:#dcfce7;border-color:#86efac;color:#15803d}
.grav-btn[data-v="media"].sel{background:#fef9c3;border-color:#fde047;color:#854d0e}
.grav-btn[data-v="alta"].sel{background:#fee2e2;border-color:#fca5a5;color:#b91c1c}

/* TEXTAREA */
textarea{
  width:100%;padding:12px 14px;
  border:1.5px solid #e2e8f0;border-radius:10px;
  font-size:15px;color:#1e293b;background:#f8fafc;
  height:96px;resize:none;font-family:inherit;line-height:1.5
}
textarea:focus{outline:none;border-color:#0077b6;background:white}

/* FOTO */
.foto-label{
  display:flex;align-items:center;justify-content:center;gap:9px;
  width:100%;padding:14px;
  background:#f8fafc;border:2px dashed #cbd5e1;border-radius:10px;
  font-size:15px;font-weight:600;color:#475569;cursor:pointer;
  transition:all .2s
}
.foto-label.has{background:#f0fdf4;border-color:#86efac;color:#15803d;border-style:solid}
#foto-input{display:none}
#preview{
  width:100%;border-radius:10px;margin-top:10px;
  display:none;max-height:220px;object-fit:cover
}

/* NOME */
input[type=text]{
  width:100%;padding:13px 14px;
  border:1.5px solid #e2e8f0;border-radius:10px;
  font-size:15px;color:#1e293b;background:#f8fafc;font-family:inherit
}
input[type=text]:focus{outline:none;border-color:#0077b6;background:white}

/* SUBMIT */
.submit-btn{
  width:100%;padding:17px;margin-top:4px;
  background:linear-gradient(135deg,#0077b6,#023e8a);
  color:white;border:none;border-radius:14px;
  font-size:17px;font-weight:700;cursor:pointer;
  letter-spacing:.2px;box-shadow:0 3px 10px rgba(0,119,182,.35);
  transition:opacity .2s
}
.submit-btn:disabled{opacity:.5;cursor:not-allowed}
@keyframes spin{to{transform:rotate(360deg)}}
.spinner{
  display:none;width:20px;height:20px;
  border:3px solid rgba(255,255,255,.35);border-top-color:white;
  border-radius:50%;animation:spin .75s linear infinite
}
.loading .spinner{display:inline-block}
.loading .btn-text{display:none}

/* SUCCESSO */
#success-card{display:none;text-align:center;padding:40px 16px}
.ok-icon{font-size:72px;margin-bottom:14px}
#success-card h2{font-size:23px;color:#15803d;margin-bottom:8px}
#success-card p{color:#475569;font-size:15px;line-height:1.6}
.new-btn{
  margin-top:24px;padding:14px 36px;
  background:#0077b6;color:white;border:none;border-radius:12px;
  font-size:16px;font-weight:700;cursor:pointer
}
</style>
</head>
<body>

<header>
  <h1>🌊 OneHealth Puglia</h1>
  <p>Segnala un'anomalia nelle acque costiere</p>
</header>

<div class="container">

  <!-- FORM -->
  <form id="form">

    <!-- GPS -->
    <div class="card">
      <div class="card-title">📍 Posizione</div>
      <button type="button" class="gps-btn" id="gps-btn" onclick="rilevGps()">
        <span id="gps-icon">📡</span>
        <span id="gps-txt">Rileva posizione GPS reale</span>
      </button>
      <div class="coords" id="coords-txt"></div>
      <input type="hidden" id="lat" name="lat">
      <input type="hidden" id="lon" name="lon">
      <input type="hidden" id="acc" name="acc">
      <div class="preset-sep">— oppure scegli una posizione di esempio —</div>
      <div class="preset-row" id="preset-row">
        <button type="button" class="preset-pill" onclick="usaPreset(this,'Gallipoli',40.0565,17.9929)">📍 Gallipoli</button>
        <button type="button" class="preset-pill" onclick="usaPreset(this,'Otranto',40.1472,18.4910)">📍 Otranto</button>
        <button type="button" class="preset-pill" onclick="usaPreset(this,'Torre dell\\'Orso',40.3033,18.4633)">📍 Torre dell'Orso</button>
        <button type="button" class="preset-pill" onclick="usaPreset(this,'Taranto',40.4693,17.2383)">📍 Taranto</button>
        <button type="button" class="preset-pill" onclick="usaPreset(this,'Monopoli',40.9460,17.3070)">📍 Monopoli</button>
        <button type="button" class="preset-pill" onclick="usaPreset(this,'Leuca',39.7975,18.3580)">📍 Leuca</button>
        <button type="button" class="preset-pill" onclick="usaPreset(this,'Bari',41.1290,16.8700)">📍 Bari</button>
        <button type="button" class="preset-pill" onclick="usaPreset(this,'Brindisi',40.6400,17.9600)">📍 Brindisi</button>
        <button type="button" class="preset-pill" onclick="usaPreset(this,'Vieste',41.8820,16.1780)">📍 Vieste (Gargano)</button>
      </div>
      <div class="preset-sep">— oppure descrivi la posizione a parole —</div>
      <input type="text" name="posizione_testo" id="posizione_testo"
             placeholder="es. Spiaggia di Torre dell'Orso, vicino al porto di Gallipoli…"
             autocomplete="off"
             style="width:100%;padding:11px 13px;border:1.5px solid #e2e8f0;border-radius:10px;
                    font-size:14px;color:#1e293b;background:#f8fafc;font-family:inherit">
      <div style="font-size:11px;color:#94a3b8;margin-top:5px;text-align:center">
        Se compili questo campo ha la <b>priorità sul GPS</b>: l'operatore ricava le
        coordinate dalla dashboard
      </div>
    </div>

    <!-- BALNEABILITA' VICINO -->
    <div class="card" id="vicine-card" style="display:none">
      <div class="card-title">🏖️ Balneabilità nelle vicinanze</div>
      <div style="font-size:12px;color:#64748b;margin-bottom:8px">
        Boe entro 30 km dalla tua posizione
      </div>
      <div id="mini-map" style="height:200px;border-radius:10px;margin-bottom:10px;display:none;
                                border:1px solid #e2e8f0"></div>
      <div id="vicine-content"></div>
    </div>

    <!-- TIPO -->
    <div class="card">
      <div class="card-title">⚠️ Tipo di problema</div>
      <select name="tipo" id="tipo" required>
        <option value="">— Seleziona —</option>
        <option>Odore anomalo</option>
        <option>Colore anomalo</option>
        <option>Schiume in superficie</option>
        <option>Meduse in massa</option>
        <option>Inquinamento visibile (plastica / rifiuti)</option>
        <option>Olio / idrocarburi</option>
        <option>Moria di pesci</option>
        <option>Altro</option>
      </select>
    </div>

    <!-- GRAVITA' -->
    <div class="card">
      <div class="card-title">🚦 Gravità</div>
      <div class="grav-row" id="grav-row">
        <button type="button" class="grav-btn" data-v="bassa" onclick="selGrav(this)">🟢 Bassa</button>
        <button type="button" class="grav-btn" data-v="media" onclick="selGrav(this)">🟡 Media</button>
        <button type="button" class="grav-btn" data-v="alta"  onclick="selGrav(this)">🔴 Alta</button>
      </div>
      <input type="hidden" id="gravita" name="gravita" value="">
    </div>

    <!-- DESCRIZIONE -->
    <div class="card">
      <div class="card-title">📝 Descrizione</div>
      <textarea name="descrizione" id="descrizione"
                placeholder="Descrivi brevemente cosa hai visto…"></textarea>
    </div>

    <!-- FOTO -->
    <div class="card">
      <div class="card-title">📷 Foto (opzionale)</div>
      <label class="foto-label" id="foto-label" for="foto-input">
        <span>📸</span> Scatta o carica una foto
      </label>
      <input type="file" id="foto-input" name="foto"
             accept="image/*" capture="environment"
             onchange="anteprimaFoto(this)">
      <img id="preview" alt="Anteprima">
    </div>

    <!-- NOME -->
    <div class="card">
      <div class="card-title">👤 Il tuo nome (opzionale)</div>
      <input type="text" name="nome" id="nome"
             placeholder="Nome e cognome o anonimo">
    </div>

    <button type="button" class="submit-btn" id="submit-btn" onclick="invia()">
      <span class="btn-text">📤 Invia Segnalazione</span>
      <span class="spinner"></span>
    </button>
  </form>

  <!-- SUCCESSO -->
  <div id="success-card">
    <div class="ok-icon">✅</div>
    <h2>Segnalazione inviata!</h2>
    <p>Grazie per la collaborazione.<br>
       I dati sono stati registrati e saranno<br>
       analizzati dal team OneHealth Puglia.</p>
    <button class="new-btn" onclick="nuovaSegnalazione()">+ Nuova segnalazione</button>
  </div>

</div><!-- /container -->

<script>
// Posizione di esempio (demo)
function usaPreset(el, nome, lat, lon) {
  document.querySelectorAll('.preset-pill').forEach(p => p.classList.remove('sel'));
  el.classList.add('sel');
  document.getElementById('lat').value = lat;
  document.getElementById('lon').value = lon;
  document.getElementById('acc').value = 10;
  const btn = document.getElementById('gps-btn');
  btn.className = 'gps-btn ok';
  document.getElementById('gps-icon').textContent = '📍';
  document.getElementById('gps-txt').textContent = nome + ' (demo)';
  document.getElementById('coords-txt').innerHTML =
    `Lat: <b>${lat}</b> &nbsp; Lon: <b>${lon}</b> &nbsp; <span style="color:#0369a1">[posizione simulata]</span>`;
  mostraVicine(lat, lon);
}

// Consigli balneabilità in base alle boe più vicine
async function mostraVicine(lat, lon) {
  const card = document.getElementById('vicine-card');
  const box  = document.getElementById('vicine-content');
  card.style.display = 'block';
  box.innerHTML = '<div style="text-align:center;color:#94a3b8;font-size:13px;padding:6px">Ricerca località vicine…</div>';
  try {
    const res  = await fetch(`/vicine?lat=${lat}&lon=${lon}`);
    const data = await res.json();
    if (!data.ok) {
      box.innerHTML = '<div style="text-align:center;color:#94a3b8;font-size:13px;padding:6px">Dati boe non disponibili al momento.</div>';
      return;
    }
    if (!data.localita || !data.localita.length) {
      box.innerHTML = '<div style="text-align:center;color:#94a3b8;font-size:13px;padding:6px">Nessuna boa entro 30 km dalla tua posizione.</div>';
      disegnaMappa(parseFloat(lat), parseFloat(lon), []);
      return;
    }
    const ok  = data.localita.filter(l => l.consigliata);
    const no  = data.localita.filter(l => !l.consigliata);
    let html = '';
    if (ok.length) {
      html += '<div style="font-size:12px;font-weight:700;color:#15803d;margin:4px 0 2px">✅ Consigliate</div>';
      ok.forEach(l => html += locRow(l, true));
    }
    if (no.length) {
      html += '<div style="font-size:12px;font-weight:700;color:#b91c1c;margin:12px 0 2px">⛔ Sconsigliate</div>';
      no.forEach(l => html += locRow(l, false));
    }
    box.innerHTML = html;
    disegnaMappa(parseFloat(lat), parseFloat(lon), data.localita);
  } catch(e) {
    box.innerHTML = '<div style="text-align:center;color:#b91c1c;font-size:13px;padding:6px">Errore nel recupero dei dati.</div>';
  }
}

let miniMap = null, miniLayer = null;
function disegnaMappa(lat, lon, localita) {
  const el = document.getElementById('mini-map');
  el.style.display = 'block';
  if (!miniMap) {
    miniMap = L.map('mini-map', { attributionControl: false });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                { maxZoom: 18 }).addTo(miniMap);
    miniLayer = L.layerGroup().addTo(miniMap);
  }
  miniLayer.clearLayers();
  miniMap.setView([lat, lon], 10);
  setTimeout(() => miniMap.invalidateSize(), 100);

  // posizione utente
  L.circleMarker([lat, lon], {
    radius: 8, color: '#1d4ed8', fillColor: '#3b82f6', fillOpacity: 1, weight: 2
  }).addTo(miniLayer).bindPopup('📍 La tua posizione');

  // boe
  const pts = [[lat, lon]];
  localita.forEach(l => {
    const good = l.consigliata;
    L.circleMarker([l.lat, l.lon], {
      radius: 7,
      color: good ? '#15803d' : '#b91c1c',
      fillColor: good ? '#22c55e' : '#ef4444',
      fillOpacity: 0.9, weight: 2
    }).addTo(miniLayer)
      .bindPopup(`<b>${l.nome}</b><br>${l.comune} · ${l.distanza_km} km<br>` +
                 `Qualità: <b>${l.classificazione}</b>`);
    pts.push([l.lat, l.lon]);
  });

  // inquadra tutti i punti
  if (pts.length > 1) {
    miniMap.fitBounds(pts, { padding: [25, 25], maxZoom: 12 });
  }
}
function locRow(l, good) {
  const c  = good ? '#15803d' : '#b91c1c';
  const bg = good ? '#f0fdf4' : '#fef2f2';
  const bd = good ? '#86efac' : '#fca5a5';
  return `<div style="display:flex;justify-content:space-between;align-items:center;
            background:${bg};border:1px solid ${bd};border-radius:9px;padding:9px 11px;margin-top:6px">
            <div><div style="font-weight:600;font-size:14px;color:#1e293b">${l.nome}</div>
              <div style="font-size:11px;color:#64748b">${l.comune} · ${l.distanza_km} km da te</div></div>
            <div style="font-size:12px;font-weight:700;color:${c};text-align:right">${l.classificazione}</div>
          </div>`;
}

// GPS reale
function rilevGps() {
  const btn  = document.getElementById('gps-btn');
  const icon = document.getElementById('gps-icon');
  const txt  = document.getElementById('gps-txt');
  icon.textContent = '⏳'; txt.textContent = 'Rilevamento…';
  if (!navigator.geolocation) {
    btn.className = 'gps-btn err';
    icon.textContent = '❌'; txt.textContent = 'GPS non disponibile';
    return;
  }
  navigator.geolocation.getCurrentPosition(
    pos => {
      const la = pos.coords.latitude.toFixed(6);
      const lo = pos.coords.longitude.toFixed(6);
      const ac = Math.round(pos.coords.accuracy);
      document.getElementById('lat').value = la;
      document.getElementById('lon').value = lo;
      document.getElementById('acc').value = ac;
      btn.className = 'gps-btn ok';
      icon.textContent = '✅'; txt.textContent = 'Posizione rilevata';
      document.getElementById('coords-txt').innerHTML =
        `Lat: <b>${la}</b> &nbsp; Lon: <b>${lo}</b> &nbsp; (±${ac}m)`;
      mostraVicine(la, lo);
    },
    () => {
      btn.className = 'gps-btn err';
      icon.textContent = '❌'; txt.textContent = 'Impossibile rilevare il GPS';
    },
    { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
  );
}

// Gravità
function selGrav(el) {
  document.querySelectorAll('.grav-btn').forEach(b => b.classList.remove('sel'));
  el.classList.add('sel');
  document.getElementById('gravita').value = el.dataset.v;
}

// Foto
function anteprimaFoto(input) {
  if (!input.files || !input.files[0]) return;
  const reader = new FileReader();
  reader.onload = e => {
    const prev = document.getElementById('preview');
    prev.src = e.target.result;
    prev.style.display = 'block';
    document.getElementById('foto-label').className = 'foto-label has';
    document.getElementById('foto-label').innerHTML = '<span>✅</span> Foto caricata';
  };
  reader.readAsDataURL(input.files[0]);
}

// Invio
async function invia() {
  const tipo = document.getElementById('tipo').value;
  if (!tipo) { alert('Seleziona il tipo di problema.'); return; }
  const btn = document.getElementById('submit-btn');
  btn.disabled = true; btn.classList.add('loading');
  try {
    const res = await fetch('/segnala', { method:'POST', body: new FormData(document.getElementById('form')) });
    const data = await res.json();
    if (data.ok) {
      document.getElementById('form').style.display = 'none';
      document.getElementById('success-card').style.display = 'block';
      window.scrollTo(0, 0);
    } else {
      alert('Errore: ' + (data.error || 'sconosciuto'));
    }
  } catch(e) {
    alert('Errore di rete. Controlla la connessione.');
  } finally {
    btn.disabled = false; btn.classList.remove('loading');
  }
}

// Reset
function nuovaSegnalazione() {
  document.getElementById('form').reset();
  document.getElementById('form').style.display = 'block';
  document.getElementById('success-card').style.display = 'none';
  document.getElementById('preview').style.display = 'none';
  document.getElementById('coords-txt').textContent = '';
  document.getElementById('vicine-card').style.display = 'none';
  document.getElementById('gps-btn').className = 'gps-btn';
  document.getElementById('gps-icon').textContent = '📡';
  document.getElementById('gps-txt').textContent = 'Rileva posizione GPS reale';
  document.querySelectorAll('.preset-pill').forEach(p => p.classList.remove('sel'));
  document.getElementById('foto-label').className = 'foto-label';
  document.getElementById('foto-label').innerHTML = '<span>📸</span> Scatta o carica una foto';
  document.querySelectorAll('.grav-btn').forEach(b => b.classList.remove('sel'));
  window.scrollTo(0, 0);
}
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return Response(HTML, content_type="text/html; charset=utf-8")


@app.route("/segnala", methods=["POST"])
def segnala():
    """Inoltra la segnalazione al backend. Passa da Flask (stessa origine HTTPS)
    cosi' il browser non deve contattare direttamente il backend HTTP:8000
    (che darebbe errore di protocollo misto / rete)."""

    try:

        campi = [
            "tipo", "descrizione", "gravita", "nome",
            "posizione_testo", "lat", "lon", "acc"
        ]

        data = {}

        for k in campi:
            v = request.form.get(k)
            if v is not None and v != "":
                data[k] = v

        if not data.get("tipo"):
            return jsonify({"ok": False, "error": "tipo mancante"}), 400

        files = None

        foto = request.files.get("foto")

        if foto and foto.filename:
            files = {
                "foto": (foto.filename, foto.stream, foto.mimetype)
            }

        r = requests.post(
            f"{BACKEND_URL}/segnalazioni/invia",
            data=data,
            files=files,
            timeout=15
        )

        if r.status_code >= 300:
            return jsonify({"ok": False, "error": r.text}), 500

        return jsonify({"ok": True})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/vicine")
def vicine():
    """Boe/localita' piu' vicine alla posizione dell'utente.
    I dati delle boe si leggono dal backend (API REST), non dal database."""

    try:
        lat = float(request.args.get("lat", ""))
        lon = float(request.args.get("lon", ""))

    except (TypeError, ValueError):
        return jsonify({
            "ok": False,
            "error": "coordinate mancanti"
        }), 400


    try:

        r = requests.get(
            f"{BACKEND_URL}/boe/ultime",
            timeout=10
        )

        r.raise_for_status()

        boe = r.json()


        loc = []


        for b in boe:

            b_lat = b.get("latitudine")
            b_lon = b.get("longitudine")

            if b_lat is None or b_lon is None:
                continue


            dist = distanza_km(lat, lon, b_lat, b_lon)

            if dist > 30:
                continue


            cls = b.get("classificazione", "")


            loc.append({

                "nome": b.get("nome_boa", b.get("id_boa", "")),

                "comune": b.get("comune", ""),

                "classificazione": cls,

                "consigliata":
                    cls in (
                        "Eccellente",
                        "Buona"
                    ),

                "lat": round(b_lat, 6),

                "lon": round(b_lon, 6),

                "distanza_km": round(dist, 1)

            })


        loc.sort(
            key=lambda x: x["distanza_km"]
        )


        return jsonify({
            "ok": True,
            "localita": loc,
            "raggio_km": 30
        })


    except Exception as e:

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "127.0.0.1"
    print("=" * 50)
    print("  OneHealth Puglia — App Segnalazioni")
    print(f"  Locale:  http://localhost:8080")
    print(f"  Rete:    http://{ip}:8080")
    print("  (usa l'IP di rete per accedere da smartphone)")
    print("=" * 50)
    # HTTP (niente HTTPS auto-firmato): l'invio dai dispositivi in rete
    # funziona in modo affidabile. Il GPS reale da smartphone non e'
    # disponibile su HTTP non-localhost (i browser lo bloccano su origini
    # non sicure): usare i preset o il campo testo per la posizione.
    app.run(host="0.0.0.0", port=8080, debug=False)


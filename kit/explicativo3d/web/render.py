# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Render do Explicativo 3D no navegador (Three.js): o caminho para máquina sem placa de vídeo e sem Blender.

Abre um Chromium sem janela, monta a cena do episódio (um cena.js) e pede quadro a quadro, no tempo do vídeo e não
no relógio: o resultado é igual em qualquer máquina, só muda quanto demora. Grava em PASTA o mesmo que o cena.py do
Blender, então o resto do kit (compor.py, capa, QA) não muda nada:
- quadros/q_0001.png ... (RGBA, fundo transparente);
- etiquetas.json (posição na tela de cada rótulo, quadro a quadro, 0..1);
- render.json (quadros, segundos de render e a placa: "SwiftShader" é o render por CPU).
Com --stills renderiza só os instantes pedidos, em stills/still_<t>.png.

Uso (a partir da pasta kit/):
    python explicativo3d/web/render.py --teste                     # confere o navegador e mostra a placa
    python explicativo3d/web/render.py CENA.js --tempos T.json --saida PASTA [--episodio EP.json] [--fps 30]
           [--stills 0.5,5.0] [--leve] [--ate SEGUNDOS] [--placa software|gpu] [--chromium CAMINHO]

Navegador: o do Playwright (python -m playwright install chromium). Sem ele, use o Chromium do sistema com
--chromium CAMINHO ou a variável X3D_CHROMIUM; se nenhum for dado e o do Playwright faltar, o script procura um
Chromium, Chrome ou Edge instalado.
"""
import argparse
import base64
import json
import mimetypes
import os
import platform
import shutil
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

AQUI = Path(__file__).resolve().parent
X3D = AQUI.parent

TIPOS = {".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json", ".html": "text/html",
         ".glb": "model/gltf-binary", ".gltf": "model/gltf+json", ".png": "image/png", ".jpg": "image/jpeg",
         ".bin": "application/octet-stream"}

FLAGS_COMUNS = ["--disable-dev-shm-usage", "--hide-scrollbars", "--mute-audio", "--no-first-run"]
# SwiftShader é o WebGL por CPU do próprio Chromium: o mesmo que roda numa sessão na nuvem sem placa.
FLAGS_SOFTWARE = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"]
FLAGS_GPU = ["--ignore-gpu-blocklist", "--force_high_performance_gpu"]

TESTE_JS = """() => { const c = document.createElement('canvas'); const gl = c.getContext('webgl2');
  if (!gl) return null; const e = gl.getExtension('WEBGL_debug_renderer_info');
  return e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER); }"""


def erro(msg, fazer):
    print(f"ERRO: {msg}\nO QUE FAZER: {fazer}", file=sys.stderr, flush=True)
    raise SystemExit(1)


# ------------------------------------------------------------------------------------------------ servidor local

class Servidor:
    """HTTP em 127.0.0.1 (porta livre): o navegador não carrega módulo ES por file://.

    Rotas: /web/ (motor e Three.js), /cena/ (pasta do cena.js), /modelos/ (GLB do kit) e /dados.json (na memória).
    """

    def __init__(self, rotas, dados):
        rotas = {k: Path(v).resolve() for k, v in rotas.items()}
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")

        class Pedido(SimpleHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                caminho = self.path.split("?", 1)[0]
                if caminho == "/dados.json":
                    return self._enviar(corpo, "application/json")
                for prefixo, base in rotas.items():
                    if caminho.startswith(prefixo):
                        arq = (base / unquote(caminho[len(prefixo):])).resolve()
                        if arq.is_file() and arq.is_relative_to(base):
                            tipo = TIPOS.get(arq.suffix.lower()) or mimetypes.guess_type(arq.name)[0] or "application/octet-stream"
                            return self._enviar(arq.read_bytes(), tipo)
                self.send_error(404)

            def _enviar(self, dados_, tipo):
                self.send_response(200)
                self.send_header("Content-Type", tipo)
                self.send_header("Content-Length", str(len(dados_)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(dados_)

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Pedido)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def __enter__(self):
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *a):
        self.httpd.shutdown()
        self.httpd.server_close()


# ------------------------------------------------------------------------------------------------ navegador

def chromium_do_sistema():
    """Chromium, Chrome ou Edge instalado (para quando o download do Playwright não é possível)."""
    for nome in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "microsoft-edge"):
        if shutil.which(nome):
            return shutil.which(nome)
    sistema = platform.system()
    if sistema == "Windows":
        raizes = [os.environ.get(v, "") for v in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA")]
        relativos = ["Google/Chrome/Application/chrome.exe", "Chromium/Application/chrome.exe",
                     "Microsoft/Edge/Application/msedge.exe"]
        candidatos = [Path(r, rel) for r in raizes if r for rel in relativos]
    elif sistema == "Darwin":
        candidatos = [Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                      Path("/Applications/Chromium.app/Contents/MacOS/Chromium")]
    else:
        candidatos = [Path("/usr/bin/chromium"), Path("/snap/bin/chromium")]
    return next((str(c) for c in candidatos if c.is_file()), None)


def abrir_navegador(pw, placa, chromium):
    flags = FLAGS_COMUNS + (FLAGS_SOFTWARE if placa == "software" else FLAGS_GPU)
    if placa == "gpu" and platform.system() == "Windows":
        flags.append("--use-angle=d3d11")
    pedido = chromium or os.environ.get("X3D_CHROMIUM")
    if pedido:
        if not Path(pedido).is_file():
            erro(f"o navegador indicado não existe: {pedido}",
                 "confira o caminho em --chromium ou na variável X3D_CHROMIUM (no Linux: which chromium)")
        return pw.chromium.launch(headless=True, executable_path=pedido, args=flags), pedido
    try:
        return pw.chromium.launch(headless=True, args=flags), "Chromium do Playwright"
    except Exception as e:  # navegador do Playwright não baixado
        if "Executable doesn't exist" not in str(e) and "playwright install" not in str(e):
            raise
        achado = chromium_do_sistema()
        if not achado:
            erro("o Playwright está instalado, mas falta o navegador dele e não achei um Chromium no sistema",
                 "rode: python -m playwright install --only-shell --with-deps chromium (no Linux da nuvem, se o download for "
                 "bloqueado: apt-get install -y chromium e use --chromium /usr/bin/chromium)")
        print(f"aviso: navegador do Playwright não encontrado; usando {achado}", flush=True)
        return pw.chromium.launch(headless=True, executable_path=achado, args=flags), achado


def importar_playwright():
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError:
        erro("falta o Playwright, que abre o navegador sem janela para renderizar o 3D",
             "rode: python -m pip install playwright e depois python -m playwright install --only-shell chromium")


# ------------------------------------------------------------------------------------------------ render

def ler_json(caminho, o_que):
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except FileNotFoundError:
        erro(f"não achei {o_que}: {caminho}", "confira o caminho passado no comando")
    except json.JSONDecodeError as e:
        erro(f"{o_que} está com o JSON quebrado ({caminho}: {e})", "corrija o arquivo (vírgula ou aspas sobrando)")


def png_de(data_url):
    return base64.b64decode(data_url.split(",", 1)[1])


def teste(a):
    with importar_playwright()() as pw:
        nav, origem = abrir_navegador(pw, a.placa, a.chromium)
        pg = nav.new_page()
        pg.goto("about:blank")
        placa = pg.evaluate(TESTE_JS)
        versao = nav.version
        nav.close()
    if not placa:
        erro("o navegador abriu, mas sem WebGL 2", "rode de novo com --placa software (render por CPU)")
    print(f"Navegador: {origem} {versao}\nWebGL: {placa}\nTESTE_OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cena", nargs="?", help="cena.js do episódio (exporta montar e quadro)")
    ap.add_argument("--tempos", help="tempos.json da narração (palavra a palavra)")
    ap.add_argument("--saida", help="pasta de trabalho do episódio")
    ap.add_argument("--episodio", help="episodio.json (padrão: o da pasta do cena.js)")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--largura", type=int, default=1080)
    ap.add_argument("--altura", type=int, default=1920)
    ap.add_argument("--stills", help="só estes instantes (segundos, separados por vírgula)")
    ap.add_argument("--leve", action="store_true", help="metade da resolução (prévia; o compor.py amplia)")
    ap.add_argument("--ate", type=float, help="só os primeiros SEGUNDOS (teste de velocidade)")
    ap.add_argument("--placa", choices=("software", "gpu"), default="software",
                    help="software = WebGL por CPU (SwiftShader, igual à nuvem); gpu = placa de vídeo, se houver")
    ap.add_argument("--chromium", help="caminho de um Chromium/Chrome do sistema (no lugar do do Playwright)")
    ap.add_argument("--teste", action="store_true", help="só abre o navegador e mostra o WebGL usado")
    a = ap.parse_args()
    if a.teste:
        return teste(a)
    if not (a.cena and a.tempos and a.saida):
        erro("faltou a cena, o --tempos ou a --saida", "veja o uso com: python explicativo3d/web/render.py --help")

    cena = Path(a.cena).resolve()
    if not cena.is_file():
        erro(f"não achei a cena: {cena}", "passe o caminho do cena.js do episódio")
    episodio = Path(a.episodio) if a.episodio else cena.parent / "episodio.json"
    escala = 50 if a.leve else 100
    larg, alt = a.largura * escala // 100, a.altura * escala // 100
    dados = {"cena": f"/cena/{cena.name}", "largura": larg, "altura": alt, "fps": a.fps,
             "tempos": ler_json(a.tempos, "o tempos.json"), "episodio": ler_json(episodio, "o episodio.json")}
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    rotas = {"/web/": AQUI, "/cena/": cena.parent, "/modelos/": X3D / "modelos"}

    sync_playwright = importar_playwright()
    with Servidor(rotas, dados) as srv, sync_playwright() as pw:
        nav, origem = abrir_navegador(pw, a.placa, a.chromium)
        pg = nav.new_page(viewport={"width": larg, "height": alt}, device_scale_factor=1)
        erros_js = []
        pg.on("pageerror", lambda e: erros_js.append(str(e)))
        pg.on("console", lambda m: erros_js.append(m.text) if m.type == "error" else None)
        t0 = time.perf_counter()
        pg.goto(f"{srv.url}/web/pagina.html")
        try:
            pg.wait_for_function("window.X3D_PRONTO || window.X3D_ERRO", timeout=300_000)
        except Exception:
            erro("a cena não terminou de montar em 5 minutos", "rode com --stills 0.5 para ver o erro mais rápido")
        falha = pg.evaluate("window.X3D_ERRO || null")
        if falha:
            detalhe = "\n".join(dict.fromkeys([falha, *erros_js]))
            erro(f"a cena deu erro no navegador:\n{detalhe}", "corrija o cena.js na linha indicada e rode de novo")
        info = pg.evaluate("({duracao: X3D.duracao, placa: X3D.placa, amostras: X3D.amostras, montagem: X3D.montagem})")
        n = int(round(info["duracao"] * a.fps))
        print(f"montagem {time.perf_counter() - t0:.1f} s, duração {info['duracao']:.2f} s, {n} quadros, "
              f"{larg}x{alt}, {info['placa']}", flush=True)

        if a.stills:
            (saida / "stills").mkdir(exist_ok=True)
            for ts in a.stills.split(","):
                f = int(float(ts) * a.fps) + 1  # mesmo arredondamento do cena.py
                (saida / "stills" / f"still_{float(ts):05.2f}.png").write_bytes(png_de(pg.evaluate("t => X3D.png(t)", (f - 1) / a.fps)))
            print(f"STILLS_OK {saida / 'stills'}", flush=True)
            nav.close()
            return

        # âncoras de todos os quadros (mesmo com --ate, como no Blender); chaves "1", "2"... como o json do Python
        ancoras = pg.evaluate("ts => X3D.ancoras(ts)", [(f - 1) / a.fps for f in range(1, n + 1)])
        (saida / "etiquetas.json").write_text(json.dumps({str(f): v for f, v in enumerate(ancoras, 1)}), encoding="utf-8")

        fim = min(n, int(a.ate * a.fps)) if a.ate else n
        pasta = saida / "quadros"
        pasta.mkdir(exist_ok=True)
        for velho in pasta.glob("q_*.png"):  # render anterior mais longo deixaria quadros sobrando no fim
            velho.unlink()
        t0 = time.perf_counter()
        aviso = max(1, fim // 10)
        with ThreadPoolExecutor(max_workers=2) as gravador:  # grava o PNG enquanto o navegador faz o próximo
            for f in range(1, fim + 1):
                url = pg.evaluate("t => X3D.png(t)", (f - 1) / a.fps)
                gravador.submit(lambda u=url, f=f: (pasta / f"q_{f:04d}.png").write_bytes(png_de(u)))
                if f % aviso == 0 or f == fim:
                    dt = time.perf_counter() - t0
                    print(f"   quadro {f}/{fim} ({dt / f:.3f} s/quadro)", flush=True)
        dt = time.perf_counter() - t0
        versao = nav.version
        nav.close()

    info_render = {"quadros": fim, "segundos": round(dt, 1), "s_por_quadro": round(dt / fim, 3),
                   "duracao_video": round(info["duracao"], 2), "amostras": info["amostras"], "escala": escala,
                   "motor": "three.js r187", "navegador": f"{origem} {versao}", "placa": info["placa"]}
    (saida / "render.json").write_text(json.dumps(info_render, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"RENDER_OK {dt:.1f} s = {dt / fim:.2f} s/quadro ({info['placa']})", flush=True)


if __name__ == "__main__":
    main()

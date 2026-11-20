# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Motor de render: desenha cada quadro com Skia e manda direto para o ffmpeg, sem arquivos intermediários.

- PC com placa de vídeo: desenho na GPU (Skia sobre OpenGL por glfw, janela oculta; no notebook com duas placas, a
  dedicada) + encoder da placa (NVENC -> Quick Sync -> AMF -> VideoToolbox), testado de verdade com um encode curto.
  Um processo só: a GPU já é o paralelo.
- Nuvem, celular ou PC sem placa: desenho na CPU (raster) + libx264, com o vídeo dividido em partes desenhadas por
  processos paralelos (um por núcleo, x264 com 1 thread cada) e juntadas sem recodificar.
- OpenGL de software (llvmpipe, SwiftShader, "GDI Generic", área de trabalho remota) conta como sem placa: desenhar
  nele num processo só é mais lento que a CPU em paralelo.
- `--cpu` (ou MAQUINA_CPU=1, ou render.gpu = "nao") força CPU + libx264.
- Vídeos gravados ao mesmo tempo (`encoders_simultaneos`) abrem no máximo `render.sessoes_gpu` encoders da placa
  (padrão 3); placa comum recusa sessões de NVENC além do limite do driver, e as que passam vão para o libx264.

Uso típico, dentro do script do episódio:

    from maquina.motor import renderizar
    renderizar(quadro, duracao, "ep.mp4", audio="audio/mix_norm.wav", cpu="--cpu" in sys.argv, marcos=[1.0, 5.0])
"""
import os
import platform
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
import skia

import licenca
from config import CFG, ffmpeg

from .desenho import FPS, H, W

R = CFG["render"]
INFO_BGRA = skia.ImageInfo.Make(W, H, skia.kBGRA_8888_ColorType, skia.kPremul_AlphaType)
GL_SOFTWARE = ("llvmpipe", "softpipe", "swiftshader", "gdi generic", "basic render", "software rasterizer")


def forcar_cpu(cpu=False):
    return bool(cpu) or os.environ.get("MAQUINA_CPU") == "1" or str(R.get("gpu", "auto")).lower() in ("nao", "não", "false", "0")


# ---------------------------------------------------------------- superfície

def _prefere_placa_dedicada():
    """Notebook com duas placas (Optimus): o Windows abre o OpenGL na integrada, a não ser que o processo já tenha
    carregado a biblioteca da NVIDIA. Carregar nvapi64.dll antes do contexto manda o desenho para a placa dedicada;
    sem NVIDIA a DLL não existe e nada muda."""
    if sys.platform == "win32":
        import ctypes

        try:
            ctypes.WinDLL("nvapi64.dll")
        except OSError:
            pass


def _placa_gl():
    """Nome da placa do contexto OpenGL atual (GL_RENDERER), lido da biblioteca do sistema; "" se não der para ler."""
    import ctypes
    import ctypes.util

    try:
        if sys.platform == "win32":
            lib = ctypes.WinDLL("opengl32")
        elif sys.platform == "darwin":
            lib = ctypes.CDLL("/System/Library/Frameworks/OpenGL.framework/OpenGL")
        else:
            lib = ctypes.CDLL(ctypes.util.find_library("GL") or "libGL.so.1")
        lib.glGetString.restype = ctypes.c_char_p
        lib.glGetString.argtypes = [ctypes.c_uint]
        return (lib.glGetString(0x1F01) or b"").decode(errors="replace").strip()
    except Exception:
        return ""


class Superficie:
    """Superfície de desenho. `backend` diz onde ela roda: "GPU (OpenGL)" ou "CPU (raster)"."""

    def __init__(self, w=W, h=H, cpu=False, transparente=False):
        self.w, self.h = w, h
        self.ctx = None
        self._glfw = None
        self.motivo_cpu = ""
        self.placa = ""
        if forcar_cpu(cpu):
            self.motivo_cpu = "CPU forçada"
        else:
            try:
                self._abre_gpu()
            except ModuleNotFoundError:
                self.motivo_cpu = "glfw não instalado (pip install glfw)"
                self._fecha_gpu()
            except Exception as e:  # sem placa, sem tela, sem driver: segue na CPU
                self.motivo_cpu = f"{type(e).__name__}: {e}"
                self._fecha_gpu()
        if self.ctx is None:
            self.surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(w, h, skia.kBGRA_8888_ColorType, skia.kPremul_AlphaType))
        self.backend = f"GPU (OpenGL: {self.placa or 'placa'})" if self.ctx is not None else "CPU (raster)"
        self.canvas = self.surf.getCanvas()
        self.info = skia.ImageInfo.Make(w, h, skia.kBGRA_8888_ColorType,
                                        skia.kUnpremul_AlphaType if transparente else skia.kPremul_AlphaType)
        self.buf = np.empty((h, w, 4), dtype=np.uint8)

    def _abre_gpu(self):
        if sys.platform.startswith("linux") and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
            raise RuntimeError("sem tela (Linux headless)")
        import glfw

        _prefere_placa_dedicada()
        if not glfw.init():
            raise RuntimeError("glfw.init falhou")
        self._glfw = glfw
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        janela = glfw.create_window(64, 64, "maquina", None, None)
        if not janela:
            raise RuntimeError("sem contexto OpenGL")
        glfw.make_context_current(janela)
        self.placa = _placa_gl()
        if any(k in self.placa.lower() for k in GL_SOFTWARE):
            raise RuntimeError(f"OpenGL de software ({self.placa}), sem placa de verdade")
        ctx = skia.GrDirectContext.MakeGL()
        if ctx is None:
            raise RuntimeError("Skia não abriu contexto GL")
        surf = skia.Surface.MakeRenderTarget(ctx, skia.Budgeted.kNo, skia.ImageInfo.MakeN32Premul(self.w, self.h))
        if surf is None:
            raise RuntimeError("sem superfície na GPU")
        self.ctx, self.surf = ctx, surf

    def _fecha_gpu(self):
        """Solta tudo que vive na GPU ANTES de fechar o contexto OpenGL (senão o processo trava ao sair)."""
        from . import cinema

        cinema._APOIO.clear()
        if self.ctx is not None:
            self.canvas = None
            self.surf = None
            try:
                self.ctx.flushAndSubmit()
                self.ctx.releaseResourcesAndAbandonContext()
            except Exception:
                pass
        self.ctx = None
        if self._glfw is not None:
            try:
                self._glfw.terminate()
            except Exception:
                pass
            self._glfw = None

    def ler(self):
        """Termina o quadro e devolve os pixels BGRA (h, w, 4)."""
        if self.ctx is not None:
            self.ctx.flushAndSubmit()
        self.surf.readPixels(self.info, self.buf, self.w * 4, 0, 0)
        return self.buf

    def salvar_png(self, caminho):
        arr = self.ler()
        rgba = np.ascontiguousarray(arr[:, :, [2, 1, 0, 3]])
        skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType).save(str(caminho))

    def fechar(self):
        self._fecha_gpu()


# ---------------------------------------------------------------- encoder

def _bufsize(teto):
    n = float(teto.rstrip("MmKk"))
    return f"{n * 2:g}{teto[-1]}" if teto[-1].isalpha() else str(int(n * 2))


def args_encoder(nome):
    q, teto = int(R.get("qualidade", 21)), str(R.get("teto_bitrate", "8M"))
    buf = _bufsize(teto)
    return {
        "h264_nvenc": ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", str(q), "-b:v", "0",
                       "-maxrate", teto, "-bufsize", buf],
        "h264_qsv": ["-c:v", "h264_qsv", "-preset", "slow", "-global_quality", str(q + 2), "-maxrate", teto, "-bufsize", buf],
        "h264_amf": ["-c:v", "h264_amf", "-quality", "quality", "-rc", "vbr_peak", "-b:v", "5M", "-maxrate", teto],
        "h264_videotoolbox": ["-c:v", "h264_videotoolbox", "-b:v", "6M", "-maxrate", teto],
        "libx264": ["-c:v", "libx264", "-preset", str(R.get("x264_preset", "medium")), "-crf", str(q),
                    "-maxrate", teto, "-bufsize", buf],
    }[nome]


def _candidatos():
    ordem = ["h264_nvenc", "h264_qsv", "h264_amf"]
    if platform.system() == "Darwin":
        ordem.append("h264_videotoolbox")
    return ordem + ["libx264"]


@lru_cache(maxsize=None)
def _funciona(nome):
    """Encode curto de verdade: o encoder estar listado não garante placa nem driver."""
    cmd = [ffmpeg(), "-v", "error", "-f", "lavfi", "-i", "color=c=black:s=320x240:r=30", "-frames:v", "8",
           *args_encoder(nome), "-pix_fmt", "yuv420p", "-f", "null", "-"]
    try:
        return subprocess.run(cmd, capture_output=True, timeout=60).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def escolher_encoder(cpu=False):
    """Encoder de vídeo: o configurado, ou o primeiro que funciona na ordem NVENC -> QSV -> AMF -> VT -> libx264."""
    pedido = str(R.get("encoder", "auto"))
    if forcar_cpu(cpu):
        return "libx264"
    if pedido != "auto":
        if not _funciona(pedido):
            raise RuntimeError(f"encoder configurado ({pedido}) não funciona nesta máquina; use \"auto\".")
        return pedido
    for nome in _candidatos():
        if _funciona(nome):
            return nome
    raise RuntimeError("nenhum encoder H.264 funcionou; o ffmpeg instalado tem libx264? (ver INSTALAR.md)")


def encoders_simultaneos(n, cpu=False):
    """Encoder de cada um de `n` vídeos gravados ao mesmo tempo (ex.: uma versão por rede).

    Placa comum abre poucas sessões de NVENC (e de Quick Sync e AMF) ao mesmo tempo, e outros programas abertos
    também gastam sessão. Até `render.sessoes_gpu` (padrão 3) usam a placa; as que passam vão para o libx264.
    """
    enc = escolher_encoder(cpu)
    lim = 0 if enc == "libx264" else max(1, int(R.get("sessoes_gpu", 3)))
    return [enc if k < lim else "libx264" for k in range(n)]


def placa_sem_uso(sup, cpu=False):
    """Aviso quando o encoder da placa funciona mas o desenho caiu na CPU: é instalação a corrigir, não falta de GPU."""
    if sup.ctx is not None or forcar_cpu(cpu) or "software" in sup.motivo_cpu:
        return ""
    enc = escolher_encoder(cpu)
    if enc == "libx264":
        return ""
    return (f"AVISO: a placa existe (encoder {enc}), mas o desenho caiu na CPU ({sup.motivo_cpu}). "
            "Rode python verificar.py e corrija antes do render longo.")


def comando_ffmpeg(saida, encoder, audio=None, duracao=None, w=W, h=H, threads=None):
    A = CFG["audio"]
    cmd = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
           "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-i", str(audio), "-map", "0:v", "-map", "1:a"]
    if (w, h) != (W, H):  # prévia desenhada em resolução menor: volta ao tamanho final
        cmd += ["-vf", f"scale={W}:{H}:flags=lanczos"]
    cmd += [*args_encoder(encoder), "-pix_fmt", "yuv420p", "-r", str(FPS)]
    if threads:  # partes em paralelo: um núcleo por processo, sem o x264 de cada um disputar a máquina toda
        cmd += ["-threads", str(threads)]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", str(A["bitrate_aac"]), "-ar", str(A["taxa"]), "-ac", "2"]
    if duracao:
        cmd += ["-t", f"{duracao:.3f}"]
    return cmd + ["-movflags", "+faststart", str(saida)]


# ---------------------------------------------------------------- render

def folha(pngs, saida, colunas=9, larg=216):
    """Folha de conferência com os quadros-marco."""
    from PIL import Image

    if not pngs:
        return None
    alt = int(larg * H / W)
    ims = [Image.open(p).convert("RGB").resize((larg, alt)) for p in pngs]
    linhas = (len(ims) + colunas - 1) // colunas
    f = Image.new("RGB", (larg * min(colunas, len(ims)), alt * linhas), (0, 0, 0))
    for k, im in enumerate(ims):
        f.paste(im, ((k % colunas) * larg, (k // colunas) * alt))
    f.save(saida, quality=88)
    return saida


def _tamanho_cpu():
    """Tamanho do desenho na CPU: `render.escala_cpu` < 1 desenha menor e o ffmpeg amplia (prévia rápida)."""
    e = min(1.0, max(0.25, float(R.get("escala_cpu", 1.0))))
    return int(W * e) // 2 * 2, int(H * e) // 2 * 2


def _processos_cpu():
    pedido = str(R.get("processos_cpu", "auto"))
    if pedido.isdigit():
        return max(1, int(pedido))
    return max(1, min((os.cpu_count() or 2) - 1, 16))


def _loop(sup, desenhar, quadros, alvo, pasta_quadros, ff, nf, prefixo=""):
    c = sup.canvas
    e = sup.w / W
    pngs = []
    for f in quadros:
        t = f / FPS
        c.save()
        c.clear(skia.Color(0, 0, 0))
        if e != 1.0:
            c.scale(e, e)
        desenhar(c, t)
        c.restore()
        buf = sup.ler()
        if ff:
            ff.stdin.write(buf.data)
        if f in alvo:
            p = pasta_quadros / f"q{f:05d}.png"
            rgba = np.ascontiguousarray(buf[:, :, [2, 1, 0, 3]])
            skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType).save(str(p))
            pngs.append(p)
        if ff and f % (FPS * 5) == 0:
            print(f"  {prefixo}quadro {f}/{nf}", flush=True)
    return pngs


def _fatia(desenhar, nf, alvo, pasta_quadros):
    """Processo filho do render em paralelo na CPU: desenha só a sua faixa de quadros num pedaço de vídeo."""
    k, n, destino = os.environ["MAQUINA_FATIA"].split("|", 2)
    k, n = int(k), int(n)
    ini, fim = k * nf // n, (k + 1) * nf // n
    sup = Superficie(*_tamanho_cpu(), cpu=True)
    ff = subprocess.Popen(comando_ffmpeg(destino, "libx264", w=sup.w, h=sup.h, threads=1), stdin=subprocess.PIPE)
    try:
        _loop(sup, desenhar, range(ini, fim), alvo, pasta_quadros, ff, nf, prefixo=f"[{k + 1}/{n}] ")
    finally:
        ff.stdin.close()
        ff.wait()
        sup.fechar()
    sys.exit(ff.returncode)


def _paralelo(saida, audio, duracao, n):
    """Divide o vídeo em `n` faixas renderizadas por processos separados (mesmo script) e junta sem recodificar."""
    import tempfile

    with tempfile.TemporaryDirectory(dir=str(saida.parent)) as tmp:
        pedacos = [Path(tmp) / f"p{k:02d}.mp4" for k in range(n)]
        filhos = []
        for k, p in enumerate(pedacos):
            env = dict(os.environ, MAQUINA_FATIA=f"{k}|{n}|{p}", MAQUINA_CPU="1")
            filhos.append(subprocess.Popen([sys.executable, *sys.argv], env=env))
        erros = [f.wait() for f in filhos]
        if any(erros):
            raise RuntimeError(f"render em paralelo falhou (códigos {erros})")
        lista = Path(tmp) / "lista.txt"
        lista.write_text("\n".join(f"file '{p.as_posix()}'" for p in pedacos) + "\n", encoding="utf-8")
        A = CFG["audio"]
        cmd = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista)]
        if audio:
            cmd += ["-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", str(A["bitrate_aac"]),
                    "-ar", str(A["taxa"]), "-ac", "2"]
        cmd += ["-c:v", "copy", "-t", f"{duracao:.3f}", "-movflags", "+faststart", str(saida)]
        subprocess.run(cmd, check=True)


AMOSTRAS_CENA = 8
BORDA_MIN = 0.005   # fração mínima de pixels com contorno: degradê dá 0; a noite mais escura do exemplo, 1,2%


def _contorno(rgba):
    """Fração de pixels com borda nítida (desenho) numa imagem reduzida; degradê e cor chapada dão perto de zero."""
    g = rgba[:, :, :3].astype(np.int16).mean(axis=2)
    dx = np.abs(np.diff(g, axis=1))[:-1, :]
    dy = np.abs(np.diff(g, axis=0))[:, :-1]
    return float(((dx + dy) > 24).mean())


def trava_cena_vazia(desenhar, duracao, pasta):
    """Para o render quando a cena do episódio não tem desenho (só fundo, texto e legenda por cima).

    Mede a função `cena(c, t)` do mesmo arquivo do `quadro` (o padrão do exemplo/ep.py), sem gancho, legenda e
    selo, em 8 momentos do vídeo. Se metade ou mais estiver vazia, sai com ERRO e grava a folha dos momentos em
    <trabalho>/cena_vazia.jpg. Veio de um comprador que recebeu 1:45 de fundo bege com texto (lição 17/11/2026).
    """
    import inspect
    cena = getattr(desenhar, "__globals__", {}).get("cena")
    if not callable(cena):
        return
    try:
        if len(inspect.signature(cena).parameters) != 2:
            return
    except (TypeError, ValueError):
        return
    surf = skia.Surface(W, H)
    larg, alt = W // 4, H // 4
    medidas, miniaturas = [], []
    for i in range(AMOSTRAS_CENA):
        t = duracao * (i + 0.5) / AMOSTRAS_CENA
        c = surf.getCanvas()
        c.clear(skia.ColorBLACK)
        c.save()
        try:
            cena(c, t)
        except Exception as e:  # a cena depende de algo que só o quadro prepara: não dá para medir sozinha
            print(f"AVISO: não deu para conferir a cena sozinha ({type(e).__name__}: {e}); confira a folha.", flush=True)
            return
        finally:
            c.restore()
        img = surf.makeImageSnapshot().resize(larg, alt)
        rgba = img.toarray(colorType=skia.kRGBA_8888_ColorType)
        medidas.append((t, _contorno(rgba)))
        miniaturas.append(img)
    vazios = [(t, m) for t, m in medidas if m < BORDA_MIN]
    print("TRAVA DA CENA: " + ", ".join(f"{t:.1f}s {m * 100:.1f}%" for t, m in medidas), flush=True)
    from .rig import Boneco
    if not any(isinstance(v, Boneco) for v in desenhar.__globals__.values()):
        raise SystemExit(
            "ERRO: o episódio não tem personagem: nenhum boneco foi carregado no arquivo da cena.\n"
            "O QUE FAZER: crie o personagem antes de renderizar. Use um boneco pronto do kit (personagens/lola ou "
            "personagens/nico, com Boneco(\"lola\") de maquina/rig.py, desenhado em cena() como no exemplo/ep.py) ou "
            "crie o do canal com personagem_novo.py. Mostre ao usuário a folha de quadros com o personagem e só "
            "depois rode o vídeo.")
    if len(vazios) * 2 < AMOSTRAS_CENA:
        return
    folha_s = skia.Surface(larg * AMOSTRAS_CENA, alt)
    fc = folha_s.getCanvas()
    for i, img in enumerate(miniaturas):
        fc.drawImage(img, i * larg, 0)
    arq = Path(pasta) / "cena_vazia.jpg"
    folha_s.makeImageSnapshot().save(str(arq), skia.kJPEG)
    momentos = ", ".join(f"{t:.1f} s" for t, _ in vazios)
    raise SystemExit(
        f"ERRO: a cena do vídeo está vazia em {len(vazios)} de {AMOSTRAS_CENA} momentos ({momentos}): só fundo, sem "
        f"cenário nem personagem. Com isso o vídeo sai só com texto e legenda.\n"
        f"O QUE FAZER: desenhe em cena(c, t) o cenário e o personagem de cada trecho do roteiro (o boneco do kit em "
        f"maquina/rig.py, Boneco, e o cenário em perspectiva como no exemplo/ep.py), passe pela folha de quadros e "
        f"rode de novo. Folha dos momentos medidos: {arq}. Não apague esta trava: ela existe porque um vídeo assim "
        f"chegou a um comprador.")


def renderizar(desenhar, duracao, saida, audio=None, cpu=False, marcos=(), pasta_quadros=None, so_marcos=False):
    """Renderiza `duracao` segundos chamando `desenhar(canvas, t)` a cada quadro.

    `marcos` (segundos) viram PNG em `pasta_quadros` e uma folha `folha.jpg`. `so_marcos=True` renderiza só eles
    (conferência rápida, sem vídeo). Na CPU, o vídeo é dividido entre vários processos (render.processos_cpu;
    "auto" = núcleos - 1, até 16, x264 com 1 thread em cada) e juntado sem recodificar. Devolve um resumo com backend, encoder e velocidade.
    """
    licenca.exigir()
    saida = Path(saida)
    pasta_quadros = Path(pasta_quadros or saida.parent / "quadros")
    pasta_quadros.mkdir(parents=True, exist_ok=True)
    if not os.environ.get("MAQUINA_FATIA"):
        trava_cena_vazia(desenhar, duracao, pasta_quadros.parent)
    nf = int(round(duracao * FPS))
    alvo = {min(nf - 1, int(m * FPS)) for m in marcos}
    if os.environ.get("MAQUINA_FATIA"):
        _fatia(desenhar, nf, alvo, pasta_quadros)
    sup = Superficie(cpu=cpu)
    if sup.ctx is None and _tamanho_cpu() != (W, H):
        sup.fechar()
        sup = Superficie(*_tamanho_cpu(), cpu=True)
    aviso = "" if so_marcos else placa_sem_uso(sup, cpu)
    if aviso:
        print(aviso, flush=True)
    n_proc = 1 if (so_marcos or sup.ctx is not None) else _processos_cpu()
    encoder = None if so_marcos else ("libx264" if n_proc > 1 else escolher_encoder(cpu))
    print(f"RENDER: {sup.backend}" + (f" ({sup.motivo_cpu})" if sup.motivo_cpu else "")
          + (f" | encoder {encoder}" if encoder else " | só marcos")
          + (f" | {n_proc} processos" if n_proc > 1 else ""), flush=True)
    t_ini = time.perf_counter()
    if n_proc > 1:
        sup.fechar()
        _paralelo(saida, audio, duracao, n_proc)
        pngs = sorted(pasta_quadros.glob("q*.png"))
        pngs = [p for p in pngs if int(p.stem[1:]) in alvo]
        quadros = range(nf)
    else:
        ff = None if so_marcos else subprocess.Popen(comando_ffmpeg(saida, encoder, audio, duracao, sup.w, sup.h),
                                                     stdin=subprocess.PIPE)
        quadros = sorted(alvo) if so_marcos else range(nf)
        try:
            pngs = _loop(sup, desenhar, quadros, alvo, pasta_quadros, ff, nf)
        finally:
            if ff:
                ff.stdin.close()
                ff.wait()
            sup.fechar()
        if ff and ff.returncode:
            raise RuntimeError(f"ffmpeg terminou com erro {ff.returncode}")
    seg = time.perf_counter() - t_ini
    folha(sorted(pngs), pasta_quadros.parent / "folha.jpg")
    resumo = dict(backend=sup.backend, encoder=encoder, processos=n_proc, quadros=len(quadros), segundos=round(seg, 1),
                  quadros_por_s=round(len(quadros) / max(seg, 1e-6), 1), saida=None if so_marcos else str(saida))
    print("RENDER_OK", resumo, flush=True)
    return resumo

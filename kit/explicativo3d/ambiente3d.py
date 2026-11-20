# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Acha o Blender, confere a versão e (com --teste) faz um render curto para mostrar qual placa o EEVEE usou.

    python explicativo3d/ambiente3d.py              # onde está o Blender e qual a versão
    python explicativo3d/ambiente3d.py --teste      # + render de teste e o nome da placa usada
    python explicativo3d/ambiente3d.py --teste --gpu-device 1   # testa outra placa (notebook com duas)

Ordem de busca: variável BLENDER, `ferramentas.blender` no config.json do kit, o PATH e as pastas padrão de
instalação (Windows: Arquivos de Programas\\Blender Foundation; Mac: /Applications/Blender.app).
"""
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))

from config import CFG  # noqa: E402

TESTADA = (5, 2)   # versão em que o motor e o exemplo foram testados (5.2.3 LTS)
MINIMA = (4, 2)    # abaixo disso o EEVEE e o formato das animações são outros: não roda


def achar_blender():
    pedidos = [os.environ.get("BLENDER", ""), CFG["ferramentas"].get("blender", "")]
    for p in pedidos:
        if p and Path(p).is_file():
            return str(Path(p))
        if p and shutil.which(p):
            return shutil.which(p)
    if shutil.which("blender"):
        return shutil.which("blender")
    candidatos = []
    if platform.system() == "Windows":
        for raiz in {os.environ.get("ProgramFiles", r"C:\Program Files"), r"C:\Program Files"}:
            candidatos += Path(raiz, "Blender Foundation").glob("Blender*/blender.exe")
        candidatos += Path(os.environ.get("LOCALAPPDATA", ""), "Programs").glob("Blender*/blender.exe")
    elif platform.system() == "Darwin":
        candidatos += [Path("/Applications/Blender.app/Contents/MacOS/Blender"),
                       Path.home() / "Applications/Blender.app/Contents/MacOS/Blender"]
    else:
        candidatos += Path.home().glob("blender*/blender")
    existentes = [c for c in candidatos if c.is_file()]
    if not existentes:
        return None
    # várias instaladas: a mais nova pelo número da pasta ("Blender 5.2")
    def chave(c):
        return tuple(int(n) for n in re.findall(r"\d+", c.parent.name)[:2]) or (0,)
    return str(max(existentes, key=chave))


def versao(exe):
    r = subprocess.run([exe, "--version"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=120)
    m = re.search(r"Blender (\d+)\.(\d+)\.?(\d*)", r.stdout)
    if not m:
        raise RuntimeError(f"não consegui ler a versão de {exe}")
    return tuple(int(x) for x in m.groups() if x)


def blender_ok():
    """(executável, versão) ou SystemExit com o que fazer."""
    exe = achar_blender()
    if not exe:
        raise SystemExit("BLENDER_AUSENTE: instale o Blender 5.2 LTS (ver explicativo3d/INSTALAR.md) ou aponte "
                         "ferramentas.blender no config.json do kit (ou a variável BLENDER).")
    v = versao(exe)
    if v[:2] < MINIMA:
        raise SystemExit(f"BLENDER_ANTIGO: {exe} é {'.'.join(map(str, v))}; o motor precisa do 5.2 LTS.")
    if v[:2] != TESTADA:
        print(f"AVISO: Blender {'.'.join(map(str, v))}; o motor foi testado no 5.2 LTS. Se der erro, instale o 5.2.",
              flush=True)
    return exe, v


def comando(exe, script, args=(), gpu_device=None):
    """Linha de comando do Blender em segundo plano. `--python-exit-code 1` faz erro no script virar erro no
    processo (sem isso o Blender sai com 0 mesmo quando o script quebra)."""
    cmd = [exe, "-b", "--factory-startup", "--python-exit-code", "1"]
    if gpu_device is not None:
        cmd += ["--gpu-backend", "vulkan", "--gpu-device", str(gpu_device)]
    return cmd + ["-P", str(script), "--", *[str(a) for a in args]]


TESTE = r"""
import time, bpy, gpu
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.eevee.taa_render_samples = 8
bpy.ops.mesh.primitive_monkey_add()
cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam)
sc.camera = cam; cam.location = (0, -4, 0); cam.rotation_euler = (1.5708, 0, 0)
sc.render.filepath = bpy.app.tempdir + "teste3d.png"
t = time.time(); bpy.ops.render.render(write_still=True); t1 = time.time() - t
t = time.time(); bpy.ops.render.render(write_still=True); t2 = time.time() - t
print("PLACA", gpu.platform.backend_type_get(), "|", gpu.platform.renderer_get(), "|", f"{t1:.2f}", f"{t2:.2f}")
"""


def main():
    exe, v = blender_ok()
    print(f"Blender {'.'.join(map(str, v))}: {exe}")
    if "--teste" not in sys.argv:
        return
    dev = sys.argv[sys.argv.index("--gpu-device") + 1] if "--gpu-device" in sys.argv else None
    cmd = [exe, "-b", "--factory-startup", "--python-exit-code", "1"]
    if dev is not None:
        cmd += ["--gpu-backend", "vulkan", "--gpu-device", dev]
    t0 = time.time()
    r = subprocess.run(cmd + ["--python-expr", TESTE], capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    linha = next((ln for ln in r.stdout.splitlines() if ln.startswith("PLACA")), None)
    if r.returncode or not linha:
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit("TESTE_FALHOU: o EEVEE não abriu. Precisa de placa de vídeo (a integrada serve) com driver "
                         "atualizado; ver INSTALAR.md.")
    backend, placa, tempos = [p.strip() for p in linha[len("PLACA"):].split("|")]
    t1, t2 = tempos.split()
    print(f"EEVEE OK na placa: {placa} ({backend})")
    print(f"quadro de teste 1080x1920: {t2} s (o primeiro levou {t1} s, compilando shaders); "
          f"total {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()

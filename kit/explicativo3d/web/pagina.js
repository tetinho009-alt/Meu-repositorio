/*! © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C */
/**
 * Página que o render.py abre no Chromium sem janela. Lê /dados.json (cena, tamanho, tempos e episódio), monta a
 * cena do episódio e expõe window.X3D para o Python pedir quadro a quadro. O tempo vem sempre de fora: nada aqui
 * anda sozinho, então o vídeo não depende da velocidade da máquina.
 */
import * as THREE from 'three';
import { Motor } from './motor3d.js';

function erro(e) {
  window.X3D_ERRO = String((e && e.stack) || (e && e.message) || e);
  console.error(window.X3D_ERRO);
}
window.addEventListener('error', (ev) => erro(ev.error || ev.message));
window.addEventListener('unhandledrejection', (ev) => erro(ev.reason));

async function iniciar() {
  const dados = await (await fetch('/dados.json')).json();
  const tela = document.getElementById('tela');
  const renderer = new THREE.WebGLRenderer({
    canvas: tela, antialias: true, alpha: true, premultipliedAlpha: true, preserveDrawingBuffer: true,
    powerPreference: 'high-performance',
  });
  renderer.setPixelRatio(1);
  renderer.setSize(dados.largura, dados.altura, false);
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const kit = new Motor(renderer, { largura: dados.largura, altura: dados.altura, modelos: '/modelos/' });
  const cena = await import(dados.cena);
  const t0 = performance.now();
  const info = await cena.montar(THREE, kit, dados);
  if (!kit.camera) throw new Error('a cena não criou a câmera (chame kit.criarCamera dentro de montar)');
  if (!(info && info.duracao > 0)) throw new Error('montar() precisa devolver { duracao: segundos }');

  const pose = (t) => {
    cena.quadro(t);
    kit.atualizar(t);
  };
  pose(0);
  renderer.compile(kit.cena, kit.camera); // compila os shaders antes do primeiro quadro medido
  kit.renderizar();

  const gl = renderer.getContext();
  const ext = gl.getExtension('WEBGL_debug_renderer_info');
  window.X3D = {
    duracao: info.duracao,
    montagem: (performance.now() - t0) / 1000,
    placa: ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
    amostras: gl.getParameter(gl.SAMPLES),
    ancoras: (ts) => ts.map((t) => { pose(t); return kit.ancoras(); }),
    png: (t) => {
      pose(t);
      kit.renderizar();
      return tela.toDataURL('image/png');
    },
  };
  window.X3D_PRONTO = true;
}

iniciar().catch(erro);

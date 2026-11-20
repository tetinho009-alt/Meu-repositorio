/*! © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C */
/**
 * bichos3d.js: os bichos procedurais do bichos3d.py no navegador. Cada bicho volta separado em partes, cada parte
 * num grupo de controle, para a desmontagem animar uma por uma.
 *
 *     const cv = caravela(kit, 'caravela_1', [0, 0, 2.2], 1.0);
 *     cv.raiz, cv.boia, cv.cacadores, cv.digestao, cv.filhotes, cv.crista
 */
import * as THREE from 'three';
import { aleatorio, blob, cadeia, esfera, mesclar, rad, tubo } from './motor3d.js';

export const CORES_CARAVELA = {
  boia: ['#86CFFF', '#C9A2FF'], // base -> topo
  crista: ['#B79BFF', '#FF8FD0'],
  tentaculo: '#4D6CFF',
  conta: '#2F45C9',
  digestao: ['#FF9F6B', '#FFD0A8'],
  filhotes: ['#B07CFF', '#FFB3E0'],
};

/** Par de olhos cartoon (esclera, pupila e brilho) virados para `olhar`, lado a lado no eixo X. */
export function olhos(kit, nome, centro, raio, { olhar = [0, -1, 0], afastar = 1.15, pai = kit.mundo, linha = 0.002 } = {}) {
  const dir = new THREE.Vector3(...olhar).normalize();
  const obs = [];
  for (const s of [-1, 1]) {
    const c = new THREE.Vector3(centro[0] + s * raio * afastar, centro[1], centro[2]);
    for (const [parte, r, desloc, cor] of [['esclera', raio, 0, '#FFFFFF'], ['pupila', raio * 0.55, raio * 0.62, '#120E1E'],
      ['brilho', raio * 0.2, raio * 1.02, '#FFFFFF']]) {
      const p = c.clone().addScaledVector(dir, desloc);
      if (parte === 'brilho') p.add(new THREE.Vector3(-0.35 * raio, 0, 0.4 * raio));
      obs.push(kit.objeto(`${nome}_${parte}_${s}`, esfera(r, p.toArray(), [20, 14]), kit.matChapado(cor),
        { linha: parte === 'esclera' ? linha : 0, pai }));
    }
  }
  return obs;
}

/** Caravela-portuguesa cartoon (boia de ~0,5 m, tentáculos de ~1,5 m na escala 1), igual à do bichos3d.py. */
export function caravela(kit, nome, local, escala = 1, { linha = 0.005, semente = 3, pai = kit.mundo } = {}) {
  const rnd = aleatorio(semente);
  const raiz = kit.grupo(nome, pai, local);
  raiz.scale.setScalar(escala);
  raiz.updateMatrixWorld(true);
  const partes = { raiz };

  // boia: corpo alongado no X, mais grosso na frente (+X), com a ponta de trás arrebitada
  const boia = kit.grupo(`${nome}_boia`, raiz);
  let els = [];
  for (let i = 0; i < 14; i++) {
    const u = i / 13;
    const r = 0.095 * (1 - 0.45 * u) + 0.02;
    els.push([[0.26 - 0.52 * u, 0, 0.05 + 0.06 * u * u], r * 1.35, [1.0, 0.85, 0.9]]);
  }
  kit.objeto(`${nome}_boia_m`, blob(els, 0.01), kit.matGradiente(...CORES_CARAVELA.boia, -0.05, 0.2), { linha, pai: boia });
  // crista (a "vela"): barbatana fina, com a borda de cima ondulada; num grupo próprio para esticar na fala
  const crista = kit.grupo(`${nome}_crista`, boia);
  els = [];
  for (let i = 0; i < 40; i++) {
    const u = i / 39;
    const topo = 0.2 + 0.03 * Math.sin(u * Math.PI * 3.5) + 0.06 * Math.sin(u * Math.PI);
    for (let k = 0; k < 4; k++) els.push([[0.2 - 0.4 * u, 0, 0.09 + (topo - 0.09) * k / 3], 0.04, [1.0, 0.22, 1.0]]);
  }
  kit.objeto(`${nome}_crista_m`, blob(els, 0.006), kit.matGradiente(...CORES_CARAVELA.crista, 0.1, 0.27), { linha, pai: crista });
  const bb = new THREE.SphereGeometry(1, 16, 10); // brilho de balão
  bb.scale(0.07, 0.012, 0.022);
  bb.rotateY(rad(-12));
  bb.translate(0.02, -0.112, 0.11);
  kit.objeto(`${nome}_boia_brilho`, bb, kit.matChapado('#F4FBFF'), { linha: 0, pai: boia });
  olhos(kit, `${nome}_olho`, [0.16, -0.105, 0.07], 0.034, { pai: boia });
  partes.boia = boia;
  partes.crista = crista;

  // caçadores: tentáculos pendurados do lado, com contas de veneno
  const cac = kit.grupo(`${nome}_cacadores`, raiz);
  const tubos = [];
  const contas = [];
  for (let k = 0; k < 7; k++) {
    const x0 = 0.12 - 0.04 * k + rnd.uniforme(-0.01, 0.01);
    const y0 = 0.03 + 0.015 * (k % 2);
    const comp = 1.5 * rnd.uniforme(0.7, 1.0);
    const fase = rnd.uniforme(0, 6.28);
    const pts = [];
    for (let j = 0; j < 40; j++) {
      const u = j / 39;
      pts.push([x0 + 0.03 * Math.sin(fase + u * 9) * u, y0 + 0.02 * Math.cos(fase + u * 7) * u, -0.02 - comp * u]);
    }
    tubos.push(tubo(pts, 0.011, 8, 'fim'));
    for (let j = 3; j < 40; j += 4) contas.push(esfera(0.016 * (1 - 0.5 * j / 39), pts[j], [10, 7]));
  }
  kit.objeto(`${nome}_tentaculos`, mesclar(tubos), kit.matToon(CORES_CARAVELA.tentaculo), { linha: linha * 0.7, pai: cac });
  kit.objeto(`${nome}_contas`, mesclar(contas), kit.matToon(CORES_CARAVELA.conta), { linha: linha * 0.5, pai: cac });
  olhos(kit, `${nome}_olho_cac`, [0.0, -0.02, -0.06], 0.016, { pai: cac, linha: 0.0012 });
  partes.cacadores = cac;

  // digestão: tubinhos curtos e caídos embaixo do meio da boia
  const dig = kit.grupo(`${nome}_digestao`, raiz);
  els = [];
  for (let k = 0; k < 9; k++) {
    const a = 2 * Math.PI * k / 9;
    const p0 = [-0.02 + 0.06 * Math.cos(a), 0.04 * Math.sin(a), -0.02];
    const p1 = [p0[0] + 0.03 * Math.cos(a), p0[1] + 0.02 * Math.sin(a), p0[2] - 0.13 - 0.04 * (k % 3)];
    els.push(...cadeia(p0, p1, 0.026, 0.018, 0.4));
  }
  kit.objeto(`${nome}_digestao_m`, blob(els, 0.008), kit.matGradiente(...CORES_CARAVELA.digestao, -0.2, 0.0), { linha: linha * 0.8, pai: dig });
  olhos(kit, `${nome}_olho_dig`, [-0.02, -0.07, -0.08], 0.016, { pai: dig, linha: 0.0012 });
  partes.digestao = dig;

  // filhotes: cachos de bolinhas (gonozooides) atrás
  const fil = kit.grupo(`${nome}_filhotes`, raiz);
  els = [];
  for (let k = 0; k < 3; k++) {
    const c = [-0.13 - 0.05 * k, 0.02 * (k - 1), -0.06 - 0.02 * k];
    for (let i = 0; i < 9; i++) {
      els.push([[c[0] + rnd.uniforme(-0.04, 0.04), c[1] + rnd.uniforme(-0.035, 0.035), c[2] + rnd.uniforme(-0.05, 0.02)], 0.028]);
    }
  }
  kit.objeto(`${nome}_filhotes_m`, blob(els, 0.007), kit.matGradiente(...CORES_CARAVELA.filhotes, -0.13, 0.0), { linha: linha * 0.8, pai: fil });
  olhos(kit, `${nome}_olho_fil`, [-0.18, -0.06, -0.06], 0.016, { pai: fil, linha: 0.0012 });
  partes.filhotes = fil;
  return partes;
}

/** Chinelo de dedo genérico (sem marca): sola amarela e tira turquesa, para o "achado no corte". */
export function chinelo(kit, nome, local, { giro = 0, linha = 0.004, pai = kit.mundo } = {}) {
  const raiz = kit.grupo(nome, pai, local);
  raiz.rotation.z = giro;
  const els = [];
  for (let i = 0; i < 12; i++) {
    const u = i / 11;
    const larg = 0.045 + 0.012 * Math.sin(Math.PI * u) + (u > 0.7 ? 0.008 : 0);
    els.push([[-0.12 + 0.24 * u, 0, 0], larg, [1.0, 1.0, 0.22]]);
  }
  kit.objeto(`${nome}_sola`, blob(els, 0.006), kit.matToon('#FFD23F'), { linha, pai: raiz });
  const tiras = [-1, 1].map((s) => {
    const pts = [[0.07, 0, 0.012], ...[0.25, 0.5, 0.75, 1.0].map((t) =>
      [0.07 - 0.11 * t, s * 0.045 * Math.sin(Math.PI * t * 0.9), 0.012 + 0.03 * Math.sin(Math.PI * t)])];
    return tubo(pts, 0.008, 8, 'uniforme');
  });
  kit.objeto(`${nome}_tira`, mesclar(tiras), kit.matToon('#3CC8C8'), { linha, pai: raiz });
  return raiz;
}

/**
 * Personagem de qualquer coisa (mascote): corpo com olhos, boca, bracinhos e perninhas. É o jeito de pôr um
 * personagem em qualquer assunto, mesmo sem modelo pronto: o raio, a casa, a tomada, a gota, o átomo...
 * Base nos pés, em `local`; ~0,32 m de altura na escala 1; frente para -Y (a câmera).
 *
 *     const r = mascote(kit, 'raio', [0.3, -0.2, 0], { forma: 'raio', cor: '#FFE45E', cor2: '#FFB23E' });
 *     r.raiz, r.corpo, r.bracoE, r.bracoD (grupos para girar), r.boca (escala Z para falar), r.olhos
 *
 * Formas: 'gota', 'bola', 'caixa' (bloco arredondado) e 'raio' (zigue-zague).
 */
export function mascote(kit, nome, local, { cor = '#FFD23F', cor2 = null, forma = 'gota', escala = 1, linha = 0.005, pai = kit.mundo } = {}) {
  const raiz = kit.grupo(nome, pai, local);
  raiz.scale.setScalar(escala);
  const corpo = kit.grupo(`${nome}_corpo`, raiz, [0, 0, 0.07]);
  let els, olhoZ = 0.17, frente = -0.08, largura = 0.09;
  if (forma === 'bola') {
    els = [[[0, 0, 0.11], 0.11]];
    olhoZ = 0.14;
  } else if (forma === 'caixa') {
    els = [];
    for (const x of [-0.05, 0, 0.05]) for (const y of [-0.03, 0.03]) for (const z of [0.05, 0.11, 0.17]) els.push([[x, y, z], 0.055]);
    olhoZ = 0.16; largura = 0.1;
  } else if (forma === 'raio') {
    els = [...cadeia([0.05, 0, 0.26], [-0.04, 0, 0.14], 0.055, 0.05, 0.3), ...cadeia([-0.04, 0, 0.14], [0.04, 0, 0.11], 0.05, 0.05, 0.3),
      ...cadeia([0.04, 0, 0.11], [-0.03, 0, -0.02], 0.05, 0.02, 0.3)].map(([p, r]) => [p, r, [1, 0.6, 1]]);
    olhoZ = 0.17; frente = -0.035; largura = 0.06;
  } else { // gota
    els = [[[0, 0, 0.08], 0.1], [[0, 0, 0.17], 0.07], [[0, 0, 0.24], 0.035]];
  }
  const geo = blob(els, 0.007);
  const mat = cor2 ? kit.matGradiente(cor2, cor, 0, 0.26) : kit.matToon(cor);
  kit.objeto(`${nome}_corpo_m`, geo, mat, { linha, pai: corpo });
  // Olhos, boca, braços e pernas presos na superfície de verdade do corpo (o blob fica dentro dos raios das bolas).
  const sonda = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }));
  const ray = new THREE.Raycaster();
  const bater = (o, d) => { ray.set(new THREE.Vector3(...o), new THREE.Vector3(...d).normalize()); const h = ray.intersectObject(sonda)[0]; return h ? h.point : null; };
  let cx = 0;
  frente = 0;
  for (let x = -0.08; x <= 0.0801; x += 0.01) {
    const h = bater([x, -1, olhoZ], [0, 1, 0]);
    if (h && h.y < frente) { frente = h.y; cx = x; }
  }
  frente += 0.008;
  const lado = (s) => { const h = bater([cx + s, 0, 0.11], [-s, 0, 0]); return h ? Math.abs(h.x - cx) - 0.004 : largura; };
  const ombro = { '-1': lado(-1), '1': lado(1) };
  const fundoZ = (x) => { const h = bater([x, 0, -1], [0, 0, 1]); return h ? h.z : 0; };
  const ol = olhos(kit, `${nome}_olho`, [cx, frente, olhoZ], 0.022, { afastar: 1.05, pai: corpo, linha: linha * 0.5 });
  const boca = kit.grupo(`${nome}_boca`, corpo, [cx, frente - 0.004, olhoZ - 0.05]);
  const gb = esfera(0.02, [0, 0, 0], [16, 10]);
  gb.scale(1.2, 0.5, 0.6);
  kit.objeto(`${nome}_boca_m`, gb, kit.matChapado('#3A1020'), { linha: 0, pai: boca });
  const membros = kit.matToon('#1B1530');
  const braco = (s) => {
    const g = kit.grupo(`${nome}_braco_${s > 0 ? 'd' : 'e'}`, corpo, [cx + s * ombro[String(s)], 0, 0.11]);
    kit.objeto(`${g.name}_m`, tubo([[0, 0, 0], [s * 0.05, -0.01, -0.03], [s * 0.09, -0.01, -0.02]], 0.009, 8, 'nenhum'), membros, { linha: 0, pai: g });
    kit.objeto(`${g.name}_mao`, esfera(0.016, [s * 0.095, -0.01, -0.02], [12, 8]), kit.matToon('#FFFFFF'), { linha: linha * 0.5, pai: g });
    return g;
  };
  const bracoE = braco(-1), bracoD = braco(1);
  for (const s of [-1, 1]) {
    kit.objeto(`${nome}_perna_${s}`, tubo([[s * 0.035, 0, 0.07 + fundoZ(s * 0.035) + 0.01], [s * 0.04, 0, 0.012]], 0.01, 8, 'nenhum'), membros, { linha: 0, pai: raiz });
    const pe = esfera(0.022, [s * 0.042, -0.012, 0.012], [14, 10]);
    pe.scale(1, 1.4, 0.55);
    kit.objeto(`${nome}_pe_${s}`, pe, kit.matToon('#1B1530'), { linha: 0, pai: raiz });
  }
  return { raiz, corpo, bracoE, bracoD, boca, olhos: ol };
}

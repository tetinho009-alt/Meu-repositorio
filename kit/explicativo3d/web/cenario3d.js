/*! © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C */
/**
 * cenario3d.js: o cenário do kit3d.py no navegador. Fatia de oceano em corte (estratos de areia, areia ondulada com
 * cáustica, água, vidro e superfície), coral, alga, anêmona, estrela, pedra, seixo, feixe de luz e os peixes CC0.
 *
 * Cada função recebe o `kit` (Motor do motor3d.js) e usa os eixos do Blender (Z para cima). Os nomes e medidas são os
 * do kit3d.py, para um episódio do Blender virar um do navegador trocando pouco.
 */
import * as THREE from 'three';
import { PALETA, aleatorio, blob, cadeia, caixa, esfera } from './motor3d.js';

export const CORES_PEIXE = {
  palhaco: { Clownfish_Main: '#FF7B2C', Clownfish_Light: '#FFF6EA', Clownfish_Dark: '#1B1530', Eyes: '#120E1E' },
  baiacu: { Pufferfish_Main: '#F2C14E', Pufferfish_Light: '#FFF1C9', Puffefish_Black: '#7A5A3A', Eyes: '#120E1E' },
  peixe: { Bottom: '#DDF4F0', Top: '#3E7FD0', Fins: '#FFB23E' },
};

export function peixe(kit, nome, arquivo, comprimento, local, direcao, opcoes = {}) {
  return kit.peixe(nome, arquivo, comprimento, local, direcao, { cores: CORES_PEIXE[arquivo] || {}, ...opcoes });
}

/** Coral de galhos: ramos que sobem abrindo, ponta mais grossa e mais clara. */
export function coral(kit, nome, base, altura, corA, corB, linha) {
  const els = [[base, altura * 0.16, [1.4, 1.4, 0.6]]];
  const rnd = aleatorio(nome);
  const galho = (p, d, comp, r, nivel) => {
    const fim = p.map((v, k) => v + d[k] * comp);
    els.push(...cadeia(p, fim, r, r * 0.8));
    els.push([fim, r * 1.25]);
    if (nivel < 3) {
      for (let i = 0; i < (nivel ? 2 : 3); i++) {
        const nd = new THREE.Vector3(d[0] + rnd.uniforme(-0.7, 0.7), d[1] + rnd.uniforme(-0.5, 0.5), d[2] + 0.35).normalize();
        galho(fim, nd.toArray(), comp * rnd.uniforme(0.6, 0.8), r * 0.78, nivel + 1);
      }
    }
  };
  galho(base, [0, 0, 1], altura * 0.36, altura * 0.1, 0);
  const geo = blob(els, altura * 0.018);
  return kit.objeto(nome, geo, kit.matGradiente(corA, corB, base[2], base[2] + altura), { linha });
}

/** Tufo de fitas achatadas e onduladas. O pivô fica na base, para balançar a partir do chão. */
export function alga(kit, nome, base, altura, nFitas, linha, fase = 0) {
  const els = [];
  const rnd = aleatorio(nome);
  for (let i = 0; i < nFitas; i++) {
    const ang = 2 * Math.PI * i / nFitas + rnd.uniforme(-0.3, 0.3);
    const alt = altura * rnd.uniforme(0.6, 1.0);
    const lado = [Math.cos(ang), Math.sin(ang)];
    for (let j = 0; j < 40; j++) {
      const u = j / 39;
      const onda = 0.07 * altura * Math.sin(5.5 * u + fase + i) * u;
      const d = 0.05 * altura * u + onda;
      const larg = altura * 0.075 * (1 - 0.55 * u) * (0.7 + 0.3 * Math.sin(Math.PI * Math.min(1, u * 1.3)));
      els.push([[lado[0] * d, lado[1] * d, alt * u], larg, [1.0, 0.4, 1.3]]);
    }
  }
  const geo = blob(els, altura * 0.01);
  const ob = kit.objeto(nome, geo, kit.matGradiente(PALETA.alga, PALETA.alga_ponta, 0, altura), { linha });
  ob.position.set(...base);
  return ob;
}

export function anemona(kit, nome, base, raio, linha, n = 26) {
  const els = [[base, raio * 0.75, [1.3, 1.3, 0.8]]];
  const rnd = aleatorio(nome);
  for (let i = 0; i < n; i++) {
    const ang = 2 * Math.PI * i / n + rnd.uniforme(-0.12, 0.12);
    const anel = i % 2 ? 0.55 : 0.85;
    const p0 = [base[0] + Math.cos(ang) * raio * anel * 0.6, base[1] + Math.sin(ang) * raio * anel * 0.6, base[2] + raio * 0.25];
    const comp = raio * rnd.uniforme(1.0, 1.4);
    const aberto = 0.55 + 0.35 * anel;
    const curva = (u) => [Math.cos(ang) * comp * aberto * u * u, Math.sin(ang) * comp * aberto * u * u, 0];
    els.push(...cadeia(p0, [p0[0], p0[1], p0[2] + comp], raio * 0.16, raio * 0.11, 0.4, curva));
  }
  const geo = blob(els, raio * 0.05);
  const z0 = base[2];
  return kit.objeto(nome, geo, kit.matGradiente(PALETA.anemona, PALETA.anemona_ponta, z0, z0 + raio * 1.5), { linha });
}

export function estrela(kit, nome, centro, raio, linha, giro = 0) {
  let els = [[centro, raio * 0.42]];
  for (let i = 0; i < 5; i++) {
    const a = giro + 2 * Math.PI * i / 5;
    els.push(...cadeia(centro, [centro[0] + Math.cos(a) * raio, centro[1] + Math.sin(a) * raio, centro[2]], raio * 0.3, raio * 0.12, 0.35));
  }
  els = els.map(([p, r]) => [p, r, [1.0, 1.0, 0.55]]);
  return kit.objeto(nome, blob(els, raio * 0.06), kit.matToon(PALETA.estrela), { linha });
}

export function pedra(kit, nome, centro, tam, cor, linha, achatar = 0.6) {
  const g = new THREE.IcosahedronGeometry(1, 5);
  const rnd = aleatorio(nome);
  const f = [rnd.uniforme(0, 6.28), rnd.uniforme(0, 6.28), rnd.uniforme(0, 6.28)];
  const pos = g.attributes.position;
  const n = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++) {
    n.fromBufferAttribute(pos, i).normalize();
    const k = 1 + 0.12 * Math.sin(3 * n.x + f[0]) + 0.1 * Math.sin(4 * n.y + f[1]) + 0.08 * Math.sin(5 * n.z + f[2]);
    pos.setXYZ(i, n.x * tam[0] * k + centro[0], n.y * tam[1] * k + centro[1], n.z * tam[2] * k * achatar + centro[2]);
  }
  const geo = mergeSuave(g);
  return kit.objeto(nome, geo, kit.matToon(cor), { linha });
}

/** Icosaedro do Three.js vem com vértice repetido por face: funde para sombrear liso. */
function mergeSuave(g) {
  g.deleteAttribute('normal');
  g.deleteAttribute('uv');
  const idx = [];
  const mapa = new Map();
  const pos = [];
  const a = g.attributes.position;
  for (let i = 0; i < a.count; i++) {
    const chave = `${a.getX(i).toFixed(5)},${a.getY(i).toFixed(5)},${a.getZ(i).toFixed(5)}`;
    if (!mapa.has(chave)) {
      mapa.set(chave, pos.length / 3);
      pos.push(a.getX(i), a.getY(i), a.getZ(i));
    }
    idx.push(mapa.get(chave));
  }
  const out = new THREE.BufferGeometry();
  out.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  out.setIndex(idx);
  out.computeVertexNormals();
  return out;
}

/** Seixos embutidos no corte da areia. plano: ['y', valor, a0, a1] ou ['x', valor, a0, a1]. */
export function seixos(kit, nome, plano, faixaZ, n, cor, linha, tam = 0.035) {
  const rnd = aleatorio(nome);
  const [eixo, v, a0, a1] = plano;
  for (let i = 0; i < n; i++) {
    const a = rnd.uniforme(a0 + 0.05, a1 - 0.05);
    const z = rnd.uniforme(...faixaZ);
    const t = tam * rnd.uniforme(0.6, 1.3);
    const c = eixo === 'y' ? [a, v, z] : [v, a, z];
    pedra(kit, `${nome}_${i}`, c, [t * 1.3, t * 1.3, t], cor, linha, 0.75);
  }
}

/** Feixe de luz que some para baixo (alfa = altura^1,6 * alfa). */
export function feixe(kit, nome, topo, baseZ, raioTopo, raioBase, alfa) {
  const alt = topo[2] - baseZ;
  const g = new THREE.CylinderGeometry(raioTopo, raioBase, alt, 24, 10, true);
  g.rotateX(Math.PI / 2); // cilindro do Three.js em pé no Y; aqui, no Z
  g.translate(topo[0], topo[1], (topo[2] + baseZ) / 2);
  const pos = g.attributes.position;
  const cor = [];
  const c = kit.cor('#E8FFF8');
  for (let i = 0; i < pos.count; i++) {
    const u = (pos.getZ(i) - baseZ) / alt;
    cor.push(c.r, c.g, c.b, Math.pow(Math.max(0, u), 1.6) * alfa);
  }
  g.setAttribute('color', new THREE.Float32BufferAttribute(cor, 4));
  const mat = new THREE.MeshBasicMaterial({ vertexColors: true, transparent: true, depthWrite: false, side: THREE.DoubleSide });
  return kit.objeto(nome, g, mat, { linha: 0 });
}

/** Areia com cáustica toon (linhas claras de Voronoi) só nas faces viradas para cima. */
function matAreiaTopo(kit) {
  const m = kit.matToon(PALETA.areia, 'padrao', { plano: true });
  m.onBeforeCompile = (sh) => {
    sh.uniforms.corLinha = { value: kit.cor('#FFF4D2') };
    sh.vertexShader = 'varying vec3 vObj;\n' + sh.vertexShader.replace(
      '#include <begin_vertex>', '#include <begin_vertex>\n\tvObj = position;');
    sh.fragmentShader = `uniform vec3 corLinha;
varying vec3 vObj;
vec2 hash2(vec2 p) {
  p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
  return fract(sin(p) * 43758.5453);
}
float vorBorda(vec2 x) {
  vec2 n = floor(x), f = fract(x), mg, mr;
  float md = 8.0;
  for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) {
    vec2 g = vec2(float(i), float(j));
    vec2 r = g + hash2(n + g) - f;
    float d = dot(r, r);
    if (d < md) { md = d; mr = r; mg = g; }
  }
  md = 8.0;
  for (int j = -2; j <= 2; j++) for (int i = -2; i <= 2; i++) {
    vec2 g = mg + vec2(float(i), float(j));
    vec2 r = g + hash2(n + g) - f;
    if (dot(mr - r, mr - r) > 0.00001) md = min(md, dot(0.5 * (mr + r), normalize(r - mr)));
  }
  return md;
}
` + sh.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>
\tvec3 nObj = normalize(cross(dFdx(vObj), dFdy(vObj)));
\tfloat linha = step(vorBorda(vObj.xy * 5.0), 0.035) * step(0.6, abs(nObj.z));
\tdiffuseColor.rgb = mix(diffuseColor.rgb, corLinha, linha * 0.55);`);
  };
  m.customProgramCacheKey = () => 'areiaTopo';
  return m;
}

/** Superfície de areia ondulada, fechada até zBase (as laterais viram o corte da fatia). */
export function areiaTopo(kit, nome, x0, x1, y0, y1, zBase, altura, linha) {
  const g = caixa(x0, x1, y0, y1, zBase, zBase + altura, [48, 36, 1]);
  const pos = g.attributes.position;
  const meio = zBase + altura / 2;
  for (let i = 0; i < pos.count; i++) {
    if (pos.getZ(i) < meio) continue;
    const x = pos.getX(i), y = pos.getY(i);
    const h = altura * (0.55 + 0.25 * Math.sin(4.0 * x + 1.3) * Math.cos(3.2 * y) + 0.2 * Math.sin(9 * x + 5 * y));
    pos.setZ(i, zBase + h);
  }
  g.computeVertexNormals();
  return kit.objeto(nome, g, matAreiaTopo(kit), { linha });
}

/** A fatia: estratos de areia no corte, areia ondulada em cima, água em caixa de vidro e superfície. */
export function blocoOceano(kit, L, P, H, BASE, linha) {
  const [x0, x1, y0, y1] = [-L / 2, L / 2, -P / 2, P / 2];
  for (const [nome, za, zb, cor] of [['estrato_fundo', -BASE, -BASE * 0.62, PALETA.areia_funda],
    ['estrato_meio', -BASE * 0.62, -BASE * 0.28, PALETA.areia_meio]]) {
    kit.objeto(nome, caixa(x0, x1, y0, y1, za, zb), kit.matToon(cor, 'padrao', { plano: true }), { linha });
  }
  areiaTopo(kit, 'areia', x0, x1, y0, y1, -BASE * 0.28, BASE * 0.28 + 0.06, linha);
  seixos(kit, 'seixo_f', ['y', y0, x0, x1], [-BASE * 0.95, -BASE * 0.35], 16, PALETA.seixo, linha * 0.7);
  seixos(kit, 'seixo_l', ['x', x1, y0, y1], [-BASE * 0.95, -BASE * 0.35], 10, PALETA.seixo, linha * 0.7);
  seixos(kit, 'concha_f', ['y', y0, x0, x1], [-BASE * 0.25, -0.02], 6, '#F7E7CE', linha * 0.7, 0.022);

  // Água: só as faces de trás da caixa (vistas por dentro), do azul fundo embaixo à cor da água em cima.
  const ga = caixa(x0, x1, y0, y1, -BASE - 0.01, H);
  const pa = ga.attributes.position;
  const fundo = kit.cor('#0E5A6E'), topo = kit.cor(PALETA.agua);
  const cores = [];
  for (let i = 0; i < pa.count; i++) {
    const c = fundo.clone().lerp(topo, (pa.getZ(i) + BASE + 0.01) / (H + BASE + 0.01));
    cores.push(c.r, c.g, c.b);
  }
  ga.setAttribute('color', new THREE.Float32BufferAttribute(cores, 3));
  const agua = kit.objeto('agua', ga, new THREE.MeshBasicMaterial({
    vertexColors: true, transparent: true, opacity: 0.55, depthWrite: false, side: THREE.BackSide,
  }), { linha: 0 });

  // Vidro: só as 12 arestas da caixa, em barras de 12 mm.
  const e = 0.012, zA = -BASE, zB = H;
  const barras = [];
  for (const x of [x0, x1]) for (const y of [y0, y1]) barras.push(caixa(x - e / 2, x + e / 2, y - e / 2, y + e / 2, zA, zB));
  for (const x of [x0, x1]) for (const z of [zA, zB]) barras.push(caixa(x - e / 2, x + e / 2, y0, y1, z - e / 2, z + e / 2));
  for (const y of [y0, y1]) for (const z of [zA, zB]) barras.push(caixa(x0, x1, y - e / 2, y + e / 2, z - e / 2, z + e / 2));
  const vidro = new THREE.Group();
  vidro.name = 'vidro';
  kit.mundo.add(vidro);
  const matVidro = kit.matChapado('#D9FFFA');
  barras.forEach((g, i) => kit.objeto(`vidro_${i}`, g, matVidro, { linha: 0, pai: vidro }));

  // Superfície com ondinhas, vista por baixo.
  const gs = new THREE.PlaneGeometry(L, P, 60, 40);
  const ps = gs.attributes.position;
  for (let i = 0; i < ps.count; i++) {
    const x = ps.getX(i), y = ps.getY(i);
    ps.setZ(i, H + 0.025 * Math.sin(7 * x + 2 * y) + 0.015 * Math.sin(11 * y - 3 * x));
  }
  gs.computeVertexNormals();
  kit.objeto('superficie', gs, kit.matTransparente('#7FE6DC', 0.55, 'ambos'), { linha: 0 });
  return agua;
}

/** Bolha translúcida com brilho (para episódios que precisarem). */
export function bolha(kit, nome, centro, raio) {
  const ob = kit.objeto(nome, esfera(raio, centro, [24, 16]), kit.matTransparente(PALETA.agua_clara, 0.35, 'frente'), { linha: 0 });
  const b = [centro[0] - 0.4 * raio, centro[1] - 0.6 * raio, centro[2] + 0.45 * raio];
  kit.objeto(`${nome}_brilho`, esfera(raio * 0.22, b, [12, 8]), kit.matChapado('#FFFFFF'), { linha: 0, pai: ob });
  return ob;
}

// ------------------------------------------------------------------------------------------------ cenários gerais
// O fundo do mar é só um dos cenários. Para qualquer outro assunto, monte o lugar do assunto com estas peças (ou com
// caixa/esfera/tubo/blob do motor3d.js) e escolha o "fundo" do episodio.json que combina (casa, tempestade, ceu...).

/** Cômodo de casa em corte: piso de tábuas, parede do fundo com janela, parede da esquerda e rodapé. */
export function blocoComodo(kit, L, P, H, BASE, linha, {
  parede = '#F4D9B0', parede2 = '#E6BF8E', piso = '#C98B55', piso2 = '#A86A3E', rodape = '#FFF8EC',
  ceu = '#5B6E9A', janela = true,
} = {}) {
  const [x0, x1, y0, y1] = [-L / 2, L / 2, -P / 2, P / 2];
  const e = 0.06; // espessura das paredes (m)
  const partes = {};
  partes.base = kit.objeto('comodo_base', caixa(x0, x1, y0, y1, -BASE, 0), kit.matToon(piso2, 'padrao', { plano: true }), { linha });
  const nTabuas = 7;
  for (let i = 0; i < nTabuas; i++) {
    const ya = y0 + (P * i) / nTabuas, yb = y0 + (P * (i + 1)) / nTabuas - 0.006;
    kit.objeto(`comodo_tabua_${i}`, caixa(x0, x1, ya, yb, 0, 0.018), kit.matToon(i % 2 ? piso : piso2, 'suave', { plano: true }), { linha: linha * 0.5 });
  }
  partes.fundo = kit.objeto('comodo_parede_fundo', caixa(x0, x1, y1 - e, y1, 0, H), kit.matToon(parede, 'suave', { plano: true }), { linha });
  partes.lado = kit.objeto('comodo_parede_lado', caixa(x0, x0 + e, y0, y1, 0, H), kit.matToon(parede2, 'suave', { plano: true }), { linha });
  const matRod = kit.matToon(rodape, 'suave', { plano: true });
  kit.objeto('comodo_rodape_fundo', caixa(x0 + e, x1, y1 - e - 0.012, y1 - e, 0.018, 0.09), matRod, { linha: linha * 0.6 });
  kit.objeto('comodo_rodape_lado', caixa(x0 + e, x0 + e + 0.012, y0, y1 - e, 0.018, 0.09), matRod, { linha: linha * 0.6 });
  if (janela) {
    const [jx0, jx1, jz0, jz1] = [L * 0.08, L * 0.38, H * 0.42, H * 0.82];
    const yv = y1 - e - 0.004, f = 0.035;
    partes.vidro = kit.objeto('comodo_janela_vidro', caixa(jx0, jx1, yv - 0.004, yv, jz0, jz1), kit.matChapado(ceu), { linha: 0 });
    const matMold = kit.matToon(rodape, 'suave', { plano: true });
    for (const [n, a, b, c, d] of [['b', jx0 - f, jx1 + f, jz0 - f, jz0], ['c', jx0 - f, jx1 + f, jz1, jz1 + f],
      ['e', jx0 - f, jx0, jz0, jz1], ['d', jx1, jx1 + f, jz0, jz1], ['m', (jx0 + jx1) / 2 - f / 3, (jx0 + jx1) / 2 + f / 3, jz0, jz1]]) {
      kit.objeto(`comodo_janela_${n}`, caixa(a, b, yv - 0.03, yv, c, d), matMold, { linha: linha * 0.6 });
    }
  }
  return partes;
}

/** Chão de grama (ou de outra cor) em bloco, com terra no corte. */
export function chao(kit, nome, L, P, BASE, linha, { topo = '#7BCB5A', terra = '#8A5A3C' } = {}) {
  const [x0, x1, y0, y1] = [-L / 2, L / 2, -P / 2, P / 2];
  kit.objeto(`${nome}_terra`, caixa(x0, x1, y0, y1, -BASE, -0.04), kit.matToon(terra, 'padrao', { plano: true }), { linha });
  return kit.objeto(`${nome}_topo`, caixa(x0, x1, y0, y1, -0.04, 0), kit.matToon(topo, 'suave', { plano: true }), { linha });
}

/** Casinha cartoon (corpo, telhado de duas águas, porta, janela e chaminé), com a base em `local`. */
export function casinha(kit, nome, local, escala = 1, { cor = '#FFE3B0', telhado = '#E5484D', porta = '#8A5A3C', linha = 0.005, pai = kit.mundo } = {}) {
  const raiz = kit.grupo(nome, pai, local);
  raiz.scale.setScalar(escala);
  const [l, p, h] = [0.5, 0.4, 0.36];
  const corpo = kit.objeto(`${nome}_corpo`, caixa(-l / 2, l / 2, -p / 2, p / 2, 0, h), kit.matToon(cor), { linha, pai: raiz });
  const aba = Math.hypot(l / 2 + 0.04, 0.2);
  const ang = Math.atan2(0.2, l / 2 + 0.04);
  for (const s of [-1, 1]) {
    const g = caixa(-aba / 2, aba / 2, -p / 2 - 0.04, p / 2 + 0.04, -0.015, 0.015);
    const m = kit.objeto(`${nome}_telhado_${s}`, g, kit.matToon(telhado), { linha, pai: raiz });
    m.position.set(s * (l / 4 + 0.01), 0, h + 0.1);
    m.rotation.y = s * ang;
  }
  // oitão: prisma quadrado girado 45° e achatado, para fechar o triângulo debaixo do telhado
  const oitao = kit.grupo(`${nome}_oitao`, raiz, [0, 0, h]);
  oitao.scale.set((l / 2) / 0.1414, 1, 0.19 / 0.1414);
  const po = kit.objeto(`${nome}_oitao_m`, caixa(-0.1, 0.1, -p / 2, p / 2, -0.1, 0.1), kit.matToon(cor), { linha, pai: oitao });
  po.rotation.y = Math.PI / 4;
  kit.objeto(`${nome}_chamine`, caixa(0.1, 0.17, -0.05, 0.02, h + 0.05, h + 0.3), kit.matToon('#B9774A'), { linha, pai: raiz });
  kit.objeto(`${nome}_porta`, caixa(-0.06, 0.06, -p / 2 - 0.012, -p / 2, 0, 0.2), kit.matToon(porta), { linha: linha * 0.7, pai: raiz });
  kit.objeto(`${nome}_janela`, caixa(0.1, 0.2, -p / 2 - 0.012, -p / 2, 0.16, 0.26), kit.matChapado('#FFE45E'), { linha: linha * 0.7, pai: raiz });
  return { raiz, corpo };
}

/** Nuvem fofa de bolhas (clara no céu, escura na tempestade). */
export function nuvem(kit, nome, centro, tam = 0.3, { cor = '#FFFFFF', cor2 = null, semente = 1, linha = 0.004, pai = kit.mundo } = {}) {
  const rnd = aleatorio(semente);
  const els = [];
  for (let i = 0; i < 7; i++) {
    const u = i / 6 - 0.5;
    els.push([[u * tam * 1.6, (rnd() - 0.5) * tam * 0.3, (0.25 - Math.abs(u)) * tam * 0.8 + rnd() * tam * 0.15], tam * (0.38 + 0.18 * rnd())]);
  }
  const g = blob(els, Math.max(0.006, tam * 0.03));
  g.translate(...centro);
  const mat = cor2 ? kit.matGradiente(cor2, cor, centro[2] - tam * 0.3, centro[2] + tam * 0.4, 'suave') : kit.matToon(cor, 'suave');
  return kit.objeto(nome, g, mat, { linha, pai });
}

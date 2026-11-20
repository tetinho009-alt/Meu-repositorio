/*! © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C */
/**
 * motor3d.js: base do Explicativo 3D no navegador (Three.js), para máquina sem placa de vídeo.
 *
 * Espelha o visual do motor do Blender (motor/base3d.py e motor/kit3d.py): sombreado toon de 3 tons com a luz
 * presa na câmera, contorno de nanquim por casca invertida, cores da paleta, peixes CC0 (GLB), câmera vertical
 * e a projeção dos rótulos na tela.
 *
 * Eixos: tudo o que a cena monta entra em `kit.mundo`, que usa os eixos do Blender (Z para cima, -Y virado para a
 * câmera). Assim as medidas dos scripts do Blender valem aqui sem conversão.
 *
 * Determinismo: nada aqui lê o relógio. O quadro do tempo t sai igual em qualquer máquina.
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { mergeGeometries, mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';

export const PALETA = {
  tinta: '#1B1530',
  agua: '#3CC8C8',
  agua_clara: '#9FF3E8',
  areia: '#F6D38C',
  areia_meio: '#E2AE62',
  areia_funda: '#B9774A',
  seixo: '#8A5A3C',
  rocha: '#6B7BA4',
  rocha_escura: '#4E5A82',
  coral: '#FF6F59',
  coral_ponta: '#FFC07A',
  coral2: '#C77DFF',
  coral2_ponta: '#FF9FD0',
  alga: '#3DBE7A',
  alga_ponta: '#B5E86A',
  anemona: '#FF8FAB',
  anemona_ponta: '#FFE3EC',
  estrela: '#FFB23E',
  branco: '#FFF8EC',
};

// Tons do toon (iguais ao base3d.TOM): sombra, brilho e os limiares de N.L entre os 3 degraus.
export const TOM = {
  padrao: [0.68, 1.10, 0.30, 0.95],
  suave: [0.86, 1.04, 0.16, 0.97],
  chapado: [1.0, 1.0, 0.0, 0.99],
};
// O mapa de degraus guarda valor / TETO e a luz vale PI * TETO: assim o degrau de brilho passa de 1.
const TETO = 1.25;

// ------------------------------------------------------------------------------------------------ tempo e movimento

/** Rampa suave (smoothstep) de 0 em `a` a 1 em `b`. */
export function suave(a, b, x) {
  if (b === a) return x >= b ? 1 : 0;
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
}

/** Ease com passada (back-out): passa um pouco do ponto e volta. */
export function volta(u, s = 1.7) {
  u = Math.max(0, Math.min(1, u)) - 1;
  return 1 + u * u * ((s + 1) * u + s);
}

/** 0 -> pico -> 0 em `dur` segundos: o quique de uma parte no ritmo da fala. */
export function pulo(t, t0, dur = 0.32, alto = 1) {
  if (t < t0 || t > t0 + dur) return 0;
  return alto * Math.sin(Math.PI * (t - t0) / dur);
}

export const rad = (g) => g * Math.PI / 180;

/** Gerador pseudoaleatório com semente (número ou texto): mesma semente, mesma cena. */
export function aleatorio(semente) {
  let h = 2166136261 >>> 0;
  for (const c of String(semente)) h = Math.imul(h ^ c.charCodeAt(0), 16777619) >>> 0;
  const r = () => {
    h = (h + 0x6D2B79F5) >>> 0;
    let x = h;
    x = Math.imul(x ^ (x >>> 15), x | 1);
    x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
  r.uniforme = (a, b) => a + (b - a) * r();
  return r;
}

/**
 * Planos de câmera (ou qualquer valor) marcados no tempo: [[marco, v1, v2, ...], ...]. Em cada marco o valor sai do
 * plano anterior e chega ao novo em `transicao` segundos (igual ao camera_em do cena.py).
 */
export function planos(lista, transicao = 1.6) {
  return (t) => {
    let k = 0;
    for (let i = 0; i < lista.length; i++) if (lista[i][0] <= t) k = i;
    if (k === 0) return lista[0].slice(1);
    const u = suave(lista[k][0], lista[k][0] + transicao, t);
    return lista[k].slice(1).map((b, i) => lista[k - 1][i + 1] + (b - lista[k - 1][i + 1]) * u);
  };
}

/** Minúsculo, sem acento e sem pontuação ("Água-viva," -> "aguaviva"), igual ao tempos.norm. */
export function norm(s) {
  return s.normalize('NFKD').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
}

/** Linha do tempo da narração (tempos.json do alinhar.py): marcos por palavra, nunca por segundo. */
export class Tempos {
  constructor(palavras) {
    if (!palavras || !palavras.length) throw new Error('tempos.json vazio');
    this.palavras = palavras;
    this.fim = palavras[palavras.length - 1].fim;
  }

  quando(palavra, depois = 0, fim = false) {
    const alvo = norm(palavra);
    for (const w of this.palavras) {
      if (w.ini >= depois && norm(w.palavra).startsWith(alvo)) return fim ? w.fim : w.ini;
    }
    throw new Error(`a palavra '${palavra}' não está na narração (confira o narrador.txt e o tempos.json)`);
  }
}

// ------------------------------------------------------------------------------------------------ geometria pura

/** Elementos de metaball ao longo de um segmento (com desvio opcional), raio afinando de r0 a r1. */
export function cadeia(p0, p1, r0, r1, passo = 0.45, curva = null) {
  const comp = Math.hypot(p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]);
  const n = Math.max(2, Math.floor(comp / (passo * Math.min(r0, r1))) + 1);
  const out = [];
  for (let i = 0; i < n; i++) {
    const u = i / (n - 1);
    let p = [0, 1, 2].map((k) => p0[k] + (p1[k] - p0[k]) * u);
    if (curva) {
      const d = curva(u);
      p = p.map((v, k) => v + d[k]);
    }
    out.push([p, r0 + (r1 - r0) * u]);
  }
  return out;
}

/**
 * Metaball -> malha, com o mesmo campo do Blender: cada elemento soma 2 * (1 - d²/r²)³ e a superfície fica onde o
 * total passa do `limiar` (0,6 no Blender). Elementos: [centro, raio] ou [centro, raio, [sx, sy, sz]] (elipsoide).
 * A malha sai por "surface nets" numa grade de lado `resolucao` (metros).
 */
export function blob(elementos, resolucao = 0.012, limiar = 0.6) {
  const lo = [Infinity, Infinity, Infinity];
  const hi = [-Infinity, -Infinity, -Infinity];
  for (const [c, r, s = [1, 1, 1]] of elementos) {
    for (let k = 0; k < 3; k++) {
      lo[k] = Math.min(lo[k], c[k] - r * s[k]);
      hi[k] = Math.max(hi[k], c[k] + r * s[k]);
    }
  }
  const h = resolucao;
  const o = lo.map((v) => v - 2 * h);
  const n = [0, 1, 2].map((k) => Math.ceil((hi[k] - lo[k]) / h) + 5);
  const [nx, ny, nz] = n;
  const campo = new Float32Array(nx * ny * nz).fill(-limiar);
  const id = (i, j, k) => (k * ny + j) * nx + i;

  for (const [c, r, s = [1, 1, 1]] of elementos) {
    const ir2 = 1 / (r * r);
    const a = [0, 1, 2].map((k) => Math.max(0, Math.floor((c[k] - r * s[k] - o[k]) / h)));
    const b = [0, 1, 2].map((k) => Math.min(n[k] - 1, Math.ceil((c[k] + r * s[k] - o[k]) / h)));
    for (let k = a[2]; k <= b[2]; k++) {
      const dz = (o[2] + k * h - c[2]) / s[2];
      for (let j = a[1]; j <= b[1]; j++) {
        const dy = (o[1] + j * h - c[1]) / s[1];
        for (let i = a[0]; i <= b[0]; i++) {
          const dx = (o[0] + i * h - c[0]) / s[0];
          const d2 = (dx * dx + dy * dy + dz * dz) * ir2;
          if (d2 < 1) {
            const u = 1 - d2;
            campo[id(i, j, k)] += 2 * u * u * u;
          }
        }
      }
    }
  }
  return redeSuperficie(campo, n, o, h);
}

const CANTOS = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]];
const ARESTAS = [[0, 1], [2, 3], [4, 5], [6, 7], [0, 2], [1, 3], [4, 6], [5, 7], [0, 4], [1, 5], [2, 6], [3, 7]];

/** Surface nets: um vértice por célula cortada, um quadrado por aresta da grade que cruza a superfície. */
function redeSuperficie(campo, n, o, h) {
  const [nx, ny, nz] = n;
  const id = (i, j, k) => (k * ny + j) * nx + i;
  const cel = new Int32Array(nx * ny * nz).fill(-1);
  const pos = [];
  const v = new Float32Array(8);
  for (let k = 0; k < nz - 1; k++) {
    for (let j = 0; j < ny - 1; j++) {
      for (let i = 0; i < nx - 1; i++) {
        let dentro = 0;
        for (let c = 0; c < 8; c++) {
          v[c] = campo[id(i + CANTOS[c][0], j + CANTOS[c][1], k + CANTOS[c][2])];
          if (v[c] > 0) dentro++;
        }
        if (dentro === 0 || dentro === 8) continue;
        let sx = 0, sy = 0, sz = 0, m = 0;
        for (const [a, b] of ARESTAS) {
          if ((v[a] > 0) === (v[b] > 0)) continue;
          const t = v[a] / (v[a] - v[b]);
          sx += CANTOS[a][0] + (CANTOS[b][0] - CANTOS[a][0]) * t;
          sy += CANTOS[a][1] + (CANTOS[b][1] - CANTOS[a][1]) * t;
          sz += CANTOS[a][2] + (CANTOS[b][2] - CANTOS[a][2]) * t;
          m++;
        }
        cel[id(i, j, k)] = pos.length / 3;
        pos.push(o[0] + (i + sx / m) * h, o[1] + (j + sy / m) * h, o[2] + (k + sz / m) * h);
      }
    }
  }
  // Eixos em ordem cíclica (a, b, c): os 4 vizinhos da aresta em (b, c) giram no sentido que aponta a normal para +a.
  const idx = [];
  const p = [0, 0, 0];
  const viz = [[-1, -1], [0, -1], [0, 0], [-1, 0]];
  for (let a = 0; a < 3; a++) {
    const b = (a + 1) % 3, c = (a + 2) % 3;
    for (p[2] = 1; p[2] < nz - 1; p[2]++) {
      for (p[1] = 1; p[1] < ny - 1; p[1]++) {
        for (p[0] = 1; p[0] < nx - 1; p[0]++) {
          if (p[a] >= n[a] - 1) continue;
          const q = p.slice();
          q[a]++;
          const f0 = campo[id(p[0], p[1], p[2])];
          const f1 = campo[id(q[0], q[1], q[2])];
          if ((f0 > 0) === (f1 > 0)) continue;
          const vs = viz.map(([db, dc]) => {
            const r = p.slice();
            r[b] += db;
            r[c] += dc;
            return cel[id(r[0], r[1], r[2])];
          });
          if (vs.some((x) => x < 0)) continue;
          if (f0 > 0) idx.push(vs[0], vs[1], vs[2], vs[0], vs[2], vs[3]);
          else idx.push(vs[0], vs[2], vs[1], vs[0], vs[3], vs[2]);
        }
      }
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setIndex(idx);
  geo.computeVertexNormals();
  return geo;
}

/** Tubo por uma lista de pontos (igual ao base3d.tubo); `afinar`: lens, fim ou uniforme. */
export function tubo(pontos, raio, nu = 8, afinar = 'lens') {
  const pts = pontos.map((q) => new THREE.Vector3(...q));
  const n = pts.length;
  const pos = [];
  const idx = [];
  let ref = new THREE.Vector3(0, 0, 1);
  for (let k = 0; k < n; k++) {
    const t = pts[Math.min(k + 1, n - 1)].clone().sub(pts[Math.max(k - 1, 0)]).normalize();
    if (Math.abs(t.dot(ref)) > 0.95) ref = new THREE.Vector3(1, 0, 0);
    const u = t.clone().cross(ref).normalize();
    const w = t.clone().cross(u).normalize();
    const s = k / (n - 1);
    const f = afinar === 'lens' ? 0.35 + 0.65 * Math.sin(Math.PI * s) : afinar === 'fim' ? 1 - 0.75 * s : 1;
    for (let i = 0; i < nu; i++) {
      const th = 2 * Math.PI * i / nu;
      const q = pts[k].clone().addScaledVector(u, Math.cos(th) * raio * f).addScaledVector(w, Math.sin(th) * raio * f);
      pos.push(q.x, q.y, q.z);
    }
  }
  for (let j = 0; j < n - 1; j++) {
    for (let i = 0; i < nu; i++) {
      const a = j * nu + i, b = j * nu + (i + 1) % nu;
      idx.push(a, b, b + nu, a, b + nu, a + nu);
    }
  }
  const i0 = pos.length / 3, i1 = i0 + 1;
  pos.push(...pts[0].toArray(), ...pts[n - 1].toArray());
  for (let i = 0; i < nu; i++) {
    idx.push(i0, (i + 1) % nu, i);
    idx.push(i1, (n - 1) * nu + i, (n - 1) * nu + (i + 1) % nu);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setIndex(idx);
  geo.computeVertexNormals();
  return geo;
}

/** Caixa alinhada aos eixos, de (x0, y0, z0) a (x1, y1, z1). */
export function caixa(x0, x1, y0, y1, z0, z1, segmentos = [1, 1, 1]) {
  const g = new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0, ...segmentos);
  g.translate((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
  return g;
}

export function esfera(raio, centro = [0, 0, 0], seg = [20, 14]) {
  const g = new THREE.SphereGeometry(raio, seg[0], seg[1]);
  g.translate(...centro);
  return g;
}

/** Junta várias geometrias numa só (menos objetos para desenhar). */
export function mesclar(geos) {
  const limpas = geos.map((g) => {
    const c = g.index ? g : g.toNonIndexed();
    for (const nome of Object.keys(c.attributes)) if (nome !== 'position' && nome !== 'normal') c.deleteAttribute(nome);
    return c;
  });
  return mergeGeometries(limpas, false);
}

// ------------------------------------------------------------------------------------------------ motor

const _v = new THREE.Vector3();
const _q = new THREE.Quaternion();
const _s = new THREE.Vector3();

export class Motor {
  constructor(renderer, { largura = 1080, altura = 1920, modelos = '/modelos/' } = {}) {
    this.renderer = renderer;
    this.largura = largura;
    this.altura = altura;
    this.modelos = modelos;
    this.cena = new THREE.Scene();
    this.mundo = new THREE.Group();
    this.mundo.name = 'mundo_eixos_blender';
    this.mundo.rotation.x = -Math.PI / 2; // Z do Blender vira o Y do Three.js
    this.cena.add(this.mundo);
    this.camera = null;
    this._degraus = {};
    this._cascaMat = new Map();
    this._cascaGeo = new Map();
    this._rotulos = [];
    this._mixers = [];
    this._loader = new GLTFLoader();
  }

  cor(hexa) {
    return new THREE.Color(hexa);
  }

  // -------------------------------------------------------------------------------------------- materiais

  _degrau(tom) {
    if (!this._degraus[tom]) {
      const [sombra, brilho, l0, l1] = TOM[tom];
      const n = 256;
      const dados = new Uint8Array(n * 4);
      for (let i = 0; i < n; i++) {
        const nl = ((i + 0.5) / n) * 2 - 1; // o Three.js lê o mapa em N.L * 0,5 + 0,5
        const v = nl < l0 ? sombra : nl < l1 ? 1 : brilho;
        dados.fill(Math.round((v / TETO) * 255), i * 4, i * 4 + 4);
      }
      const tex = new THREE.DataTexture(dados, n, 1, THREE.RGBAFormat);
      tex.minFilter = tex.magFilter = THREE.NearestFilter;
      tex.generateMipmaps = false;
      tex.needsUpdate = true;
      this._degraus[tom] = tex;
    }
    return this._degraus[tom];
  }

  /** Toon de 3 tons (sombra, luz, brilho), como o mat_toon do Blender. `plano`: faces chapadas, sem suavizar. */
  matToon(cor, tom = 'padrao', { plano = false, mapa = null } = {}) {
    return new THREE.MeshToonMaterial({ color: this.cor(cor), gradientMap: this._degrau(tom), flatShading: plano, map: mapa });
  }

  /** Toon com a cor variando na altura do objeto (Z local de z0 a z1), como o mat_gradiente do kit3d. */
  matGradiente(corA, corB, z0, z1, tom = 'padrao') {
    const m = this.matToon('#FFFFFF', tom);
    const a = this.cor(corA), b = this.cor(corB);
    m.onBeforeCompile = (sh) => {
      sh.uniforms.gradA = { value: a };
      sh.uniforms.gradB = { value: b };
      sh.uniforms.gradZ = { value: new THREE.Vector2(z0, z1) };
      sh.vertexShader = 'varying float vGradZ;\n' + sh.vertexShader.replace(
        '#include <begin_vertex>', '#include <begin_vertex>\n\tvGradZ = position.z;');
      sh.fragmentShader = 'uniform vec3 gradA;\nuniform vec3 gradB;\nuniform vec2 gradZ;\nvarying float vGradZ;\n' +
        sh.fragmentShader.replace('#include <color_fragment>', '#include <color_fragment>\n' +
          '\tdiffuseColor.rgb *= mix(gradA, gradB, clamp((vGradZ - gradZ.x) / (gradZ.y - gradZ.x), 0.0, 1.0));');
    };
    m.customProgramCacheKey = () => 'gradienteZ';
    return m;
  }

  /** Cor pura, sem luz (olho, brilho, aresta do vidro). */
  matChapado(cor) {
    return new THREE.MeshBasicMaterial({ color: this.cor(cor) });
  }

  /** Translúcido sem luz (água, superfície, feixe). `lado`: frente, tras ou ambos. */
  matTransparente(cor, alfa, lado = 'ambos', extra = {}) {
    const side = { frente: THREE.FrontSide, tras: THREE.BackSide, ambos: THREE.DoubleSide }[lado];
    return new THREE.MeshBasicMaterial({ color: this.cor(cor), transparent: true, opacity: alfa, depthWrite: false, side, ...extra });
  }

  // -------------------------------------------------------------------------------------------- contorno

  _matCasca(espessura) {
    const chave = espessura.toFixed(6);
    if (!this._cascaMat.has(chave)) {
      const m = new THREE.MeshBasicMaterial({ color: this.cor(PALETA.tinta), side: THREE.BackSide });
      m.onBeforeCompile = (sh) => {
        sh.uniforms.espessura = { value: espessura };
        sh.vertexShader = 'uniform float espessura;\n' + sh.vertexShader.replace(
          '#include <begin_vertex>', '#include <begin_vertex>\n\ttransformed += normalize(normal) * espessura;');
      };
      m.customProgramCacheKey = () => 'casca';
      this._cascaMat.set(chave, m);
    }
    return this._cascaMat.get(chave);
  }

  _geoCasca(geo, comOssos) {
    if (!this._cascaGeo.has(geo.uuid)) {
      let g = new THREE.BufferGeometry();
      g.setAttribute('position', geo.attributes.position);
      if (geo.index) g.setIndex(geo.index);
      if (comOssos) {
        for (const nome of ['normal', 'skinIndex', 'skinWeight']) if (geo.attributes[nome]) g.setAttribute(nome, geo.attributes[nome]);
      } else {
        // Normais médias por posição: a casca não racha nas quinas de faces chapadas.
        g = mergeVertices(g, 1e-5);
        g.computeVertexNormals();
      }
      this._cascaGeo.set(geo.uuid, g);
    }
    return this._cascaGeo.get(geo.uuid);
  }

  /** Casca invertida de nanquim; a espessura é em metros do mundo (compensa a escala do objeto). */
  contorno(mesh, espessura) {
    if (!(espessura > 0)) return null;
    mesh.updateWorldMatrix(true, false);
    mesh.matrixWorld.decompose(_v, _q, _s);
    const k = (Math.abs(_s.x) + Math.abs(_s.y) + Math.abs(_s.z)) / 3;
    const geo = this._geoCasca(mesh.geometry, mesh.isSkinnedMesh);
    const mat = this._matCasca(espessura / k);
    let casca;
    if (mesh.isSkinnedMesh) {
      casca = new THREE.SkinnedMesh(geo, mat);
      casca.bind(mesh.skeleton, mesh.bindMatrix);
      casca.bindMode = mesh.bindMode;
      casca.position.copy(mesh.position);
      casca.quaternion.copy(mesh.quaternion);
      casca.scale.copy(mesh.scale);
      mesh.parent.add(casca);
    } else {
      casca = new THREE.Mesh(geo, mat);
      mesh.add(casca);
    }
    casca.name = `${mesh.name}_contorno`;
    casca.frustumCulled = false;
    return casca;
  }

  // -------------------------------------------------------------------------------------------- objetos

  grupo(nome, pai = this.mundo, local = [0, 0, 0]) {
    const g = new THREE.Group();
    g.name = nome;
    g.position.set(...local);
    pai.add(g);
    return g;
  }

  /** Malha com material e contorno (linha em metros; 0 = sem contorno), filha de `pai`. */
  objeto(nome, geo, mat, { linha = 0.006, pai = this.mundo } = {}) {
    const m = new THREE.Mesh(geo, mat);
    m.name = nome;
    pai.add(m);
    this.contorno(m, linha);
    return m;
  }

  // -------------------------------------------------------------------------------------------- modelos GLB

  async carregarGLB(arquivo) {
    return this._loader.loadAsync(`${this.modelos}${arquivo}.glb`);
  }

  /**
   * Peixe GLB (CC0) com os materiais trocados pelo toon da paleta, a pose da animação de nado e o brilho no olho,
   * igual ao kit3d.peixe. `direcao`: ângulo (graus, em Z) para onde a cabeça aponta; 0 = +X, -90 = para a câmera.
   * O nado anda sozinho em `atualizar(t)`.
   */
  async peixe(nome, arquivo, comprimento, local, direcao, opcoes = {}) {
    const { cores = {}, acao = 'Swimming_Normal', linha = 0.005, brilho = true, tinta = null, pai = this.mundo } = opcoes;
    const gltf = await this.carregarGLB(arquivo);
    const modelo = gltf.scene;
    modelo.traverse((o) => { if (o.isMesh && o.name.startsWith('Icosphere')) o.removeFromParent(); });
    const eixos = new THREE.Group(); // GLB tem Y para cima; o mundo do kit, Z
    eixos.rotation.x = Math.PI / 2;
    eixos.add(modelo);
    const raiz = this.grupo(nome, pai);
    raiz.add(eixos);

    if (gltf.animations.length) {
      const mixer = new THREE.AnimationMixer(modelo);
      const clip = gltf.animations.find((a) => a.name.includes(acao)) || gltf.animations[0];
      mixer.clipAction(clip).play();
      mixer.setTime(0.5); // pose de medida, como o quadro 12 a 24 q/s do Blender
      this._mixers.push(mixer);
    }

    // medidas no espaço da raiz: comprimento em Y; a cabeça é o lado dos olhos
    raiz.updateMatrixWorld(true);
    const malhas = [];
    modelo.traverse((o) => { if (o.isMesh) malhas.push(o); });
    for (const m of malhas) if (m.isSkinnedMesh) m.skeleton.update();
    const paraRaiz = new THREE.Matrix4().copy(raiz.matrixWorld).invert();
    const centro = new THREE.Vector3();
    const olhos = [];
    let ymin = Infinity, ymax = -Infinity, total = 0;
    const p = new THREE.Vector3();
    for (const m of malhas) {
      const ehOlho = (m.material?.name || '').startsWith('Eyes');
      const mat = new THREE.Matrix4().multiplyMatrices(paraRaiz, m.matrixWorld);
      for (let i = 0; i < m.geometry.attributes.position.count; i++) {
        m.getVertexPosition(i, p).applyMatrix4(mat);
        centro.add(p);
        total++;
        ymin = Math.min(ymin, p.y);
        ymax = Math.max(ymax, p.y);
        if (ehOlho) olhos.push(p.clone());
      }
    }
    centro.divideScalar(total);
    let sinal = 1;
    if (olhos.length) sinal = olhos.reduce((s, q) => s + q.y, 0) / olhos.length > centro.y ? 1 : -1;
    const base = sinal > 0 ? 90 : -90;

    for (const m of malhas) {
      const nomeMat = m.material?.name || '';
      const chave = Object.keys(cores).find((k) => nomeMat.startsWith(k));
      if (chave) m.material = this.matToon(chave !== 'Eyes' && tinta ? tinta : cores[chave]);
      else if (m.material?.map) m.material = this.matToon('#FFFFFF', 'padrao', { mapa: m.material.map });
      else m.material = this.matToon('#8899AA');
      m.frustumCulled = false;
    }

    const k = comprimento / (ymax - ymin);
    const giro = rad(direcao - base);
    raiz.userData.direcao = direcao;
    raiz.scale.setScalar(k);
    raiz.rotation.z = giro;
    const desloc = centro.clone().multiplyScalar(k).applyAxisAngle(new THREE.Vector3(0, 0, 1), giro);
    raiz.position.set(local[0] - desloc.x, local[1] - desloc.y, local[2] - desloc.z);
    raiz.updateMatrixWorld(true);
    for (const m of malhas) this.contorno(m, linha);

    if (brilho && olhos.length) { // pontinho branco no olho: o modelo vem com olho todo preto
      for (const lado of [-1, 1]) {
        const grupo = olhos.filter((q) => (q.x > centro.x) === (lado > 0));
        if (!grupo.length) continue;
        const c = grupo.reduce((s, q) => s.add(q), new THREE.Vector3()).divideScalar(grupo.length);
        const r = Math.max(...grupo.map((q) => q.distanceTo(c)));
        const q = c.clone().add(new THREE.Vector3(lado * r * 0.62, sinal * r * 0.3, r * 0.42));
        this.objeto(`${nome}_brilho_${lado}`, esfera(r * 0.3, q.toArray(), [12, 8]), this.matChapado('#FFFFFF'), { linha: 0, pai: raiz });
      }
    }
    return raiz;
  }

  // -------------------------------------------------------------------------------------------- câmera e rótulos

  /**
   * Câmera vertical olhando o alvo de frente (pitch em graus), com a luz toon presa nela: a luz anda com a câmera,
   * então o sombreado não muda quando o plano muda. `lente` em mm com sensor vertical de 36 mm, como no Blender.
   */
  criarCamera(alvo, distancia, lente = 40, pitch = 11) {
    const fov = 2 * Math.atan(18 / lente) * 180 / Math.PI;
    this.camera = new THREE.PerspectiveCamera(fov, this.largura / this.altura, 0.05, 100);
    const luz = new THREE.DirectionalLight(0xFFFFFF, Math.PI * TETO);
    luz.position.set(-0.55, 0.6, 1.0); // o sol do Blender anda em (0,55, -0,6, -1) no espaço da câmera
    this.camera.add(luz, luz.target);
    this.cena.add(this.camera);
    this.mirar(alvo, distancia, pitch);
    return this.camera;
  }

  /** Reposiciona a câmera (eixos do Blender): mesmo cálculo do cena.py. */
  mirar(alvo, distancia, pitch) {
    const p = rad(pitch);
    const [ax, ay, az] = alvo;
    const by = ay - distancia * Math.cos(p);
    const bz = az + distancia * Math.sin(p);
    this.camera.position.set(ax, bz, -by);
    this.camera.lookAt(ax, az, -ay);
  }

  /** Registra um rótulo preso a um ponto local de um objeto (o nome tem de bater com o episodio.json). */
  rotulo(nome, objeto, ponto = [0, 0, 0]) {
    this._rotulos.push([nome, objeto, new THREE.Vector3(...ponto)]);
  }

  /** Posição na tela (0..1, y para baixo) de cada rótulo no quadro atual. */
  ancoras() {
    this.cena.updateMatrixWorld(true);
    const out = {};
    const r4 = (x) => Math.round(x * 10000) / 10000;
    for (const [nome, objeto, ponto] of this._rotulos) {
      const v = objeto.localToWorld(ponto.clone()).project(this.camera);
      out[nome] = [r4((v.x + 1) / 2), r4((1 - v.y) / 2)];
    }
    return out;
  }

  /** Anima o que é do motor (nado dos GLB) no tempo t. Chamado pela página depois do quadro(t) da cena. */
  atualizar(t) {
    for (const m of this._mixers) m.setTime(t);
  }

  renderizar() {
    this.renderer.render(this.cena, this.camera);
  }
}

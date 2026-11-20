/*! © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C */
/**
 * Exemplo fora do mar: "Um raio consegue entrar na sua casa? Consegue, pela fiação." Sala em corte com tempestade lá fora, o raio
 * vira personagem, cai do céu, a tomada leva um susto e a faísca corre pelo fio até ela.
 */
import { Tempos, caixa as cxa, planos, pulo, rad, suave, tubo, esfera, volta } from 'x3d/motor3d.js';
import * as C from 'x3d/cenario3d.js';
import * as B from 'x3d/bichos3d.js';

const [L, P, H, BASE] = [1.6, 1.2, 1.3, 0.3];
const LN = 0.006;
let kit, S;

export async function montar(THREE, motor, dados) {
  kit = motor;
  const tp = new Tempos(dados.tempos);
  const q = (p) => tp.quando(p);
  const T = { raio: q('raio'), entrar: q('entrar'), casa: q('casa'), consegue2: q('consegue', q('casa')), fiacao: q('fiação') };
  const duracao = tp.fim + 0.4 + dados.episodio.cta_segundos;

  const camera = planos([
    [0.0, 0.2, 1.25, 3.6, 10],
    [T.entrar, 0.1, 0.75, 3.0, 12],
    [T.fiacao, -0.35, 0.45, 2.2, 10],
    [tp.fim + 0.3, 0.0, 0.8, 3.4, 12],
  ], 0.7);

  C.blocoComodo(kit, L, P, H, BASE, LN, { ceu: '#3B4570' });
  // móveis: sofá e abajur, para a sala ter cara de casa
  const sofa = kit.grupo('sofa', kit.mundo, [0.35, 0.2, 0.018]);
  const matSofa = kit.matToon('#6C8EF5');
  kit.objeto('sofa_assento', cxa(-0.3, 0.3, -0.16, 0.16, 0, 0.14), matSofa, { linha: LN, pai: sofa });
  kit.objeto('sofa_encosto', cxa(-0.3, 0.3, 0.1, 0.18, 0.14, 0.34), matSofa, { linha: LN, pai: sofa });
  for (const s of [-1, 1]) kit.objeto(`sofa_braco_${s}`, cxa(s * 0.3 - 0.04, s * 0.3 + 0.04, -0.16, 0.18, 0, 0.22), matSofa, { linha: LN, pai: sofa });
  kit.objeto('abajur_haste', tubo([[0.72, 0.4, 0.02], [0.72, 0.4, 0.5]], 0.01, 8, 'nenhum'), kit.matToon('#1B1530'), { linha: 0 });
  kit.objeto('abajur_cupula', esfera(0.09, [0.72, 0.4, 0.55], [16, 10]), kit.matToon('#FFE45E'), { linha: LN });

  // fio que desce da janela até a tomada, junto da parede da esquerda
  const fioPts = [[-0.1, P / 2 - 0.08, 1.05], [-0.74, P / 2 - 0.08, 1.05], [-0.74, P / 2 - 0.08, 0.16], [-0.74, -0.1, 0.16], [-0.53, -0.1, 0.16]];
  kit.objeto('fio', tubo(fioPts, 0.012, 8, 'nenhum'), kit.matToon('#2B2440'), { linha: 0.003 });
  const faisca = kit.objeto('faisca', esfera(0.07, [0, 0, 0], [16, 10]), kit.matChapado('#FFF27A'), { linha: 0.004 });

  // tempestade lá fora: nuvens escuras por cima da sala
  const nuvens = [
    C.nuvem(kit, 'nuvem_1', [-0.3, 0.5, 2.05], 0.32, { cor: '#8C93B5', cor2: '#4A5078', semente: 2 }),
    C.nuvem(kit, 'nuvem_2', [0.45, 0.4, 2.2], 0.26, { cor: '#9AA1C2', cor2: '#4A5078', semente: 5 }),
  ];

  const raio = B.mascote(kit, 'raio', [0.4, -0.15, 2.0], { forma: 'raio', cor: '#FFF27A', cor2: '#FFB23E', escala: 1.6 });
  const tomada = B.mascote(kit, 'tomada', [-0.45, -0.1, 0.018], { forma: 'caixa', cor: '#FFFFFF', cor2: '#D9E2F2', escala: 1.25 });

  kit.criarCamera([0.2, 0, 1.25], 3.6, 40, 10);
  kit.rotulo('FIAÇÃO', faisca, [0, 0, 0.06]);
  for (const o of [raio.raiz, raio.corpo, tomada.raiz, tomada.corpo, raio.bracoE, raio.bracoD, tomada.bracoE, tomada.bracoD]) o.rotation.order = 'ZYX';
  S = { T, camera, raio, tomada, faisca, fioPts, nuvens, fim: tp.fim };
  return { duracao };
}

function noFio(u) {
  const p = S.fioPts;
  const seg = [];
  let total = 0;
  for (let i = 0; i < p.length - 1; i++) {
    const d = Math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1], p[i + 1][2] - p[i][2]);
    seg.push(d);
    total += d;
  }
  let alvo = Math.max(0, Math.min(1, u)) * total;
  for (let i = 0; i < seg.length; i++) {
    if (alvo <= seg[i] || i === seg.length - 1) {
      const k = Math.min(1, alvo / seg[i]);
      return [0, 1, 2].map((j) => p[i][j] + (p[i + 1][j] - p[i][j]) * k);
    }
    alvo -= seg[i];
  }
  return p[p.length - 1];
}

export function quadro(t) {
  const { T, raio, tomada } = S;
  const [ax, az, dist, pitch] = S.camera(t);
  kit.mirar([ax, 0, az], dist, pitch);
  S.nuvens.forEach((n, i) => { n.position.x = 0.04 * Math.sin(0.8 * t + i); });

  // o raio balança na nuvem, cai em "entrar" e pousa no chão em "casa", com um quique
  const cai = suave(T.entrar, T.casa, t);
  const z = 2.0 - 1.98 * cai * cai + 0.1 * pulo(t, T.casa, 0.35);
  raio.raiz.position.set(0.4 - 0.25 * cai, -0.15, z + 0.03 * Math.sin(5 * t) * (1 - cai));
  raio.corpo.rotation.set(0, rad(12 * Math.sin(3 * t) * (1 - cai)), rad(-15 * cai));
  raio.bracoE.rotation.set(0, rad(-40 * volta((t - T.raio) / 0.5) - 30 * pulo(t, T.consegue2, 0.4)), 0);
  raio.bracoD.rotation.set(0, rad(40 * volta((t - T.raio) / 0.5) + 60 * pulo(t, T.consegue2, 0.4)), 0);
  raio.boca.scale.set(1, 1, 1 + 1.5 * pulo(t, T.consegue2, 0.3));

  // a tomada leva um susto quando o raio chega ("casa") e treme quando a faísca chega pelo fio
  const susto = pulo(t, T.casa + 0.15, 0.4, 1);
  const chega = suave(T.fiacao + 0.5, T.fiacao + 0.7, t);
  tomada.raiz.position.set(-0.45, -0.1, 0.018 + 0.12 * susto);
  tomada.corpo.rotation.set(rad(3 * Math.sin(40 * t) * chega), 0, rad(6 * Math.sin(30 * t) * chega));
  tomada.bracoE.rotation.set(0, rad(70 * susto + 50 * chega), 0);
  tomada.bracoD.rotation.set(0, rad(-70 * susto - 50 * chega), 0);
  tomada.boca.scale.set(1, 1, 1 + 2.0 * Math.max(susto, chega));

  // faísca corre pelo fio em "fiação"
  const u = suave(T.fiacao - 0.1, T.fiacao + 0.6, t);
  S.faisca.visible = t > T.fiacao - 0.15;
  S.faisca.position.set(...noFio(u));
  S.faisca.scale.setScalar(0.8 + 0.3 * Math.sin(25 * t));
}

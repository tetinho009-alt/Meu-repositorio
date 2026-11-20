/*! © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C */
/**
 * Cena do exemplo "Isso não é uma água-viva" no navegador: a mesma do exemplo/cena.py do Blender (plano contínuo
 * dentro de uma fatia de oceano, animado pela narração), com as mesmas marcas de tempo e os mesmos rótulos.
 *
 * Contrato com o render.py: `montar(THREE, kit, dados)` monta tudo e devolve { duracao }; `quadro(t)` põe cada
 * coisa no lugar do instante t. quadro(t) não guarda estado entre chamadas: o mesmo t dá sempre o mesmo quadro.
 * dados = { tempos (tempos.json), episodio (episodio.json), fps, largura, altura }.
 */
import { PALETA, Tempos, blob, cadeia, planos, pulo, rad, suave, volta } from 'x3d/motor3d.js';
import * as C from 'x3d/cenario3d.js';
import * as B from 'x3d/bichos3d.js';

const [L, P, H, BASE] = [1.7, 1.2, 2.2, 0.55]; // largura, profundidade, altura da água e espessura da areia (m)
const LN = 0.0075; // espessura do contorno (m)

let kit, S;

function coracao(nome) {
  let els = [[[-0.03, 0, 0.02], 0.045], [[0.03, 0, 0.02], 0.045]];
  els.push(...cadeia([0, 0, -0.01], [0, 0, -0.07], 0.04, 0.012, 0.3));
  els = els.map(([p, r]) => [p, r, [1.0, 0.55, 1.0]]);
  return kit.objeto(nome, blob(els, 0.006), kit.matToon('#FF5C8A'), { linha: 0.004 });
}

export async function montar(THREE, motor, dados) {
  kit = motor;
  const tp = new Tempos(dados.tempos);
  const q = (p) => tp.quando(p);
  const T = {
    caravela: q('caravela'), condominio: q('condomínio'), boia: q('boia'), caca: q('caça'),
    come: q('come'), namora: q('namora'), sozinho: q('sozinho'), sobrevive: q('sobrevive'),
  };
  const falaFim = tp.fim;
  const duracao = falaFim + 0.4 + dados.episodio.cta_segundos;

  // Câmera: (marco, alvo_x, alvo_z, distância, pitch). O último plano repete o primeiro (o fim emenda no replay).
  const camera = planos([
    [0.0, 0.0, 1.7, 5.2, 11],
    [T.caravela, 0.0, 1.85, 3.3, 8],
    [T.condominio, 0.0, 2.1, 2.5, 7],
    [T.sozinho, 0.0, 1.85, 3.3, 8],
    [falaFim, 0.0, 1.7, 5.2, 11],
  ], 1.6);

  C.blocoOceano(kit, L, P, H, BASE, LN);
  C.feixe(kit, 'feixe_1', [-0.35, 0.25, H], 0.0, 0.16, 0.34, 0.12);
  C.feixe(kit, 'feixe_2', [0.35, 0.1, H], 0.4, 0.1, 0.22, 0.09);
  const algas = [
    C.alga(kit, 'alga_1', [-0.62, 0.38, 0.03], 1.2, 6, LN, 0.0),
    C.alga(kit, 'alga_2', [0.68, 0.45, 0.03], 0.8, 4, LN, 0.6),
  ];
  C.coral(kit, 'coral_1', [0.6, -0.3, 0.04], 0.52, PALETA.coral, PALETA.coral_ponta, LN);
  C.coral(kit, 'coral_2', [0.3, 0.38, 0.04], 0.4, PALETA.coral2, PALETA.coral2_ponta, LN);
  C.pedra(kit, 'pedra_1', [0.55, 0.18, 0.05], [0.2, 0.16, 0.16], PALETA.rocha, LN);
  C.estrela(kit, 'estrela_1', [-0.25, -0.42, 0.09], 0.08, LN, 0.4);
  C.anemona(kit, 'anemona_1', [-0.55, -0.2, 0.05], 0.1, LN);
  const ch = B.chinelo(kit, 'chinelo_1', [0.38, -P / 2 + 0.012, -BASE * 0.45], { linha: 0.004 }); // achado no corte
  ch.rotation.order = 'ZYX'; // mesma ordem do Euler XYZ do Blender
  ch.rotation.set(rad(90), rad(-18), 0);
  ch.scale.setScalar(0.9);

  const cv = B.caravela(kit, 'caravela_1', [0.0, -0.05, H - 0.03], 1.35);
  const peixe = await C.peixe(kit, 'palhaco_1', 'palhaco', 0.3, [0.62, -0.25, 1.35], 180, { linha: 0.005 });
  const baiacu = await C.peixe(kit, 'baiacu_1', 'baiacu', 0.24, [-0.5, 0.3, 0.9], 15, { linha: 0.004 });
  const cardume = [];
  for (let i = 0; i < 3; i++) {
    cardume.push(await C.peixe(kit, `cardume_${i}`, 'peixe', 0.11, [-0.55 + 0.08 * i, 0.4, 1.45 + 0.07 * (i % 2)], 10,
      { linha: 0.003, brilho: false }));
  }
  const cor = coracao('coracao_1');

  // Tudo gira junto em torno do Z (o "mundo" do cena.py); a câmera fica de fora.
  const mundo = kit.grupo('mundo');
  for (const o of [...kit.mundo.children]) if (o !== mundo) mundo.add(o);
  kit.criarCamera([0.0, 0.0, 1.7], 5.2, 40, 11);

  // âncoras dos rótulos (ponto no espaço local de cada parte), iguais às do cena.py
  kit.rotulo('BOIA', cv.boia, [0.0, 0.0, 0.2]);
  kit.rotulo('CAÇADORES', cv.cacadores, [0.0, 0.0, -0.7]);
  kit.rotulo('DIGESTÃO', cv.digestao, [0.0, 0.0, -0.12]);
  kit.rotulo('FILHOTES', cv.filhotes, [-0.15, 0.0, -0.1]);

  for (const o of [cv.raiz, cv.boia, cv.digestao, cv.filhotes, ...algas]) o.rotation.order = 'ZYX';
  S = {
    T, camera, mundo, algas, cv, peixe, baiacu, cardume, cor,
    sup: mundo.getObjectByName('superficie'),
    p0: peixe.position.clone(), rz0: peixe.rotation.z,
    b0: baiacu.position.clone(), card0: cardume.map((o) => o.position.clone()),
  };
  return { duracao };
}

export function quadro(t) {
  const { T, cv } = S;
  const [ax, az, dist, pitch] = S.camera(t);
  kit.mirar([ax, 0, az], dist, pitch);
  S.mundo.rotation.z = rad(-24 + 4 * Math.sin(t / 9));
  S.sup.position.z = 0.004 * Math.sin(2.1 * t);
  S.algas.forEach((a, i) => a.rotation.set(rad(3.5 * Math.sin(1.3 * t + i)), rad(4.5 * Math.sin(0.9 * t + 1.7 * i)), 0));

  // desmonta em "condomínio"; em "sozinho" a digestão se afasta e murcha; em "sobrevive" tudo encaixa de volta
  const junta = 1 - suave(T.sobrevive - 0.1, T.sobrevive + 0.35, t);
  const abre = volta((t - T.condominio) / 0.6) * junta;
  const sozinho = suave(T.sozinho, T.sozinho + 0.5, t) * junta;
  const boiaZ = H - 0.03 + 0.02 * Math.sin(1.6 * t);
  cv.raiz.position.set(0.0, -0.05, boiaZ);
  cv.raiz.rotation.set(0, rad(2 * Math.sin(1.1 * t)), 0);
  const ritmo = Object.fromEntries(['boia', 'caca', 'come', 'namora'].map((k) => [k, pulo(t, T[k])]));
  cv.boia.position.set(0, 0, 0.16 * abre + 0.06 * ritmo.boia);
  cv.boia.rotation.set(0, 0, rad(8 * abre));
  cv.cacadores.position.set(0, 0, -0.08 * abre - 0.04 * ritmo.caca);
  cv.cacadores.scale.set(1, 1, 0.6);
  cv.digestao.position.set(0.34 * abre + 0.08 * sozinho, 0, -0.04 * abre + 0.05 * ritmo.come - 0.05 * sozinho);
  cv.digestao.rotation.set(0, rad(-20 * sozinho), rad(25 * abre));
  cv.digestao.scale.setScalar(1 - 0.25 * sozinho);
  cv.filhotes.position.set(-0.36 * abre, 0, -0.04 * abre + 0.05 * ritmo.namora);
  cv.filhotes.rotation.set(0, 0, rad(-25 * abre));
  cv.crista.scale.set(1, 1, 1 + 0.25 * ritmo.boia);

  // coração no "namora"
  const u = (t - T.namora) / 1.2;
  S.cor.visible = u > 0 && u < 1;
  S.cor.position.set(-0.5, -0.12, boiaZ - 0.05 + 0.3 * u);
  S.cor.scale.setScalar(Math.max(0.001, 1.6 * volta(u * 3)));

  // micro-gag: o peixe-palhaço chega perto dos tentáculos e, no "caça", dá meia-volta e foge
  const ida = suave(T.condominio, T.caca, t);
  const ondula = 0.02 * Math.sin(2 * t);
  let dx, giro;
  if (t < T.caca) {
    dx = -0.38 * ida;
    giro = 0;
  } else {
    dx = -0.38 + 0.9 * suave(T.caca + 0.15, T.caca + 1.4, t);
    giro = Math.PI * suave(T.caca, T.caca + 0.25, t);
  }
  S.peixe.position.set(S.p0.x + dx, S.p0.y, S.p0.z + ondula);
  S.peixe.rotation.z = S.rz0 + giro;
  S.baiacu.position.set(S.b0.x + 0.12 * Math.sin(0.4 * t), S.b0.y, S.b0.z + 0.03 * Math.sin(1.3 * t));
  S.cardume.forEach((o, i) => {
    const c = S.card0[i];
    o.position.set(c.x + 0.25 * Math.sin(0.3 * t + i * 0.3), c.y, c.z + 0.02 * Math.sin(2 * t + i));
  });
}

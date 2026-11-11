// Zombies "vecinos" estilo South Park (recorte de papel), para pxl:
//   node <pxl>/bin/pxl.js build tools/zombies.px.js --out <carpeta>
// Adultos inventados del pueblo. Miran a la izquierda, pies en la fila 45 del frame final.
// Cada lienzo es 2 px más chico que el frame final: el contorno automático suma 1 px por lado.

pal({
  k: "#000000",                                   // contorno (igual que las plantas)
  z: "#8fae86", Z: "#66855f",                     // piel zombie y su sombra
  f: "#d98a74", F: "#b0654f",                     // piel colorada (enojado)
  w: "#ffffff", m: "#3a1a1a", t: "#f0ecd8",       // ojos, boca, dientes
  b: "#4f73b8", B: "#38558c",                     // suéter azul
  c: "#c9b27a", C: "#a08955",                     // pantalón caqui
  x: "#30364a", X: "#1f2333",                     // pantalón oscuro
  d: "#ece6d6", D: "#c3b9a2", e: "#9fd0ea", y: "#f2c94c",   // puerta, vidrio, picaporte
  g: "#9aa0a8", G: "#6f757e",                     // jogging gris
  o: "#ee8a2c", O: "#c0661a",                     // naranja
  r: "#d23a3a", R: "#9c2626",                     // rojo
  n: "#8a5a32", N: "#5e3b1e",                     // marrón / tierra
  h: "#f7d23b", H: "#c9a51c",                     // casco amarillo
  v: "#8a4fc0", V: "#663894",                     // violeta
  l: "#e86aa8", L: "#b8478a",                     // malla rosa
  q: "#3fb3b0", Q: "#2b8784",                     // turquesa
  a: "#e9e6da", A: "#9a9a9a",                     // diario
  i: "#b8bcc4", I: "#7d828c",                     // metal
  j: "#b07a40", J: "#7a5228",                     // madera
  s: "#f4f6fa", S: "#cfd6e0",                     // nieve / blanco sucio
  u: "#56634f",                                   // mancha en la ropa
})

// ---------------------------------------------------------------- poses (8 frames)
const CAMINAR = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => ({
  bob: [0, 1, 1, 0, 0, 1, 1, 0][i], paso: [-2, -1, 0, 1, 2, 1, 0, -1][i], brazo: [0, 0, 1, 1, 0, 0, 1, 1][i] }))
const CORRER = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => ({
  bob: [0, 1, 2, 1, 0, 1, 2, 1][i], paso: [-3, -2, 0, 2, 3, 2, 0, -2][i], brazo: [0, 1, 1, 0, 0, 1, 1, 0][i] }))
const ATACAR = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => ({
  bob: 0, paso: 0, brazo: [0, 1, 2, 2, 1, 0, 0, 0][i], adelante: [0, 1, 2, 3, 3, 2, 1, 0][i], boca: i >= 2 && i <= 5 }))

// Caja con borde negro (las partes del recorte de papel tienen su línea)
function caja(c, x, y, w, h, col) {
  c.rect(x, y, w, h, "k")
  if (w > 2 && h > 2) c.rect(x + 1, y + 1, w - 2, h - 2, col)
}

// ---------------------------------------------------------------- el vecino base
// Proporciones de South Park: cabeza enorme y redonda (más ancha que el cuerpo), cuerpo y piernas cortos.
// o: { piel, pielS, ropa, ropaS, pant, cx, pies, cab (radio x de la cabeza), alto (torso), ancho,
//      pierna, piernaAncho, brazosArriba, sinBrazos, brazoPiel (brazos al aire: musculosa) }
function vecino(c, o, p) {
  const piel = o.piel || "z", pielS = o.pielS || "Z"
  const cx = o.cx ?? 14, pies = o.pies ?? 44, rx = o.cab ?? 10, ry = rx - 1
  const torso = o.alto ?? 11, ancho = o.ancho ?? 12
  const bob = p.bob || 0, ad = p.adelante || 0
  // Piernas y zapatos (el paso las mueve en direcciones opuestas)
  const pierna = o.pierna ?? 7, pa = o.piernaAncho ?? 4
  const ly = pies - 1 - pierna
  for (const [dx, sg] of [[-Math.round(ancho * 0.33), 1], [Math.round(ancho * 0.1), -1]]) {
    const x = cx + dx + sg * (p.paso || 0)
    caja(c, x, ly, pa, pierna, o.pant || "x")
    c.rect(x - 2, pies - 2, pa + 2, 3, "k")
  }
  // Torso con una sombra de un tono a la derecha y la ropa rota abajo
  const by = ly - torso - bob, bx = cx - Math.floor(ancho / 2)
  caja(c, bx, by, ancho, torso + 1, o.ropa)
  c.rect(bx + ancho - 3, by + 1, 2, torso - 1, o.ropaS)
  c.px(bx + 3, by + torso, "_"); c.px(bx + 7, by + torso, "_")             // dobladillo roto
  c.rect(bx + 4, by + 5, 2, 2, "u")                                       // mancha
  const brazo = o.brazoPiel ? [piel, pielS] : [o.ropa, o.ropaS]
  // Brazo de atrás (detrás del cuerpo)
  const ay = by + 2 + (p.brazo || 0)
  if (!o.sinBrazos && !o.brazosArriba) {
    caja(c, bx - 6 - ad, ay - 1, 8, 4, brazo[1]); caja(c, bx - 9 - ad, ay - 1, 4, 4, pielS)
  }
  // Cabeza enorme y redonda, con la sombra de un tono abajo a la derecha
  const hx = cx - 1 - ad, hy = by - ry + 3
  c.ellipse(hx, hy, rx, ry, piel); c.ellipse(hx, hy, rx, ry, "k", true)
  c.rect(hx + rx - 3, hy - 2, 2, ry - 1, pielS); c.hline(hx - 2, hy + ry - 1, rx + 1, pielS)
  // Ojos: dos óvalos blancos grandes y pegados, desparejos (uno más chico, pupilas distintas)
  const ox = hx - Math.round(rx / 2), oy = hy - 1
  c.ellipse(ox, oy, 3, 3, "w"); c.ellipse(ox, oy, 3, 3, "k", true)
  c.ellipse(ox + 5, oy + 1, 2, 2, "w"); c.ellipse(ox + 5, oy + 1, 2, 2, "k", true)
  c.rect(ox - 2, oy, 2, 2, "k"); c.px(ox + 4, oy + 1, "k")
  c.hline(ox - 3, oy + 4, 4, pielS)                                        // ojera
  // Boca: cerrada (línea despareja) o abierta mordiendo
  const mx = ox - 3, my = hy + Math.round(ry / 2) + 1
  if (p.boca) {
    c.ellipse(mx + 3, my, 3, 2, "m"); c.px(mx + 2, my - 2, "t"); c.px(mx + 4, my - 2, "t")
  } else {
    c.hline(mx, my, 3, "k"); c.hline(mx + 3, my + 1, 2, "k"); c.px(mx + 5, my, "k")
  }
  // Brazo de adelante, estirado (zombie), o los dos arriba al costado de la cabeza
  let mano
  if (o.brazosArriba) {
    const izq = Math.max(0, hx - rx - 3), der = Math.min(c.w - 4, hx + rx)
    caja(c, izq, by - 6, 4, 9, brazo[0]); caja(c, izq, by - 9, 4, 4, piel)
    caja(c, der, by - 6, 4, 9, brazo[1]); caja(c, der, by - 9, 4, 4, pielS)
    mano = [izq + 1, by - 8]
  } else if (!o.sinBrazos) {
    caja(c, bx - 7 - ad, ay + 1, 9, 4, brazo[0]); caja(c, bx - 10 - ad, ay + 1, 4, 4, piel)
    mano = [bx - 9 - ad, ay + 2]
  }
  return { hx, hy, rx, ry, bx, by, ancho, torso, mano, cx, pies, ly, oy }
}

// Helper: una animación de 8 frames (o n) de un vecino con su ropa y sus accesorios
function zombie(nombre, poses, dibujar, tam = [30, 46], fps = 8) {
  anim(nombre, { w: tam[0], h: tam[1], frames: poses.length, fps, outline: "k" }, (c) => dibujar(c, poses[c.frame], c.frame))
}

// ---------------------------------------------------------------- peinados y gorros
function pelado(c, s) { c.hline(s.hx - 1, s.hy - s.ry, 5, "k"); c.px(s.hx + 2, s.hy - s.ry - 1, "k") }
function pelo(c, s, col) { c.ellipse(s.hx + 1, s.hy - s.ry + 1, s.rx - 1, 3, col); c.ellipse(s.hx + 1, s.hy - s.ry + 1, s.rx - 1, 3, "k", true) }
function gorra(c, s, col, visera = -1) {
  c.ellipse(s.hx, s.hy - s.ry + 1, s.rx - 1, 3, col); c.ellipse(s.hx, s.hy - s.ry + 1, s.rx - 1, 3, "k", true)
  c.rect(s.hx - s.rx, s.hy - s.ry + 3, s.rx * 2 + 1, 2, "k")
  if (visera < 0) caja(c, s.hx - s.rx - 4, s.hy - s.ry + 3, 6, 3, col)
}

// ---------------------------------------------------------------- 1. Puerta: papá de suéter que se cubre con la puerta de su casa
const PAPA = { ropa: "b", ropaS: "B", pant: "c" }
function puerta(c, p, i, conPuerta) {
  const s = vecino(c, PAPA, p)
  pelo(c, s, "N")
  if (!conPuerta) return
  const top = s.by - 2
  caja(c, 0, top, 11, 44 - top, "d")
  c.rect(8, top + 1, 2, 42 - top, "D")                                   // sombra de la puerta
  caja(c, 2, top + 3, 6, 7, "e")                                         // vidrio
  caja(c, 6, top + 17, 3, 3, "y")                                        // picaporte
}
zombie("puerta_caminar", CAMINAR, (c, p, i) => puerta(c, p, i, true))
zombie("puerta_atacar", ATACAR, (c, p, i) => puerta(c, p, i, true))
zombie("puerta_sin_caminar", CAMINAR, (c, p, i) => puerta(c, p, i, false))
zombie("puerta_sin_atacar", ATACAR, (c, p, i) => puerta(c, p, i, false))

// ---------------------------------------------------------------- 2. Pértiga: profe de gimnasia con jogging gris y silbato
const PROFE = { ropa: "g", ropaS: "G", pant: "G" }
function profe(c, p, i, conPertiga, opts = {}) {
  const s = vecino(c, { ...PROFE, ...opts }, p)
  gorra(c, s, "r")
  c.px(s.bx + 3, s.by + 2, "y"); c.px(s.bx + 3, s.by + 3, "y")             // silbato
  if (conPertiga && s.mano) c.line(0, s.mano[1] + 3, 29, s.mano[1] - 3, "j")
  return s
}
zombie("pertiga_caminar", CORRER, (c, p, i) => profe(c, p, i, true), [30, 46], 12)
zombie("pertiga_sin_caminar", CAMINAR, (c, p, i) => profe(c, p, i, false))
zombie("pertiga_sin_atacar", ATACAR, (c, p, i) => profe(c, p, i, false))
// Salto en 4 frames: clava la pértiga, sube, pasa por arriba, cae
anim("pertiga_salto", { w: 30, h: 46, frames: 4, fps: 5, loop: false, outline: "k" }, (c) => {
  const f = c.frame
  const pies = [44, 41, 39, 44][f], cx = [16, 15, 13, 10][f]
  const s = profe(c, CORRER[f * 2], f, false, { cx, pies, brazosArriba: f === 1 || f === 2 })
  if (f === 0) c.line(1, 44, 22, s.by - 3, "j")
  if (f === 1) c.line(6, 44, 9, 12, "j")
  if (f === 2) c.line(4, 44, 4, 16, "j")
})

// ---------------------------------------------------------------- 3. Escalera: electricista de mameluco con la escalera en la espalda
const ELECTRI = { ropa: "o", ropaS: "O", pant: "B" }
function electricista(c, p, i, conEscalera) {
  if (conEscalera) {                                                     // la escalera va detrás
    const b = p.bob || 0
    for (const x of [19, 26]) caja(c, x, 1 - b, 3, 42, "j")
    for (let y = 5 - b; y < 41 - b; y += 5) c.rect(21, y, 5, 2, "J")
  }
  const s = vecino(c, ELECTRI, p)
  c.rect(s.bx + 1, s.by + 1, 3, s.torso - 1, "B"); c.rect(s.bx + 8, s.by + 1, 2, s.torso - 1, "B")   // tiradores
  gorra(c, s, "b")
}
zombie("escalera_caminar", CAMINAR, (c, p, i) => electricista(c, p, i, true))
zombie("escalera_sin_caminar", CAMINAR, (c, p, i) => electricista(c, p, i, false))
zombie("escalera_sin_atacar", ATACAR, (c, p, i) => electricista(c, p, i, false))

// ---------------------------------------------------------------- 4. Tractor: barrendero municipal en su barredora de nieve (46x46 -> 48x48)
function barredora(c, p, i, atacando) {
  const vib = i % 2, sube = atacando ? [0, -2, -3, -2, 0, 1, 0, 0][i] : 0
  caja(c, 38, 9 - vib, 3, 12, "I")                                       // caño de escape
  if (i % 4 < 2) { c.ellipse(39, 5 - vib - (i % 4), 3, 2, "S") }
  // vecino en la cabina (solo la cabeza y los hombros)
  const s = vecino(c, { ropa: "o", ropaS: "O", cx: 30, pies: 36, cab: 7, alto: 8, ancho: 10, sinBrazos: true },
    { bob: vib, boca: atacando && p.boca, adelante: atacando ? Math.min(2, p.adelante || 0) : 0 })
  gorra(c, s, "b", 0); c.px(s.hx, s.hy - s.ry - 3, "s")
  caja(c, 12, 22 - vib, 33, 15, "o"); c.rect(13, 33 - vib, 31, 3, "O")   // carrocería
  caja(c, 15, 25 - vib, 9, 6, "e")                                       // ventana de la puerta
  caja(c, 9, 36, 37, 10, "X")                                            // orugas
  for (let k = 0; k < 4; k++) {
    const wx = 14 + k * 9
    c.circ(wx, 41, 3, "I"); c.ring(wx, 41, 3, "k")
    const a = (i + k) % 4
    c.px(wx + [1, 0, -1, 0][a], 41 + [0, 1, 0, -1][a], "k")
  }
  // pala con el borde amarillo, sube y baja al atacar
  c.poly([0, 22 + sube, 10, 26 + sube, 10, 44, 1, 45], "I")
  c.line(0, 22 + sube, 1, 45, "y")
  c.rect(10, 31, 3, 3, "k")
}
zombie("tractor_caminar", CAMINAR, (c, p, i) => barredora(c, p, i, false), [46, 46])
zombie("tractor_atacar", ATACAR, (c, p, i) => barredora(c, p, i, true), [46, 46])

// ---------------------------------------------------------------- 5. Bungee: doble de riesgo en mono turquesa, casco y arnés
const DOBLE = { ropa: "q", ropaS: "Q", pant: "Q" }
function doble(c, p, i, opts = {}) {
  const s = vecino(c, { ...DOBLE, ...opts }, p)
  c.line(s.bx + 1, s.by + 1, s.bx + s.ancho - 2, s.by + s.torso - 1, "k")   // arnés
  c.line(s.bx + s.ancho - 2, s.by + 1, s.bx + 1, s.by + s.torso - 1, "k")
  c.ellipse(s.hx, s.hy - s.ry + 1, s.rx - 1, 3, "r"); c.ellipse(s.hx, s.hy - s.ry + 1, s.rx - 1, 3, "k", true)   // casco
  c.rect(s.hx - 2, s.hy - s.ry, 4, 1, "w")
  return s
}
zombie("bungee_caminar", CAMINAR, (c, p, i) => doble(c, p, i))
zombie("bungee_atacar", ATACAR, (c, p, i) => doble(c, p, i))
// Cayendo: colgado de la soga, brazos arriba y piernas que patalean
anim("bungee_cayendo", { w: 30, h: 46, frames: 4, fps: 6, outline: "k" }, (c) => {
  const f = c.frame
  doble(c, { bob: [0, 1, 2, 1][f], paso: [-2, 0, 2, 0][f] }, f, { brazosArriba: true, pies: 44 - [0, 1, 2, 1][f] })
  c.vline(14, 0, 3, "k")                                                 // enganche de la soga
})

// ---------------------------------------------------------------- 6. Diario: oficinista de camisa y corbata leyendo el diario
const OFICINA = { ropa: "s", ropaS: "S", pant: "x" }
function oficinista(c, p, i, enojado) {
  const s = vecino(c, enojado ? { ...OFICINA, piel: "f", pielS: "F" } : OFICINA, p)
  c.rect(s.bx + 5, s.by + 1, 2, s.torso - 2, "r")                         // corbata
  pelado(c, s); c.hline(s.hx - 4, s.hy - s.ry + 1, 8, "N")               // peinado de costado
  const ex = s.hx - Math.round(s.rx / 2), ey = s.oy
  c.hline(ex - 3, ey + 6, 5, "N")                                        // bigote
  if (enojado) {
    c.line(ex - 3, ey - 5, ex, ey - 4, "k"); c.line(ex + 7, ey - 4, ex + 4, ey - 4, "k")   // cejas
    if (i % 2) { c.px(s.hx + 4, s.hy - s.ry - 3, "s"); c.px(s.hx - 2, s.hy - s.ry - 4, "s") }   // vapor
    return
  }
  const baja = p.boca ? 3 : 0
  const [mx, my] = s.mano
  caja(c, 0, my - 7 + baja, 14, 12, "a")
  for (let y = my - 4 + baja; y < my + 4 + baja; y += 2) c.hline(2, y, 10, "A")
  c.hline(2, my - 5 + baja, 10, "k")                                     // titular
}
zombie("diario_caminar", CAMINAR, (c, p, i) => oficinista(c, p, i, false))
zombie("diario_atacar", ATACAR, (c, p, i) => oficinista(c, p, i, false))
zombie("diario_enojado_caminar", CORRER, (c, p, i) => oficinista(c, p, i, true), [30, 46], 14)
zombie("diario_enojado_atacar", ATACAR, (c, p, i) => oficinista(c, p, i, true), [30, 46], 12)

// ---------------------------------------------------------------- 7. Bailarín: profe de aeróbic con malla rosa, vincha y calentadores
const AEROBIC = { ropa: "l", ropaS: "L", pant: "v" }
function aerobic(c, p, i, opts = {}) {
  const s = vecino(c, { ...AEROBIC, ...opts }, p)
  pelo(c, s, "y")
  c.rect(s.hx - s.rx + 1, s.hy - s.ry + 3, s.rx * 2 - 1, 2, "v")          // vincha
  for (const dx of [-4, 1]) c.rect(s.cx + dx + 1, s.ly + 4, 2, 4, "w")      // calentadores
  return s
}
zombie("bailarin_caminar", CAMINAR, (c, p, i) => aerobic(c, p, i))
zombie("bailarin_atacar", ATACAR, (c, p, i) => aerobic(c, p, i))
// Invocando refuerzos: baila con los brazos arriba y la tierra se mueve a los costados
anim("bailarin_invocar", { w: 30, h: 46, frames: 4, fps: 6, outline: "k" }, (c) => {
  const f = c.frame
  aerobic(c, { bob: [0, 2, 0, 2][f], paso: [-2, 0, 2, 0][f] }, f, { brazosArriba: f % 2 === 0 })
  for (const x of [1, 25]) {                                             // la tierra se abre y sale una mano
    caja(c, x - 1, 41, 6, 4, "n")
    if (f % 2) { caja(c, x, 36, 4, 5, "z"); c.px(x + 1, 36, "k") }
  }
})

// ---------------------------------------------------------------- 8. Excavador: minero con casco y linterna, pico al hombro
const MINERO = { ropa: "n", ropaS: "N", pant: "x" }
function minero(c, p, i, conPico) {
  if (conPico) {                                                         // pico al hombro, detrás de la cabeza
    const by = 25 - (p.bob || 0), bx = 8 - (p.adelante || 0)
    c.line(bx + 10, by + 8, bx + 18, by - 12, "J")
    c.line(bx + 12, by - 14, bx + 24, by - 12, "i", 2)
    c.px(bx + 11, by - 13, "i"); c.px(bx + 25, by - 11, "i")
  }
  const s = vecino(c, MINERO, p)
  c.hline(s.bx + 1, s.by + 5, s.ancho - 2, "y")                          // banda reflectiva
  c.ellipse(s.hx, s.hy - s.ry + 1, s.rx - 1, 3, "h"); c.ellipse(s.hx, s.hy - s.ry + 1, s.rx - 1, 3, "k", true)
  c.rect(s.hx - s.rx, s.hy - s.ry + 3, s.rx * 2 + 1, 2, "k")
  caja(c, s.hx - s.rx + 1, s.hy - s.ry - 1, 3, 3, "w")                    // linterna
}
zombie("excavador_caminar", CAMINAR, (c, p, i) => minero(c, p, i, true))
zombie("excavador_atacar", ATACAR, (c, p, i) => minero(c, p, i, true))
zombie("excavador_sin_caminar", CAMINAR, (c, p, i) => minero(c, p, i, false))
zombie("excavador_sin_atacar", ATACAR, (c, p, i) => minero(c, p, i, false))
// Bajo tierra: un montículo que avanza, con la punta del casco asomando
anim("excavador_tierra", { w: 30, h: 46, frames: 4, fps: 8, outline: "k" }, (c) => {
  const f = c.frame
  c.ellipse(15, 41, 13, 4, "n"); c.ellipse(15, 41, 13, 4, "N", true)
  c.ellipse(14 + (f % 2), 37, 4, 2, "h")                                  // casco
  for (let k = 0; k < 3; k++) caja(c, 4 + ((k * 9 + f * 3) % 20), 38 + ((k + f) % 3), 3, 2, "N")   // terrones
})

// ---------------------------------------------------------------- 9. Gigante: patovica de musculosa con un cartel de PARE (46x62 -> 48x64)
const PATOVICA = { ropa: "S", ropaS: "D", pant: "N", cx: 24, pies: 60, cab: 12, alto: 20, ancho: 24, pierna: 11, piernaAncho: 7, brazoPiel: true }
function gigante(c, p, i, conMini, golpe) {
  if (conMini) {                                                         // el mini asoma por el hombro
    c.ellipse(38, 16, 5, 4, "z"); c.ellipse(38, 16, 5, 4, "k", true)
    c.ellipse(38, 13, 5, 2, "G")
    c.ellipse(36, 16, 1, 2, "w"); c.px(36, 16, "k")
    caja(c, 42, 20, 4, 4, "z")
  }
  const s = vecino(c, PATOVICA, p)
  pelado(c, s)
  c.rect(s.bx + 3, s.by, 2, 4, "z"); c.rect(s.bx + s.ancho - 6, s.by, 2, 4, "z")   // breteles de la musculosa
  c.rect(s.bx + 8, s.by + 9, 5, 4, "u")                                   // mancha
  const [mx, my] = s.mano
  let tip
  if (golpe) {                                                           // 0-3 lo levanta, 4-5 golpea, 6-7 vuelve
    const fase = [0, 1, 2, 3, 4, 4, 2, 1][i]
    tip = fase <= 3 ? [Math.max(6, mx - 1 + fase), Math.max(6, my - 10 - fase * 4)] : [6, 54]
  } else {
    tip = [Math.max(6, mx + 2), Math.max(6, my - 20 + (p.bob || 0))]
  }
  c.line(mx + 1, my + 1, tip[0], tip[1], "I", 2)
  c.circ(tip[0], tip[1], 5, "r"); c.ring(tip[0], tip[1], 5, "k")
  c.hline(tip[0] - 3, tip[1], 7, "w")
}
const GOLPE = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => ({ bob: 0, paso: 0, brazo: [0, -1, -2, -3, 2, 3, 1, 0][i], boca: i >= 3 && i <= 5 }))
zombie("gigante_caminar", CAMINAR, (c, p, i) => gigante(c, p, i, true, false), [46, 62], 6)
zombie("gigante_atacar", GOLPE, (c, p, i) => gigante(c, p, i, true, true), [46, 62])
zombie("gigante_sin_caminar", CAMINAR, (c, p, i) => gigante(c, p, i, false, false), [46, 62], 6)
zombie("gigante_sin_atacar", GOLPE, (c, p, i) => gigante(c, p, i, false, true), [46, 62])

// ---------------------------------------------------------------- 10. Mini: nene zombie de campera naranja y gorro verde (22x30 -> 24x32)
const NENE = { ropa: "o", ropaS: "O", pant: "B", cx: 11, pies: 28, cab: 8, alto: 5, ancho: 9, pierna: 4, piernaAncho: 3 }
function nene(c, p) {
  const s = vecino(c, NENE, { ...p, adelante: Math.min(2, p.adelante || 0) })
  c.ellipse(s.hx, s.hy - s.ry + 1, s.rx - 1, 2, "G"); c.ellipse(s.hx, s.hy - s.ry + 1, s.rx - 1, 2, "k", true)
  caja(c, s.hx - 1, s.hy - s.ry - 3, 3, 3, "s")                          // pompón
}
zombie("mini_caminar", CAMINAR, (c, p) => nene(c, p), [22, 30], 10)
zombie("mini_atacar", ATACAR, (c, p) => nene(c, p), [22, 30], 12)

// ---------------------------------------------------------------- vista previa animada (solo para revisar)
// Todas las tiras a 8 fps en una grilla, con el nombre abajo. Las de 4 frames se repiten dos veces.
const PREVIA = ["puerta_caminar", "puerta_atacar", "puerta_sin_caminar", "puerta_sin_atacar",
  "pertiga_caminar", "pertiga_salto", "pertiga_sin_caminar", "pertiga_sin_atacar",
  "escalera_caminar", "escalera_sin_caminar", "escalera_sin_atacar",
  "tractor_caminar", "tractor_atacar", "bungee_cayendo", "bungee_caminar", "bungee_atacar",
  "diario_caminar", "diario_atacar", "diario_enojado_caminar", "diario_enojado_atacar",
  "bailarin_caminar", "bailarin_atacar", "bailarin_invocar",
  "excavador_tierra", "excavador_caminar", "excavador_atacar", "excavador_sin_caminar", "excavador_sin_atacar",
  "gigante_caminar", "gigante_atacar", "gigante_sin_caminar", "gigante_sin_atacar", "mini_caminar", "mini_atacar"]
const DE_CUATRO = ["pertiga_salto", "bungee_cayendo", "bailarin_invocar", "excavador_tierra"]
const COLS = 6, CW = 64, CH = 82
anim("preview_animado", { w: COLS * CW, h: Math.ceil(PREVIA.length / COLS) * CH, frames: 8, fps: 8 }, (c) => {
  c.rect(0, 0, c.w, c.h, "S")
  PREVIA.forEach((n, k) => {
    const x = (k % COLS) * CW, y = Math.floor(k / COLS) * CH
    if ((k + Math.floor(k / COLS)) % 2) c.rect(x, y, CW, CH, "s")
    const ancho = n.startsWith("tractor") || n.startsWith("gigante") ? 48 : n.startsWith("mini") ? 24 : 32
    const alto = n.startsWith("gigante") ? 64 : n.startsWith("mini") ? 32 : 48
    c.stamp(n, x + Math.floor((CW - ancho) / 2), y + 66 - alto, { frame: c.frame % (DE_CUATRO.includes(n) ? 4 : 8) })
    const [a, ...resto] = n.toUpperCase().split("_")
    c.text(x + CW / 2, y + 69, a + "\n" + resto.join(" "), "k", { align: "c" })
  })
})

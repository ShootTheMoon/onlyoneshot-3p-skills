import fs from 'node:fs';
let s = fs.readFileSync('SkillPreviewConfig.lua', 'utf8').replace(/\r\n/g, '\n');
// clip 키 -> 임포트된 ANIMATION 에셋 id (2026-09-16 임포트분)
const ids = {
  Wakizashi_Idle: 45904500, Wakizashi_Attack1: 45903300, Wakizashi_Attack2: 45901400,
  Wakizashi_Attack3: 45901500, Wakizashi_BlockIn: 45903700, Wakizashi_BlockHold: 45903500,
  Wakizashi_BlockOut: 45904200, Wakizashi_KunaiThrow: 45904600, Wakizashi_Teleport: 45906300,
  Wakizashi_Draw: 45903900, Wakizashi_Ryunochi: 45905200,
  Gukgung_HorizontalAttack: 45902100, Gukgung_DrawRelease: 45901100,
};
const oldFn = 'local function clip(seconds)\n\treturn { id = "", weaponId = "", seconds = seconds }\nend';
const newFn = 'local function clip(seconds, id)\n\treturn { id = id and ("ovdrassetid://" .. id) or "", weaponId = "", seconds = seconds }\nend';
if (!s.includes(oldFn)) throw new Error('clip() anchor missing');
s = s.replace(oldFn, newFn);
let n = 0;
for (const [k, v] of Object.entries(ids)) {
  const head = k + ' = clip(';
  const i = s.indexOf(head);
  if (i < 0) throw new Error('no anchor ' + k);
  const close = s.indexOf(')', i + head.length);
  const secs = s.slice(i + head.length, close);
  if (!/^[0-9.]+$/.test(secs)) throw new Error('bad seconds for ' + k + ': ' + secs);
  s = s.slice(0, close) + ', ' + v + s.slice(close);
  n++;
}
fs.writeFileSync('SkillPreviewConfig.lua', s);
console.log('filled', n);

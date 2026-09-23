import fs from 'node:fs';
const r=JSON.parse(fs.readFileSync('GameIntegration/live-lobby.json','utf8'));const s=JSON.parse(r.content[0].text).source;
console.log({newlines:s.split('\n').length,escaped:s.includes('\\r\\n'),head:s.slice(0,90)});

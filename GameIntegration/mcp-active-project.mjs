import fs from 'node:fs';
import path from 'node:path';
import {syncBuiltinESMExports} from 'node:module';
// Scope project discovery to the active map named by Studio metadata; exclude backup maps.
const project='C:/Users/29/Desktop/onlyonetap';
const original=fs.readdirSync;
fs.readdirSync=function(dir,...args){
 const entries=original.call(this,dir,...args);
 if(path.resolve(String(dir)).toLowerCase()===path.resolve(project).toLowerCase() && entries.every(e=>typeof e==='string'))
  return entries.filter(e=>!e.toLowerCase().endsWith('.ovdrjm')||e==='onlyoneshot.ovdrjm');
 return entries;
};
syncBuiltinESMExports();
process.env.OVERDARE_PROJECT_DIR=project;
await import('file:///C:/Users/29/Desktop/overdare-mcp/dist/index.js');

import fs from 'node:fs';
import {Client} from 'file:///C:/Users/29/Desktop/overdare-mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import {StdioClientTransport} from 'file:///C:/Users/29/Desktop/overdare-mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js';
const client=new Client({name:'animation-integration',version:'1.0.0'});
try {
 await client.connect(new StdioClientTransport({command:process.execPath,args:['C:/Users/29/Desktop/3y/GameIntegration/mcp-active-project.mjs']}));
 const request=JSON.parse(fs.readFileSync(process.argv[2],'utf8').replace(/^\uFEFF/,''));
 for(const call of (Array.isArray(request)?request:[request])) {
  const result=call.name==='listTools'?await client.listTools():await client.callTool(call,undefined,{timeout:120000});
  if(result.isError)throw new Error(JSON.stringify(result));
  if(call.output)fs.writeFileSync(call.output,JSON.stringify(result,null,2));
  console.log(JSON.stringify({name:call.name,result:call.output?{saved:call.output}:result}));
 }
} finally {await client.close();}



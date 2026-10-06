'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// ---- 最小 .env 加载（仅当进程没有该变量时）----
function loadEnv() {
  const p = path.join(__dirname, '.env');
  if (!fs.existsSync(p)) return;
  const txt = fs.readFileSync(p, 'utf8');
  for (const line of txt.split('\n')) {
    const m = line.match(/^\s*([\w.-]+)\s*=\s*(.*)\s*$/);
    if (m && !process.env[m[1]]) {
      process.env[m[1]] = m[2].replace(/^["']|["']$/g, '');
    }
  }
}
loadEnv();

const PORT = process.env.PORT || 3000;
const KEY = process.env.FLYAI_API_KEY || '';

function flyaiBin() {
  const base = path.join(
    __dirname, 'node_modules', '.bin',
    process.platform === 'win32' ? 'flyai.cmd' : 'flyai'
  );
  return fs.existsSync(base) ? base : 'flyai';
}

// 调用 flyai-cli，返回 { ok, obj }
function runFlyai(args, timeoutMs = 25000) {
  return new Promise((resolve) => {
    const bin = flyaiBin();
    const useShell = process.platform === 'win32' && bin.endsWith('.cmd');
    let stdout = '', stderr = '', done = false, child;
    try {
      child = spawn(bin, args, {
        env: { ...process.env, FLYAI_API_KEY: KEY || process.env.FLYAI_API_KEY || '' },
        windowsHide: true,
        shell: useShell,
      });
    } catch (err) {
      return resolve({ ok: false, message: 'spawn 失败: ' + err.message });
    }
    const timer = setTimeout(() => {
      if (!done) { done = true; try { child.kill('SIGKILL'); } catch (e) {} resolve({ ok: false, message: '调用超时' }); }
    }, timeoutMs);
    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });
    child.on('error', (err) => {
      if (done) return; done = true; clearTimeout(timer);
      resolve({ ok: false, message: 'spawn 失败: ' + err.message });
    });
    child.on('close', () => {
      if (done) return; done = true; clearTimeout(timer);
      const raw = stdout.trim();
      if (!raw) return resolve({ ok: false, message: (stderr || '空输出').slice(0, 200) });
      const s = raw.indexOf('{'), e = raw.lastIndexOf('}');
      if (s < 0 || e < 0) return resolve({ ok: false, message: '非 JSON 输出: ' + raw.slice(0, 200) });
      try {
        const obj = JSON.parse(raw.slice(s, e + 1));
        resolve({ ok: obj.status === 0, obj });
      } catch (err) {
        resolve({ ok: false, message: 'JSON 解析失败: ' + err.message });
      }
    });
  });
}

function itemsOf(r) { return (r && r.obj && r.obj.data && r.obj.data.itemList) || []; }

function buildScript(city, days, pois, hotels) {
  const top = pois.slice(0, 2).map((p) => p.name).join('、');
  const stay = hotels.slice(0, 3).map((h) => h.name).join('、');
  return {
    hook: `${city}到底怎么玩才不踩坑？收藏这条，${days}天帮你安排得明明白白。`,
    day1: `主打开${top || city + '核心景点'}——实拍打卡 + 飞猪购票链接放评论区，边玩边省。`,
    stay: stay ? `住哪儿：${stay} 都是飞猪高分推荐，链接同款放评论区。` : `住哪儿：飞猪高分酒店推荐，链接放评论区。`,
    cta: `数据来自飞猪实时库存，价格随时变，点我主页看更多${city}玩法。`,
  };
}

function renderResult(city, days, category, poiRes, hotelRes) {
  const pois = itemsOf(poiRes);
  const hotels = itemsOf(hotelRes);
  return {
    city, days, category,
    poiCount: pois.length,
    hotelCount: hotels.length,
    poiReal: poiRes.ok,
    hotelReal: hotelRes.ok,
    pois: pois.slice(0, 6).map((p) => ({ name: p.name, address: p.address, jumpUrl: p.jumpUrl, mainPic: p.mainPic })),
    hotels: hotels.slice(0, 8).map((h) => ({ name: h.name, price: h.price, detailUrl: h.detailUrl, mainPic: h.mainPic, star: h.star })),
    script: buildScript(city, days, pois, hotels),
  };
}

const server = http.createServer(async (req, res) => {
  if (req.method === 'GET' && (req.url === '/' || req.url === '/index.html')) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    fs.createReadStream(path.join(__dirname, 'public', 'index.html')).pipe(res);
    return;
  }
  if (req.method === 'POST' && req.url === '/api/generate') {
    let body = '';
    req.on('data', (c) => { body += c; });
    req.on('end', async () => {
      let city = '', days = 2, category = '';
      try {
        const o = JSON.parse(body);
        city = (o.city || '').trim();
        days = Math.min(7, Math.max(1, parseInt(o.days, 10) || 2));
        category = (o.category || '').trim();
      } catch (e) {}
      if (!city || !/^[一-龥A-Za-z0-9\s]{1,20}$/.test(city)) {
        res.writeHead(400, { 'Content-Type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify({ error: '请输入有效的城市名（1-20 字）' }));
      }
      const poiArgs = ['search-poi', '--city-name', city];
      if (category) poiArgs.push('--category', category);
      const [poiRes, hotelRes] = await Promise.all([
        runFlyai(poiArgs),
        runFlyai(['search-hotel', '--dest-name', city]),
      ]);
      const result = renderResult(city, days, category, poiRes, hotelRes);
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify(result));
    });
    return;
  }
  res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end('Not found');
});

server.listen(PORT, '0.0.0.0', () => {
  console.log('游纪 demo listening on ' + PORT + (KEY ? ' (key loaded)' : ' (trial mode)'));
});

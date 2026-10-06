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
  // 每天前 2 个景点进脚本，其余补充
  const daily = [];
  for (let d = 1; d <= days; d++) {
    const dayPois = pois.filter((_, i) => i % days === (d - 1));
    const scriptSpots = dayPois.slice(0, 2);
    daily.push({
      day: d,
      morning: scriptSpots[0] || null,
      afternoon: scriptSpots[1] || null,
      transition: d < days
        ? `“第 ${d} 天先这样，第 ${d + 1} 天我带你们去 ${city} 另一个更值得拍的点。”`
        : '',
    });
  }

  const scriptHotels = hotels.slice(0, 2);
  const stayNames = scriptHotels.map((h) => h.name).join('、');
  const stay = stayNames
    ? `“住宿我推荐 ${stayNames}，都是飞猪高分且离上面这些点比较方便的酒店。价格会随日期浮动，评论区放了同款链接，订之前可以比价。”`
    : `“住宿建议选在市中心或景区沿线，飞猪上按评分排序挑高分酒店，同款链接放评论区。”`;

  return {
    hook: `“来 ${city} 玩了 ${days} 天，发现 90% 的人都去错了地方。这条视频帮你把 ${city} 最好拍、最不踩坑的点一次说清，收藏了直接照着走。”`,
    days: daily,
    stay,
    cta: `“好了，这份 ${city} ${days} 天攻略里的景点、酒店、路线全来自飞猪实时数据。评论区有购票和酒店同款链接，出发前再确认一次价格。点我主页，还有更多城市的 AI 旅行脚本。”`,
  };
}

function renderResult(city, days, category, poiRes, hotelRes) {
  const pois = itemsOf(poiRes);
  const hotels = itemsOf(hotelRes);

  // 按天拆分脚本景点与补充景点
  const scriptPois = [];
  const extraPois = [];
  for (let d = 1; d <= days; d++) {
    const dayPois = pois.filter((_, i) => i % days === (d - 1));
    scriptPois.push(...dayPois.slice(0, 2));
    extraPois.push(...dayPois.slice(2));
  }

  const scriptHotels = hotels.slice(0, 2);
  const extraHotels = hotels.slice(2, 8);

  return {
    city, days, category,
    poiCount: pois.length,
    hotelCount: hotels.length,
    poiReal: poiRes.ok,
    hotelReal: hotelRes.ok,
    scriptPois: scriptPois.slice(0, 14).map((p) => ({ name: p.name, address: p.address, jumpUrl: p.jumpUrl, mainPic: p.mainPic })),
    scriptHotels: scriptHotels.map((h) => ({ name: h.name, price: h.price, detailUrl: h.detailUrl, mainPic: h.mainPic, star: h.star })),
    extraPois: extraPois.slice(0, 12).map((p) => ({ name: p.name, address: p.address, jumpUrl: p.jumpUrl, mainPic: p.mainPic })),
    extraHotels: extraHotels.map((h) => ({ name: h.name, price: h.price, detailUrl: h.detailUrl, mainPic: h.mainPic, star: h.star })),
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

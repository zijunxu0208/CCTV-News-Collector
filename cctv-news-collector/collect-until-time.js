// CCTV 时讯24小时 滚动加载采集脚本
// 用法：在 https://ysxw.cctv.cn/24hours.html 页面刷新后，打开浏览器控制台(F12)，
//       粘贴本脚本并回车执行。脚本会自动点击“加载更多”，直到达到目标回溯小时数，
//       然后将当前窗口内所有时讯标题、时间、链接导出为 JSON 文件。
// 注意：本脚本仅用于浏览器控制台，不依赖 Playwright 或其他自动化框架。
(function () {
  const TARGET_HOURS = 36; // 默认回溯小时数，可按需修改

  const parseTime = (s) => {
    const m = s.match(/(\d+)月(\d+)日\s+(\d+):(\d+)/);
    return m ? new Date(2026, +m[1] - 1, +m[2], +m[3], +m[4]) : null;
  };

  const wait = (ms) => new Promise((r) => setTimeout(r, ms));

  const anchorEl = document.querySelector('a.__card-container .time');
  const anchorText = anchorEl ? anchorEl.textContent.trim() : '';
  const anchorDate = parseTime(anchorText);

  if (!anchorDate) {
    console.error('未找到锚点时间，请确认页面已加载');
    return { ok: false, error: '未找到锚点时间' };
  }

  const cutoff = new Date(anchorDate.getTime() - TARGET_HOURS * 60 * 60 * 1000);
  const loadMoreSelector = '.sc-kOHTFB.joraUR';

  async function loadUntilCutoff() {
    let rounds = 0;
    while (rounds < 100) {
      const items = document.querySelectorAll('a.__card-container');
      const lastTime = items[items.length - 1].querySelector('.time')?.textContent.trim();
      const lastDate = parseTime(lastTime);
      if (lastDate && lastDate <= cutoff) break;

      const btn = document.querySelector(loadMoreSelector);
      if (!btn) {
        console.log('已无加载更多按钮');
        break;
      }
      btn.click();
      await wait(3000);
      rounds++;
    }
    return document.querySelectorAll('a.__card-container');
  }

  function extract(items) {
    return Array.from(items).map((el) => {
      const titleEl = el.querySelector('.title');
      const timeEl = el.querySelector('.time');
      return {
        title: titleEl ? titleEl.textContent.trim() : '',
        time: timeEl ? timeEl.textContent.trim() : '',
        href: el.href,
      };
    });
  }

  function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  loadUntilCutoff().then((items) => {
    const data = extract(items);
    const safeAnchor = anchorText.replace(/[日:\s]/g, '_');
    downloadJSON(data, `cctv_24h_${safeAnchor}.json`);
    console.log('完成，共提取', data.length, '条');
  });

  return {
    started: true,
    anchor: anchorText,
    cutoff: cutoff.toLocaleString('zh-CN'),
  };
})();

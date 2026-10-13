const $ = (selector) => document.querySelector(selector);
const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');
const players = [];
let paused = motionPreference.matches;
let following = false;
let mainPet;
let installPet;
let installation;
let map;
let atlas;

function createPlayer(canvas, initialState, active = () => true) {
  const context = canvas.getContext('2d');
  const player = { canvas, state: initialState, frame: 0, elapsed: 0, returnTo: null, direction: null, active };
  player.draw = () => {
    const row = player.direction === null ? map.states.find((item) => item.state === player.state).row : 9 + Math.floor(player.direction / 8);
    const column = player.direction === null ? player.frame : player.direction % 8;
    context.clearRect(0, 0, 192, 208);
    context.imageSmoothingEnabled = false;
    context.drawImage(atlas, column * 192, row * 208, 192, 208, 0, 0, 192, 208);
    canvas.dataset.state = player.direction === null ? player.state : 'gaze';
    canvas.dataset.frame = String(column);
    canvas.dataset.row = String(row);
  };
  player.play = (state, returnTo = null) => {
    Object.assign(player, { state, frame: 0, elapsed: 0, direction: null, returnTo });
    player.draw();
  };
  player.look = (direction) => {
    player.direction = direction;
    player.returnTo = null;
    player.draw();
  };
  players.push(player);
  player.draw();
  return player;
}

function updatePause() {
  $('#pause').setAttribute('aria-pressed', String(paused));
  $('#pause span').textContent = paused ? '播放' : '暂停';
  $('#pause use').setAttribute('href', paused ? '#i-play' : '#i-pause');
  $('#motion-note').textContent = paused ? '已暂停；仍可手动选动作和方向。' : '面无表情，瓜事很多。';
}

function chooseAction(state) {
  following = false;
  $('#follow').setAttribute('aria-pressed', 'false');
  $('#direction').value = '';
  document.querySelectorAll('[data-state]').forEach((button) => {
    if (button.tagName === 'BUTTON') button.setAttribute('aria-pressed', String(button.dataset.state === state));
  });
  mainPet.play(state);
  const action = map.states.find((item) => item.state === state);
  $('#action-status span').textContent = action.caption ? `${action.title} · ${action.caption}` : action.title;
  $('#pet').setAttribute('aria-label', `小睦：${action.title}`);
  $('#stage-hint span').textContent = '选一个动作，或开启注视模式和她对视。';
}

function chooseDirection(direction) {
  document.querySelectorAll('.actiongrid button').forEach((button) => button.setAttribute('aria-pressed', 'false'));
  mainPet.look(direction);
  $('#direction').value = String(direction);
  const label = $('#direction').selectedOptions[0].textContent;
  $('#action-status span').textContent = `${following ? '跟着你看' : '十六向注视'} · ${label}`;
  $('#pet').setAttribute('aria-label', `小睦看向${label}`);
  $('#stage-hint span').textContent = following ? '移动指针和她对视；暂停后眼神会停住。' : '选择方向；聚焦小睦后可用左右方向键切换。';
}

function installationPrompt() {
  const activation = $('#activate').checked
    ? '安装后，按目标应用支持的方法启用小睦。如无法原生启用，请如实说明，不要臆造设置。'
    : '只安装文件，保留当前已启用的宠物；不要自动切换。';
  return `请帮我安装「${installation.name}」${installation.version}。

下载：${installation.download_url}
ZIP SHA-256：${installation.zip_sha256}

先核验下载文件，再解压到临时目录并阅读 ${installation.package_root}/README.md。包内配置为 ${installation.package_root}/pet.json，图集为 ${installation.package_root}/spritesheet.png。图集 SHA-256：${installation.spritesheet_sha256}。

先识别当前目标应用，再选择目录：
1. Codex：使用实际 CODEX_HOME/pets/${installation.slug}/；CODEX_HOME 未设置时默认 ~/.codex/pets/${installation.slug}/。
2. 其他兼容 Agent：使用其文档或配置中确认的宠物目录，并适配它要求的元数据。
3. 无法确认兼容应用时：使用 PetDex 通用目录 ~/.petdex/pets/${installation.slug}/，同时说明目标应用尚未确认。
不要因找不到 codex 命令而中止。将包内文件直接放入对应的宠物目录，避免重复嵌套一层。已有同名宠物时先保留原文件，不要影响其他宠物。

核对 pet.json 的图片路径以及 1536×2288、192×208 单元格的 Sprite v2 透明 PNG。若应用需要分配新身份，以它的导入结果为准。
${activation}
最后分别报告文件安装目录、校验结果和实际启用状态；不要把下载完成或复制完成当成安装成功。`;
}

function showInstall() {
  $('#install').showModal();
  if (installation) $('#install-prompt').value = installationPrompt();
  if (installPet) installPet.play('waiting');
}

$('#install-open').addEventListener('click', showInstall);
$('#install-close').addEventListener('click', () => $('#install').close());
$('#install').addEventListener('click', (event) => {
  if (event.target !== $('#install')) return;
  const bounds = $('#install').getBoundingClientRect();
  if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) $('#install').close();
});
$('#activate').addEventListener('change', () => {
  if (!installation) return;
  $('#install-prompt').value = installationPrompt();
  $('#copy-status').textContent = $('#activate').checked ? '指令会要求安装后启用小睦。' : '默认只安装，保留当前宠物。';
});
$('#copy').addEventListener('click', async () => {
  $('#copy').disabled = true;
  try {
    await navigator.clipboard.writeText($('#install-prompt').value);
    $('#copy-status').textContent = '指令已复制。把它发给你的 Agent 接瓜吧。';
    if (!paused && installPet) installPet.play('jumping', 'waiting');
  } catch {
    $('#install-prompt').focus();
    $('#install-prompt').select();
    $('#copy-status').textContent = '自动复制未完成，已选中指令，请手动复制。';
  } finally {
    $('#copy').disabled = false;
  }
});

$('#pause').addEventListener('click', () => { paused = !paused; updatePause(); });
motionPreference.addEventListener('change', (event) => { paused = event.matches; updatePause(); });
updatePause();

let backdrop = 0;
const backgrounds = [['grid', '网格'], ['cream', '米白'], ['dark', '深色']];
$('#backdrop').addEventListener('click', () => {
  backdrop = (backdrop + 1) % backgrounds.length;
  $('#stage').dataset.backdrop = backgrounds[backdrop][0];
  $('#backdrop span').textContent = `背景：${backgrounds[backdrop][1]}`;
});

let theme = 0;
const themes = [['system', '跟随系统'], ['light', '浅色'], ['dark', '深色']];
$('#theme').addEventListener('click', () => {
  theme = (theme + 1) % themes.length;
  document.documentElement.dataset.theme = themes[theme][0];
  $('#theme span').textContent = themes[theme][1];
  $('#theme').setAttribute('aria-label', `主题：${themes[theme][1]}，点击切换${themes[(theme + 1) % themes.length][1]}`);
});

async function loadPet() {
  atlas = new Image();
  atlas.src = 'assets/spritesheet.png';
  const [metadata, installMetadata] = await Promise.all([
    fetch('assets/animation-map.json').then((response) => { if (!response.ok) throw new Error('Animation map unavailable'); return response.json(); }),
    fetch('agent-install.json').then((response) => { if (!response.ok) throw new Error('Install metadata unavailable'); return response.json(); }),
    atlas.decode(),
  ]);
  map = metadata;
  installation = installMetadata;
  mainPet = createPlayer($('#pet'), 'idle');
  installPet = createPlayer($('#install-pet'), 'waiting', () => $('#install').open);
  $('#poster').hidden = true;
  $('#pet').hidden = false;
  $('#pet-controls').disabled = false;
  $('#reset').disabled = false;
  $('#copy').disabled = false;
  $('#install-prompt').value = installationPrompt();
  $('#download-zip').href = installation.download_url;
  chooseAction('idle');

  document.querySelectorAll('.actiongrid button').forEach((button) => button.addEventListener('click', () => chooseAction(button.dataset.state)));
  $('#reset').addEventListener('click', () => chooseAction('idle'));
  $('#direction').addEventListener('change', () => {
    if ($('#direction').value === '') return;
    following = false;
    $('#follow').setAttribute('aria-pressed', 'false');
    chooseDirection(Number($('#direction').value));
  });
  $('#follow').addEventListener('click', () => {
    following = !following;
    $('#follow').setAttribute('aria-pressed', String(following));
    chooseDirection(mainPet.direction ?? 4);
  });
  window.addEventListener('pointermove', (event) => {
    if (!following || paused || $('#install').open) return;
    const bounds = $('#pet').getBoundingClientRect();
    const dx = event.clientX - bounds.left - bounds.width * 0.65;
    const dy = event.clientY - bounds.top - bounds.height * 0.75;
    if (Math.hypot(dx, dy) < 10) return;
    const angle = (Math.atan2(dx, -dy) + Math.PI * 2) % (Math.PI * 2);
    const direction = Math.round(angle / (Math.PI / 8)) % 16;
    if (direction !== mainPet.direction) chooseDirection(direction);
  });
  $('#pet').addEventListener('keydown', (event) => {
    if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
    event.preventDefault();
    following = false;
    $('#follow').setAttribute('aria-pressed', 'false');
    const current = mainPet.direction ?? 0;
    const direction = event.key === 'ArrowUp' ? 0 : event.key === 'ArrowDown' ? 8 : (current + (event.key === 'ArrowRight' ? 1 : 15)) % 16;
    chooseDirection(direction);
  });

  let lastTime = performance.now();
  function tick(now) {
    const delta = Math.min(now - lastTime, 100);
    lastTime = now;
    if (!paused && !document.hidden) {
      for (const player of players) {
        if (!player.active() || player.direction !== null) continue;
        const state = map.states.find((item) => item.state === player.state);
        player.elapsed += delta;
        if (player.elapsed < state.durations_ms[player.frame]) continue;
        player.elapsed -= state.durations_ms[player.frame];
        player.frame += 1;
        if (player.frame === state.frame_count) {
          if (player.returnTo) { player.play(player.returnTo); continue; }
          player.frame = 0;
        }
        player.draw();
      }
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

loadPet().catch(() => {
  $('#action-status span').textContent = '小睦加载失败，请刷新重试。';
  $('#copy-status').textContent = '安装信息尚未载入，可以先下载 ZIP。';
});

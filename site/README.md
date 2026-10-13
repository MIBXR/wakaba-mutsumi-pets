# 小睦的像素桌面

若叶睦「好女孩」像素桌宠的静态展示页，采用像素窗口布局。包含九种动作、十六向注视、三种预览背景、暂停、系统/浅色/深色主题、Agent 安装指令与 v1.0 下载入口。

[下载桌宠](https://github.com/MIBXR/wakaba-mutsumi-pets/releases/tag/v1.0) · [创作来源](../pets/wakaba-mutsumi-good-girl-pixel/creation/README.md)

![小睦的像素桌面实际页面](preview.png)

## 本地打开

在此目录启动任意静态 HTTP 服务，例如 `python -m http.server 8772`，然后打开 `http://localhost:8772`。页面不需要依赖安装或构建。

`index.html`、`styles.css`、`app.js`、`agent-install.json` 与 `assets/` 是完整运行文件。动画来自 `pets/wakaba-mutsumi-good-girl-pixel/package/spritesheet.png` 的同内容副本，时序采用作品的 `animation-map.json`。复制安装指令和下载按钮指向同一个经过校验的 GitHub Release 附件。

## 使用

- 默认循环待机，选择按钮后循环对应动作。
- 注视可跟随指针或手动选择方向；聚焦小睦后，左右方向键切换相邻方向，上下方向键看向正上/正下方。
- 暂停会同时停止动作和指针注视，手动选择仍会显示对应静态帧；系统要求减少动态时默认暂停。
- 安装弹窗独立播放递瓜动作。成功复制指令后播放一次庆祝再回到递瓜；暂停或减少动态时只显示文字反馈。
- 安装指令默认保留当前宠物，仅勾选后才要求目标 Agent 启用小睦。网页中的复制、下载均不代表已经安装。

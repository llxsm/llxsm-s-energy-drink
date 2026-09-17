<div align="center">

<img src="app_icon_preview.png" width="140" alt="浪里小神猫的能量小站">

# 浪里小神猫的能量小站

**一个用 Python + Web 技术做的桌面小应用：每天一句温柔勉励，累了就来一局星际巡航。**

[![Python](https://img.shields.io/badge/Python-3.12%20%2F%203.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![pywebview](https://img.shields.io/badge/pywebview-6.x-4B8BBE)](https://pywebview.flowrl.com/)
[![PyInstaller](https://img.shields.io/badge/PyInstaller-single--file-2E8B57)](https://pyinstaller.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D4?logo=windows)](#环境要求)
[![UI](https://img.shields.io/badge/UI-%E7%BA%AF%20HTML%2FCSS%2FJS-f7df1e)](#技术栈)
[![License](https://img.shields.io/badge/License-MIT-3DA639)](LICENSE)

</div>

---

## 目录

- [这是什么](#这是什么)
- [快速开始](#快速开始)
- [两大功能](#两大功能)
  - [📜 今日勉励](#-今日勉励)
  - [🎮 星际巡航](#-星际巡航)
- [项目结构](#项目结构)
- [架构与数据流](#架构与数据流)
- [前后端接口（js_api）](#前后端接口js_api)
- [本地开发](#本地开发)
- [打包成 exe](#打包成-exe)
- [常见问题](#常见问题)
- [开发笔记](#开发笔记)
- [许可证](#许可证)

---

## 这是什么

一个**单文件绿色 exe**，双击即用、无需安装 Python：

- 窗口 520 × 780，无控制台黑框，自带心形图标；
- 界面是一整页 HTML/CSS/JS，由 pywebview 内嵌的 WebView2 渲染，所以动效、渐变、动画都是网页级手感；
- 后端 Python 极轻：只留一个 `webbrowser` 桥（用来在系统浏览器里打开链接）。所有玩法逻辑都在前端，不碰摄像头、不联网、不采集本地数据；
- 六套配色主题：青蓝 / 海洋蓝 / 薄荷绿 / 星空紫 / 落日橙 / 樱花粉，随点随换。

首页长这样：

```
        ┌──────────────────────────────┐
        │             🌅               │
        │          今日勉励             │
        │    送自己一句温柔而坚定的话     │
        │   [  获取今日勉励语句  ]       │
        │   [    原神，启动！    ]       │
        │   [  🎮 星际巡航      ]       │
        │   配色 ● ● ● ● ● ●           │
        └──────────────────────────────┘
```

> 一句话：**用写网页的方式写桌面软件。**

---

## 快速开始

### 普通用户

1. 打开 `dist` 文件夹；
2. 双击 **`浪里小神猫的能量小站.exe`**；
3. 开始用。

`dist\浪里小神猫的能量小站.zip` 是同一个 exe 的压缩包，解压后效果一致。首次启动需要几秒解包，属于 PyInstaller 单文件模式的正常现象。

> **杀毒软件报毒？** PyInstaller 单文件 exe 被误报很常见（自解压行为触发的启发式规则）。加白名单即可；介意的话按[本地开发](#本地开发)直接跑源码。

### 开发者（跑源码）

```bash
pip install pywebview
python wrapper.py
```

在 `build_exe` 目录下执行即可，程序会读取同目录的 `app.html`。运行期依赖只有 pywebview 一个。

---

## 两大功能

### 📜 今日勉励

一句随机生成的温柔句子，句句不重样。

```
        ┌──────────────────────────────────┐
        │              ❝                   │
        │   晨光漫过山脊的时候，愿你始终      │
        │   保有抬头的勇气，而我，始终在      │
        │   你看得见的地方。                │
        └──────────────────────────────────┘
        [  再获取一句  ]      [ 返回 ]
```

句子不是硬编码的几百条，而是**三段式组合生成**：

| 段落 | 数量 | 样例 |
| --- | --- | --- |
| 开头（意象） | 40 | “晨光漫过山脊的时候，” |
| 中段（祝福） | 42 | “愿你始终保有抬头的勇气，” |
| 结尾（表白） | 16 | “而我，始终在你看得见的地方。” |

**40 × 42 × 16 = 26,880 句**，启动时用 Fisher–Yates 洗牌打乱一次，所以每次打开顺序都不同，并且短时间内不会重复上一句。

**彩蛋：防连点。** 600 ms 内连点“再获取一句”，会触发随机吐槽并锁定按钮 1.5 秒，19 条文案轮流上阵，比如：

> “别急嘛，好句子也要喘口气呀～”
> “我猜你是在测试按钮的耐久度，它已经瑟瑟发抖了～”
> “慢慢来，惊喜才不会错过你呀～”

### 🎮 星际巡航

Canvas 手写的太空射击小游戏，420 × 560，星空背景 + 漂浮陨石。

```
   ┌──────────────────────────────┐
   │  ✦        ●        ✦         │  得分 12
   │       ●         ✦            │
   │   ✦        ✦        ●        │
   │            ▲                 │
   │            │  ← 飞船自动开火  │
   └──────────────────────────────┘
        ↑ ↓ ← →   /   W A S D
```

- **操作**：`←` `→` `↑` `↓` 或 `W` `A` `S` `D` 驾驶飞船，**子弹自动发射**（每 0.18 s 一发），专心走位就好；
- **手感**：请求动画帧 + 时间去耦，`dt` 封顶 0.05 s，窗口卡顿不会导致穿模；
- **难度曲线**：陨石生成间隔从 0.95 s 随游戏时间递减到 0.42 s，下落速度同步加快，越往后越手忙脚乱；
- **计分**：小陨石（半径 < 16）2 分，大陨石 1 分——小的更难打；
- **结束**：飞船撞上陨石即结算，弹出得分面板，可“再试一次”或返回首页。

---

## 项目结构

| 路径 | 说明 |
| --- | --- |
| `wrapper.py` | **主程序**。窗口创建 + `js_api` 桥接，约 40 行 |
| `app.html` | **全部界面与玩法**。样式、布局、勉励语句库、小游戏、主题切换都在这一个文件里 |
| `app_icon.ico` | 应用图标（多尺寸：16 / 20 / 24 / 32 / 40 / 48 / 64 / 128 / 256） |
| `make_icon.py` | **图标生成脚本**。用 Pillow + NumPy 画圆角渐变底 + 心形曲线 + 高光，重新生成 `app_icon.ico` |
| `app_icon_preview.png` | 图标预览图（本 README 顶部用的就是它） |
| `浪里小神猫的能量小站.spec` | PyInstaller 打包配置（当前使用） |
| `今日勉励语句.spec` | 早期版本的打包配置，仅作品名不同，保留作历史记录 |
| `dist/` | 打包产物：`浪里小神猫的能量小站.exe` 与同名 `.zip` |
| `build/` | PyInstaller 中间产物（分析缓存、`PYZ-00.pyz` 等），**可安全删除**，下次打包自动重建 |

`build/` 里那几十 MB 的 `.pkg` / `.pyz` 都是中间文件，**不要**当成发布物分发。

---

## 架构与数据流

```
        ┌────────────────────────────────────────────┐
        │            wrapper.py (Python)             │
        │                                            │
        │   resource_path()  →  读取 app.html         │
        │   class Api        →  open_url(url)        │
        │   webview.create_window(..., js_api=Api()) │
        └───────────────────┬────────────────────────┘
                            │ 注入 js_api + 传入 HTML
        ┌───────────────────▼────────────────────────┐
        │      pywebview 窗口（WebView2 内核）         │
        │      app.html：今日勉励 / 星际巡航            │
        │                                            │
        │   · 勉励：26,880 句组合生成 + 洗牌           │
        │   · 游戏：Canvas + requestAnimationFrame    │
        │   · 主题：localStorage 持久化                │
        └────────────────────────────────────────────┘
```

线程模型很简单：pywebview 在自己的消息循环里跑，前端所有计算（洗牌、物理、绘制）都发生在 WebView 的 JS 单线程内，没有跨线程共享状态，也没有后台服务。

---

## 前后端接口（js_api）

`wrapper.py` 的 `Api` 类通过 `js_api=Api()` 注入前端，JS 侧调用方式：

```js
window.pywebview.api.open_url("https://example.com");
```

| 方法 | 参数 | 返回 | 说明 |
| --- | --- | --- | --- |
| `open_url(url)` | 网址 | — | 用系统默认浏览器打开链接（首页“原神，启动！”用的就是它） |

**一个必须知道的坑（代码里已经处理）：** `js_api` 是**异步注入**的，窗口创建后约 1 秒 `window.pywebview.api` 才可用，所以前端不能把它缓存进变量。`app.html` 里统一实时读取 `window.pywebview && window.pywebview.api`，取不到就退回 `window.open()` —— 这样直接用浏览器打开 `app.html` 预览界面也不会报错。

---

## 本地开发

```bash
# 依赖（只有一个）
pip install pywebview

# 运行
python wrapper.py

# 重新生成图标（改配色/形状后）
python make_icon.py
```

改 `app.html` 后**直接重跑 `python wrapper.py`** 即可，无需打包——前端是运行时读文件，不走编译。也可以直接用浏览器打开 `app.html` 调样式、手感，只有“原神，启动！”会走系统浏览器而不是内嵌窗口。

调试小技巧：

- 想临时开控制台看报错，把 spec 里的 `console=False` 改成 `True` 再打包，或直接跑源码；
- 前端报错不好定位时，可以临时给窗口加 `webview.start(debug=True)` 打开开发者工具。

---

## 打包成 exe

```bash
pip install pyinstaller
pyinstaller --noconfirm "浪里小神猫的能量小站.spec"
```

产物：`dist\浪里小神猫的能量小站.exe`（单文件、无控制台、带图标、启用 UPX 压缩）。

spec 的关键几行：

```python
datas=[('app.html', '.')],                 # 把界面打进包里
name='浪里小神猫的能量小站',                   # exe 文件名
icon=['app_icon.ico'], console=False,      # 图标 + 隐藏黑框
```

代码里通过 `resource_path()` 兼容两种形态：打包后从 `sys._MEIPASS` 临时解包目录读 `app.html`，源码运行时从脚本同目录读。

> ⚠️ **改名要改两处**：exe 的**文件名**由 spec 里的 `name=` 决定，窗口标题由 `wrapper.py` 里 `create_window()` 的第一个参数决定。

---

## 常见问题

<details>
<summary><b>窗口一片空白 / 点了按钮没反应</b></summary>

可能是系统缺少 **WebView2 运行时**，去微软官网装一下 Evergreen Runtime 即可。Windows 11 一般自带，Windows 10 部分版本需要手动安装。
</details>

<details>
<summary><b>“原神，启动！”没反应</b></summary>

这个按钮走 `js_api` 桥，需要约 1 秒注入完成，稍等一下再点。如果是在浏览器里直接打开 `app.html`，则会退化为新标签页打开。
</details>

<details>
<summary><b>想改名字 / 换图标</b></summary>

名字：改 spec 里的 `name=`（exe 文件名）和 `wrapper.py` 里 `create_window()` 的第一个参数（窗口标题）；`今日勉励语句.spec` 就是复制改名来的。
图标：改 `make_icon.py` 顶部的配色常量后 `python make_icon.py`，会重新生成 `app_icon.ico`。
</details>

<details>
<summary><b>为什么 exe 有十几 MB？</b></summary>

主要是 PyInstaller 要把 Python 解释器、标准库，以及 WebView2 的 .NET 桥（pythonnet / clr_loader）一起打进去。单文件模式追求的是“双击即用”，不是体积。移除小镜子功能后已不再打包 OpenCV / NumPy，exe 从 **69.7 MB 降到 12.6 MB**。
</details>

---

## 开发笔记

- **运行期依赖只有 pywebview**；`make_icon.py` 额外用到 Pillow 和 NumPy，但那只在生成图标时跑，不影响打包结果。
- **配色只在本次运行内保留**：pywebview 用 HTML 字符串建窗，页面 origin 是 `null`，`localStorage` 会被 WebView2 拒绝（`SecurityError`）。代码里包了一层 `themeStore` 做降级——能写就写、不能写就退回内存，所以换主题立刻生效、重启回到默认青蓝。想真正持久化，可以把这个值交给 Python 侧存文件。
- **实测量级**：`app.html` 约 900 行，`wrapper.py` 约 40 行——重的东西全在前端，Python 侧刻意保持薄。
- **依赖版本**：当前打包环境为 Python 3.12 + pywebview 6.x + PyInstaller 6.x；Windows 平台的 WebView2 桥接依赖 pythonnet / clr_loader。
- **单文件 vs 单目录**：单文件启动慢几秒（每次都要解包到临时目录），换来的是“一个文件发出去就能用”。如果更在意启动速度，可以改用 `--onedir`。
- **`build/` 目录的建议**：加入 `.gitignore`。里面的 `Analysis-00.toc` 有好几 MB，`*.pkg` 更是几十 MB，全是可再生的中间物。
- **版本演进**：早期版本带一个基于 OpenCV 的「小镜子」（摄像头美颜 + 拍照），已按需求整体移除——`Camera` 类、MJPEG 回环服务、滤镜/磨皮/拍照接口、拍照产物目录及相关调试脚本一并删除；小游戏原名也已改为 **星际巡航**。现在 Python 侧只剩一个 `open_url` 桥。

---

## 许可证

本项目采用 **MIT License**，完整条款见仓库中的 [LICENSE](LICENSE) 文件——你可以自由使用、修改、分发，包括商业用途，只需保留版权声明。

---

<div align="center">

用 ❤️ 和一点 Python 做的小东西

**愿你把每一天，都过成值得纪念的日子。**

</div>

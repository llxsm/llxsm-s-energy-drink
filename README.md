<div align="center">

<img src="app_icon_preview.png" width="140" alt="浪里小神猫的能量小站">

# 浪里小神猫的能量小站

**一个用 Python + Web 技术做的桌面小应用：每天一句勉励、一面会美颜的小镜子、一局打发时间的打飞机。**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![pywebview](https://img.shields.io/badge/pywebview-5.x-4B8BBE)](https://pywebview.flowrl.com/)
[![PyInstaller](https://img.shields.io/badge/PyInstaller-single--file-2E8B57)](https://pyinstaller.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D4?logo=windows)](#环境要求)
[![UI](https://img.shields.io/badge/UI-%E7%BA%AF%20HTML%2FCSS%2FJS-f7df1e)](#技术栈)

</div>

---

## 目录

- [这是什么](#这是什么)
- [快速开始](#快速开始)
- [三大功能](#三大功能)
  - [📜 今日勉励](#-今日勉励)
  - [🪞 小镜子](#-小镜子)
  - [🎮 打飞机](#-打飞机)
- [项目结构](#项目结构)
- [架构与数据流](#架构与数据流)
- [前后端接口（js_api）](#前后端接口js_api)
- [本地开发](#本地开发)
- [打包成 exe](#打包成-exe)
- [常见问题](#常见问题)
- [开发笔记](#开发笔记)

---

## 这是什么

一个**单文件绿色 exe**，双击即用、无需安装 Python：

- 窗口 520 × 780，无控制台黑框，自带心形图标；
- 界面是一整页 HTML/CSS/JS，由 pywebview 内嵌的 WebView2 渲染，所以动效、渐变、动画都是网页级手感；
- 后端 Python 只做三件网页做不了（或做不好）的事：**开摄像头、做美颜滤镜、开系统浏览器和文件夹**；
- 六套配色主题：青蓝 / 海洋蓝 / 薄荷绿 / 星空紫 / 落日橙 / 樱花粉，换一次记一辈子（存在 `localStorage`）。

> 一句话：**用写网页的方式写桌面软件。**

---

## 快速开始

### 普通用户

1. 打开 `dist` 文件夹；
2. 双击 **`浪里小神猫的能量小站.exe`**；
3. 开始用。

`dist\浪里小神猫的能量小站.zip` 是同一个 exe 的压缩包（69 MB → 69 MB，主要方便传输），解压后效果一致。首次启动需要几秒解包，属于 PyInstaller 单文件模式的正常现象。

> **杀毒软件报毒？** PyInstaller 单文件 exe 被误报很常见（自解压行为触发的启发式规则）。加白名单即可；介意的话按[本地开发](#本地开发)直接跑源码。

### 开发者（跑源码）

```bash
pip install pywebview opencv-python numpy pillow
python wrapper.py
```

在 `build_exe` 目录下执行即可，程序会读取同目录的 `app.html`。

---

## 三大功能

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

### 🪞 小镜子

调用本机摄像头，实时镜像 + 美颜 + 滤镜，一键拍照存本地。

```
   ┌──────────────────────────────┐
   │                              │
   │        实时视频流（镜像）      │
   │                              │
   └──────────────────────────────┘
   [原图][美颜][美白][红润][黑白][复古][冷色][暖色]
   磨皮  ●───────────────────  20
   亮度  ──────────●─────────   0
   [ 📷 拍照 ]  [ 打开照片文件夹 ]
```

- **镜像**：`cv2.flip(frame, 1)`，像照镜子一样符合直觉；
- **磨皮**：`bilateralFilter` 保边平滑（保留五官轮廓，不是糊成一片），磨皮滑杆 0–100 线性映射滤波强度与混合比例；“美颜”预设会强制把磨皮拉到 60 以上；
- **滤镜**：美白（降饱和 + 提亮）、红润、黑白、复古（Sepia 矩阵）、冷色、暖色，纯 NumPy 通道运算，零额外依赖；
- **拍照**：拍的是**处理后**的帧，以 95 质量编码 JPEG，文件名 `照片_20260909_104338_01.jpg`（时间戳 + 会话内序号，天然防重名）；
- **保存位置**：exe 同级的 **`照片`** 文件夹，不存在会自动创建；界面上的“打开照片文件夹”会直接唤起资源管理器。

> 视频流走本机回环的 MJPEG：Python 起一个 `ThreadingHTTPServer`（端口 `0` = 系统随机分配，不占固定端口），前端 `<img src="http://127.0.0.1:<port>/stream">` 直接消费。这样既避开了 WebView2 对 `getUserMedia` 的权限限制，也顺手拿到了 OpenCV 的全部处理能力。

### 🎮 打飞机

Canvas 手写的太空射击小游戏，420 × 560，星空背景 + 漂浮陨石。

- **操作**：`←` `→` `↑` `↓` 或 `W` `A` `S` `D`，**子弹自动发射**（每 0.18 s 一发），专心走位就好；
- **手感**：请求动画帧 + 时间去耦，`dt` 封顶 0.05 s，窗口卡顿不会导致穿模；
- **难度曲线**：陨石生成间隔从 0.95 s 随游戏时间递减到 0.42 s，下落速度同步加快，越往后越手忙脚乱；
- **计分**：小陨石（半径 < 16）2 分，大陨石 1 分——小的更难打；
- **结束**：飞机撞上陨石即结算，弹出得分面板，可“再试一次”或返回首页。

---

## 项目结构

| 路径 | 说明 |
| --- | --- |
| `wrapper.py` | **主程序**。摄像头采集 / 美颜滤镜 / MJPEG 服务 / js_api 桥接 / 窗口启动 |
| `app.html` | **全部界面**。样式、布局、勉励语句库、小游戏、主题切换都在这一个文件里（1000+ 行） |
| `app_icon.ico` | 应用图标（多尺寸：16 / 20 / 24 / 32 / 40 / 48 / 64 / 128 / 256） |
| `make_icon.py` | **图标生成脚本**。用 Pillow + NumPy 画圆角渐变底 + 心形曲线 + 高光，重新生成 `app_icon.ico` |
| `app_icon_preview.png` | 图标预览图（本 README 顶部用的就是它） |
| `浪里小神猫的能量小站.spec` | PyInstaller 打包配置（当前使用） |
| `今日勉励语句.spec` | 早期版本的打包配置，仅作品名不同，保留作历史记录 |
| `dist/` | 打包产物：`浪里小神猫的能量小站.exe`、同名 `.zip`、运行后生成的 `照片/` |
| `build/` | PyInstaller 中间产物（分析缓存、`PYZ-00.pyz` 等），**可安全删除**，下次打包自动重建 |
| `diag.py` / `diag_result.txt` | 诊断脚本：验证 pywebview 的 `js_api` 注入时机与调用链 |
| `cam_test.py` / `cam_result.txt` | 诊断脚本：验证 WebView2 下 `getUserMedia` 的可用性与报错名 |
| `__pycache__/` | Python 字节码缓存，可删 |

`build/` 里那几十 MB 的 `.pkg` / `.pyz` 都是中间文件，**不要**当成发布物分发。

---

## 架构与数据流

```
                    ┌──────────────────────────────────────┐
                    │           wrapper.py (Python)        │
                    │                                      │
   前端调用 ───────▶ │  class Api  ──  open_url             │
   (js_api)         │             ├─  start_mirror          │
                    │             ├─  stop_mirror           │
                    │             ├─  set_effect            │
                    │             ├─  set_param             │
                    │             ├─  capture               │
                    │             └─  open_photos           │
                    │                    │                 │
                    │                    ▼                 │
                    │  class Camera ──────────────┐        │
                    │   ├─ cv2.VideoCapture(0)    │        │
                    │   ├─ 滤镜 / 磨皮 / 亮度      │        │
                    │   └─ capture() → 照片/*.jpg  │        │
                    └──────────────────────────────┼───────┘
                                                   │
                    ┌──────────────────────────────▼───────┐
                    │  ThreadingHTTPServer (127.0.0.1:0)   │
                    │  GET /stream → MJPEG 多段流           │
                    └──────────────┬───────────────────────┘
                                   │ <img src=".../stream">
                    ┌──────────────▼───────────────────────┐
                    │   pywebview 窗口（WebView2 内核）      │
                    │   app.html：勉励 / 小镜子 / 打飞机      │
                    └──────────────────────────────────────┘
```

线程模型：主线程跑 pywebview 消息循环；摄像头采集线程 20 ms 一轮写入最新帧；HTTP 服务线程按 30 ms 节流推送 JPEG；三者用一把 `threading.Lock` 保护共享帧，互不阻塞。

---

## 前后端接口（js_api）

`wrapper.py` 的 `Api` 类通过 `js_api=Api()` 注入前端，JS 侧调用方式：

```js
const url = await window.pywebview.api.start_mirror();
```

| 方法 | 参数 | 返回 | 说明 |
| --- | --- | --- | --- |
| `open_url(url)` | 网址 | — | 用系统默认浏览器打开链接 |
| `start_mirror()` | — | `"http://127.0.0.1:<port>/stream"` 或 `""` | 打开摄像头并启动 MJPEG 服务，失败返回空串 |
| `stop_mirror()` | — | — | 停止采集、释放摄像头、关闭 HTTP 服务 |
| `set_effect(name)` | `none` `beauty` `whiten` `rosy` `bw` `vintage` `cool` `warm` | — | 切换滤镜预设 |
| `set_param(key, value)` | `smooth` 0–100 / `brightness` -100–100 | — | 调整磨皮与亮度，越界自动裁剪，非数字忽略 |
| `capture()` | — | 保存路径 或 `null` | 保存当前处理后画面为 JPEG |
| `open_photos()` | — | — | 用资源管理器打开照片文件夹 |

**两个必须知道的坑（代码里已经处理）：**

1. **`js_api` 是异步注入的**——窗口创建后约 1 秒 `window.pywebview.api` 才可用。所以前端**不能**把它缓存进变量（`diag.py` + `diag_result.txt` 就是验证这件事的：t0 时是 `undefined`，t1500 时已有完整方法列表）。界面里统一用 `getApi()` 实时读取，点击“小镜子”时还会最多轮询 4 秒等接口就绪。
2. **摄像头不要用 `getUserMedia`**——WebView2 下权限链路容易失败（`cam_test.py` 就是为此写的探针）。改用 OpenCV 在本机采集、再以 MJPEG 回环推送，稳定且可控。

---

## 本地开发

```bash
# 依赖
pip install pywebview opencv-python numpy pillow

# 运行
python wrapper.py

# 重新生成图标（改配色/形状后）
python make_icon.py
```

改 `app.html` 后**直接重跑 `python wrapper.py`** 即可，无需打包——前端是运行时读文件，不走编译。

调试小技巧：

- 想临时开控制台看报错，把 spec 里的 `console=False` 改成 `True` 再打包，或直接跑源码；
- 前端报错不好定位时，可以临时给窗口加 `webview.start(debug=True)` 打开开发者工具；
- 摄像头相关的问题，先跑 `python cam_test.py`，结果会写到 `cam_result.txt`。

---

## 打包成 exe

```bash
pip install pyinstaller
pyinstaller --noconfirm "浪里小神猫的能量小站.spec"
```

产物：`dist\浪里小神猫的能量小站.exe`（单文件、无控制台、带图标、启用 UPX 压缩，约 70 MB）。

spec 的关键三行：

```python
datas=[('app.html', '.')],                 # 把界面打进包里
name='浪里小神猫的能量小站',                   # 产物名
icon=['app_icon.ico'], console=False,      # 图标 + 隐藏黑框
```

代码里通过 `resource_path()` 兼容两种形态：打包后从 `sys._MEIPASS` 临时解包目录读 `app.html`，源码运行时从脚本同目录读。

> ⚠️ **注意**：现有 `dist` 里的 exe 构建于 2026-08-21，而 `app.html` 在 2026-09-09 又更新过。想拿到最新界面，请按上面的命令重新打包。

---

## 常见问题

<details>
<summary><b>“无法打开摄像头，请检查系统相机权限”</b></summary>

1. Windows 设置 → 隐私和安全性 → 相机 → 允许桌面应用访问相机；
2. 关掉正在占用摄像头的软件（微信、腾讯会议、OBS 等）；
3. 确认设备管理器里摄像头驱动正常；
4. 代码已做兜底：先尝试 `CAP_DSHOW` 后端，失败再退回默认后端。
</details>

<details>
<summary><b>窗口一片空白 / 点了按钮没反应</b></summary>

多半是 `js_api` 还没注入就点了按钮（启动后约 1 秒）。稍等片刻重试即可；如果持续空白，可能是系统缺少 **WebView2 运行时**，去微软官网装一下 Evergreen Runtime。Windows 11 一般自带。
</details>

<details>
<summary><b>照片存到哪儿了？</b></summary>

exe 同级的 `照片` 文件夹，文件名形如 `照片_20260909_104338_01.jpg`。点界面上的“打开照片文件夹”可以直接跳过去。
</details>

<details>
<summary><b>想改名字 / 换图标</b></summary>

名字：改 spec 文件里的 `name=`（或复制一份 spec 改个名，`今日勉励语句.spec` 就是这么来的）。
图标：改 `make_icon.py` 顶部的配色常量后 `python make_icon.py`，会重新生成 `app_icon.ico`。
</details>

<details>
<summary><b>为什么 exe 有 70 MB？</b></summary>

OpenCV + NumPy 本身就占大头，PyInstaller 还会把 Python 解释器、标准库、WebView2 的 .NET 桥（pythonnet / clr_loader）一起打进去。单文件模式追求的是“双击即用”，不是体积。
</details>

---

## 开发笔记

- **依赖版本**：打包环境为 Python 3.13，涉及 pywebview 5.x、opencv-python、numpy、Pillow、PyInstaller；Windows 平台的 WebView2 桥接依赖 pythonnet / clr_loader。
- **单文件 vs 单目录**：单文件启动慢几秒（每次都要解包到临时目录），换来的是“一个文件发出去就能用”。如果更在意启动速度，可以改用 `--onedir`。
- **`build/` 目录的建议**：加入 `.gitignore`。里面的 `Analysis-00.toc` 有好几 MB，`*.pkg` 更是几十 MB，全是可再生的中间物。
- **安全提示**：MJPEG 服务只监听 `127.0.0.1`，不会暴露到局域网；端口由系统随机分配，进程退出即释放。

---

<div align="center">

用 ❤️ 和一点 Python 做的小东西

**愿你把每一天，都过成值得纪念的日子。**

</div>

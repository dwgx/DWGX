<!-- ════════════════════════════════════════════════════════════════ -->
<!--  dwgx.menu  v2.1                                                 -->
<!-- ════════════════════════════════════════════════════════════════ -->

<img src="assets/bios-header.png" width="100%" alt="dwgx.menu" />

<div align="center">

<img src="https://q1.qlogo.cn/g?b=qq&nk=136666451&s=640" width="128" style="border-radius:50%;" />

<br/>

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Noto+Serif+JP&weight=600&size=22&pause=1200&color=F2A6C4&center=true&vCenter=true&random=false&width=600&lines=injected+into+process+%C2%B7+host%3Dkobe;Java+%C2%B7+C%2B%2B+%C2%B7+C%23+%C2%B7+Swift+%C2%B7+TypeScript;Reverse+Engineering+%C2%B7+Game+Hacking+%C2%B7+Systems)](https://dwgx.github.io)

<p>
  <img src="https://komarev.com/ghpvc/?username=DWGX&style=flat-square&color=f2a6c4&label=visits" />
  &nbsp;
  <img src="https://img.shields.io/github/followers/DWGX?style=flat-square&color=f2a6c4&label=follow" />
  &nbsp;
  <img src="https://img.shields.io/github/stars/DWGX?style=flat-square&color=c9a84c&label=stars" />
</p>

<p>
  <img src="https://img.shields.io/badge/total_stars-3k+-c9a84c?style=flat-square&labelColor=06020f" />
  &nbsp;
  <img src="https://img.shields.io/badge/public_repos-83-f2a6c4?style=flat-square&labelColor=06020f" />
  &nbsp;
  <img src="https://img.shields.io/badge/flagship-WindsurfAPI_★2889-2d1b69?style=flat-square&labelColor=06020f" />
</p>

</div>

---

### `main.cfg`

```ini
; dwgx.cfg  —  last modified 2026-07-14 JST
; injection status: active  ·  process.count: 12

[identity]
alias      = dwgx · 帝王尬笑
location   = Kobe, Hyogo · JST+9
motto      = be water
bio        = 也许我就是dwgx

[role]
primary    = independent-developer
origin     = Minecraft cheat scene
focus      = reverse-engineering, game-hacking, systems, backend, ai-tooling
anti-focus = normal-human-activity

[languages]
active     = rust · java · cpp · csharp · swift · typescript · python · go
previous   = js · php
```

---

### `process.table`

```
 PID    MODULE                   ADDR             LANG    STATUS
 ──────────────────────────────────────────────────────────────────────────────
 0001   WindsurfAPI              0x7FF6A4010000   js      LISTENING  :8080  ★2889
 0002   KiroStudio               0x7FF6A40AB000   rust    GATEWAY  proto-bridge+pool
 0003   SaoMoLa                  0x7FF6A40FF000   c       UPLOADING  vrc.avatar.pipe
 0004   driver-vuln-research     0x7FF6A4180000   asm     BYOVD  ring0.probe
 0005   vrchat-il2cpp-re         0x7FF6A4220000   c#      ▓▓▓▓▓▓▓▓▓░  64k cls deobf
 0006   SmartCLI                 0x7FF6A42D0000   py      PTY+pyte  tui.driver
 0007   VRCSM                    0x7FF6A4350000   ts      ▓▓▓▓▓▓▓░░░  cache.mgr
 0008   claude-code-fork         0x7FF6A4400000   ts      SOURCEMAP  cli.reversed
 0009   RepoDLL                  0x7FF6A4480000   cpp     HOOKED  Present()  ★10
 0010   Lavender-rise-main       0x7FF6A4520000   java    MC-1.21  cheat-client
 0011   flipper-custom-apps      0x7FF6A45C0000   c       ESP32-BOOST  ble-spam
 0012   FlipperZeroTeacher       0x7FF6A4660000   html    雙語教學.知識庫
```

---

<div align="center">

### `pinned`

<table>
<tr>
<td width="33%" valign="top">

```
╔════════════════════════╗
║ vrchat-il2cpp-re       ║
╠════════════════════════╣
║                        ║
║ 64K classes            ║
║ 570K methods · 188K fld║
║ Unity 6 baseline RE    ║
║                        ║
║ lang  · C#             ║
║ stage · live           ║
║ diff  · ★★★★☆          ║
╚════════════════════════╝
```

[open module →](https://github.com/dwgx/vrchat-il2cpp-re)

</td>
<td width="33%" valign="top">

```
╔════════════════════════╗
║ KiroStudio             ║
╠════════════════════════╣
║                        ║
║ Kiro unified gateway   ║
║ proto-bridge + pool    ║
║ Rust + SQLite + Docker ║
║                        ║
║ lang  · Rust           ║
║ stage · active-dev     ║
║ diff  · ★★★★☆          ║
╚════════════════════════╝
```

[open module →](https://github.com/dwgx/KiroStudio)

</td>
<td width="33%" valign="top">

```
╔════════════════════════╗
║ WindsurfAPI            ║
╠════════════════════════╣
║                        ║
║ Windsurf ⇄ OpenAI      ║
║ 100+ models · 3 APIs   ║
║ zero-dep self-host     ║
║                        ║
║ lang  · JavaScript     ║
║ stage · flagship ★2889 ║
║ diff  · ★★☆☆☆          ║
╚════════════════════════╝
```

[open module →](https://github.com/dwgx/WindsurfAPI)

</td>
</tr>
<tr>
<td width="33%" valign="top">

```
╔════════════════════════╗
║ SmartCLI               ║
╠════════════════════════╣
║                        ║
║ 3 agent skills · 1 PTY ║
║ pyte cell-accurate TUI ║
║ pip smartcli-toolkit   ║
║                        ║
║ lang  · Python         ║
║ stage · shipped        ║
║ diff  · ★★★☆☆          ║
╚════════════════════════╝
```

[open module →](https://github.com/dwgx/SmartCLI)

</td>
<td width="33%" valign="top">

```
╔════════════════════════╗
║ VRCSM                  ║
╠════════════════════════╣
║                        ║
║ VRChat cache / config  ║
║ Windows desktop app    ║
║ C++20 + WebView2 + TS  ║
║                        ║
║ lang  · TypeScript     ║
║ stage · active-dev     ║
║ diff  · ★★★☆☆          ║
╚════════════════════════╝
```

[open module →](https://github.com/dwgx/VRCSM)

</td>
<td width="33%" valign="top">

```
╔════════════════════════╗
║ + 78 more modules      ║
╠════════════════════════╣
║                        ║
║ 83 public repos        ║
║ 3k+ total stars        ║
║ solo crew · kobe       ║
║                        ║
║ lang  · polyglot       ║
║ stage · always-on      ║
║ diff  · ★★★★★          ║
╚════════════════════════╝
```

[browse all →](https://github.com/dwgx?tab=repositories)

</td>
</tr>
</table>

</div>

---

### `recent.log`

```
 2026-07-14 --:--   push  driver-vuln-research  ★0     asm    byovd kernel driver research
 2026-07-14 --:--   push  SaoMoLa               ★0     c      vrchat avatar extract/upload
 2026-07-14 --:--   push  KiroStudio            ★3     rust   kiro gateway · pool + inject
 2026-07-13 --:--   push  SmartCLI              ★2     py     pty+pyte tui driver · pip pkg
 2026-07-13 --:--   push  WindsurfAPI           ★2889  js     windsurf ⇄ openai/anthropic
 2026-07-13 --:--   push  claude-code-fork      ★0     ts     cli fork · sourcemap restore
 2026-07-12 --:--   push  beautify-console      ★1     js     vscode visual beautify panel
 2026-07-11 --:--   push  MCPClient             ★0     java   mcp client experiment
 2026-07-13 --:--   push  vrchat-il2cpp-re      ★19    c#     64k cls · unity 6 baseline
 2026-07-10 --:--   push  VRCSM                 ★3     ts     vrchat cache/settings manager
```

<details>
<summary><code>archive.log  — +25 older entries</code></summary>

```
 2026-02-11 --:--   push  JSM                   ★12    swift  macos mc-server manager · java/paper/spigot
 2026-01-17 --:--   push  RepoDLL               ★10    cpp    r.e.p.o. dx11/imgui overlay · unity/mono
 2026-02-23 --:--   push  THIzaKaYaDEVCosole    ★8     cpp    東方雾雨居酒屋 il2cpp debug console
 2025-04-06 --:--   push  NewAppleMusicPlayer   ★9     js     electron apple music · dynamic-island ui
 2025-03-07 --:--   push  Lavender-rise-main    ★8     java   old dream mc client · republished w/ love
 2026-06-16 --:--   push  bing-rewards-auto     ★5     py     ms rewards auto-farmer · playwright
 2026-07-06 --:--   push  CEGM                  ★3     py     llm-driven cheat engine layer · mcp http
 2026-07-10 --:--   push  VirtualDesktop        ★1     c#     离线串流补丁 + 汉化 · il 级二进制补丁工程
 2026-07-06 --:--   push  debugger-workstation  ★1     py     portable re/security workstation skeleton
 2026-07-06 --:--   push  AgentScope            ★1     ts     monitor codex/claude sessions · safety ctrl
 2026-07-06 --:--   push  Quest-ADB-Dashboard   ★1     c#     meta quest adb diagnostics dashboard
 2026-07-06 --:--   push  TH08-Platform         ★1     cpp    東方8 联机平台 · decomp + dll injection
 2026-06-13 --:--   push  crash-sentinel        ★2     ps     windows thermal / power-loss crash monitor
 2026-04-09 --:--   push  blender-copilot       ★1     py     blender mcp · ai 3d · vrchat pipeline
 2026-07-10 --:--   push  vrc-mod-guide         ★1     js     改模资源库 · 拿 ai 跑了两天爬出来的
 2026-01-10 --:--   push  PTTRDLL               ★1     c#     pttr dx11/imgui playground · that era's feel
 2026-02-12 --:--   push  Rep0S2cLeak           ★1     c#     r.e.p.o. src snapshot · chaotic but historic
 2025-08-10 --:--   push  Dustman               ★1     py     pyqt windows cleaner · preview-first
 2024-11-24 --:--   push  KeyManagerApp         ★1     py     fbl 档案柜式本地加密密钥管理器 · pyside6
 2024-09-01 --:--   push  OpenNative            ★1     -      old mc client · 狗屎实验
 2025-01-25 --:--   push  Wechathacker          ★1     -      很邪恶的旧版微信内存研究
 2025-04-22 --:--   push  MouseDash             ★1     py     老鼠大师
 2023-11-11 --:--   push  Open-source-sharing   ★1     -      当年购入现在不用的 · 倒卖成分我不说
 2024-11-08 --:--   push  GarlicKing            ★1     java   makes your intestines confuse and spin
 2024-11-03 --:--   push  Example-Wasted1       ★2     java   like a man perfectly mating with a woman
```

</details>

---

### `hardware.dmp`

```
               ╭─── dwgx@kobe ──────────────────────────────────╮
               │                                                │
 ROG Strix ════╡  host       ASUS ROG Strix G18  (primary)      │
               │  cpu        Intel Ultra 9 275HX                │
               │  gpu        NVIDIA RTX 5070 Ti                 │
               │  mem        32 GB DDR5                         │
               │  disp       18"  2.5K                          │
               │                                                │
 Desktop ══════╡  gpu        Colorful iGame RTX 3060 Ultra      │
               │  mem        16 GB DDR4 3200                    │
               │                                                │
 MacBook ══════╡  host       MacBook Air M2 · A2681             │
               │  mem        8 GB · 256 GB SSD · 13.6" Retina   │
               │                                                │
 Mobile ═══════╡  phone      iPhone 17 · 256GB · JP-region      │
               │  phone-2    Redmi K60 · 512GB                  │
               │  wear       Apple Watch 1st · Stainless · 2015 │
               │                                                │
 Peripheral ═══╡  kbd        VGN FLASH Ultra 太陽神 · mag-switch │
               │  mouse      VGN Dragonfly 3 Master 超跑紅 · 56g │
               │  audio      AirPods Pro 3 · Panasonic SL-CT790 │
               │  vr         Meta Quest 3                       │
               │                                                │
               │  uptime     5853 days                          │
               │  status     online · JST+9                     │
               ╰────────────────────────────────────────────────╯
```

---

<div align="center">

### `discord.presence`

<a href="https://discord.com/users/1284670281926967336">
  <img src="https://lanyard.cnrad.dev/api/1284670281926967336?theme=dark&bg=06020f&borderRadius=10px&animated=true&idleMessage=AFK%20%C2%B7%20probably%20coding" alt="discord presence" />
</a>

---

### `featured`

## 幻想万華鏡 ~ The Memories of Phantasm

<img src="assets/gensou.gif" width="640" />

<br/>

<sub>滿福神社製作  ·  全18話  ·  BDRip  ·  東方Project 二次創作</sub>

<br/><br/>

<img src="https://img.shields.io/badge/東方Project-二次創作-f2a6c4?style=flat-square&labelColor=06020f" />
<img src="https://img.shields.io/badge/滿福神社-Studio-c9a84c?style=flat-square&labelColor=06020f" />
<img src="https://img.shields.io/badge/Episodes-18-d4c8ef?style=flat-square&labelColor=06020f" />
<img src="https://img.shields.io/badge/Format-BDRip-2d1b69?style=flat-square&labelColor=06020f" />

</div>

---

<!-- ════════════════════════════════════════════════════════════════ -->
<!--  style switch: scene-nfo release note                            -->
<!-- ════════════════════════════════════════════════════════════════ -->

. d w g x . p r e s e n t s .

dwgx.menu · v2.1 · 2026  
scene release // kobe, jp // solo crew

**group** — dwgx  
**location** — kobe · jp · jst+9  
**release** — personal-profile.v2.1  
**files** — 1 readme.md + 3 assets  
**size** — ≈ 2.0 mb (gif-heavy)  
**target** — github.com/dwgx  
**born** — 20100705  
**date** — 2026.07.14

<div align="center">

### `▓▒░  [ stack.manifest ]  ░▒▓`

<img src="https://skillicons.dev/icons?i=rust,java,spring,kotlin,cpp,cmake,cs,swift,ts,py,go,react,vue,vite,tailwind,mysql,redis,nginx,cloudflare,nodejs,docker&perline=21" />

</div>

<table align="center" width="100%">
<tr>
  <td align="right" width="110"><code><b>jvm</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Java_21-ED8B00?style=for-the-badge&labelColor=06020f&logo=openjdk&logoColor=white" />
    <img src="https://img.shields.io/badge/Paper_Plugin-F2A6C4?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXNjcm9sbCIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjMDYwMjBmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0xOSAxN1Y1YTIgMiAwIDAgMC0yLTJINCIgLz4KICA8cGF0aCBkPSJNOCAyMWgxMmEyIDIgMCAwIDAgMi0ydi0xYTEgMSAwIDAgMC0xLTFIMTFhMSAxIDAgMCAwLTEgMXYxYTIgMiAwIDEgMS00IDBWNWEyIDIgMCAxIDAtNCAwdjJhMSAxIDAgMCAwIDEgMWgzIiAvPgo8L3N2Zz4=&logoColor=white" />
    <img src="https://img.shields.io/badge/Spring_Boot-6DB33F?style=for-the-badge&labelColor=06020f&logo=springboot&logoColor=white" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>native</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Rust-000000?style=for-the-badge&labelColor=06020f&logo=rust&logoColor=white" />
    <img src="https://img.shields.io/badge/C%2B%2B_20-00599C?style=for-the-badge&labelColor=06020f&logo=cplusplus&logoColor=white" />
    <img src="https://img.shields.io/badge/CMake-064F8C?style=for-the-badge&labelColor=06020f&logo=cmake&logoColor=white" />
    <img src="https://img.shields.io/badge/Dear_ImGui-2D1B69?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXBhbmVscy10b3AtbGVmdCIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxyZWN0IHdpZHRoPSIxOCIgaGVpZ2h0PSIxOCIgeD0iMyIgeT0iMyIgcng9IjIiIC8+CiAgPHBhdGggZD0iTTMgOWgxOCIgLz4KICA8cGF0aCBkPSJNOSAyMVY5IiAvPgo8L3N2Zz4=&logoColor=white" />
    <img src="https://img.shields.io/badge/DirectX_11-76B900?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWJveCIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0yMSA4YTIgMiAwIDAgMC0xLTEuNzNsLTctNGEyIDIgMCAwIDAtMiAwbC03IDRBMiAyIDAgMCAwIDMgOHY4YTIgMiAwIDAgMCAxIDEuNzNsNyA0YTIgMiAwIDAgMCAyIDBsNy00QTIgMiAwIDAgMCAyMSAxNloiIC8+CiAgPHBhdGggZD0ibTMuMyA3IDguNyA1IDguNy01IiAvPgogIDxwYXRoIGQ9Ik0xMiAyMlYxMiIgLz4KPC9zdmc+&logoColor=white" />
    <img src="https://img.shields.io/badge/Win32-0078D6?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWFwcC13aW5kb3ciCiAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iI2ZmZmZmZiIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cmVjdCB4PSIyIiB5PSI0IiB3aWR0aD0iMjAiIGhlaWdodD0iMTYiIHJ4PSIyIiAvPgogIDxwYXRoIGQ9Ik0xMCA0djQiIC8+CiAgPHBhdGggZD0iTTIgOGgyMCIgLz4KICA8cGF0aCBkPSJNNiA0djQiIC8+Cjwvc3ZnPg==&logoColor=white" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>managed</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/C%23-239120?style=for-the-badge&labelColor=06020f&logo=csharp&logoColor=white" />
    <img src="https://img.shields.io/badge/Swift-FA7343?style=for-the-badge&labelColor=06020f&logo=swift&logoColor=white" />
    <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&labelColor=06020f&logo=typescript&logoColor=white" />
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&labelColor=06020f&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&labelColor=06020f&logo=go&logoColor=white" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>reverse</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/IDA_Pro-C9A84C?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXNlYXJjaC1jb2RlIgogIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICB3aWR0aD0iMjQiCiAgaGVpZ2h0PSIyNCIKICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgZmlsbD0ibm9uZSIKICBzdHJva2U9IiMwNjAyMGYiCiAgc3Ryb2tlLXdpZHRoPSIyIgogIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICBzdHJva2UtbGluZWpvaW49InJvdW5kIgo+CiAgPHBhdGggZD0ibTEzIDEzLjUgMi0yLjUtMi0yLjUiIC8+CiAgPHBhdGggZD0ibTIxIDIxLTQuMy00LjMiIC8+CiAgPHBhdGggZD0iTTkgOC41IDcgMTFsMiAyLjUiIC8+CiAgPGNpcmNsZSBjeD0iMTEiIGN5PSIxMSIgcj0iOCIgLz4KPC9zdmc+&logoColor=white" />
    <img src="https://img.shields.io/badge/Ghidra-FF6E00?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWJ1ZyIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0xMiAyMHYtOSIgLz4KICA8cGF0aCBkPSJNMTQgN2E0IDQgMCAwIDEgNCA0djNhNiA2IDAgMCAxLTEyIDB2LTNhNCA0IDAgMCAxIDQtNHoiIC8+CiAgPHBhdGggZD0iTTE0LjEyIDMuODggMTYgMiIgLz4KICA8cGF0aCBkPSJNMjEgMjFhNCA0IDAgMCAwLTMuODEtNCIgLz4KICA8cGF0aCBkPSJNMjEgNWE0IDQgMCAwIDEtMy41NSAzLjk3IiAvPgogIDxwYXRoIGQ9Ik0yMiAxM2gtNCIgLz4KICA8cGF0aCBkPSJNMyAyMWE0IDQgMCAwIDEgMy44MS00IiAvPgogIDxwYXRoIGQ9Ik0zIDVhNCA0IDAgMCAwIDMuNTUgMy45NyIgLz4KICA8cGF0aCBkPSJNNiAxM0gyIiAvPgogIDxwYXRoIGQ9Im04IDIgMS44OCAxLjg4IiAvPgogIDxwYXRoIGQ9Ik05IDcuMTNWNmEzIDMgMCAxIDEgNiAwdjEuMTMiIC8+Cjwvc3ZnPg==&logoColor=white" />
    <img src="https://img.shields.io/badge/x64dbg-1E90FF?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWJpbmFyeSIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxyZWN0IHg9IjE0IiB5PSIxNCIgd2lkdGg9IjQiIGhlaWdodD0iNiIgcng9IjIiIC8+CiAgPHJlY3QgeD0iNiIgeT0iNCIgd2lkdGg9IjQiIGhlaWdodD0iNiIgcng9IjIiIC8+CiAgPHBhdGggZD0iTTYgMjBoNCIgLz4KICA8cGF0aCBkPSJNMTQgMTBoNCIgLz4KICA8cGF0aCBkPSJNNiAxNGgydjYiIC8+CiAgPHBhdGggZD0iTTE0IDRoMnY2IiAvPgo8L3N2Zz4=&logoColor=white" />
    <img src="https://img.shields.io/badge/Il2CppDumper-8A2BE2?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWxheWVycyIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0xMi44MyAyLjE4YTIgMiAwIDAgMC0xLjY2IDBMMi42IDYuMDhhMSAxIDAgMCAwIDAgMS44M2w4LjU4IDMuOTFhMiAyIDAgMCAwIDEuNjYgMGw4LjU4LTMuOWExIDEgMCAwIDAgMC0xLjgzeiIgLz4KICA8cGF0aCBkPSJNMiAxMmExIDEgMCAwIDAgLjU4LjkxbDguNiAzLjkxYTIgMiAwIDAgMCAxLjY1IDBsOC41OC0zLjlBMSAxIDAgMCAwIDIyIDEyIiAvPgogIDxwYXRoIGQ9Ik0yIDE3YTEgMSAwIDAgMCAuNTguOTFsOC42IDMuOTFhMiAyIDAgMCAwIDEuNjUgMGw4LjU4LTMuOUExIDEgMCAwIDAgMjIgMTciIC8+Cjwvc3ZnPg==&logoColor=white" />
    <img src="https://img.shields.io/badge/dnSpy-4B4B4B?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWZpbGUtY29kZSIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik02IDIyYTIgMiAwIDAgMS0yLTJWNGEyIDIgMCAwIDEgMi0yaDhhMi40IDIuNCAwIDAgMSAxLjcwNC43MDZsMy41ODggMy41ODhBMi40IDIuNCAwIDAgMSAyMCA4djEyYTIgMiAwIDAgMS0yIDJ6IiAvPgogIDxwYXRoIGQ9Ik0xNCAydjVhMSAxIDAgMCAwIDEgMWg1IiAvPgogIDxwYXRoIGQ9Ik0xMCAxMi41IDggMTVsMiAyLjUiIC8+CiAgPHBhdGggZD0ibTE0IDEyLjUgMiAyLjUtMiAyLjUiIC8+Cjwvc3ZnPg==&logoColor=white" />
    <img src="https://img.shields.io/badge/Cheat_Engine-D01C1F?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWhlYXJ0LXB1bHNlIgogIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICB3aWR0aD0iMjQiCiAgaGVpZ2h0PSIyNCIKICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgZmlsbD0ibm9uZSIKICBzdHJva2U9IiNmZmZmZmYiCiAgc3Ryb2tlLXdpZHRoPSIyIgogIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICBzdHJva2UtbGluZWpvaW49InJvdW5kIgo+CiAgPHBhdGggZD0iTTIgOS41YTUuNSA1LjUgMCAwIDEgOS41OTEtMy42NzYuNTYuNTYgMCAwIDAgLjgxOCAwQTUuNDkgNS40OSAwIDAgMSAyMiA5LjVjMCAyLjI5LTEuNSA0LTMgNS41bC01LjQ5MiA1LjMxM2EyIDIgMCAwIDEtMyAuMDE5TDUgMTVjLTEuNS0xLjUtMy0zLjItMy01LjUiIC8+CiAgPHBhdGggZD0iTTMuMjIgMTNIOS41bC41LTEgMiA0LjUgMi03IDEuNSAzLjVoNS4yNyIgLz4KPC9zdmc+&logoColor=white" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>os / kernel</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Windows_Kernel-0078D6?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNwdSIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0xMiAyMHYyIiAvPgogIDxwYXRoIGQ9Ik0xMiAydjIiIC8+CiAgPHBhdGggZD0iTTE3IDIwdjIiIC8+CiAgPHBhdGggZD0iTTE3IDJ2MiIgLz4KICA8cGF0aCBkPSJNMiAxMmgyIiAvPgogIDxwYXRoIGQ9Ik0yIDE3aDIiIC8+CiAgPHBhdGggZD0iTTIgN2gyIiAvPgogIDxwYXRoIGQ9Ik0yMCAxMmgyIiAvPgogIDxwYXRoIGQ9Ik0yMCAxN2gyIiAvPgogIDxwYXRoIGQ9Ik0yMCA3aDIiIC8+CiAgPHBhdGggZD0iTTcgMjB2MiIgLz4KICA8cGF0aCBkPSJNNyAydjIiIC8+CiAgPHJlY3QgeD0iNCIgeT0iNCIgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2IiByeD0iMiIgLz4KICA8cmVjdCB4PSI4IiB5PSI4IiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMSIgLz4KPC9zdmc+&logoColor=white" />
    <img src="https://img.shields.io/badge/Ring0-D01C1F?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXNoaWVsZC1hbGVydCIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0yMCAxM2MwIDUtMy41IDcuNS03LjY2IDguOTVhMSAxIDAgMCAxLS42Ny0uMDFDNy41IDIwLjUgNCAxOCA0IDEzVjZhMSAxIDAgMCAxIDEtMWMyIDAgNC41LTEuMiA2LjI0LTIuNzJhMS4xNyAxLjE3IDAgMCAxIDEuNTIgMEMxNC41MSAzLjgxIDE3IDUgMTkgNWExIDEgMCAwIDEgMSAxeiIgLz4KICA8cGF0aCBkPSJNMTIgOHY0IiAvPgogIDxwYXRoIGQ9Ik0xMiAxNmguMDEiIC8+Cjwvc3ZnPg==&logoColor=white" />
    <img src="https://img.shields.io/badge/BYOVD-8A2BE2?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXNoaWVsZC1vZmYiCiAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iI2ZmZmZmZiIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJtMiAyIDIwIDIwIiAvPgogIDxwYXRoIGQ9Ik01IDVhMSAxIDAgMCAwLTEgMXY3YzAgNSAzLjUgNy41IDcuNjcgOC45NGExIDEgMCAwIDAgLjY3LjAxYzIuMzUtLjgyIDQuNDgtMS45NyA1LjktMy43MSIgLz4KICA8cGF0aCBkPSJNOS4zMDkgMy42NTJBMTIuMjUyIDEyLjI1MiAwIDAgMCAxMS4yNCAyLjI4YTEuMTcgMS4xNyAwIDAgMSAxLjUyIDBDMTQuNTEgMy44MSAxNyA1IDE5IDVhMSAxIDAgMCAxIDEgMXY3YTkuNzg0IDkuNzg0IDAgMCAxLS4wOCAxLjI2NCIgLz4KPC9zdmc+&logoColor=white" />
    <img src="https://img.shields.io/badge/VT_x-C9A84C?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLW1pY3JvY2hpcCIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjMDYwMjBmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0xMCAxMmg0IiAvPgogIDxwYXRoIGQ9Ik0xMCAxN2g0IiAvPgogIDxwYXRoIGQ9Ik0xMCA3aDQiIC8+CiAgPHBhdGggZD0iTTE4IDEyaDIiIC8+CiAgPHBhdGggZD0iTTE4IDE4aDIiIC8+CiAgPHBhdGggZD0iTTE4IDZoMiIgLz4KICA8cGF0aCBkPSJNNCAxMmgyIiAvPgogIDxwYXRoIGQ9Ik00IDE4aDIiIC8+CiAgPHBhdGggZD0iTTQgNmgyIiAvPgogIDxyZWN0IHg9IjYiIHk9IjIiIHdpZHRoPSIxMiIgaGVpZ2h0PSIyMCIgcng9IjIiIC8+Cjwvc3ZnPg==&logoColor=white" />
    <img src="https://img.shields.io/badge/WinDbg-2D1B69?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXRlcm1pbmFsIgogIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICB3aWR0aD0iMjQiCiAgaGVpZ2h0PSIyNCIKICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgZmlsbD0ibm9uZSIKICBzdHJva2U9IiNmZmZmZmYiCiAgc3Ryb2tlLXdpZHRoPSIyIgogIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICBzdHJva2UtbGluZWpvaW49InJvdW5kIgo+CiAgPHBhdGggZD0iTTEyIDE5aDgiIC8+CiAgPHBhdGggZD0ibTQgMTcgNi02LTYtNiIgLz4KPC9zdmc+&logoColor=white" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>ai</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Claude-D97757?style=for-the-badge&labelColor=06020f&logo=anthropic&logoColor=white" />
    <img src="https://img.shields.io/badge/MCP-F2A6C4?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXdvcmtmbG93IgogIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICB3aWR0aD0iMjQiCiAgaGVpZ2h0PSIyNCIKICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgZmlsbD0ibm9uZSIKICBzdHJva2U9IiMwNjAyMGYiCiAgc3Ryb2tlLXdpZHRoPSIyIgogIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICBzdHJva2UtbGluZWpvaW49InJvdW5kIgo+CiAgPHJlY3Qgd2lkdGg9IjgiIGhlaWdodD0iOCIgeD0iMyIgeT0iMyIgcng9IjIiIC8+CiAgPHBhdGggZD0iTTcgMTF2NGEyIDIgMCAwIDAgMiAyaDQiIC8+CiAgPHJlY3Qgd2lkdGg9IjgiIGhlaWdodD0iOCIgeD0iMTMiIHk9IjEzIiByeD0iMiIgLz4KPC9zdmc+&logoColor=white" />
    <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWJyYWluLWNpcmN1aXQiCiAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iI2ZmZmZmZiIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTIgNWEzIDMgMCAxIDAtNS45OTcuMTI1IDQgNCAwIDAgMC0yLjUyNiA1Ljc3IDQgNCAwIDAgMCAuNTU2IDYuNTg4QTQgNCAwIDEgMCAxMiAxOFoiIC8+CiAgPHBhdGggZD0iTTkgMTNhNC41IDQuNSAwIDAgMCAzLTQiIC8+CiAgPHBhdGggZD0iTTYuMDAzIDUuMTI1QTMgMyAwIDAgMCA2LjQwMSA2LjUiIC8+CiAgPHBhdGggZD0iTTMuNDc3IDEwLjg5NmE0IDQgMCAwIDEgLjU4NS0uMzk2IiAvPgogIDxwYXRoIGQ9Ik02IDE4YTQgNCAwIDAgMS0xLjk2Ny0uNTE2IiAvPgogIDxwYXRoIGQ9Ik0xMiAxM2g0IiAvPgogIDxwYXRoIGQ9Ik0xMiAxOGg2YTIgMiAwIDAgMSAyIDJ2MSIgLz4KICA8cGF0aCBkPSJNMTIgOGg4IiAvPgogIDxwYXRoIGQ9Ik0xNiA4VjVhMiAyIDAgMCAxIDItMiIgLz4KICA8Y2lyY2xlIGN4PSIxNiIgY3k9IjEzIiByPSIuNSIgLz4KICA8Y2lyY2xlIGN4PSIxOCIgY3k9IjMiIHI9Ii41IiAvPgogIDxjaXJjbGUgY3g9IjIwIiBjeT0iMjEiIHI9Ii41IiAvPgogIDxjaXJjbGUgY3g9IjIwIiBjeT0iOCIgcj0iLjUiIC8+Cjwvc3ZnPg==&logoColor=white" />
    <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&labelColor=06020f&logo=ollama&logoColor=white" />
    <img src="https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&labelColor=06020f&logo=playwright&logoColor=white" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>gamedev</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Unity-000000?style=for-the-badge&labelColor=06020f&logo=unity&logoColor=white" />
    <img src="https://img.shields.io/badge/IL2CPP-8A2BE2?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWxheWVycyIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0xMi44MyAyLjE4YTIgMiAwIDAgMC0xLjY2IDBMMi42IDYuMDhhMSAxIDAgMCAwIDAgMS44M2w4LjU4IDMuOTFhMiAyIDAgMCAwIDEuNjYgMGw4LjU4LTMuOWExIDEgMCAwIDAgMC0xLjgzeiIgLz4KICA8cGF0aCBkPSJNMiAxMmExIDEgMCAwIDAgLjU4LjkxbDguNiAzLjkxYTIgMiAwIDAgMCAxLjY1IDBsOC41OC0zLjlBMSAxIDAgMCAwIDIyIDEyIiAvPgogIDxwYXRoIGQ9Ik0yIDE3YTEgMSAwIDAgMCAuNTguOTFsOC42IDMuOTFhMiAyIDAgMCAwIDEuNjUgMGw4LjU4LTMuOUExIDEgMCAwIDAgMjIgMTciIC8+Cjwvc3ZnPg==&logoColor=white" />
    <img src="https://img.shields.io/badge/Mono-C9A84C?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWJveCIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjMDYwMjBmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0yMSA4YTIgMiAwIDAgMC0xLTEuNzNsLTctNGEyIDIgMCAwIDAtMiAwbC03IDRBMiAyIDAgMCAwIDMgOHY4YTIgMiAwIDAgMCAxIDEuNzNsNyA0YTIgMiAwIDAgMCAyIDBsNy00QTIgMiAwIDAgMCAyMSAxNloiIC8+CiAgPHBhdGggZD0ibTMuMyA3IDguNyA1IDguNy01IiAvPgogIDxwYXRoIGQ9Ik0xMiAyMlYxMiIgLz4KPC9zdmc+&logoColor=white" />
    <img src="https://img.shields.io/badge/Photon-F2A6C4?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXJhZGlvIgogIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICB3aWR0aD0iMjQiCiAgaGVpZ2h0PSIyNCIKICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgZmlsbD0ibm9uZSIKICBzdHJva2U9IiMwNjAyMGYiCiAgc3Ryb2tlLXdpZHRoPSIyIgogIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICBzdHJva2UtbGluZWpvaW49InJvdW5kIgo+CiAgPHBhdGggZD0iTTE2LjI0NyA3Ljc2MWE2IDYgMCAwIDEgMCA4LjQ3OCIgLz4KICA8cGF0aCBkPSJNMTkuMDc1IDQuOTMzYTEwIDEwIDAgMCAxIDAgMTQuMTM0IiAvPgogIDxwYXRoIGQ9Ik00LjkyNSAxOS4wNjdhMTAgMTAgMCAwIDEgMC0xNC4xMzQiIC8+CiAgPHBhdGggZD0iTTcuNzUzIDE2LjIzOWE2IDYgMCAwIDEgMC04LjQ3OCIgLz4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIyIiAvPgo8L3N2Zz4=&logoColor=white" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>minecraft</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Paper-2D1B69?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXNjcm9sbCIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0xOSAxN1Y1YTIgMiAwIDAgMC0yLTJINCIgLz4KICA8cGF0aCBkPSJNOCAyMWgxMmEyIDIgMCAwIDAgMi0ydi0xYTEgMSAwIDAgMC0xLTFIMTFhMSAxIDAgMCAwLTEgMXYxYTIgMiAwIDEgMS00IDBWNWEyIDIgMCAxIDAtNCAwdjJhMSAxIDAgMCAwIDEgMWgzIiAvPgo8L3N2Zz4=&logoColor=white" />
    <img src="https://img.shields.io/badge/Spigot-C9A84C?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXNlcnZlciIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjMDYwMjBmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxyZWN0IHdpZHRoPSIyMCIgaGVpZ2h0PSI4IiB4PSIyIiB5PSIyIiByeD0iMiIgcnk9IjIiIC8+CiAgPHJlY3Qgd2lkdGg9IjIwIiBoZWlnaHQ9IjgiIHg9IjIiIHk9IjE0IiByeD0iMiIgcnk9IjIiIC8+CiAgPGxpbmUgeDE9IjYiIHgyPSI2LjAxIiB5MT0iNiIgeTI9IjYiIC8+CiAgPGxpbmUgeDE9IjYiIHgyPSI2LjAxIiB5MT0iMTgiIHkyPSIxOCIgLz4KPC9zdmc+&logoColor=white" />
    <img src="https://img.shields.io/badge/Bukkit-F2A6C4?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWJsb2NrcyIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjMDYwMjBmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0xMCAyMlY3YTEgMSAwIDAgMC0xLTFINGEyIDIgMCAwIDAtMiAydjEyYTIgMiAwIDAgMCAyIDJoMTJhMiAyIDAgMCAwIDItMnYtNWExIDEgMCAwIDAtMS0xSDIiIC8+CiAgPHJlY3QgeD0iMTQiIHk9IjIiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIiAvPgo8L3N2Zz4=&logoColor=white" />
    <img src="https://img.shields.io/badge/Fabric-DBB68F?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWdyaWQtM3gzIgogIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICB3aWR0aD0iMjQiCiAgaGVpZ2h0PSIyNCIKICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgZmlsbD0ibm9uZSIKICBzdHJva2U9IiMwNjAyMGYiCiAgc3Ryb2tlLXdpZHRoPSIyIgogIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICBzdHJva2UtbGluZWpvaW49InJvdW5kIgo+CiAgPHJlY3Qgd2lkdGg9IjE4IiBoZWlnaHQ9IjE4IiB4PSIzIiB5PSIzIiByeD0iMiIgLz4KICA8cGF0aCBkPSJNMyA5aDE4IiAvPgogIDxwYXRoIGQ9Ik0zIDE1aDE4IiAvPgogIDxwYXRoIGQ9Ik05IDN2MTgiIC8+CiAgPHBhdGggZD0iTTE1IDN2MTgiIC8+Cjwvc3ZnPg==&logoColor=white" />
    <img src="https://img.shields.io/badge/Forge-1E2D4B?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWhhbW1lciIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Im0xNSAxMi05LjM3MyA5LjM3M2ExIDEgMCAwIDEtMy4wMDEtM0wxMiA5IiAvPgogIDxwYXRoIGQ9Im0xOCAxNSA0LTQiIC8+CiAgPHBhdGggZD0ibTIxLjUgMTEuNS0xLjkxNC0xLjkxNEEyIDIgMCAwIDEgMTkgOC4xNzJ2LS4zNDRhMiAyIDAgMCAwLS41ODYtMS40MTRsLTEuNjU3LTEuNjU3QTYgNiAwIDAgMCAxMi41MTYgM0g5bDEuMjQzIDEuMjQzQTYgNiAwIDAgMSAxMiA4LjQ4NVYxMGwyIDJoMS4xNzJhMiAyIDAgMCAxIDEuNDE0LjU4NkwxOC41IDE0LjUiIC8+Cjwvc3ZnPg==&logoColor=white" />
    <img src="https://img.shields.io/badge/Mixin-8A2BE2?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXB1enpsZSIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0xNS4zOSA0LjM5YTEgMSAwIDAgMCAxLjY4LS40NzQgMi41IDIuNSAwIDEgMSAzLjAxNCAzLjAxNSAxIDEgMCAwIDAtLjQ3NCAxLjY4bDEuNjgzIDEuNjgyYTIuNDE0IDIuNDE0IDAgMCAxIDAgMy40MTRMMTkuNjEgMTUuMzlhMSAxIDAgMCAxLTEuNjgtLjQ3NCAyLjUgMi41IDAgMSAwLTMuMDE0IDMuMDE1IDEgMSAwIDAgMSAuNDc0IDEuNjhsLTEuNjgzIDEuNjgyYTIuNDE0IDIuNDE0IDAgMCAxLTMuNDE0IDBMOC42MSAxOS42MWExIDEgMCAwIDAtMS42OC40NzQgMi41IDIuNSAwIDEgMS0zLjAxNC0zLjAxNSAxIDEgMCAwIDAgLjQ3NC0xLjY4bC0xLjY4My0xLjY4MmEyLjQxNCAyLjQxNCAwIDAgMSAwLTMuNDE0TDQuMzkgOC42MWExIDEgMCAwIDEgMS42OC40NzQgMi41IDIuNSAwIDEgMCAzLjAxNC0zLjAxNSAxIDEgMCAwIDEtLjQ3NC0xLjY4bDEuNjgzLTEuNjgyYTIuNDE0IDIuNDE0IDAgMCAxIDMuNDE0IDB6IiAvPgo8L3N2Zz4=&logoColor=white" />
    <img src="https://img.shields.io/badge/Gradle-02303A?style=for-the-badge&labelColor=06020f&logo=gradle&logoColor=white" />
    <img src="https://img.shields.io/badge/LWJGL-F2A6C4?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWdhbWVwYWQtMiIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjMDYwMjBmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxsaW5lIHgxPSI2IiB4Mj0iMTAiIHkxPSIxMSIgeTI9IjExIiAvPgogIDxsaW5lIHgxPSI4IiB4Mj0iOCIgeTE9IjkiIHkyPSIxMyIgLz4KICA8bGluZSB4MT0iMTUiIHgyPSIxNS4wMSIgeTE9IjEyIiB5Mj0iMTIiIC8+CiAgPGxpbmUgeDE9IjE4IiB4Mj0iMTguMDEiIHkxPSIxMCIgeTI9IjEwIiAvPgogIDxwYXRoIGQ9Ik0xNy4zMiA1SDYuNjhhNCA0IDAgMCAwLTMuOTc4IDMuNTljLS4wMDYuMDUyLS4wMS4xMDEtLjAxNy4xNTJDMi42MDQgOS40MTYgMiAxNC40NTYgMiAxNmEzIDMgMCAwIDAgMyAzYzEgMCAxLjUtLjUgMi0xbDEuNDE0LTEuNDE0QTIgMiAwIDAgMSA5LjgyOCAxNmg0LjM0NGEyIDIgMCAwIDEgMS40MTQuNTg2TDE3IDE4Yy41LjUgMSAxIDIgMWEzIDMgMCAwIDAgMy0zYzAtMS41NDUtLjYwNC02LjU4NC0uNjg1LTcuMjU4LS4wMDctLjA1LS4wMTEtLjEtLjAxNy0uMTUxQTQgNCAwIDAgMCAxNy4zMiA1eiIgLz4KPC9zdmc+&logoColor=white" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>hardware</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Flipper_Zero-FF8300?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXJhZGlvIgogIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICB3aWR0aD0iMjQiCiAgaGVpZ2h0PSIyNCIKICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgZmlsbD0ibm9uZSIKICBzdHJva2U9IiNmZmZmZmYiCiAgc3Ryb2tlLXdpZHRoPSIyIgogIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICBzdHJva2UtbGluZWpvaW49InJvdW5kIgo+CiAgPHBhdGggZD0iTTE2LjI0NyA3Ljc2MWE2IDYgMCAwIDEgMCA4LjQ3OCIgLz4KICA8cGF0aCBkPSJNMTkuMDc1IDQuOTMzYTEwIDEwIDAgMCAxIDAgMTQuMTM0IiAvPgogIDxwYXRoIGQ9Ik00LjkyNSAxOS4wNjdhMTAgMTAgMCAwIDEgMC0xNC4xMzQiIC8+CiAgPHBhdGggZD0iTTcuNzUzIDE2LjIzOWE2IDYgMCAwIDEgMC04LjQ3OCIgLz4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIyIiAvPgo8L3N2Zz4=&logoColor=white" />
    <img src="https://img.shields.io/badge/ESP32--S3-E7352C?style=for-the-badge&labelColor=06020f&logo=espressif&logoColor=white" />
    <img src="https://img.shields.io/badge/Soldering_Iron-C9A84C?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXphcCIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjMDYwMjBmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik00IDE0YTEgMSAwIDAgMS0uNzgtMS42M2w5LjktMTAuMmEuNS41IDAgMCAxIC44Ni40NmwtMS45MiA2LjAyQTEgMSAwIDAgMCAxMyAxMGg3YTEgMSAwIDAgMSAuNzggMS42M2wtOS45IDEwLjJhLjUuNSAwIDAgMS0uODYtLjQ2bDEuOTItNi4wMkExIDEgMCAwIDAgMTEgMTR6IiAvPgo8L3N2Zz4=&logoColor=white" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>desktop</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Electron-47848F?style=for-the-badge&labelColor=06020f&logo=electron&logoColor=white" />
    <img src="https://img.shields.io/badge/Tauri-24C8DB?style=for-the-badge&labelColor=06020f&logo=tauri&logoColor=white" />
    <img src="https://img.shields.io/badge/Qt-41CD52?style=for-the-badge&labelColor=06020f&logo=qt&logoColor=white" />
    <img src="https://img.shields.io/badge/PySide6-3776AB?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWFwcC13aW5kb3ciCiAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iI2ZmZmZmZiIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cmVjdCB4PSIyIiB5PSI0IiB3aWR0aD0iMjAiIGhlaWdodD0iMTYiIHJ4PSIyIiAvPgogIDxwYXRoIGQ9Ik0xMCA0djQiIC8+CiAgPHBhdGggZD0iTTIgOGgyMCIgLz4KICA8cGF0aCBkPSJNNiA0djQiIC8+Cjwvc3ZnPg==&logoColor=white" />
    <img src="https://img.shields.io/badge/WebView2-0078D6?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWdsb2JlIgogIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICB3aWR0aD0iMjQiCiAgaGVpZ2h0PSIyNCIKICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgZmlsbD0ibm9uZSIKICBzdHJva2U9IiNmZmZmZmYiCiAgc3Ryb2tlLXdpZHRoPSIyIgogIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICBzdHJva2UtbGluZWpvaW49InJvdW5kIgo+CiAgPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiIC8+CiAgPHBhdGggZD0iTTEyIDJhMTQuNSAxNC41IDAgMCAwIDAgMjAgMTQuNSAxNC41IDAgMCAwIDAtMjAiIC8+CiAgPHBhdGggZD0iTTIgMTJoMjAiIC8+Cjwvc3ZnPg==&logoColor=white" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>web</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&labelColor=06020f&logo=react&logoColor=black" />
    <img src="https://img.shields.io/badge/Vue-4FC08D?style=for-the-badge&labelColor=06020f&logo=vuedotjs&logoColor=white" />
    <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&labelColor=06020f&logo=vite&logoColor=white" />
    <img src="https://img.shields.io/badge/MUI-007FFF?style=for-the-badge&labelColor=06020f&logo=mui&logoColor=white" />
    <img src="https://img.shields.io/badge/Tailwind-06B6D4?style=for-the-badge&labelColor=06020f&logo=tailwindcss&logoColor=white" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>backend</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Spring-6DB33F?style=for-the-badge&labelColor=06020f&logo=spring&logoColor=white" />
    <img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&labelColor=06020f&logo=nodedotjs&logoColor=white" />
    <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&labelColor=06020f&logo=mysql&logoColor=white" />
    <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&labelColor=06020f&logo=redis&logoColor=white" />
    <img src="https://img.shields.io/badge/Nginx-009639?style=for-the-badge&labelColor=06020f&logo=nginx&logoColor=white" />
    <img src="https://img.shields.io/badge/Cloudflare-F38020?style=for-the-badge&labelColor=06020f&logo=cloudflare&logoColor=white" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>archive</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/5853_days_uptime-F2A6C4?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNsb2NrIgogIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICB3aWR0aD0iMjQiCiAgaGVpZ2h0PSIyNCIKICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgZmlsbD0ibm9uZSIKICBzdHJva2U9IiMwNjAyMGYiCiAgc3Ryb2tlLXdpZHRoPSIyIgogIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICBzdHJva2UtbGluZWpvaW49InJvdW5kIgo+CiAgPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiIC8+CiAgPHBhdGggZD0iTTEyIDZ2Nmw0IDIiIC8+Cjwvc3ZnPg==&logoColor=white" />
    <img src="https://img.shields.io/badge/still_learning-2D1B69?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWJvb2stb3BlbiIKICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgd2lkdGg9IjI0IgogIGhlaWdodD0iMjQiCiAgdmlld0JveD0iMCAwIDI0IDI0IgogIGZpbGw9Im5vbmUiCiAgc3Ryb2tlPSIjZmZmZmZmIgogIHN0cm9rZS13aWR0aD0iMiIKICBzdHJva2UtbGluZWNhcD0icm91bmQiCiAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKPgogIDxwYXRoIGQ9Ik0xMiA3djE0IiAvPgogIDxwYXRoIGQ9Ik0zIDE4YTEgMSAwIDAgMS0xLTFWNGExIDEgMCAwIDEgMS0xaDVhNCA0IDAgMCAxIDQgNCA0IDQgMCAwIDEgNC00aDVhMSAxIDAgMCAxIDEgMXYxM2ExIDEgMCAwIDEtMSAxaC02YTMgMyAwIDAgMC0zIDMgMyAzIDAgMCAwLTMtM3oiIC8+Cjwvc3ZnPg==&logoColor=white" />
    <img src="https://img.shields.io/badge/will_never_know_enough-C9A84C?style=for-the-badge&labelColor=06020f&logo=data:image/svg%2Bxml;base64,PHN2ZwogIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWluZmluaXR5IgogIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICB3aWR0aD0iMjQiCiAgaGVpZ2h0PSIyNCIKICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgZmlsbD0ibm9uZSIKICBzdHJva2U9IiMwNjAyMGYiCiAgc3Ryb2tlLXdpZHRoPSIyIgogIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICBzdHJva2UtbGluZWpvaW49InJvdW5kIgo+CiAgPHBhdGggZD0iTTYgMTZjNSAwIDctOCAxMi04YTQgNCAwIDAgMSAwIDhjLTUgMC03LTgtMTItOGE0IDQgMCAxIDAgMCA4IiAvPgo8L3N2Zz4=&logoColor=white" />
  </td>
</tr>
</table>

. s h o u t o u t s .

to every anon who kept pushing commits with zero stars and zero watchers  
to every kid who built something just to see if it could be done

— dwgx, kobe

---

### `stats`

<div align="center">

<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/metrics.svg" width="80%" alt="metrics dashboard" />

<br/><br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats-sigma-five.vercel.app/api?username=DWGX&show_icons=true&hide_border=true&bg_color=06020f&title_color=f2a6c4&icon_color=c9a84c&text_color=d4c8ef&ring_color=f2a6c4" />
  <img height="170" src="https://github-readme-stats-sigma-five.vercel.app/api?username=DWGX&show_icons=true&hide_border=true&bg_color=06020f&title_color=f2a6c4&icon_color=c9a84c&text_color=d4c8ef&ring_color=f2a6c4" />
</picture>
&nbsp;&nbsp;
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://streak-stats.demolab.com/?user=DWGX&hide_border=true&background=06020F&stroke=2d1b69&ring=f2a6c4&fire=c9a84c&currStreakLabel=f2a6c4&sideLabels=d4c8ef&currStreakNum=d4c8ef&sideNums=d4c8ef&dates=8a7aaa" />
  <img height="170" src="https://streak-stats.demolab.com/?user=DWGX&hide_border=true&background=06020F&stroke=2d1b69&ring=f2a6c4&fire=c9a84c&currStreakLabel=f2a6c4&sideLabels=d4c8ef&currStreakNum=d4c8ef&sideNums=d4c8ef&dates=8a7aaa" />
</picture>

<br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats-sigma-five.vercel.app/api/top-langs/?username=DWGX&layout=compact&hide_border=true&bg_color=06020f&title_color=f2a6c4&text_color=d4c8ef" />
  <img height="160" src="https://github-readme-stats-sigma-five.vercel.app/api/top-langs/?username=DWGX&layout=compact&hide_border=true&bg_color=06020f&title_color=f2a6c4&text_color=d4c8ef" />
</picture>
&nbsp;&nbsp;
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=DWGX&theme=github_dark&utcOffset=9" />
  <img height="160" src="https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=DWGX&theme=github_dark&utcOffset=9" />
</picture>

</div>

---

### `achievements`

<div align="center">

<img src="https://img.shields.io/badge/★-Solo_Crew-f2a6c4?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-IL2CPP_Diver-c9a84c?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Starstruck_2.8k-ed8b00?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Pull_Shark-3178c6?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Quickdraw-d01c1f?style=for-the-badge&labelColor=06020f" />

<br/>

<img src="https://img.shields.io/badge/★-Cheat_Scene_Alumnus-2d1b69?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Flipper_Hacker-ff8300?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Paper_Plugin_Dev-6db33f?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Live2D_Pet_Maker-ff66aa?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-5853_Days_Uptime-8a7aaa?style=for-the-badge&labelColor=06020f" />

</div>

---

### `3d.contrib`

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dwgx/DWGX/main/profile-3d-contrib/profile-night-rainbow.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/dwgx/DWGX/main/profile-3d-contrib/profile-season.svg" />
  <img src="https://raw.githubusercontent.com/dwgx/DWGX/main/profile-3d-contrib/profile-season.svg" width="100%" alt="3d contribution" />
</picture>

</div>

---

### `summary.cards`

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=DWGX&theme=nord_dark" />
  <img height="175" src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=DWGX&theme=nord_dark" />
</picture>
&nbsp;
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=DWGX&theme=nord_dark" />
  <img height="175" src="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=DWGX&theme=nord_dark" />
</picture>

<br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=DWGX&theme=nord_dark&exclude=html,css" />
  <img height="175" src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=DWGX&theme=nord_dark&exclude=html,css" />
</picture>
&nbsp;
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/most-commit-language?username=DWGX&theme=nord_dark" />
  <img height="175" src="https://github-profile-summary-cards.vercel.app/api/cards/most-commit-language?username=DWGX&theme=nord_dark" />
</picture>

</div>

---

### `contribution.snake`

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dwgx/DWGX/output/github-contribution-grid-snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/dwgx/DWGX/output/github-contribution-grid-snake.svg" />
  <img alt="dwgx contribution snake" src="https://raw.githubusercontent.com/dwgx/DWGX/output/github-contribution-grid-snake.svg" width="100%" />
</picture>

</div>

---

<!-- ════════════════════════════════════════════════════════════════ -->
<!--  ledger — quote / motto fragment                                 -->
<!-- ════════════════════════════════════════════════════════════════ -->

<div align="center">

```
    ╭───────────────────────────────────────────────────────────╮
    │                                                           │
    │                   be   water   my   friend.               │
    │                                                           │
    ╰───────────────────────────────────────────────────────────╯
```

</div>

---

### `hex.dump`

```
 00401000  e5 b8 9d e7 8e 8b e5 b0   ac e7 ac 91 00 00 00 00   帝王尬笑....
 00401010  64 77 67 78 40 6b 6f 62   65 3a 7e 2f 64 65 76 24   dwgx@kobe:~/dev$
 00401020  72 65 76 65 72 73 65 2e   65 6e 67 69 6e 65 65 72   reverse.engineer
 00401030  67 61 6d 65 20 68 61 63   6b 69 6e 67 20 73 79 73   game hacking sys
 00401040  62 65 20 77 61 74 65 72   20 6d 79 20 66 72 69 65   be water my frie
 00401050  6e 64 20 2f 2f 20 73 6f   6c 6f 20 20 63 72 65 77   nd // solo  crew
 00401060  69 6e 64 65 70 20 73 69   6e 63 65 20 32 30 31 30   indep since 2010
```

---

### `hotkeys`

<div align="center">

<kbd>F1</kbd> [dwgx.github.io](https://dwgx.github.io)
&nbsp;&nbsp;·&nbsp;&nbsp;
<kbd>F2</kbd> [YouTube](https://www.youtube.com/@dwgx1337)
&nbsp;&nbsp;·&nbsp;&nbsp;
<kbd>F3</kbd> [Bilibili](https://space.bilibili.com/1452905012)
&nbsp;&nbsp;·&nbsp;&nbsp;
<kbd>F4</kbd> [QQ](https://user.qzone.qq.com/136666451/)

</div>

---

<div align="center">

<img src="https://github-readme-activity-graph.vercel.app/graph?username=DWGX&bg_color=06020f&color=f2a6c4&line=c9a84c&point=f2a6c4&area=true&area_color=2d1b69&hide_border=true&custom_title=archive.activity" width="95%" />

</div>

```
 ─── dwgx@kobe ── JST+9 ── mode: archive ── uptime 5853d ── be water ───
```

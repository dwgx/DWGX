<!-- ════════════════════════════════════════════════════════════════ -->
<!--  dwgx.menu  v2.0                                                 -->
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

</div>

---

### `main.cfg`

```ini
; dwgx.cfg  —  last modified 2026-04-21 JST
; injection status: active  ·  process.count: 10

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
active     = java · cpp · csharp · swift · typescript · python · go
previous   = js · php
```

---

### `process.table`

```
 PID    MODULE                   ADDR             LANG    STATUS
 ──────────────────────────────────────────────────────────────────────────────
 0001   vrchat-il2cpp-re         0x7FF6A4010000   c#      ▓▓▓▓▓▓▓▓▓░  97.7% deobf
 0002   VRCSM                    0x7FF6A40AB000   ts      ▓▓▓▓▓▓▓░░░  cache.mgr
 0003   WindsurfAPI              0x7FF6A40FF000   js      LISTENING  :8080  ★199
 0004   skiapi-frontend          0x7FF6A4180000   js      ADMIN-UI  MUI.console
 0005   RepoDLL                  0x7FF6A4220000   cpp     HOOKED  Present()  ★10
 0006   Rep0S2cLeak              0x7FF6A42D0000   c#      LEAKED  src.dumped
 0007   Lavender-rise-main       0x7FF6A4350000   java    MC-1.21  cheat-client
 0008   OpenNative               0x7FF6A4400000   cpp     NATIVE-HOOK  dx11.vtbl
 0009   flipper-custom-apps      0x7FF6A4480000   c       ESP32-BOOST  ble-spam
 0010   FlipperZeroTeacher       0x7FF6A4520000   html    雙語教學.知識庫
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
║ 42,000 classes         ║
║ 97.7% deobfuscated     ║
║ Photon protocol RE     ║
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
║ WindsurfAPI            ║
╠════════════════════════╣
║                        ║
║ Windsurf ⇄ OpenAI      ║
║ 59+ free models        ║
║ load-balancing proxy   ║
║                        ║
║ lang  · JavaScript     ║
║ stage · popular  ★199  ║
║ diff  · ★★☆☆☆          ║
╚════════════════════════╝
```

[open module →](https://github.com/dwgx/WindsurfAPI)

</td>
</tr>
</table>

</div>

---

### `recent.log`

```
 2026-04-20 11:27   push  WindsurfAPI           ★199   js     windsurf ⇄ openai proxy
 2026-04-19 13:19   push  VRCSM                 ★1     ts     vrchat cache/settings manager
 2026-04-16 13:50   push  vrchat-il2cpp-re      ★1     c#     97.7% deobf · 42k classes
 2026-04-15 10:44   push  RepoDLL               ★10    cpp    dx11+imgui · mono reflection
 2026-04-19 13:23   push  cs2-walkbot-ext       ★1     c      windmouse+fitts · imgui overlay
 2026-04-16 06:56   push  blender-copilot       ★1     py     blender mcp · 70+ tools
 2026-04-20 11:22   push  VRC-Auto-Uploader     ★1     py     unity batchmode · avatar pipeline
 2026-04-20 11:24   push  flipper-custom-apps   ★1     c      ble-spam + esp32 dual-radio
 2026-04-15 10:44   push  YuKiKo                ★19    py     skiapi backend engine
 2026-04-15 10:44   push  Wechathacker          ★2     -      wxid binary-search tool
```

<details>
<summary><code>archive.log  — +14 older entries</code></summary>

```
 2026-04-20 11:26   push  Live2DPet             ★1     js     ai live2d + voicevox pet
 2026-04-20 11:26   push  claude-gemini-subagent ★1    sh     claude-code subagent bridge
 2026-04-15 10:52   push  claude-codex-subagent ★1     sh     claude→codex worker subagent
 2026-04-15 10:53   push  FlipperZeroTeacher    ★1     html   flipper 雙語教學知識庫
 2026-04-15 10:52   push  dev-history           ★1     -      項目檔案 · 開發日曆
 2026-04-15 10:52   push  blog                  ★1     md     personal markdown blog
 2026-04-18 12:52   push  dwgx.github.io        ★1     html   personal site
 2026-04-15 11:34   push  skiapi-frontend       ★1     js     newapi admin console · MUI
 2026-04-10 09:18   push  strict                ★1     java   minecraft 1.21.3 anti-cheat
 2026-04-10 09:17   push  CleanerKing           ★1     java   host-machine accelerator
 2026-04-10 09:16   push  darkpixel             ★1     java   1.21.4 paper-plugin
 2026-03-21 11:50   push  Rep0S2cLeak           ★1     c#     repo leaked src
 2026-03-21 11:50   push  ToolBox               ★2     py     good toolbox
 2026-03-08 23:18   push  QQbot                 ★1     py     tencent bot python lib
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
               │  uptime     5768 days                          │
               │  status     online · JST+9                     │
               ╰────────────────────────────────────────────────╯
```

---

<div align="center">

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

```
                              . d w g x . p r e s e n t s .
 ████████████████████████████████████████████████████████████████████████████
 ██                                                                        ██
 ██      d w g x . m e n u      ·      v 2 . 1      ·      2 0 2 6         ██
 ██                                                                        ██
 ██              scene release // kobe, jp // solo crew                    ██
 ██                                                                        ██
 ████████████████████████████████████████████████████████████████████████████

 ┌──────────────────────────────────────────────────────────────────────────┐
 │  ▌  group      dwgx                                                      │
 │  ▌  location   kobe · jp  ·  jst +9                                      │
 │  ▌  release    personal-profile.v2.1                                     │
 │  ▌  files      1 readme.md  +  2 assets                                  │
 │  ▌  size       ≈ 1.8 mb  (gif-heavy)                                     │
 │  ▌  target     github.com/dwgx                                           │
 │  ▌  supplier   15yo indep dev · minecraft cheat scene origin             │
 │  ▌  date       2026.04.21                                                │
 └──────────────────────────────────────────────────────────────────────────┘
```

<div align="center">

### `▓▒░  [ stack.manifest ]  ░▒▓`

<img src="https://skillicons.dev/icons?i=java,spring,kotlin,cpp,cmake,cs,swift,ts,py,go,mysql,redis,nginx,cloudflare,nodejs,docker&perline=16" />

</div>

<table align="center" width="100%">
<tr>
  <td align="right" width="110"><code><b>jvm</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Java_21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Paper_Plugin-F2A6C4?style=for-the-badge&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Spring_Boot-6DB33F?style=for-the-badge&logo=springboot&logoColor=white&labelColor=06020f" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>native</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/C++_20-00599C?style=for-the-badge&logo=cplusplus&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/CMake-064F8C?style=for-the-badge&logo=cmake&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Dear_ImGui-2D1B69?style=for-the-badge&labelColor=06020f" />
    <img src="https://img.shields.io/badge/DirectX_11-76B900?style=for-the-badge&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Win32-0078D6?style=for-the-badge&logo=windows&logoColor=white&labelColor=06020f" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>managed</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/C%23-239120?style=for-the-badge&logo=csharp&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Swift-FA7343?style=for-the-badge&logo=swift&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white&labelColor=06020f" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>reverse</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/IDA_Pro-C9A84C?style=for-the-badge&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Ghidra-FF6E00?style=for-the-badge&labelColor=06020f" />
    <img src="https://img.shields.io/badge/x64dbg-1E90FF?style=for-the-badge&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Il2CppDumper-8A2BE2?style=for-the-badge&labelColor=06020f" />
    <img src="https://img.shields.io/badge/dnSpy-4B4B4B?style=for-the-badge&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Cheat_Engine-D01C1F?style=for-the-badge&labelColor=06020f" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>ai</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Claude-D97757?style=for-the-badge&logo=anthropic&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/MCP-F2A6C4?style=for-the-badge&labelColor=06020f" />
    <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Live2D-FF66AA?style=for-the-badge&labelColor=06020f" />
    <img src="https://img.shields.io/badge/VOICEVOX-4EA64E?style=for-the-badge&labelColor=06020f" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>hardware</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Flipper_Zero-FF8300?style=for-the-badge&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/ESP32--S3-E7352C?style=for-the-badge&logo=espressif&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Soldering_Iron-C9A84C?style=for-the-badge&labelColor=06020f" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>backend</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/Spring-6DB33F?style=for-the-badge&logo=spring&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white&labelColor=06020f" />
    <img src="https://img.shields.io/badge/Cloudflare-F38020?style=for-the-badge&logo=cloudflare&logoColor=white&labelColor=06020f" />
  </td>
</tr>
<tr>
  <td align="right"><code><b>archive</b></code></td>
  <td>
    <img src="https://img.shields.io/badge/5768_days_uptime-F2A6C4?style=for-the-badge&labelColor=06020f" />
    <img src="https://img.shields.io/badge/still_learning-2D1B69?style=for-the-badge&labelColor=06020f" />
    <img src="https://img.shields.io/badge/will_never_know_enough-C9A84C?style=for-the-badge&labelColor=06020f" />
  </td>
</tr>
</table>

```
 ▓▒░  [ shoutouts ]  ░▒▓─────────────────────────────────────────────────────

    to every kid who traced a decompiled class at 3 am
    to every anon who dropped a repo and walked away without credit
    to the cat who sleeps on my mechanical keyboard

    — dwgx, kobe
```

---

### `stats`

<div align="center">

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

### `trophies`

<div align="center">

<img src="https://github-profile-trophy.vercel.app/?username=DWGX&theme=radical&no-frame=true&no-bg=true&margin-w=6&row=1&column=7&rank=SECRET,SSS,SS,S,AAA,AA,A" />

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
<!--  archive drawer — handwritten ledger style                       -->
<!-- ════════════════════════════════════════════════════════════════ -->

```
 ╔══════════════════════════════════════════════════════════════════════════╗
 ║   档 案 抽 屉     ·     archive drawer     ·     drawer no. 01          ║
 ╠══════════════════════════════════════════════════════════════════════════╣
 ║                                                                          ║
 ║   [ 01 ]   2010  ·  —        始点                · kobe, jp             ║
 ║   [ 02 ]   ····  ·  —        minecraft cheat scene · first compile      ║
 ║   [ 03 ]   ····  ·  —        paper-plugin · anti-cheat                  ║
 ║   [ 04 ]   ····  ·  —        esp32-s3 · flipper zero · ble-spam         ║
 ║   [ 05 ]   ····  ·  —        vrchat il2cpp diving begin                 ║
 ║   [ 06 ]   ····  ·  —        skiapi · backend / frontend                ║
 ║   [ 07 ]   2026  ·  apr      WindsurfAPI ★200 milestone                 ║
 ║   [ 08 ]   2026  ·  apr      vrchat-il2cpp-re 97.7% deobf  ·  42k cls   ║
 ║   [ 09 ]   2026  ·  apr      VRCSM · RepoDLL · flipper-custom-apps      ║
 ║   [ 10 ]   2026  ·  apr      dwgx.menu v2.1 rebuild                     ║
 ║   [ 11 ]   ....  ·  —        still writing                              ║
 ║                                                                          ║
 ║                                       ─────── drawer.sealed ───────      ║
 ╚══════════════════════════════════════════════════════════════════════════╝
```

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
 00401000  e5 b8 9d e7 8e 8b e5 b0   ac e7 ac 91 00 00 00 00   帝王尬笑........
 00401010  64 77 67 78 40 6b 6f 62   65 3a 7e 24 00 00 00 00   dwgx@kobe:~$....
 00401020  62 65 20 77 61 74 65 72   2c 20 6d 79 20 66 72 69   be water, my fri
 00401030  2f 68 6f 6d 65 2f 6b 6f   62 65 2f 2e 64 77 67 78   /home/kobe/.dwgx
 00401040  2f 70 65 72 73 6f 6e 61   2e 64 61 74 00 00 00 00   /persona.dat....
 00401050  69 6e 64 65 70 20 64 65   76 20 2f 2f 20 31 35 79   indep dev // 15y
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
 ─── dwgx@kobe ── JST+9 ── mode: archive ── uptime 5768d ── be water ───
```

<img width="100%" src="https://capsule-render.vercel.app/api?type=soft&color=0:f2a6c4,30:2d1b69,60:1a0a3e,100:06020f&height=100&section=footer&text=&fontSize=0" />

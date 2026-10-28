# 生产环境：永不熄灭的服务器

四章连载技术小说。跟随 Java 后端工程师林川与技术负责人陈默，在事故现场学习 CPU、内存、线程与 MySQL 问题的判断、止血、定位和复盘。第五章“无法提交的事务——MySQL 锁战争”仅保留预告。

- [在线阅读](https://wupzl.github.io/online-troubleshooting-reader/)
- [全书 Markdown 导航](chapters/00-全书导航.md)
- [学习书架](https://wupzl.github.io/)
- [整理说明与技术参考](EDITORIAL.md)

沿用 AI 纪元阅读器的布局：章内目录、上下章切换、字号调整、纯白 / 米白 / 深色背景，支持手机和桌面，无需登录。橙红色主题，20 张本地 SVG 图表，6 组明确标注的模拟趋势与可下载 CSV，无运行时 CDN、框架或后端依赖。

## 构建与预览

```bash
python -m pip install -r requirements.txt
python build.py
python -m http.server 4176 --directory docs --bind 127.0.0.1
```

打开 http://127.0.0.1:4176/。日常编辑 `chapters/01.md` 等正文、`book.json` 和 `assets/`，再执行构建。原稿保存在 `source/original.md`；首次导入脚本不会覆盖已有章节。图表重新生成另需 Matplotlib 和中文字体，参见整理说明。

## 验证

```bash
python -m pip install -r requirements-test.txt
python -m playwright install chromium
python verify.py
```

检查原稿存档、四章正文边界、章节完整性、资源与锚点、SVG、390 / 768 / 1440px 布局、字号、三种背景持久化及预告导航。截图在 `test-results/`。

六个项目同级放置时，在共同父目录执行 `python bookshelf/verify.py`，检查书架、所有页面和跨项目导航。

## 发布与续章

GitHub Pages 从 `main` 分支 `/docs` 发布。新增章节时更新 `book.json`、正文与预告、连载说明及学习书架章节数，再构建与验证。所有页面保留返回书架及六项目切换入口；布局和阅读交互沿用同一书架中的阅读器。


项目切换菜单已接入 [Agent 帝国：代码审判者](https://wupzl.github.io/coding-agent-reader/)，九章小说式 Coding Agent 工程阅读。


项目切换菜单已接入 [面试官的审判](https://wupzl.github.io/interview-proof-reader/)，七章技术面试小说与七组本地训练，第八章待续。

"""Add this reader to sibling navigation and the existing learning bookshelf, idempotently."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SLUG = 'online-troubleshooting-reader'
LINK = f'<a href="/{SLUG}/">生产环境</a>'
READERS = ['pytorch-apprentice', 'ai-era-reader', 'data-empire-reader', 'rag-empire-reader', 'system-design-reader']


def edit(path, transform):
    original = path.read_text(encoding='utf-8')
    updated = transform(original)
    if original != updated:
        path.write_text(updated, encoding='utf-8')


def add_menu(text):
    def add(match):
        content = match[1]
        return match[0] if f'/{SLUG}/' in content else f'<div class="shelf-menu">{content}{LINK}</div>'
    return re.sub(r'<div class="shelf-menu">(.*?)</div>', add, text, flags=re.S)


def add_project_tuple(text):
    if f"('{SLUG}'" in text:
        return text
    for item in ["('system-design-reader', '系统设计')", "('system-design-reader','系统设计')"]:
        if item in text:
            return text.replace(item, item + f", ('{SLUG}', '生产环境')", 1)
    raise AssertionError('Missing project list')


def main():
    for slug in READERS:
        project = ROOT / slug
        for path in (project / 'docs').glob('*.html'):
            edit(path, add_menu)
        build = project / 'build.py'
        if build.exists():
            edit(build, add_menu if slug == 'pytorch-apprentice' else add_project_tuple)
    edit(ROOT / 'system-design-reader/verify.py', lambda s: s.replace("page.locator('.shelf-menu a').count() == 5", "page.locator('.shelf-menu a').count() == 6"))
    edit(ROOT / 'system-design-reader/README.md', lambda s: s.replace('五项目切换入口', '六项目切换入口'))
    shelf = ROOT / 'bookshelf'
    card = '''<a class="project incident" href="/online-troubleshooting-reader/"><div class="cover" aria-hidden="true"><span class="volume">06 / ALWAYS ON</span><strong>生产环境<span class="cover-subtitle">永不熄灭的服务器</span></strong><span class="symbol">!</span><span class="cover-foot">观察 · 止血 · 定位 · 复盘</span></div><div class="project-copy"><p class="category">JAVA 线上排查 · 技术小说</p><h3>生产环境：永不熄灭的服务器</h3><p>跟随林川与陈默，沿着 CPU、内存、线程和慢 SQL 的线索，学会从告警判断影响、恢复服务并找到根因。</p><div class="tags"><span>4 章 · 第五章待续</span><span class="project-status">连载</span><span>20 张本地图表</span></div><span class="enter">进入阅读 <span aria-hidden="true">↗</span></span></div></a>'''

    def add_card(text):
        if f'/{SLUG}/' not in text:
            marker = '</div><div class="shelf-note">'
            assert marker in text
            text = text.replace(marker, card + marker, 1)
        return text.replace('05 / 持续更新', '06 / 持续更新')
    edit(shelf / 'index.html', add_card)
    edit(shelf / 'bookshelf.css', lambda s: s if '.incident .cover' in s else s+'\n.incident .cover{background:#a53d24;color:#fff2df}.incident .symbol{font-style:normal;right:50px}\n')
    edit(shelf / 'verify.py', lambda s: s.replace('five', 'six').replace("    'system-design-reader': '连载',", "    'system-design-reader': '连载',\n    'online-troubleshooting-reader': '连载',") if "    'online-troubleshooting-reader': '连载'," not in s else s)
    workflow = shelf / '.github/workflows/verify-readers.yml'

    def ci(text):
        if 'repository: wupzl/online-troubleshooting-reader' not in text:
            marker = '      - uses: actions/setup-python@v5'
            text = text.replace(marker, '      - uses: actions/checkout@v4\n        with:\n          repository: wupzl/online-troubleshooting-reader\n          ref: main\n          path: online-troubleshooting-reader\n' + marker, 1)
            marker = '      - name: Verify system design reader'
            text = text.replace(marker, '      - name: Verify production troubleshooting reader\n        run: python online-troubleshooting-reader/verify.py\n' + marker, 1)
            text = text.replace('            system-design-reader/test-results/', '            system-design-reader/test-results/\n            online-troubleshooting-reader/test-results/')
        return text.replace('all five readers', 'all six readers')
    edit(workflow, ci)
    edit(shelf / 'README.md', lambda s: s.replace('RAG 帝国和系统设计五个阅读项目', 'RAG 帝国、系统设计和生产环境六个阅读项目').replace('系统设计 8 章（连载，第九章待续）。', '系统设计 8 章（连载，第九章待续）、生产环境 4 章（连载，第五章待续）。').replace('其余五个仓库', '其余六个仓库').replace('`system-design-reader/` 目录中', '`system-design-reader/`、`online-troubleshooting-reader/` 目录中').replace('五项目切换菜单', '六项目切换菜单').replace('五个阅读仓库', '六个阅读仓库').replace('与 PyTorch 完整验收', '、生产环境阅读验收与 PyTorch 完整验收'))
    print('Updated six-project navigation, bookshelf card, source generators and shared verification workflow.')


if __name__ == '__main__':
    main()

"""Create local SVG diagrams and reproducible illustrative charts; not a production benchmark."""
from pathlib import Path
import csv
import html
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/diagrams'
DATA = ROOT / 'assets/data'
OUT.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)


def escape(value):
    return html.escape(value, quote=True)


def flow(name, title, rows, subtitle='工程示意 · 按证据分析，结合实际配置验证', arrows=True):
    width, gap, margin, row_height = 900, 18, 32, 126
    height = 125 + len(rows) * row_height
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
           f'<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle + '。' + '；'.join(' / '.join(a + '：' + b for a,b in row) for row in rows))}</desc>',
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#a44b32"/></marker></defs>',
           '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif;fill:#302b28}.detail{font-size:15px;fill:#69605b}.title{font-size:25px;font-weight:700}.label{font-size:19px;font-weight:650}</style>',
           f'<rect width="900" height="{height}" rx="12" fill="#fffaf4"/>',
           f'<text x="32" y="44" class="title">{escape(title)}</text>',
           f'<text x="32" y="76" class="detail">{escape(subtitle)}</text>']
    previous = []
    for r, row in enumerate(rows):
        card_width = (width - margin*2 - gap*(len(row)-1)) / len(row)
        current = []
        y = 108 + r*row_height
        for c, (label, detail) in enumerate(row):
            x = margin + c*(card_width+gap)
            center = x + card_width/2
            if arrows and previous:
                for px in previous:
                    if len(previous) == 1 or len(row) == 1 or abs(px-center) < 1:
                        svg.append(f'<path d="M{px} {y-28} L{center} {y-4}" stroke="#a44b32" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
            svg.append(f'<rect x="{x}" y="{y}" width="{card_width}" height="96" rx="7" fill="#fff" stroke="#e1cec0"/>')
            svg.append(f'<text x="{center}" y="{y+30}" text-anchor="middle" class="label">{escape(label)}</text>')
            lines = textwrap.wrap(detail, width=max(10, int(card_width/16)-2))
            for k, line in enumerate(lines[:2]):
                svg.append(f'<text x="{center}" y="{y+56+k*22}" text-anchor="middle" class="detail">{escape(line)}</text>')
            current.append(center)
        previous = current
    svg.append('</svg>')
    (OUT / f'{name}.svg').write_text('\n'.join(svg), encoding='utf-8')


def chart(name, title, xlabels, series, ylabel, ymax, xlabel='时间'):
    available = {f.name for f in font_manager.fontManager.ttflist}
    font = next((f for f in ['Microsoft YaHei', 'Noto Sans CJK SC', 'SimHei', 'DejaVu Sans'] if f in available))
    plt.rcParams.update({'font.family': font, 'svg.fonttype': 'none', 'svg.hashsalt': name,
                         'axes.unicode_minus': False, 'font.size': 11})
    fig, ax = plt.subplots(figsize=(10, 4.9), facecolor='#fffaf4')
    ax.set_facecolor('#fffaf4')
    for (label, values), color in zip(series.items(), ['#b64728', '#286885']):
        ax.plot(range(len(xlabels)), values, color=color, marker='o', linewidth=2.5, markersize=4, label=label)
    ax.set_xticks(range(len(xlabels)), xlabels)
    ax.set_ylim(0, ymax)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', color='#e1d7cf', alpha=.8)
    ax.legend(frameon=False, loc='upper left')
    fig.suptitle(title, x=.10, ha='left', fontsize=16, weight='bold', color='#302b28')
    fig.text(.10, .87, '模拟数据 · 仅展示故事中的趋势，不代表真实监控或性能基准', color='#75645a', fontsize=10)
    fig.subplots_adjust(left=.10, right=.96, bottom=.18, top=.79)
    fig.savefig(OUT / f'{name}.svg', metadata={'Date': None, 'Title': title, 'Description': '模拟数据，非真实监控或性能测试结果'})
    plt.close(fig)
    path = OUT / f'{name}.svg'
    content = path.read_text(encoding='utf-8')
    content = content.replace('<svg ', '<svg role="img" aria-labelledby="chart-title chart-desc" ', 1)
    position = content.index('>', content.index('<svg ')) + 1
    content = content[:position] + f'<title id="chart-title">{escape(title)}</title><desc id="chart-desc">模拟数据，非真实监控或性能基准。横轴：{escape(xlabel)}；纵轴：{escape(ylabel)}。</desc>' + content[position:]
    path.write_text(content, encoding='utf-8')
    with (DATA / f'{name}.csv').open('w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([xlabel + '（模拟）', *[label+'（'+ylabel+'）' for label in series]])
        writer.writerows(zip(xlabels, *series.values()))


def main():
    flow('request-chain', '领券请求链路与调查边界', [
        [('浏览器 / App', '用户发起领券请求')], [('Nginx / API Gateway', '鉴权、限流、转发与超时')],
        [('Spring Boot 业务服务', '线程池、JVM 与业务逻辑')],
        [('Redis', '缓存与库存'), ('MySQL', '事务与业务数据'), ('RabbitMQ', '异步履约任务')]])
    flow('jvm-memory', 'Java 堆只是进程内存的一部分', [
        [('Java Heap', '对象实例与数组；-Xmx 限制上限'), ('Metaspace', '类元数据'), ('Thread Stacks', '平台线程栈与线程数量')],
        [('Direct Memory', '直接缓冲区与缓冲池'), ('Code Cache', 'JIT 编译代码'), ('其他原生资源', 'GC、JNI、映射与第三方库')]],
        '非真实比例 · reserved / committed / used / RSS / cgroup 的口径不同', False)
    flow('oom-paths', '先确认谁终止了服务', [
        [('JVM 无法满足分配', '例如 Java heap space'), ('内核或外部发送 SIGKILL', '容器内存压力或其他强制终止')],
        [('OutOfMemoryError', '根据配置尝试记录异常与转储'), ('进程立即终止', '通常没有机会生成 JVM 堆转储')],
        [('分析 Heap / 原生内存', '结合 GC 日志、NMT 与对象引用'), ('核对退出原因与事件', '137 本身不能单独证明 OOM')]])
    flow('gc-roots', '无用对象仍然被强引用', [
        [('存活类的静态字段 CACHE', '类及其加载器仍然可达')], [('ConcurrentHashMap', '没有容量限制、过期或清理机制')],
        [('User A / User B / User C …', '业务不再需要，但仍然强可达')]])
    flow('thread-pool', '忙碌线程不等于 CPU 正在计算', [
        [('HTTP 请求持续进入', '传统 Spring MVC 同步请求模型')], [('Tomcat 工作线程 200 / 200', '线程正在承担请求，也可能等待锁或 I/O')],
        [('后续请求等待、拒绝或超时', '其他共享线程池的接口也可能受到影响')]])
    flow('lock-owner', '先寻找锁持有者，再分析等待者', [
        [('线程 A 持有 CouponService 监视器', '调用远程规则服务，并等待 Future 返回')],
        [('线程 A：TIMED_WAITING', '等待期间仍持有 synchronized 监视器')],
        [('线程 B ～ N：BLOCKED', '等待同一个监视器，无法进入业务方法')]])
    flow('fulfillment', '权益履约需要明确跨系统边界', [
        [('远程规则查询', '设置超时、限流与失败策略')], [('Redis Lua 预占', '单个脚本内原子；记录预占标识并支持恢复')],
        [('MySQL 本地事务', '业务状态与 Outbox 事件一同提交')], [('Outbox Relay → RabbitMQ', '发布确认、重试与重复投递处理')],
        [('履约消费者 → MySQL', '唯一约束、幂等状态机、补偿与对账')]],
        'Redis 预占与 MySQL 事务之间仍有失败窗口，需要超时释放与恢复机制')
    flow('pool-starvation', '唯一工作线程无法执行排队的子任务', [
        [('任务 A 占用唯一工作线程', '向同一线程池提交任务 B')], [('任务 A 调用 inner.get()', '等待 B 完成，但不归还工作线程')],
        [('任务 B 只能留在队列', 'B 等待工作线程；A 等待 B，无法自行推进')]])
    flow('timeout-investigation', 'CPU 不高、接口超时的调查路线', [
        [('影响范围 / 证据 / 止血', '结合版本、实例、业务影响决定恢复措施')], [('多份 Thread Dump + 资源指标', '连续采样；关联线程池、连接池与下游调用')],
        [('BLOCKED', '查监视器与锁持有者'), ('WAITING / TIMED_WAITING', '查 Future、连接池、条件与超时'), ('RUNNABLE', '结合 CPU、I/O 与原生栈')],
        [('验证根因 → 修复 → 压测 → 灰度 → 复盘', '不能只凭某个瞬时状态下结论')]])
    flow('connection-life', '数据库连接占用时间影响并发需求', [
        [('HTTP 请求进入 Spring Boot', '从 HikariCP 获取连接')], [('执行 SQL / 提交事务', '连接在这一段时间内被占用')],
        [('归还连接并返回响应', '稳定系统中：平均占用量 L = 吞吐率 λ × 占用时间 W')]])
    flow('slow-sql-cascade', '连接池耗尽可能是连锁反应', [
        [('SQL 执行时间增长', '扫描、排序、锁等待或其他资源瓶颈')], [('数据库连接占用时间变长', 'HikariCP 活跃连接达到上限')],
        [('Tomcat 请求线程等待连接', '尾延迟和错误率上升，共享资源的其他接口受影响')]])
    flow('deep-pagination', '返回 20 条，不代表只处理 20 条', [
        [('LIMIT 1000000, 20', '从满足条件的有序结果中跳过前一百万条')],
        [('扫描或跳过约 1,000,020 条候选记录', '典型有序索引扫描；还可能存在过滤、排序和回表')], [('最终返回 20 条', '实际扫描量取决于数据与执行计划')]])
    flow('composite-index', '联合索引是有序的组合键', [
        [('索引 (status, created_at DESC, id DESC)', '先按 status 分组，再在组内按时间与 ID 倒序')],
        [('status = 0', 'created_at DESC → id DESC'), ('status = 1', 'created_at DESC → id DESC')]],
        '逻辑顺序示意，并非真实 B+ 树页面结构')
    flow('index-lookup', '二级索引与聚簇索引的两次访问', [
        [('二级索引', '包含 status、created_at 与主键 id')], [('根据 id 访问聚簇索引', '查询还需要二级索引未覆盖的字段')],
        [('读取 user_id、amount 等完整字段', '覆盖索引可减少回表，但不会自动消除 OFFSET 成本')]])
    chart('rollback-errors', '回滚后领券错误率逐步恢复', ['02:10','02:15','02:17','02:20','02:23','02:26','02:30'], {'错误率':[.2,.3,38.6,24,7,1,.2]}, '错误率（%）', 45)
    chart('memory-growth', '堆平稳，容器内存仍在增长', ['00:00','00:30','01:00','01:30','02:00','02:30','03:42'], {'容器内存':[5,5.6,6.4,7.2,8,8.8,10], 'Java Heap Used':[3.9,4,4.1,4,4.2,4,4.1]}, '内存（GiB）', 10.5)
    chart('rss-comparison', '原生资源释放前后的 RSS 趋势', ['0','500','1000','1500','2000','2500','3000'], {'修复前':[2.5,3.5,4.6,5.8,7,8.2,9.4], '修复后':[2.5,2.8,2.7,2.9,2.8,2.9,2.8]}, 'RSS（GiB）', 10, '文档解析次数')
    chart('query-latency', '数据库压力增大，接口尾延迟恶化', ['11:10','11:12','11:14','11:16','11:18','11:20'], {'订单查询 P99':[.03,.06,.3,2.8,9.6,18.4]}, 'P99 延迟（秒）', 20)
    chart('pagination-cost', '分页位置越深，OFFSET 成本越高', ['1','100','1000','10000','50000'], {'OFFSET':[15,50,280,2600,12000], '游标':[15,18,20,21,24]}, '查询耗时（毫秒）', 12500, '页码（等间距类别，非线性数值轴）')
    chart('database-recovery', '限流与暂停高成本任务后恢复', ['11:20','11:25','11:30','11:35','11:40','11:45','11:50'], {'MySQL CPU':[95,97,96,78,51,31,25]}, 'CPU（%）', 100)
    print(f'Created {len(list(OUT.glob("*.svg")))} local SVGs and six illustrative CSV datasets.')


if __name__ == '__main__':
    main()

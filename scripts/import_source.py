"""One-time import with explicit editorial changes. Never overwrite maintained chapters."""
from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'online-troubleshooting.md'


def replace(text, old, new):
    assert old in text, f'Missing editorial target: {old[:70]}'
    return text.replace(old, new, 1)


def region(text, start, end, value):
    a = text.index(start)
    b = text.index(end, a) + len(end)
    return text[:a] + '\n\n' + value + '\n\n' + text[b:]


def diagram(name, label):
    return f'![{label}](../assets/diagrams/{name}.svg)'


def note(value):
    return '\n\n> **工程补充**：' + value + '\n\n'


def main():
    for folder in ('source', 'chapters', 'assets', 'assets/diagrams'):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    if list((ROOT / 'chapters').glob('[0-9][0-9].md')):
        raise SystemExit('Maintained chapters exist; refusing to overwrite.')
    shutil.copyfile(SOURCE, ROOT / 'source/original.md')
    source = SOURCE.read_text(encoding='utf-8')
    blocks = re.split(r'^# 《生产环境：永不熄灭的服务器》\s*$', source, flags=re.M)[1:]
    assert len(blocks) == 4
    titles = ['凌晨两点，服务器突然失联', '消失的内存——16GB 的服务器为什么还是 OOM 了？',
              '被困住的线程——CPU 只有 15%，为什么所有接口都超时了？',
              '数据库的死亡倒计时——一条 SQL 如何拖垮整个系统']
    descriptions = ['CPU 热点 · 线程快照 · 回滚与复盘', 'JVM 内存 · 原生资源 · OOMKilled',
                    '线程池 · 锁竞争 · 连接池耗尽', '慢 SQL · 联合索引 · 游标分页']
    chapters = []
    for i, text in enumerate(blocks, 1):
        # All content before the first scene is duplicated book/chapter metadata.
        text = text[text.index('## 第一幕'):]
        parts = re.split(r'(```[^\n]*\n.*?```)', text, flags=re.S)
        for j in range(0, len(parts), 2):
            value = parts[j]
            value = re.sub(r'^\[[^\n]+\]\(https://images\.openai\.com/[^\n]+\)\s*$', '', value, flags=re.M)
            value = re.sub(r'^\d+\s*$', '', value, flags=re.M)  # orphaned image-result counts
            value = re.sub(r'^下一章[。．]?\s*$', '', value, flags=re.M)
            value = re.sub(r'^#{1,3} (第[一二三四五六七八九十]+幕[^\n]*)', r'## \1', value, flags=re.M)
            value = re.sub(r'^## (\d+\. [^\n]+)', r'### \1', value, flags=re.M)
            value = re.sub(r'^#{1,2} ([\d][\d.,%sGB /+]+)\s*$', r'**\1**', value, flags=re.M)
            parts[j] = value
        text = ''.join(parts)
        if i == 1:
            text = region(text, '生产环境告警\n', '异常：HTTP 500 / 504 激增，实例健康检查失败',
                '### 事故快照 · 虚构场景\n\n| 项目 | 观测值 |\n| --- | --- |\n| 等级与时间 | P1 · 2026-10-16 02:17:34 |\n| 服务 | benefit-service-prod |\n| 错误率 | 38.6% |\n| P99 延迟 | 12.8s |\n| CPU | 96% |\n| 异常 | HTTP 500 / 504 激增，实例健康检查失败 |')
            text = region(text, '用户请求\n', '异步履约', diagram('request-chain', '领券请求链路：从网关到应用及下游依赖'))
            text = region(text, '领券接口错误率变化（虚构事故数据）', '0%15%30%45%02:1002:1502:1702:2002:2302:2602:30',
                diagram('rollback-errors', '回滚后错误率下降（模拟数据，非真实监控）'))
            text = replace(text, '“算法复杂度从可以忽略，变成了整个服务的性能瓶颈。”',
                '“算法复杂度从可以忽略，变成了整个服务的性能瓶颈。”' + note('示例保留了事故代码。除了二次复杂度，还要检查整数溢出：两个 int 相减和累加都可能溢出，Math.abs(Integer.MIN_VALUE) 也不会得到正数。修复时应在相减前提升数值类型，并按输入范围验证总和是否超出 long；若列表不是随机访问实现，重复 get 还会增加开销。'))
            text = replace(text, '## 《生产环境》后续章节', '## 后续章节规划 · 尚未发布')
            text = replace(text, '下一章：《消失的内存——一台拥有 16GB 内存的服务器，为什么还是 OOM 了？》',
                '### 下一章：消失的内存——16GB 的服务器为什么还是 OOM 了？')
            text = text.replace('\\\\[ 10\\\\,000 \\times 10\\\\,000 = 100\\\\,000\\\\,000 \\\\]', '**10,000 × 10,000 = 100,000,000**')
            text = text.replace('\\\\(a_0\\leq a_1\\leq\\cdots\\leq a\\_{n-1}\\\\)', '`a₀ ≤ a₁ ≤ … ≤ aₙ₋₁`')
            text = text.replace('\\\\(O(n\\log n)\\\\)', '`O(n log n)`')
        if i == 2:
            text = region(text, '生产环境严重告警\n', '异常：服务进程突然消失，应用日志中没有 Java OutOfMemoryError',
                '### 事故快照 · 虚构场景\n\n| 项目 | 观测值 |\n| --- | --- |\n| 等级与服务 | P1 · rag-service-prod-02 |\n| 时间 | 03:42:17 |\n| 宿主机内存 | 16GB |\n| JVM 最大堆 | 8GiB（-Xmx8g） |\n| 退出码 | 137 |\n| 异常 | 进程突然消失，无 Java OutOfMemoryError 日志 |')
            text = region(text, 'Java 进程内存空间\n', '进程的 RSS、虚拟内存和 JVM 各内存区域不是简单的一一对应关系，不能直接把所有配置上限相加当成实际物理内存使用量。',
                diagram('jvm-memory', 'JVM 内存版图：堆、元空间、线程栈与原生资源（非真实比例）') + '\n\n进程的 RSS、虚拟内存和 JVM 各内存区域不是简单的一一对应关系，不能把配置上限之和当作实际物理内存。')
            text = region(text, 'JVM 发现 OOM\n', 'SIGKILL，进程立即终止', diagram('oom-paths', '两种退出路径：JVM 抛出 OOM 与内核发送 SIGKILL'))
            text = region(text, '事故配置：容器内存上限 10Gi', '堆上限已经占容器限制的 80%，留给其他内存区域及运行余量的预算可能不足。',
                '| 事故配置 | 内存预算 |\n| --- | --- |\n| 容器上限 | 10GiB |\n| 堆上限 | 8GiB |\n| 其他区域与余量 | 2GiB |\n\n堆上限占容器限制的 80%，剩余预算是否足够需要实测。')
            text = region(text, '故障前内存变化（模拟数据）', '0 GiB2.5 GiB5 GiB7.5 GiB10 GiB00:0000:3001:0001:3002:0002:3003:42',
                diagram('memory-growth', '堆使用量平稳而容器内存增长（模拟数据，非真实监控）'))
            text = replace(text, '### 第一件武器：Native Memory Tracking',
                note('事故进程已退出，无法再对它执行 jcmd 或读取其 /proc。下文的在线检查来自尚存活的同版本实例和受控复现实验；事后分析同时使用事先采集的指标、容器退出记录与内核事件。命令中的 PID 只是占位示例。') + '### 第一件武器：Native Memory Tracking')
            text = text.replace('Total: reserved=13500MB, committed=7600MB', 'Total: reserved=13500MB, committed=9100MB')
            text = replace(text, '- Code\n    reserved=250MB, committed=95MB', '- Code\n    reserved=250MB, committed=95MB\n\n- Other categories (combined for illustration)\n    reserved=2708MB, committed=508MB')
            text = replace(text, '假设输出部分内容：', '以下为合并其他类别后的教学输出，数值用于说明 reserved、committed 与 used 的区别，不是逐字复制的 NMT 日志：')
            text = region(text, '修复前后进程 RSS 对比（模拟实验）', '0 GiB3 GiB6 GiB9 GiB050010001500200025003000',
                diagram('rss-comparison', '相同文档集下修复前后 RSS 趋势（模拟实验数据）'))
            text = region(text, 'GC Root\n', '只要仍然可达，即使业务已经不需要这些对象，GC 也无法判断它们应被删除。',
                diagram('gc-roots', '对象滞留引用链：存活类的静态缓存持续引用用户对象') + '\n\n只要仍然强可达，即使业务已经不需要这些对象，GC 也无法判断它们应被删除。')
            text = replace(text, 'java.util.HashMap$Node       2,100,000', 'java.util.concurrent.ConcurrentHashMap$Node  2,100,000')
            a = text.index('排查进度\n')
            b = text.index('重置清单', a) + len('重置清单')
            steps = [x.strip() for x in text[a:b].split('\n\n') if x.strip() and x.strip() not in ('排查进度', '0/8', '重置清单')]
            assert len(steps) == 8
            text = text[:a] + '\n'.join(f'{k}. {step}' for k, step in enumerate(steps, 1)) + text[b:]
            text = text.replace('\\\\[ \\text{进程内存使用量}\\neq\\text{Java Heap 使用量} \\\\]', '**进程内存使用量 ≠ Java Heap 使用量**')
        if i == 3:
            text = region(text, '生产环境告警\n', '大量 HTTP 504，用户领取优惠券失败',
                '### 事故快照 · 虚构场景\n\n| 项目 | 观测值 |\n| --- | --- |\n| 等级与时间 | P1 · 10:07:23 |\n| 服务 | benefit-service-prod |\n| CPU / JVM 堆 | 15% / 42% |\n| P99 延迟 | 30s+ |\n| Tomcat 忙碌线程 | 200/200 |\n| 影响 | 大量 HTTP 504，领券失败 |')
            text = region(text, '用户请求\n', '后续请求排队、被拒绝或超时', diagram('thread-pool', '请求线程池耗尽：承担请求的线程也可能在等待'))
            text = region(text, '线程 A：持有锁\n', '大量 Tomcat 工作线程无法进入业务方法', diagram('lock-owner', '线程 A 持锁等待远程服务，其余请求等待同一监视器'))
            text = region(text, '用户领取请求\n', '唯一约束、状态机、幂等消费', diagram('fulfillment', '异步履约边界：数据库本地事务与 Redis 预占需要分别处理'))
            text = replace(text, '“但 Redis 原子性不等于 Redis、RabbitMQ 和 MySQL 三者之间存在一个原子事务。”',
                '“但 Redis 原子性不等于 Redis、RabbitMQ 和 MySQL 三者之间存在一个原子事务。”' + note('Transactional Outbox 的前提是业务状态与待发送事件写入同一个数据库本地事务。Redis Lua 预扣与 MySQL Outbox 之间仍有失败窗口，需要可恢复的预占记录、幂等事件标识、超时释放和对账；不能只加一个 Outbox 表就宣称跨系统原子。Redis Cluster 中脚本访问的键还应满足同槽约束。'))
            text = region(text, '外层任务 A\n', '循环等待，程序无法自行取得进展', diagram('pool-starvation', '线程池饥饿：父任务占用唯一工作线程并等待子任务'))
            text = region(text, '接口超时，CPU 不高\n', '验证根因 → 修复 → 压测 → 灰度 → 复盘', diagram('timeout-investigation', '低 CPU 超时调查：按线程状态继续寻找等待资源'))
            text = text.replace('\\\\[ QPS \\approx \\frac{1}{0.5}=2 \\\\]', '**QPS ≈ 1 ÷ 0.5 = 2**')
            text = text.replace('\\\\[ QPS \\approx \\frac{1}{0.005}=200 \\\\]', '**QPS ≈ 1 ÷ 0.005 = 200**')
            text = text.replace('\\\\[ \\text{JVM 内互斥}\\neq\\text{分布式业务唯一性} \\\\]', '**JVM 内互斥 ≠ 分布式业务唯一性**')
        if i == 4:
            text = region(text, 'MySQL 生产集群告警\n', '订单列表接口大面积超时，部分支付查询请求受影响',
                '### 事故快照 · 虚构场景\n\n| 项目 | 观测值 |\n| --- | --- |\n| 等级与时间 | P1 · 11:20:36 |\n| 实例 | mysql-order-primary |\n| MySQL CPU | 95% |\n| 接口 P99 延迟 | 18.4s |\n| HikariCP 活跃连接 | 50/50 |\n| 接口错误率 | 32.7% |\n| 影响 | 订单列表超时，部分支付查询受影响 |')
            text = region(text, '订单查询延迟变化（模拟事故数据）', '0 s5 s10 s15 s20 s11:1011:1211:1411:1611:1811:20', diagram('query-latency', '数据库压力增加时接口尾延迟恶化（模拟数据）'))
            text = region(text, 'HTTP 请求进入 Spring Boot\n', '归还连接，返回响应', diagram('connection-life', '请求占用数据库连接的生命周期'))
            text = region(text, 'SQL 执行时间增长\n', '共享连接池中的其他接口也可能受到影响', diagram('slow-sql-cascade', '慢 SQL 引发连接占用增长与请求线程排队'))
            text = region(text, '深分页扫描示意\n', '这是典型有序索引扫描下的示意，实际扫描行数由过滤条件、索引、优化器执行计划和数据分布决定。', diagram('deep-pagination', '典型索引扫描：跳过一百万条记录后返回二十条（示意）'))
            text = region(text, '联合索引 `(status, created_at DESC, id DESC)`\n', '这是索引逻辑顺序的简化表示，并非真实 B+ 树页面结构。', diagram('composite-index', '联合索引的逻辑顺序：先按状态分组，再按时间与 ID 倒序'))
            text = region(text, '二级索引\n', '读取 user_id、amount 等字段', diagram('index-lookup', '回表：使用二级索引取得主键，再获取完整记录'))
            text = region(text, '分页深度与查询耗时（示意数据）', '0 ms3000 ms6000 ms9000 ms1.2万 ms第1页第100页第1000页第10000页第50000页', diagram('pagination-cost', 'OFFSET 与游标分页的趋势对比（模拟数据，非性能基准）'))
            text = region(text, '止血后数据库 CPU 变化（模拟数据）', '0%25%50%75%100%11:2011:2511:3011:3511:4011:4511:50', diagram('database-recovery', '限流与暂停高成本任务后 CPU 回落（模拟数据）'))
            text = replace(text, '“加上唯一的 `id`，就能形成确定性的排序顺序。”', '“加上唯一的 `id`，就能形成确定性的排序顺序。”' + note('确定性排序不等于多次翻页共享同一个数据快照。若翻页期间排序字段或筛选条件发生更新，仍可能漏读或重复；需要明确业务是否接受实时变化，或采用快照、版本边界等策略。'))
            text = replace(text, '## 第五章：《无法提交的事务——MySQL 锁战争》', '## 待续：无法提交的事务——MySQL 锁战争')
            text = text.replace('\\\\[ L=\\lambda W \\\\]', '**L = λ × W**')
            text = text.replace('\\\\[ 100\\times0.02=2 \\\\]', '**100 × 0.02 = 2**')
            text = text.replace('\\\\[ 100\\times2=200 \\\\]', '**100 × 2 = 200**')
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        assert '\\\\[' not in text and '\\\\(' not in text, 'Unconverted formula'
        assert 'images.openai.com' not in text
        (ROOT / f'chapters/{i:02}.md').write_text('# ' + titles[i-1] + '\n\n' + text + '\n', encoding='utf-8')
        chapters.append({'number': i, 'title': titles[i-1], 'description': descriptions[i-1]})
    (ROOT / 'book.json').write_text(json.dumps({'title': '生产环境：永不熄灭的服务器', 'status': '连载中', 'next': '无法提交的事务——MySQL 锁战争', 'chapters': chapters}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Imported four chapters; original archived byte-for-byte.')


if __name__ == '__main__':
    main()

用小说的方式讲解一下线上遇到各种问题的排查已经解决方案。



# 《生产环境：永不熄灭的服务器》

第一卷：线上事故调查局

这是一部关于 Java 后端工程师如何从线上事故中成长的技术小说。

故事从一个刚刚入职的 Java 后端工程师开始。他原本以为，只要代码写得足够好、单元测试全部通过，系统就能稳定运行。

直到某天凌晨，一场生产事故彻底改变了他的认知。

整部小说会遵循一个原则：

每次事故都从真实的故障现象出发，随着主角调查，逐步揭开 JVM、MySQL、Redis、消息队列、网络和分布式系统的底层原理，最后给出可执行的排查命令、解决方案和面试回答。

## 第一章：凌晨两点，服务器突然失联

[GitHub 8月17日7小时大宕机：29亿提交下的过载防御失灵 — 团子技术日报](https://images.openai.com/static-rsc-4/AJhMsJhJik-AwUetrHPue93kC9RB3l49sLlpli8u3baBpaV8yz4rYsFNwFdDR4JKUm9V8XwEMBUNvMTe0FNgdciTUrSTl6nxWD-simyDHZ5Lb6WQOroIWSaBMKhbyM7UYrkzJRG13Op13drfZF_zz1CTW45FAUFUNjunGJopHG4?purpose=inline)

[Medium](https://images.openai.com/static-rsc-4/qShI_8pw-yB94clR3bNosN0iQx-Fje42LFC3UwQlN28ITvqpqe5mJvaAJNZiNNZbcfmBqtAVzrvalpen0Kr4Gwrrow9Vm-r-X6RtLrVpOroWsa8t08s_bWKEWVBJFwsC2UqJSd0EJ207pPUX6VnibUXqUeqerdpCTSZmho7bm8Q?purpose=inline)

[Handling Production Outages. Production outages have a way of… | by Mounick | Feb, 2026 | Medium](https://images.openai.com/static-rsc-4/WxKgs0yZ6MQlIcS-bgBEk7p-O1brt9Kk2O5bumn-zbmI8K14-_DeRn4iK1ENhMcCRGErRRPAojg7Qc1uv_AQxmVgujboNY8TezJn37hOfux8O72hwiLpDslgBXoMFSTVe5WfOoaBlXFauNmSEPZ2psIRo1Skn3HitRDMEIzQKmY?purpose=inline)

10

### 第一幕：一条来自生产环境的警报

凌晨 2:17。

星海科技总部，二十三楼。

整个研发中心已经空无一人，只有服务器机房的散热风扇还在持续轰鸣。

突然，一条告警打破了寂静。

生产环境告警

P1 严重

2026-10-16 02:17:34

营销权益服务异常

服务：benefit-service-prod

错误率

# 38.6%

P99 延迟

# 12.8s

CPU

# 96%

异常：HTTP 500 / 504 激增，实例健康检查失败

值班工程师林川被手机震醒。

他刚入职三个月，主要负责公司基于 Spring Boot、MySQL、Redis 和 RabbitMQ 构建的营销权益发放系统。

手机再次震动。

技术负责人陈默发来消息：

“林川，生产出问题了。用户领不了优惠券，你先看一下。”

林川迅速打开电脑。

监控显示，原本稳定在每秒 800 次请求的系统，突然出现了大量超时。

他第一反应是：

“是不是服务器 CPU 太高了？要不要重启？”

陈默立即回复：

“你连 CPU 为什么高都不知道，就准备重启？”

“可是系统已经快不能用了。”

“那你告诉我，重启能解决什么问题？”

林川沉默了。

陈默继续说道：

“记住，线上事故最危险的不是系统宕机，而是工程师在不知道原因的时候，随意操作生产环境。”

“现在，我教你第一件事。”

“先判断故障范围，再止血，保留证据，最后定位根因。不要把排查顺序搞反。”

### 第二幕：第一条线索——到底是谁出了问题？

陈默打开监控平台。

“林川，假设用户反馈领券失败，你会怀疑哪里？”

林川思考片刻：

“可能是前端，也可能是网关、Java 服务、Redis、MySQL，甚至 RabbitMQ。”

“没错。那你怎么判断？”

陈默在白板上画出整条请求链路。

用户请求

浏览器 / App

Nginx / API Gateway

负载均衡、鉴权、限流

Spring Boot 业务服务

线程池、JVM、业务逻辑

Redis

缓存 / 库存

MySQL

事务 / 数据

RabbitMQ

异步履约

“现在假设 Nginx 记录大量 504，你能确定 Java 服务 CPU 有问题吗？”

“不能。504 只能说明网关在规定时间内没有等到上游的有效响应。”

“对。它可能是 Java 服务处理太慢，也可能是网络异常、连接建立失败、依赖阻塞等。”

陈默补充：

“还有一点，HTTP 500 和 504 不一定来自同一个故障点。 你必须结合网关日志、应用日志和链路追踪分析。”

### 第一轮排查：判断影响范围

陈默要求林川先回答四个问题：

1. 是所有用户失败，还是部分用户失败？
2. 是所有接口失败，还是只有领券接口失败？
3. 是所有实例异常，还是某一个实例异常？
4. 是突然发生，还是随着流量增加逐渐恶化？

林川查看监控，发现：

- 登录、查询商品等接口基本正常。
- 领券接口错误率大幅上升。
- 三个业务实例中有两个 CPU 接近 100%。
- 故障发生前五分钟，领券服务刚刚发布过新版本。

林川眼睛一亮。

“难道是新版本有 Bug？”

陈默摇头。

“新版本是重要线索，但时间相关不等于因果关系。先看发布前后差异。”

他们核对了发布记录，发现新版本引入了一个营销资格计算逻辑。

但此时系统还在不断报错。

“先止血。”陈默说。

他们确认旧版本兼容当前数据库结构、没有不可逆数据迁移后，通过发布平台将流量切回上一稳定版本，并逐步摘除异常实例。

几分钟后，错误率开始下降。

领券接口错误率变化（虚构事故数据）

回滚后错误率逐步恢复正常

0%15%30%45%02:1002:1502:1702:2002:2302:2602:30

“系统恢复了。”林川长出一口气。

“但事故还没结束。”陈默说，“我们还不知道为什么。”

### 第三幕：CPU 100%，就一定是死循环吗？

陈默拿出刚才保留的 JVM 线程快照。

“假设我们在故障发生时登录到 Linux 服务器，你第一步会执行什么？”

林川回答：

```
top
```

屏幕显示：

```
PID     USER    %CPU   %MEM   COMMAND
18432   app     195.3  18.2   java
```

林川愣住了。

“CPU 不是最高 100% 吗？怎么会有 195%？”

陈默笑了笑。

“在 Linux 常见的 `top` 显示模式下，进程 CPU 使用率可以超过 100%，因为一个进程可能同时使用多个 CPU 核心。”

“195% 大致相当于使用了接近两个逻辑 CPU 核心的计算能力。”

“但注意，这还不能说明一定是 Java 业务代码的问题。”

“可能是频繁 GC、死循环、热点计算、序列化开销，也可能是其他原因。”

“所以，我们需要继续往下查。”

#### 第一步：找到 Java 进程

```
jps -l
```

假设输出：

```
18432 com.xinghai.BenefitApplication
```

#### 第二步：查看进程内的高 CPU 线程

```
top -H -p 18432
```

林川看到：

```
PID     %CPU   COMMAND
18479   98.7   java
18483   91.2   java
18491    2.1   java
```

“18479 和 18483 这两个线程很可疑！”

“对。但现在我们只知道线程 ID，不知道它们执行了什么 Java 代码。”

“怎么办？”

“把线程 ID 转换成十六进制。”

```
printf '%x\n' 18479
```

输出：

```
482f
```

“为什么要转十六进制？”

“因为 HotSpot JVM 的线程 dump 通常使用十六进制 `nid` 表示操作系统原生线程 ID。”

#### 第三步：抓取线程栈

```
jcmd 18432 Thread.print -l > /tmp/thread.txt
```

然后搜索：

```
grep -A 35 'nid=0x482f' /tmp/thread.txt
```

屏幕上出现：

```
"coupon-worker-7" #85
   java.lang.Thread.State: RUNNABLE
    at com.xinghai.rule.RuleEngine.calculate(...)
    at com.xinghai.coupon.CouponService.check(...)
    at com.xinghai.coupon.CouponController.receive(...)
```

林川兴奋地说道：

“找到凶手了！RuleEngine！”

陈默却摇头。

“还不能确定。”

“为什么？”

“因为 `RUNNABLE` 只是 JVM 线程状态，单次线程栈也只能说明采样瞬间它正在执行这段代码。”

“我们要连续采样，看它是不是一直停留在同一段计算逻辑里。”

于是，他们间隔几秒抓取了多份线程快照。

结果发现，两条高 CPU 线程反复出现在同一个规则计算方法中。

而 GC 指标没有显示异常增长。

“现在我们才有比较充分的理由怀疑业务代码热点。”

### 第四幕：隐藏在循环里的杀手

林川打开刚刚上线的规则计算代码。

```
public int calculate(List<Integer> scores) {
    int result = 0;

    for (int i = 0; i < scores.size(); i++) {
        for (int j = 0; j < scores.size(); j++) {
            result += Math.abs(scores.get(i) - scores.get(j));
        }
    }

    return result;
}
```

“这段代码有什么问题？”陈默问。

“嵌套循环，时间复杂度 O(n²)。”

“那它一定有问题吗？”

“不一定。如果 scores 只有十个元素，执行一百次计算，问题不大。”

“很好。那如果有一万个元素呢？”

林川迅速计算。

\\[ 10\\,000 \times 10\\,000 = 100\\,000\\,000 \\]

“一亿次！”

“而且如果有大量用户并发请求，多个线程就会同时执行这些计算。”

“这才是 CPU 被打满的原因。”

陈默继续解释：

“以前的版本只对少量固定规则评分。新版本把用户历史行为全部传了进来，部分用户的集合达到了上万个元素。”

“算法复杂度从可以忽略，变成了整个服务的性能瓶颈。”

林川问：

“那是不是把服务器扩容就行？”

“扩容可以缓解，但未必解决。”

“假设单次请求耗费大量 CPU，扩容可能暂时增加吞吐量，但如果流量继续增长，问题仍会出现。更重要的是，这段算法本身是否能优化？”

他们重新分析需求，发现根本不需要计算所有元素对之间的绝对差。

对于排序后的数组 \\(a_0\leq a_1\leq\cdots\leq a\_{n-1}\\)，可以利用每个元素对总和的贡献，将原来的二次复杂度优化为排序主导的 \\(O(n\log n)\\)。

但陈默没有立刻把优化代码提交生产。

“先补边界测试、压测和性能基准，再走灰度发布。”

“因为我们解决的是线上事故，不是一道只要求通过样例的算法题。”

## 第五幕：真正的线上排查方法论

凌晨 4:12。

故障复盘会议开始。

陈默在白板上写下八个字：

现象 → 范围 → 止血 → 根因

接着，他补充了完整流程。

1. 发现异常

   通过错误率、P95/P99 延迟、吞吐量、资源使用率发现故障
2. 确定故障范围

   按用户、接口、实例、机房、版本、时间维度缩小范围
3. 安全止血

   回滚、限流、降级、熔断、切流或扩容；优先选择可逆操作
4. 保留现场证据

   保存日志、线程栈、GC 指标、Trace、数据库与中间件状态
5. 提出并验证假设

   根据证据排除错误方向，不凭单一指标下结论
6. 修复并验证

   测试环境复现、压测、灰度、监控验证，必要时回滚
7. 事故复盘

   补充测试、告警、容量规划和应急预案，避免再次发生

陈默最后问：

“林川，你现在还觉得线上 CPU 100%，直接重启就可以了吗？”

“不觉得了。”

“说说为什么。”

“因为 CPU 高只是现象，可能是业务计算、GC、线程竞争等原因。重启可能暂时恢复，但也可能销毁关键现场，而且问题可能很快再次出现。”

“如果业务影响严重，应优先通过可控方式止血，同时尽量保存证据。之后再结合 CPU、线程栈、GC、发布记录和调用链定位根因。”

陈默点点头。

“这才是生产环境工程师的思维方式。”

## 本章技术档案：CPU 异常排查速查

| 现象             | 重点怀疑             | 排查手段                  |
| -------------- | ---------------- | --------------------- |
| CPU 高，少数线程持续繁忙 | 死循环、热点计算         | `top -H`、线程栈、Profiler |
| CPU 高，GC 次数频繁  | 对象分配过快、堆压力       | `jstat`、GC 日志、JFR     |
| CPU 不高，请求却很慢   | I/O 阻塞、锁等待、连接池耗尽 | 线程栈、Trace、连接池指标       |
| CPU 高，吞吐量下降    | GC、锁竞争、计算瓶颈      | CPU/GC/线程联合分析         |
| 只有个别实例异常       | 流量倾斜、实例配置、局部故障   | 实例对比、负载均衡指标           |

注意：生产排查命令应在具备权限、遵循操作规范的情况下执行。线程 dump、Profiler、Heap Dump 都可能产生开销，尤其需要注意磁盘空间、敏感数据和高负载实例。

### 面试官突然出现

第二天上午，陈默扮演面试官。

“假设线上 Java 服务 CPU 突然达到 100%，你会怎么排查？”

林川回答：

“我会先判断影响范围和业务严重程度，结合监控确定是否需要限流、切流或回滚止血。

然后通过 `top` 判断是哪个进程占用 CPU，通过 `top -H -p PID` 找到高 CPU 线程，将线程 ID 转为十六进制，结合 `jcmd Thread.print` 或线程 dump 定位对应 Java 调用栈。

如果线程持续执行某段业务逻辑，我会重点排查死循环、算法复杂度和热点计算；如果 GC 指标异常，则进一步查看 GC 日志、堆使用情况和对象分配速率。

定位原因后，在测试环境复现并验证修复方案，灰度发布，观察 CPU、吞吐量、延迟和错误率是否恢复，最后完成事故复盘。”

陈默说：

“这个回答已经具备了完整的排查逻辑。但真正的难点在于，你能不能根据现场证据判断下一步应该查什么，而不是机械地背命令。”

## 《生产环境》后续章节

这部小说会逐渐从单机故障深入到完整的分布式系统事故。

| 章节   | 事故主题              | 核心技术                                  |
| ---- | ----------------- | ------------------------------------- |
| 第二章  | 消失的内存：服务器为什么越跑越慢？ | JVM 内存泄漏、OOM、Heap Dump、MAT            |
| 第三章  | 被困住的线程：接口突然全部超时   | 线程池、锁竞争、死锁、连接池                        |
| 第四章  | 数据库的死亡倒计时         | MySQL 慢 SQL、索引失效、执行计划                 |
| 第五章  | 一场无法提交的事务         | 行锁、间隙锁、死锁、MVCC                        |
| 第六章  | Redis 帝国的雪崩       | 缓存穿透、击穿、雪崩、热 Key                      |
| 第七章  | 消失的十万张优惠券         | RabbitMQ 消息丢失、重复消费、积压                 |
| 第八章  | 504 风暴：谁偷走了响应时间？  | TCP、连接池、Nginx、超时链路                    |
| 第九章  | JVM 的停顿：消失的三秒钟    | GC、STW、G1、ZGC                         |
| 第十章  | 流量洪峰：十万请求同时抵达     | 限流、熔断、降级、容量规划                         |
| 第十一章 | 幽灵订单：数据为何不一致？     | 分布式事务、幂等、补偿、最终一致性                     |
| 第十二章 | 看不见的凶手：生产事故终极调查   | Prometheus、Grafana、Tracing、Arthas、JFR |

下一章：《消失的内存——一台拥有 16GB 内存的服务器，为什么还是 OOM 了？》

故事将从一次诡异的生产事故开始：服务器拥有 16GB 内存，JVM 最大堆设置为 8GB，监控显示堆内存似乎还有空间，Java 进程却突然被 Linux 杀死。

我们将随着林川的调查，逐步揭开 Java Heap OOM、Metaspace OOM、Direct Memory OOM、容器 OOMKilled、Linux OOM Killer、内存泄漏与内存溢出的区别，以及如何使用 `jcmd`、`jmap`、MAT、GC 日志和 Arthas 找出真正的问题。



下一章


# 《生产环境：永不熄灭的服务器》

第二章：消失的内存——16GB 的服务器为什么还是 OOM 了？

第一卷：线上事故调查局

## 第一幕：一台被 Linux 判处死刑的服务器

凌晨 3:42。

星海科技研发中心。

林川刚刚结束上一场 CPU 事故的复盘，原本以为终于可以安稳睡觉。

突然，手机再次响起。

生产环境严重告警

P1

03:42:17 · rag-service-prod-02

企业知识库服务实例异常退出

服务器内存

## 16 GB

JVM 最大堆

## 8 GB

退出码

## 137

异常：服务进程突然消失，应用日志中没有 Java OutOfMemoryError

林川看着监控，皱起眉头。

“奇怪，服务器有 16GB 内存，我给 JVM 配置了 `-Xmx8g`，按理说还有 8GB 留给系统。”

“为什么会内存不足？”

电话另一端，技术负责人陈默沉默了几秒。

“林川，你是不是认为 JVM 最大堆内存等于 Java 进程最大内存？”

“难道不是？”

“当然不是。”

“那 `-Xmx8g` 到底限制了什么？”

“只限制 Java 堆的最大容量，不是整个 JVM 进程的内存上限。”

陈默打开远程会议。

“今晚，我带你认识一个比 CPU 100% 更隐蔽的敌人。”

“内存。”

[FBI-Datenleck und globale Telekom-Angriffe erschüttern Branche](https://images.openai.com/static-rsc-4/-g5-7iN4PeNrtXkSadZNtsXTaFM3IsM0jJqjbvxCjRTyKWyb15S5aQbjmSV2fTI38Wf3lmPanBOrqzWo5nvbleEqkDDisLG2dKDLgBSdokHl1UAqdk6Mm9E7eDqFl-oO0DpYlIdULRJQu87JRUF664ZC8kb2kAmWCg9ejq1Vtp0?purpose=inline)

[Bill Vivino Technology Blog — Dev Tips & Case Studies](https://images.openai.com/static-rsc-4/KeC5BS3oH0lGHOtWsCDd3dk4P0ZywBStDyXru1Faq0kV9alCCqyZ5ilvDDWDAZjDEE_HiAh3hr4lfXmfuTq_JosC_XsL4V2Eh6Hz5kRiDVBrWZ5AsDwZUHmxFWVGe6pE0a3nO-yHW0IE5JHL-u-mqqPoSsf8_wBQ9kAqLCbmL2c?purpose=inline)

[ChipSoft Ransomware Attack Disrupts Dutch Hospital Network](https://images.openai.com/static-rsc-4/uxc2xu49NcK2mCPM7pGzNAVlZc3pqCYbiwkGo3DKbXnmJCAzQWKq03Tq9QVpOYE7KahIFotAf27i2phGb7h97K2pXGwo6fuxun5XFJ9xlDYT_w42tGFBVVrKcyt33YvdhuytYeQnllxeYe1TOtQpzXGwikawtmbUJunOInEH5Cw?purpose=inline)

8

## 第二幕：内存王国——JVM 到底占用了多少内存？

陈默在白板上画了一座城市。

“你可以把 JVM 想象成一座城市。”

“Java 堆只是城市里最大的一片住宅区。”

“但城市不可能只有住宅区。”

“还需要道路、仓库、行政中心、工厂，以及工人自己的休息空间。”

林川点点头。

“也就是说，Java 进程除了堆，还有其他内存开销？”

“对。”

### JVM 进程的内存版图

Java 进程内存空间

示意图，非真实比例

Java Heap（堆）

对象实例、数组等 · -Xmx8g

Metaspace

类元数据

Thread Stacks

线程栈

Direct Memory

直接内存

Code Cache

JIT 编译代码

其他原生内存与映射

GC 内部结构、JNI、JVM 自身、共享库、内存映射等

进程的 RSS、虚拟内存和 JVM 各内存区域不是简单的一一对应关系，不能直接把所有配置上限相加当成实际物理内存使用量。

陈默解释：

“Java 进程可能消耗的内存，包括堆、元空间、线程栈、直接内存、JIT 代码缓存、GC 数据结构和其他原生内存。”

“因此，即使堆内存没有达到 8GB，整个进程仍然可能超过操作系统或容器的内存限制。”

林川突然想到：

“那我是不是只要把 `-Xmx` 设置小一点，就能解决？”

“未必。”

“为什么？”

“因为你还不知道内存究竟消耗在哪里。”

“如果是线程数量异常，降低堆大小不一定有用。”

“如果是 Direct Memory 不断增长，降低堆大小可能只是给它暂时腾出空间。”

“如果是容器限制太小，还可能需要重新规划整个内存预算。”

陈默在白板上写下：

\\[ \text{进程内存使用量}\neq\text{Java Heap 使用量} \\]

“这是今天你必须记住的第一件事。”

## 第三幕：137 号死亡通知书

林川翻阅应用日志。

最后一条日志停留在：

```
03:42:16 INFO  DocumentParser
Parsing document: handbook-2026.pdf
```

随后，没有异常堆栈，没有 `OutOfMemoryError`，进程直接消失。

“为什么没有 Java 异常？”

陈默问：

“如果 JVM 自己发现 Java 堆空间不足，会发生什么？”

“通常抛出 `java.lang.OutOfMemoryError`。”

“那如果是 Linux 内核直接杀死进程呢？”

林川愣住了。

“JVM 根本没有机会抛异常？”

“没错。”

### 两种完全不同的死亡方式

陈默画了两条路径。

JVM 发现 OOM

无法满足内存分配

抛出 OutOfMemoryError

可能生成 Heap Dump

内核 / 容器 OOM

触及内存限制

OOM Killer 选中进程

SIGKILL，进程立即终止

“所以，137 代表什么？”陈默问。

林川回答：

“通常是 128 + 9，也就是进程因 SIGKILL 终止。”

“很好。但要注意，退出码 137 不能单独证明发生了 OOM。 管理员执行 `kill -9`，或者其他机制发送 SIGKILL，也可能出现 137。”

“我们必须继续寻找证据。”

#### 第一步：检查容器退出原因

假设服务运行在 Kubernetes 中：

```
kubectl describe pod rag-service-xxx
```

林川看到：

```
Last State:
  Terminated:
    Reason: OOMKilled
    Exit Code: 137
```

“这下可以确定了！”

“基本可以确认该容器被判定为 OOMKilled。但我们仍然需要弄清楚具体的内存压力来源。”

#### 第二步：查看容器资源限制

```
kubectl get pod rag-service-xxx -o yaml
```

关键配置：

```
resources:
  requests:
    memory: "4Gi"
  limits:
    memory: "10Gi"
```

林川突然发现了问题。

“服务器虽然有 16GB，但容器的内存限制只有 10Gi！”

“对。容器能使用的内存，并不直接等于宿主机物理内存。”

陈默继续说道：

“`requests.memory` 主要用于调度与资源保障相关机制；`limits.memory` 才是这里需要重点关注的内存上限。”

“所以，我们应该以容器的 10Gi 为基础制定 JVM 内存预算，而不是宿主机的 16GB。”

### 一个危险的内存配置

事故配置：容器内存上限 10Gi

Java 堆最大 8Gi

剩余预算 2Gi

堆上限已经占容器限制的 80%，留给其他内存区域及运行余量的预算可能不足。

“但是，”林川问，“我们现在只是发现配置有风险，仍然不知道究竟是什么吃掉了内存。”

“正确。”

陈默打开了另一张监控图。

## 第四幕：不断膨胀的幽灵

监控数据显示：

故障前内存变化（模拟数据）

Java Heap 相对稳定，但容器内存持续增长；单位 GiB

Java 堆已使用容器内存使用

0 GiB2.5 GiB5 GiB7.5 GiB10 GiB00:0000:3001:0001:3002:0002:3003:42

林川盯着屏幕。

“Java 堆一直只有 4GB 左右，但是容器内存从 5GB 一直涨到 10GB。”

“说明什么？”

“说明内存增长可能主要发生在堆外。”

“没错。不过这里还有一个细节。”

“什么？”

“容器内存指标可能包含文件页缓存等内容，和进程 RSS 不是同一个概念。所以不能仅凭这张图就认定 Direct Memory 泄漏。”

陈默决定进一步调查。

“我们需要区分三类证据：JVM 内部统计、进程内存，以及容器 cgroup 统计。”

### 第一件武器：Native Memory Tracking

陈默问：

“你知道 JVM 自带一个叫 NMT 的工具吗？”

“不知道。”

“全称 Native Memory Tracking，可以跟踪 HotSpot JVM 自身管理的多类原生内存分配。”

“不过有两个限制：需要在 JVM 启动时启用，而且它不能完整覆盖所有第三方原生库和所有内存映射。”

他们检查了事故实例的启动配置。

```
-XX:NativeMemoryTracking=summary
```

“幸好这个服务之前就启用了 NMT。”

陈默解释：

“如果没有提前启用，不能指望在进程运行中直接开启完整的 NMT 跟踪。我们需要通过新实例或下次启动启用。”

查看统计：

```
jcmd 18432 VM.native_memory summary scale=MB
```

假设输出部分内容：

```
Native Memory Tracking:

Total: reserved=13500MB, committed=7600MB

- Java Heap
    reserved=8192MB, committed=8192MB

- Class
    reserved=1050MB, committed=180MB

- Thread
    reserved=1300MB, committed=125MB

- Code
    reserved=250MB, committed=95MB
```

林川发现：

“为什么 Java Heap committed 是 8192MB，但监控中使用量只有 4GB？”

陈默解释：

“因为 committed 和 used 不是同一个概念。”

“committed 代表 JVM 已向操作系统提交的内存容量，而堆 used 代表当前堆中已使用的容量。”

“而且 committed 也不能直接等同于实际 RSS。”

“那 reserved 呢？”

“reserved 通常表示保留的虚拟地址空间，不代表已经占用了等量物理内存。”

陈默在白板上写下：

| 指标            | 含义                   |
| ------------- | -------------------- |
| Reserved      | 预留的虚拟地址空间            |
| Committed     | 已提交的内存容量             |
| Heap Used     | 堆中当前已使用的空间           |
| RSS           | 进程实际驻留在物理内存中的页面量     |
| Cgroup Memory | 容器所属 cgroup 计费的内存使用量 |

“这些指标口径不同，不能混为一谈。”

林川问：

“可是 NMT 没发现特别明显的增长，怎么办？”

陈默回答：

“这反而是一条线索。”

“如果 JVM 自己跟踪的原生内存变化不大，但进程 RSS 持续增长，就需要怀疑 NMT 覆盖不到的原生分配或内存映射。”

“接下来查操作系统。”

### 第二件武器：进程内存

```
cat /proc/18432/status
```

重点关注：

```
VmRSS:
VmSize:
Threads:
```

也可以查看：

```
cat /proc/18432/smaps_rollup
```

以及：

```
pmap -x 18432
```

陈默补充：

“如果是容器，还要查看 cgroup v2 的 `memory.current`、`memory.stat` 和 `memory.events` 等指标。”

“不同容器运行时、cgroup 版本、权限和命名空间下，路径可能不同。”

林川追问：

“所以我们需要对比 JVM 内存、进程 RSS 和容器内存三条曲线？”

“对。这样才能判断内存到底是被 JVM、原生库，还是文件缓存等其他部分消耗。”

## 第五幕：真正的凶手——被遗忘的 PDF 页面

凌晨 5:06。

林川终于找到了异常代码。

服务负责解析企业上传的 PDF 文档，再将文本切分并写入向量数据库。

某个开发人员为了提高解析性能，引入了一个原生 PDF 渲染库。

代码经过简化后类似：

```
public void parsePdf(String path) {
    NativePdfDocument document =
        NativePdfDocument.open(path);

    for (int i = 0; i < document.pageCount(); i++) {
        NativePdfPage page = document.loadPage(i);

        String text = page.extractText();
        saveText(text);
    }
}
```

林川看了半天。

“这有什么问题？”

陈默指向 `NativePdfPage`。

“它是什么？”

“一个 Java 对象。”

“它背后呢？”

“可能对应原生 PDF 页面资源。”

“那么当 Java 对象不可达的时候，原生资源就一定立即释放了吗？”

林川愣住了。

“不一定。”

“没错。某些原生库要求调用者显式关闭或释放底层资源。”

“如果只依赖 Java GC，而没有按照库的资源管理协议释放原生对象，内存就可能不断累积。”

陈默展示了修复后的伪代码：

```
public void parsePdf(String path) {
    try (NativePdfDocument document =
             NativePdfDocument.open(path)) {

        for (int i = 0; i < document.pageCount(); i++) {
            try (NativePdfPage page =
                     document.loadPage(i)) {

                String text = page.extractText();
                saveText(text);
            }
        }
    }
}
```

这里的 NativePdfDocument、NativePdfPage 是用于讲解的虚构接口，假设它们实现 AutoCloseable。实际使用时必须遵循对应 PDF 库的释放规范。

“原来如此！”林川说道。

“Java 堆中的对象可能被 GC 回收，但是底层原生资源未必按照预期释放。”

“正是这样。”

### 为什么 GC 没能拯救服务器？

陈默进一步解释：

“GC 主要依据 Java 对象的可达性和堆内存压力工作。”

“但某些原生内存分配不会完整地反映在 Java 堆的使用量里。”

“因此可能出现这样一种情况：”

- Java 堆使用量长期稳定。
- 原生内存持续增加。
- JVM 没有明显的堆空间压力。
- 容器内存逐渐触及限制。
- 最终被 OOM Killer 终止。

“当然，这不意味着所有堆外内存都不受 GC 影响。”陈默补充，“例如某些直接缓冲区具有与 Java 对象生命周期关联的清理机制，但释放时机和实现细节需要具体分析。”

“这次的关键是，我们使用的原生库要求显式释放资源，而代码没有做到。”

### 如何证明修复有效？

林川提出：

“我们把 `close()` 加上，然后发布不就行了？”

陈默摇头。

“你怎么证明这就是根因？”

他们做了一个可控的复现实验。

首先，在测试环境中使用固定的 PDF 文件集，连续解析数千次。

记录进程 RSS、容器内存、JVM Heap 和 NMT 数据。

然后分别运行旧版本和修复版本。

修复前后进程 RSS 对比（模拟实验）

相同文档集、相同运行环境，单位 GiB

修复前修复后

0 GiB3 GiB6 GiB9 GiB050010001500200025003000

“修复后 RSS 没有持续增长！”林川说道。

“这才是更有力的证据。”

“还需要检查资源释放是否影响解析正确性、异常分支是否也能关闭资源，以及并发解析时是否仍然稳定。”

“然后再灰度发布。”

陈默关闭监控页面。

“这次我们不仅修好了代码，还要重新设计容器内存预算，并给原生内存增长增加告警。”

# 第六幕：另一个世界——如果真的是 Java Heap OOM 呢？

天亮以后，林川以为课程结束了。

陈默却打开了一份新的事故档案。

“刚才是原生内存问题。”

“但 Java 面试官更喜欢问另一种情况。”

“如果出现 `java.lang.OutOfMemoryError: Java heap space`，你该怎么办？”

林川回答：

“把 `-Xmx` 调大？”

陈默看了他一眼。

“你又想直接扩容了。”

“……”

“假设你的服务每小时泄漏 500MB 内存，8GB 堆撑不住，换成 16GB 堆就不会泄漏了吗？”

“还是会，只是死得更晚。”

“对。”

“所以你必须先理解什么叫内存泄漏。”

## 1. 内存溢出与内存泄漏的区别

陈默画了一个仓库。

“假设 Java 堆是一座仓库。”

“正常情况下，你往里面放货物，不需要的货物会被清理出去。”

“但有两种情况会让仓库爆满。”

第一种：仓库确实不够大。

例如业务需要同时处理一个 5GB 的数据集，但可用堆空间只有 2GB。

即使程序没有泄漏，也可能 OOM。

第二种：仓库里堆满了永远不会被清理的旧货。

例如某个静态集合不断保存用户对象，却从来不删除。

```
public class UserCache {

    private static final Map<Long, User> CACHE =
        new ConcurrentHashMap<>();

    public static void add(User user) {
        CACHE.put(user.getId(), user);
    }
}
```

“假设用户数量持续增加，而且缓存没有容量限制、过期或清理机制，会发生什么？”

“Map 会越来越大。”

“GC 能回收这些 User 吗？”

“不能，因为静态 Map 仍然持有它们的引用。”

“这就是典型的 Java 对象滞留问题，可能构成内存泄漏。”

### GC 为什么不回收这些对象？

陈默继续解释：

“垃圾回收器不是根据对象有没有业务价值来判断是否回收。”

“而是根据对象是否仍然可达。”

“只要存在从 GC Roots 到对象的引用路径，它就可能继续存活。”

例如：

GC Root

例如被类静态字段引用的对象

static CACHE

ConcurrentHashMap

User A

User B

User C

只要仍然可达，即使业务已经不需要这些对象，GC 也无法判断它们应被删除。

林川终于理解了。

“所以内存泄漏不一定是内存没有释放，而是对象已经没有业务价值，却仍然被引用着。”

“准确。”

“不过，注意 Java 的内存泄漏与 C/C++ 的典型内存泄漏表现可能不同。”

# 第七幕：Heap Dump——给内存拍一张尸检照片

“如果你怀疑 Java 堆内存泄漏，怎么找到具体对象？”

陈默问。

林川思考片刻：

“查看 Heap Dump？”

“没错。”

“Heap Dump 就像给 Java 堆拍一张快照，记录堆中对象及其引用关系。”

### 1. 提前配置 OOM 自动转储

```
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/data/dumps
```

陈默提醒：

“这个参数很有用，但不是万能的。”

“如果是容器被内核直接 SIGKILL，通常不能指望 JVM 自动生成 Heap Dump。”

“而且 Dump 文件可能很大，可能包含用户数据、Token、密码等敏感信息，必须控制磁盘空间和访问权限。”

### 2. 手动生成 Heap Dump

```
jcmd <PID> GC.heap_dump /data/dumps/heap.hprof
```

“生产环境能随便执行吗？”林川问。

“不能。生成堆转储可能造成明显停顿、I/O 压力和额外内存开销。”

“应先评估实例负载、磁盘容量和业务影响，优先在可隔离实例或测试环境操作。”

“而且默认情况下，这类命令可能触发 Full GC；具体行为与 JDK 版本及参数有关。”

### 3. 使用 MAT 分析

陈默打开 Eclipse Memory Analyzer，简称 MAT。

“MAT 中有几个重要概念。”

| 概念               | 含义                        |
| ---------------- | ------------------------- |
| Histogram        | 按类统计对象数量和浅堆大小             |
| Dominator Tree   | 根据对象支配关系分析内存保留情况          |
| Shallow Heap     | 对象本身占用的堆空间                |
| Retained Heap    | 如果对象被移除，理论上可能释放的对象集合所占堆空间 |
| Path to GC Roots | 查找对象为什么仍然可达               |

林川看到：

```
Class                         Objects
-------------------------------------
java.util.HashMap$Node       2,100,000
com.xinghai.User             1,800,000
byte[]                         950,000
java.lang.String             3,500,000
```

“User 对象这么多，是不是 User 泄漏？”

“不能直接这么判断。”

“对象数量多，可能是业务正常需求，也可能是异常滞留。”

“要结合 Retained Heap、GC Roots 引用链、对象生命周期和业务预期。”

他们打开 Dominator Tree。

发现：

```
UserCache.CACHE
  -> ConcurrentHashMap
      -> Node[]
          -> User
          -> User
          -> User
```

“这下找到根因了。”

陈默说道：

“更准确地说，我们找到了大量 User 对象被保留的引用链。”

“接下来还要核对：这个缓存是否应该长期保存这么多用户，以及为什么没有过期策略。”

## 第八幕：五种常见 OOM，五种不同的调查方向

陈默在会议室中放下五份档案。

“林川，线上内存事故不能只背 `Java heap space`。”

“不同类型的 OOM，排查方向完全不同。”

档案一：Java heap space

堆空间无法满足对象分配。重点检查大对象、对象滞留、缓存无限增长、内存配置不足。

工具：GC 日志、Heap Dump、MAT、JFR

档案二：Metaspace

类元数据相关的原生内存不足。重点检查动态类生成、ClassLoader 泄漏、反复热加载，以及元空间限制。

工具：jcmd VM.classloader_stats、NMT、类加载指标

档案三：Unable to create native thread

无法创建新的原生线程。可能是线程数过多、系统线程或进程限制、原生内存不足。

工具：线程数量、线程栈、ulimit、cgroup pids 指标

档案四：Direct buffer memory

直接缓冲区分配失败。重点检查 NIO/Netty 缓冲区、资源释放、缓冲区池以及直接内存限制。

工具：BufferPoolMXBean、JFR、NMT、框架泄漏检测

档案五：容器 OOMKilled

容器触及内存限制并被终止。重点检查容器内存、进程 RSS、堆与原生内存、文件缓存、cgroup 事件。

工具：kubectl describe、memory.stat、memory.events、进程指标

“所以，”陈默说，“看见 OOM 之后，第一件事不是盲目调大内存，而是确定 OOM 的类型。”

# 第九幕：生产事故中的实战决策

现在，陈默给林川一道现场题。

“假设你接到告警，Java 服务内存持续增长，最终 OOM。”

“你怎么排查？”

林川没有立即回答。

他先在纸上写下三个问题：

第一，谁报的 OOM？

是 JVM 抛出 `OutOfMemoryError`，还是容器 OOMKilled？

第二，哪里在增长？

是 Heap Used、进程 RSS、容器内存，还是某个具体原生内存区域？

第三，为什么增长？

是正常业务峰值、配置不足、对象滞留、原生资源泄漏，还是线程数量异常？

陈默说道：

“很好。现在我给你一套真实工作中可以参考的排查顺序。”

### 线上内存异常排查清单

排查进度

0/8

确认故障范围、OOM 类型与退出原因

判断是否需要切流、回滚、限流或扩容止血

检查容器限制、Heap Used、RSS 和内存趋势

检查 GC 日志与对象分配速率

针对 Heap OOM 分析 Heap Dump 与 GC Roots

针对堆外增长分析 NMT、cgroup 和原生资源

复现问题并验证修复方案

灰度上线、观察指标并完成事故复盘

重置清单

## 第十幕：面试官的最后一道题

上午 9:30。

陈默坐在会议室里。

“林川，现在你来回答一道 Java 后端面试题。”

“线上 Java 服务内存持续上涨，最终 OOM，你会怎么排查和解决？”

林川回答：

“我会按照故障分类、监控定位、现场分析、修复验证四个层次展开。”

“首先判断是 JVM 抛出的 OOM，还是操作系统或容器触发的 OOMKilled。如果是容器 OOMKilled，我会检查退出原因、容器内存限制、进程 RSS 和 cgroup 内存指标。”

“其次，我会查看 JVM 堆使用量、GC 次数、GC 停顿、Old Gen 使用趋势以及堆外内存情况，判断增长发生在哪个区域。”

“如果是 Java Heap OOM，我会分析 GC 日志和 Heap Dump，通过 MAT 的 Dominator Tree、Retained Heap 和 Path to GC Roots 找到异常保留的对象，并结合业务逻辑判断是否存在缓存无限增长、集合未清理或大对象问题。”

“如果是原生内存异常，我会结合 NMT、线程数量、直接缓冲区统计和进程内存映射，进一步检查 Direct Memory、线程栈、动态类加载或第三方原生库。”

“最后根据根因采取措施，例如修复对象滞留、释放原生资源、限制缓存容量、优化批处理或调整 JVM 和容器内存预算。修复后通过压测和灰度验证内存曲线是否恢复稳定。”

陈默问：

“如果面试官追问：为什么你不直接调大 `-Xmx`？”

林川回答：

“因为调大堆只能解决部分容量不足问题，不能消除内存泄漏，而且在容器内存固定的情况下，堆越大，留给原生内存的空间可能越少，反而增加 OOMKilled 风险。”

“很好。”

陈默合上电脑。

“现在你终于明白，为什么生产环境排查不能只会背几个 JVM 参数了。”

## 本章总结：真正需要记住的五件事

1. `-Xmx` 不是 Java 进程的内存上限。 堆外还有元空间、线程栈、直接内存、JVM 原生开销等。
2. OOM 不等于内存泄漏。 容量不足、大对象、突发流量和内存滞留都可能导致 OOM。
3. 137 不一定是 OOM。 必须结合容器状态和内核或 cgroup 证据。
4. Heap Dump 主要解决 Java 堆对象问题。 对原生内存增长，还需要 NMT、RSS、cgroup、JFR 等证据。
5. 修复的关键是找到持续增长的来源。 扩容可以止血，但不能替代根因分析。

## 下一章预告

[Managed IT Services Chicago | L4IT](https://images.openai.com/static-rsc-4/yociA364B6ayVsR3sMKkH1KCDobqR0yGOrOmW9NDYaHcQpiiSOfKVsNtIPtRWtCYUdsj_5LvcjYi90SQdZ5jw_RX3sNsgc5W2TWcoUjpIdX4QYHo8Iqz2iaUeLG9Noi5NxtC1YjlEDX3ypeZ2yEXGs7HXrO6vroxlUEZYME1_7E?purpose=inline)

## 第三章：《被困住的线程——接口突然全部超时》

某天上午 10:00，星海科技的 Java 服务突然出现大规模超时。

CPU 只有 15%，内存使用正常，MySQL 也没有明显异常，但所有业务请求都堵在了 Tomcat 中。

林川起初怀疑数据库慢查询，随后发现 200 个 Tomcat 工作线程全部处于等待状态，而真正的凶手竟然藏在一个看似普通的 `synchronized` 方法中。

下一章将通过这场事故，深入理解 Tomcat 线程池、BLOCKED/WAITING/TIMED_WAITING、Java 锁竞争、死锁、Thread Dump、数据库连接池耗尽、线程池饥饿，以及为什么 CPU 很低也能导致整个服务不可用。





下一章




# 《生产环境：永不熄灭的服务器》

第一卷 · 第三章：被困住的线程——CPU 只有 15%，为什么所有接口都超时了？

## 第一幕：一场没有任何征兆的瘫痪

上午 10:07。

星海科技总部，研发中心。

林川正坐在工位上修改昨天的 RAG 文档解析服务。

突然，企业微信群响起了密集的告警。

生产环境告警

P1 严重

10:07:23 · benefit-service-prod

营销权益服务大面积超时

CPU 使用率

# 15%

JVM 堆内存

# 42%

P99 延迟

# 30s+

Tomcat 忙碌线程

# 200/200

大量 HTTP 504，用户领取优惠券失败

林川愣住了。

“CPU 才 15%，内存也正常，为什么服务器会崩？”

他第一时间查看 MySQL 监控。

连接数正常。

慢查询数量没有明显增加。

Redis 延迟正常。

RabbitMQ 消息积压也没有明显变化。

“难道是 Nginx 出问题了？”

他打开网关日志。

```
10:07:24 GET /api/coupon/receive 504 30.001s
10:07:25 GET /api/coupon/list    504 30.002s
10:07:26 GET /api/user/profile   504 30.001s
```

几乎所有接口都在超时。

此时，技术负责人陈默走了过来。

“查到什么了？”

“CPU 正常，内存正常，数据库正常，但所有请求都在超时。”

“那你有没有想过，CPU 低本身就是一条重要线索？”

林川抬起头。

“什么意思？”

陈默拉开椅子。

“如果线程一直在执行计算，CPU 可能很高。”

“但如果线程都在等待呢？”

“等待数据库？等待网络？”

“还有呢？”

“等待锁？”

陈默点点头。

“今天，我们要调查的不是一台忙碌的服务器。”

“而是一台所有工人都在上班，却没有一个人能够干活的服务器。”

[Observability vs Monitoring: Prometheus, Grafana и Loki](https://images.openai.com/static-rsc-4/bMCVjLawEN8hfXL9L0aAlKMPAKnYrG6mJkRovw4uRD7Eg29k12eVqQR4ovw2wKK8k5682ksFETGm_Ok9Fz35DWZOR6iYquyyUnm_HfBz7WGGbeMbffyvL7duqpxGkI9H4T8HPTw1kcAx5B-qE8r1HuglrqvypxkJ1G6jKDPa7Bc?purpose=inline)

[Handling Production Outages. Production outages have a way of… | by Mounick | Feb, 2026 | Medium](https://images.openai.com/static-rsc-4/WxKgs0yZ6MQlIcS-bgBEk7p-O1brt9Kk2O5bumn-zbmI8K14-_DeRn4iK1ENhMcCRGErRRPAojg7Qc1uv_AQxmVgujboNY8TezJn37hOfux8O72hwiLpDslgBXoMFSTVe5WfOoaBlXFauNmSEPZ2psIRo1Skn3HitRDMEIzQKmY?purpose=inline)

[Server dark room in datacenter with blue neon lights](https://images.openai.com/static-rsc-4/yAazFfQc7X_gvw3L93B39qvVhSUfO040kAfTTSoAytT5ZZRwXDuWgSCN1ebFAtxk0yXqhX_Bkng6Al5wvyGpJyg1A_hjWuo0qJyIZ_f2ElSOumFV7NgG4yjIy8YDdHtTk9k5SI41AZ0YVrnX3PxJOtrtK4HyBIsqRQ66ZRPOEGBlnjCVmctKtsWwQsBrpaeD?purpose=inline)

7

## 第二幕：Tomcat 王国——200 个工人全部消失了

陈默在白板上画了一座餐厅。

“林川，你知道 Tomcat 的工作线程是什么吗？”

“就是处理 HTTP 请求的线程。”

“那我们用餐厅来理解。”

“假设 Tomcat 是一家餐厅，有 200 名服务员。”

“每当用户发送 HTTP 请求，就相当于有一名顾客进入餐厅。”

“服务员负责接待顾客、处理订单，最后返回结果。”

林川点点头。

“所以，一个请求通常会占用一个工作线程？”

“在传统 Spring MVC 同步请求处理模型中，通常如此。异步 Servlet、WebFlux 等模型的线程使用方式不同。”

陈默继续画图。

用户请求

持续进入服务

Tomcat 工作线程池

200/200 忙碌

每个方格代表 10 个工作线程。全部被占用，不代表全部在执行 CPU 计算。

请求无法及时完成

后续请求排队、被拒绝或超时

“现在假设 200 名服务员全部在等一把钥匙。”

“即使餐厅还有大量食材和厨房设备，也没有人能继续服务顾客。”

林川突然明白了。

“所以 CPU 低，并不代表服务有空闲处理能力。”

“对。”

“CPU 衡量的是计算资源使用情况，不是线程是否能够完成业务。”

“线程可能因为锁、数据库连接、网络 I/O、Future 结果等原因长时间等待。”

### 一个重要区别：忙碌线程不等于 RUNNABLE 线程

陈默补充：

“Tomcat 的 busy threads 指标通常反映工作线程正在承担请求处理任务。”

“但这些线程在 JVM 中可能处于 `RUNNABLE`、`BLOCKED`、`WAITING` 或 `TIMED_WAITING` 状态。”

“因此，看到 Tomcat 忙碌线程达到上限，下一步应该查看线程栈，而不是直接增加 `maxThreads`。”

林川问：

“为什么不能直接加到 500？”

“如果 200 个线程都被同一把锁阻塞，增加到 500，只是让更多线程一起等待。”

“而且线程越多，可能带来更多内存开销、上下文切换和下游资源压力。”

## 第三幕：Thread Dump——给 200 个线程拍一张合影

“那我们怎么知道线程在等待什么？”

林川问。

陈默打开终端。

“先找到 Java 进程。”

```
jps -l
```

输出：

```
18432 com.xinghai.BenefitApplication
```

“然后抓取线程快照。”

```
jcmd 18432 Thread.print -l > /tmp/thread-1.txt
```

陈默又连续抓取了两次。

“为什么要多次采样？”

“因为单次线程快照只能反映一个瞬间。如果连续多次看到相同线程等待相同资源，就能获得更强的证据。”

他打开文件。

```
"http-nio-8080-exec-17"
   java.lang.Thread.State: BLOCKED
    at com.xinghai.coupon.CouponService.receive(CouponService.java:48)
    - waiting to lock <0x000000071a2b3c40>
```

林川问：

“`BLOCKED` 是什么意思？”

“在 Java 的线程状态中，`BLOCKED` 通常表示线程正在等待进入一个 `synchronized` 监视器，或者等待重新获取该监视器。”

“那 `waiting to lock` 后面是什么？”

“是它正在等待的对象监视器标识。”

林川继续往下看。

```
"http-nio-8080-exec-18"
   java.lang.Thread.State: BLOCKED
    at com.xinghai.coupon.CouponService.receive(CouponService.java:48)
    - waiting to lock <0x000000071a2b3c40>
```

再往下：

```
"http-nio-8080-exec-19"
   java.lang.Thread.State: BLOCKED
    at com.xinghai.coupon.CouponService.receive(CouponService.java:48)
    - waiting to lock <0x000000071a2b3c40>
```

十个。

五十个。

一百个。

大量线程都在等待同一个监视器。

林川猛地站起来。

“找到了！所有线程都在争同一把锁！”

陈默却没有急着下结论。

“我们已经找到了大量等待者。”

“现在还有一个更重要的问题。”

“什么？”

“谁拿着这把锁？它为什么迟迟不释放？”

## 第四幕：锁的主人

林川搜索监视器标识。

```
grep -n -B 15 -A 25 '0x000000071a2b3c40' \
  /tmp/thread-1.txt
```

终于，他找到了持锁线程。

```
"http-nio-8080-exec-7"
   java.lang.Thread.State: TIMED_WAITING
    at jdk.internal.misc.Unsafe.park(Native Method)
    at java.util.concurrent.locks.LockSupport.parkNanos(...)
    at java.util.concurrent.CompletableFuture.get(...)
    at com.xinghai.rule.RemoteRuleClient.query(...)
    at com.xinghai.coupon.CouponService.receive(...)

    - locked <0x000000071a2b3c40>
```

林川看着这段栈，陷入沉思。

“等等。”

“这个线程不是 `BLOCKED`，而是 `TIMED_WAITING`。”

“它不是已经不运行了吗？”

陈默摇头。

“线程进入等待状态，不代表它自动释放已经持有的 synchronized 锁。”

“你看，线程栈里还有一行。”

```
- locked <0x000000071a2b3c40>
```

“说明它仍然持有这把监视器。”

林川突然意识到问题。

“也就是说，一个线程拿着锁去等待远程服务，其他所有线程都进不来？”

“没错。”

“这就是整个事故的核心。”

### 事故现场的线程关系

线程 A：持有锁

持有者

进入 synchronized，调用远程规则服务，等待响应

JVM 状态：TIMED_WAITING

CouponService 的对象监视器

同一时刻只允许一个线程持有

线程 B～N：等待锁

BLOCKED

大量 Tomcat 工作线程无法进入业务方法

陈默解释：

“一个线程正在等待远程 I/O。”

“其他线程正在等待这个线程释放锁。”

“所以 CPU 不高，因为大量线程没有执行计算。”

“但 Tomcat 的工作线程全部被占用了，服务吞吐量迅速下降。”

“如果其他接口也依赖同一个 Tomcat 工作线程池，那么即使它们完全不使用这把锁，也可能因为拿不到工作线程而超时。”

林川点点头。

“原来一次局部锁竞争，竟然能导致整个服务不可用。”

## 第五幕：罪魁祸首——一个 synchronized 关键字

两人打开代码仓库。

```
@Service
public class CouponService {

    private final RemoteRuleClient ruleClient;

    public CouponService(RemoteRuleClient ruleClient) {
        this.ruleClient = ruleClient;
    }

    public synchronized CouponResult receive(Long userId) {
        // 查询远程规则服务
        Rule rule = ruleClient.query(userId);

        // 校验资格
        checkRule(rule);

        // 扣减库存
        deductStock(userId);

        return CouponResult.success();
    }
}
```

林川看了几秒。

“这个方法为什么加了 `synchronized`？”

陈默打开 Git 历史。

提交说明写着：

> 修复高并发情况下优惠券重复领取问题。

林川恍然大悟。

“原来开发人员担心并发安全，就给整个方法加锁。”

“是的。但这带来了三个严重问题。”

### 问题一：锁的粒度太大

陈默说道：

“假设整个方法需要 500ms，其中真正需要互斥的操作只有 5ms。”

“如果给整个方法加锁，所有请求都必须串行执行这 500ms。”

“理论上，单实例这段串行路径的吞吐量上限大约是：”

\\[ QPS \approx \frac{1}{0.5}=2 \\]

“也就是每秒只能完成大约两个请求。”

“但如果能够安全地把临界区缩小到 5ms，单从这段串行临界区的理论上限看：”

\\[ QPS \approx \frac{1}{0.005}=200 \\]

“当然，真实吞吐量还会受到 CPU、数据库、网络和其他共享资源限制。”

“但这说明锁的持有时间有多么重要。”

### 问题二：锁里面存在远程调用

陈默指着：

```
Rule rule = ruleClient.query(userId);
```

“这段调用的耗时由谁决定？”

“远程规则服务。”

“如果它平时只需要 30ms，但今天突然变成 10 秒呢？”

“那么当前线程可能持锁等待 10 秒。”

“如果远程客户端没有合理的超时设置，等待甚至可能更长。”

陈默补充：

“即使设置了超时，也要考虑连接超时、读取超时、请求总超时和重试策略之间的关系。不能只配置一个数字，就以为整个调用一定能在这个时间内结束。”

### 问题三：synchronized 只能保护当前 JVM 内的监视器

林川突然想到：

“可是我们线上部署了三个 Spring Boot 实例。”

“对。”

“每个实例都有自己的 CouponService Bean，也有自己的对象锁。”

“那么三个实例之间的锁根本不互通？”

“正确。”

“所以，这个 synchronized 不仅导致了严重性能问题，甚至不能完整解决分布式环境下的重复领取问题。”

陈默在白板上写下：

\\[ \text{JVM 内互斥}\neq\text{分布式业务唯一性} \\]

“这就是很多初级工程师容易犯的错误。”

“把线程安全、业务幂等、数据库一致性和分布式协调当成同一件事。”

## 第六幕：真正的解决方案

林川立即说道：

“那我们把 synchronized 删除不就行了？”

陈默表情严肃起来。

“你确定？”

“……”

“如果删除之后，两个并发请求同时领取同一张优惠券，怎么办？”

林川沉默。

“所以线上修复不能只考虑性能，还要保证业务正确性。”

“这次我们需要重新设计并发控制。”

### 方案一：把远程调用移出锁

陈默先给出了一个最小改动的思路。

```
public CouponResult receive(Long userId) {
    // 不持锁执行远程调用
    Rule rule = ruleClient.query(userId);

    synchronized (this) {
        checkRule(rule);
        deductStock(userId);
        return CouponResult.success();
    }
}
```

“这样能缩短锁的持有时间，但仍然存在两个问题。”

“第一，所有用户依旧争抢同一把锁。”

“第二，这把锁仍然只能保护当前实例。”

“而且如果锁内执行数据库或 Redis 远程操作，依然可能出现长时间持锁。”

林川问：

“那真正的生产方案呢？”

“根据业务不变量设计原子操作和持久化约束。”

### 方案二：Redis Lua + MySQL 唯一索引 + 异步履约

陈默重新画出权益发放链路。

用户领取请求

远程规则查询

设置合理超时、限流和失败策略

Redis Lua 原子执行

资格校验 / 去重 / 库存预扣

可靠投递履约任务

通过 Outbox 等机制避免状态与消息不一致

RabbitMQ 消费者

异步执行履约

MySQL 持久化

唯一约束、状态机、幂等消费

“Redis Lua 可以保证脚本中的操作在单个 Redis 执行上下文中原子执行，避免多个请求交错修改同一份库存和领取标记。”

“但 Redis 原子性不等于 Redis、RabbitMQ 和 MySQL 三者之间存在一个原子事务。”

林川点点头。

“所以还需要消息可靠投递、消费幂等、失败补偿，以及最终状态对账。”

“没错。”

“对于用户重复领取，MySQL 可以设置类似 `(activity_id, user_id)` 的唯一约束，前提是业务规则确实规定每人每活动只能领取一次。”

“而对于跨服务履约，需要根据业务决定何时返回领取成功、如何处理库存预占超时、如何补偿失败任务。”

林川总结：

“原来正确解决并发问题，不是给所有代码套一把锁，而是识别真正需要保证的业务不变量，再选择合适的原子操作和一致性机制。”

“正是如此。”

# 第七幕：四种线程状态，四种完全不同的故障

事故恢复后，陈默没有让林川离开。

“你今天只遇到了 `BLOCKED`。”

“但生产环境还有其他线程状态，排查方式不同。”

他打开 Java 的 `Thread.State` 枚举。

## 1. RUNNABLE：正在运行，或者准备运行

“如果一个线程处于 `RUNNABLE`，意味着它在 JVM 线程状态模型中处于可执行状态。”

“但要注意，在 HotSpot/Linux 上，某些执行原生 I/O 的线程也可能显示为 RUNNABLE。”

“因此不能直接认为 RUNNABLE 就一定在消耗 CPU。”

典型问题：

- 死循环。
- 大量 JSON 序列化。
- 高复杂度算法。
- 部分网络 I/O 或原生调用。

排查时结合：

```
top -H -p <PID>
```

以及线程栈、CPU Profiling。

## 2. BLOCKED：等待进入 synchronized

典型线程栈：

```
java.lang.Thread.State: BLOCKED
- waiting to lock <0x12345678>
```

“这种情况，优先寻找锁的持有者。”

“如果大量线程都在等待同一个监视器，说明可能存在严重的锁竞争。”

## 3. WAITING：无限期等待某个条件

例如：

```
future.get();
```

当结果尚未完成且没有设置超时，线程可能一直等待。

但陈默提醒：

“`WAITING` 不一定是异常。”

“线程池中的空闲工作线程可能正常地等待任务。”

“所以不能简单统计 WAITING 数量，就认定系统故障。”

## 4. TIMED_WAITING：有限时间等待

例如：

```
Thread.sleep(1000);
```

或者：

```
future.get(3, TimeUnit.SECONDS);
```

“它意味着线程进入了带时间限制的等待状态，但不代表业务一定会在预期时间完成。”

“例如多次重试、嵌套调用和多个超时叠加，仍可能让整体请求耗时很长。”

### Java 线程状态速查

| 状态            | 典型场景                | 排查重点        |
| ------------- | ------------------- | ----------- |
| NEW           | 线程尚未启动              | 通常不是线上阻塞根因  |
| RUNNABLE      | 计算、可运行、部分原生 I/O     | CPU、调用栈     |
| BLOCKED       | 等待 synchronized 监视器 | 锁持有者、临界区    |
| WAITING       | 无超时等待结果或条件          | 等待对象、唤醒条件   |
| TIMED_WAITING | sleep、带超时等待         | 超时设置、重试     |
| TERMINATED    | 线程执行结束              | 线程异常退出或正常结束 |

# 第八幕：另一场灾难——数据库连接池耗尽

下午 2:30。

陈默突然给林川发来一份新的事故日志。

“这是另一个服务的 Thread Dump。”

```
"http-nio-8080-exec-31"
   java.lang.Thread.State: TIMED_WAITING
    at jdk.internal.misc.Unsafe.park(...)
    at java.util.concurrent.locks.LockSupport.parkNanos(...)
    at com.zaxxer.hikari.pool.HikariPool.getConnection(...)
```

林川看完说道：

“线程在等待数据库连接。”

“对。”

“假设 HikariCP 最大连接池只有 20 个连接，但有 200 个 Tomcat 请求线程。”

“当 20 个连接全部被占用，后续请求会怎样？”

“等待空闲连接。”

“如果连接长时间不归还呢？”

“等待线程不断积累，最终可能耗尽 Tomcat 工作线程。”

陈默问：

“那你第一反应是不是把连接池从 20 改成 200？”

林川笑了。

“不能直接改。”

“为什么？”

“因为连接池耗尽可能是 SQL 太慢、事务持有连接过久、连接泄漏，或者数据库本身处理能力不足。”

“增加连接数可能把压力直接转移到 MySQL。”

“很好。”

### 数据库连接池耗尽的典型链路

慢 SQL / 长事务 / 连接未归还

数据库连接长期被占用

HikariCP 无空闲连接

Tomcat 工作线程等待连接

接口超时，服务吞吐量下降

“这就是为什么 CPU 很低，服务却可能完全不可用。”

“因为系统的瓶颈不一定是 CPU。”

“可能是任何一个容量有限的共享资源。”

## 第九幕：线程池饥饿——工人等待自己完成任务

陈默又拿出一段代码。

```
ExecutorService pool =
    Executors.newFixedThreadPool(1);

Future<String> outer = pool.submit(() -> {
    Future<String> inner = pool.submit(() -> {
        return "done";
    });

    return inner.get();
});

System.out.println(outer.get());
```

“林川，这段代码会发生什么？”

林川思考了几秒。

“线程池只有一个线程。”

“外层任务占用了唯一的工作线程。”

“然后外层任务又往同一个线程池提交内部任务。”

“接着调用 `inner.get()` 等待内部任务完成。”

“但内部任务需要工作线程才能执行，而唯一的线程正被外层任务占着。”

他猛地抬头。

“所以内部任务永远无法执行！”

“对。”

“这叫线程池饥饿死锁的一种典型形式。”

### 死锁并不一定发生在 synchronized 上

陈默解释：

“很多人一提到死锁，就只想到两个线程互相持有两把锁。”

“但线程池、Future、信号量和其他有限资源，也可能形成循环等待。”

“在这段代码中，外层任务等待内层任务完成，而内层任务等待工作线程空闲。”

“双方形成无法自行解除的等待关系。”

外层任务 A

占有唯一工作线程

等待内层任务 B 完成

任务 B 无法执行

线程池唯一线程被任务 A 占用

循环等待，程序无法自行取得进展

林川问：

“那应该怎么解决？”

陈默回答：

“优先避免在同一个容量有限的线程池中，提交子任务后又同步等待子任务。”

“可以重新组织任务依赖关系、使用合适的异步组合方式，或者在确有必要时隔离不同任务类型的执行资源。”

“但单纯增大线程池容量，仍可能只是暂时缓解。”

# 第十幕：真正的死锁——两把锁与两个囚徒

陈默决定再加一道题。

“假设两个线程分别持有两把锁。”

“线程 A 持有 Lock1，等待 Lock2。”

“线程 B 持有 Lock2，等待 Lock1。”

“会发生什么？”

“死锁。”

“写出来。”

林川打开 IDE。

```
public class DeadlockDemo {

    private static final Object LOCK1 = new Object();
    private static final Object LOCK2 = new Object();

    public static void main(String[] args) {

        Thread t1 = new Thread(() -> {
            synchronized (LOCK1) {
                synchronized (LOCK2) {
                    System.out.println("T1 finished");
                }
            }
        });

        Thread t2 = new Thread(() -> {
            synchronized (LOCK2) {
                synchronized (LOCK1) {
                    System.out.println("T2 finished");
                }
            }
        });

        t1.start();
        t2.start();
    }
}
```

陈默说道：

“注意，这段代码存在死锁风险，但不保证每次运行都发生死锁，因为线程调度顺序不同。”

“现在你告诉我，死锁的四个必要条件是什么？”

林川回答：

1. 互斥条件：资源同一时刻只能被一个线程占有。
2. 请求并保持条件：线程持有资源的同时继续等待其他资源。
3. 不可剥夺条件：已获得的资源不能被其他线程强制夺走。
4. 循环等待条件：多个线程之间形成循环等待链。

“正确。”

“那如何解决？”

“最常见的方式之一是统一加锁顺序，破坏循环等待条件。”

例如所有线程都按：

```
synchronized (LOCK1) {
    synchronized (LOCK2) {
        // business logic
    }
}
```

“此外，对于 `ReentrantLock`，可以在适当场景下使用 `tryLock` 和超时机制，避免无限期等待。”

“但必须注意获取失败后的释放、重试、回滚和业务一致性处理。”

### 生产环境怎么发现死锁？

```
jcmd <PID> Thread.print -l
```

HotSpot 在支持的场景下，可以检测并报告 Java 监视器或部分显式锁相关的死锁。

但陈默提醒：

“并不是所有逻辑上的死锁都能被 JVM 自动识别。”

“例如刚才的线程池饥饿问题，可能没有传统的锁循环关系。”

“所以依然需要根据任务依赖、线程状态和资源使用情况进行分析。”

# 第十一幕：真正的生产排查流程

下午 5:10。

林川把今天的事故整理成了一套方法。

陈默看完后，只改了一个地方。

“你写的是先抓线程栈，再止血。”

“但如果业务已经大面积不可用，你应该先判断是否需要立即止血。”

“排查和止血可以并行，但不能为了研究问题而无限拖延恢复业务。”

### CPU 低、接口超时的排查路线

接口超时，CPU 不高

确定影响范围、保留证据、评估止血

抓取多份 Thread Dump

大量 BLOCKED

找锁持有者、临界区

大量 WAITING

找 Future、条件与资源依赖

大量 TIMED_WAITING

查超时、连接池、重试

大量 RUNNABLE

结合 CPU、I/O、原生栈

验证根因 → 修复 → 压测 → 灰度 → 复盘

陈默补充：

“还要同时看几个关键指标。”

| 指标                          | 主要用途        |
| --------------------------- | ----------- |
| Tomcat busy threads         | 判断工作线程是否被占满 |
| Tomcat current threads      | 判断线程池当前规模   |
| HikariCP active connections | 判断数据库连接占用   |
| HikariCP pending threads    | 判断是否有线程等待连接 |
| 线程状态分布                      | 判断是否存在集中等待  |
| 接口 P95/P99                  | 判断尾延迟是否恶化   |
| 下游调用耗时                      | 定位远程依赖      |
| 线程池队列长度                     | 判断任务是否积压    |

“另外，所有线程池和连接池的指标，都应该结合业务吞吐量、错误率和时间趋势分析，不能只凭某一个瞬时数字下结论。”

# 第十二幕：面试官的拷问

第二天上午。

陈默坐在会议室里，打开录音笔。

“现在假设你在面试一家大型互联网公司的 Java 后端岗位。”

“我问你一个场景题。”

面试官：线上接口突然大量超时，但 CPU 和内存都正常，你会怎么排查？

林川思考了几秒，开始回答。

“首先，我会确认故障范围，包括是否所有接口都超时、是否只有部分实例异常，以及最近是否存在发布或流量变化。”

“如果业务影响严重，我会优先评估回滚、切流、限流或降级，同时尽可能保留现场信息。”

“然后我会查看 Tomcat 工作线程数、线程池队列、数据库连接池和下游调用耗时，判断是否存在资源耗尽。”

“如果 Tomcat 工作线程接近上限，我会通过 `jcmd Thread.print` 获取多份线程栈，观察线程主要处于什么状态。”

“如果大量线程处于 `BLOCKED`，我会寻找共同等待的锁及其持有者，检查是否存在锁粒度过大、锁内远程调用或死锁。”

“如果大量线程等待数据库连接，我会检查 HikariCP 的 active、idle、pending 指标，并结合 MySQL 慢 SQL、长事务和连接泄漏情况定位问题。”

“如果线程在等待 Future 或远程服务，我会检查任务依赖、超时配置、重试策略和下游服务状态，判断是否存在同步等待、线程池饥饿或下游阻塞。”

“最后根据根因优化锁粒度、隔离线程池、修复连接泄漏、调整超时或重构业务流程，再通过压测和灰度验证。”

陈默问：

“为什么不直接增加 Tomcat 的 maxThreads？”

林川回答：

“因为如果瓶颈是锁竞争、数据库连接池或下游服务，增加 Tomcat 线程数不能提高瓶颈资源的处理能力，反而可能增加等待线程、内存占用和下游压力。”

陈默继续追问：

“那为什么 CPU 只有 15%，系统却完全不可用？”

林川回答：

“因为 CPU 使用率只反映计算资源消耗。大量线程可能因为锁、I/O、连接池或任务依赖而阻塞，虽然不消耗多少 CPU，但仍然占用有限的请求处理资源，最终导致新请求无法及时处理。”

陈默合上录音笔。

“这次你真正理解了线程池和锁，而不是只会背 `synchronized` 和 `ReentrantLock` 的区别。”

## 本章技术总结

CPU 低不代表系统健康。 阻塞、等待和有限资源耗尽都可能导致服务不可用。

Tomcat 工作线程被占满，不等于 CPU 被打满。 工作线程可能正在等待锁、连接或下游响应。

锁的持有者比等待者更重要。 排查大量 BLOCKED 线程时，要找到谁持锁以及为什么不释放。

不要在大范围锁中执行慢 I/O。 远程调用、数据库操作和长时间等待可能显著放大锁竞争。

线程池、数据库连接池和锁都是有限资源。 扩大其中一个池，不代表整体吞吐量一定提高。

## 下一章预告

[ChipSoft Ransomware Attack Disrupts Dutch Hospital Network](https://images.openai.com/static-rsc-4/uxc2xu49NcK2mCPM7pGzNAVlZc3pqCYbiwkGo3DKbXnmJCAzQWKq03Tq9QVpOYE7KahIFotAf27i2phGb7h97K2pXGwo6fuxun5XFJ9xlDYT_w42tGFBVVrKcyt33YvdhuytYeQnllxeYe1TOtQpzXGwikawtmbUJunOInEH5Cw?purpose=inline)

## 第四章：《数据库的死亡倒计时——一条 SQL 拖垮整个系统》

上午 11:20，营销系统的订单查询接口突然从 30ms 飙升到 18 秒。

MySQL CPU 达到 95%，数据库连接池逐渐耗尽，所有依赖数据库的接口开始超时。

但开发人员坚称：“这条 SQL 已经加索引了，不可能慢！”

林川随后发现，真正的问题竟然隐藏在一个看似普通的 `ORDER BY` 和 `LIMIT 1000000, 20` 中。

下一章将围绕一次完整的 MySQL 生产事故，深入讲解 慢 SQL 定位、EXPLAIN、EXPLAIN ANALYZE、索引失效、回表、覆盖索引、深分页、排序、临时表、连接池耗尽，以及 SQL 优化为什么必须结合真实数据分布和执行计划。




下一章。



# 《生产环境：永不熄灭的服务器》

第一卷 · 第四章：数据库的死亡倒计时——一条 SQL 如何拖垮整个系统

## 第一幕：上午十一点，数据库开始窒息

上午 11:20。

星海科技，研发中心。

林川刚刚解决了上一场线程池阻塞事故。

他以为自己已经掌握了线上故障排查的基本方法。

直到一条来自 MySQL 的告警出现在屏幕上。

MySQL 生产集群告警

P1 严重

11:20:36 · mysql-order-primary

MySQL CPU

# 95%

订单查询 P99

# 18.4s

HikariCP 活跃连接

# 50/50

接口错误率

# 32.7%

订单列表接口大面积超时，部分支付查询请求受影响

“又出事了？”

林川打开 Grafana。

过去十分钟，订单查询接口的响应时间从几十毫秒一路上涨。

订单查询延迟变化（模拟事故数据）

数据库压力升高后，接口尾延迟迅速恶化

0 s5 s10 s15 s20 s11:1011:1211:1411:1611:1811:20

他立即查看应用日志。

```
SQLTransientConnectionException:
HikariPool-1 - Connection is not available,
request timed out after 30000ms.
```

“数据库连接池耗尽？”

林川想起了上一章。

“是不是连接泄漏？”

这时，技术负责人陈默走进办公室。

“先别下结论。”

“连接池耗尽只是现象。连接可能没有泄漏，而是被长时间运行的 SQL 占用了。”

“那该怎么判断？”

陈默打开数据库监控。

“今天我们要调查的是一条 SQL。”

“它没有死循环，没有语法错误，甚至使用了索引。”

“但它几乎拖垮了整个数据库。”

[DraftKings Eyes $57M NFL Prediction Market Windfall in 2026 Season | iGaming Pulse | iGaming Pulse](https://images.openai.com/static-rsc-4/o4L9evu1A2cUsHO5bAsq-RtRQUtvKFNc2arcHo2_cOihtW9_jd_dPmgK2Xl6wPtpmHOK1TqPVqOvvR6H__oCe_D3-Lnz1-Qg7aoG2Ruv7Tk4L41Lxk_IW7fQpysAqRUeKc7UdhoKhn5lXiTWEuACKnKhb8ultApVl2AVNQ0DRtw?purpose=inline)

[Database Schema Design & Zero-Downtime Migrations (Postgres) | by QuarkAndCode | Medium](https://images.openai.com/static-rsc-4/DGwXXiEGHlN5GaAUhGeFl0gP2UeF7NGRSbfSHok6b-rhYjlyUA6PhZ6klV2QNEOvps_lzW91mXtSxdAr4_KEkFKeWNMcupZ3hZ1P5JU0j11zLtfz2Ome5csPmFEAP9hCDVbEvqWBPD3uMgLjhmJMNXPlt6r93mc12LZt0zAkV3s?purpose=inline)

[Heroku → Aurora移行の全記録｜Claude Code + MCPで深夜3時のDB移行監視をどう乗り切ったか｜ウェブ系ウシジマくん](https://images.openai.com/static-rsc-4/9L_yY7BhBLXfNHdQxVLE_AzqvcH3V-hxA7y69x0Tvlk0W8YQadC_U675Aal5i2OVWH1mKRW3v2z78cBOGlL6vS6MS43R4Wvv-tHnVTNYZnkxcyoDn5VCEAkKbO1zEXya2zWnfIN14nXO9pAuwP7EpIpagZZObyXa6tYvm5j_0XY?purpose=inline)

7

## 第二幕：第一条线索——连接池为什么耗尽？

陈默没有立即查看 SQL。

他先问了一个问题。

“假设你的 HikariCP 最大连接数是 50，为什么会被占满？”

林川回答：

“可能是并发请求太多，也可能是 SQL 执行太慢、事务太长，或者连接没有归还。”

“很好。”

“那我们先理解连接池为什么会被慢 SQL 拖垮。”

### 一条请求的生命

正常情况下：

HTTP 请求进入 Spring Boot

从 HikariCP 获取数据库连接

执行 SQL

正常：20ms

归还连接，返回响应

陈默在白板上写下一条公式：

\\[ L=\lambda W \\]

“这是 Little 定律。”

“在稳定系统中，平均在系统内的请求数量，等于吞吐率乘以平均停留时间。”

“假设每秒有 100 个需要数据库连接的请求，每个请求平均占用连接 20ms。”

\\[ 100\times0.02=2 \\]

“平均大约需要两个被占用的连接。”

“但是，如果 SQL 从 20ms 变成 2 秒呢？”

\\[ 100\times2=200 \\]

林川一惊。

“平均需要 200 个连接才能维持同样的吞吐！”

“对。但你的连接池只有 50 个。”

“于是请求开始等待连接，排队越来越严重。”

“注意，这里的 200 是假设系统仍能稳定维持原有吞吐时的平均并发占用需求，并不是说连接池真的能提供 200 个连接。实际上，系统会受到容量限制，吞吐下降并出现排队和超时。”

### 为什么慢 SQL 会引起连锁故障？

SQL 执行时间增长

数据库连接占用时间变长

HikariCP 活跃连接达到上限

Tomcat 工作线程等待连接

接口超时，错误率上升

共享连接池中的其他接口也可能受到影响

“所以，”陈默说道，“线上排查最重要的是区分根因与连锁反应。”

“数据库连接池耗尽，可能只是慢 SQL 的下游症状。”

## 第三幕：寻找凶手——究竟是哪条 SQL？

林川打开 MySQL 终端。

“我先执行 `SHOW PROCESSLIST`。”

```
SHOW FULL PROCESSLIST;
```

屏幕上出现大量类似记录：

```
Id     Time   State          Info
-----------------------------------------------
421    12     Sending data   SELECT ... FROM orders
427    15     Sending data   SELECT ... FROM orders
435    17     Sending data   SELECT ... FROM orders
```

“都是订单查询！”

陈默说道：

“`SHOW FULL PROCESSLIST` 可以帮助我们查看当前连接及正在执行的语句。”

“不过，`Sending data` 这样的状态名不能直接理解为正在向客户端传输数据。它也可能涵盖读取、处理和返回查询结果的过程。”

“我们需要进一步确认哪类 SQL 消耗了最多资源。”

### 第一件武器：慢查询日志

```
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';
```

陈默解释：

“慢查询日志可以记录执行时间超过阈值的语句。”

“但线上修改日志配置需要考虑日志量、I/O 和管理规范，不能随意在高负载数据库上开启大量详细日志。”

林川查看已有的慢查询日志。

```
Query_time: 18.241
Rows_examined: 1000020
Rows_sent: 20
```

下面是一条 SQL：

```
SELECT
    id,
    user_id,
    amount,
    status,
    created_at
FROM orders
WHERE status = 1
ORDER BY created_at DESC
LIMIT 1000000, 20;
```

林川皱起眉头。

“这条 SQL 看起来很普通。”

“而且 `status` 和 `created_at` 都有索引。”

陈默问：

“你觉得数据库为了返回 20 条记录，需要处理多少条？”

“20 条？”

“你再看看 `LIMIT`。”

林川看了一眼。

```
LIMIT 1000000, 20
```

他突然意识到问题。

“要跳过前面一百万条！”

陈默点点头。

“这就是今天的第一个凶手。”

## 第四幕：深分页——为了寻找二十个人，翻过一百万份档案

陈默在白板上画了一座巨大的档案馆。

“假设数据库是一座档案馆。”

“你想找最新的 20 份订单。”

“如果直接取第一页，管理员只需要找到最前面的 20 份。”

“但如果你说，先跳过一百万份，再给我后面的 20 份呢？”

林川回答：

“那管理员就得先走过前面一百万份。”

“对。”

“即使这些档案已经按照时间排序，也不代表数据库可以直接跳到第 1000001 条。”

### LIMIT 的真正含义

```
LIMIT 1000000, 20;
```

相当于：

```
LIMIT 20 OFFSET 1000000;
```

在典型的有序索引扫描执行计划中，MySQL 需要扫描或跳过大量符合条件的索引记录，才能返回最后 20 条。

如果还涉及回表、排序、过滤等操作，成本可能进一步增加。

深分页扫描示意

跳过 1,000,000 条

返回 20 条

需要扫描或跳过

## 1,000,020

最终返回

## 20

这是典型有序索引扫描下的示意，实际扫描行数由过滤条件、索引、优化器执行计划和数据分布决定。

林川问：

“可是我们给 `created_at` 建了索引，为什么还是慢？”

陈默回答：

“因为索引解决的是查找和有序访问的问题。”

“它不能自动消除深分页需要跳过大量记录的成本。”

“使用了索引，不等于 SQL 一定高效。”

## 第五幕：EXPLAIN——审问 MySQL 优化器

“那我们怎么知道 MySQL 到底执行了什么？”

林川问。

陈默打开终端。

“用 `EXPLAIN`。”

```
EXPLAIN
SELECT
    id, user_id, amount, status, created_at
FROM orders
WHERE status = 1
ORDER BY created_at DESC
LIMIT 1000000, 20;
```

假设查询计划如下：

| type  | key            | rows    | Extra       |
| ----- | -------------- | ------- | ----------- |
| index | idx_created_at | 2500000 | Using where |

林川问：

“`type=index` 不是说明走索引了吗？”

“是使用了索引扫描访问方式，但并不代表只读取了少量数据。”

“`index` 往往意味着扫描索引中的一段甚至大量条目。”

“和 `const`、`ref`、`range` 等访问方式相比，不能单凭名称判断实际性能，仍然要结合扫描量和执行时间。”

### EXPLAIN 中最值得关注的字段

| 字段            | 主要含义             |
| ------------- | ---------------- |
| type          | 表访问方式            |
| possible_keys | 优化器认为可能使用的索引     |
| key           | 实际选择的索引          |
| rows          | 估计需要检查的行数        |
| filtered      | 估计过滤后保留的比例       |
| Extra         | 排序、覆盖索引、临时表等额外信息 |

陈默继续说道：

“尤其注意，`rows` 通常是优化器估算值，不是实际扫描行数。”

“如果要看实际执行情况呢？”

林川回答：

“`EXPLAIN ANALYZE`？”

“对。MySQL 8.0.18 及之后的版本支持它。”

```
EXPLAIN ANALYZE
SELECT ...
```

“它会真正执行语句，并给出执行计划中各节点的实际耗时和行数信息。”

“所以线上使用时必须谨慎，尤其不能在事故高峰期随意执行可能产生巨大开销的查询。”

### EXPLAIN 与 EXPLAIN ANALYZE 的区别

EXPLAIN

主要展示优化器选择的执行计划和估算成本，通常不实际执行目标 SELECT。

EXPLAIN ANALYZE

实际执行语句并收集运行时统计，可以对比估算行数和实际行数，发现优化器估计偏差。

“林川，记住。”

“优化 SQL，不是看有没有索引。”

“而是看 MySQL 实际如何访问数据、处理多少行、执行多少次操作，以及耗费多少时间。”

## 第六幕：第二个凶手——索引明明存在，为什么还要排序？

林川继续检查订单表结构。

```
CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status TINYINT NOT NULL,
    created_at DATETIME NOT NULL,

    KEY idx_status (status),
    KEY idx_created_at (created_at)
);
```

“我们已经有 `status` 和 `created_at` 两个索引。”

“那为什么还会慢？”

陈默反问：

“你的 SQL 需要做哪两件事？”

“先过滤 `status = 1`，然后按照 `created_at DESC` 排序。”

“那两个独立索引就一定能同时高效完成过滤和排序吗？”

“不一定。”

“对。”

“如果 MySQL 使用 `idx_status` 找到所有状态为 1 的订单，它可能还需要对结果进行排序。”

“如果使用 `idx_created_at` 按时间顺序扫描，它可能需要逐条判断 `status` 是否等于 1。”

“优化器会根据统计信息和成本模型选择计划。”

### 联合索引登场

陈默写下：

```
CREATE INDEX idx_status_created_id
ON orders(status, created_at DESC, id DESC);
```

“对于下面的查询：”

```
SELECT id, user_id, amount, status, created_at
FROM orders
WHERE status = 1
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

“这个联合索引通常更有利于按照 `status` 定位，再按照 `created_at` 和 `id` 的顺序读取数据。”

“因为 `status` 是等值条件，后续索引列的顺序可以用于满足排序要求。”

林川问：

“为什么还要加 `id`？”

“因为 `created_at` 可能重复。”

“如果只按时间排序，多个订单的时间相同，分页边界可能不稳定。”

“加上唯一的 `id`，就能形成确定性的排序顺序。”

### 联合索引的排列方式为什么重要？

陈默画出一个 B+ 树索引的简化顺序。

联合索引 `(status, created_at DESC, id DESC)`

先按 status 分组排序

status = 0

按时间和 ID 排序

status = 1

按时间和 ID 排序

这是索引逻辑顺序的简化表示，并非真实 B+ 树页面结构。

“但要注意，”陈默补充，“联合索引不是越长越好。”

“它会增加存储空间和写入维护成本。”

“而且是否真正使用索引完成排序，还要看查询条件、排序方向、执行计划和 MySQL 版本。”

## 第七幕：回表——索引找到了地址，却还要跑一趟仓库

林川突然问：

“既然联合索引已经包含 `status`、`created_at` 和 `id`，为什么查询仍然可能很慢？”

陈默回答：

“因为你的 SELECT 还需要 `user_id` 和 `amount`。”

“而它们不在这个二级索引中。”

“这就涉及回表。”

### InnoDB 的两种索引

陈默解释：

“在 InnoDB 中，聚簇索引的叶子记录存储整行数据。”

“对于常见的以主键作为聚簇索引的表，二级索引的叶子记录包含索引列和用于定位聚簇记录的主键值。”

“因此，当查询需要的字段不在二级索引中时，MySQL 可能需要根据主键再次访问聚簇索引。”

这就是回表。

二级索引

status、created_at、id

获取对应主键 id

回到聚簇索引

读取 user_id、amount 等字段

“如果深分页过程中，执行计划对大量候选行进行回表，成本可能很高。”

“那怎么优化？”

“其中一种方式是先在覆盖索引中完成分页，取得少量 ID，再根据这些 ID 获取完整数据。”

例如：

```
SELECT o.id, o.user_id, o.amount,
       o.status, o.created_at
FROM orders o
JOIN (
    SELECT id
    FROM orders
    WHERE status = 1
    ORDER BY created_at DESC, id DESC
    LIMIT 1000000, 20
) page ON o.id = page.id
ORDER BY o.created_at DESC, o.id DESC;
```

林川眼睛一亮。

“内层查询只使用索引列，减少大规模回表，外层只对 20 条记录获取完整字段。”

“对。”

“不过，这并没有消除跳过一百万条索引记录的成本。”

“所以它只是针对某些执行计划的优化，而不是深分页的根本解决方案。”

## 第八幕：真正的解决方案——游标分页

陈默关闭了旧 SQL。

“现在我们不再让数据库翻过一百万条记录。”

“我们换一种思路。”

“假设用户已经看到了第 100 页。”

“他想看下一页。”

“你真的需要告诉数据库，这是第 101 页吗？”

林川思考片刻。

“不一定。”

“如果知道上一页最后一条记录的时间和 ID，就可以直接从那里继续查询。”

“这就是 Keyset Pagination，也叫游标分页。”

### 传统 OFFSET 分页

```
SELECT id, user_id, amount, created_at
FROM orders
WHERE status = 1
ORDER BY created_at DESC, id DESC
LIMIT 1000000, 20;
```

需要跳过大量记录。

### 游标分页

假设上一页最后一条记录：

```
created_at = 2026-10-16 10:30:00
id         = 987654
```

下一页查询：

```
SELECT id, user_id, amount, created_at
FROM orders
WHERE status = 1
  AND (
      created_at < '2026-10-16 10:30:00'
      OR (
          created_at = '2026-10-16 10:30:00'
          AND id < 987654
      )
  )
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

“这样数据库就可以利用索引，从游标附近继续读取后续记录。”

“而不必每次从头跳过一百万条。”

陈默补充：

“这里的游标不是数据库服务端 Cursor，而是由业务保存的分页位置。”

“另外，在支持行构造器比较的 MySQL 中，也可以写成类似 `(created_at, id) < (?, ?)` 的形式，但具体索引利用情况仍需要通过执行计划验证。”

### OFFSET 与游标分页对比

分页深度与查询耗时（示意数据）

仅展示典型趋势，不代表实际性能测试结果

OFFSET 分页游标分页

0 ms3000 ms6000 ms9000 ms1.2万 ms第1页第100页第1000页第10000页第50000页

林川说道：

“所以游标分页的优势，是查询成本通常不会随着页码线性增加。”

“对，但有前提。”

“必须有合适的索引，游标字段需要形成稳定排序，而且查询条件要与索引匹配。”

“另外，游标分页不擅长直接跳转到任意页码。”

“如果业务必须支持跳转到第 50000 页，就需要考虑其他方案，比如限制最大翻页深度、搜索引擎、预计算、异步导出，或者重新设计产品交互。”

## 第九幕：索引失效的六种陷阱

事故已经找到主要原因。

但陈默并没有停止教学。

“林川，今天我们遇到的是深分页。”

“下次可能是索引失效。”

“你需要知道，哪些 SQL 写法会让索引难以发挥作用。”

他在白板上列出了六种典型情况。

### 陷阱一：对索引列进行函数运算

```
SELECT *
FROM orders
WHERE DATE(created_at) = '2026-10-16';
```

普通的 `created_at` 索引通常难以直接用于这种函数表达式的范围定位。

更推荐：

```
SELECT *
FROM orders
WHERE created_at >= '2026-10-16'
  AND created_at <  '2026-10-17';
```

“这样更容易使用索引范围扫描。”

“但如果有合适的函数索引或生成列索引，也可能有其他优化方案。”

### 陷阱二：LIKE 前置通配符

```
SELECT *
FROM users
WHERE name LIKE '%张三';
```

普通 B+ 树索引通常无法高效进行前缀定位。

但：

```
WHERE name LIKE '张三%';
```

通常更容易利用索引范围。

### 陷阱三：隐式类型转换

```
SELECT *
FROM users
WHERE phone = 13800138000;
```

假设 `phone` 是字符串类型。

“这种写法可能引发类型转换和不符合预期的索引利用。”

“但不能简单记成只要发生隐式转换就一定不走索引，具体还要看类型、转换方向和优化器。”

“最稳妥的做法是让参数类型与字段类型一致。”

### 陷阱四：联合索引不满足有效前缀条件

假设索引：

```
INDEX idx_abc(a, b, c)
```

查询：

```
WHERE b = 10 AND c = 20
```

“通常无法像 `a = ? AND b = ?` 那样充分利用索引的前导列。”

“不过 MySQL 某些版本和场景可能采用 Skip Scan 等优化，不能把最左前缀规则理解成绝对的‘完全不使用索引’。”

### 陷阱五：OR 条件

```
WHERE user_id = 100
   OR amount > 500;
```

“如果两个条件的索引选择性、数据分布和成本不合适，优化器可能选择全表扫描。”

“某些情况下也可能使用 Index Merge。”

“所以 `OR` 不等于必然索引失效。”

### 陷阱六：选择性太低

```
WHERE status = 1
```

“假设全表 95% 的订单都是状态 1。”

“即使 `status` 有索引，优化器也可能认为全表扫描更便宜。”

“因为通过二级索引找到大量记录，再进行回表，可能比直接扫描表还慢。”

林川总结：

“所以索引是否有效，最终还是要看数据分布和执行计划。”

“没错。”

“不要把 SQL 优化变成背诵‘索引失效口诀’。”

## 第十幕：生产环境真正的止血方案

上午 11:38。

故障仍在持续。

陈默问林川：

“现在已经知道是深分页造成的慢 SQL，你会怎么止血？”

林川回答：

“先把 SQL 改成游标分页，然后发布。”

“太慢了。”

“那怎么办？”

“线上事故首先要恢复服务。”

他们采取了以下措施：

1. 在 API Gateway 对订单深分页查询进行临时限流。
2. 对超过安全分页深度的请求返回明确错误，避免继续打满数据库。
3. 暂停触发超深分页的批量导出任务。
4. 对已经确认的高成本查询进行受控处理，避免随意终止正常事务。
5. 在数据库压力下降后，逐步恢复正常请求。

陈默提醒：

“限流阈值必须结合实际容量和业务优先级确定。”

“对于已执行中的 SQL，必要时可以考虑 `KILL QUERY`，但要先确认目标会话和语句，避免误伤关键业务。”

“而且杀掉查询不代表根因解决，客户端如果立即重试，还可能重新制造压力。”

### 故障恢复曲线

止血后数据库 CPU 变化（模拟数据）

限流和暂停高成本查询后，数据库负载逐步恢复

0%25%50%75%100%11:2011:2511:3011:3511:4011:4511:50

“数据库恢复了。”

林川松了一口气。

陈默却说道：

“接下来才是修复。”

“我们需要修改分页接口、补充联合索引、验证执行计划、进行压测，并通过灰度发布观察实际效果。”

“另外，还要检查是不是存在其他接口共享同一个连接池、同一个数据库实例，导致故障扩散。”

## 第十一幕：慢 SQL 排查的完整作战手册

陈默要求林川整理一套可以直接用于生产排查的流程。

林川写下：

1. 确定数据库是否为瓶颈

   查看数据库 CPU、I/O、活跃会话、连接数、锁等待和应用连接池指标。
2. 定位高成本 SQL

   使用慢查询日志、Performance Schema、sys schema、SQL 监控或受控的 PROCESSLIST 检查。
3. 检查执行计划

   分析访问方式、索引、估算行数、排序、临时表、回表等信息。
4. 验证真实执行开销

   在安全环境使用 EXPLAIN ANALYZE，结合数据分布、索引基数与实际耗时。
5. 确定优化方向

   优化 SQL、联合索引、覆盖索引、分页方式、查询范围或数据模型。
6. 验证并上线

   使用接近生产的数据量压测，评估索引维护成本，灰度发布并持续观察。

### 生产排查命令速查

```
-- 查看当前连接与执行语句
SHOW FULL PROCESSLIST;

-- 检查慢查询日志配置
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- 查看表索引
SHOW INDEX FROM orders;

-- 查看估算执行计划
EXPLAIN SELECT ...;

-- 查看 InnoDB 状态
SHOW ENGINE INNODB STATUS;
```

如果启用了 Performance Schema，还可以利用 `events_statements_summary_by_digest` 等汇总表寻找累计耗时高、执行次数多的 SQL 模式。

陈默补充：

“生产环境中，SQL 的总资源消耗不只取决于单次耗时。”

“一条执行 20ms、每秒运行 10000 次的 SQL，也可能比一条偶尔执行 5 秒的 SQL 更值得优化。”

“所以排查时还要看调用频率、总耗时和资源消耗。”

## 第十二幕：面试官的终极追问

第二天。

陈默再次扮演面试官。

“假设线上 MySQL CPU 95%，接口超时，你会怎么排查？”

林川回答：

“首先，我会确认数据库压力是否与接口超时相关，查看 MySQL CPU、I/O、活跃连接、锁等待以及应用连接池指标。”

“如果业务影响严重，我会优先评估限流、暂停高成本任务、回滚近期变更或切流等止血措施。”

“然后通过慢查询日志、Performance Schema 和当前执行语句定位高成本 SQL。”

“找到 SQL 后，我会使用 EXPLAIN 检查访问方式、索引选择、估算扫描行数、排序和临时表情况，并在安全环境通过 EXPLAIN ANALYZE 验证实际执行开销。”

“如果存在深分页，我会考虑游标分页或延迟关联；如果存在索引不匹配，会结合 WHERE、ORDER BY 和数据分布设计合适的联合索引；如果存在大量回表，会考虑覆盖索引或减少查询字段。”

“最后在接近生产的数据规模下进行压测，验证 SQL 延迟、数据库 CPU、扫描行数、连接池占用等指标，并灰度上线。”

陈默继续问：

“如果 SQL 已经走索引了，为什么还会慢？”

林川回答：

“因为走索引不等于扫描量小。可能存在深分页、大范围索引扫描、大量回表、低选择性条件、排序或临时表等问题。必须结合执行计划和实际执行统计判断。”

“如果你创建了联合索引，优化器却不使用，怎么办？”

“我会检查统计信息是否准确、数据分布、查询条件和排序是否匹配索引，以及使用索引的真实成本。必要时在测试环境验证更新统计信息、调整索引或改写 SQL 的效果，而不是直接在生产强制使用索引。”

“为什么不直接增加 MySQL 连接数？”

“因为连接数增加并不能解决单条 SQL 资源消耗过大的问题，反而可能增加数据库并发压力，让 CPU、I/O 和锁竞争进一步恶化。”

陈默终于点头。

“这次你理解的不是一条 SQL。”

“而是整个数据库性能问题的因果链。”

## 本章核心知识

| 现象          | 可能原因           | 关键排查                 |
| ----------- | -------------- | -------------------- |
| MySQL CPU 高 | 大量扫描、排序、计算     | 慢日志、执行计划             |
| SQL 走索引仍慢   | 深分页、大量回表       | rows、实际执行统计          |
| 连接池耗尽       | 慢 SQL、长事务、连接泄漏 | HikariCP、PROCESSLIST |
| 查询突然变慢      | 数据量变化、执行计划变化   | 统计信息、索引、历史计划         |
| 大量锁等待       | 长事务、热点行、死锁     | InnoDB 状态、锁等待        |
| ORDER BY 很慢 | 索引不匹配、排序开销     | Extra、排序统计           |
| LIMIT 深分页很慢 | 大量跳过记录         | 游标分页、延迟关联            |

## 下一章预告

[ChipSoft Ransomware Attack Disrupts Dutch Hospital Network](https://images.openai.com/static-rsc-4/uxc2xu49NcK2mCPM7pGzNAVlZc3pqCYbiwkGo3DKbXnmJCAzQWKq03Tq9QVpOYE7KahIFotAf27i2phGb7h97K2pXGwo6fuxun5XFJ9xlDYT_w42tGFBVVrKcyt33YvdhuytYeQnllxeYe1TOtQpzXGwikawtmbUJunOInEH5Cw?purpose=inline)

## 第五章：《无法提交的事务——MySQL 锁战争》

一场看似普通的优惠券库存扣减，突然让数据库出现大量锁等待。

一个事务只修改了一条记录，却让数百个请求排队。

更诡异的是，两个事务分别更新不同的订单，MySQL 却报告了死锁。

林川将深入 InnoDB 的锁管理系统，调查行锁、间隙锁、Next-Key Lock、MVCC、隔离级别、死锁检测和长事务。

下一章还会揭开一个容易在 Java 面试中答错的问题：为什么 MySQL 明明使用了行锁，却仍然可能锁住大量记录，甚至阻塞插入操作？





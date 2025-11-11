# eBPF可观测性

## 📋 目录

- [eBPF可观测性](#ebpf可观测性)
  - [📋 目录](#-目录)
  - [概述](#概述)
    - [eBPF可观测性革命](#ebpf可观测性革命)
    - [核心优势](#核心优势)
    - [技术架构](#技术架构)
  - [系统追踪技术](#系统追踪技术)
    - [Kprobes - 内核函数追踪](#kprobes---内核函数追踪)
    - [Uprobes - 用户空间函数追踪](#uprobes---用户空间函数追踪)
    - [Tracepoints - 静态追踪点](#tracepoints---静态追踪点)
    - [USDT - 用户态静态探针](#usdt---用户态静态探针)
  - [bpftrace工具](#bpftrace工具)
    - [bpftrace概述](#bpftrace概述)
    - [bpftrace语法](#bpftrace语法)
    - [单行脚本示例](#单行脚本示例)
    - [复杂脚本示例](#复杂脚本示例)
  - [BCC工具集](#bcc工具集)
    - [BCC概述](#bcc概述)
    - [性能分析工具](#性能分析工具)
    - [网络分析工具](#网络分析工具)
    - [自定义BCC程序](#自定义bcc程序)
  - [容器可观测性](#容器可观测性)
    - [Pixie - Kubernetes可观测平台](#pixie---kubernetes可观测平台)
  - [实战案例](#实战案例)
    - [案例1: 应用延迟诊断](#案例1-应用延迟诊断)
    - [案例2: 内存泄漏检测](#案例2-内存泄漏检测)
  - [最佳实践](#最佳实践)
    - [生产环境使用指南](#生产环境使用指南)
    - [性能影响评估](#性能影响评估)
  - [参考资料](#参考资料)
  - [相关文档](#相关文档)
    - [本模块相关](#本模块相关)
    - [其他模块相关](#其他模块相关)

---

## 概述

### eBPF可观测性革命

**eBPF可观测性**通过在内核中动态插入追踪点，提供了前所未有的系统洞察能力，无需修改应用代码或重启系统。

```text
传统可观测性 vs eBPF可观测性:

┌────────────────────────────────────────────────────────────────┐
│ 传统可观测性工具                                                │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  应用层:                                                        │
│    - 应用日志 (需要添加日志代码)                                 │
│    - APM Agent (侵入式, 性能开销5-10%)                          │
│    - 代码注入 (需要修改代码)                                     │
│                                                                 │
│  系统层:                                                        │
│    - strace (性能开销100-300%, 不可用于生产)                    │
│    - perf (采样, 可能miss关键事件)                              │
│    - SystemTap (需要调试符号, 部署复杂)                         │
│                                                                │
│  问题:                                                          │
│    ❌ 需要修改应用代码                                         │
│    ❌ 性能开销大 (5-300%)                                      │
│    ❌ 需要重启应用                                             │
│    ❌ 可见性有限 (只能看到预定义的指标)                         │
│    ❌ 内核可见性差                                             │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ eBPF可观测性                                                    │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  eBPF追踪点:                                                    │
│    ┌──────────────────────────────────────────────────────┐   │
│    │ Kprobes: 追踪任何内核函数 (40,000+)                 │   │
│    │ Uprobes: 追踪用户空间函数 (任意应用)                │   │
│    │ Tracepoints: 内核稳定追踪点 (1,500+)               │   │
│    │ USDT: 应用静态探针 (MySQL, PostgreSQL, Java)       │   │
│    └──────────────────────────────────────────────────────┘   │
│                                                                 │
│  eBPF程序:                                                      │
│    - 动态加载 (无需重启)                                       │
│    - 内核态执行 (低开销 <1%)                                  │
│    - 安全验证 (不会崩溃内核)                                  │
│    - 实时数据 (微秒级粒度)                                    │
│                                                                 │
│  优势:                                                          │
│    ✅ 零侵入 (无需修改代码)                                    │
│    ✅ 极低开销 (<1%)                                           │
│    ✅ 动态插入 (无需重启)                                      │
│    ✅ 完整可见性 (内核+用户空间)                               │
│    ✅ 生产可用 (低影响)                                        │
└────────────────────────────────────────────────────────────────┘
```

### 核心优势

```yaml
性能优势:
  ✅ 开销极低: <1% CPU (vs APM 5-10%)
  ✅ 无重启: 动态加载卸载
  ✅ 高精度: 纳秒级时间戳
  ✅ 实时性: 微秒级数据采集

功能优势:
  ✅ 全栈可见: 内核+应用+网络
  ✅ 深度追踪: 函数级粒度
  ✅ 历史回溯: 事件记录
  ✅ 上下文关联: 进程/线程/请求

灵活性:
  ✅ 任意函数: 追踪40,000+内核函数
  ✅ 自定义逻辑: 过滤、聚合、统计
  ✅ 多语言支持: C/C++/Go/Java/Python...
  ✅ 动态脚本: bpftrace单行命令

生产友好:
  ✅ 安全验证: eBPF验证器保证安全
  ✅ 资源限制: 防止过度消耗
  ✅ 无侵入性: 不修改应用
  ✅ 随时停止: 卸载即恢复
```

### 技术架构

```text
eBPF可观测性技术栈:

┌────────────────────────────────────────────────────────────────┐
│                       可观测性工具层                            │
│  bpftrace │ BCC │ Pixie │ Grafana Tempo │ OpenTelemetry       │
├────────────────────────────────────────────────────────────────┤
│                       前端工具库                                │
│  libbpf │ libbcc │ bpftrace库 │ Python/Lua绑定              │
├────────────────────────────────────────────────────────────────┤
│                    eBPF程序 (内核态)                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Kprobe BPF: 追踪内核函数                                 │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ Uprobe BPF: 追踪用户函数                                 │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ Tracepoint BPF: 稳定追踪点                               │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ Perf Event BPF: 性能事件采样                             │ │
│  └──────────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────────┤
│                    eBPF Maps (数据传递)                        │
│  Ringbuf │ Perf Buffer │ Hash Map │ Array │ Stack Trace      │
├────────────────────────────────────────────────────────────────┤
│                    Linux Kernel                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 追踪点:                                                   │ │
│  │  - 内核函数 (Kprobe: 40,000+)                           │ │
│  │  - 稳定追踪点 (Tracepoint: 1,500+)                      │ │
│  │  - 性能计数器 (Perf Events)                             │ │
│  └──────────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────────┤
│                    用户空间应用                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Uprobe追踪点:                                             │ │
│  │  - 应用函数 (任意二进制)                                 │ │
│  │  - USDT探针 (MySQL, PostgreSQL, JVM)                    │ │
│  │  - 动态库函数 (libc, SSL库)                             │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## 系统追踪技术

### Kprobes - 内核函数追踪

**Kprobes** 允许在几乎任何内核函数的入口和出口插入探针，实现动态追踪。

```yaml
Kprobes类型:
  kprobe: 函数入口追踪
    - 函数被调用时触发
    - 可以访问函数参数
    - 示例: kprobe:tcp_sendmsg

  kretprobe: 函数返回追踪
    - 函数返回时触发
    - 可以访问返回值
    - 示例: kretprobe:tcp_sendmsg

Kprobe能力:
  ✅ 追踪40,000+内核函数
  ✅ 访问函数参数和返回值
  ✅ 访问内核数据结构
  ✅ 计算函数执行时间
  ✅ 统计调用频率

使用场景:
  - 文件I/O分析 (vfs_read, vfs_write)
  - 网络性能分析 (tcp_sendmsg, tcp_recvmsg)
  - 进程调度分析 (schedule, wake_up_process)
  - 系统调用追踪 (sys_open, sys_read)
```

**Kprobe示例 - 追踪文件打开**:

```bash
# 使用bpftrace追踪所有open系统调用
sudo bpftrace -e 'kprobe:do_sys_openat2 {
  printf("%s opened %s\n", comm, str(arg1));
}'

# 输出示例:
# bash opened /etc/passwd
# cat opened /var/log/syslog
# nginx opened /var/www/html/index.html

# 追踪特定进程的文件打开
sudo bpftrace -e 'kprobe:do_sys_openat2 / comm == "nginx" / {
  printf("%s opened: %s\n", comm, str(arg1));
}'

# 统计每个进程打开文件次数
sudo bpftrace -e 'kprobe:do_sys_openat2 {
  @opens[comm] = count();
}'
# 输出 (按次数排序):
# @opens[systemd]: 1234
# @opens[chrome]: 567
# @opens[nginx]: 123
```

**Kprobe示例 - 网络延迟分析**:

```bash
# 追踪TCP发送延迟
sudo bpftrace -e '
kprobe:tcp_sendmsg {
  @start[tid] = nsecs;
}

kretprobe:tcp_sendmsg /@start[tid]/ {
  $duration_us = (nsecs - @start[tid]) / 1000;
  @latency_us = hist($duration_us);
  delete(@start[tid]);
}'

# 输出直方图:
# @latency_us:
# [1, 2)        1024 |@@@@@@@@@@@@@@@@@@@@                        |
# [2, 4)        2048 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
# [4, 8)         512 |@@@@@@@@@@                                  |
# [8, 16)        128 |@@                                          |
```

### Uprobes - 用户空间函数追踪

**Uprobes** 允许追踪用户空间应用的任意函数，无需修改应用代码。

```yaml
Uprobe类型:
  uprobe: 用户函数入口追踪
    - 应用函数被调用时触发
    - 访问函数参数
    - 示例: uprobe:/bin/bash:readline

  uretprobe: 用户函数返回追踪
    - 函数返回时触发
    - 访问返回值
    - 示例: uretprobe:/lib/x86_64-linux-gnu/libc.so.6:malloc

Uprobe能力:
  ✅ 追踪任意应用函数
  ✅ 追踪动态库函数 (libc, libssl)
  ✅ 多语言支持 (C/C++/Go/Rust)
  ✅ 符号解析 (需要符号表)
  ✅ 参数和返回值访问

使用场景:
  - SSL/TLS流量分析 (SSL_read, SSL_write)
  - 内存分配追踪 (malloc, free)
  - 应用性能分析 (自定义函数)
  - 数据库查询追踪 (USDT探针)
```

**Uprobe示例 - SSL流量解密**:

```bash
# 追踪OpenSSL的SSL_write函数，捕获明文数据
sudo bpftrace -e '
uprobe:/usr/lib/x86_64-linux-gnu/libssl.so.3:SSL_write {
  printf("PID %d writing %d bytes: %s\n",
    pid, arg2, str(arg1, arg2));
}'

# 输出示例 (HTTPS请求明文):
# PID 12345 writing 80 bytes: GET /api/users HTTP/1.1\r\nHost: example.com\r\n...

# 追踪SSL_read (HTTPS响应)
sudo bpftrace -e '
uretprobe:/usr/lib/x86_64-linux-gnu/libssl.so.3:SSL_read {
  printf("PID %d read %d bytes\n", pid, retval);
}'
```

**Uprobe示例 - 内存分配追踪**:

```bash
# 追踪malloc/free，检测内存泄漏
sudo bpftrace -e '
uprobe:/lib/x86_64-linux-gnu/libc.so.6:malloc {
  @allocs[pid, ustack] = count();
  @size[pid] = sum(arg0);
}

uretprobe:/lib/x86_64-linux-gnu/libc.so.6:malloc {
  @addr[retval] = 1;
}

uprobe:/lib/x86_64-linux-gnu/libc.so.6:free {
  delete(@addr[arg0]);
}

interval:s:10 {
  printf("Memory allocations by process:\n");
  print(@size);
  printf("\nTop allocation stacks:\n");
  print(@allocs, 10);
  clear(@size);
  clear(@allocs);
}'

# 输出:
# Memory allocations by process:
# @size[12345]: 104857600  # 100MB分配
# @size[12346]: 52428800   # 50MB分配
#
# Top allocation stacks:
# @allocs[12345,
#   0x7f1234567890 malloc+0
#   0x7f1234567900 my_function+32
#   0x7f1234567a00 main+128
# ]: 1000
```

### Tracepoints - 静态追踪点

**Tracepoints** 是内核中预定义的稳定追踪点，不会因内核版本变化而失效。

```yaml
Tracepoint分类:
  syscalls: 系统调用 (600+)
    - sys_enter_*: 系统调用入口
    - sys_exit_*: 系统调用出口
    - 示例: tracepoint:syscalls:sys_enter_openat

  sched: 进程调度 (30+)
    - sched_switch: 进程切换
    - sched_wakeup: 进程唤醒
    - sched_process_fork: 进程创建

  net: 网络 (50+)
    - net_dev_xmit: 网络发送
    - net_dev_queue: 网络队列
    - netif_receive_skb: 网络接收

  block: 块设备I/O (20+)
    - block_rq_issue: I/O请求发起
    - block_rq_complete: I/O请求完成

  其他: irq, kmem, power, workqueue...

Tracepoint优势:
  ✅ 稳定API (不随内核版本变化)
  ✅ 性能开销最小
  ✅ 内核官方维护
  ✅ 完整文档

使用场景:
  - 系统调用统计
  - 进程调度分析
  - 网络性能监控
  - I/O性能分析
```

**Tracepoint示例 - 系统调用统计**:

```bash
# 统计每个进程的系统调用次数
sudo bpftrace -e '
tracepoint:syscalls:sys_enter_* {
  @syscalls[comm, probe] = count();
}'

# 运行10秒后按Ctrl+C，输出:
# @syscalls[chrome, sys_enter_futex]: 12345
# @syscalls[nginx, sys_enter_epoll_wait]: 6789
# @syscalls[mysqld, sys_enter_read]: 4567

# 统计系统调用延迟
sudo bpftrace -e '
tracepoint:syscalls:sys_enter_read {
  @start[tid] = nsecs;
}

tracepoint:syscalls:sys_exit_read /@start[tid]/ {
  $duration_us = (nsecs - @start[tid]) / 1000;
  @latency = hist($duration_us);
  delete(@start[tid]);
}'
```

**Tracepoint示例 - 进程调度分析**:

```bash
# 追踪进程调度，计算运行时间
sudo bpftrace -e '
tracepoint:sched:sched_switch {
  // $prev = args->prev_comm; $next = args->next_comm;

  if (@start[args->prev_pid]) {
    $runtime_us = (nsecs - @start[args->prev_pid]) / 1000;
    @runtime[args->prev_comm] = hist($runtime_us);
  }

  @start[args->next_pid] = nsecs;
}

interval:s:10 {
  printf("Process runtime distribution (μs):\n");
  print(@runtime);
  clear(@runtime);
}'

# 输出每个进程的运行时间分布直方图
```

### USDT - 用户态静态探针

**USDT (User Statically-Defined Tracing)** 是应用预埋的追踪点，如MySQL、PostgreSQL、Java等。

```yaml
USDT支持的应用:
  MySQL/MariaDB:
    - query-start: 查询开始
    - query-done: 查询完成
    - query-parse-start/done

  PostgreSQL:
    - transaction-start/commit
    - query-start/done
    - lock-wait-start/done

  Java/JVM (HotSpot):
    - gc-begin/end: GC事件
    - thread-start/stop
    - method-entry/return

  Node.js:
    - http-server-request/response
    - gc-start/done

  Python:
    - function-entry/return
    - gc-start/done

USDT优势:
  ✅ 应用感知的追踪点
  ✅ 语义化信息 (查询SQL, 事务ID)
  ✅ 极低开销 (默认禁用)
  ✅ 稳定接口

使用场景:
  - 数据库查询性能分析
  - GC暂停时间追踪
  - 应用事务追踪
  - HTTP请求延迟分析
```

**USDT示例 - MySQL查询追踪**:

```bash
# 列出MySQL的USDT探针
sudo bpftrace -l 'usdt:/usr/sbin/mysqld:*'
# 输出:
# usdt:/usr/sbin/mysqld:mysql:query__start
# usdt:/usr/sbin/mysqld:mysql:query__done
# usdt:/usr/sbin/mysqld:mysql:query__parse__start
# ...

# 追踪MySQL慢查询 (>100ms)
sudo bpftrace -e '
usdt:/usr/sbin/mysqld:mysql:query__start {
  @start[arg1] = nsecs;  // arg1 = connection_id
  @query[arg1] = str(arg0);  // arg0 = query SQL
}

usdt:/usr/sbin/mysqld:mysql:query__done /@start[arg1]/ {
  $duration_ms = (nsecs - @start[arg1]) / 1000000;

  if ($duration_ms > 100) {
    printf("Slow query (%d ms): %s\n", $duration_ms, @query[arg1]);
  }

  delete(@start[arg1]);
  delete(@query[arg1]);
}'

# 输出示例:
# Slow query (234 ms): SELECT * FROM users WHERE created_at > '2025-01-01'
# Slow query (567 ms): SELECT COUNT(*) FROM orders JOIN users ON...
```

---

## bpftrace工具

### bpftrace概述

**bpftrace** 是一个高级eBPF追踪语言和工具，受DTrace和SystemTap启发，提供了简洁的单行脚本能力。

```yaml
bpftrace特点:
  ✅ 简洁语法: 类似awk的编程模型
  ✅ 单行脚本: 快速问题诊断
  ✅ 强大功能: 40,000+内核函数追踪
  ✅ 多种追踪点: kprobe/uprobe/tracepoint/USDT
  ✅ 内置函数: 丰富的辅助函数
  ✅ Maps支持: 统计、直方图、栈追踪

bpftrace vs 其他工具:
  vs DTrace:
    ✅ Linux原生支持
    ✅ 更现代的语法
    ✅ 活跃的社区

  vs SystemTap:
    ✅ 无需调试符号
    ✅ 更简洁的语法
    ✅ 更安全（eBPF验证器）

  vs perf:
    ✅ 更灵活的过滤
    ✅ 自定义聚合
    ✅ 实时可编程

使用场景:
  - 快速问题诊断
  - 性能分析
  - 延迟追踪
  - 系统行为观察
```

### bpftrace语法

**基本语法结构**:

```bash
# bpftrace程序结构
probe_type:probe_name /filter/ {
  actions
}

# 示例：追踪所有系统调用
sudo bpftrace -e '
tracepoint:syscalls:sys_enter_* {
  @syscalls[probe] = count();
}'
```

**内置变量**:

```yaml
进程/线程信息:
  pid: 进程ID
  tid: 线程ID
  uid: 用户ID
  gid: 组ID
  comm: 进程名称
  nsecs: 纳秒时间戳

参数和返回值:
  arg0-argN: 函数参数
  args: tracepoint参数结构
  retval: 函数返回值 (kretprobe/uretprobe)

内核信息:
  cpu: CPU编号
  curtask: 当前任务结构
  kstack: 内核栈
  ustack: 用户栈
```

**内置函数**:

```yaml
字符串函数:
  str(addr [,len]): 读取字符串
  printf(fmt, ...): 格式化输出
  system(cmd): 执行系统命令

时间函数:
  nsecs: 纳秒时间戳
  elapsed: 程序运行时间

统计函数:
  count(): 计数
  sum(value): 求和
  avg(value): 平均值
  min(value): 最小值
  max(value): 最大值
  hist(value): 直方图
  lhist(value, min, max, step): 线性直方图

栈追踪:
  kstack: 内核栈
  ustack: 用户栈
  usym(addr): 用户符号
  ksym(addr): 内核符号
```

### 单行脚本示例

**文件I/O追踪**:

```bash
# 1. 追踪所有文件打开
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args->filename)); }'

# 2. 统计每个进程打开文件数
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_openat { @[comm] = count(); }'

# 3. 追踪文件读写大小
sudo bpftrace -e 'tracepoint:syscalls:sys_exit_read /args->ret > 0/ { @bytes[comm] = sum(args->ret); }'

# 4. 追踪慢速文件操作 (>10ms)
sudo bpftrace -e 'kprobe:vfs_read { @start[tid] = nsecs; }
kretprobe:vfs_read /@start[tid]/ {
  $ms = (nsecs - @start[tid]) / 1000000;
  if ($ms > 10) { printf("%s slow read: %d ms\n", comm, $ms); }
  delete(@start[tid]);
}'
```

**网络追踪**:

```bash
# 1. 追踪TCP连接
sudo bpftrace -e 'kprobe:tcp_connect { printf("%s connecting to %s\n", comm, str(args->saddr)); }'

# 2. 统计每个进程的网络发送字节数
sudo bpftrace -e 'kprobe:tcp_sendmsg { @send_bytes[comm] = sum(arg2); }'

# 3. 追踪网络延迟
sudo bpftrace -e 'kprobe:tcp_sendmsg { @start[tid] = nsecs; }
kretprobe:tcp_sendmsg /@start[tid]/ {
  @latency_us = hist((nsecs - @start[tid]) / 1000);
  delete(@start[tid]);
}'

# 4. 追踪DNS查询
sudo bpftrace -e 'kprobe:__inet_lookup_established { printf("DNS lookup: %s\n", str(arg1)); }'
```

**进程追踪**:

```bash
# 1. 追踪新进程创建
sudo bpftrace -e 'tracepoint:sched:sched_process_exec { printf("%s exec %s\n", comm, str(args->filename)); }'

# 2. 追踪进程退出
sudo bpftrace -e 'tracepoint:sched:sched_process_exit { printf("%s (PID %d) exited\n", comm, pid); }'

# 3. 统计CPU调度延迟
sudo bpftrace -e 'tracepoint:sched:sched_wakeup { @wakeup[args->pid] = nsecs; }
tracepoint:sched:sched_switch /@wakeup[args->next_pid]/ {
  @latency_us = hist((nsecs - @wakeup[args->next_pid]) / 1000);
  delete(@wakeup[args->next_pid]);
}'
```

### 复杂脚本示例

**MySQL慢查询分析**:

```bash
#!/usr/bin/env bpftrace
# mysql_slow_queries.bt - 追踪MySQL慢查询

usdt:/usr/sbin/mysqld:mysql:query__start
{
  @start[arg1] = nsecs;
  @query[arg1] = str(arg0, 200);  // 保存SQL (最多200字符)
}

usdt:/usr/sbin/mysqld:mysql:query__done
/@start[arg1]/
{
  $duration_ms = (nsecs - @start[arg1]) / 1000000;

  if ($duration_ms > 100) {
    time("%H:%M:%S ");
    printf("Slow query (%d ms, conn_id=%d):\n", $duration_ms, arg1);
    printf("  SQL: %s\n\n", @query[arg1]);

    // 记录到慢查询统计
    @slow_count = @slow_count + 1;
    @slow_total_ms = @slow_total_ms + $duration_ms;
  }

  // 清理
  delete(@start[arg1]);
  delete(@query[arg1]);
}

interval:s:10
{
  printf("\n===== Slow Query Statistics (last 10s) =====\n");
  printf("Slow queries: %d\n", @slow_count);
  printf("Total time: %d ms\n", @slow_total_ms);
  printf("Average: %d ms\n\n", @slow_total_ms / @slow_count);

  clear(@slow_count);
  clear(@slow_total_ms);
}

END
{
  clear(@start);
  clear(@query);
  clear(@slow_count);
  clear(@slow_total_ms);
}
```

**HTTP请求延迟分析**:

```bash
#!/usr/bin/env bpftrace
# http_latency.bt - 追踪HTTP请求延迟

uprobe:/usr/sbin/nginx:ngx_http_process_request
{
  @start[tid] = nsecs;
  @req_count = @req_count + 1;
}

uretprobe:/usr/sbin/nginx:ngx_http_process_request
/@start[tid]/
{
  $latency_us = (nsecs - @start[tid]) / 1000;

  // 延迟直方图
  @latency_hist = hist($latency_us);

  // 按延迟分类
  if ($latency_us < 1000) {
    @fast = @fast + 1;  // <1ms
  } else if ($latency_us < 10000) {
    @medium = @medium + 1;  // 1-10ms
  } else {
    @slow = @slow + 1;  // >10ms
    printf("%s: Slow request %d us\n", comm, $latency_us);
  }

  delete(@start[tid]);
}

interval:s:5
{
  printf("\n===== HTTP Request Stats (last 5s) =====\n");
  printf("Total requests: %d\n", @req_count);
  printf("  Fast (<1ms):   %d (%.1f%%)\n", @fast, @fast * 100.0 / @req_count);
  printf("  Medium (1-10ms): %d (%.1f%%)\n", @medium, @medium * 100.0 / @req_count);
  printf("  Slow (>10ms):  %d (%.1f%%)\n", @slow, @slow * 100.0 / @req_count);
  printf("\nLatency distribution (μs):\n");
  print(@latency_hist);

  clear(@req_count);
  clear(@fast);
  clear(@medium);
  clear(@slow);
  clear(@latency_hist);
}
```

---

## BCC工具集

### BCC概述

**BCC (BPF Compiler Collection)** 是一个eBPF工具包，包含100+个性能分析和追踪工具。

```yaml
BCC特点:
  ✅ 100+现成工具: 开箱即用
  ✅ Python/Lua前端: 易于扩展
  ✅ 低级libbpf: 高性能
  ✅ 多语言支持: C/C++/Python
  ✅ 丰富示例: 学习资源

BCC工具分类:
  性能分析:
    - execsnoop: 追踪新进程
    - opensnoop: 追踪文件打开
    - biolatency: 块I/O延迟
    - tcplife: TCP连接生命周期

  网络分析:
    - tcpconnect: TCP连接追踪
    - tcpaccept: TCP接受追踪
    - tcpretrans: TCP重传追踪
    - tcptop: TCP流量Top

  I/O分析:
    - biosnoop: 块I/O追踪
    - filelife: 文件生命周期
    - vfsstat: VFS统计
    - cachestat: 页缓存统计

  CPU分析:
    - cpudist: CPU使用分布
    - runqlat: 运行队列延迟
    - profile: CPU性能剖析

  内存分析:
    - memleak: 内存泄漏检测
    - slabratetop: Slab分配Top
```

### 性能分析工具

**execsnoop - 追踪新进程**:

```bash
# 追踪所有新进程
sudo execsnoop

# 输出示例:
# PCOMM            PID    PPID   RET ARGS
# bash             12345  12344    0 /bin/bash
# ls               12346  12345    0 /bin/ls -la
# grep             12347  12345    0 /bin/grep error /var/log/syslog

# 只追踪失败的exec (RET != 0)
sudo execsnoop -x

# 追踪特定进程名
sudo execsnoop -n nginx
```

**opensnoop - 追踪文件打开**:

```bash
# 追踪所有文件打开
sudo opensnoop

# 输出示例:
# PID    COMM               FD ERR PATH
# 1234   nginx               3   0 /var/www/html/index.html
# 5678   mysqld              4   0 /var/lib/mysql/ibdata1
# 9012   cat                 3   0 /etc/passwd

# 只追踪失败的open
sudo opensnoop -x

# 追踪特定进程
sudo opensnoop -p 1234

# 追踪特定用户
sudo opensnoop -u www-data
```

**biolatency - 块I/O延迟**:

```bash
# 显示块I/O延迟直方图
sudo biolatency

# 输出示例 (每秒刷新):
#      usecs               : count     distribution
#          0 -> 1          : 0        |                                        |
#          2 -> 3          : 0        |                                        |
#          4 -> 7          : 0        |                                        |
#          8 -> 15         : 12       |*                                       |
#         16 -> 31         : 456      |****************************            |
#         32 -> 63         : 789      |****************************************|
#         64 -> 127        : 234      |**************                          |
#        128 -> 255        : 67       |****                                    |

# 按进程分组
sudo biolatency -p

# 按磁盘分组
sudo biolatency -D
```

**profile - CPU性能剖析**:

```bash
# CPU采样 (默认49Hz)
sudo profile

# 输出示例:
#     ngx_http_process_request
#     ngx_http_handler
#     ngx_epoll_process_events
#     [unknown]
#     -                nginx (8973)
#         6789

# 采样用户态+内核态
sudo profile -aK

# 特定进程的性能剖析
sudo profile -p 1234

# 生成火焰图数据
sudo profile -a -f 30 > profile.stacks
# 使用FlameGraph工具生成火焰图
```

### 网络分析工具

**tcpconnect - TCP连接追踪**:

```bash
# 追踪所有TCP出站连接
sudo tcpconnect

# 输出示例:
# PID    COMM         IP SADDR            DADDR            DPORT
# 1234   wget         4  192.168.1.100    8.8.8.8          443
# 5678   curl         4  192.168.1.100    example.com      80
# 9012   ssh          4  192.168.1.100    10.0.0.5         22

# 只追踪特定端口
sudo tcpconnect --dport 443

# 追踪特定进程
sudo tcpconnect -p 1234
```

**tcplife - TCP连接生命周期**:

```bash
# 追踪TCP连接的完整生命周期
sudo tcplife

# 输出示例:
# PID   COMM   LADDR           LPORT RADDR           RPORT TX_KB  RX_KB MS
# 1234  nginx  192.168.1.100   80    10.0.0.5        54321  156    89   1234
# 5678  mysqld 192.168.1.100   3306  10.0.0.6        45678  234    567  5678

# 只显示时间>1秒的连接
sudo tcplife -m 1000

# 按字节数排序
sudo tcplife | sort -k6 -rn
```

**tcpretrans - TCP重传追踪**:

```bash
# 追踪TCP重传
sudo tcpretrans

# 输出示例:
# TIME     PID    IP LADDR:LPORT          T> RADDR:RPORT          STATE
# 01:23:45 1234   4  192.168.1.100:80     R> 10.0.0.5:54321       ESTABLISHED
# 01:23:46 5678   4  192.168.1.100:443    R> 10.0.0.6:45678       ESTABLISHED

# 每秒统计重传次数
sudo tcpretrans -l
```

### 自定义BCC程序

**简单的BCC Python程序**:

```python
#!/usr/bin/env python3
# hello_bcc.py - 简单的BCC程序示例

from bcc import BPF

# eBPF程序 (C代码)
bpf_program = """
#include <uapi/linux/ptrace.h>

// 数据结构
struct data_t {
    u32 pid;
    char comm[16];
};

// Perf buffer用于数据传递
BPF_PERF_OUTPUT(events);

// Kprobe: 追踪sys_execve
int trace_execve(struct pt_regs *ctx) {
    struct data_t data = {};

    data.pid = bpf_get_current_pid_tgid() >> 32;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    // 发送事件到用户空间
    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}
"""

# 编译eBPF程序
b = BPF(text=bpf_program)
b.attach_kprobe(event="__x64_sys_execve", fn_name="trace_execve")

# 事件处理回调
def print_event(cpu, data, size):
    event = b["events"].event(data)
    print(f"PID {event.pid} executed: {event.comm.decode('utf-8', 'replace')}")

# 打开Perf buffer
b["events"].open_perf_buffer(print_event)

# 主循环
print("Tracing sys_execve... Hit Ctrl-C to end.")
while True:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()
```

**复杂的BCC程序 - 网络延迟追踪**:

```python
#!/usr/bin/env python3
# tcp_latency.py - TCP连接延迟追踪

from bcc import BPF
import time

bpf_program = """
#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>

struct connect_event_t {
    u64 ts_us;
    u32 pid;
    char comm[16];
    u32 saddr;
    u32 daddr;
    u16 dport;
};

BPF_HASH(start, u64);  // 记录连接开始时间
BPF_PERF_OUTPUT(events);

// 追踪tcp_connect
int trace_connect(struct pt_regs *ctx, struct sock *sk) {
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u64 ts = bpf_ktime_get_ns();

    // 保存开始时间
    start.update(&pid_tgid, &ts);

    return 0;
}

// 追踪tcp_connect返回
int trace_connect_return(struct pt_regs *ctx) {
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u64 *tsp = start.lookup(&pid_tgid);

    if (tsp == 0) {
        return 0;  // 找不到开始时间
    }

    // 计算延迟
    u64 delta_ns = bpf_ktime_get_ns() - *tsp;
    u64 delta_us = delta_ns / 1000;

    // 准备事件
    struct connect_event_t event = {};
    event.ts_us = delta_us;
    event.pid = pid_tgid >> 32;
    bpf_get_current_comm(&event.comm, sizeof(event.comm));

    // 发送事件
    events.perf_submit(ctx, &event, sizeof(event));

    // 清理
    start.delete(&pid_tgid);

    return 0;
}
"""

# 加载eBPF程序
b = BPF(text=bpf_program)
b.attach_kprobe(event="tcp_v4_connect", fn_name="trace_connect")
b.attach_kretprobe(event="tcp_v4_connect", fn_name="trace_connect_return")

# 打印头部
print("%-8s %-16s %-8s" % ("TIME", "COMM", "LAT(us)"))

# 事件处理
def print_event(cpu, data, size):
    event = b["events"].event(data)
    print("%-8s %-16s %-8d" % (
        time.strftime("%H:%M:%S"),
        event.comm.decode('utf-8', 'replace'),
        event.ts_us
    ))

b["events"].open_perf_buffer(print_event)

# 主循环
while True:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()
```

---

## 容器可观测性

### Pixie - Kubernetes可观测平台

**Pixie** 是一个基于eBPF的Kubernetes可观测性平台，提供零配置、自动化的深度洞察。

```yaml
Pixie特点:
  ✅ 零配置: 自动发现服务和追踪
  ✅ 实时可视: 服务拓扑、流量分析
  ✅ 协议解析: HTTP/gRPC/MySQL/PostgreSQL/DNS
  ✅ 集群视图: Pod/Service/Node级别监控
  ✅ 脚本语言: PxL (Pixie Language)

使用场景:
  - Kubernetes集群监控
  - 微服务性能分析
  - 网络故障排查
  - 安全审计
```

**Pixie部署**:

```bash
# 1. 安装Pixie CLI
bash -c "$(curl -fsSL https://withpixie.ai/install.sh)"

# 2. 部署到Kubernetes集群
px deploy

# 3. 查看集群状态
px get vizier-info

# 4. 启动Web UI
px live
# 访问: https://work.withpixie.ai/live
```

---

## 实战案例

### 案例1: 应用延迟诊断

**场景**: Web应用响应缓慢，需要定位性能瓶颈。

```bash
# 步骤1: 追踪HTTP请求延迟
sudo bpftrace -e '
uprobe:/usr/sbin/nginx:ngx_http_process_request {
  @start[tid] = nsecs;
}
uretprobe:/usr/sbin/nginx:ngx_http_process_request /@start[tid]/ {
  $latency_ms = (nsecs - @start[tid]) / 1000000;
  @latency = hist($latency_ms);
  if ($latency_ms > 100) {
    printf("%s: Slow request %d ms\n", comm, $latency_ms);
  }
  delete(@start[tid]);
}'

# 步骤2: 定位慢速系统调用
sudo bpftrace -e '
tracepoint:syscalls:sys_enter_* /comm == "nginx"/ {
  @start[tid, probe] = nsecs;
}
tracepoint:syscalls:sys_exit_* /@start[tid, probe]/ {
  $duration_ms = (nsecs - @start[tid, probe]) / 1000000;
  if ($duration_ms > 10) {
    printf("Slow syscall: %s %d ms\n", probe, $duration_ms);
  }
  delete(@start[tid, probe]);
}'
```

### 案例2: 内存泄漏检测

**场景**: 应用内存持续增长，怀疑内存泄漏。

```bash
# 使用bpftrace追踪malloc/free
sudo bpftrace -e '
uprobe:/lib/x86_64-linux-gnu/libc.so.6:malloc /comm == "myapp"/ {
  @allocs[pid, ustack] = count();
  @alloc_bytes[pid] = sum(arg0);
}
uretprobe:/lib/x86_64-linux-gnu/libc.so.6:malloc /comm == "myapp"/ {
  @addr[retval] = 1;
  @total_allocs = @total_allocs + 1;
}
uprobe:/lib/x86_64-linux-gnu/libc.so.6:free /comm == "myapp"/ {
  if (@addr[arg0]) {
    delete(@addr[arg0]);
    @total_frees = @total_frees + 1;
  }
}
interval:s:10 {
  printf("Leaked: %d\n", @total_allocs - @total_frees);
  print(@allocs, 5);
}'

# 或使用BCC memleak工具
sudo /usr/share/bcc/tools/memleak -p $(pidof myapp) 10
```

---

## 最佳实践

### 生产环境使用指南

```yaml
部署建议:
  ✅ 先在测试环境验证
  ✅ 监控eBPF程序的性能影响
  ✅ 设置资源限制 (CPU/内存)

权限管理:
  ✅ 最小权限原则
  ✅ 审计eBPF程序加载

数据安全:
  ✅ 避免追踪敏感数据
  ✅ 遵守数据合规要求
```

### 性能影响评估

```yaml
CPU开销:
  bpftrace: 0.1-1%
  BCC工具: 0.5-2%
  Pixie: 1-2%
  对比APM: 5-10%

最佳实践:
  ✅ 在eBPF中尽量过滤和聚合
  ✅ 避免追踪高频事件
  ✅ 使用采样技术
  ✅ 监控eBPF自身的性能影响
```

---

## 参考资料

**官方文档**:

- [eBPF.io](https://ebpf.io/)
- [bpftrace GitHub](https://github.com/iovisor/bpftrace)
- [BCC GitHub](https://github.com/iovisor/bcc)
- [Pixie Documentation](https://docs.px.dev/)

**学习资源**:

- [BPF Performance Tools Book](http://www.brendangregg.com/bpf-performance-tools-book.html)
- [bpftrace Tutorial](https://github.com/iovisor/bpftrace/blob/master/docs/tutorial_one_liners.md)

---

**文档版本**: v1.0
**最后更新**: 2025-10-19
**维护者**: 虚拟化容器化技术知识库项目组

**本章总结**:

本章深入介绍了eBPF可观测性技术，包括：

- ✅ **概述**: eBPF可观测性革命，<1% CPU开销
- ✅ **系统追踪**: Kprobes/Uprobes/Tracepoints/USDT
- ✅ **bpftrace**: 高级追踪语言，单行脚本和复杂脚本
- ✅ **BCC工具集**: 100+现成工具，自定义程序开发
- ✅ **容器可观测性**: Pixie Kubernetes平台
- ✅ **实战案例**: 延迟诊断、内存泄漏
- ✅ **最佳实践**: 生产部署、性能评估

**下一步阅读**:

- [05_eBPF安全技术](./05_eBPF安全技术.md)
- [06_eBPF性能优化](./06_eBPF性能优化.md)

---

## 相关文档

### 本模块相关

- [eBPF概述与架构](./01_eBPF概述与架构.md) - eBPF概述与架构详解
- [eBPF网络技术](./02_eBPF网络技术.md) - eBPF网络技术详解
- [eBPF与容器技术](./03_eBPF与容器技术.md) - eBPF与容器技术详解
- [eBPF安全技术](./05_eBPF安全技术.md) - eBPF安全技术详解
- [eBPF性能优化](./06_eBPF性能优化.md) - eBPF性能优化详解
- [eBPF实战案例](./07_eBPF实战案例.md) - eBPF实战案例详解
- [eBPF最佳实践](./08_eBPF最佳实践.md) - eBPF最佳实践详解
- [README.md](./README.md) - 本模块导航

### 其他模块相关

- [容器监控技术](../06_容器监控与运维/01_容器监控技术.md) - 容器监控技术
- [容器日志管理](../06_容器监控与运维/02_容器日志管理.md) - 容器日志管理
- [容器性能调优](../06_容器监控与运维/03_容器性能调优.md) - 容器性能调优
- [Kubernetes监控与日志管理](../03_Kubernetes技术详解/06_监控与日志管理.md) - K8s监控日志

---

**最后更新**: 2025年11月11日
**维护状态**: 持续更新

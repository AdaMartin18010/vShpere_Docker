# eBPF性能优化

## 📋 目录

- [eBPF性能优化](#ebpf性能优化)
  - [📋 目录](#-目录)
  - [概述](#概述)
    - [性能优化必要性](#性能优化必要性)
    - [优化原则](#优化原则)
    - [性能指标](#性能指标)
  - [eBPF程序优化](#ebpf程序优化)
    - [代码结构优化](#代码结构优化)
    - [循环展开](#循环展开)
    - [内联函数](#内联函数)
    - [避免复杂计算](#避免复杂计算)
  - [Maps优化](#maps优化)
    - [Map类型选择](#map类型选择)
    - [Map大小调优](#map大小调优)
    - [Per-CPU Maps](#per-cpu-maps)
    - [LRU Maps](#lru-maps)
  - [数据传输优化](#数据传输优化)
    - [Ringbuf vs Perf Buffer](#ringbuf-vs-perf-buffer)
    - [批量处理](#批量处理)
    - [数据过滤](#数据过滤)
  - [JIT编译优化](#jit编译优化)
    - [JIT工作原理](#jit工作原理)
  - [实战优化案例](#实战优化案例)
    - [案例1: 高频追踪优化](#案例1-高频追踪优化)
    - [案例2: Map性能调优](#案例2-map性能调优)
  - [性能测试](#性能测试)
  - [最佳实践](#最佳实践)
  - [参考资料](#参考资料)
  - [相关文档](#相关文档)
    - [本模块相关](#本模块相关)
    - [其他模块相关](#其他模块相关)

---

## 概述

### 性能优化必要性

虽然eBPF本身性能已经很高，但在高负载场景下，不当的实现仍可能带来显著开销。

```yaml
常见性能瓶颈:
  ❌ 高频事件追踪 (每秒百万次)
  ❌ 大量Map查找
  ❌ 频繁用户态数据传输
  ❌ 复杂的数据处理逻辑
  ❌ 不合适的Map类型

优化后的收益:
  ✅ CPU开销降低 50-90%
  ✅ 内存使用减少 30-70%
  ✅ 事件丢失率降低
  ✅ 更高的吞吐量
  ✅ 更低的延迟

优化目标:
  目标1: CPU开销 <2% (高负载场景)
  目标2: 内存使用 <200MB
  目标3: 事件丢失率 <0.1%
  目标4: 延迟 <100μs (P99)
```

### 优化原则

```yaml
核心原则:
  1. 在eBPF中做尽可能多的工作
     ✅ 在内核态过滤
     ✅ 在内核态聚合
     ✅ 减少用户态数据传输

  2. 选择正确的数据结构
     ✅ Hash vs Array
     ✅ Per-CPU vs 共享
     ✅ LRU vs 固定大小

  3. 避免不必要的操作
     ✅ 减少Map查找
     ✅ 减少helper调用
     ✅ 减少内存拷贝

  4. 使用高效的算法
     ✅ 位操作代替除法
     ✅ 循环展开
     ✅ 提前返回

权衡考虑:
  性能 vs 功能: 有时需要权衡
  复杂度 vs 可维护性: 保持代码可读
  通用性 vs 优化: 针对场景优化
```

### 性能指标

```yaml
关键指标:
  CPU开销:
    测量: perf, top
    目标: <2% CPU
    警戒: >5% CPU

  内存使用:
    测量: /proc/meminfo, bpftool
    目标: <200MB
    警戒: >500MB

  事件处理:
    吞吐量: 事件/秒
    丢失率: <0.1%
    延迟: P50/P95/P99

  Map操作:
    查找延迟: <100ns
    更新延迟: <200ns
    大小: 避免过大
```

---

## eBPF程序优化

### 代码结构优化

**优化前 - 低效代码**:

```c
// 低效: 重复计算、多次Map查找
SEC("kprobe/tcp_sendmsg")
int trace_tcp_send(struct pt_regs *ctx)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid >> 32;
    u32 tid = pid_tgid & 0xFFFFFFFF;

    // 重复调用
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();

    // 多次Map查找
    u64 *count = bpf_map_lookup_elem(&stats, &pid);
    if (count) {
        (*count)++;
    } else {
        u64 init_count = 1;
        bpf_map_update_elem(&stats, &pid, &init_count, BPF_ANY);
    }

    // 再次查找相同key
    u64 *bytes = bpf_map_lookup_elem(&bytes_map, &pid);
    if (bytes) {
        (*bytes) += PT_REGS_PARM3(ctx);
    }

    return 0;
}
```

**优化后 - 高效代码**:

```c
// 高效: 减少重复、优化逻辑
SEC("kprobe/tcp_sendmsg")
int trace_tcp_send_optimized(struct pt_regs *ctx)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid >> 32;

    // 使用结构体减少Map查找
    struct stats_t {
        u64 count;
        u64 bytes;
    };

    struct stats_t *stats = bpf_map_lookup_elem(&combined_stats, &pid);
    if (stats) {
        // 一次查找，两次更新
        __sync_fetch_and_add(&stats->count, 1);
        __sync_fetch_and_add(&stats->bytes, PT_REGS_PARM3(ctx));
    } else {
        struct stats_t init_stats = {
            .count = 1,
            .bytes = PT_REGS_PARM3(ctx)
        };
        bpf_map_update_elem(&combined_stats, &pid, &init_stats, BPF_NOEXIST);
    }

    return 0;
}
```

### 循环展开

**优化技巧**:

```c
// 低效: 动态循环 (eBPF验证器不喜欢)
#define MAX_BUFSIZE 256
SEC("kprobe/vfs_read")
int trace_read(struct pt_regs *ctx)
{
    char buf[MAX_BUFSIZE];
    char *user_buf = (char *)PT_REGS_PARM2(ctx);

    // 危险: 可能无法通过验证器
    for (int i = 0; i < MAX_BUFSIZE; i++) {
        bpf_probe_read(&buf[i], 1, user_buf + i);
        if (buf[i] == '\0') break;
    }

    return 0;
}

// 高效: 循环展开 + 固定边界
SEC("kprobe/vfs_read")
int trace_read_optimized(struct pt_regs *ctx)
{
    char buf[MAX_BUFSIZE];
    char *user_buf = (char *)PT_REGS_PARM2(ctx);

    // 使用#pragma unroll展开循环
    #pragma unroll
    for (int i = 0; i < 16; i++) {  // 固定小循环
        bpf_probe_read(&buf[i * 16], 16, user_buf + i * 16);
    }

    // 或者直接一次读取
    bpf_probe_read_user(buf, sizeof(buf), user_buf);

    return 0;
}
```

### 内联函数

```c
// 定义内联helper函数
static __always_inline bool is_interesting_comm(const char *comm)
{
    // 快速检查
    return comm[0] == 'n' && comm[1] == 'g' && comm[2] == 'i' &&
           comm[3] == 'n' && comm[4] == 'x';
}

static __always_inline u64 get_time_ns()
{
    return bpf_ktime_get_ns();
}

SEC("kprobe/tcp_sendmsg")
int trace_tcp(struct pt_regs *ctx)
{
    char comm[16];
    bpf_get_current_comm(&comm, sizeof(comm));

    // 使用内联函数
    if (!is_interesting_comm(comm))
        return 0;  // 提前返回

    u64 ts = get_time_ns();
    // ... 处理逻辑

    return 0;
}
```

### 避免复杂计算

```c
// 低效: 使用除法和模运算
SEC("kprobe/example")
int example_slow(struct pt_regs *ctx)
{
    u64 value = PT_REGS_PARM1(ctx);

    // 除法很慢
    u64 result = value / 1000;
    u64 remainder = value % 1000;

    return 0;
}

// 高效: 使用位操作和乘法
SEC("kprobe/example")
int example_fast(struct pt_regs *ctx)
{
    u64 value = PT_REGS_PARM1(ctx);

    // 位移代替2的幂次除法
    u64 result = value >> 10;  // value / 1024

    // 乘法代替除法 (如果可能)
    // value / 1000 ≈ (value * 1049) >> 20
    u64 approx = (value * 1049) >> 20;

    return 0;
}

// 提前返回，避免不必要计算
SEC("kprobe/tcp_sendmsg")
int trace_tcp_optimized(struct pt_regs *ctx)
{
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    // 快速过滤
    if (pid < 1000)  // 系统进程
        return 0;

    char comm[16];
    bpf_get_current_comm(&comm, sizeof(comm));

    // 提前检查
    if (comm[0] != 'n')  // 不是nginx
        return 0;

    // 只有必要时才做复杂计算
    // ... 处理逻辑

    return 0;
}
```

---

## Maps优化

### Map类型选择

```yaml
Map类型性能对比:
  BPF_MAP_TYPE_HASH:
    查找: O(1) 平均, O(n) 最坏
    适用: 动态key, 不可预测大小
    内存: key数量 * (key_size + value_size + 开销)

  BPF_MAP_TYPE_ARRAY:
    查找: O(1) 确定
    适用: 固定大小, 连续索引
    内存: max_entries * value_size
    优势: 最快，最低开销

  BPF_MAP_TYPE_PERCPU_HASH:
    查找: O(1) 无锁
    适用: 高并发写入
    内存: CPU数 * hash内存

  BPF_MAP_TYPE_PERCPU_ARRAY:
    查找: O(1) 无锁
    适用: 高并发统计
    内存: CPU数 * array内存
    优势: 最快的统计聚合

  BPF_MAP_TYPE_LRU_HASH:
    查找: O(1)
    适用: 固定内存，自动淘汰
    内存: max_entries * (key+value+开销)
    优势: 自动管理内存

选择建议:
  统计聚合 → PERCPU_ARRAY
  高频查找 → ARRAY
  动态key → HASH/LRU_HASH
  高并发 → PERCPU_*
```

**Map类型示例**:

```c
// 场景1: 统计计数 - 使用PERCPU_ARRAY (最快)
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __type(key, u32);
    __type(value, u64);
    __uint(max_entries, 256);  // 固定统计类别
} stats SEC(".maps");

// 场景2: 动态key - 使用LRU_HASH (自动淘汰)
struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __type(key, u32);  // PID
    __type(value, struct task_info);
    __uint(max_entries, 10000);
} task_cache SEC(".maps");

// 场景3: 高频临时存储 - 使用PERCPU_HASH
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_HASH);
    __type(key, u64);  // thread_id
    __type(value, u64);  // timestamp
    __uint(max_entries, 10240);
} timestamps SEC(".maps");
```

### Map大小调优

```c
// 低效: Map过大，浪费内存
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1000000);  // 1M entries!
} huge_map SEC(".maps");

// 高效: 合理大小
struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __uint(max_entries, 10000);  // 10K entries, LRU自动淘汰
} reasonable_map SEC(".maps");

// 根据实际负载调整
// 检查Map使用率:
// bpftool map list
// bpftool map dump id <map_id>
```

### Per-CPU Maps

```c
// Per-CPU Maps避免锁竞争
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __type(key, u32);
    __type(value, struct stats_t);
    __uint(max_entries, 1);
} percpu_stats SEC(".maps");

SEC("kprobe/tcp_sendmsg")
int trace_tcp(struct pt_regs *ctx)
{
    u32 key = 0;
    struct stats_t *stats;

    // 每个CPU独立，无锁
    stats = bpf_map_lookup_elem(&percpu_stats, &key);
    if (stats) {
        stats->packets++;
        stats->bytes += PT_REGS_PARM3(ctx);
    }

    return 0;
}

// 用户态聚合
void read_percpu_stats() {
    unsigned int nr_cpus = libbpf_num_possible_cpus();
    struct stats_t values[nr_cpus];
    struct stats_t total = {0};
    u32 key = 0;

    bpf_map_lookup_elem(fd, &key, values);

    for (int i = 0; i < nr_cpus; i++) {
        total.packets += values[i].packets;
        total.bytes += values[i].bytes;
    }
}
```

### LRU Maps

```c
// LRU Maps自动淘汰旧数据
struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __type(key, u32);
    __type(value, struct conn_info);
    __uint(max_entries, 10000);
} connections SEC(".maps");

SEC("kprobe/tcp_connect")
int trace_connect(struct pt_regs *ctx)
{
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    struct conn_info info = {
        .timestamp = bpf_ktime_get_ns(),
        // ... 其他字段
    };

    // 自动淘汰最久未使用的entry
    bpf_map_update_elem(&connections, &pid, &info, BPF_ANY);

    return 0;
}
```

---

## 数据传输优化

### Ringbuf vs Perf Buffer

```yaml
性能对比:
  Ringbuf (推荐, 内核5.8+):
    ✅ 更高吞吐量 (2-3x)
    ✅ 更低内存使用
    ✅ 更好的局部性
    ✅ 无需per-CPU buffer
    ✅ 动态大小调整

  Perf Buffer (传统):
    ✅ 更广泛支持
    ❌ per-CPU buffer (内存多)
    ❌ 复杂的用户态处理
    ❌ 容易丢事件

选择建议:
  内核5.8+ → 使用Ringbuf
  内核5.8- → 使用Perf Buffer
  高吞吐 → 使用Ringbuf
```

**Ringbuf示例 (推荐)**:

```c
// Ringbuf: 更高效
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);  // 256KB
} events SEC(".maps");

SEC("kprobe/tcp_sendmsg")
int trace_tcp(struct pt_regs *ctx)
{
    struct event_t *event;

    // Reserve space
    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 0;

    // 填充数据
    event->pid = bpf_get_current_pid_tgid() >> 32;
    event->bytes = PT_REGS_PARM3(ctx);
    bpf_get_current_comm(&event->comm, sizeof(event->comm));

    // Submit
    bpf_ringbuf_submit(event, 0);

    return 0;
}
```

### 批量处理

```c
// 低效: 每个事件单独发送
SEC("kprobe/tcp_sendmsg")
int trace_tcp_per_event(struct pt_regs *ctx)
{
    struct event_t event = {...};
    bpf_perf_event_output(ctx, &events, BPF_F_CURRENT_CPU, &event, sizeof(event));
    return 0;
}

// 高效: 批量聚合后发送
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __type(key, u32);
    __type(value, struct batch_t);
    __uint(max_entries, 1);
} batch SEC(".maps");

struct batch_t {
    u32 count;
    struct event_t events[100];  // 批量
};

SEC("kprobe/tcp_sendmsg")
int trace_tcp_batched(struct pt_regs *ctx)
{
    u32 key = 0;
    struct batch_t *batch = bpf_map_lookup_elem(&batch, &key);
    if (!batch)
        return 0;

    // 添加到batch
    if (batch->count < 100) {
        batch->events[batch->count++] = (struct event_t){...};
    }

    // 达到阈值时发送
    if (batch->count >= 100) {
        bpf_perf_event_output(ctx, &events, BPF_F_CURRENT_CPU,
                              batch, sizeof(*batch));
        batch->count = 0;
    }

    return 0;
}
```

### 数据过滤

```c
// 核心原则: 在内核态过滤，减少用户态数据传输

// 低效: 传输所有数据到用户态过滤
SEC("kprobe/tcp_sendmsg")
int trace_all(struct pt_regs *ctx)
{
    struct event_t event = {...};
    // 发送所有事件
    bpf_ringbuf_output(&events, &event, sizeof(event), 0);
    return 0;
}

// 高效: 在eBPF中过滤
SEC("kprobe/tcp_sendmsg")
int trace_filtered(struct pt_regs *ctx)
{
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    // 过滤1: 只关注特定PID
    if (pid < 1000)
        return 0;

    char comm[16];
    bpf_get_current_comm(&comm, sizeof(comm));

    // 过滤2: 只关注特定进程
    if (comm[0] != 'n' || comm[1] != 'g')  // nginx
        return 0;

    size_t bytes = PT_REGS_PARM3(ctx);

    // 过滤3: 只关注大包
    if (bytes < 1024)
        return 0;

    // 只有通过所有过滤器才发送
    struct event_t event = {...};
    bpf_ringbuf_output(&events, &event, sizeof(event), 0);

    return 0;
}

// 过滤效果: 数据量减少90%+, CPU开销降低80%+
```

---

## JIT编译优化

### JIT工作原理

```yaml
eBPF JIT编译流程:
  1. eBPF字节码 → 2. JIT编译器 → 3. 原生机器码 → 4. 直接执行

JIT优势:
  ✅ 接近原生代码性能
  ✅ 消除解释器开销
  ✅ 5-10x性能提升
```

**启用JIT**:

```bash
# 启用JIT (推荐)
echo 1 > /proc/sys/net/core/bpf_jit_enable

# 查看JIT汇编
bpftool prog dump jited id <prog_id>
```

---

## 实战优化案例

### 案例1: 高频追踪优化

```c
// 优化: 内核态聚合 + 采样
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_HASH);
    __type(key, u32);
    __type(value, struct stats_t);
    __uint(max_entries, 10000);
} stats SEC(".maps");

SEC("tracepoint/syscalls/sys_enter_read")
int trace_read_optimized(struct trace_event_raw_sys_enter *ctx)
{
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    // 快速过滤
    if (pid < 1000)
        return 0;

    // 内核态聚合
    struct stats_t *st = bpf_map_lookup_elem(&stats, &pid);
    if (st) {
        __sync_fetch_and_add(&st->count, 1);
        __sync_fetch_and_add(&st->bytes, ctx->args[2]);
    } else {
        struct stats_t init = {.count = 1, .bytes = ctx->args[2]};
        bpf_map_update_elem(&stats, &pid, &init, BPF_NOEXIST);
    }

    // 采样: 只发送1%
    if ((bpf_get_prandom_u32() % 100) == 0) {
        // 发送采样事件
    }

    return 0;
}

// 优化效果:
// - CPU: 15% → <2% (7.5x降低)
// - 数据传输: 100% → 1% (100x降低)
```

### 案例2: Map性能调优

```c
// 优化: 使用LRU_HASH自动管理
struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __uint(max_entries, 10000);
} connections SEC(".maps");

// 优化效果:
// - 内存: 稳定在固定大小
// - 延迟: 降低30%
// - 无需手动管理
```

---

## 性能测试

```bash
# 基准测试
perf stat -e 'bpf:*' -a sleep 10

# CPU Profiling
perf record -F 99 -a -g -- sleep 10
perf report

# 实时监控
watch -n 1 'bpftool prog show; bpftool map show'
```

---

## 最佳实践

```yaml
优化清单:
  eBPF程序:
    ✅ 提前返回
    ✅ 循环展开
    ✅ 避免复杂计算
    ✅ 位操作代替算术

  Maps:
    ✅ 选择合适类型
    ✅ 使用Per-CPU
    ✅ 使用LRU

  数据传输:
    ✅ 优先Ringbuf
    ✅ 内核态过滤
    ✅ 内核态聚合
    ✅ 采样而非全量

监控指标:
  ✅ CPU <2%
  ✅ 内存 <200MB
  ✅ 丢失率 <0.1%
```

---

## 参考资料

- [eBPF Performance](https://ebpf.io/what-is-ebpf/#performance)
- [BPF Performance Tools](http://www.brendangregg.com/bpf-performance-tools-book.html)

---

**文档版本**: v1.0
**最后更新**: 2025-10-19
**维护者**: 虚拟化容器化技术知识库项目组

**本章总结**:

本章深入介绍了eBPF性能优化技术，包括：

- ✅ **eBPF程序优化**: 代码结构、循环展开、内联函数
- ✅ **Maps优化**: 类型选择、Per-CPU、LRU
- ✅ **数据传输优化**: Ringbuf、批量处理、数据过滤
- ✅ **JIT编译优化**: JIT原理、优化技巧
- ✅ **实战优化案例**: CPU降低7.5x、数据传输降低100x
- ✅ **性能测试**: 基准测试、性能分析工具
- ✅ **最佳实践**: 完整优化清单

**优化效果**: CPU开销降低50-90%, 内存减少30-70%, 吞吐量提升2-10x

**下一步阅读**:

- [07_eBPF实战案例](./07_eBPF实战案例.md)
- [08_eBPF最佳实践](./08_eBPF最佳实践.md)

---

## 相关文档

### 本模块相关

- [eBPF概述与架构](./01_eBPF概述与架构.md) - eBPF概述与架构详解
- [eBPF网络技术](./02_eBPF网络技术.md) - eBPF网络技术详解
- [eBPF与容器技术](./03_eBPF与容器技术.md) - eBPF与容器技术详解
- [eBPF可观测性](./04_eBPF可观测性.md) - eBPF可观测性详解
- [eBPF安全技术](./05_eBPF安全技术.md) - eBPF安全技术详解
- [eBPF实战案例](./07_eBPF实战案例.md) - eBPF实战案例详解
- [eBPF最佳实践](./08_eBPF最佳实践.md) - eBPF最佳实践详解
- [README.md](./README.md) - 本模块导航

### 其他模块相关

- [容器性能调优](../06_容器监控与运维/03_容器性能调优.md) - 容器性能调优
- [容器监控技术](../06_容器监控与运维/01_容器监控技术.md) - 容器监控技术
- [Kubernetes技术详解](../03_Kubernetes技术详解/README.md) - Kubernetes技术体系

---

**最后更新**: 2025年11月11日
**维护状态**: 持续更新

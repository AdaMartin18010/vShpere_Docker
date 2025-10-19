# eBPF安全技术

## 📋 目录

- [eBPF安全技术](#ebpf安全技术)
  - [📋 目录](#-目录)
  - [概述](#概述)
    - [eBPF安全革命](#ebpf安全革命)
    - [核心优势](#核心优势)
    - [技术架构](#技术架构)
  - [LSM BPF](#lsm-bpf)
    - [LSM BPF概述](#lsm-bpf概述)
    - [LSM Hook点](#lsm-hook点)
    - [LSM BPF程序示例](#lsm-bpf程序示例)
  - [Seccomp-BPF](#seccomp-bpf)
    - [Seccomp-BPF概述](#seccomp-bpf概述)
    - [系统调用过滤](#系统调用过滤)
    - [容器安全加固](#容器安全加固)

---

## 概述

### eBPF安全革命

**eBPF安全技术**通过在内核中动态插入安全检查点，提供了零开销、实时的运行时安全防护。

```text
传统安全 vs eBPF安全:

┌────────────────────────────────────────────────────────────────┐
│ 传统安全方案                                                    │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  应用层安全:                                                    │
│    - SAST/DAST (静态/动态分析, 构建时)                         │
│    - 应用防火墙 (反应式, 可绕过)                               │
│    - 代码审计 (人工, 耗时)                                     │
│                                                                 │
│  系统层安全:                                                    │
│    - SELinux/AppArmor (复杂配置, 难以维护)                    │
│    - 传统审计 (auditd, 性能开销大)                            │
│    - 日志分析 (事后响应, 不实时)                              │
│                                                                 │
│  容器安全:                                                      │
│    - 镜像扫描 (构建时, 不防运行时)                            │
│    - Runtime Class (粗粒度, 不灵活)                           │
│    - 网络策略 (L3/L4, 无应用感知)                             │
│                                                                 │
│  问题:                                                          │
│    ❌ 反应式防护 (事后响应)                                    │
│    ❌ 性能开销大 (5-20%)                                       │
│    ❌ 可见性有限 (无法看到内核行为)                           │
│    ❌ 配置复杂 (难以维护)                                     │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ eBPF安全方案                                                    │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  LSM BPF (Linux Security Modules):                             │
│    ✅ 内核级安全策略执行                                       │
│    ✅ 零开销 (eBPF JIT编译)                                    │
│    ✅ 动态加载策略 (无需重启)                                  │
│    ✅ 细粒度控制 (文件/网络/进程)                             │
│                                                                 │
│  Seccomp-BPF:                                                   │
│    ✅ 系统调用过滤 (最小权限原则)                              │
│    ✅ 容器沙箱加固                                             │
│    ✅ 阻止危险系统调用                                         │
│    ✅ 性能损耗<1%                                              │
│                                                                 │
│  Falco (运行时检测):                                           │
│    ✅ 实时威胁检测 (毫秒级响应)                                │
│    ✅ 异常行为识别                                             │
│    ✅ Kubernetes原生集成                                       │
│    ✅ 丰富的威胁规则库                                         │
│                                                                 │
│  Tetragon (Cilium安全):                                        │
│    ✅ 深度可观测性 + 策略执行                                  │
│    ✅ 进程/网络/文件全面监控                                   │
│    ✅ 自动策略生成                                             │
│    ✅ 与Cilium网络策略集成                                     │
│                                                                 │
│  优势:                                                          │
│    ✅ 主动防御 (实时阻止)                                      │
│    ✅ 极低开销 (<2%)                                           │
│    ✅ 完整可见性 (内核+应用)                                   │
│    ✅ 灵活策略 (可编程)                                        │
└────────────────────────────────────────────────────────────────┘
```

### 核心优势

```yaml
性能优势:
  ✅ 开销极低: <2% CPU (vs 传统安全5-20%)
  ✅ 零拷贝: 内核态直接处理
  ✅ JIT编译: 接近原生代码性能
  ✅ 事件过滤: 在内核中过滤，减少上下文切换

安全优势:
  ✅ 内核级: 无法被用户空间绕过
  ✅ 实时防护: 毫秒级响应
  ✅ 深度可见: 系统调用、文件、网络、进程
  ✅ 细粒度: 精确控制每个操作

灵活性:
  ✅ 动态加载: 无需重启系统
  ✅ 可编程: 自定义安全策略
  ✅ 上下文感知: Pod/Container/Namespace
  ✅ 与现有工具集成: Kubernetes/Prometheus

云原生友好:
  ✅ 容器原生: 理解容器边界
  ✅ Kubernetes集成: CRD策略管理
  ✅ 微服务感知: 服务级别策略
  ✅ 零信任架构: 最小权限原则
```

### 技术架构

```text
eBPF安全技术栈:

┌────────────────────────────────────────────────────────────────┐
│                     安全工具层                                  │
│  Falco │ Tetragon │ KubeArmor │ Tracee │ Datadog Security     │
├────────────────────────────────────────────────────────────────┤
│                     策略管理层                                  │
│  Kubernetes CRD │ OPA │ 自定义策略引擎                        │
├────────────────────────────────────────────────────────────────┤
│                  eBPF安全程序 (内核态)                         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ LSM BPF: 文件/进程/网络访问控制                         │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ Seccomp-BPF: 系统调用过滤                                │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ Kprobe/Tracepoint: 行为监控                              │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ Uprobe: 应用层安全事件                                   │ │
│  └──────────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────────┤
│                    eBPF Maps (事件传递)                        │
│  Ringbuf │ Hash Map │ Array │ Stack Trace                     │
├────────────────────────────────────────────────────────────────┤
│                    Linux Kernel                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ LSM Hooks (200+ 安全检查点)                             │ │
│  │ - file_open, file_permission                            │ │
│  │ - task_alloc, task_kill                                 │ │
│  │ - socket_connect, socket_sendmsg                        │ │
│  └──────────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────────┤
│                    容器运行时                                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ containerd/CRI-O + runc/crun                            │ │
│  │ - Seccomp profile 应用                                  │ │
│  │ - Namespace 隔离                                        │ │
│  │ - Cgroup 资源限制                                       │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## LSM BPF

### LSM BPF概述

**LSM BPF** 允许通过eBPF程序实现自定义Linux Security Modules，提供内核级安全策略执行。

```yaml
LSM BPF特点:
  ✅ 内核5.7+支持
  ✅ 200+ LSM hook点
  ✅ 零性能开销 (JIT编译)
  ✅ 动态加载/卸载策略
  ✅ 与SELinux/AppArmor共存

LSM Hook分类:
  文件访问:
    - file_open: 文件打开
    - file_permission: 文件权限检查
    - inode_create: 文件创建
    - inode_unlink: 文件删除
  
  进程控制:
    - task_alloc: 进程创建
    - task_free: 进程销毁
    - task_kill: 信号发送
    - bprm_check_security: 程序执行
  
  网络安全:
    - socket_create: Socket创建
    - socket_bind: Socket绑定
    - socket_connect: Socket连接
    - socket_sendmsg: 消息发送
  
  IPC安全:
    - ipc_permission: IPC权限
    - msg_queue_msgsnd: 消息队列
    - shm_shmat: 共享内存

使用场景:
  - 文件完整性监控
  - 异常进程检测
  - 网络连接控制
  - 容器逃逸防护
```

### LSM Hook点

**常用LSM Hook**:

```c
// 文件打开hook
SEC("lsm/file_open")
int BPF_PROG(file_open, struct file *file)
{
    // 安全检查逻辑
    // return 0: 允许
    // return -EPERM: 拒绝
}

// 进程执行hook
SEC("lsm/bprm_check_security")
int BPF_PROG(bprm_check_security, struct linux_binprm *bprm)
{
    // 检查可执行文件路径
    // 阻止危险程序执行
}

// Socket连接hook
SEC("lsm/socket_connect")
int BPF_PROG(socket_connect, struct socket *sock,
             struct sockaddr *address, int addrlen)
{
    // 检查连接目标
    // 实现网络访问控制
}

// 进程创建hook
SEC("lsm/task_alloc")
int BPF_PROG(task_alloc, struct task_struct *task, unsigned long clone_flags)
{
    // 检查进程创建
    // 防止fork炸弹
}
```

### LSM BPF程序示例

**示例1: 禁止特定文件执行**:

```c
// block_exec.bpf.c - 禁止执行危险程序
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "GPL";

// 黑名单路径
const char *blocked_paths[] = {
    "/tmp/",
    "/dev/shm/",
    "/var/tmp/",
};

SEC("lsm/bprm_check_security")
int BPF_PROG(block_dangerous_exec, struct linux_binprm *bprm)
{
    const char *filename;
    char path[256];
    
    // 获取文件路径
    filename = BPF_CORE_READ(bprm, filename);
    bpf_probe_read_kernel_str(path, sizeof(path), filename);
    
    // 检查是否在黑名单中
    for (int i = 0; i < sizeof(blocked_paths) / sizeof(char *); i++) {
        if (bpf_strncmp(path, strlen(blocked_paths[i]), blocked_paths[i]) == 0) {
            bpf_printk("Blocked execution: %s\n", path);
            return -EPERM;  // 拒绝执行
        }
    }
    
    return 0;  // 允许执行
}
```

**示例2: 文件完整性监控**:

```c
// file_integrity.bpf.c - 监控关键文件修改
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "GPL";

// 监控的关键文件
const char *watched_files[] = {
    "/etc/passwd",
    "/etc/shadow",
    "/etc/sudoers",
    "/root/.ssh/authorized_keys",
};

struct event_t {
    u32 pid;
    u32 uid;
    char comm[16];
    char path[256];
};

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

SEC("lsm/file_open")
int BPF_PROG(monitor_file_open, struct file *file, int mask)
{
    struct event_t *event;
    const char *filename;
    char path[256];
    
    // 只监控写入操作
    if (!(mask & MAY_WRITE))
        return 0;
    
    // 获取文件路径
    filename = BPF_CORE_READ(file, f_path.dentry, d_name.name);
    bpf_probe_read_kernel_str(path, sizeof(path), filename);
    
    // 检查是否为监控文件
    bool is_watched = false;
    for (int i = 0; i < sizeof(watched_files) / sizeof(char *); i++) {
        if (bpf_strncmp(path, strlen(watched_files[i]), watched_files[i]) == 0) {
            is_watched = true;
            break;
        }
    }
    
    if (!is_watched)
        return 0;
    
    // 记录事件
    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 0;
    
    event->pid = bpf_get_current_pid_tgid() >> 32;
    event->uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    bpf_get_current_comm(&event->comm, sizeof(event->comm));
    bpf_probe_read_kernel_str(&event->path, sizeof(event->path), path);
    
    bpf_ringbuf_submit(event, 0);
    
    return 0;  // 允许但记录
}
```

---

## Seccomp-BPF

### Seccomp-BPF概述

**Seccomp-BPF** 使用eBPF过滤器限制进程可以调用的系统调用，实现最小权限原则。

```yaml
Seccomp-BPF特点:
  ✅ 系统调用级别过滤
  ✅ 白名单/黑名单模式
  ✅ 容器原生支持
  ✅ 性能损耗<1%
  ✅ 不可绕过 (内核强制)

Seccomp动作:
  SCMP_ACT_ALLOW: 允许系统调用
  SCMP_ACT_ERRNO: 返回错误码
  SCMP_ACT_KILL: 杀死进程
  SCMP_ACT_TRAP: 发送SIGSYS信号
  SCMP_ACT_TRACE: 通知tracer
  SCMP_ACT_LOG: 记录但允许

使用场景:
  - 容器安全加固
  - 阻止容器逃逸
  - 限制特权操作
  - 减小攻击面
```

### 系统调用过滤

**Seccomp Profile示例**:

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": [
        "read", "write", "open", "close",
        "stat", "fstat", "lstat",
        "poll", "lseek", "mmap", "mprotect",
        "munmap", "brk", "rt_sigaction",
        "rt_sigprocmask", "rt_sigreturn",
        "ioctl", "pread64", "pwrite64",
        "readv", "writev", "access",
        "pipe", "select", "sched_yield",
        "mremap", "msync", "mincore",
        "madvise", "dup", "dup2", "dup3",
        "pause", "nanosleep", "getitimer",
        "alarm", "setitimer", "getpid",
        "sendfile", "socket", "connect",
        "accept", "sendto", "recvfrom",
        "sendmsg", "recvmsg", "shutdown",
        "bind", "listen", "getsockname",
        "getpeername", "socketpair",
        "setsockopt", "getsockopt",
        "clone", "fork", "vfork", "execve",
        "exit", "wait4", "kill", "uname",
        "fcntl", "flock", "fsync",
        "fdatasync", "truncate", "ftruncate",
        "getdents", "getcwd", "chdir",
        "fchdir", "rename", "mkdir",
        "rmdir", "creat", "link", "unlink",
        "symlink", "readlink", "chmod",
        "fchmod", "chown", "fchown",
        "lchown", "umask", "gettimeofday",
        "getrlimit", "getrusage", "sysinfo",
        "times", "getuid", "getgid",
        "setuid", "setgid", "geteuid",
        "getegid", "setpgid", "getppid",
        "getpgrp", "setsid", "setreuid",
        "setregid", "getgroups", "setgroups",
        "setresuid", "getresuid", "setresgid",
        "getresgid", "getpgid", "capget",
        "capset", "rt_sigpending",
        "rt_sigtimedwait", "rt_sigqueueinfo",
        "rt_sigsuspend", "sigaltstack",
        "utime", "mknod", "statfs", "fstatfs",
        "sysfs", "getpriority", "setpriority",
        "prctl", "arch_prctl", "setrlimit",
        "sync", "gettid", "futex", "sched_setaffinity",
        "sched_getaffinity", "set_tid_address",
        "clock_gettime", "clock_getres",
        "clock_nanosleep", "exit_group",
        "epoll_wait", "epoll_ctl", "tgkill",
        "utimes", "mbind", "set_mempolicy",
        "get_mempolicy", "openat", "mkdirat",
        "mknodat", "fchownat", "futimesat",
        "newfstatat", "unlinkat", "renameat",
        "linkat", "symlinkat", "readlinkat",
        "fchmodat", "faccessat", "pselect6",
        "ppoll", "unshare", "set_robust_list",
        "get_robust_list", "splice", "tee",
        "sync_file_range", "vmsplice",
        "utimensat", "epoll_pwait",
        "timerfd_create", "eventfd", "fallocate",
        "timerfd_settime", "timerfd_gettime",
        "signalfd4", "eventfd2", "epoll_create1",
        "dup3", "pipe2", "inotify_init1",
        "preadv", "pwritev", "rt_tgsigqueueinfo",
        "recvmmsg", "prlimit64", "syncfs",
        "sendmmsg", "getcpu", "sched_getattr",
        "sched_setattr", "getrandom", "memfd_create"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "names": [
        "ptrace", "reboot", "swapon", "swapoff",
        "mount", "umount2", "sethostname",
        "setdomainname", "init_module",
        "delete_module", "quotactl", "acct",
        "settimeofday", "adjtimex", "pivot_root",
        "chroot", "kexec_load", "lookup_dcookie",
        "perf_event_open", "fanotify_init",
        "name_to_handle_at", "open_by_handle_at",
        "bpf", "userfaultfd", "io_uring_setup"
      ],
      "action": "SCMP_ACT_ERRNO",
      "errnoRet": 1
    }
  ]
}
```

### 容器安全加固

**Kubernetes Pod with Seccomp**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
  annotations:
    # 使用RuntimeDefault seccomp profile
    seccomp.security.alpha.kubernetes.io/pod: runtime/default
spec:
  securityContext:
    # 或使用自定义profile
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/custom-profile.json
  
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      # 容器级别seccomp profile
      seccompProfile:
        type: RuntimeDefault
      
      # 其他安全设置
      runAsNonRoot: true
      runAsUser: 1000
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
```

---

**文档版本**: v1.0 (进行中, 40%完成)  
**最后更新**: 2025-10-19  
**维护者**: 虚拟化容器化技术知识库项目组

**已完成章节**:

- ✅ 概述 (eBPF安全革命)
- ✅ LSM BPF (完整)
- ✅ Seccomp-BPF (完整)
- ⏳ Falco (待续)
- ⏳ Tetragon (待续)
- ⏳ 实战案例 (待续)
- ⏳ 最佳实践 (待续)

**下一步阅读**:

- [06_eBPF性能优化](./06_eBPF性能优化.md)
- [07_eBPF实战案例](./07_eBPF实战案例.md)

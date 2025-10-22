#!/usr/bin/env python3
"""
K8s AI Scheduler 预测测试脚本
"""

import time
import random
from kubernetes import client, config

def create_memory_leak_pod():
    """创建内存泄漏模拟Pod"""
    config.load_kube_config()
    v1 = client.CoreV1Api()
    
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name="memory-leak-test"),
        spec=client.V1PodSpec(
            scheduler_name="ai-scheduler",
            containers=[
                client.V1Container(
                    name="leak",
                    image="python:3.11-alpine",
                    command=["python", "-c"],
                    args=["""
import time
data = []
while True:
    data.append(' ' * 1024 * 1024)  # 1MB per second
    time.sleep(1)
                    """],
                    resources=client.V1ResourceRequirements(
                        requests={"memory": "64Mi"},
                        limits={"memory": "256Mi"}
                    )
                )
            ]
        )
    )
    
    v1.create_namespaced_pod(namespace="default", body=pod)
    print("✅ 内存泄漏测试Pod已创建")

def monitor_predictions():
    """监控AI预测"""
    config.load_kube_config()
    v1 = client.CoreV1Api()
    
    print("🔍 监控AI预测...")
    
    for i in range(60):
        # 获取Pod状态
        pod = v1.read_namespaced_pod(name="memory-leak-test", namespace="default")
        
        # 检查驱逐事件
        events = v1.list_namespaced_event(
            namespace="default",
            field_selector=f"involvedObject.name=memory-leak-test,reason=AIEviction"
        )
        
        if events.items:
            print(f"🎯 AI预测驱逐! (第{i}秒)")
            print(f"   原因: {events.items[0].message}")
            return True
        
        print(f"⏱️  {i}s: Pod状态={pod.status.phase}")
        time.sleep(1)
    
    print("⏰ 60秒超时，未触发AI驱逐")
    return False

if __name__ == "__main__":
    create_memory_leak_pod()
    time.sleep(5)
    monitor_predictions()


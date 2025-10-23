#!/usr/bin/env python3
"""
libvirt域生命周期测试套件
按功能模块组织：创建、启动、停止、重启、快照、克隆、删除
"""

import pytest
import libvirt
import time
import xml.etree.ElementTree as ET


class LibvirtLifecycleTestSuite:
    """libvirt域生命周期测试套件"""
    
    @pytest.fixture(scope="class")
    def libvirt_connection(self):
        """创建libvirt连接"""
        # 连接到QEMU/KVM
        conn = libvirt.open('qemu:///system')
        if conn is None:
            pytest.skip("无法连接到libvirt")
        
        yield conn
        
        # 清理
        conn.close()
    
    # ====================
    # 辅助方法
    # ====================
    
    def _create_test_domain_xml(self, name):
        """创建测试域的XML定义"""
        xml = f"""
        <domain type='kvm'>
          <name>{name}</name>
          <memory unit='MB'>1024</memory>
          <vcpu>1</vcpu>
          <os>
            <type arch='x86_64'>hvm</type>
            <boot dev='hd'/>
          </os>
          <devices>
            <disk type='file' device='disk'>
              <driver name='qemu' type='qcow2'/>
              <source file='/var/lib/libvirt/images/{name}.qcow2'/>
              <target dev='vda' bus='virtio'/>
            </disk>
            <interface type='network'>
              <source network='default'/>
              <model type='virtio'/>
            </interface>
            <graphics type='vnc' port='-1'/>
          </devices>
        </domain>
        """
        return xml
    
    def _wait_for_domain_state(self, domain, expected_state, timeout=30):
        """等待域达到指定状态"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            state, reason = domain.state()
            if state == expected_state:
                return True
            time.sleep(1)
        return False
    
    # ====================
    # 1. 域创建测试
    # ====================
    
    def test_define_domain(self, libvirt_connection):
        """测试定义域"""
        domain_name = f"test-domain-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义域
        domain = libvirt_connection.defineXML(xml)
        assert domain is not None
        assert domain.name() == domain_name
        print(f"✅ 定义域成功: {domain_name}")
        
        # 清理
        domain.undefine()
    
    def test_define_domain_with_custom_cpu(self, libvirt_connection):
        """测试定义自定义CPU的域"""
        domain_name = f"test-domain-cpu-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 修改XML以设置4核CPU
        root = ET.fromstring(xml)
        vcpu = root.find('vcpu')
        vcpu.text = '4'
        vcpu.set('placement', 'static')
        
        # 添加CPU拓扑
        cpu = ET.SubElement(root, 'cpu')
        topology = ET.SubElement(cpu, 'topology')
        topology.set('sockets', '1')
        topology.set('cores', '4')
        topology.set('threads', '1')
        
        modified_xml = ET.tostring(root, encoding='unicode')
        
        # 定义域
        domain = libvirt_connection.defineXML(modified_xml)
        assert domain is not None
        
        # 验证vCPU数量
        info = domain.info()
        assert info[3] == 4, f"vCPU数量应该是4，实际: {info[3]}"
        print(f"✅ 定义4核域成功: {domain_name}")
        
        # 清理
        domain.undefine()
    
    def test_define_domain_with_custom_memory(self, libvirt_connection):
        """测试定义自定义内存的域"""
        domain_name = f"test-domain-mem-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 修改XML以设置4GB内存
        root = ET.fromstring(xml)
        memory = root.find('memory')
        memory.text = '4096'
        memory.set('unit', 'MB')
        
        modified_xml = ET.tostring(root, encoding='unicode')
        
        # 定义域
        domain = libvirt_connection.defineXML(modified_xml)
        assert domain is not None
        
        # 验证内存大小
        info = domain.info()
        assert info[1] == 4096 * 1024, f"内存应该是4GB"
        print(f"✅ 定义4GB内存域成功: {domain_name}")
        
        # 清理
        domain.undefine()
    
    # ====================
    # 2. 域启动测试
    # ====================
    
    def test_start_domain(self, libvirt_connection):
        """测试启动域"""
        domain_name = f"test-domain-start-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义域
        domain = libvirt_connection.defineXML(xml)
        
        try:
            # 启动域
            result = domain.create()
            assert result == 0, "启动域应该成功"
            
            # 验证状态
            state, _ = domain.state()
            assert state == libvirt.VIR_DOMAIN_RUNNING
            print(f"✅ 启动域成功: {domain_name}")
            
        finally:
            # 清理
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    def test_start_already_running_domain(self, libvirt_connection):
        """测试重复启动已运行的域"""
        domain_name = f"test-domain-restart-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义并启动域
        domain = libvirt_connection.defineXML(xml)
        
        try:
            # 第一次启动
            domain.create()
            
            # 第二次启动（应该失败）
            with pytest.raises(libvirt.libvirtError):
                domain.create()
            
            print(f"✅ 正确阻止重复启动")
            
        finally:
            # 清理
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    # ====================
    # 3. 域停止测试
    # ====================
    
    def test_shutdown_domain(self, libvirt_connection):
        """测试关闭域"""
        domain_name = f"test-domain-shutdown-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义并启动域
        domain = libvirt_connection.defineXML(xml)
        domain.create()
        
        try:
            # 关闭域
            result = domain.shutdown()
            assert result == 0, "关闭域应该成功"
            
            # 等待关闭（或超时后强制停止）
            if not self._wait_for_domain_state(domain, libvirt.VIR_DOMAIN_SHUTOFF, timeout=10):
                domain.destroy()
            
            # 验证状态
            state, _ = domain.state()
            assert state == libvirt.VIR_DOMAIN_SHUTOFF
            print(f"✅ 关闭域成功: {domain_name}")
            
        finally:
            # 清理
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    def test_destroy_domain(self, libvirt_connection):
        """测试强制停止域"""
        domain_name = f"test-domain-destroy-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义并启动域
        domain = libvirt_connection.defineXML(xml)
        domain.create()
        
        try:
            # 强制停止域
            result = domain.destroy()
            assert result == 0, "强制停止域应该成功"
            
            # 验证状态
            state, _ = domain.state()
            assert state == libvirt.VIR_DOMAIN_SHUTOFF
            print(f"✅ 强制停止域成功: {domain_name}")
            
        finally:
            # 清理
            domain.undefine()
    
    def test_suspend_resume_domain(self, libvirt_connection):
        """测试挂起和恢复域"""
        domain_name = f"test-domain-suspend-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义并启动域
        domain = libvirt_connection.defineXML(xml)
        domain.create()
        
        try:
            # 挂起域
            result = domain.suspend()
            assert result == 0, "挂起域应该成功"
            
            # 验证挂起状态
            state, _ = domain.state()
            assert state == libvirt.VIR_DOMAIN_PAUSED
            print(f"✅ 挂起域成功: {domain_name}")
            
            # 恢复域
            result = domain.resume()
            assert result == 0, "恢复域应该成功"
            
            # 验证运行状态
            state, _ = domain.state()
            assert state == libvirt.VIR_DOMAIN_RUNNING
            print(f"✅ 恢复域成功: {domain_name}")
            
        finally:
            # 清理
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    # ====================
    # 4. 域重启测试
    # ====================
    
    def test_reboot_domain(self, libvirt_connection):
        """测试重启域"""
        domain_name = f"test-domain-reboot-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义并启动域
        domain = libvirt_connection.defineXML(xml)
        domain.create()
        
        try:
            # 重启域
            result = domain.reboot(0)
            assert result == 0, "重启域应该成功"
            print(f"✅ 重启域成功: {domain_name}")
            
        finally:
            # 清理
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    def test_reset_domain(self, libvirt_connection):
        """测试重置域（强制重启）"""
        domain_name = f"test-domain-reset-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义并启动域
        domain = libvirt_connection.defineXML(xml)
        domain.create()
        
        try:
            # 重置域
            result = domain.reset(0)
            assert result == 0, "重置域应该成功"
            
            # 验证仍在运行
            state, _ = domain.state()
            assert state == libvirt.VIR_DOMAIN_RUNNING
            print(f"✅ 重置域成功: {domain_name}")
            
        finally:
            # 清理
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    # ====================
    # 5. 域快照测试
    # ====================
    
    def test_create_snapshot(self, libvirt_connection):
        """测试创建快照"""
        domain_name = f"test-domain-snap-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义域（无需启动）
        domain = libvirt_connection.defineXML(xml)
        
        try:
            # 快照XML
            snapshot_xml = f"""
            <domainsnapshot>
              <name>test-snapshot</name>
              <description>Test snapshot</description>
            </domainsnapshot>
            """
            
            # 创建快照
            snapshot = domain.snapshotCreateXML(snapshot_xml, 0)
            assert snapshot is not None
            assert snapshot.getName() == "test-snapshot"
            print(f"✅ 创建快照成功: test-snapshot")
            
            # 清理快照
            snapshot.delete(0)
            
        finally:
            # 清理
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    def test_revert_snapshot(self, libvirt_connection):
        """测试恢复快照"""
        domain_name = f"test-domain-revert-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义域
        domain = libvirt_connection.defineXML(xml)
        
        try:
            # 创建快照
            snapshot_xml = """
            <domainsnapshot>
              <name>revert-snapshot</name>
            </domainsnapshot>
            """
            snapshot = domain.snapshotCreateXML(snapshot_xml, 0)
            
            # 恢复快照
            result = domain.revertToSnapshot(snapshot, 0)
            assert result == 0, "恢复快照应该成功"
            print(f"✅ 恢复快照成功")
            
            # 清理快照
            snapshot.delete(0)
            
        finally:
            # 清理
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    def test_delete_snapshot(self, libvirt_connection):
        """测试删除快照"""
        domain_name = f"test-domain-delsnap-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义域
        domain = libvirt_connection.defineXML(xml)
        
        try:
            # 创建快照
            snapshot_xml = """
            <domainsnapshot>
              <name>delete-snapshot</name>
            </domainsnapshot>
            """
            snapshot = domain.snapshotCreateXML(snapshot_xml, 0)
            
            # 删除快照
            result = snapshot.delete(0)
            assert result == 0, "删除快照应该成功"
            print(f"✅ 删除快照成功")
            
            # 验证快照已删除
            with pytest.raises(libvirt.libvirtError):
                domain.snapshotLookupByName("delete-snapshot", 0)
            
        finally:
            # 清理
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    def test_list_snapshots(self, libvirt_connection):
        """测试列出快照"""
        domain_name = f"test-domain-listsnap-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义域
        domain = libvirt_connection.defineXML(xml)
        
        try:
            # 创建多个快照
            for i in range(3):
                snapshot_xml = f"""
                <domainsnapshot>
                  <name>snapshot-{i}</name>
                </domainsnapshot>
                """
                domain.snapshotCreateXML(snapshot_xml, 0)
            
            # 列出快照
            snapshots = domain.listAllSnapshots(0)
            assert len(snapshots) == 3
            print(f"✅ 列出快照成功: 共{len(snapshots)}个快照")
            
            # 清理快照
            for snapshot in snapshots:
                snapshot.delete(0)
            
        finally:
            # 清理
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    # ====================
    # 6. 域删除测试
    # ====================
    
    def test_undefine_inactive_domain(self, libvirt_connection):
        """测试删除未激活的域"""
        domain_name = f"test-domain-undef-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义域
        domain = libvirt_connection.defineXML(xml)
        domain_name_saved = domain.name()
        
        # 删除域
        result = domain.undefine()
        assert result == 0, "删除域应该成功"
        print(f"✅ 删除域成功: {domain_name_saved}")
        
        # 验证域已删除
        with pytest.raises(libvirt.libvirtError):
            libvirt_connection.lookupByName(domain_name_saved)
    
    def test_undefine_active_domain(self, libvirt_connection):
        """测试删除活动域（应该失败）"""
        domain_name = f"test-domain-undef-active-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 定义并启动域
        domain = libvirt_connection.defineXML(xml)
        domain.create()
        
        try:
            # 尝试删除活动域（应该失败）
            with pytest.raises(libvirt.libvirtError):
                domain.undefine()
            
            print(f"✅ 正确阻止删除活动域")
            
        finally:
            # 清理
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    # ====================
    # 7. 完整生命周期测试
    # ====================
    
    def test_full_lifecycle(self, libvirt_connection):
        """测试完整域生命周期"""
        print("\n=== libvirt域完整生命周期测试 ===")
        
        domain_name = f"test-domain-full-{int(time.time())}"
        xml = self._create_test_domain_xml(domain_name)
        
        # 1. 定义域
        domain = libvirt_connection.defineXML(xml)
        print(f"✅ 1. 定义域: {domain_name}")
        
        try:
            # 2. 启动域
            domain.create()
            state, _ = domain.state()
            assert state == libvirt.VIR_DOMAIN_RUNNING
            print("✅ 2. 启动域")
            
            # 3. 创建快照
            snapshot_xml = """
            <domainsnapshot>
              <name>lifecycle-snapshot</name>
              <description>Lifecycle test</description>
            </domainsnapshot>
            """
            snapshot = domain.snapshotCreateXML(snapshot_xml, 0)
            print("✅ 3. 创建快照")
            
            # 4. 挂起域
            domain.suspend()
            state, _ = domain.state()
            assert state == libvirt.VIR_DOMAIN_PAUSED
            print("✅ 4. 挂起域")
            
            # 5. 恢复域
            domain.resume()
            state, _ = domain.state()
            assert state == libvirt.VIR_DOMAIN_RUNNING
            print("✅ 5. 恢复域")
            
            # 6. 恢复快照
            domain.revertToSnapshot(snapshot, 0)
            print("✅ 6. 恢复快照")
            
            # 7. 删除快照
            snapshot.delete(0)
            print("✅ 7. 删除快照")
            
            # 8. 关闭域
            domain.destroy()
            state, _ = domain.state()
            assert state == libvirt.VIR_DOMAIN_SHUTOFF
            print("✅ 8. 关闭域")
            
            # 9. 删除域
            domain.undefine()
            print("✅ 9. 删除域")
            
            print("=== 完整生命周期测试完成 ===\n")
            
        except Exception as e:
            # 确保清理
            print(f"❌ 测试失败: {e}")
            if domain.isActive():
                domain.destroy()
            domain.undefine()
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


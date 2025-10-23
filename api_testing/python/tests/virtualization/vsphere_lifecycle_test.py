#!/usr/bin/env python3
"""
VMware vSphere虚拟机生命周期测试套件
按功能模块组织：创建、启动、停止、重启、快照、克隆、删除
"""

import pytest
import time
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import ssl
import atexit


class vSphereLifecycleTestSuite:
    """vSphere虚拟机生命周期测试套件"""
    
    @pytest.fixture(scope="class")
    def vsphere_connection(self):
        """创建vSphere连接"""
        # 配置 - 从环境变量或配置文件读取
        host = "vcenter.example.com"
        user = "administrator@vsphere.local"
        password = "your_password"
        port = 443
        
        # 禁用SSL验证（仅用于测试环境）
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        # 连接vCenter
        si = SmartConnect(
            host=host,
            user=user,
            pwd=password,
            port=port,
            sslContext=context
        )
        
        atexit.register(Disconnect, si)
        yield si
        
        # 清理
        Disconnect(si)
    
    # ====================
    # 辅助方法
    # ====================
    
    def _get_obj(self, content, vimtype, name=None):
        """获取vSphere对象"""
        obj = None
        container = content.viewManager.CreateContainerView(
            content.rootFolder, vimtype, True
        )
        for item in container.view:
            if name:
                if item.name == name:
                    obj = item
                    break
            else:
                obj = item
                break
        return obj
    
    def _wait_for_task(self, task, timeout=300):
        """等待任务完成"""
        start_time = time.time()
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"任务超时: {task.info.description}")
            time.sleep(1)
        
        if task.info.state == vim.TaskInfo.State.error:
            raise Exception(f"任务失败: {task.info.error.msg}")
        
        return task.info.result
    
    def _get_vm_by_name(self, content, name):
        """通过名称获取VM"""
        return self._get_obj(content, [vim.VirtualMachine], name)
    
    def _create_test_vm_spec(self, datacenter, datastore, resource_pool):
        """创建测试VM配置规范"""
        # VM配置
        config = vim.vm.ConfigSpec()
        config.name = f"test-vm-{int(time.time())}"
        config.memoryMB = 1024
        config.numCPUs = 1
        config.guestId = 'otherLinux64Guest'
        
        # 文件信息
        config.files = vim.vm.FileInfo()
        config.files.vmPathName = f"[{datastore.name}]"
        
        # 磁盘控制器
        disk_spec = vim.vm.device.VirtualDeviceSpec()
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        disk_spec.fileOperation = vim.vm.device.VirtualDeviceSpec.FileOperation.create
        
        disk = vim.vm.device.VirtualDisk()
        disk.capacityInKB = 10 * 1024 * 1024  # 10GB
        disk.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        disk.backing.diskMode = 'persistent'
        disk.backing.thinProvisioned = True
        
        disk_spec.device = disk
        
        config.deviceChange = [disk_spec]
        
        return config
    
    # ====================
    # 1. 虚拟机创建测试
    # ====================
    
    def test_create_basic_vm(self, vsphere_connection):
        """测试基础VM创建"""
        content = vsphere_connection.RetrieveContent()
        
        # 获取必要对象
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        # 创建VM配置
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        
        # 创建VM
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        assert vm is not None
        assert vm.name == config.name
        print(f"✅ 创建VM成功: {vm.name}")
        
        # 清理
        task = vm.Destroy_Task()
        self._wait_for_task(task)
    
    def test_create_vm_with_custom_cpu(self, vsphere_connection):
        """测试创建自定义CPU的VM"""
        content = vsphere_connection.RetrieveContent()
        
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        # 配置4核CPU
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        config.numCPUs = 4
        config.numCoresPerSocket = 2
        
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        assert vm.config.hardware.numCPU == 4
        print(f"✅ 创建4核VM成功: {vm.name}")
        
        # 清理
        task = vm.Destroy_Task()
        self._wait_for_task(task)
    
    def test_create_vm_with_custom_memory(self, vsphere_connection):
        """测试创建自定义内存的VM"""
        content = vsphere_connection.RetrieveContent()
        
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        # 配置4GB内存
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        config.memoryMB = 4096
        
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        assert vm.config.hardware.memoryMB == 4096
        print(f"✅ 创建4GB内存VM成功: {vm.name}")
        
        # 清理
        task = vm.Destroy_Task()
        self._wait_for_task(task)
    
    # ====================
    # 2. 虚拟机启动测试
    # ====================
    
    def test_power_on_vm(self, vsphere_connection):
        """测试启动VM"""
        content = vsphere_connection.RetrieveContent()
        
        # 创建测试VM
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        try:
            # 启动VM
            task = vm.PowerOn()
            self._wait_for_task(task)
            
            # 验证状态
            assert vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn
            print(f"✅ VM启动成功: {vm.name}")
            
        finally:
            # 清理
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                task = vm.PowerOff()
                self._wait_for_task(task)
            task = vm.Destroy_Task()
            self._wait_for_task(task)
    
    def test_power_on_already_running_vm(self, vsphere_connection):
        """测试重复启动已运行的VM"""
        content = vsphere_connection.RetrieveContent()
        
        # 创建并启动VM
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        try:
            # 第一次启动
            task = vm.PowerOn()
            self._wait_for_task(task)
            
            # 第二次启动（应该失败或无操作）
            try:
                task = vm.PowerOn()
                self._wait_for_task(task)
                print("⚠️ 重复启动未返回错误")
            except Exception as e:
                print(f"✅ 重复启动正确返回错误: {e}")
                
        finally:
            # 清理
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                task = vm.PowerOff()
                self._wait_for_task(task)
            task = vm.Destroy_Task()
            self._wait_for_task(task)
    
    # ====================
    # 3. 虚拟机停止测试
    # ====================
    
    def test_power_off_vm(self, vsphere_connection):
        """测试关闭VM"""
        content = vsphere_connection.RetrieveContent()
        
        # 创建并启动VM
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        try:
            # 启动VM
            task = vm.PowerOn()
            self._wait_for_task(task)
            
            # 关闭VM
            task = vm.PowerOff()
            self._wait_for_task(task)
            
            # 验证状态
            assert vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff
            print(f"✅ VM关闭成功: {vm.name}")
            
        finally:
            # 清理
            task = vm.Destroy_Task()
            self._wait_for_task(task)
    
    def test_suspend_vm(self, vsphere_connection):
        """测试挂起VM"""
        content = vsphere_connection.RetrieveContent()
        
        # 创建并启动VM
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        try:
            # 启动VM
            task = vm.PowerOn()
            self._wait_for_task(task)
            
            # 挂起VM
            task = vm.Suspend()
            self._wait_for_task(task)
            
            # 验证状态
            assert vm.runtime.powerState == vim.VirtualMachinePowerState.suspended
            print(f"✅ VM挂起成功: {vm.name}")
            
        finally:
            # 清理
            if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOff:
                task = vm.PowerOff()
                self._wait_for_task(task)
            task = vm.Destroy_Task()
            self._wait_for_task(task)
    
    # ====================
    # 4. 虚拟机重启测试
    # ====================
    
    def test_reset_vm(self, vsphere_connection):
        """测试重置VM（强制重启）"""
        content = vsphere_connection.RetrieveContent()
        
        # 创建并启动VM
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        try:
            # 启动VM
            task = vm.PowerOn()
            self._wait_for_task(task)
            
            # 获取启动时间
            boot_time_1 = vm.runtime.bootTime
            time.sleep(2)
            
            # 重置VM
            task = vm.Reset()
            self._wait_for_task(task)
            
            # 等待重启
            time.sleep(5)
            
            # 验证状态和启动时间
            assert vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn
            boot_time_2 = vm.runtime.bootTime
            assert boot_time_2 != boot_time_1, "启动时间应该更新"
            print(f"✅ VM重置成功: {vm.name}")
            
        finally:
            # 清理
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                task = vm.PowerOff()
                self._wait_for_task(task)
            task = vm.Destroy_Task()
            self._wait_for_task(task)
    
    # ====================
    # 5. 虚拟机快照测试
    # ====================
    
    def test_create_snapshot(self, vsphere_connection):
        """测试创建快照"""
        content = vsphere_connection.RetrieveContent()
        
        # 创建VM
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        try:
            # 创建快照
            snapshot_name = f"test-snapshot-{int(time.time())}"
            snapshot_desc = "Test snapshot description"
            
            task = vm.CreateSnapshot(
                name=snapshot_name,
                description=snapshot_desc,
                memory=False,
                quiesce=False
            )
            self._wait_for_task(task)
            
            # 验证快照
            assert vm.snapshot is not None
            assert vm.snapshot.rootSnapshotList[0].name == snapshot_name
            print(f"✅ 快照创建成功: {snapshot_name}")
            
        finally:
            # 清理
            if vm.snapshot:
                task = vm.RemoveAllSnapshots()
                self._wait_for_task(task)
            task = vm.Destroy_Task()
            self._wait_for_task(task)
    
    def test_revert_snapshot(self, vsphere_connection):
        """测试恢复快照"""
        content = vsphere_connection.RetrieveContent()
        
        # 创建VM
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        try:
            # 创建快照
            task = vm.CreateSnapshot(
                name="test-snapshot",
                description="Test",
                memory=False,
                quiesce=False
            )
            self._wait_for_task(task)
            
            # 恢复快照
            snapshot = vm.snapshot.currentSnapshot
            task = snapshot.RevertToSnapshot_Task()
            self._wait_for_task(task)
            
            print(f"✅ 快照恢复成功")
            
        finally:
            # 清理
            if vm.snapshot:
                task = vm.RemoveAllSnapshots()
                self._wait_for_task(task)
            task = vm.Destroy_Task()
            self._wait_for_task(task)
    
    def test_remove_snapshot(self, vsphere_connection):
        """测试删除快照"""
        content = vsphere_connection.RetrieveContent()
        
        # 创建VM
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        try:
            # 创建快照
            task = vm.CreateSnapshot(
                name="test-snapshot",
                description="Test",
                memory=False,
                quiesce=False
            )
            self._wait_for_task(task)
            
            # 删除快照
            snapshot = vm.snapshot.currentSnapshot
            task = snapshot.RemoveSnapshot_Task(removeChildren=False)
            self._wait_for_task(task)
            
            # 验证快照已删除
            assert vm.snapshot is None
            print(f"✅ 快照删除成功")
            
        finally:
            # 清理
            task = vm.Destroy_Task()
            self._wait_for_task(task)
    
    # ====================
    # 6. 虚拟机克隆测试
    # ====================
    
    def test_clone_vm(self, vsphere_connection):
        """测试克隆VM"""
        content = vsphere_connection.RetrieveContent()
        
        # 创建源VM
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        source_vm = self._wait_for_task(task)
        
        try:
            # 克隆规范
            clone_spec = vim.vm.CloneSpec()
            clone_spec.location = vim.vm.RelocateSpec()
            clone_spec.location.datastore = datastore
            clone_spec.location.pool = resource_pool
            clone_spec.powerOn = False
            clone_spec.template = False
            
            # 执行克隆
            clone_name = f"clone-{int(time.time())}"
            task = source_vm.Clone(
                folder=vm_folder,
                name=clone_name,
                spec=clone_spec
            )
            cloned_vm = self._wait_for_task(task)
            
            # 验证克隆
            assert cloned_vm is not None
            assert cloned_vm.name == clone_name
            print(f"✅ VM克隆成功: {clone_name}")
            
            # 清理克隆的VM
            task = cloned_vm.Destroy_Task()
            self._wait_for_task(task)
            
        finally:
            # 清理源VM
            task = source_vm.Destroy_Task()
            self._wait_for_task(task)
    
    # ====================
    # 7. 虚拟机删除测试
    # ====================
    
    def test_destroy_powered_off_vm(self, vsphere_connection):
        """测试删除已关闭的VM"""
        content = vsphere_connection.RetrieveContent()
        
        # 创建VM
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        vm_name = vm.name
        
        # 删除VM
        task = vm.Destroy_Task()
        self._wait_for_task(task)
        
        # 验证VM已删除
        deleted_vm = self._get_vm_by_name(content, vm_name)
        assert deleted_vm is None
        print(f"✅ VM删除成功: {vm_name}")
    
    def test_destroy_powered_on_vm(self, vsphere_connection):
        """测试删除运行中的VM（应该失败）"""
        content = vsphere_connection.RetrieveContent()
        
        # 创建并启动VM
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        
        try:
            # 启动VM
            task = vm.PowerOn()
            self._wait_for_task(task)
            
            # 尝试删除运行中的VM（应该失败）
            with pytest.raises(Exception):
                task = vm.Destroy_Task()
                self._wait_for_task(task)
            
            print("✅ 正确阻止删除运行中的VM")
            
        finally:
            # 清理
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                task = vm.PowerOff()
                self._wait_for_task(task)
            task = vm.Destroy_Task()
            self._wait_for_task(task)
    
    # ====================
    # 8. 完整生命周期测试
    # ====================
    
    def test_full_lifecycle(self, vsphere_connection):
        """测试完整VM生命周期"""
        print("\n=== vSphere VM完整生命周期测试 ===")
        
        content = vsphere_connection.RetrieveContent()
        
        # 1. 创建VM
        datacenter = self._get_obj(content, [vim.Datacenter])
        datastore = self._get_obj(content, [vim.Datastore])
        resource_pool = self._get_obj(content, [vim.ResourcePool])
        vm_folder = datacenter.vmFolder
        
        config = self._create_test_vm_spec(datacenter, datastore, resource_pool)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        vm = self._wait_for_task(task)
        print(f"✅ 1. 创建VM: {vm.name}")
        
        try:
            # 2. 启动VM
            task = vm.PowerOn()
            self._wait_for_task(task)
            assert vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn
            print("✅ 2. 启动VM")
            
            # 3. 创建快照
            task = vm.CreateSnapshot(
                name="lifecycle-snapshot",
                description="Lifecycle test",
                memory=False,
                quiesce=False
            )
            self._wait_for_task(task)
            print("✅ 3. 创建快照")
            
            # 4. 挂起VM
            task = vm.Suspend()
            self._wait_for_task(task)
            assert vm.runtime.powerState == vim.VirtualMachinePowerState.suspended
            print("✅ 4. 挂起VM")
            
            # 5. 恢复VM
            task = vm.PowerOn()
            self._wait_for_task(task)
            print("✅ 5. 恢复VM")
            
            # 6. 关闭VM
            task = vm.PowerOff()
            self._wait_for_task(task)
            assert vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff
            print("✅ 6. 关闭VM")
            
            # 7. 删除快照
            task = vm.RemoveAllSnapshots()
            self._wait_for_task(task)
            print("✅ 7. 删除快照")
            
            # 8. 删除VM
            task = vm.Destroy_Task()
            self._wait_for_task(task)
            print("✅ 8. 删除VM")
            
            print("=== 完整生命周期测试完成 ===\n")
            
        except Exception as e:
            # 确保清理
            print(f"❌ 测试失败: {e}")
            if vm.snapshot:
                task = vm.RemoveAllSnapshots()
                self._wait_for_task(task)
            if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOff:
                task = vm.PowerOff()
                self._wait_for_task(task)
            task = vm.Destroy_Task()
            self._wait_for_task(task)
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


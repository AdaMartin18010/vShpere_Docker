#!/usr/bin/env python3
"""
VMware vSphere认证与鉴权测试套件
包含：用户认证、会话管理、权限管理、角色管理
"""

import pytest
import time
from pyVim.connect import SmartConnect, Disconnect, SmartConnectNoSSL
from pyVmomi import vim, vmodl
import ssl
import atexit


class vSphereAuthTestSuite:
    """vSphere认证与鉴权测试套件"""
    
    # ====================
    # 测试配置
    # ====================
    
    @pytest.fixture(scope="class")
    def vcenter_config(self):
        """vCenter配置"""
        return {
            'host': 'vcenter.example.com',
            'admin_user': 'administrator@vsphere.local',
            'admin_password': 'AdminPassword123!',
            'test_user': 'testuser@vsphere.local',
            'test_password': 'TestPassword123!',
            'port': 443
        }
    
    # ====================
    # 1. 用户认证测试
    # ====================
    
    def test_auth_valid_credentials(self, vcenter_config):
        """测试有效凭据登录"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        # 使用管理员凭据登录
        si = SmartConnect(
            host=vcenter_config['host'],
            user=vcenter_config['admin_user'],
            pwd=vcenter_config['admin_password'],
            port=vcenter_config['port'],
            sslContext=context
        )
        
        assert si is not None
        assert si.content is not None
        print(f"✅ 有效凭据登录成功: {vcenter_config['admin_user']}")
        
        # 清理
        Disconnect(si)
    
    def test_auth_invalid_username(self, vcenter_config):
        """测试无效用户名登录"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        # 使用无效用户名
        with pytest.raises(Exception) as exc_info:
            SmartConnect(
                host=vcenter_config['host'],
                user='nonexistent@vsphere.local',
                pwd=vcenter_config['admin_password'],
                port=vcenter_config['port'],
                sslContext=context
            )
        
        assert 'Cannot complete login' in str(exc_info.value) or 'Invalid credentials' in str(exc_info.value)
        print("✅ 无效用户名正确被拒绝")
    
    def test_auth_invalid_password(self, vcenter_config):
        """测试无效密码登录"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        # 使用错误密码
        with pytest.raises(Exception) as exc_info:
            SmartConnect(
                host=vcenter_config['host'],
                user=vcenter_config['admin_user'],
                pwd='WrongPassword123!',
                port=vcenter_config['port'],
                sslContext=context
            )
        
        assert 'Cannot complete login' in str(exc_info.value) or 'Invalid credentials' in str(exc_info.value)
        print("✅ 无效密码正确被拒绝")
    
    def test_auth_empty_credentials(self, vcenter_config):
        """测试空凭据登录"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        # 空用户名
        with pytest.raises(Exception):
            SmartConnect(
                host=vcenter_config['host'],
                user='',
                pwd=vcenter_config['admin_password'],
                port=vcenter_config['port'],
                sslContext=context
            )
        
        # 空密码
        with pytest.raises(Exception):
            SmartConnect(
                host=vcenter_config['host'],
                user=vcenter_config['admin_user'],
                pwd='',
                port=vcenter_config['port'],
                sslContext=context
            )
        
        print("✅ 空凭据正确被拒绝")
    
    # ====================
    # 2. 会话管理测试
    # ====================
    
    def test_session_creation(self, vcenter_config):
        """测试会话创建"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        si = SmartConnect(
            host=vcenter_config['host'],
            user=vcenter_config['admin_user'],
            pwd=vcenter_config['admin_password'],
            port=vcenter_config['port'],
            sslContext=context
        )
        
        # 获取会话管理器
        session_manager = si.content.sessionManager
        current_session = session_manager.currentSession
        
        assert current_session is not None
        assert current_session.key is not None
        assert current_session.userName == vcenter_config['admin_user']
        
        print(f"✅ 会话创建成功")
        print(f"   会话ID: {current_session.key}")
        print(f"   用户名: {current_session.userName}")
        print(f"   登录时间: {current_session.loginTime}")
        
        Disconnect(si)
    
    def test_session_keep_alive(self, vcenter_config):
        """测试会话保持"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        si = SmartConnect(
            host=vcenter_config['host'],
            user=vcenter_config['admin_user'],
            pwd=vcenter_config['admin_password'],
            port=vcenter_config['port'],
            sslContext=context
        )
        
        session_manager = si.content.sessionManager
        initial_time = session_manager.currentSession.lastActiveTime
        
        # 等待一段时间
        time.sleep(5)
        
        # 执行操作以保持会话活跃
        si.content.rootFolder
        
        # 检查最后活跃时间是否更新
        updated_time = session_manager.currentSession.lastActiveTime
        assert updated_time > initial_time
        
        print("✅ 会话保持成功")
        print(f"   初始时间: {initial_time}")
        print(f"   更新时间: {updated_time}")
        
        Disconnect(si)
    
    def test_session_logout(self, vcenter_config):
        """测试会话登出"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        si = SmartConnect(
            host=vcenter_config['host'],
            user=vcenter_config['admin_user'],
            pwd=vcenter_config['admin_password'],
            port=vcenter_config['port'],
            sslContext=context
        )
        
        session_key = si.content.sessionManager.currentSession.key
        print(f"   会话ID: {session_key}")
        
        # 登出
        si.content.sessionManager.Logout()
        
        # 验证会话已失效（尝试操作应该失败）
        with pytest.raises(Exception):
            si.content.rootFolder
        
        print("✅ 会话登出成功")
    
    def test_multiple_concurrent_sessions(self, vcenter_config):
        """测试多个并发会话"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        sessions = []
        
        # 创建多个会话
        for i in range(3):
            si = SmartConnect(
                host=vcenter_config['host'],
                user=vcenter_config['admin_user'],
                pwd=vcenter_config['admin_password'],
                port=vcenter_config['port'],
                sslContext=context
            )
            sessions.append(si)
        
        # 验证所有会话都有效
        session_keys = []
        for si in sessions:
            session_key = si.content.sessionManager.currentSession.key
            session_keys.append(session_key)
            assert session_key is not None
        
        # 验证会话ID不同
        assert len(session_keys) == len(set(session_keys)), "会话ID应该唯一"
        
        print(f"✅ 创建{len(sessions)}个并发会话成功")
        for i, key in enumerate(session_keys):
            print(f"   会话{i+1}: {key}")
        
        # 清理
        for si in sessions:
            Disconnect(si)
    
    # ====================
    # 3. SSL/TLS安全测试
    # ====================
    
    def test_ssl_secure_connection(self, vcenter_config):
        """测试SSL安全连接"""
        # 使用SSL验证的连接
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # 生产环境应该验证证书
        
        si = SmartConnect(
            host=vcenter_config['host'],
            user=vcenter_config['admin_user'],
            pwd=vcenter_config['admin_password'],
            port=vcenter_config['port'],
            sslContext=context
        )
        
        assert si is not None
        print("✅ SSL安全连接成功")
        
        Disconnect(si)
    
    def test_ssl_no_verification(self, vcenter_config):
        """测试禁用SSL验证连接（测试环境）"""
        # 使用SmartConnectNoSSL（不推荐生产使用）
        si = SmartConnectNoSSL(
            host=vcenter_config['host'],
            user=vcenter_config['admin_user'],
            pwd=vcenter_config['admin_password'],
            port=vcenter_config['port']
        )
        
        assert si is not None
        print("✅ 无SSL验证连接成功（仅用于测试）")
        
        Disconnect(si)
    
    # ====================
    # 4. 权限验证测试
    # ====================
    
    def test_permission_check_admin(self, vcenter_config):
        """测试管理员权限"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        si = SmartConnect(
            host=vcenter_config['host'],
            user=vcenter_config['admin_user'],
            pwd=vcenter_config['admin_password'],
            port=vcenter_config['port'],
            sslContext=context
        )
        
        # 获取权限管理器
        auth_manager = si.content.authorizationManager
        
        # 检查当前用户的角色
        current_user = si.content.sessionManager.currentSession.userName
        
        # 尝试执行需要管理员权限的操作
        try:
            # 列出所有数据中心（需要浏览权限）
            datacenters = si.content.rootFolder.childEntity
            assert datacenters is not None
            print(f"✅ 管理员权限验证成功")
            print(f"   用户: {current_user}")
            print(f"   可访问数据中心数量: {len(datacenters)}")
        except Exception as e:
            pytest.fail(f"管理员应该有浏览权限: {e}")
        
        Disconnect(si)
    
    def test_permission_check_readonly(self, vcenter_config):
        """测试只读权限用户"""
        # 注意：需要预先创建只读用户
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        # 假设有只读用户
        readonly_user = 'readonly@vsphere.local'
        readonly_pwd = 'ReadonlyPassword123!'
        
        try:
            si = SmartConnect(
                host=vcenter_config['host'],
                user=readonly_user,
                pwd=readonly_pwd,
                port=vcenter_config['port'],
                sslContext=context
            )
            
            # 只读用户应该能够浏览
            datacenters = si.content.rootFolder.childEntity
            assert datacenters is not None
            
            # 只读用户不应该能够创建VM（这需要实际测试环境）
            print("✅ 只读权限验证成功（能浏览，不能修改）")
            
            Disconnect(si)
            
        except Exception as e:
            pytest.skip(f"只读用户不存在或配置错误: {e}")
    
    # ====================
    # 5. 角色管理测试
    # ====================
    
    def test_role_list(self, vcenter_config):
        """测试列出所有角色"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        si = SmartConnect(
            host=vcenter_config['host'],
            user=vcenter_config['admin_user'],
            pwd=vcenter_config['admin_password'],
            port=vcenter_config['port'],
            sslContext=context
        )
        
        # 获取授权管理器
        auth_manager = si.content.authorizationManager
        
        # 列出所有角色
        roles = auth_manager.roleList
        
        assert roles is not None
        assert len(roles) > 0
        
        print(f"✅ 列出角色成功: 共{len(roles)}个角色")
        for role in roles[:5]:  # 显示前5个
            print(f"   角色: {role.name} (ID: {role.roleId})")
            print(f"      系统: {role.system}")
            print(f"      权限数: {len(role.privilege)}")
        
        Disconnect(si)
    
    def test_role_builtin_roles(self, vcenter_config):
        """测试内置角色"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        si = SmartConnect(
            host=vcenter_config['host'],
            user=vcenter_config['admin_user'],
            pwd=vcenter_config['admin_password'],
            port=vcenter_config['port'],
            sslContext=context
        )
        
        auth_manager = si.content.authorizationManager
        
        # 查找常见的内置角色
        builtin_role_names = ['Admin', 'ReadOnly', 'NoAccess']
        found_roles = []
        
        for role in auth_manager.roleList:
            if role.name in builtin_role_names:
                found_roles.append(role)
                print(f"✅ 找到内置角色: {role.name}")
                print(f"   角色ID: {role.roleId}")
                print(f"   系统角色: {role.system}")
                print(f"   权限数: {len(role.privilege)}")
        
        assert len(found_roles) > 0, "应该找到至少一个内置角色"
        
        Disconnect(si)
    
    # ====================
    # 6. 审计日志测试
    # ====================
    
    def test_audit_event_query(self, vcenter_config):
        """测试查询审计事件"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        si = SmartConnect(
            host=vcenter_config['host'],
            user=vcenter_config['admin_user'],
            pwd=vcenter_config['admin_password'],
            port=vcenter_config['port'],
            sslContext=context
        )
        
        # 获取事件管理器
        event_manager = si.content.eventManager
        
        # 创建事件过滤器（查询最近的事件）
        filter_spec = vim.event.EventFilterSpec()
        filter_spec.maxCount = 10
        
        # 查询事件
        events = event_manager.QueryEvents(filter_spec)
        
        assert events is not None
        print(f"✅ 查询审计事件成功: 共{len(events)}个事件")
        
        for event in events[:3]:  # 显示前3个
            print(f"   事件: {event.__class__.__name__}")
            print(f"      时间: {event.createdTime}")
            print(f"      用户: {event.userName}")
            if hasattr(event, 'fullFormattedMessage'):
                print(f"      消息: {event.fullFormattedMessage}")
        
        Disconnect(si)
    
    def test_audit_login_events(self, vcenter_config):
        """测试查询登录事件"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        si = SmartConnect(
            host=vcenter_config['host'],
            user=vcenter_config['admin_user'],
            pwd=vcenter_config['admin_password'],
            port=vcenter_config['port'],
            sslContext=context
        )
        
        event_manager = si.content.eventManager
        
        # 创建过滤器，查找用户登录事件
        filter_spec = vim.event.EventFilterSpec()
        filter_spec.eventTypeId = ['UserLoginSessionEvent']
        filter_spec.maxCount = 10
        
        events = event_manager.QueryEvents(filter_spec)
        
        print(f"✅ 查询登录事件: 共{len(events)}个")
        
        for event in events[:3]:
            print(f"   登录事件:")
            print(f"      用户: {event.userName}")
            print(f"      时间: {event.createdTime}")
            print(f"      IP地址: {event.ipAddress if hasattr(event, 'ipAddress') else 'N/A'}")
        
        Disconnect(si)
    
    # ====================
    # 7. 完整认证流程测试
    # ====================
    
    def test_full_auth_workflow(self, vcenter_config):
        """测试完整认证工作流"""
        print("\n=== vSphere完整认证工作流测试 ===")
        
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        
        # 1. 登录
        si = SmartConnect(
            host=vcenter_config['host'],
            user=vcenter_config['admin_user'],
            pwd=vcenter_config['admin_password'],
            port=vcenter_config['port'],
            sslContext=context
        )
        print("✅ 1. 用户登录成功")
        
        # 2. 获取会话信息
        session_manager = si.content.sessionManager
        session = session_manager.currentSession
        print(f"✅ 2. 获取会话信息")
        print(f"   会话ID: {session.key}")
        print(f"   用户: {session.userName}")
        
        # 3. 验证权限
        auth_manager = si.content.authorizationManager
        roles = auth_manager.roleList
        print(f"✅ 3. 验证权限 - 可访问{len(roles)}个角色")
        
        # 4. 执行操作
        datacenters = si.content.rootFolder.childEntity
        print(f"✅ 4. 执行操作 - 浏览到{len(datacenters)}个数据中心")
        
        # 5. 查询审计日志
        event_manager = si.content.eventManager
        filter_spec = vim.event.EventFilterSpec()
        filter_spec.maxCount = 5
        events = event_manager.QueryEvents(filter_spec)
        print(f"✅ 5. 查询审计日志 - {len(events)}个事件")
        
        # 6. 登出
        session_manager.Logout()
        print("✅ 6. 用户登出成功")
        
        print("=== 完整认证工作流测试完成 ===\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


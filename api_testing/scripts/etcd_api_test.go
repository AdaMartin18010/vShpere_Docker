package main

import (
	"context"
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/fatih/color"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/suite"
	clientv3 "go.etcd.io/etcd/client/v3"
)

// EtcdAPITestSuite etcd API测试套件
type EtcdAPITestSuite struct {
	suite.Suite
	client  *clientv3.Client
	ctx     context.Context
	leaseID clientv3.LeaseID
}

// SetupSuite 初始化测试套件
func (s *EtcdAPITestSuite) SetupSuite() {
	s.ctx = context.Background()

	// etcd连接配置
	endpoints := []string{"localhost:2379"}
	if env := os.Getenv("ETCD_ENDPOINTS"); env != "" {
		endpoints = []string{env}
	}

	// 创建etcd客户端
	cli, err := clientv3.New(clientv3.Config{
		Endpoints:   endpoints,
		DialTimeout: 5 * time.Second,
	})
	s.Require().NoError(err, "Failed to create etcd client")
	s.client = cli

	color.Green("\n=== etcd API 测试套件初始化 ===\n")
	fmt.Printf("  - Endpoints: %v\n", endpoints)
}

// TearDownSuite 清理测试套件
func (s *EtcdAPITestSuite) TearDownSuite() {
	if s.client != nil {
		s.client.Close()
	}
	color.Green("\n=== etcd API 测试套件清理完成 ===\n")
}

// Test01_GetStatus 测试1: 获取etcd状态
func (s *EtcdAPITestSuite) Test01_GetStatus() {
	color.Cyan("\n测试1: 获取etcd服务器状态")

	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	resp, err := s.client.Status(ctx, s.client.Endpoints()[0])
	s.Require().NoError(err)

	color.Green("✅ etcd状态获取成功:")
	fmt.Printf("  - Version: %s\n", resp.Version)
	fmt.Printf("  - DB Size: %d bytes\n", resp.DbSize)
	fmt.Printf("  - Leader: %d\n", resp.Leader)
	fmt.Printf("  - Raft Index: %d\n", resp.RaftIndex)
	fmt.Printf("  - Raft Term: %d\n", resp.RaftTerm)

	assert.NotEmpty(s.T(), resp.Version)
}

// Test02_MemberList 测试2: 列出集群成员
func (s *EtcdAPITestSuite) Test02_MemberList() {
	color.Cyan("\n测试2: 列出etcd集群成员")

	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	resp, err := s.client.MemberList(ctx)
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ 集群成员列表获取成功: 共 %d 个成员", len(resp.Members)))

	for i, member := range resp.Members {
		fmt.Printf("  - Member %d:\n", i+1)
		fmt.Printf("    ID: %x\n", member.ID)
		fmt.Printf("    Name: %s\n", member.Name)
		fmt.Printf("    Peer URLs: %v\n", member.PeerURLs)
		fmt.Printf("    Client URLs: %v\n", member.ClientURLs)
	}

	assert.Greater(s.T(), len(resp.Members), 0)
}

// Test03_PutKey 测试3: 存储键值对
func (s *EtcdAPITestSuite) Test03_PutKey() {
	color.Cyan("\n测试3: 存储键值对")

	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	key := "/test/key1"
	value := "test_value_golang"

	resp, err := s.client.Put(ctx, key, value)
	s.Require().NoError(err)

	color.Green("✅ 键值对存储成功:")
	fmt.Printf("  - Key: %s\n", key)
	fmt.Printf("  - Value: %s\n", value)
	fmt.Printf("  - Revision: %d\n", resp.Header.Revision)

	assert.NotNil(s.T(), resp.Header)
}

// Test04_GetKey 测试4: 获取键值对
func (s *EtcdAPITestSuite) Test04_GetKey() {
	color.Cyan("\n测试4: 获取键值对")

	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	key := "/test/key1"

	resp, err := s.client.Get(ctx, key)
	s.Require().NoError(err)

	color.Green("✅ 键值对获取成功:")
	fmt.Printf("  - Key: %s\n", key)
	fmt.Printf("  - Count: %d\n", resp.Count)

	if len(resp.Kvs) > 0 {
		kv := resp.Kvs[0]
		fmt.Printf("  - Value: %s\n", string(kv.Value))
		fmt.Printf("  - Version: %d\n", kv.Version)
		fmt.Printf("  - Create Revision: %d\n", kv.CreateRevision)
		fmt.Printf("  - Mod Revision: %d\n", kv.ModRevision)

		assert.Equal(s.T(), "test_value_golang", string(kv.Value))
	}
}

// Test05_GetKeyWithPrefix 测试5: 按前缀获取键值对
func (s *EtcdAPITestSuite) Test05_GetKeyWithPrefix() {
	color.Cyan("\n测试5: 按前缀获取键值对")

	// 先存储几个测试键
	ctx := context.Background()
	s.client.Put(ctx, "/test/prefix/key1", "value1")
	s.client.Put(ctx, "/test/prefix/key2", "value2")
	s.client.Put(ctx, "/test/prefix/key3", "value3")

	// 按前缀查询
	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	prefix := "/test/prefix/"
	resp, err := s.client.Get(ctx, prefix, clientv3.WithPrefix())
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ 按前缀获取成功: 找到 %d 个键", resp.Count))

	for i, kv := range resp.Kvs {
		if i >= 5 {
			break
		}
		fmt.Printf("  - %s: %s\n", string(kv.Key), string(kv.Value))
	}

	assert.GreaterOrEqual(s.T(), resp.Count, int64(3))
}

// Test06_LeaseGrant 测试6: 创建租约
func (s *EtcdAPITestSuite) Test06_LeaseGrant() {
	color.Cyan("\n测试6: 创建租约")

	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	// 创建60秒的租约
	resp, err := s.client.Grant(ctx, 60)
	s.Require().NoError(err)

	s.leaseID = resp.ID

	color.Green("✅ 租约创建成功:")
	fmt.Printf("  - Lease ID: %x\n", s.leaseID)
	fmt.Printf("  - TTL: %d 秒\n", resp.TTL)

	assert.NotZero(s.T(), s.leaseID)
}

// Test07_PutKeyWithLease 测试7: 存储带租约的键值对
func (s *EtcdAPITestSuite) Test07_PutKeyWithLease() {
	color.Cyan("\n测试7: 存储带租约的键值对")

	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	key := "/test/lease_key"
	value := "value_with_lease"

	resp, err := s.client.Put(ctx, key, value, clientv3.WithLease(s.leaseID))
	s.Require().NoError(err)

	color.Green("✅ 带租约的键值对存储成功:")
	fmt.Printf("  - Key: %s\n", key)
	fmt.Printf("  - Value: %s\n", value)
	fmt.Printf("  - Lease ID: %x\n", s.leaseID)

	assert.NotNil(s.T(), resp.Header)
}

// Test08_LeaseTimeToLive 测试8: 获取租约信息
func (s *EtcdAPITestSuite) Test08_LeaseTimeToLive() {
	color.Cyan("\n测试8: 获取租约信息")

	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	resp, err := s.client.TimeToLive(ctx, s.leaseID)
	s.Require().NoError(err)

	color.Green("✅ 租约信息获取成功:")
	fmt.Printf("  - Lease ID: %x\n", resp.ID)
	fmt.Printf("  - TTL: %d 秒\n", resp.TTL)
	fmt.Printf("  - Granted TTL: %d 秒\n", resp.GrantedTTL)

	assert.Greater(s.T(), resp.TTL, int64(0))
}

// Test09_LeaseKeepAlive 测试9: 续约
func (s *EtcdAPITestSuite) Test09_LeaseKeepAlive() {
	color.Cyan("\n测试9: 租约续约")

	ctx, cancel := context.WithTimeout(s.ctx, 10*time.Second)
	defer cancel()

	// 开始续约
	ch, err := s.client.KeepAlive(ctx, s.leaseID)
	s.Require().NoError(err)

	// 等待第一个续约响应
	resp := <-ch
	s.Require().NotNil(resp)

	color.Green("✅ 租约续约成功:")
	fmt.Printf("  - Lease ID: %x\n", resp.ID)
	fmt.Printf("  - TTL: %d 秒\n", resp.TTL)

	assert.Equal(s.T(), s.leaseID, resp.ID)
}

// Test10_WatchKey 测试10: 监听键变化
func (s *EtcdAPITestSuite) Test10_WatchKey() {
	color.Cyan("\n测试10: 监听键变化")

	ctx, cancel := context.WithTimeout(s.ctx, 10*time.Second)
	defer cancel()

	key := "/test/watch_key"

	// 启动Watch
	watchChan := s.client.Watch(ctx, key)

	// 在另一个goroutine中修改键
	go func() {
		time.Sleep(1 * time.Second)
		s.client.Put(context.Background(), key, "watch_value_1")
		time.Sleep(1 * time.Second)
		s.client.Put(context.Background(), key, "watch_value_2")
	}()

	// 接收Watch事件
	eventCount := 0
	for watchResp := range watchChan {
		for _, event := range watchResp.Events {
			eventCount++
			color.Green(fmt.Sprintf("✅ 收到Watch事件 #%d:", eventCount))
			fmt.Printf("  - Type: %s\n", event.Type)
			fmt.Printf("  - Key: %s\n", string(event.Kv.Key))
			fmt.Printf("  - Value: %s\n", string(event.Kv.Value))

			if eventCount >= 2 {
				cancel()
				goto Done
			}
		}
	}
Done:

	assert.GreaterOrEqual(s.T(), eventCount, 1)
}

// Test11_Transaction 测试11: 事务操作
func (s *EtcdAPITestSuite) Test11_Transaction() {
	color.Cyan("\n测试11: 事务操作")

	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	key := "/test/txn_key"

	// 先设置初始值
	s.client.Put(ctx, key, "initial_value")

	// 执行事务: 如果值为initial_value,则更新为new_value
	txn := s.client.Txn(ctx)
	resp, err := txn.If(
		clientv3.Compare(clientv3.Value(key), "=", "initial_value"),
	).Then(
		clientv3.OpPut(key, "new_value"),
	).Else(
		clientv3.OpGet(key),
	).Commit()
	s.Require().NoError(err)

	color.Green("✅ 事务执行成功:")
	fmt.Printf("  - Succeeded: %v\n", resp.Succeeded)
	fmt.Printf("  - Revision: %d\n", resp.Header.Revision)

	// 验证值已更新
	getResp, _ := s.client.Get(ctx, key)
	if len(getResp.Kvs) > 0 {
		fmt.Printf("  - New Value: %s\n", string(getResp.Kvs[0].Value))
		assert.Equal(s.T(), "new_value", string(getResp.Kvs[0].Value))
	}

	assert.True(s.T(), resp.Succeeded)
}

// Test12_DeleteKey 测试12: 删除键值对
func (s *EtcdAPITestSuite) Test12_DeleteKey() {
	color.Cyan("\n测试12: 删除键值对")

	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	key := "/test/key1"

	resp, err := s.client.Delete(ctx, key)
	s.Require().NoError(err)

	color.Green("✅ 键值对删除成功:")
	fmt.Printf("  - Key: %s\n", key)
	fmt.Printf("  - Deleted: %d\n", resp.Deleted)

	assert.GreaterOrEqual(s.T(), resp.Deleted, int64(1))
}

// Test13_DeleteKeyWithPrefix 测试13: 按前缀删除键值对
func (s *EtcdAPITestSuite) Test13_DeleteKeyWithPrefix() {
	color.Cyan("\n测试13: 按前缀删除键值对")

	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	prefix := "/test/prefix/"

	resp, err := s.client.Delete(ctx, prefix, clientv3.WithPrefix())
	s.Require().NoError(err)

	color.Green("✅ 按前缀删除成功:")
	fmt.Printf("  - Prefix: %s\n", prefix)
	fmt.Printf("  - Deleted: %d\n", resp.Deleted)

	assert.GreaterOrEqual(s.T(), resp.Deleted, int64(0))
}

// Test14_LeaseRevoke 测试14: 撤销租约
func (s *EtcdAPITestSuite) Test14_LeaseRevoke() {
	color.Cyan("\n测试14: 撤销租约")

	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	resp, err := s.client.Revoke(ctx, s.leaseID)
	s.Require().NoError(err)

	color.Green("✅ 租约撤销成功:")
	fmt.Printf("  - Lease ID: %x\n", s.leaseID)
	fmt.Printf("  - Revision: %d\n", resp.Header.Revision)

	assert.NotNil(s.T(), resp.Header)
}

// TestEtcdAPI 运行etcd API测试套件
func TestEtcdAPI(t *testing.T) {
	suite.Run(t, new(EtcdAPITestSuite))
}

// Main函数 - 用于直接运行
func main() {
	os.Exit(0)
}

#!/usr/bin/env python3
"""
2025技术暗流 ROI计算器
"""

import argparse
from dataclasses import dataclass
from typing import List

@dataclass
class Undercurrent:
    """技术暗流"""
    id: int
    name: str
    monthly_cost: float
    annual_benefit: float
    risk_value: float
    window_months: int
    
    @property
    def roi(self) -> float:
        """ROI计算"""
        annual_cost = self.monthly_cost * 12
        if annual_cost == 0:
            return float('inf') if self.annual_benefit > 0 else 0
        return (self.annual_benefit - annual_cost) / annual_cost * 100
    
    @property
    def priority_score(self) -> float:
        """优先级得分"""
        if self.roi == float('inf'):
            return 1000000 / (self.risk_value + 1)
        return self.roi / (self.risk_value + 1)

# ============ 8条暗流数据 ============
UNDERCURRENTS = {
    'fused': Undercurrent(1, '融合运行时', 18, 3600, 15, 12),
    'multi': Undercurrent(2, '多运行时混战', 0, 5000, 50, 18),
    'rootless': Undercurrent(3, 'Rootless+无Cap', 0, 600, 2, 6),
    'nitrogen': Undercurrent(4, '液氮超导', 3000, 360, 2100, 36),
    'ai': Undercurrent(5, 'AI调度容器', 0, 8000, 2, 9),  # 故障率降低带来的间接收益
    'wasm': Undercurrent(6, 'WASM沙盒', 0, 5000, 12, 12),
    'sign': Undercurrent(7, '跨云签名', 0, 600, 5, 6),
    'fpga': Undercurrent(8, '边缘FPGA', 99, 1188, 60, 18),
}

def calculate_portfolio_roi(actions: List[str]) -> dict:
    """计算组合ROI"""
    selected = [UNDERCURRENTS[a] for a in actions if a in UNDERCURRENTS]
    
    if not selected:
        return {
            'total_monthly_cost': 0,
            'total_annual_benefit': 0,
            'total_annual_cost': 0,
            'total_roi': 0,
            'items': []
        }
    
    total_monthly_cost = sum(u.monthly_cost for u in selected)
    total_annual_benefit = sum(u.annual_benefit for u in selected)
    total_annual_cost = total_monthly_cost * 12
    
    if total_annual_cost == 0:
        total_roi = float('inf') if total_annual_benefit > 0 else 0
    else:
        total_roi = (total_annual_benefit - total_annual_cost) / total_annual_cost * 100
    
    return {
        'total_monthly_cost': total_monthly_cost,
        'total_annual_benefit': total_annual_benefit,
        'total_annual_cost': total_annual_cost,
        'total_roi': total_roi,
        'items': selected
    }

def print_single_roi(key: str):
    """打印单个暗流ROI"""
    u = UNDERCURRENTS[key]
    print(f"\n{'='*50}")
    print(f"{u.id}. {u.name}")
    print(f"{'='*50}")
    print(f"月成本: ¥{u.monthly_cost}")
    print(f"年收益: ¥{u.annual_benefit}")
    print(f"ROI: {u.roi if u.roi != float('inf') else '∞'}%")
    print(f"风险值: ¥{u.risk_value}")
    print(f"优先级得分: {u.priority_score:.2f}")
    print(f"窗口期: {u.window_months}月")

def print_portfolio_roi(result: dict):
    """打印组合ROI"""
    print(f"\n{'='*50}")
    print("ROI计算结果")
    print(f"{'='*50}")
    print(f"\n总投入: ¥{result['total_monthly_cost']}/月")
    print(f"总收益: ¥{result['total_annual_benefit']}/年")
    print(f"年成本: ¥{result['total_annual_cost']}")
    
    if result['total_roi'] == float('inf'):
        print(f"ROI: ∞%")
    else:
        print(f"ROI: {result['total_roi']:.0f}%")
    
    print(f"\n明细:")
    for u in result['items']:
        symbol = "∞" if u.roi == float('inf') else f"{u.roi:.0f}%"
        print(f"  {u.id}. {u.name}: ¥{u.monthly_cost}/月 → ¥{u.annual_benefit}/年 (ROI: {symbol})")
    
    print(f"{'='*50}\n")

def print_all_sorted():
    """打印所有暗流，按优先级排序"""
    sorted_items = sorted(UNDERCURRENTS.values(), key=lambda x: x.priority_score, reverse=True)
    
    print(f"\n{'='*60}")
    print("8条技术暗流 - 按优先级排序")
    print(f"{'='*60}")
    print(f"{'排名':<4} {'名称':<20} {'月成本':<8} {'年收益':<10} {'ROI':<10} {'风险':<8} {'窗口':<6}")
    print(f"{'-'*60}")
    
    for i, u in enumerate(sorted_items, 1):
        roi_str = "∞" if u.roi == float('inf') else f"{u.roi:.0f}%"
        print(f"{i:<4} {u.name:<20} ¥{u.monthly_cost:<7} ¥{u.annual_benefit:<9} {roi_str:<10} ¥{u.risk_value:<7} {u.window_months}月")
    
    print(f"{'='*60}\n")

def recommend_portfolio():
    """推荐组合"""
    print(f"\n{'='*50}")
    print("推荐组合")
    print(f"{'='*50}\n")
    
    print("🥇 保守组合 (低风险):")
    conservative = calculate_portfolio_roi(['sign', 'rootless', 'ai'])
    print_portfolio_roi(conservative)
    
    print("\n🥈 平衡组合 (中风险):")
    balanced = calculate_portfolio_roi(['sign', 'rootless', 'ai', 'fpga'])
    print_portfolio_roi(balanced)
    
    print("\n🥉 激进组合 (高风险):")
    aggressive = calculate_portfolio_roi(['sign', 'rootless', 'ai', 'fpga', 'wasm', 'multi'])
    print_portfolio_roi(aggressive)

def main():
    parser = argparse.ArgumentParser(
        description='2025技术暗流 ROI计算器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 计算保守组合
  %(prog)s --actions sign,rootless,ai
  
  # 计算单个暗流
  %(prog)s --single sign
  
  # 显示所有暗流
  %(prog)s --list
  
  # 显示推荐组合
  %(prog)s --recommend

可用的暗流代码:
  fused     - 融合运行时
  multi     - 多运行时混战
  rootless  - Rootless+无Cap
  nitrogen  - 液氮超导
  ai        - AI调度容器
  wasm      - WASM沙盒
  sign      - 跨云签名
  fpga      - 边缘FPGA
        """
    )
    
    parser.add_argument('--actions', help='暗流代码,用逗号分隔 (如: sign,rootless,ai)')
    parser.add_argument('--single', help='显示单个暗流ROI')
    parser.add_argument('--list', action='store_true', help='列出所有暗流')
    parser.add_argument('--recommend', action='store_true', help='显示推荐组合')
    
    args = parser.parse_args()
    
    # 横幅
    print("\n" + "="*50)
    print("2025技术暗流 ROI计算器")
    print("="*50)
    
    if args.list:
        print_all_sorted()
        return
    
    if args.recommend:
        recommend_portfolio()
        return
    
    if args.single:
        if args.single not in UNDERCURRENTS:
            print(f"错误: 未知暗流代码 '{args.single}'")
            return
        print_single_roi(args.single)
        return
    
    if args.actions:
        actions = [a.strip() for a in args.actions.split(',')]
        result = calculate_portfolio_roi(actions)
        print_portfolio_roi(result)
        return
    
    # 默认: 显示推荐组合
    recommend_portfolio()

if __name__ == '__main__':
    main()


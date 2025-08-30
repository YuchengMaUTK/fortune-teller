#!/usr/bin/env python3
"""
Test the MCP servers functionality
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fortune_teller.mcp.tarot_server import TarotMCPServer
from fortune_teller.mcp.divination_server import DivinationMCPServer
from fortune_teller.ui.colors import Colors


async def test_tarot_server():
    """Test the Tarot MCP server"""
    print(f"{Colors.YELLOW}🃏 测试塔罗牌 MCP 服务器{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*40}{Colors.ENDC}")
    
    try:
        server = TarotMCPServer()
        
        # Test card drawing
        print("📤 测试抽卡功能...")
        cards = await server.draw_random_cards(total_cards=78, draw_count=3, spread_type="three_card")
        print(f"✅ 抽取的牌: {cards}")
        
        # Test orientation
        print("📤 测试牌面方向...")
        orientations = []
        for _ in range(5):
            orientation = await server.get_orientation()
            orientations.append(orientation)
        print(f"✅ 牌面方向测试: {orientations}")
        
        # Test entropy quality
        print("📤 测试熵源质量...")
        quality = await server.get_entropy_quality()
        print(f"✅ 熵源质量: {quality['quality_score']}")
        print(f"   随机数源: {quality['entropy_source']}")
        print(f"   洗牌算法: {quality['shuffle_algorithm']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 塔罗服务器测试失败: {e}")
        return False


async def test_divination_server():
    """Test the Divination MCP server"""
    print(f"\n{Colors.YELLOW}🎲 测试通用占卜随机化 MCP 服务器{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*40}{Colors.ENDC}")
    
    try:
        server = DivinationMCPServer()
        
        # Test quantum random int
        print("📤 测试量子随机整数...")
        random_ints = []
        for _ in range(5):
            rand_int = await server.quantum_random_int(1, 100)
            random_ints.append(rand_int)
        print(f"✅ 随机整数: {random_ints}")
        
        # Test entropy shuffle
        print("📤 测试熵洗牌...")
        test_list = list(range(1, 11))
        shuffled = await server.entropy_shuffle(test_list)
        print(f"✅ 原始列表: {test_list}")
        print(f"   洗牌结果: {shuffled}")
        
        # Test multi-source random
        print("📤 测试多源随机数...")
        random_floats = await server.multi_source_random(5)
        print(f"✅ 多源随机数: {[f'{x:.4f}' for x in random_floats]}")
        
        # Test randomness quality
        print("📤 测试随机性质量...")
        quality = await server.get_randomness_quality()
        print(f"✅ 整体质量: {quality['overall_quality']:.3f}")
        print(f"   最佳熵源: {quality['best_source']}")
        print(f"   可用熵源: {list(quality['entropy_sources'].keys())}")
        
        # Test statistical tests
        print("📤 运行统计测试...")
        test_results = await server.run_statistical_tests(sample_size=100)
        print(f"✅ 统计测试结果:")
        print(f"   样本大小: {test_results['sample_size']}")
        print(f"   平均值: {test_results['mean']:.4f}")
        print(f"   方差: {test_results['variance']:.4f}")
        print(f"   Chi-square 测试: {'通过' if test_results['chi_square_test']['passed'] else '失败'}")
        print(f"   KS 测试: {'通过' if test_results['kolmogorov_smirnov_test']['passed'] else '失败'}")
        print(f"   游程测试: {'通过' if test_results['runs_test']['passed'] else '失败'}")
        print(f"   整体通过: {'✅ 是' if test_results['overall_passed'] else '❌ 否'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 占卜服务器测试失败: {e}")
        return False


async def main():
    """Main test function"""
    print(f"{Colors.BOLD}🧪 MCP 服务器功能测试{Colors.ENDC}\n")
    
    results = []
    
    # Test Tarot server
    tarot_result = await test_tarot_server()
    results.append(("塔罗牌服务器", tarot_result))
    
    # Test Divination server
    divination_result = await test_divination_server()
    results.append(("占卜随机化服务器", divination_result))
    
    # Summary
    print(f"\n{Colors.BOLD}📊 测试结果汇总{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*40}{Colors.ENDC}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✅ 通过{Colors.ENDC}" if result else f"{Colors.RED}❌ 失败{Colors.ENDC}"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n结果: {passed}/{total} 个服务器测试通过")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 所有 MCP 服务器测试通过！{Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}⚠️ 部分测试失败，请检查上述错误信息{Colors.ENDC}")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}测试被用户中断{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}测试运行器崩溃: {e}{Colors.ENDC}")
        sys.exit(1)
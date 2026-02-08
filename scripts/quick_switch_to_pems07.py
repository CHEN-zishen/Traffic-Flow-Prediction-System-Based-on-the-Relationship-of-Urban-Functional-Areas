"""快速切换到PeMS07数据集"""
from switch_dataset import switch_dataset

print("正在切换到PeMS07数据集（883个传感器）...")
success = switch_dataset('PeMS07')

if success:
    print("\n" + "=" * 70)
    print("切换成功！")
    print("=" * 70)
    print("\n下一步操作:")
    print("1. 重启API服务:")
    print("   在API终端按 Ctrl+C，然后运行: python run_api.py")
    print("\n2. 刷新浏览器查看新数据:")
    print("   http://127.0.0.1:5000")
    print("\n3. 点击'实时预测'测试新数据集")
    print("=" * 70)
else:
    print("\n切换失败，请检查数据文件是否存在")


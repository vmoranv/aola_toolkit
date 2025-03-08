import re
import os
import itertools
from colorama import Fore, Style, init

# 初始化colorama
init()

def display_template_preview(template_content, placeholders):
    """彩色显示模板预览"""
    preview = template_content
    colors = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.YELLOW, Fore.MAGENTA, Fore.CYAN]
    
    # 为每个占位符分配颜色
    for i, ph in enumerate(placeholders):
        color = colors[i % len(colors)]
        # 替换所有匹配的占位符为彩色文本
        preview = preview.replace(f"$num{ph}$", f"{color}$num{ph}${Style.RESET_ALL}")
    
    print("\n模板预览:")
    print(preview)
    print("\n识别到的爆破点:")
    
    # 显示每个爆破点的颜色标识
    for i, ph in enumerate(placeholders):
        color = colors[i % len(colors)]
        print(f"{color}$num{ph}${Style.RESET_ALL}")

def process_template(template_file, output_file, ranges):
    # 读取模板文件
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 查找所有的 $num$ 标记
    num_placeholders = re.findall(r'\$num(\d*)\$', template_content)
    
    # 如果没有找到任何标记，直接返回
    if not num_placeholders:
        print("没有找到任何 $numX$ 标记喵~")
        return
    
    # 为每个不同的标记分配一个唯一ID
    unique_placeholders = sorted(set(num_placeholders), key=lambda x: x if x else "0")
    
    # 显示彩色预览
    display_template_preview(template_content, unique_placeholders)
    
    # 检查是否为所有占位符设置了范围
    for ph in unique_placeholders:
        if ph not in ranges:
            start = int(input(f"请为 $num{ph}$ 设置起始数字: ").strip() or "1")
            end = int(input(f"请为 $num{ph}$ 设置结束数字: ").strip() or "10")
            ranges[ph] = (start, end)
    
    # 创建数字范围列表
    range_lists = [range(ranges[ph][0], ranges[ph][1] + 1) for ph in unique_placeholders]
    
    # 生成所有可能的组合
    combinations = list(itertools.product(*range_lists))
    
    # 创建输出目录（如果不存在）
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 打开输出文件
    with open(output_file, 'w', encoding='utf-8') as out_f:
        # 对每个组合生成一个结果
        for combo in combinations:
            # 创建替换映射
            replace_map = {f"$num{ph}$": str(combo[i]) for i, ph in enumerate(unique_placeholders)}
            
            # 应用替换
            result = template_content
            for placeholder, value in replace_map.items():
                result = result.replace(placeholder, value)
            
            # 写入结果
            out_f.write(result)
            out_f.write("\n")  # 每个组合之间添加换行
    
    print(f"\n处理完成喵~共生成了 {len(combinations)} 个组合~【扭动身体】")
    print(f"结果已保存到: {output_file}")

if __name__ == "__main__":
    print("======= 模板文件数字遍历工具 =======")
    print("(支持多点爆破和自定义范围)")
    
    template_file = input("请输入模板文件路径: ").strip()
    
    if not os.path.exists(template_file):
        print(f"错误：模板文件 '{template_file}' 不存在喵~")
    else:
        output_file = input("请输入输出文件路径 (默认: output.txt): ").strip() or "output.txt"
        
        # 存储每个占位符的范围
        placeholder_ranges = {}
        
        process_template(template_file, output_file, placeholder_ranges)

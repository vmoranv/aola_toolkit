import re
import os
import requests
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, unescape

def download_xml(url):
    """从URL下载XML文件"""
    try:
        print("正在下载XML文件...")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # 创建临时文件
            temp_file = "sceneitem.xml"
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            print("下载完成!")
            return temp_file
        else:
            print(f"下载失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"下载文件时出错: {str(e)}")
        return None

def clean_xml_content(xml_file):
    """预处理XML内容，处理特殊字符"""
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换特殊字符
        content = content.replace('&', '&amp;')
        
        # 创建临时文件
        temp_file = xml_file + '.temp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return temp_file
    except Exception as e:
        print(f"预处理XML文件时出错: {str(e)}")
        return None

def extract_activity_info(xml_file, output_dir):
    """提取XML中的活动信息并保存为.mya文件"""
    try:
        # 预处理XML文件
        temp_file = clean_xml_content(xml_file)
        if not temp_file:
            return False
            
        try:
            # 解析XML文件
            tree = ET.parse(temp_file)
            root = tree.getroot()
            
            # 遍历所有item元素
            for item in root.findall('.//item'):
                try:
                    # 获取tips属性作为文件名
                    tips = item.get('tips')
                    if not tips:
                        continue
                        
                    # 处理文件名中的特殊字符
                    safe_tips = tips.replace('/', '_').replace('\\', '_').replace(':', '_')
                    safe_tips = safe_tips.replace('*', '_').replace('?', '_').replace('"', '_')
                    safe_tips = safe_tips.replace('<', '_').replace('>', '_').replace('|', '_')
                    
                    # 查找res标签
                    res = item.find('.//res')
                    if res is None:
                        continue
                        
                    # 获取file和cls属性
                    file_path = res.get('file', '')
                    cls_path = res.get('cls', '')
                    
                    if not file_path or not cls_path:
                        continue
                    
                    # 创建输出文件名
                    output_file = os.path.join(output_dir, f"{safe_tips}.mya")
                    
                    # 写入文件
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f"#activ='{file_path}','{cls_path}'")
                        
                    print(f"已保存: {safe_tips}.mya")
                    
                except Exception as e:
                    print(f"处理item时出错: {str(e)}")
                    continue
                    
            print("\n处理完成!")
            
        finally:
            # 删除临时文件
            try:
                os.remove(temp_file)
            except:
                pass
            
    except Exception as e:
        print(f"处理XML文件时出错: {str(e)}")
        return False
        
    return True

def main():
    print("活动信息提取工具")
    print("=" * 50)
    
    # XML文件URL
    xml_url = "https://aola.100bt.com/play/sceneitem.xml"
    
    # 下载XML文件
    xml_file = download_xml(xml_url)
    if not xml_file:
        return
    
    try:
        # 创建输出目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "existing")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 提取信息
        if extract_activity_info(xml_file, output_dir):
            print(f"\n文件已保存到: {output_dir}")
        else:
            print("\n处理失败！")
            
    finally:
        # 清理下载的XML文件
        try:
            os.remove(xml_file)
        except:
            pass

if __name__ == "__main__":
    main() 
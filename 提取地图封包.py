import xml.etree.ElementTree as ET
import os
import re
import requests

def extract_scene_info(xml_url, save_dir):
    """从XML URL提取场景信息并生成.mya文件"""
    try:
        # 下载XML内容
        print("\n正在下载XML内容...")
        response = requests.get(xml_url)
        response.raise_for_status() # 如果请求失败会抛出异常
        xml_content = response.text
        
        # 解析XML
        print("\n正在解析XML内容...")
        root = ET.fromstring(xml_content)
        
        # 查找所有包含nm属性的r标签
        scene_elements = root.findall(".//r[@nm]")
        total_count = len(scene_elements)
        
        if total_count == 0:
            print("未找到场景信息")
            return
        
        print(f"\n找到 {total_count} 个场景")
        
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        
        # 处理每个场景
        print("\n正在生成文件...")
        success_count = 0
        
        for elem in scene_elements:
            try:
                nm = elem.get('nm', '')
                desc = elem.get('desc', '')
                
                # 如果没有desc，使用nm作为文件名
                filename = desc if desc else nm
                # 替换文件名中的非法字符
                filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                
                # 构建文件内容和路径
                content = f"#scene={nm}"
                file_path = os.path.join(save_dir, f"{filename}.mya")
                
                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                success_count += 1
                
            except Exception as e:
                print(f"处理场景 {nm} 时出错: {str(e)}")
        
        print(f"\n处理完成!")
        print(f"总场景数: {total_count}")
        print(f"成功生成: {success_count}")
        print(f"保存位置: {save_dir}")
        
    except ET.ParseError as e:
        print(f"XML解析错误: {e}")
    except Exception as e:
        print(f"处理过程出错: {e}")

def main():
    try:
        # XML文件URL
        xml_url = "https://aola.100bt.com/play/config.xml"
        save_dir = input("请输入保存文件夹路径: ").strip()
        
        # 执行提取
        extract_scene_info(xml_url, save_dir)
        
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")

if __name__ == "__main__":
    main()

import requests
import xml.etree.ElementTree as ET
import subprocess
import os
from tqdm import tqdm
import re

def get_version():
    """从start.xml获取版本号"""
    try:
        print("\n正在获取版本信息...")
        url = "http://aola.100bt.com/play/start~1.xml"
        response = requests.get(url)
        response.raise_for_status()
        
        # 解析XML
        root = ET.fromstring(response.content)
        version = root.find('.//v').text
        
        print(f"获取到版本号: {version}")
        return version
        
    except Exception as e:
        print(f"获取版本号失败: {e}")
        return None

def download_swf(version, save_path):
    """下载版本SWF文件"""
    try:
        print("\n开始下载版本文件...")
        url = f"http://aola.100bt.com/play/versiondata~{version}.swf"
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        
        # 下载文件并显示进度条
        with open(save_path, 'wb') as f, tqdm(
            desc="下载进度",
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                pbar.update(size)
                
        print(f"文件已保存到: {save_path}")
        return True
        
    except Exception as e:
        print(f"下载失败: {e}")
        return False

def get_release_date(file_path):
    """从XML文件中获取发布日期"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 使用正则表达式查找releaseDate
            match = re.search(r'releaseDate="([^"]+)"', content)
            if match:
                return match.group(1).replace('-', '')
    except Exception as e:
        print(f"获取发布日期失败: {e}")
    return None

def extract_binary(ffdec_jar, swf_path, output_dir):
    """使用FFDec解包SWF文件"""
    try:
        print("\n开始解包SWF文件...")
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 验证FFDec路径
        if not os.path.exists(ffdec_jar):
            print(f"错误: FFDec.jar不存在: {ffdec_jar}")
            return False
            
        # 构建命令
        cmd = [
            "java",
            "-jar",
            ffdec_jar,
            "-export",
            "binaryData",
            output_dir,
            swf_path,
            "-format",
            "xml"  # 导出为XML格式
        ]
        
        # 执行命令
        print("正在执行FFDec命令...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"解包完成! 文件保存在: {output_dir}")
            
            # 重命名解包的文件
            for root, _, files in os.walk(output_dir):
                for file in files:
                    if not file.endswith('.xml'):
                        old_path = os.path.join(root, file)
                        # 先添加.xml后缀以便读取内容
                        temp_path = old_path + '.xml'
                        os.rename(old_path, temp_path)
                        
                        # 获取发布日期
                        release_date = get_release_date(temp_path)
                        if release_date:
                            # 使用发布日期重命名文件
                            new_path = os.path.join(root, f"{release_date}.xml")
                            # 如果文件已存在，添加序号
                            counter = 1
                            while os.path.exists(new_path):
                                new_path = os.path.join(root, f"{release_date}_{counter}.xml")
                                counter += 1
                            os.rename(temp_path, new_path)
                            print(f"已重命名: {file} -> {os.path.basename(new_path)}")
                        else:
                            # 如果没有找到日期，保留.xml后缀
                            print(f"已重命名: {file} -> {file}.xml")
            
            # 自动删除SWF文件
            try:
                os.remove(swf_path)
                print("\nSWF文件已自动删除")
            except Exception as e:
                print(f"\n删除SWF文件失败: {e}")
                
            return True
        else:
            print(f"解包失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"解包过程出错: {e}")
        return False

def main():
    try:
        # 获取FFDec.jar路径
        ffdec_jar = input("请输入ffdec.jar路径: ").strip()
        
        # 验证FFDec.jar路径
        if not os.path.exists(ffdec_jar):
            print("错误: ffdec.jar不存在!")
            return
            
        # 获取版本号
        version = get_version()
        if not version:
            return
        
        # 设置保存路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        swf_path = os.path.join(current_dir, f"versiondata_{version}.swf")
        output_dir = os.path.join(current_dir, f"binary_{version}")
        
        # 下载SWF
        if not download_swf(version, swf_path):
            return
        
        # 解包SWF
        extract_binary(ffdec_jar, swf_path, output_dir)
        
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"\n发生错误: {e}")

if __name__ == "__main__":
    main()

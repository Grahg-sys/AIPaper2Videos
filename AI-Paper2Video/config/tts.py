"""
文本转语音脚本
将一句话转换为语音并保存为 WAV 文件
"""

import os
import sys
import asyncio
import edge_tts


async def text_to_speech(text: str, output_file: str = "output.wav", voice: str = "zh-CN-XiaoxiaoNeural"):
    """
    将文本转换为语音并保存为 WAV 文件
    
    Args:
        text: 要转换的文本
        output_file: 输出文件名（默认为 output.wav）
        voice: 语音模型（默认为中文女声）
    
    Returns:
        输出文件的完整路径
    """
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(current_dir, output_file)
        
        # 使用 edge-tts 生成语音
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        
        print(f"✓ 语音生成成功: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"✗ 语音生成失败: {e}")
        return None


async def list_voices():
    """列出所有可用的语音"""
    voices = await edge_tts.list_voices()
    print("\n可用的中文语音:")
    print("-" * 60)
    for voice in voices:
        if voice["Locale"].startswith("zh"):
            print(f"名称: {voice['ShortName']}")
            print(f"  描述: {voice['FriendlyName']}")
            print(f"  性别: {voice['Gender']}")
            print()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        script_name = os.path.basename(sys.argv[0])
        print("使用方法:")
        print(f"  python {script_name} <文本内容> [输出文件名] [语音模型] [重复次数]")
        print("\n示例:")
        print(f'  python {script_name} "你好，这是一段测试文本"')
        print(f'  python {script_name} "你好，这是一段测试文本" output.wav')
        print(f'  python {script_name} "测试" test.wav zh-CN-YunxiNeural 3')
        print(f'  python {script_name} "你好" output.wav zh-CN-XiaoxiaoNeural 5  # 重复5次')
        print("\n查看可用语音:")
        print(f"  python {script_name} --list-voices")
        print("\n注意:")
        print("  - 如果当前在 config 目录下，直接运行: python tts.py")
        print("  - 如果当前在项目根目录，运行: python config/tts.py")
        print("  - 重复次数默认为1，可以设置为2、3、5等数字来延长音频")
        return
    
    # 列出可用语音
    if sys.argv[1] == "--list-voices":
        asyncio.run(list_voices())
        return
    
    # 获取参数
    text = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].isdigit() else "output.wav"
    
    # 判断参数位置（因为输出文件名是可选的）
    voice_idx = 2 if output_file != "output.wav" else 1
    repeat_idx = voice_idx + 1
    
    voice = sys.argv[voice_idx] if len(sys.argv) > voice_idx and not sys.argv[voice_idx].isdigit() else "zh-CN-XiaoxiaoNeural"
    
    # 检查重复次数参数
    repeat_times = 1
    if len(sys.argv) > repeat_idx:
        try:
            repeat_times = int(sys.argv[repeat_idx])
        except (ValueError, IndexError):
            pass
    
    # 如果第二个参数是数字，说明没有指定输出文件名
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        repeat_times = int(sys.argv[2])
        output_file = "output.wav"
        voice = "zh-CN-XiaoxiaoNeural"
    elif len(sys.argv) > 3 and sys.argv[3].isdigit():
        repeat_times = int(sys.argv[3])
    elif len(sys.argv) > 4 and sys.argv[4].isdigit():
        repeat_times = int(sys.argv[4])
    
    # 重复文本
    if repeat_times > 1:
        text = " ".join([text] * repeat_times)
        print(f"文本将重复 {repeat_times} 次，生成更长的音频...")
    
    # 确保输出文件是 .wav 格式
    if not output_file.endswith('.wav'):
        output_file += '.wav'
    
    # 执行转换
    asyncio.run(text_to_speech(text, output_file, voice))


if __name__ == "__main__":
    main()


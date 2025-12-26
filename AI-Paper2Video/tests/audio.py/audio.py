import pyttsx3

# 初始化语音引擎
engine = pyttsx3.init()
# 设置要合成的文本
text = "然后将音频添加到视频中，所以理论上支持 ffmpeg 支持的所有音频格式"
# 保存为WAV文件
engine.save_to_file(text, "audio_output.wav")
# 执行合成并保存
engine.runAndWait()
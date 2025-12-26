# VideoMerging 使用示例

在项目根目录下运行（`paper` 环境），脚本路径是 `src/core/VideoMerging`：

- 添加字幕（默认字号 192，可在末尾自定义）  
  `python video+cap.py C:/Users/23154/Desktop/AI硬件项目/AI文献视觉/AI-Paper2Video/config/merged_output.mp4 "你好呀我是你爸爸" C:/Users/23154/Desktop/AI硬件项目/AI文献视觉/AI-Paper2Video/config/captioned.mp4 80`

- 添加语音（音频更长截断，短则静音填充）  
  `python video+voi.py C:/Users/23154/Desktop/AI硬件项目/AI文献视觉/AI-Paper2Video/config/merged_output.mp4 C:/Users/23154/Desktop/AI硬件项目/AI文献视觉/AI-Paper2Video/config/output.wav C:/Users/23154/Desktop/AI硬件项目/AI文献视觉/AI-Paper2Video/config/voiced.mp4`

如果你 cd 到 `src/core/VideoMerging/` 目录，再运行时需要补上相对路径，例如：  
`python video+cap.py C:\Users\23154\Desktop\AI硬件项目\AI文献视觉\AI-Paper2Video\config\merged_output.mp4 "啊大师傅撒旦发射点发生打法二分阿斯蒂芬" C:\Users\23154\Desktop\AI硬件项目\AI文献视觉\AI-Paper2Video\config\captioned.mp4 192`

### 调整字号 / 字体
- 字号：命令末尾的数字控制字号（默认 192），例如 `... captioned.mp4 240` 更大，`... 120` 更小。
- 字体：代码会依次尝试微软雅黑/宋体/Arial/DejaVuSans，仍不理想可在代码中传入字体路径。如需我改成命令行可传字体，请告诉我。



<h1 align="center" style="font-size:50px;font-weight:bold">VideoSlim</h1>
<p align="center">简洁易用的 Windows 视频压缩工具</p>

<p align="center">
  <img src="./img/interface.jpg" width="520" style="display:block;margin:auto;" />
  <br/>
  <img src="./img/readme.jpg" width="820" style="display:block;margin:auto;" />
  <br/>
  <a href="https://github.com/mainite/VideoSlim">GitHub</a>
  ·
  <a href="#%E5%BF%AB%E9%80%9F%E4%BD%BF%E7%94%A8">快速使用</a>
  ·
  <a href="#%E9%85%8D%E7%BD%AE">配置</a>
  ·
  <a href="#%E6%9E%84%E5%BB%BA%E8%84%9A%E6%9C%AC">构建指南</a>
</p>

---

## 功能特性
- **拖拽即用**: 将文件或文件夹拖入窗口，一键开始压缩
- **批量处理与递归扫描**: 可递归扫描子文件夹中的视频
- **多配置切换**: `config.json` 中可定义多套压缩参数方案
- **可选删除音频轨道** 与 **完成后删除源文件**
- **自动修正旋转信息**: 若视频存在旋转元数据，自动预处理
- **日志记录**: 生成 `log.txt`，方便调试和问题排查
- **单文件打包**: 支持将应用和ffmpeg等工具打包为单个可执行文件

## 技术栈
- **Python 3.12+**: 主要开发语言
- **Tkinter**: 图形用户界面
- **FFmpeg**: 视频处理核心工具（已内置）
- **x264**: H.264 视频编码器（通过FFmpeg调用）
- **AAC**: 音频编码（通过FFmpeg调用）
- **pymediainfo**: 媒体信息解析
- **windnd**: 拖拽功能支持

## 快速使用
1. **下载可执行文件**: 从发布页面下载 `VideoSlim.exe`（已包含所有依赖）
2. **或运行源码**: 
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
3. **使用方式**:
   - 将视频文件或包含视频的文件夹拖入窗口
   - 选择配置方案
   - 勾选所需选项（递归、删除源文件、删除音频）
   - 点击"压缩"按钮开始处理

处理完成后，将在源文件同目录生成 `*_x264.mp4` 文件。

## 配置
应用启动时读取 `config.json`。若不存在，将自动生成默认配置：

```json
{
  "comment": "Configuration file for VideoSlim. See README.md for parameter descriptions.",
  "configs": {
    "default": {
      "x264": {
        "crf": 23.5,
        "preset": "medium",
        "I": 600,
        "r": 4,
        "b": 3,
        "opencl_acceleration": false
      }
    },
    "fast": {
      "x264": {
        "crf": 28,
        "preset": "fast",
        "I": 600,
        "r": 3,
        "b": 2,
        "opencl_acceleration": true
      }
    },
    "high_quality": {
      "x264": {
        "crf": 18,
        "preset": "slow",
        "I": 600,
        "r": 6,
        "b": 4,
        "opencl_acceleration": false
      }
    }
  }
}
```

### 参数说明
- **crf (0–51)**: 质量控制参数，值越小质量越高（体积越大），推荐范围 18–28
- **preset**: 编码速度/压缩效率平衡，可选值：ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
- **I**: 关键帧间隔（GOP），推荐值 600
- **r**: 参考帧数量，推荐值 3–6
- **b**: B 帧数量，推荐值 2–4
- **opencl_acceleration**: 是否开启 OpenCL GPU 加速

## 构建指南

### 环境准备
1. 安装 Python 3.12+
2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```
3. 安装 PyInstaller:
   ```bash
   pip install pyinstaller
   ```

### 使用构建脚本
项目提供了自动化构建脚本 `scripts/build.cmd`，支持单文件打包:

```bash
# 运行构建脚本
scripts/build.cmd
```

构建完成后，可执行文件将位于 `output/dist/VideoSlim.exe`，包含所有必要的工具和依赖。

### 手动构建选项
```bash
# 构建单文件应用
pyinstaller --onefile --name "VideoSlim" --noconsole --icon "./tools/icon.ico" --add-data "./tools/ffmpeg.exe;tools" --add-data "./tools/icon.ico;tools" main.py
```

## 目录结构
```
VideoSlim/
├── main.py                # 启动入口
├── config.json            # 配置文件（首次运行自动生成）
├── pyproject.toml         # Python 项目配置
├── README.md              # 项目文档
├── LICENSE                # 许可证文件
├── src/                   # 源代码目录
│   ├── controller.py      # 控制器
│   ├── view.py            # 视图层
│   ├── service/           # 服务层
│   │   ├── video.py       # 视频处理服务
│   │   ├── config.py      # 配置服务
│   │   └── message.py     # 消息服务
│   ├── model/             # 数据模型
│   ├── meta/              # 常量定义
│   └── utils/             # 工具函数
├── tools/                 # 内置工具
│   ├── ffmpeg.exe         # FFmpeg 可执行文件
│   └── icon.ico           # 应用图标
├── img/                   # 截图和资源
├── scripts/               # 脚本文件
│   └── build.cmd          # 构建脚本
└── output/                # 构建输出目录
```

## 工作原理
1. **媒体信息解析**: 使用 MediaInfo 解析视频文件的详细信息
2. **旋转预处理**: 如果视频包含旋转元数据，使用 FFmpeg 进行修正
3. **视频压缩**: 使用 FFmpeg 和 x264 编码器进行视频压缩
4. **音频处理**: 根据用户选择保留或删除音频轨道
5. **合并输出**: 生成最终的 MP4 视频文件

## 日志与调试
- 程序运行时会生成 `log.txt` 文件
- 日志包含详细的命令执行信息和错误信息
- 如遇到问题，可查看日志文件进行调试

## 常见问题
- **无法拖拽/窗口不响应**: 确认已安装所有依赖，并以常规权限运行
- **无法解析媒体信息**: 确保视频文件未被占用，或尝试安装最新版本的 MediaInfo
- **编码失败**: 查看 `log.txt` 获取具体错误信息
- **质量不满意**: 调整 `crf` 参数（值越小质量越高）
- **编码过慢**: 提高 `preset` 参数值（如从 slow 改为 medium 或 fast）

## 许可证
本项目采用开源许可证，详见 `LICENSE` 文件。
FFmpeg 和其他第三方工具按其各自许可证使用与分发。

## 致谢
- **FFmpeg**: 强大的音视频处理工具
- **MediaInfo**: 专业的媒体信息分析库
- **x264**: 优秀的 H.264 视频编码器

—— 祝使用愉快 🎬

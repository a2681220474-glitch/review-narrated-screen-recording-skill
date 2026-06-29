# Narrated Screen Recording Review Skill

一个面向 Codex 的开源 Skill：把“边操作、边口述问题”的验收录屏转换成带时间戳和画面证据的确认清单。

它解决的核心问题不是单纯抽帧或转写，而是把声音中的真实意图与当时屏幕上的页面、控件和操作结果准确对齐。

## 能做什么

- 提取录屏音轨并执行中文或多语言转写
- 按指定间隔抓取关键帧
- 生成带时间戳的联系表
- 将字幕片段映射到附近的完整画面
- 区分电脑端鼠标、悬停与键盘操作，以及手机端点击、滑动和手势证据
- 区分修改要求、问题、认可、撤回、提问和普通操作说明
- 识别“哦，这个没事”等后续撤回，避免生成错误任务
- 始终保持录屏分析模式，不执行代码修改或其他产品操作
- 输出可按编号确认的验收清单

## 目录

```text
skills/review-narrated-screen-recording/
├── SKILL.md
├── agents/openai.yaml
├── references/checklist-format.md
├── references/platform-evidence.md
└── scripts/prepare_review.py
```

## 安装

克隆仓库后，将 Skill 复制到 Codex 的个人技能目录：

```bash
git clone https://github.com/a2681220474-glitch/review-narrated-screen-recording-skill.git
cp -R review-narrated-screen-recording-skill/skills/review-narrated-screen-recording ~/.codex/skills/
```

重新打开一个 Codex 对话后即可调用：

```text
使用 $review-narrated-screen-recording 复核这个录屏：
/absolute/path/to/video.mov
只根据声音和画面列出确认清单，不执行其他操作。
```

## 本地工具

必需：

- Python 3.10+
- FFmpeg，包括 `ffmpeg` 和 `ffprobe`

本地转写推荐：

- `whisper-cli`，来自 [whisper.cpp](https://github.com/ggml-org/whisper.cpp)
- 一个多语言 GGML Whisper 模型，例如 `ggml-small.bin`

Skill 默认优先本地转写，录屏和音频无需上传到第三方服务。

## 单独运行预处理脚本

```bash
python3 skills/review-narrated-screen-recording/scripts/prepare_review.py \
  /absolute/path/to/video.mov \
  --output /private/tmp/narrated-review-demo \
  --interval 1 \
  --language zh \
  --model /absolute/path/to/ggml-small.bin \
  --prompt "产品名、页面名、功能名"
```

主要产物：

- `audio-16k.wav`
- `frames/frame_*.jpg`
- `sheets/sheet_*.jpg`
- `frame-manifest.json`
- `transcript.txt`
- `transcript.srt`
- `transcript.json`
- `timeline.json`
- `review-summary.json`

不提供 `--model` 时，脚本仍会完成音轨、逐秒帧和联系表提取。之后可使用其他语音转写服务生成 SRT，再重新运行脚本生成时间轴映射。

## 方法原则

1. 语音决定“用户要求什么”，画面决定“用户当时指什么”。
2. 必须完整阅读转写，不能只按关键词抓问题。
3. 后说的话可以推翻前面的判断。
4. 画面中看见但用户没有提到的问题，必须单独标注，不能混入确认清单。
5. 输出只负责准确还原录屏反馈；明确说“不改”的项目必须保留。

### 电脑端与手机端

- 电脑端结合鼠标指针、悬停、按下、焦点、右键菜单、键盘和操作后的状态变化判断目标。
- 手机端优先使用触摸指示；未显示手指时，通过点击前后的页面变化推断目标，并明确标记为推断。
- 手机滑动、长按、返回手势和软键盘必须通过连续帧判断，不能把动画或网络延迟误认为另一次操作。
- 模拟器、投屏和带触控板的平板分别记录“界面类型”和“输入方式”，避免简单归类。

## 测试

仓库内的 GitHub Actions 会自动：

1. 安装 FFmpeg。
2. 生成一个带音频的测试视频。
3. 运行预处理脚本。
4. 验证音轨、逐秒帧、联系表和摘要均已生成。

## License

MIT

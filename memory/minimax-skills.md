# MiniMax Skills 学习笔记

## 仓库概览
- **Repo**: https://github.com/MiniMax-AI/skills
- **8.2k stars**, 621 forks, MIT license
- 官方 skills: 13个 | 社区 skill: 1个
- 克隆位置: `/root/.openclaw/workspace/minimax-skills/`
- **已安装到**: `~/.openclaw/skills/` ✅

## 已安装 Skill 列表 (2026-03-31)
- android-native-dev
- flutter-dev
- frontend-dev
- fullstack-dev
- gif-sticker-maker
- ios-application-dev
- minimax-docx
- minimax-multimodal-toolkit
- minimax-pdf
- minimax-xlsx
- pptx-generator
- react-native-dev
- shader-dev
- vision-analysis

## Skills 总览

### 1. frontend-dev
**定位**: 全栈前端开发 + 设计工程 + AI 媒体生成
- 设计: Tailwind CSS, 字体(Geist/Outfit/Satoshi), 8dp网格
- 动画: Framer Motion(UI) / GSAP ScrollTrigger(滚动) / R3F(3D)
- 禁止: Emojis, Inter字体, 渐变文字, 霓虹光晕
- AI资产: MiniMax TTS/音乐/图片/视频生成脚本
- 文案: AIDA/PAS/FAB 框架
- 生成艺术: p5.js 交互模式

### 2. fullstack-dev
**定位**: 全栈后端架构 + 前后端集成
- 架构: Feature-first + Controller→Service→Repository 三层
- 配置: 中心化、类型化、fail-fast
- 错误: Typed Error Hierarchy + 全局错误处理器
- 日志: 结构化JSON + request ID传播
- 认证: JWT(短期) + Refresh Token(httpOnly cookie)
- 实时: SSE(单向) / WebSocket(双向) / Polling(轮询)
- API客户端: Typed Fetch / React Query+tRPC / OpenAPI生成
- 文件上传: 预签名URL(大文件) / Multipart(小文件<10MB)

### 3. android-native-dev
**定位**: Kotlin + Jetpack Compose + Material Design 3
- 线程: Dispatchers.IO(网络) / Dispatchers.Main(UI) / Dispatchers.Default(计算)
- 空安全: `?.` + `?:` 而非 `!!`
- 异常: `Result<T>` 包装，propagate 而非 swallow
- 资源命名: 禁止 Android 保留字(background, icon, view, text...)
- 触摸: ≥48dp，最小56dp(儿童App)
- 间距: 8dp网格
- Build variants: `flavorDimensions` + `productFlavors` 支持多环境

### 4. ios-application-dev
**定位**: UIKit/SnapKit + SwiftUI + Apple HIG
- 触摸: ≥44pt
- 安全区: 内容必须在safe area内
- 导航: UITabBarController(3-5tab) / UINavigationController(钻取)
- 动态类型: UIFontMetrics + preferredFont
- 颜色: 语义系统色(.systemBackground, .label)
- 权限: 上下文情境下请求，绝不在启动时弹窗
- 减少动画: @Environment(\.accessibilityReduceMotion)

### 5. flutter-dev
**定位**: Flutter 3 + Riverpod/Bloc + GoRouter
- Widget优化: `const` 构造器, `Key` for list items
- 状态: Riverpod(简单) / Bloc/Cubit(复杂工作流)
- 性能: <16ms帧时间, RepaintBoundary隔离重绘
- 布局: 8dp间距, 响应式断点(mobile<650, tablet<1100, desktop>1100)

### 6. react-native-dev
**定位**: React Native + Expo + FlashList + Reanimated 3
- 列表: FlashList(替代FlatList，有view recycling)
- 图片: expo-image(替代RN Image，有缓存和WebP)
- 动画: Reanimated 3 替代 RN Animated API
- 状态: Zustand/Jotai(共享) + React Query(服务端) + React Hook Form+Zod(表单)
- 性能: FlashList + memo + 虚拟化

### 7. shader-dev
**定位**: GLSL着色器 36种技术
- 核心技术: Ray marching, SDF建模, PBR光照
- 仿真: Navier-Stokes流体, 粒子系统, 元胞自动机
- 程序化: Perlin/Simplex FBM, Voronoi, 分形
- 后处理: Bloom, ACES色调映射, 抗锯齿
- WebGL2适配: `#version 300 es`, `gl_FragCoord.xy`, mainImage包装

### 8. gif-sticker-maker
**定位**: 照片 → 4个Funko Pop风格GIF贴纸
- 流程: 静态图 → 视频动画 → GIF转换
- 必须: MiniMax API + ffmpeg + Python venv
- 输出: 4个GIF + caption

### 9. minimax-pdf
**定位**: 专业PDF生成/填充/重排版
- 三条路线: CREATE / FILL / REFORMAT
- 设计系统: Token化(color/typography/spacing来自文档类型)
- 15种封面风格: report/proposal/resume/portfolio/academic/minimal/stripe/diagonal/frame/editorial/magazine/darkroom/terminal/poster
- CREATE: palette.py → cover.py → render_cover.js → render_body.py → merge.py
- FILL: pypdf填写表单字段
- REFORMAT: 解析源文档 → content.json → CREATE pipeline

### 10. pptx-generator
**定位**: PowerPoint创建/编辑/读取
- 创建: PptxGenJS(从零) / XML操作(编辑模板)
- 读取: markitdown提取文本
- 5种页面类型: Cover/TOC/Section Divider/Content/Summary
- 设计系统: 配色palette + 字体 + 样式配方(Sharp/Soft/Rounded/Pill)
- 必须: 页码徽章(9.3", 5.1")，Cover除外
- 主题键: primary/secondary/accent/light/bg

### 11. minimax-xlsx
**定位**: Excel创建/读取/编辑/验证
- 读取: xlsx_reader.py + pandas
- 创建: XML模板(复制minimal_xlsx/ → 编辑XML → xlsx_pack.py)
- 编辑: XML unpack → edit → pack(禁止openpyxl round-trip!)
- 金融配色: Blue=输入, Black=公式, Green=跨sheet引用
- 公式优先: 所有计算单元格必须用Excel公式，不能硬编码

### 12. minimax-docx
**定位**: Word文档创建/编辑/模板套用
- 工具: OpenXML SDK (.NET C#)
- 三条路线: CREATE / FILL-EDIT / FORMAT-APPLY
- 验证: XSD结构验证 + 业务规则验证 + diff检查
- 关键: 元素顺序严格(OpenXML腐败问题)
  - w:p: pPr → runs
  - w:r: rPr → t/br/tab
  - w:tbl: tblPr → tblGrid → tr
  - w:body: block content → sectPr(LAST)
- 样式必须含OutlineLevel，否则TOC不工作

### 13. minimax-multimodal-toolkit
**定位**: MiniMax multimodal API统一入口
- API Host: 中国大陆api.minimaxi.com / 全球api.minimax.io
- TTS: speech-2.8-hd(推荐) / speech-2.8-turbo
- 语音: clone(10s-5min音频) / design(文本描述)
- 音乐: music-2.5模型，instrumental模式(配BGM用)
- 图片: image-01, t2i/i2i模式，比例推断(不要总用1:1)
- 视频: Hailuo-2.3(默认6s/768P), i2v/ref/sef多种模式
- 重要限制: 视频每天配额极少(2-5个)，1080P不支持
- 长视频: 多段链接 + crossfade transition

### 14. vision-analysis
**定位**: 图像分析(MiniMax understand_image MCP工具)
- 模式: describe / ocr / ui-review / chart-data / object-detect
- 用途: OCR、UI mockup review、图表数据提取、物体检测
- 配置: 需要minimax-coding-plan-mcp包

## 共同设计模式

### 工作流结构
1. **环境检查** → 2. **路由选择** → 3. **执行** → 4. **QA验证** → 5. **交付**

### 路由表模式
每个skill都有清晰的路由表(条件 → 路径 → 工具)，用表格呈现，便于快速决策。

### 质量门控(Quality Gates)
- frontend-dev: 无placeholder URL、所有资产本地化、motion cleanup
- fullstack-dev: 构建检查 + 冒烟测试 + 集成检查
- minimax-docx: XSD验证 + 业务规则 + diff + preview
- minimax-xlsx: formula_check.py exit code = 0

### 环境验证前置
大多数skill要求先验证环境(check_environment.sh / env_check.sh)，缺失依赖则不继续。

### 参考文档分离
每个skill都有references/目录，存放深度参考文档，正文只放路由表和核心模式。

### MiniMax API约定
- minimax-pdf: Python 3.9+ + reportlab + Node.js 18+ + playwright
- minimax-multimodal: curl/ffmpeg/jq/xxd，纯bash无Python依赖
- minimax-xlsx: openpyxl禁止(会破坏现有文件)，只用XML unpack/edit/pack

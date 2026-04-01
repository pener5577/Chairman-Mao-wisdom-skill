# 🤖 OpenClaw Skills 完整掌握指南

> 掌握所有自定义 Skills 的核心要点

---

## 📋 Skills 清单

### 一、核心能力（必须精通）

#### 1. proactive-agent 🦞
**核心：主动式 AI + 内存 survive**

| 概念 | 要点 |
|------|------|
| **WAL Protocol** | 收到人类输入时立即写 SESSION-STATE.md，再响应 |
| **Working Buffer** | 上下文 >60% 时记录每个交换 |
| **Compaction Recovery** | 从 working-buffer.md 恢复上下文 |
| **Heartbeat** | 每轮检查 proactive-tracker.md, 内存, 安全 |
| **反向提示** | 问"什么能帮到你"而不是等指令 |

**触发词**: 心跳, 主动检查, 主动帮忙

---

#### 2. investigate 🔍
**核心：系统化根因分析**

| 步骤 | 内容 |
|------|------|
| 1. 问题定义 | 明确错误现象、收集环境、复现条件 |
| 2. 信息收集 | 日志、堆栈、监控 |
| 3. 假设形成 | 提出可能原因、验证实验、优先级 |
| 4. 验证测试 | 逐个验证、收集证据 |
| 5. 根因确定 | 确认影响范围、修复计划 |
| 6. 修复验证 | 实施修复、确认无回归 |

**触发词**: debug, 调查, 根本原因, 为什么失败

---

#### 3. office-hours 🏢
**核心：YC 创业验证**

| 模式 | 问题 |
|------|------|
| **创业公司模式** | 6 个强制问题：问题→方案→优势→用户→商业模式→增长 |
| **构建者模式** | 问题重构→用户视角→约束创新→快速验证 |

**原则**:
- 特异性是唯一货币
- 兴趣 ≠ 需求
- 狭窄优于宽泛

**触发词**: 头脑风暴, 我有一个想法, 产品创意

---

#### 4. review 🔎
**核心：代码安全审查**

| 阶段 | 检查项 |
|------|--------|
| **关键阶段** | SQL安全、竞态条件、LLM信任边界、枚举完整、认证漏洞 |
| **信息阶段** | 条件副作用、魔法数字、死代码、测试覆盖、性能 |

**状态协议**: DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT

**触发词**: review this PR, code review, 审查代码

---

### 二、QA 与发布

#### 5. qa-test
- 运行测试
- 迭代修复 bug
- 原子化提交每个修复

#### 6. ship 🚢
- 检测基础分支
- 运行测试
- 审查差异
- 版本管理
- 更新日志
- 提交推送
- 创建 PR

---

### 三、安全护栏

#### 7. careful ⚠️
- 删除操作前警告
- 覆盖文件前警告
- 危险命令执行前警告

#### 8. freeze 🔒
- 限制文件编辑范围
- 防止意外修改

#### 9. guard 🛡️
- careful + freeze 组合
- 完全安全模式

#### 10. skill-vetter 🔐
- 安装前安全审查
- 检查可疑命令
- 权限 scope 检查

---

### 四、设计评审

#### 11. design-consultation 🎨
- 构建完整设计系统
- 专业设计建议

#### 12. design-review
- 设计审计和修复
- 检查一致性

#### 13. plan-design-review
- 设计师视角评审
- UX、视觉、交互

#### 14. plan-ceo-review
- CEO/创始人视角
- 10星级产品思维
- 挑战前提假设

#### 15. plan-eng-review
- 工程架构评审
- 锁定技术架构
- 评估实现方案

---

### 五、知识与管理

#### 16. ontology 🧠
- 知识图谱
- 实体管理（Person, Project, Task, Event）
- 跨技能数据共享

**触发词**: remember, what do I know about, link X to Y

#### 17. self-improving-agent 📈
- 捕获学习、错误、修正
- 持续改进

**触发场景**: 命令失败、用户纠正、发现更好方法

#### 18. find-skills 🔎
- 发现新技能
- 安装管理

**触发词**: how do I do X, find a skill for X

#### 19. summarize 📝
- 总结 URL/文件
- 支持 PDF、图片、音频、YouTube

#### 20. retro 📊
- 团队周报
- 迭代回顾

---

### 六、媒体与发布

#### 21. douyin-upload 📱
- 抖音登录：`sau douyin login --account <name>`
- Cookie 校验：`sau douyin check --account <name>`
- 视频上传：`sau douyin upload-video ...`
- 图文上传：`sau douyin upload-note ...`

#### 22. agent-browser 🌐
- 浏览器自动化
- 导航、点击、输入、快照

---

### 七、其他

#### 23. codex
- OpenAI Codex 独立审查
- 第二意见

#### 24. document-release
- 技术文档更新

---

## 🎯 快速调用表

| 需求 | 使用 Skill |
|------|-------------|
| 主动帮忙 | proactive-agent |
| 调试问题 | investigate |
| 创业验证 | office-hours |
| 代码审查 | review |
| 测试修复 | qa |
| 自动发布 | ship |
| 安全警告 | careful |
| 限制编辑 | freeze |
| 设计咨询 | design-consultation |
| CEO评审 | plan-ceo-review |
| 工程评审 | plan-eng-review |
| 知识管理 | ontology |
| 抖音发布 | douyin-upload |
| 总结内容 | summarize |
| 团队回顾 | retro |

---

*Last Updated: 2026-03-27*

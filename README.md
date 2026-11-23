# 毛主席智慧宝库 · mao-wisdom

一个面向 OpenClaw 的中文技能。你可以用它查毛泽东著作和诗词的原文，比较流传说法与书中的用字，也可以把调查研究、主要矛盾分析等方法用在一个具体的工作或学习问题上。

## 安装到 OpenClaw

在你的 OpenClaw 工作区根目录运行以下命令。Git 会把技能和语录库一起放进 `skills/mao-wisdom`，这个目录只需克隆一次。

```sh
git clone https://github.com/pener5577/Chairman-Mao-wisdom-skill.git skills/mao-wisdom
openclaw skills info mao-wisdom
```

看到 `mao-wisdom` 就可以新开一次对话试用。以后在同一个工作区运行 `git -C skills/mao-wisdom pull --ff-only` 即可更新。[OpenClaw 技能目录说明](https://docs.openclaw.ai/tools/skills)

## 可以怎么问

| 想做什么 | 可以直接问 |
| --- | --- |
| 找原文 | “‘前途是光明的，道路是曲折的’出自哪一篇？请给我原句和出处。” |
| 核对流传说法 | “‘最后的胜利，往往在于再坚持一下的努力之中’能在《论持久战》里找到吗？” |
| 读懂一篇文章 | “《实践论》里考察团初到延安的例子，跟后面讲的检验认识有什么关系？” |
| 用方法解决问题 | “读书会每周都有计划，却总读不完。请用调查研究的方法，帮我们找出卡在哪里。” |
| 仿写 | “给读书小组写一段鼓劲的话，模仿这种文风，并标明是仿写。” |

[语录库](references/mao-quotes.md)按主题编排，包含战略全局观、矛盾论与实践论、群众路线、工作方法、学习与调查研究等。带“核对原文”链接的条目可回到对应版本查看上下文。其余线索用于继续查找，条目标题可能是常见说法或主题概括。

读《反对本本主义》《实践论》或《矛盾论》时，可以打开[三篇文章导读](references/reading-guide.md)。每篇都从原文里的一个例子入手，列出阅读位置和适合读书会讨论的问题。

## 离线检索

在仓库根目录用 Python 3.9 或更高版本运行，无需安装第三方库。macOS 或 Linux 上可将 `python` 换成 `python3`。

```sh
python scripts/search_quotes.py --verified 调查
python scripts/search_quotes.py 吃梨子 实践论
python scripts/search_quotes.py --verified
```

第一个命令只找已核对的条目，第二个用常见说法和篇名查找同一条目，第三个按语录库顺序列出所有已核条目。带关键词时，优先显示正文和标题中的匹配，单凭主题命中的条目靠后。复制引文请取“已核原文”一行。想查一条转述的来历，也可以用“辨析”中的词搜索。

## 维护

技能入口在 [SKILL.md](SKILL.md)。补充条目时，在[语录库](references/mao-quotes.md)相应主题下记录原句、作品名和版本。逐字核对后在“出处”行附上“核对原文”链接。对尚未证实的流传说法，在“出处”行标“待核”，把可以查证的相近表述和来源放到“辨析”一行。需要支持口语查询时，用“检索词”一行列出别称，以顿号分隔。

修改语录库或检索工具后，可在仓库根目录执行 `python -m unittest discover -s tests`，检查已核条目是否都能搜到、待核条目是否会被误作原文。

[iteration.sh](iteration.sh) 供有推送权限的维护者手动运行。在项目的 `main` 分支执行 `bash iteration.sh` 会同步本项目的技能说明、语录和检索工具到 `origin/main`。如需定时同步，请在自己的任务调度器中设置运行时间。内容校订由维护者完成。

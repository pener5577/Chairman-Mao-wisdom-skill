# 毛主席智慧宝库 · mao-wisdom

一个面向 OpenClaw 的中文技能。你可以用它查毛泽东著作和诗词的原文，比较流传说法与书中的用字，也可以把调查研究、主要矛盾分析等方法用在一个具体的工作或学习问题上。

## 收录范围

| 要查的内容 | 当前覆盖 |
| --- | --- |
| 《毛泽东选集》篇名与正文片段 | [一至五卷目录](references/works-index.md)列出 229 篇正文，分卷为 18、40、31、70、70 篇。篇名随技能提供，全文片段可在首次联网建库后离线查找。第三卷的集体决议附录单列，可查篇名。 |
| 语录用字与归属 | [语录库](references/mao-quotes.md)含 47 条已核摘句，其中 35 条引自《毛泽东选集》，12 条选自《毛泽东文集》、题词和诗词。另保留 6 条待核说法。 |
| 文章导读 | [六篇导读](references/reading-guide.md)含调查研究、实践与认识、主要矛盾，以及《为人民服务》《党委会的工作方法》《关心群众生活，注意工作方法》。 |
| 《毛泽东文集》篇名 | [八卷篇目](references/collected-works-index.md)可离线查找 803 篇文稿的卷次、卷内序号及 PDF 页序。打开篇名可直达对应文稿的正文首页。 |
| 《毛泽东诗词集》诗题 | [1996 年版目录](references/poetry-index.md)收录正编 42 首、副编 25 首。组诗按书中题目合列，63 个题目均可直达诗文。两首同名《浣溪沙》附月份与首句。 |

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

读书会可以用[六篇文章导读](references/reading-guide.md)按段讨论。例如，读《党委会的工作方法》时，把会前通知、交换情况和会上讨论放在一起看，再为小组自己的下一次会议写一份通知。

## 离线检索

在仓库根目录用 Python 3.9 或更高版本运行，无需安装第三方库。macOS 或 Linux 上可将 `python` 换成 `python3`。

```sh
python scripts/search_quotes.py --verified 调查
python scripts/search_quotes.py 吃梨子 实践论
python scripts/search_quotes.py --works 第三卷 为人民服务
python scripts/search_quotes.py --collection 文集 寻乌调查
python scripts/search_quotes.py --collection 诗词 浣溪沙 和柳亚子
```

前三个命令分别查已核摘句、流传说法和《选集》篇目。后两个可以找到《寻乌调查》的卷次，以及 1950 年 10 月和 11 月的两首同名词。省略关键词时，`--verified` 列出全部已核摘句，`--works` 列出《选集》目录，`--collection 文集` 或 `--collection 诗词` 列出相应书目。

普通搜索先找语录，未命中时再查三部书的篇名。《文集》结果附原书 PDF 首页。例如，第一卷两篇《给傅作义的信》分别跳到 PDF 第 433、466 页，可以看题下注明的日期来区分。要逐字引用，取“已核原文”一行，或在对应版本中重新核对。“辨析”中的词也可用来查一条转述的来历。

### 只记得一句话，怎样找出篇名？

在仓库根目录执行第一条命令，联网读取五卷目录所列的 229 篇转录，在个人缓存目录建立全文索引。建好后，第二条命令可断网使用。

```sh
python scripts/search_quotes.py --build-index
python scripts/search_quotes.py --text "人固有一死"
```

结果列出命中的作品、转录段号、附近文字和阅读链接，默认显示前 20 段，可用 `--limit 50` 调整。标点或空格略有差异时也可匹配。遇到异体字、改写或跨段引文，可拆成较短的词组分别查找。段号用于定位这份网页转录。正式引用时，应再核对所用版本的原句和纸本页码。

需要把索引放在指定位置时，在上述两条命令中都加上 `--index-path "路径/mao-wisdom.sqlite3"`。再次执行建库命令即可刷新，获取失败会保留原有索引。

例如，《论联合政府》同一段在网页转录里写作“其它政党”，人民出版社 1991 年第二版用“其他政党”。用两版共有的“有无认真的自我批评”检索，即可定位段落，再按所用版本引用。[纸本第三卷第 1096 页](https://ebook.theorychina.org.cn/ebook/upload/storage/files/2022/07/26/96241bf235bd68bad86fed6360e6a8bc32635/files/basic-html/page318.html) · [网页转录](https://www.marxists.org/chinese/maozedong/marxist.org-chinese-mao-19450424.htm)

### 只记得诗句，怎样查诗题？

首次运行以下建库命令会读取 63 个题目的公开诗文，在个人缓存中另建诗词索引。之后可断网检索正编和副编的 67 首作品。组诗的每一首单独定位。例如，“倒海翻江卷巨澜”会命中《十六字令三首》的第二首。查询只匹配诗文，题注和赏析可打开结果链接阅读。

```sh
python scripts/search_quotes.py --collection 诗词 --build-index
python scripts/search_quotes.py --collection 诗词 --text "倒海翻江卷巨澜"
```

## 维护

技能入口在 [SKILL.md](SKILL.md)。补充条目时，在[语录库](references/mao-quotes.md)相应主题下记录原句、作品名和版本。逐字核对后在“出处”行附上“核对原文”链接。对尚未证实的流传说法，在“出处”行标“待核”，把可以查证的相近表述和来源放到“辨析”一行。需要支持口语查询时，用“检索词”一行列出别称，以顿号分隔。

修改语录库或检索工具后，可在仓库根目录执行 `python -m unittest discover -s tests`，检查已核条目是否都能搜到、待核条目是否会被误作原文。

[iteration.sh](iteration.sh) 供有推送权限的维护者手动运行。在项目的 `main` 分支执行 `bash iteration.sh` 会同步本项目的技能说明、语录和检索工具到 `origin/main`。如需定时同步，请在自己的任务调度器中设置运行时间。内容校订由维护者完成。

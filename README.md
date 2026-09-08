# RAG：企业知识库检索与引用教学工程

原创、可运行的 Python 教学工程，从文档证据逐步扩展到混合检索与可选模型回答。用于理解企业知识库，也可作为 ERP Agent 的知识工具基础；当前尚未接入 ERP 服务。

**这里的六章是本次对已有教学实现重新编排的提交，不是官方课程章节、官方源码，也不是过去开发过程的追溯。** 提交和标签使用实际创建时间。

## 独立运行

安装 Python 3.11 或 3.12，并在克隆后的仓库目录运行。离线演示仅依赖 Python 标准库，SQLite 构建需支持 FTS5（CI 会实际验证）。如需文本 PDF，另执行 `python -m pip install pypdf`。

```shell
git clone https://github.com/ooo1208/RAG.git
cd RAG
python rag_lab.py read data/procurement.md
```

PowerShell 编码异常时可先设置 `$env:PYTHONIOENCODING = 'utf-8'`。数据均为合成资料；演示使用临时数据库、不会调用外部模型。

## 当前能力（第 1 章）

- TXT、Markdown、CSV 原始文本读取，以及可选文本 PDF 按页提取。

## 逐章学习

| 章 | 文档 | 快照 |
|---|---|---|
| 01 | [文档读取与证据位置](docs/chapter-01.md) | `chapter-01` |

查看一章用 `git switch --detach chapter-01`，回到最新用 `git switch main`。各章文档中给出的运行方式与对应标签匹配；最新版本的 CLI 已随着能力扩展调整。

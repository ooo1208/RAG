# RAG：企业知识库检索与引用教学工程

原创、可运行的 Python 教学工程，从文档证据逐步扩展到混合检索与可选模型回答。用于理解企业知识库，也可作为 ERP Agent 的知识工具基础；当前尚未接入 ERP 服务。

**这里的六章是本次对已有教学实现重新编排的提交，不是官方课程章节、官方源码，也不是过去开发过程的追溯。** 提交和标签使用实际创建时间。

## 独立运行

安装 Python 3.11 或 3.12，并在克隆后的仓库目录运行。离线演示仅依赖 Python 标准库，SQLite 构建需支持 FTS5（CI 会实际验证）。如需文本 PDF，另执行 `python -m pip install pypdf`。

```shell
git clone https://github.com/ooo1208/RAG.git
cd RAG
python rag_lab.py demo
```

PowerShell 编码异常时可先设置 `$env:PYTHONIOENCODING = 'utf-8'`。数据均为合成资料；演示使用临时数据库、不会调用外部模型。

## 当前能力（第 3 章）

- TXT、Markdown、CSV 原始文本读取，以及可选文本 PDF 按页提取。
- 追加重叠切片、页码/行范围、SQLite 事务替换、命名空间。
- 追加 FTS5 BM25 中文词法检索、引用来源、3 个合成演示问题。

## 逐章学习

| 章 | 文档 | 快照 |
|---|---|---|
| 01 | [文档读取与证据位置](docs/chapter-01.md) | `chapter-01` |
| 02 | [切片与事务化入库](docs/chapter-02.md) | `chapter-02` |
| 03 | [BM25 检索与原文引用](docs/chapter-03.md) | `chapter-03` |

查看一章用 `git switch --detach chapter-01`，回到最新用 `git switch main`。各章文档中给出的运行方式与对应标签匹配；最新版本的 CLI 已随着能力扩展调整。

## 持久化导入与查询

```shell
python rag_lab.py --user learner ingest data/procurement.md data/report.md data/quality.md
python rag_lab.py --user learner ask "采购订单需要谁审批？"
python rag_lab.py --user another ask "采购订单需要谁审批？"
```

第二个用户应没有证据。`--user` 只是 CLI 命名空间，拥有数据库文件权限的人仍能读取内容。默认索引位于 `.local/rag.sqlite`，不会加入 Git。

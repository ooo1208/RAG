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

## 当前能力（第 5 章）

- TXT、Markdown、CSV 原始文本读取，以及可选文本 PDF 按页提取。
- 追加重叠切片、页码/行范围、SQLite 事务替换、命名空间。
- 追加 FTS5 BM25 中文词法检索、引用来源、3 个合成演示问题。
- 追加可选真实 Embedding 接口、余弦检索、RRF 融合、更新后向量失效。
- 追加显式 `--live` 的真实聊天模型接口及回答/引用结构校验。

## 逐章学习

| 章 | 文档 | 快照 |
|---|---|---|
| 01 | [文档读取与证据位置](docs/chapter-01.md) | `chapter-01` |
| 02 | [切片与事务化入库](docs/chapter-02.md) | `chapter-02` |
| 03 | [BM25 检索与原文引用](docs/chapter-03.md) | `chapter-03` |
| 04 | [真实向量接口与混合检索](docs/chapter-04.md) | `chapter-04` |
| 05 | [模型回答与引用校验](docs/chapter-05.md) | `chapter-05` |

查看一章用 `git switch --detach chapter-01`，回到最新用 `git switch main`。各章文档中给出的运行方式与对应标签匹配；最新版本的 CLI 已随着能力扩展调整。

## 持久化导入与查询

```shell
python rag_lab.py --user learner ingest data/procurement.md data/report.md data/quality.md
python rag_lab.py --user learner ask "采购订单需要谁审批？"
python rag_lab.py --user another ask "采购订单需要谁审批？"
```

第二个用户应没有证据。`--user` 只是 CLI 命名空间，拥有数据库文件权限的人仍能读取内容。默认索引位于 `.local/rag.sqlite`，不会加入 Git。

## 可选真实模型

参考 [.env.example](.env.example) 在运行终端配置环境变量；程序不会自动加载 `.env`。`BASE_URL` 应包含供应商实际要求的路径，例如 `/v1`，示例占位符不是可用服务。

```powershell
$env:EMBEDDING_BASE_URL = 'https://你的向量服务/v1'
$env:EMBEDDING_API_KEY = '你的密钥'
$env:EMBEDDING_MODEL = '服务支持的向量模型名'
python rag_lab.py embed
python rag_lab.py ask '保修多长时间？' --hybrid
```

`embed` 会将当前命名空间文档发往你配置的服务，混合检索也会发送问题。文档更新、模型或服务变化后必须重新构建向量。当前用全量余弦比较，适合小语料，未实现向量数据库或 ANN 索引。RRF 分数不是答对概率。

```powershell
$env:MODEL_BASE_URL = 'https://你的模型服务/v1'
$env:MODEL_API_KEY = '你的密钥'
$env:MODEL_NAME = '服务支持的聊天模型名'
python rag_lab.py ask '采购订单需要谁审批？' --live
```

`--live` 会把提问和召回片段发往你配置的聊天服务；没有该开关时只展示原文证据。服务或结构校验失败会报错，不会伪装成成功的模型结果。

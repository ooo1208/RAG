# 第 4 章：真实向量接口与混合检索

这六章是对本次已有原创教学代码重新编排的学习提交，不是官方课程章节或历史开发时间的还原。可在当前仓库运行，也可用 `git switch --detach chapter-04` 查看本章快照；返回最新版本用 `git switch main`。

## 目标

把语义检索作为明确可选能力，理解 BM25 与向量召回融合。

## 读码

`request_json`、`Embeddings.encode`、`build_vectors`、`cosine`、`retrieve`：接口校验、索引版本、全量余弦比较与 RRF。

## 运行

在仓库根目录，使用 Python 3.11 或 3.12：

```shell
python rag_lab.py demo
python rag_lab.py --help
```

## 练习

按 `.env.example` 在终端配置实际向量服务，再运行 `python rag_lab.py embed` 和 `python rag_lab.py ask "保修多长时间？" --hybrid`。这里只是接口实现，未预先完成真实服务效果验收。

## 完成标准

记录模型/服务与问题集；解释 RRF 分数不是置信度；文档更新后必须重建向量；固定测试向量不能证明语义效果。

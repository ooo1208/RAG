# 第 3 章：BM25 检索与原文引用

这六章是对本次已有原创教学代码重新编排的学习提交，不是官方课程章节或历史开发时间的还原。可在当前仓库运行，也可用 `git switch --detach chapter-03` 查看本章快照；返回最新版本用 `git switch main`。

## 目标

离线完成导入→检索→原文证据闭环，保留无答案分支。

## 读码

`tokenize`、`retrieve`、`answer`、`demo`：中文双字切分、FTS5 BM25、来源元数据、无证据响应。

## 运行

在仓库根目录，使用 Python 3.11 或 3.12：

```shell
python rag_lab.py demo
python rag_lab.py ingest data/procurement.md data/report.md data/quality.md
python rag_lab.py ask "采购订单需要谁审批？"
```

## 练习

对比“质保期限”和“保修多长时间”，收集词法匹配受同义改写影响的失败案例；用另一个 `--user` 查询观察隔离。

## 完成标准

三个合成问题来源匹配全部通过；返回原文与引用位置；能解释该结果不是语义问答准确率或生产效果报告。

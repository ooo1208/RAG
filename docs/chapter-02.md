# 第 2 章：切片与事务化入库

这六章是对本次已有原创教学代码重新编排的学习提交，不是官方课程章节或历史开发时间的还原。可在当前仓库运行，也可用 `git switch --detach chapter-02` 查看本章快照；返回最新版本用 `git switch main`。

## 目标

建立含来源、页码、行范围的切片，并保证重复导入替换旧内容。

## 读码

`KnowledgeBase.__init__`、`ingest`、`tokenize`：稳定切片 ID、重叠窗口、命名空间、事务写入与 FTS 预处理。

## 运行

在仓库根目录，使用 Python 3.11 或 3.12：

```shell
python rag_lab.py ingest data/procurement.md data/report.md data/quality.md
python rag_lab.py inspect
```

## 练习

在 Python 中分别用 `ingest("learner", path, window=3, overlap=1)` 和 6 行窗口导入，比较切片数量与上下文；修改合成制度后重新导入。

## 完成标准

能从数据库记录回到原文页/行；空文档导入失败后旧索引仍保留；解释 `--user` 仅是本地命名空间，不能替代登录认证。

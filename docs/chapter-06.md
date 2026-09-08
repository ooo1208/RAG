# 第 6 章：回归验证与评估路线

这六章是对本次已有原创教学代码重新编排的学习提交，不是官方课程章节或历史开发时间的还原。可在当前仓库运行，也可用 `git switch --detach chapter-06` 查看本章快照；返回最新版本用 `git switch main`。

## 目标

用自动化检查守住原型行为，再设计自己的效果数据集。

## 读码

`tests/test_rag.py`、`.github/workflows/ci.yml`、`docs/evaluation.md`、`多模态进阶.md`。

## 运行

在仓库根目录，使用 Python 3.11 或 3.12：

```shell
python -m unittest discover -s tests -v
python rag_lab.py demo
```

## 练习

建立至少 20 个标注问题，覆盖同义改写、跨文档、无答案、旧制度替换；真实模型接入后分别记录检索与生成结果。多模态是待实现的后续实验。

## 完成标准

5 项测试全部通过，3 个合成来源案例全部通过；能展示一条失败案例与分析，不能把此基线扩写为未经测量的提升百分比。

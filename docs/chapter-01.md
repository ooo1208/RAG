# 第 1 章：文档读取与证据位置

这六章是对本次已有原创教学代码重新编排的学习提交，不是官方课程章节或历史开发时间的还原。可在当前仓库运行，也可用 `git switch --detach chapter-01` 查看本章快照；返回最新版本用 `git switch main`。

## 目标

理解文档类型与页码；确认输入资料都是合成材料。

## 读码

`pages`：TXT/Markdown/CSV 按原始文本读取；PDF 按页提取文字。CSV 当前按文本处理，不是结构化表格解析。空白扫描 PDF 会明确报错。

## 运行

在仓库根目录，使用 Python 3.11 或 3.12：

```shell
python rag_lab.py read data/procurement.md
```

## 练习

创建一份两页的文本 PDF，对照返回页码与原文；扫描件失败时记录为什么需要 OCR。可选 PDF 依赖安装：`python -m pip install pypdf`。

## 完成标准

读出合成制度，并能说明当前支持文本 PDF，不支持扫描件 OCR；不把读取成功当成已完成检索。

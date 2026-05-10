---
name: cwnu-cs-report
description: "西华师范大学计算机学院实验报告生成工具。当用户需要生成、填写、或完成西华师范大学计算机学院的实验报告时使用此 skill。支持多语言（Python、Java、C、C++），零外部依赖，适用于 Claude Code、Codex、OpenClaw、扣子等所有 AI 平台。支持自动填充表头信息、实验目的、实验原理、核心代码、运行截图、问题及解决办法、心得体会等所有报告栏目。"
---

# 西华师范大学计算机学院实验报告

## 概述

本 skill 用于快速生成西华师范大学计算机学院的标准实验报告（.docx 格式）。**零外部依赖**，仅使用 Python 标准库（zipfile、json、os），适用于任何支持 Python 的 AI 平台。

支持多语言：Python、Java、C、C++。

## 目录结构

```
cwnu-cs-report/
  ├── SKILL.md                          # 本文件
  ├── templates/
  │   ├── 实验报告模板.doc               # 原始模板（.doc 格式，备用）
  │   └── 实验报告模板.docx              # 标准模板（推荐使用）
  └── scripts/
      ├── report_generator.py            # 纯Python生成器（零依赖，推荐）
      └── fill_report.py                 # 旧版填充脚本（需docx skill）
```

## 模板文件说明

**模板位置**：`templates/实验报告模板.docx`，clone 本 skill 后即可直接使用。

**使用前确认**：
1. 检查 `templates/` 目录下是否存在 `实验报告模板.docx`
2. 如果只有 `实验报告模板.doc`，需先转换：`soffice --headless --convert-to docx templates/实验报告模板.doc --outdir templates/`

---

## 自动询问流程（强制）

当检测到用户需要生成实验报告时，**必须先通过 AskUserQuestion 工具**收集以下信息。

> **重要原则**：
> - Skill 中**不存储**任何学生的个人信息（姓名、学号、班级等）
> - Skill 中**不存储**任何课程信息（课程名称、指导老师等）
> - **每次对话都必须询问**用户，或从对话上下文中提取
> - 以下所有字段都是**必填**的，缺一不可

### 第一步：收集必要信息

使用 AskUserQuestion 工具，分批询问以下信息：

**批次1 - 课程与实验信息：**

| 问题 | 说明 | 必填 |
|------|------|------|
| 课程名称 | 如"Java程序设计"、"算法分析与程序设计"、"C语言"等 | ✅ 必填 |
| 实验名称/主题 | 如"类的继承"、"0/1背包问题"等 | ✅ 必填 |
| 实验日期 | 具体日期，如"2026年5月8日" | ✅ 必填 |
| 指导老师 | 老师姓名，如用户未提供可留空 | 可选 |

**批次2 - 学生信息：**

| 问题 | 说明 | 必填 |
|------|------|------|
| 学生姓名 | 文本输入 | ✅ 必填 |
| 学号 | 文本输入 | ✅ 必填 |
| 年级 | 如"2024" | ✅ 必填 |
| 班级 | 如"六" | ✅ 必填 |

**批次3 - 实验配置：**

| 问题 | 选项 | 必填 |
|------|------|------|
| 编程语言 | Python / Java / C / C++ / 其他 | ✅ 必填 |
| 代码风格 | 大学生水平（推荐）/ 最优实践 / 简洁版 | ✅ 必填 |
| 实验内容来源 | 用户上传图片 / 用户直接提供代码 / AI根据主题生成 | ✅ 必填 |

### 第二步：确认信息

在开始生成之前，向用户确认所有信息是否正确：

```
请确认以下信息：
- 课程：算法分析与程序设计
- 实验：实验4 0/1背包问题
- 日期：2026年5月8日
- 姓名：张林
- 学号：202413140617
- 年级：2024
- 班级：六
- 语言：Python
- 风格：大学生水平
```

### 信息提取规则

- 如果用户在对话中已经提供了某项信息，**不要重复询问**，直接使用
- 如果用户只说了"老样子"，**必须回顾对话历史**找到之前使用的信息
- 如果信息不完整，**必须询问缺失的字段**，不能猜测或留空
- 指导老师是唯一可选字段，用户未提供时留空即可

---

## 完整工作流程（零依赖版）

### 第一步：解压模板

```bash
python scripts/report_generator.py unpack templates/实验报告模板.docx /tmp/work/report/
```

或手动解压：
```python
import zipfile
zipfile.ZipFile('实验报告模板.docx').extractall('/tmp/work/report/')
```

### 第二步：编写代码

根据用户选择的编程语言和代码风格编写代码。

**代码风格指南：**

| 风格 | Python | Java | C/C++ |
|------|--------|------|-------|
| **大学生水平** | 有中文注释、函数封装、符合PEP8、不过度设计 | 类结构清晰、main方法、基本异常处理、简洁注释 | 标准头文件、main函数、基本错误检查、中文注释 |
| **最优实践** | 类型注解、异常处理、模块化、docstring | 设计模式、接口抽象、完整Javadoc、资源管理 | 内存管理、宏定义、多文件组织、错误处理完善 |
| **简洁版** | 单文件、全局变量、少注释、能跑就行 | 一个类搞定、System.out直接输出、最少注释 | 全局变量、printf直接输出、最少注释 |

### 第三步：生成运行截图

**方式1：浏览器渲染（推荐）**
1. 创建终端风格 HTML（见下方模板）
2. 启动 HTTP 服务器：`python3 -m http.server 8766`
3. 用浏览器工具打开并截图
4. 保存为 PNG

**终端 HTML 模板（支持中文）：**
```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400&display=swap" rel="stylesheet">
<style>
body {
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Consolas', 'Noto Sans SC', 'Courier New', monospace;
  font-size: 14px;
  padding: 20px;
  margin: 0;
  white-space: pre;
  line-height: 1.5;
}
</style>
</head>
<body>========================================
  实验名称
========================================

运行输出内容...

========================================</body>
</html>
```

> **重要**：必须包含 `Noto Sans SC` 字体链接，否则在某些平台上中文会显示乱码。

**方式2：用户自己提供截图**
- 用户上传截图文件
- 直接使用，跳过渲染步骤

**方式3：纯文本（无截图）**
- 如果平台不支持浏览器，可以用代码实际运行输出代替截图
- 将输出保存为文本文件，后续手动插入

截图保存到：`/tmp/work/report/word/media/run_result.png`

### 第四步：编写配置 JSON

```json
{
  "header": {
    "grade": "2024",
    "class_name": "六",
    "name": "张林",
    "student_id": "202413140617",
    "year": "2025",
    "month": "5",
    "day": "1",
    "teacher": "罗建"
  },
  "course_name": "Java程序设计",
  "experiment_name": "实验3 类的继承",
  "purpose": ["1. 目的第一条", "2. 目的第二条", "3. 目的第三条", "4. 目的第四条"],
  "equipment": "个人计算机一台，JDK 8+，Eclipse/IntelliJ IDEA开发环境。",
  "principle": ["一、实验原理", "", "原理内容...", "", "二、核心代码"],
  "code_part1": ["代码第一行", "代码第二行", "..."],
  "code_part2": ["代码续行", "..."],
  "problems": ["1. 问题描述及解决办法...", "", "2. 问题描述及解决办法...", "", "3. 问题描述及解决办法..."],
  "experience": ["心得第一段...", "", "心得第二段...", "", "心得第三段..."]
}
```

### 第五步：运行填充脚本

```bash
python scripts/report_generator.py fill /tmp/work/report/ config.json
```

### 第六步：打包生成最终 docx

```bash
python scripts/report_generator.py pack /tmp/work/report/ output.docx
```

或手动打包：
```python
import zipfile, os
with zipfile.ZipFile('output.docx', 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk('/tmp/work/report/'):
        for f in files:
            path = os.path.join(root, f)
            z.write(path, os.path.relpath(path, '/tmp/work/report/'))
```

### 第七步：验证（可选）

如果有 LibreOffice：
```bash
soffice --headless --convert-to pdf output.docx
```

如果没有，可以跳过验证，直接交付 .docx 文件。

---

## 配置 JSON 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `header.grade` | string | 是 | 年级，如 "2024" |
| `header.class_name` | string | 是 | 班级，如 "六" |
| `header.name` | string | 是 | 姓名 |
| `header.student_id` | string | 是 | 学号 |
| `header.year` | string | 是 | 年份 |
| `header.month` | string | 是 | 月份 |
| `header.day` | string | 是 | 日期 |
| `header.teacher` | string | 否 | 指导老师 |
| `course_name` | string | 是 | 课程名称 |
| `experiment_name` | string | 是 | 实验名称 |
| `purpose` | string[] | 是 | 实验目的（每条一个元素） |
| `equipment` | string | 是 | 实验仪器和器材 |
| `principle` | string[] | 是 | 实验原理（每行一个元素，空行用 ""） |
| `code_part1` | string[] | 是 | 核心代码第一部分 |
| `code_part2` | string[] | 是 | 核心代码第二部分 |
| `problems` | string[] | 是 | 问题及解决办法 |
| `experience` | string[] | 是 | 实验心得体会 |
| `image_rid` | string | 否 | 图片关系 ID，默认 "rId4" |

---

## 多语言代码风格详细指南

### Python

**大学生水平：**
```python
def knapsack_01(values, weights, capacity):
    n = len(values)  # 物品数量
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i-1] > w:
                dp[i][w] = dp[i-1][w]
            else:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-weights[i-1]] + values[i-1])
    return dp[n][capacity]
```

**最优实践：**
```python
from typing import List

def knapsack_01(values: List[int], weights: List[int], capacity: int) -> int:
    """0/1背包问题 - 动态规划求解"""
    if not values or capacity <= 0:
        return 0
    n = len(values)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        current_wt, current_val = weights[i-1], values[i-1]
        for w in range(1, capacity + 1):
            if current_wt > w:
                dp[i][w] = dp[i-1][w]
            else:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-current_wt] + current_val)
    return dp[n][capacity]
```

### Java

**大学生水平：**
```java
public class Father {
    String xing = "张";
    String name = "某";
    int age = 40;

    public void intr() {
        System.out.println("名字：" + xing + name);
        System.out.println("年龄：" + age);
    }
}
```

**最优实践：**
```java
public class Father {
    private String xing;
    private String name;
    private int age;

    public Father(String xing, String name, int age) {
        this.xing = xing;
        this.name = name;
        this.age = age;
    }

    public void display() {
        System.out.printf("名字：%s%s%n", xing, name);
        System.out.printf("年龄：%d%n", age);
    }
}
```

### C/C++

**大学生水平：**
```c
#include <stdio.h>

int main() {
    int arr[] = {5, 3, 8, 1, 9};
    int n = 5;
    // 冒泡排序
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            if (arr[j] > arr[j+1]) {
                int temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
            }
        }
    }
    for (int i = 0; i < n; i++)
        printf("%d ", arr[i]);
    return 0;
}
```

**最优实践：**
```c
#include <stdio.h>
#include <stdlib.h>

void bubble_sort(int arr[], int n) {
    if (arr == NULL || n <= 1) return;
    for (int i = 0; i < n - 1; i++) {
        int swapped = 0;
        for (int j = 0; j < n - 1 - i; j++) {
            if (arr[j] > arr[j+1]) {
                int temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
                swapped = 1;
            }
        }
        if (!swapped) break;  // 优化：已有序则提前退出
    }
}
```

---

## 不同语言的实验仪器描述参考

| 语言 | 实验仪器描述 |
|------|-------------|
| Python | 个人计算机一台，Python 3.x 运行环境。 |
| Java | 个人计算机一台，JDK 8+，Eclipse/IntelliJ IDEA开发环境。 |
| C | 个人计算机一台，GCC编译器，Code::Blocks/Dev-C++开发环境。 |
| C++ | 个人计算机一台，G++编译器，Code::Blocks/Visual Studio开发环境。 |

---

## 模板结构说明

模板是一个标准 A4 页面的表格文档，结构如下：

| 行 | trHeight | 标签 | 内容区 |
|----|----------|------|--------|
| 0 | 786 | 课程名称 / 实验名称 | 两个独立单元格 |
| 1 | - | 实验目的 | gridSpan=3 合并单元格 |
| 2 | - | 实验仪器和器材 | gridSpan=3 合并单元格 |
| 3 | 6276 | 实验内容（第一部分） | gridSpan=3，含实验原理+代码前半 |
| 4 | 576 | 空分隔行 | 全宽空行 |
| 5 | 7452 | 实验内容（第二部分） | gridSpan=3，含代码后半 |
| 6 | 5626 | 问题及解决办法 | gridSpan=3 |
| 7 | 8628 | 运行结果截图 | gridSpan=3，插入图片 |
| 8 | 4810 | 实验心得体会 | gridSpan=3 |

---

## 平台兼容性

| 平台 | 零依赖版 | docx skill版 | 说明 |
|------|---------|-------------|------|
| Claude Code | ✅ | ✅ | 两种方式都支持 |
| Codex | ✅ | ❌ | 仅零依赖版 |
| OpenClaw | ✅ | ❌ | 仅零依赖版 |
| Hermes Agent | ✅ | ❌ | 仅零依赖版 |
| 扣子 | ✅ | ❌ | 仅零依赖版 |
| SOLO | ✅ | ✅ | 两种方式都支持 |

**推荐**：始终优先使用零依赖版（`report_generator.py`），确保最大兼容性。

---

## 注意事项

1. **零依赖**：`report_generator.py` 仅使用 Python 标准库，不需要安装任何第三方包
2. **模板格式**：使用预转换的 `.docx` 模板，不需要 soffice 转换
3. **XML 转义**：脚本已内置 `xml_escape`，JSON 中的 `<`、`>`、`&` 会自动转义
4. **截图要求**：截图必须放在 `word/media/run_result.png`，脚本会自动注册图片资源
5. **代码分行**：`code_part1` 和 `code_part2` 中每行代码是数组的一个元素
6. **空行处理**：原理、问题、心得中的空行用空字符串 `""` 表示
7. **文件命名**：建议 `学号+姓名+课程简称+实验编号.docx`
8. **指导老师**：如果模板中没有指导老师字段，`header.teacher` 会被忽略

---

## report_generator.py 命令行用法

```bash
# 解压模板
python scripts/report_generator.py unpack <docx模板路径> <输出目录>

# 填充内容
python scripts/report_generator.py fill <解压目录> <配置JSON路径>

# 打包生成docx
python scripts/report_generator.py pack <解压目录> <输出docx路径>
```

也可以作为 Python 模块导入使用：
```python
from report_generator import unpack_docx, fill_report, pack_docx

unpack_docx('template.docx', '/tmp/work/report/')
fill_report('/tmp/work/report/', config)
pack_docx('/tmp/work/report/', 'output.docx')
```

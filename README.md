# 西华师范大学计算机学院实验报告生成器

> **作者**: 张林 (202413140617)  
> **创建时间**: 2025年5月  
> **适用对象**: 西华师范大学计算机学院学弟学妹们  
> **适用课程**: Java程序设计、C语言、C++、Python、算法设计与分析等实验课程

---

## 这是什么？

这是一个**零外部依赖**的实验报告自动生成工具，只需要 Python 标准库就能运行。支持生成西华师范大学计算机学院标准格式的实验报告（.docx）。

## 能用在哪些 AI 平台上？

| 平台 | 支持情况 | 说明 |
|------|---------|------|
| Claude Code | ✅ 完美支持 | 推荐 |
| Codex | ✅ 完美支持 | |
| OpenClaw | ✅ 完美支持 | |
| Hermes Agent | ✅ 完美支持 | |
| 扣子 (Coze) | ✅ 完美支持 | |
| SOLO | ✅ 完美支持 | |
| 任何支持 Python 的 AI | ✅ 都能用 | |

**核心优势**: 不依赖任何外部工具（如 soffice、docx skill），纯 Python 实现，随处可用。

---

## 快速开始

### 1. 获取本工具

```bash
git clone https://github.com/your-repo/cwnu-cs-report.git
cd cwnu-cs-report
```

### 2. 准备模板

检查 `templates/` 目录下是否有 `实验报告模板.docx`：
- ✅ 有 → 直接用
- ❌ 只有 `.doc` → 需要转换（见下方）

**转换方法**（如果只有 .doc）：
```bash
soffice --headless --convert-to docx templates/实验报告模板.doc --outdir templates/
```

### 3. 使用流程

告诉你的 AI 助手：
> "我要生成实验报告，使用 cwnu-cs-report skill"

AI 会自动：
1. 询问编程语言（Python/Java/C/C++）
2. 询问学生信息（姓名、学号、班级、老师）
3. 询问课程和实验内容
4. 生成代码、截图、填充报告
5. 输出最终的 .docx 文件

---

## 目录结构

```
cwnu-cs-report/
├── README.md                    # 本文件
├── SKILL.md                     # 详细使用文档（给 AI 看的）
├── templates/
│   ├── 实验报告模板.doc          # 原始模板（.doc格式）
│   └── 实验报告模板.docx         # 标准模板（推荐使用）
└── scripts/
    ├── report_generator.py       # 纯Python生成器（零依赖，推荐）
    └── fill_report.py            # 旧版（需docx skill，不推荐）
```

---

## 支持的语言和代码风格

| 语言 | 大学生水平 | 最优实践 | 简洁版 |
|------|-----------|---------|--------|
| **Python** | ✅ 有注释、函数封装、符合PEP8 | ✅ 类型注解、异常处理 | ✅ 能跑就行 |
| **Java** | ✅ 类结构清晰、main方法、基本异常处理 | ✅ 设计模式、完整Javadoc | ✅ 一个类搞定 |
| **C** | ✅ 标准头文件、main函数、中文注释 | ✅ 内存管理、多文件组织 | ✅ printf直接输出 |
| **C++** | ✅ 基础语法、简单类 | ✅ STL、异常处理 | ✅ 全局变量 |

**推荐**: 大学生水平（最符合实验报告要求）

---

## 手动使用（高级用户）

如果你不想通过 AI，也可以手动操作：

```bash
# 1. 解压模板
python scripts/report_generator.py unpack templates/实验报告模板.docx ./work/

# 2. 编写 config.json（实验内容配置）
# 参考 SKILL.md 中的 JSON 格式

# 3. 填充内容
python scripts/report_generator.py fill ./work/ config.json

# 4. 打包生成 docx
python scripts/report_generator.py pack ./work/ 输出报告.docx
```

---

## 常见问题

**Q: 没有 LibreOffice 怎么转换 .doc？**  
A: 可以跳过转换，直接用现有的 `.docx` 模板，或者让 AI 帮你在线转换。

**Q: 截图怎么生成？**  
A: AI 会自动用浏览器渲染终端风格 HTML 并截图，不需要你手动操作。

**Q: 能改模板样式吗？**  
A: 可以，直接修改 `templates/实验报告模板.docx`，但建议先备份原模板。

**Q: 其他学校能用吗？**  
A: 模板是西华师范大学的格式，其他学校可能需要调整模板。

---

## 更新计划

- [ ] 支持更多课程（数据结构、操作系统、计算机网络等）
- [ ] 添加更多编程语言（Go、Rust、JavaScript 等）
- [ ] 支持自定义模板上传
- [ ] 一键生成多个实验报告
- [ ] 实验报告查重检测

**欢迎贡献**: 如果你有好想法或改进，欢迎提交 PR！

---

## 致谢

感谢西华师范大学计算机学院的老师们，以及一起折腾实验报告的同学们。

**祝学弟学妹们实验顺利，报告一次过！** 🎉

---

*最后更新: 2025年5月*

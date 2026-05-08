#!/usr/bin/env python3
"""
西华师范大学计算机学院实验报告 - 通用填充脚本

用法:
  python fill_report.py <unpacked_dir> <config_json>

功能:
  将空白模板解包后，通过本脚本填充所有报告内容。

参数说明:
  unpacked_dir  : unpack.py 解包后的目录路径
  config_json   : 报告内容配置 JSON 文件路径

依赖:
  - 需要先运行 unpack.py 解包模板
  - 需要将截图 PNG 放到 unpacked_dir/word/media/run_result.png
"""

import os
import sys
import json
import argparse
from xml.sax.saxutils import escape as xml_escape


# ============================================================
# XML 辅助函数
# ============================================================

def find_cell(xml, start_marker):
    """在 start_marker 之后找到 gridSpan=3 的合并单元格"""
    idx = xml.find(start_marker)
    if idx < 0:
        return None
    idx_gs = xml.find('<w:gridSpan w:val="3"/>', idx)
    if idx_gs < 0:
        return None
    tcpr_end = xml.find('</w:tcPr>', idx_gs)
    if tcpr_end < 0:
        return None
    content_start = tcpr_end + len('</w:tcPr>')
    search_from = idx_gs
    depth = 0
    while True:
        next_open = xml.find('<w:tc>', search_from)
        next_close = xml.find('</w:tc>', search_from)
        if next_close == -1:
            return None
        if next_open != -1 and next_open < next_close:
            depth += 1
            search_from = next_open + 5
        else:
            if depth == 0:
                return (idx_gs, content_start, next_close)
            depth -= 1
            search_from = next_close + 6


def replace_cell(xml, start_marker, new_content_xml):
    """替换 start_marker 后的 gridSpan=3 单元格内容"""
    result = find_cell(xml, start_marker)
    if result is None:
        print(f"  WARNING: 未找到 '{start_marker}' 后的单元格")
        return xml
    idx_gs, content_start, tc_end = result
    header = xml[idx_gs:content_start]
    new_cell = header + '\n' + new_content_xml + '\n        </w:tc>'
    return xml[:idx_gs] + new_cell + xml[tc_end + len('</w:tc>'):]


def make_text_para(text, font_size=21, font_name=None):
    """创建一个文本段落 XML"""
    font_attr = ''
    if font_name:
        font_attr = f'<w:rFonts w:ascii="{font_name}" w:hAnsi="{font_name}" w:eastAsia="{font_name}"/>'
    return f'''          <w:p>
            <w:pPr>
              <w:pStyle w:val="Normal"/>
              <w:snapToGrid w:val="false"/>
              <w:rPr>
                <w:sz w:val="{font_size}"/>
                <w:szCs w:val="{font_size}"/>
              </w:rPr>
            </w:pPr>
            <w:r>
              <w:rPr>
                <w:sz w:val="{font_size}"/>
                <w:szCs w:val="{font_size}"/>
                {font_attr}
              </w:rPr>
              <w:t xml:space="preserve">{xml_escape(text)}</w:t>
            </w:r>
          </w:p>'''


def make_code_para(text):
    """创建一个代码段落 XML（Consolas 字体，小字号）"""
    return f'''          <w:p>
            <w:pPr>
              <w:pStyle w:val="Normal"/>
              <w:snapToGrid w:val="false"/>
              <w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>
              <w:rPr>
                <w:sz w:val="18"/>
                <w:szCs w:val="18"/>
              </w:rPr>
            </w:pPr>
            <w:r>
              <w:rPr>
                <w:sz w:val="18"/>
                <w:szCs w:val="18"/>
                <w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:eastAsia="Consolas"/>
              </w:rPr>
              <w:t xml:space="preserve">{xml_escape(text)}</w:t>
            </w:r>
          </w:p>'''


def make_image_para(r_id="rId4", width=5800000, height=4200000):
    """创建一个包含图片的段落 XML"""
    return f'''          <w:p>
            <w:pPr>
              <w:pStyle w:val="Normal"/>
              <w:snapToGrid w:val="false"/>
              <w:rPr>
                <w:sz w:val="24"/>
                <w:szCs w:val="24"/>
              </w:rPr>
            </w:pPr>
            <w:r>
              <w:rPr>
                <w:sz w:val="24"/>
                <w:szCs w:val="24"/>
              </w:rPr>
              <w:drawing>
                <wp:inline distT="0" distB="0" distL="0" distR="0" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
                  <wp:extent cx="{width}" cy="{height}"/>
                  <wp:docPr id="1" name="Picture 1"/>
                  <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
                    <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                      <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
                        <pic:nvPicPr>
                          <pic:cNvPr id="0" name="run_result.png"/>
                          <pic:cNvPicPr/>
                        </pic:nvPicPr>
                        <pic:blipFill>
                          <a:blip r:embed="{r_id}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>
                          <a:stretch>
                            <a:fillRect/>
                          </a:stretch>
                        </pic:blipFill>
                        <pic:spPr>
                          <a:xfrm>
                            <a:off x="0" y="0"/>
                            <a:ext cx="{width}" cy="{height}"/>
                          </a:xfrm>
                          <a:prstGeom prst="rect">
                            <a:avLst/>
                          </a:prstGeom>
                        </pic:spPr>
                      </pic:pic>
                    </a:graphicData>
                  </a:graphic>
                </wp:inline>
              </w:drawing>
            </w:r>
          </w:p>'''


# ============================================================
# 各区域填充函数
# ============================================================

def fill_header(xml, info):
    """填充表头信息（年级、班级、姓名、学号、日期）"""
    print("填充表头信息...")

    if info.get('grade'):
        xml = xml.replace(
            '<w:t xml:space="preserve">           </w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>级</w:t>',
            f'<w:t xml:space="preserve">{info["grade"]:10s}</w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>级</w:t>', 1)

    if info.get('class_name'):
        xml = xml.replace(
            '<w:t xml:space="preserve">        </w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>班</w:t>',
            f'<w:t xml:space="preserve">{info["class_name"]:8s}</w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>班</w:t>', 1)

    if info.get('name'):
        xml = xml.replace(
            '<w:t xml:space="preserve">           </w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:rFonts w:cs="Calibri" w:eastAsia="Calibri"/>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t xml:space="preserve">  </w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>学号</w:t>',
            f'<w:t xml:space="preserve">{info["name"]:10s}</w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:rFonts w:cs="Calibri" w:eastAsia="Calibri"/>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t xml:space="preserve">  </w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>学号</w:t>', 1)

    if info.get('student_id'):
        xml = xml.replace(
            '<w:t xml:space="preserve">          </w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:rFonts w:cs="Calibri" w:eastAsia="Calibri"/>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t xml:space="preserve">  </w:t>\n      </w:r>\n    </w:p>\n    <w:p>\n      <w:pPr>\n        <w:pStyle w:val="Normal"/>\n        <w:rPr/>\n      </w:pPr>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>成员</w:t>',
            f'<w:t xml:space="preserve">{info["student_id"]}</w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:rFonts w:cs="Calibri" w:eastAsia="Calibri"/>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t xml:space="preserve">  </w:t>\n      </w:r>\n    </w:p>\n    <w:p>\n      <w:pPr>\n        <w:pStyle w:val="Normal"/>\n        <w:rPr/>\n      </w:pPr>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>成员</w:t>', 1)

    if info.get('year'):
        xml = xml.replace(
            '<w:t xml:space="preserve">     </w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>年</w:t>',
            f'<w:t xml:space="preserve">{str(info["year"]):5s}</w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>年</w:t>', 1)

    if info.get('month'):
        xml = xml.replace(
            '<w:t xml:space="preserve">    </w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>月</w:t>',
            f'<w:t xml:space="preserve">{str(info["month"]):4s}</w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>月</w:t>', 1)

    if info.get('day'):
        xml = xml.replace(
            '<w:t xml:space="preserve">   </w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>日</w:t>',
            f'<w:t xml:space="preserve">{str(info["day"]):3s}</w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t>日</w:t>', 1)

    # 指导教师
    if info.get('teacher'):
        xml = xml.replace(
            '<w:t>指导教师</w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:rFonts w:cs="Calibri" w:eastAsia="Calibri"/>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t xml:space="preserve"> </w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:rFonts w:cs="Calibri" w:eastAsia="Calibri"/>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n          <w:u w:val="single"/>\n        </w:rPr>\n        <w:t xml:space="preserve">            </w:t>\n      </w:r>',
            f'<w:t>指导教师</w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:rFonts w:cs="Calibri" w:eastAsia="Calibri"/>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n        </w:rPr>\n        <w:t xml:space="preserve"> </w:t>\n      </w:r>\n      <w:r>\n        <w:rPr>\n          <w:rFonts w:cs="Calibri" w:eastAsia="Calibri"/>\n          <w:b/>\n          <w:sz w:val="24"/>\n          <w:szCs w:val="24"/>\n          <w:u w:val="single"/>\n        </w:rPr>\n        <w:t xml:space="preserve">{info["teacher"]:12s}</w:t>\n      </w:r>', 1)

    print("  表头信息填充完成。")
    return xml


def fill_course_and_experiment(xml, course_name, experiment_name):
    """填充课程名称和实验名称"""
    print("填充课程名称和实验名称...")

    if course_name:
        xml = xml.replace(
            '<w:t xml:space="preserve">                   </w:t>\n            </w:r>\n          </w:p>\n        </w:tc>\n        <w:tc>\n          <w:tcPr>\n            <w:tcW w:w="1417"',
            f'<w:t>{xml_escape(course_name)}</w:t>\n            </w:r>\n          </w:p>\n        </w:tc>\n        <w:tc>\n          <w:tcPr>\n            <w:tcW w:w="1417"', 1)

    if experiment_name:
        old = '''            <w:r>
              <w:rPr>
                <w:sz w:val="24"/>
                <w:szCs w:val="24"/>
              </w:rPr>
            </w:r>
          </w:p>
        </w:tc>
      </w:tr>
      <w:tr>
        <w:trPr/>'''
        new = f'''            <w:r>
              <w:rPr>
                <w:sz w:val="24"/>
                <w:szCs w:val="24"/>
              </w:rPr>
              <w:t>{xml_escape(experiment_name)}</w:t>
            </w:r>
          </w:p>
        </w:tc>
      </w:tr>
      <w:tr>
        <w:trPr/>'''
        xml = xml.replace(old, new, 1)

    print("  课程名称和实验名称填充完成。")
    return xml


def fill_purpose(xml, purposes):
    """填充实验目的"""
    print("填充实验目的...")
    content = '\n'.join(make_text_para(p) for p in purposes)
    xml = replace_cell(xml, '<w:t>的</w:t>', content)
    print("  实验目的填充完成。")
    return xml


def fill_equipment(xml, text):
    """填充实验仪器和器材"""
    print("填充实验仪器和器材...")
    content = make_text_para(text)
    xml = replace_cell(xml, '<w:t>器材</w:t>', content)
    print("  实验仪器和器材填充完成。")
    return xml


def fill_content_part1(xml, principle_lines, code_lines):
    """填充实验内容第一部分（实验原理 + 核心代码前半）"""
    print("填充实验内容（第一部分）...")
    principle_xml = '\n'.join(make_text_para(line, font_name="宋体") for line in principle_lines)
    code_xml = '\n'.join(make_code_para(line) for line in code_lines)
    content = principle_xml + '\n' + code_xml
    xml = replace_cell(xml, '<w:trHeight w:val="6276"', content)
    print("  实验内容第一部分填充完成。")
    return xml


def fill_content_part2(xml, code_lines):
    """填充实验内容第二部分（核心代码后半）"""
    print("填充实验内容（第二部分）...")
    content = '\n'.join(make_code_para(line) for line in code_lines)
    xml = replace_cell(xml, '<w:trHeight w:val="7452"', content)
    print("  实验内容第二部分填充完成。")
    return xml


def fill_problems(xml, problems):
    """填充问题及解决办法"""
    print("填充问题及解决办法...")
    content = '\n'.join(make_text_para(p, font_name="宋体") for p in problems)
    xml = replace_cell(xml, '<w:trHeight w:val="5626"', content)
    print("  问题及解决办法填充完成。")
    return xml


def fill_screenshot(xml, unpacked_dir, r_id="rId4"):
    """填充运行结果截图"""
    print("填充运行结果截图...")

    rels_path = os.path.join(unpacked_dir, "word", "_rels", "document.xml.rels")
    with open(rels_path, 'r', encoding='utf-8') as f:
        rels = f.read()
    new_rel = f'<Relationship Id="{r_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/run_result.png"/>'
    if new_rel not in rels:
        rels = rels.replace('</Relationships>', new_rel + '\n</Relationships>')
        with open(rels_path, 'w', encoding='utf-8') as f:
            f.write(rels)

    ct_path = os.path.join(unpacked_dir, "[Content_Types].xml")
    with open(ct_path, 'r', encoding='utf-8') as f:
        ct = f.read()
    if 'Extension="png"' not in ct:
        ct = ct.replace('</Types>', '<Default Extension="png" ContentType="image/png"/>\n</Types>')
        with open(ct_path, 'w', encoding='utf-8') as f:
            f.write(ct)

    content = make_image_para(r_id=r_id)
    xml = replace_cell(xml, '<w:trHeight w:val="8628"', content)
    print("  运行结果截图填充完成。")
    return xml


def fill_experience(xml, experiences):
    """填充实验心得体会"""
    print("填充实验心得体会...")
    content = '\n'.join(make_text_para(e, font_name="宋体") for e in experiences)
    xml = replace_cell(xml, '<w:trHeight w:val="4810"', content)
    print("  实验心得体会填充完成。")
    return xml


def main():
    parser = argparse.ArgumentParser(description='填充西华师范大学计算机学院实验报告')
    parser.add_argument('unpacked_dir', help='解包后的模板目录路径')
    parser.add_argument('config_json', help='报告内容配置 JSON 文件路径')
    args = parser.parse_args()

    xml_path = os.path.join(args.unpacked_dir, "word", "document.xml")

    with open(args.config_json, 'r', encoding='utf-8') as f:
        config = json.load(f)

    with open(xml_path, 'r', encoding='utf-8') as f:
        xml = f.read()

    xml = fill_header(xml, config.get('header', {}))
    xml = fill_course_and_experiment(xml, config.get('course_name', ''), config.get('experiment_name', ''))
    xml = fill_purpose(xml, config.get('purpose', []))
    xml = fill_equipment(xml, config.get('equipment', ''))
    xml = fill_content_part1(xml, config.get('principle', []), config.get('code_part1', []))
    xml = fill_content_part2(xml, config.get('code_part2', []))
    xml = fill_problems(xml, config.get('problems', []))
    xml = fill_screenshot(xml, args.unpacked_dir, config.get('image_rid', 'rId4'))
    xml = fill_experience(xml, config.get('experience', []))

    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(xml)

    print("\n所有内容填充完成！")


if __name__ == '__main__':
    main()

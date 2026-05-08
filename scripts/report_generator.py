#!/usr/bin/env python3
"""
西华师范大学计算机学院实验报告生成器 - 纯Python实现
不依赖任何外部平台或docx skill
"""

import zipfile
import os
import shutil
import json
from xml.sax.saxutils import escape as xml_escape


def unpack_docx(docx_path, output_dir):
    """解压docx文件"""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    with zipfile.ZipFile(docx_path, 'r') as z:
        z.extractall(output_dir)
    print(f"解压完成: {docx_path} -> {output_dir}")


def pack_docx(source_dir, output_docx):
    """打包为docx文件"""
    with zipfile.ZipFile(output_docx, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                z.write(file_path, arcname)
    print(f"打包完成: {source_dir} -> {output_docx}")


def read_xml(path):
    """读取XML文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_xml(path, content):
    """写入XML文件"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def fill_header(xml, info):
    """填充表头信息"""
    print("填充表头信息...")
    
    # 年级 - 使用更灵活的匹配
    if info.get('grade'):
        old_pattern = '<w:t xml:space="preserve">           </w:t>'
        if old_pattern in xml:
            xml = xml.replace(old_pattern, f'<w:t xml:space="preserve">{info["grade"]:10s}</w:t>', 1)
            print(f"  ✓ 年级: {info['grade']}")
        else:
            print(f"  ✗ 年级替换失败，未找到匹配模式")
    
    # 班级
    if info.get('class_name'):
        old_pattern = '<w:t xml:space="preserve">        </w:t>'
        if old_pattern in xml:
            xml = xml.replace(old_pattern, f'<w:t xml:space="preserve">{info["class_name"]:8s}</w:t>', 1)
            print(f"  ✓ 班级: {info['class_name']}")
        else:
            print(f"  ✗ 班级替换失败，未找到匹配模式")
    
    # 姓名
    if info.get('name'):
        # 尝试多种匹配模式
        patterns = [
            ('<w:t xml:space="preserve">           </w:t>', 10),
        ]
        replaced = False
        for pattern, width in patterns:
            if pattern in xml:
                xml = xml.replace(pattern, f'<w:t xml:space="preserve">{info["name"]:{width}s}</w:t>', 1)
                print(f"  ✓ 姓名: {info['name']}")
                replaced = True
                break
        if not replaced:
            print(f"  ✗ 姓名替换失败，未找到匹配模式")
    
    # 学号
    if info.get('student_id'):
        old_pattern = '<w:t xml:space="preserve">          </w:t>'
        if old_pattern in xml:
            xml = xml.replace(old_pattern, f'<w:t xml:space="preserve">{info["student_id"]}</w:t>', 1)
            print(f"  ✓ 学号: {info['student_id']}")
        else:
            print(f"  ✗ 学号替换失败，未找到匹配模式")
    
    # 日期
    if info.get('year'):
        old_pattern = '<w:t xml:space="preserve">     </w:t>'
        if old_pattern in xml:
            xml = xml.replace(old_pattern, f'<w:t xml:space="preserve">{str(info["year"]):5s}</w:t>', 1)
            print(f"  ✓ 年份: {info['year']}")
    
    if info.get('month'):
        old_pattern = '<w:t xml:space="preserve">    </w:t>'
        if old_pattern in xml:
            xml = xml.replace(old_pattern, f'<w:t xml:space="preserve">{str(info["month"]):4s}</w:t>', 1)
            print(f"  ✓ 月份: {info['month']}")
    
    if info.get('day'):
        old_pattern = '<w:t xml:space="preserve">   </w:t>'
        if old_pattern in xml:
            xml = xml.replace(old_pattern, f'<w:t xml:space="preserve">{str(info["day"]):3s}</w:t>', 1)
            print(f"  ✓ 日期: {info['day']}")
    
    # 指导教师
    if info.get('teacher'):
        old_pattern = '<w:t xml:space="preserve">            </w:t>'
        if old_pattern in xml:
            xml = xml.replace(old_pattern, f'<w:t xml:space="preserve">{info["teacher"]:12s}</w:t>', 1)
            print(f"  ✓ 指导老师: {info['teacher']}")
        else:
            print(f"  ✗ 指导老师替换失败，未找到匹配模式")
    
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


def make_text_para(text, font_size=21, font_name=None):
    """创建文本段落"""
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
    """创建代码段落"""
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


def find_cell(xml, start_marker):
    """查找合并单元格"""
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
    """替换单元格内容"""
    result = find_cell(xml, start_marker)
    if result is None:
        print(f"  WARNING: 未找到 '{start_marker}' 后的单元格")
        return xml
    idx_gs, content_start, tc_end = result
    header = xml[idx_gs:content_start]
    new_cell = header + '\n' + new_content_xml + '\n        </w:tc>'
    return xml[:idx_gs] + new_cell + xml[tc_end + len('</w:tc>'):]


def fill_purpose(xml, purposes):
    """填充实验目的"""
    print("填充实验目的...")
    content = '\n'.join(make_text_para(p) for p in purposes)
    xml = replace_cell(xml, '<w:t>的</w:t>', content)
    print("  实验目的填充完成。")
    return xml


def fill_equipment(xml, text):
    """填充实验仪器"""
    print("填充实验仪器和器材...")
    content = make_text_para(text)
    xml = replace_cell(xml, '<w:t>器材</w:t>', content)
    print("  实验仪器和器材填充完成。")
    return xml


def fill_content_part1(xml, principle_lines, code_lines):
    """填充实验内容第一部分"""
    print("填充实验内容（第一部分）...")
    principle_xml = '\n'.join(make_text_para(line, font_name="宋体") for line in principle_lines)
    code_xml = '\n'.join(make_code_para(line) for line in code_lines)
    content = principle_xml + '\n' + code_xml
    xml = replace_cell(xml, '<w:trHeight w:val="6276"', content)
    print("  实验内容第一部分填充完成。")
    return xml


def fill_content_part2(xml, code_lines):
    """填充实验内容第二部分"""
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
    
    # 注册图片关系
    rels_path = os.path.join(unpacked_dir, "word", "_rels", "document.xml.rels")
    with open(rels_path, 'r', encoding='utf-8') as f:
        rels = f.read()
    
    new_rel = f'<Relationship Id="{r_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/run_result.png"/>'
    if new_rel not in rels:
        rels = rels.replace('</Relationships>', new_rel + '\n</Relationships>')
        with open(rels_path, 'w', encoding='utf-8') as f:
            f.write(rels)
    
    # 注册 png 类型
    ct_path = os.path.join(unpacked_dir, "[Content_Types].xml")
    with open(ct_path, 'r', encoding='utf-8') as f:
        ct = f.read()
    if 'Extension="png"' not in ct:
        ct = ct.replace('</Types>', '<Default Extension="png" ContentType="image/png"/>\n</Types>')
        with open(ct_path, 'w', encoding='utf-8') as f:
            f.write(ct)
    
    # 插入图片
    width, height = 5800000, 4200000
    content = f'''          <w:p>
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


def fill_report(unpacked_dir, config):
    """主填充函数"""
    xml_path = os.path.join(unpacked_dir, "word", "document.xml")
    xml = read_xml(xml_path)
    
    # 依次填充各部分
    xml = fill_header(xml, config.get('header', {}))
    xml = fill_course_and_experiment(xml, config.get('course_name', ''), config.get('experiment_name', ''))
    xml = fill_purpose(xml, config.get('purpose', []))
    xml = fill_equipment(xml, config.get('equipment', ''))
    xml = fill_content_part1(xml, config.get('principle', []), config.get('code_part1', []))
    xml = fill_content_part2(xml, config.get('code_part2', []))
    xml = fill_problems(xml, config.get('problems', []))
    xml = fill_screenshot(xml, unpacked_dir, config.get('image_rid', 'rId4'))
    xml = fill_experience(xml, config.get('experience', []))
    
    write_xml(xml_path, xml)
    print("\n所有内容填充完成！")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("西华师范大学计算机学院实验报告生成器（零依赖版）")
        print()
        print("用法:")
        print("  python report_generator.py unpack <docx模板> <输出目录>")
        print("  python report_generator.py fill   <解压目录> <配置JSON>")
        print("  python report_generator.py pack   <解压目录> <输出docx>")
        print()
        print("示例:")
        print("  python report_generator.py unpack template.docx /tmp/report/")
        print("  python report_generator.py fill   /tmp/report/ config.json")
        print("  python report_generator.py pack   /tmp/report/ output.docx")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == 'unpack':
        if len(sys.argv) < 4:
            print("用法: python report_generator.py unpack <docx模板> <输出目录>")
            sys.exit(1)
        unpack_docx(sys.argv[2], sys.argv[3])
    
    elif command == 'fill':
        if len(sys.argv) < 4:
            print("用法: python report_generator.py fill <解压目录> <配置JSON>")
            sys.exit(1)
        with open(sys.argv[3], 'r', encoding='utf-8') as f:
            config = json.load(f)
        fill_report(sys.argv[2], config)
    
    elif command == 'pack':
        if len(sys.argv) < 4:
            print("用法: python report_generator.py pack <解压目录> <输出docx>")
            sys.exit(1)
        pack_docx(sys.argv[2], sys.argv[3])
    
    else:
        print(f"未知命令: {command}")
        print("可用命令: unpack, fill, pack")
        sys.exit(1)

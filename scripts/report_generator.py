#!/usr/bin/env python3
"""
西华师范大学计算机学院实验报告生成器 - 纯Python实现
不依赖任何外部平台或docx skill
"""

import zipfile
import os
import shutil
import json
import re
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


def find_underlined_placeholder_after(xml, label):
    """找到label后第一个带下划线的占位符，返回(start, end, spaces)或None"""
    idx = xml.find(f'<w:t>{label}</w:t>')
    if idx < 0:
        return None
    after = xml[idx + len(f'<w:t>{label}</w:t>'):]
    u_idx = after.find('<w:u w:val="single"/>')
    if u_idx < 0:
        return None
    after_u = after[u_idx:]
    ph = '<w:t xml:space="preserve">'
    p_idx = after_u.find(ph)
    if p_idx < 0:
        return None
    end_idx = after_u.find('</w:t>', p_idx)
    if end_idx < 0:
        return None
    spaces = after_u[p_idx + len(ph):end_idx]
    abs_start = idx + len(f'<w:t>{label}</w:t>') + u_idx + p_idx
    abs_end = idx + len(f'<w:t>{label}</w:t>') + u_idx + end_idx + len('</w:t>')
    return (abs_start, abs_end, spaces)


def find_underlined_placeholder_before(xml, label):
    """找到label前最后一个带下划线的占位符，返回(start, end, spaces)或None"""
    idx = xml.find(f'<w:t>{label}</w:t>')
    if idx < 0:
        return None
    before = xml[:idx]
    ph_tag = '<w:t xml:space="preserve">'
    end_tag = '</w:t>'
    search_end = len(before)
    while True:
        p_idx = before.rfind(ph_tag, 0, search_end)
        if p_idx < 0:
            return None
        e_idx = before.find(end_tag, p_idx)
        if e_idx < 0:
            return None
        spaces = before[p_idx + len(ph_tag):e_idx]
        check_start = max(0, p_idx - 300)
        context = before[check_start:p_idx]
        if '<w:u w:val="single"/>' in context:
            return (p_idx, e_idx + len(end_tag), spaces)
        search_end = p_idx


def find_first_placeholder_after(xml, label):
    """找到label后第一个占位符（不要求下划线），返回(start, end, spaces)或None"""
    idx = xml.find(f'<w:t>{label}</w:t>')
    if idx < 0:
        return None
    after = xml[idx + len(f'<w:t>{label}</w:t>'):]
    ph = '<w:t xml:space="preserve">'
    p_idx = after.find(ph)
    if p_idx < 0:
        return None
    end_idx = after.find('</w:t>', p_idx)
    if end_idx < 0:
        return None
    spaces = after[p_idx + len(ph):end_idx]
    abs_start = idx + len(f'<w:t>{label}</w:t>') + p_idx
    abs_end = idx + len(f'<w:t>{label}</w:t>') + end_idx + len('</w:t>')
    return (abs_start, abs_end, spaces)


def fill_header(xml, info):
    """填充表头信息 — 基于标签上下文定位占位符"""
    print("填充表头信息...")
    fields = [
        # (key, label, direction, default_width)
        ('grade',       '级',     'before', 11),
        ('class_name',  '班',     'before',  8),
        ('name',        '报告人姓名', 'after',  11),
        ('student_id',  '学号',    'after',  10),
        ('year',        '年',     'before',  5),
        ('month',       '月',     'before',  4),
        ('day',         '日',     'before',  3),
        ('teacher',     '指导教师', 'after',  12),
    ]
    for key, label, direction, dw in fields:
        val = info.get(key, '')
        if not val:
            continue
        val_str = str(val)
        found = None
        if direction == 'before':
            found = find_underlined_placeholder_before(xml, label)
        else:
            found = find_underlined_placeholder_after(xml, label)
        if found is None:
            print(f"  ✗ {key}: 未找到 '{label}' 前后的占位符")
            continue
        start, end, spaces = found
        width = len(spaces)
        new_text = f'<w:t xml:space="preserve">{val_str:{width}s}</w:t>'
        xml = xml[:start] + new_text + xml[end:]
        print(f"  ✓ {key}: {val_str}")
    print("  表头信息填充完成。")
    return xml


def fill_course_and_experiment(xml, course_name, experiment_name):
    """填充课程名称和实验名称 — 基于标签上下文定位"""
    print("填充课程名称和实验名称...")

    if course_name:
        found = find_first_placeholder_after(xml, '课程名称')
        if found:
            start, end, spaces = found
            width = len(spaces)
            new_text = f'<w:t xml:space="preserve">{xml_escape(course_name):{width}s}</w:t>'
            xml = xml[:start] + new_text + xml[end:]
            print(f"  ✓ 课程名称: {course_name}")
        else:
            print(f"  ✗ 课程名称: 未找到占位符")

    if experiment_name:
        label = '<w:t>实验名称</w:t>'
        idx = xml.find(label)
        if idx >= 0:
            after = xml[idx + len(label):]
            empty_r = '<w:r><w:rPr><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:r>'
            r_idx = after.find(empty_r)
            if r_idx >= 0:
                new_r = f'<w:r><w:rPr><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr><w:t>{xml_escape(experiment_name)}</w:t></w:r>'
                xml = xml[:idx + len(label)] + after[:r_idx] + new_r + after[r_idx + len(empty_r):]
                print(f"  ✓ 实验名称: {experiment_name}")
            else:
                print(f"  ✗ 实验名称: 未找到空占位")
        else:
            print(f"  ✗ 实验名称: 未找到标签")

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

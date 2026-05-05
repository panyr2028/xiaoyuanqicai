
import os
import re

def remove_comments(code):
    code = re.sub(r'"""[\s\S]*?"""', '', code)
    code = re.sub(r"'''[\s\S]*?'''", '', code)
    
    lines = code.split('\n')
    result = []
    
    for line in lines:
        line = line.rstrip()
        
        if line.strip().startswith('#'):
            continue
        
        line = re.sub(r'#.*$', '', line).rstrip()
        
        result.append(line)
    
    return '\n'.join(result)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    
    cleaned = remove_comments(code)
    return cleaned

def main():
    files = [
        'config.py',
        'database.py',
        'logger.py',
        'auth.py',
        'equipment.py',
        'inout.py',
        'inventory.py',
        'report.py',
        'ui.py',
        'main.py'
    ]
    
    all_code = []
    for file in files:
        filepath = os.path.join(os.path.dirname(__file__), file)
        cleaned = process_file(filepath)
        all_code.append(cleaned)
    
    combined = '\n\n'.join(all_code)
    lines = combined.split('\n')
    
    print(f'源文件总行数: {len(lines)}')
    
    page_size = 60
    total_pages = 60
    
    while len(lines) < total_pages * page_size:
        lines.append('')
    
    lines = lines[:total_pages * page_size]
    
    output = '# 源代码说明文档\n\n'
    output += '校园体育器材出入库管理系统\n\n'
    output += '说明: 包含完整源代码，每页60行，无需注释，每页行号从1开始\n\n'
    output += '---\n\n'
    output += '## 第一部分：前30页源代码（PAGE 1-30）\n\n'
    
    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * page_size
        end = page_num * page_size
        page_lines = lines[start:end]
        
        if page_num == 31:
            output += '\n---\n\n'
            output += '## 第二部分：后30页源代码（PAGE 31-60）\n\n'
        
        page_lines_with_numbers = []
        for i, line in enumerate(page_lines, 1):
            page_lines_with_numbers.append(f"{i:4d} | {line}")
        
        output += f'### PAGE {page_num}\n'
        output += '```\n'
        output += '\n'.join(page_lines_with_numbers)
        output += '\n```\n\n'
    
    with open(os.path.join(os.path.dirname(__file__), '源代码说明文档.md'), 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f'Generated 源代码说明文档.md with {total_pages} pages')
    print(f'每页行号从1开始，每页60行')

if __name__ == '__main__':
    main()

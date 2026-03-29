"""
Markdown-to-HTML converter.
THIS IS THE FILE THE AGENT EDITS.

Takes a markdown string and returns an HTML string.
"""

import re


def convert_markdown(markdown: str) -> str:
    lines = markdown.split('\n')
    html_blocks = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Code block
        if line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1
            html_blocks.append('<pre><code>' + '\n'.join(code_lines) + '\n</code></pre>')
            continue

        if line.strip() == '':
            i += 1
            continue

        # Heading
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            html_blocks.append(f'<h{len(m.group(1))}>{_inline(m.group(2))}</h{len(m.group(1))}>')
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^---$', line.strip()):
            html_blocks.append('<hr />')
            i += 1
            continue

        # Blockquote
        if line.startswith('>'):
            quote_lines = []
            while i < len(lines) and (lines[i].startswith('> ') or lines[i] == '>'):
                quote_lines.append('' if lines[i] == '>' else lines[i][2:])
                i += 1
            inner_html = convert_markdown('\n'.join(quote_lines))
            html_blocks.append(f'<blockquote>\n{inner_html}\n</blockquote>')
            continue

        # Unordered list
        if re.match(r'^- ', line):
            i = _parse_ul(lines, i, html_blocks, 0)
            continue

        # Ordered list
        if re.match(r'^\d+\. ', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                items.append(_inline(re.sub(r'^\d+\. ', '', lines[i])))
                i += 1
            html_blocks.append('<ol>\n' + '\n'.join(f'<li>{it}</li>' for it in items) + '\n</ol>')
            continue

        # Paragraph — collect consecutive non-blank, non-block lines
        para_lines = []
        while i < len(lines) and lines[i].strip() != '' and not _is_block_start(lines[i]):
            para_lines.append(lines[i])
            i += 1
        html_blocks.append(f'<p>{_inline(chr(10).join(para_lines))}</p>')

    return '\n'.join(html_blocks)


def _is_block_start(line):
    return (line.startswith('```') or
            re.match(r'^#{1,6}\s+', line) or
            re.match(r'^---$', line.strip()) or
            line.startswith('> ') or line == '>' or
            re.match(r'^- ', line) or
            re.match(r'^\d+\. ', line))


def _parse_ul(lines, i, html_blocks, depth):
    prefix = '  ' * depth + '- '
    sub_prefix = '  ' * (depth + 1) + '- '
    items = []

    while i < len(lines):
        line = lines[i]
        if line.startswith(prefix) and not line.startswith(sub_prefix):
            items.append(_inline(line[len(prefix):]))
            i += 1
            if i < len(lines) and lines[i].startswith(sub_prefix):
                sub_html = []
                i = _parse_ul(lines, i, sub_html, depth + 1)
                if sub_html:
                    items[-1] += '\n' + sub_html[0]
        else:
            break

    html_blocks.append('<ul>\n' + '\n'.join(f'<li>{it}</li>' for it in items) + '\n</ul>')
    return i


def _inline(text):
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" />', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text

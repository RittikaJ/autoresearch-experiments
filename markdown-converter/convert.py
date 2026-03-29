"""
Markdown-to-HTML converter.
THIS IS THE FILE THE AGENT EDITS.

Takes a markdown string and returns an HTML string.
"""

import re


def convert_markdown(markdown: str) -> str:
    """Convert a markdown string to HTML."""
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
            i += 1  # skip closing ```
            html_blocks.append('<pre><code>' + '\n'.join(code_lines) + '\n</code></pre>')
            continue

        # Blank line — skip
        if line.strip() == '':
            i += 1
            continue

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = _inline(heading_match.group(2))
            html_blocks.append(f'<h{level}>{text}</h{level}>')
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
                if lines[i] == '>':
                    quote_lines.append('')
                else:
                    quote_lines.append(lines[i][2:])
                i += 1
            # Parse the inner content as markdown recursively
            inner_md = '\n'.join(quote_lines)
            inner_html = convert_markdown(inner_md)
            html_blocks.append(f'<blockquote>\n{inner_html}\n</blockquote>')
            continue

        # Unordered list
        if re.match(r'^- ', line):
            i = _parse_unordered_list(lines, i, html_blocks, 0)
            continue

        # Ordered list
        if re.match(r'^\d+\. ', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                items.append(_inline(re.sub(r'^\d+\. ', '', lines[i])))
                i += 1
            html_blocks.append('<ol>\n' + '\n'.join(f'<li>{item}</li>' for item in items) + '\n</ol>')
            continue

        # Paragraph (default) - collect consecutive non-blank, non-block lines
        para_lines = []
        while i < len(lines) and lines[i].strip() != '' and not _is_block_start(lines[i]):
            para_lines.append(lines[i])
            i += 1
        text = '\n'.join(para_lines)
        html_blocks.append(f'<p>{_inline(text)}</p>')

    return '\n'.join(html_blocks)


def _is_block_start(line):
    """Check if a line starts a block element."""
    return (line.startswith('```') or
            re.match(r'^#{1,6}\s+', line) or
            re.match(r'^---$', line.strip()) or
            line.startswith('> ') or line == '>' or
            re.match(r'^- ', line) or
            re.match(r'^\d+\. ', line))


def _parse_unordered_list(lines, i, html_blocks, indent_level):
    """Parse an unordered list, handling nested sublists."""
    prefix = '  ' * indent_level + '- '
    sub_prefix = '  ' * (indent_level + 1) + '- '
    items = []

    while i < len(lines):
        line = lines[i]
        # Check for item at current indent level
        if line.startswith(prefix) and not line.startswith(sub_prefix):
            item_text = _inline(line[len(prefix):])
            items.append(item_text)
            i += 1
            # Check for nested sublist
            if i < len(lines) and lines[i].startswith(sub_prefix):
                sub_html = []
                i = _parse_unordered_list(lines, i, sub_html, indent_level + 1)
                # Attach sublist to last item
                if items and sub_html:
                    items[-1] = items[-1] + '\n' + sub_html[0]
        elif indent_level > 0 and line.startswith(sub_prefix):
            # This is a deeper nested item
            break
        else:
            break

    result = '<ul>\n' + '\n'.join(f'<li>{item}</li>' for item in items) + '\n</ul>'
    html_blocks.append(result)
    return i


def _inline(text):
    """Process inline markdown: bold, italic, code, links, images."""
    # Inline code (must come before bold/italic to avoid conflicts)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Images (must come before links)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" />', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text

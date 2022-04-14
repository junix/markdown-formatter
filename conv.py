import re
from urllib.parse import unquote


def add_head_tail(code, use_block=False):
    use_block = use_block or ('\n' in code or '\\\\' in code or "\\tag" in code or '&' in code)
    if use_block:
        print('use block =============================')
        if 'begin' not in code:
            code = '\\begin{align}\n' + code + "\n\n\\end{align}"
        return f'\n$$\n{code}\n$$\n'
    else:
        return f'${code}$'


def regular_code(code):
    no_plus_in_right = [
        "times", "cdot", "nonumber",
        "gt", "in", "ne", "lt", "geq", "leq",
        "cap", "sim", "mid",
        "Leftarrow", "Rightarrow", "Leftrightarrow",
        "log", "exp", "partial", "sum", "prod", 'ln',
        "text", "texttt", "boldsymbol", "frac", "sqrt",
        "approx", '=', ',', '-', '_',
    ]

    no_plus_in_left = [
        "times", "cdot", "nonumber",
        "gt", "in", "ne", "lt", "geq", "leq",
        "cap", "sim", 'right', 'mid',
        "Leftarrow", "Rightarrow", "Leftrightarrow",
        "tag", "approx", '=', '_', '-', '^',
    ]

    while True:
        old = code
        code = re.sub(r'(\\begin{(align|aligned|align\*|cases)})\++', r'\1\n', code)
        code = re.sub(r'\++\\end{', r'\n\\end{', code)

        code = re.sub(r'^\+', '', code)
        code = re.sub(r'\+$', '', code)
        code = re.sub(r'\+}', '}', code)
        code = re.sub(r'\+{', '{', code)
        code = re.sub(r'(\\[a-zA-Z]+)\+', '\\1 ', code)
        code = re.sub(r'\\\+', '\\ ', code)
        code = re.sub(r'\\\\\s*\\tag', r' \\tag', code)

        # fix it
        # code = re.sub(r'\+', ' ', code)

        code = re.sub(r'\|\++', '|', code)
        code = re.sub(r'\++\|', '|', code)
        code = re.sub(r'-\++', '-', code)
        code = re.sub(r'\++-', '-', code)
        code = re.sub(r',\++', ',', code)
        code = re.sub(r'\++=', '=', code)
        code = re.sub(r'=\++', '=', code)
        code = re.sub(r'\++,', ',', code)
        code = re.sub(r'\(\++', '(', code)
        code = re.sub(r'\++\)', ')', code)

        code = re.sub(r'\+;', ';', code)
        code = re.sub(r';\+', ';', code)

        code = re.sub(r'\++\s?&', r'\n&', code)
        code = re.sub(r'&\++', r'& ', code)

        code = re.sub(r'\+{2,}', r' ', code)

        code = re.sub(f'\\++\\\\({"|".join(no_plus_in_left)})', r' \\\1', code)
        code = re.sub(f'\\\\({"|".join(no_plus_in_right)})\\++', r'\\\1 ', code)

        code = re.sub(r'\+-', r'-', code)
        code = re.sub(r'\+\^', r'^', code)
        code = re.sub(r'\+{2,}', r'', code)
        code = re.sub(r'(\\\+){2,}', r'', code)

        code = re.sub(r'\\Re', r'\\mathfrak{R}', code)

        code = re.sub(r'\+\\\\', r' \\\\', code)
        code = re.sub(r'\\\\\++', r'\\\\\n', code)

        code = re.sub(r'(\\(sum|prod)_{[^}]+}\^{[^}]+})\++', r"\1", code)

        if code == old:
            return code


def convert_to_latex_formula(line, remove_plus, keep_graph):
    line = _convert_to_latex_formula(line, next_formula_zhihu, remove_plus, keep_graph)
    line = _convert_to_latex_formula(line, next_formula_jianshu, remove_plus, keep_graph)
    line = _convert_to_latex_formula(line, next_formula_wiki, remove_plus, keep_graph)
    line = _convert_to_latex_formula(line, next_formula_github, remove_plus, keep_graph)
    return line


def _convert_to_latex_formula(line, code_extractor, remove_plus, keep_graph=False):
    acc = []
    while True:
        res = code_extractor(line)
        if not res:
            # 在这行没有找到任何需要处理的公示，直接返回，不要再格式化，防止格式化错误
            if not acc and line:
                return line
            if line:
                acc.append((line, "text"))
            break

        # 在这行找到了个链接公式，格式化
        matched_text, code = res
        assert len(matched_text) > 0
        index = line.index(matched_text)
        prev = line[:index]
        if prev:
            acc.append((prev, "text"))

        fmt_code = regular_code(code)
        if remove_plus:
            fmt_code = re.sub(r'\+', ' ', fmt_code)
        acc.append((fmt_code, "formula"))
        if keep_graph and '+' in code:
            acc.append((f"\n\n{matched_text}\n", "text"))
        line = line[index + len(matched_text):]

    if len(acc) == 1 and acc[0][1] == "formula":
        return add_head_tail(acc[0][0], use_block=True)
    return ''.join(s if t == "text" else add_head_tail(s) for s, t in acc)


def next_formula_zhihu(line):
    pattern = re.compile(r'!\[\[公式]]\(https://www\.zhihu\.com/equation\?tex=([^)]*)\)')
    m = pattern.search(line)
    if not m:
        return None
    tex_encode = m.group(1)
    tex_encode = re.sub(r'\+', '%20', tex_encode)
    code = unquote(tex_encode)
    return m.group(0), code


def next_formula_jianshu(line):
    pattern = re.compile(r'!\[(.+?)]\(https://math.jianshu.com/math\?formula=([-*~._()%\da-zA-Z]*)\)')
    m = pattern.search(line)
    if not m:
        return None
    desc = m.group(1)
    url_code = unquote(m.group(2))
    if re.sub(r'\s', '', desc) != re.sub(r'\s', '', url_code):
        return None
    return m.group(0), url_code


def next_formula_github(line):
    pattern = re.compile(
        r'!\[(.+?)\]\(https://render.githubusercontent.com/render/math\?math=[-*~._()%\da-zA-Z]+&mode=inline')
    m = pattern.search(line)
    if not m:
        return None
    desc = m.group(1)
    return m.group(0), desc.strip('$')


def next_formula_wiki(line):
    pattern = re.compile(r'!\[(.+?)]\(https://wikimedia.org/api/rest_v1/media/math/render/svg/[0-9a-f]+\)')
    m = pattern.search(line)
    if not m:
        return None
    tex_code = m.group(1)
    return m.group(0), tex_code


_useless_zhihu_link = re.compile(r'\[([^]]+)]\(https://www.zhihu.com/search\?q=.*?search_source.*?\)')


def remove_useless_links(text):
    while True:
        orig = text
        text = _useless_zhihu_link.sub(r'\1', text)
        if text == orig:
            return text

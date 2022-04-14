import string, re

cmd2symbol = {
    'times': '×',
    'sigma': 'σ',
    'mu': 'μ',
    'eta': 'η',
    'phi': 'ϕ',
    'pi': 'π',
    'infty': '∞',
    'gamma': 'γ',
    'epsilon': 'ϵ',
    'varepsilon': 'ε',
    'theta': 'θ',
    'omega': 'ω',
    'alpha': 'α',
    'beta': 'β',
    'delta': 'δ',
    'lambda': 'λ',
    'odot': '⊙',
    'otimes': '⊗',
    'pm':'±',
    'neq': '≠',
    'ne': '≠',
    'leq': '⩽',
    'le': '⩽',
    'leqslant': '⩽',
    'geq': '⩾',
    'ge': '⩾',
    'geqslant': '⩾',
    'therefore': '∴',
    'Leftrightarrow': '⇔',
    'Rightarrow': '⇒',
    'langle': '⟨',
    'rangle': '⟩',
    'sim': '∼',
    'exist': '∃',
    'exists': '∃',
    'cap': '∩',
    'subset': '⊂',
    'sub': '⊂',
    'sube': '⊆',
    'subseteq': '⊆',
    'sube': '⊆',
    'in': '∈',
    'isin': '∈',
    'to': '→',
    'approx': '≈',
    'simeq': '≃',
    'emptyset': '∅',
    'empty': '∅',
    'mid': '|',
    'cdot': '·',
    'rightarrow': '→',
    'leftarrow': '←',
    "partial": "∂",
    "R": "ℝ",
    "E": "𝔼",
    "nabla": "∇",
    "intercal": "⊺",
    "cdots": "⋯",
    # user defined symbol
    "note": '<span style="color: red">✍</span>'
}


def is_letter(c):
    return c in string.ascii_letters


def is_punct(c):
    return c in string.punctuation


def replace_tex_command(line, tab=cmd2symbol):
    from itertools import takewhile
    acc = []
    while line:
        prefix = ''.join(takewhile(lambda x: x != '\\', line))
        acc.append(prefix)
        line = line[len(prefix):]
        if not line:
            return ''.join(acc)

        cmd = ''.join(takewhile(is_letter, line[1:]))
        symbol = tab.get(cmd)
        length = max(2, len(cmd) + 1)
        if symbol is None:
            acc.append(line[:length])
        else:
            acc.append(symbol)
        line = line[length:]
    return ''.join(acc)


def regularize_formula(text):
    text = re.sub(r'\\begin{aligned}', r'\\begin{align}', text)
    text = re.sub(r'\\end{aligned}', r'\\end{align}', text)

    text = re.sub(r'\\mathbb{E}', r'𝔼', text)
    text = re.sub(r'\\mathbb{R}', r'ℝ', text)
    text = re.sub(r'\\mathbb{X}', r'𝕏', text)

    text = re.sub(r'\s{3,}', r'  ', text)

    text = re.sub(r' +_', r'_', text)
    text = re.sub(r' +\^', r'^', text)
    text = re.sub(r'[∇] +', r'∇', text)
    text = re.sub(r'(?<=[^ $])[∇]', r' ∇', text)
    text = re.sub(r'\s*([∈≠≃=<>])\s*', r' \1 ', text)

    text = re.sub(r'\^{\\mathrm{T}}', r'^⊺', text)
    text = re.sub(r'\^{T}', r'^⊺', text)
    text = re.sub(r'\^T', r'^⊺', text)

    return text


_lookbehind = f'(?<=[\u4E00-\u9FFF，。])'
_lookforward = f'(?=[\u4E00-\u9FFF，。])'
_to_formula_patterns = (
    r"[a-z]",
    r'[a-zA-Z]_[1-9ikj]',
    r"[a-zA-Z]_{[1-9ikj]}"
)
_new_formula_pattern = re.compile(_lookbehind + '(' + '|'.join(_to_formula_patterns) + ")" + _lookforward)


def detect_new_formula(text):
    return _new_formula_pattern.sub(r'$\1$', text)


def remove_tag(code, tag_beg, tag_end):
    ...


if __name__ == '__main__':
    s = "f _1    ^2"
    print(regularize_formula(s))

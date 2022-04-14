import os

note_dir = os.path.join(os.path.dirname(__file__), '..')

sym_tags = (
    ["attention", "注意力机制"],
    ['AI', "machine learning", "机器学习", "machinelearning"],
    ["multi-task", "multitask", "多目标学习", "多任务学习"],
    ["optim", "优化器", "optmizer"],
    ["QU", "Query理解", "查询理解"],
    ["information theory", "information-theory", "informationtheory", "信息论"],
    ["deep-learning", "深度学习", "deeplearning"],
    ['lex', '分词']
)


def regularize_tag(tag):
    for syms in sym_tags:
        if tag in syms:
            return syms[0]
    return tag


def abspath(*paths):
    return os.path.abspath(os.path.expanduser(os.path.join(*paths)))


def seek_tag_dir(tag: str) -> str:
    for root, sub_dirs, files in os.walk(note_dir):
        for sub_dir in sub_dirs:
            if sub_dir.lower() == tag.lower():
                return abspath(root, sub_dir)
    return abspath(note_dir, tag)


def is_broken_link(file):
    file = abspath(file)
    if not os.path.islink(file):
        return False
    source = abspath(os.readlink(file))
    return not os.path.exists(source)


def find_the_latest_modified_markdown_file(directory):
    latest_file = None
    latest_mtime = 0
    for root, sub_dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith('.md'):
                continue
            path = abspath(root, file)
            if os.path.islink(path):
                if is_broken_link(path):
                    print(f"remove broken link:{path}")
                    os.unlink(path)
                continue
            mtime = os.path.getmtime(path)
            if mtime <= latest_mtime:
                continue
            latest_file = path
            latest_mtime = mtime
    return latest_file


def ensure_dir_created(path):
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.mkdir(d)
    else:
        if not os.path.isdir(d):
            raise ValueError(f"existed {d} is not dir")


def read_file(path):
    if not os.path.isfile(path):
        raise ValueError(f"{path} is not file")

    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return None


def dump(path, lines: str):
    ensure_dir_created(path)
    with open(path, 'w') as f:
        if isinstance(lines, (list, tuple)):
            f.write('\n'.join(lines))
        elif isinstance(lines, str):
            f.write(lines)
        else:
            raise TypeError(f"invalid content type:{type(lines)}")
        cwd = os.getcwd()
        if path.startswith(cwd):
            print(f"dump to {path[len(cwd) + 1:]}")
        else:
            print(f"dump to {path}")
        return path


def seek_same_name_file(to_check):
    to_check = abspath(to_check)
    base_name = os.path.basename(to_check)
    for root, sub_dirs, files in os.walk(note_dir):
        for f in files:
            if f != base_name:
                continue
            path = abspath(root, f)
            if os.path.islink(path):
                continue
            if path == to_check:
                continue
            return path
    return None


def release_to_tag_dirs(orig_file, content, tags):
    if not tags:
        print("no tags found")
        dump(orig_file, content)
        return orig_file

    orig_file = abspath(orig_file)
    basename = os.path.basename(orig_file)
    tag_dirs = [seek_tag_dir(t) for t in tags]

    hierarchical_tag_dirs = []
    for t in tag_dirs:
        has_sub_tag = False
        for x in tag_dirs:
            if x.startswith(t + "/"):
                has_sub_tag = True
                break
        if not has_sub_tag:
            hierarchical_tag_dirs.append(t)

    tags_files = [abspath(t, basename) for t in hierarchical_tag_dirs]
    to_dump = tags_files[0]
    to_links = tags_files[1:]

    for root, sub_dirs, files in os.walk(note_dir):
        for file in files:
            path = abspath(root, file)
            if not os.path.islink(path):
                continue
            source = abspath(os.readlink(path))
            if not os.path.exists(source) or source == orig_file or source in tags_files:
                print(f"unlink:{path}")
                os.unlink(path)

    if os.path.exists(orig_file):
        os.remove(orig_file)
    dump(to_dump, content)
    for f in to_links:
        ensure_dir_created(f)
        if os.path.exists(f):
            continue
        os.symlink(to_dump, f)
        print(f"symlink {f}")
    return to_dump

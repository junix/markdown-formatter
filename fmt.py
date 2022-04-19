#!/usr/bin/env python3
import optparse

from conv import *
from htmls import *
from md import *
from seg import *
from tags import *
from tex import *


def reopen(file):
    import sys
    if sys.platform == 'darwin':
        os.system(f"/usr/bin/open '{file}'")
    else:
        raise ValueError(f"to impl")


######################################################
#              内容理解和格式化                       #
######################################################


def seek_tags(lines):
    for line in lines:
        if line.text_type == LineType.Tag:
            tags = getattr(line, 'tags', [])
            return list(set(regularize_tag(tag) for tag in tags))

    return []


han_char = r'[\u3400-\u4DBF\u4E00-\u9FFF]'
han_char_punct = r'[\u3400-\u4DBF\u4E00-\u9FFF，。]'


def contain_hans(str):
    return any('\u4e00' <= c <= '\u9fa5' for c in str)


def format_content(lines, relabel=True):
    for line in lines:
        segs = []
        for s in line.to_segments():
            if isinstance(s, ImgSeg):
                segs.append(s.to_html_tag_seg())
            else:
                segs.append(s)
        for seg in segs:
            print(seg)
            if isinstance(seg, (CodeSeg, TagSeg, TitleSeg)):
                continue

            x = seg.text
            x = convert_to_latex_formula(x, False, False)
            # x = zoom_img(x)
            if isinstance(seg, TextSeg):
                x = remove_space(x)
            x = replace_tex_command(x)
            if isinstance(seg, FormulaSeg):
                # x = remove_space_in_command(x)
                x = regularize_formula(x)
            if isinstance(seg, TextSeg):
                x = detect_new_formula(x)
                x = conv_to_ruby(x)
            x = regular_quote(x)
            x = remove_zhihu_redirect_url(x)
            x = remove_useless_links(x)
            seg.text = x
        line.remain = join_segs(*segs)

    if relabel:
        remark_title_seq_no(lines)

    return lines


def main():
    parser = optparse.OptionParser()
    parser.add_option('-f', '--file', dest="file", help="file", default=())
    parser.add_option('-o', '--object', dest="save_to", help="save_to", default=None)
    parser.add_option('', '--relabel', dest="relabel", help="relabel", action="store_true", default=False)
    parser.add_option('', '--verbose', dest="verbose", help="verbose", action='store_true', default=False)
    parser.add_option('', '--rmp', dest="rmp", help="remove plus", action='store_true', default=False)
    parser.add_option('', '--keep-graph', dest="keep_graph", help="keep graph", action='store_true', default=False)
    (options, args) = parser.parse_args()

    to_fmts = options.file or args or [find_the_latest_modified_markdown_file(os.getcwd())]
    for file in to_fmts:
        lines = list(parse_to_lines(read_file(file)))
        # for l in lines:
        #     print(l)
        lines = format_content(lines, relabel=options.relabel)
        tags = seek_tags(lines)
        content = '\n'.join([x.remain for x in lines])
        if not tags:
            new_path = dump(file, content)
        else:
            conflict_file = seek_same_name_file(file)
            if conflict_file:
                print(f"名字冲突:\n\t当前文件>> {file}\n\t冲突文件>> {conflict_file}")
                continue
            new_path = release_to_tag_dirs(file, content, tags)
        reopen(new_path)


def test():
    s = "tags: 推荐系统，双塔，SENet"
    d = "推荐系统/a.md"
    print(os.path.abspath(os.path.expanduser(d)))
    tags = seek_tags([s])
    release_to_tag_dirs("推荐系统/a.md", "test", tags)


if __name__ == '__main__':
    main()
    # t = "你好x_{1}中国"
    # print(detect_new_formula(t))

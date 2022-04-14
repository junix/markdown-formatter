def seek_util(text: str, delim: str):
    acc = []
    while text:
        if text[0] == delim:
            acc.append(text[0])
            return ''.join(acc)
        n_step = 2 if text[0] == '\\' else 1
        acc.append(text[:n_step])
        text = text[n_step:]
    return None

def seek_pair(text: str, delim:str):
    if not text or not text.startswith(delim):
        return None
    text = text[len(delim):]
    remain = seek_util(text, delim)
    return delim + remain if remain else None


if __name__ == '__main__':
    s = "ok\\\\$good$"
    print(seek_util(s, '$'))

import re


def delete_brackets(s):
    table = {
        "(": "（",
        ")": "）",
        "<": "＜",
        ">": "＞",
        "{": "｛",
        "}": "｝",
        "[": "［",
        "]": "］"
    }

    for key in table.keys():
        s = s.replace(key, table[key])

    l = ['（[^（|^）]*）', '【[^【|^】]*】', '＜[^＜|^＞]*＞', '［[^［|^］]*］',
         '「[^「|^」]*」', '｛[^｛|^｝]*｝', '〔[^〔|^〕]*〕', '〈[^〈|^〉]*〉']
    for l_ in l:
        s = re.sub(l_, "", s)

    return delete_brackets(s) if sum([1 if re.search(l_, s) else 0 for l_ in l]) > 0 else s


def format(s):
    return delete_brackets(s).strip().replace('\u3000', ' ').translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))

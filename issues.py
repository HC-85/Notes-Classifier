from typing import Union, List
import os

#TODO: check for repeated tags
def check_md_tags_headers(vault_path:str, source: Union[List[str], str]):
    md_files = source if isinstance(source, list) else [source]

    no_tags = []
    multi_tags = []    
    for md_name in md_files:
        tag_flag = 0
        with open(os.path.join(vault_path, md_name), 'r', encoding='utf-8') as f:
            text = f.read()

        for line in text.split('\n'):
            if line == '###### Tags':
                tag_flag += 1
                continue

        if tag_flag == 0:
            no_tags.append(md_name)
        elif tag_flag > 1:
            multi_tags.append(md_name)
        
    return no_tags, multi_tags


def write_header(vault = 'Software', md = 'test.md'):
    target = os.path.join(vault, md)
    with open(target, 'a') as file:
        file.write('\n###### Tags\n')
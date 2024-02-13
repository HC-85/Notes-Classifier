from typing import Union, List
import re
import os

#TODO: replace this shit with the other one
def inspect_md_tags(vault_path:str, md: Union[List[str], str]):
    tagset = set()
    tag_flag = False
    with open(os.path.join(vault_path, md), 'r', encoding='utf-8') as f:
        text = f.read()
    
    for line in text.split('\n'):
        if tag_flag:
            tags = re.findall(r'#([^ ]+)', line)
            if tags:
                tagset = tagset.union(set(tags))
            else:
                break

        else:
            if line == '###### Tags':
                tag_flag = True
                continue

    return sorted(list(tagset))


def demo_suggest_tags(vault, md, n_suggestions):
    from numpy.random import default_rng
    rng = default_rng()
    existing_tags = inspect_md_tags(vault, md) 
    new_tags = []

    while len(new_tags)<n_suggestions:
        tag_ids = rng.integers(0, 10, n_suggestions)
        sug_tags = [f'Tag{id}' for id in tag_ids]
        for tag in sug_tags:
            if (tag not in existing_tags) and (tag not in new_tags):
                new_tags.append(tag)
                if len(new_tags) == n_suggestions:
                    break
    return new_tags


def append_tags(vault, mds, tags_to_append):
    for md in mds:
        target = os.path.join(vault, md)
        with open(target, 'a', encoding = 'utf-8') as file:
            for tag in tags_to_append[md]:
                file.write(f' #{tag}')
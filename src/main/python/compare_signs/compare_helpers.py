# helper functions for compare signs
from collections import defaultdict
from constant import ARTICULATOR_ABBREVS


def summarize_path_comparison(ld):
    def fuse_two_dicts(d1, d2):
        merged = defaultdict(dict)

        for key in set(d1) | set(d2):  # for each key in either d1 or d2
            if key in d1 and key in d2:
                if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                    # Recursively merge dictionaries
                    merged[key] = fuse_two_dicts(d1[key], d2[key])
                else:
                    # If both keys exist and aren't dictionaries, prioritize True
                    merged[key] = d1[key] or d2[key]
            elif key in d1:
                merged[key] = d1[key]
            else:
                merged[key] = d2[key]

        return dict(merged)

    result_dict = {}

    for d in ld:
        result_dict = fuse_two_dicts(result_dict, d)

    return [result_dict]


def get_informative_elements(l: list) -> list:
    result = []
    for element in reversed(l):
        if not any(element in already for already in result):
            result.append(element)
    return result


def compare_elements(e1: str, e2: str, pairwise=True):
    components1 = e1.split('>')
    components2 = e2.split('>')

    res1 = {}
    res2 = {}

    for c1, c2 in zip(components1, components2):
        res1[c1] = (c1 == c2)
        res2[c2] = (c1 == c2)

    # If there are extra components in either e1 or e2
    if len(components1) > len(components2):
        for c in components1[len(components2):]:
            res1[c] = False
    elif len(components2) > len(components1):
        for c in components2[len(components1):]:
            res2[c] = False

    hierarchical_res1 = current = {}
    for item in components1[:-1]:
        current[item] = {}
        current = current[item]
    current[components1[-1]] = res1[components1[-1]]

    hierarchical_res2 = current = {}
    for item in components2[:-1]:
        current[item] = {}
        current = current[item]
    current[components2[-1]] = res2[components2[-1]]

    if not pairwise:
        current[components1[-1]], current[components2[-1]] = False, False

    return hierarchical_res1, hierarchical_res2


def qcolor_to_rgba_str(qcolor):
    # convert qcolor into rgba string by extracting red, green, blue, alpha
    raw_rgba = qcolor.getRgbF()
    red, green, blue = [int(i * 255) for i in raw_rgba[:3]]
    alpha = raw_rgba[3]
    return f'rgba({red}, {green}, {blue}, {alpha:.3f})'


def analyze_modules(modules: list, module_numbers: dict, module_abbrev: str):
    r = {}
    for m in modules:
        this_uniqid = m.uniqueid
        articulator_name: str = m.articulators[0]
        articulator_bool: dict = m.articulators[1]
        art_abbrev = ARTICULATOR_ABBREVS[articulator_name]

        # for each case where articulator_bool is true, add (key: module_id, value: module)
        # and module_id is like H1.Mov1 that is in the summary panel!
        r.update({
            f'{art_abbrev}{art_num}.{module_abbrev}{module_numbers[this_uniqid]}': m
            for art_num, b in articulator_bool.items() if b
        })
    return r

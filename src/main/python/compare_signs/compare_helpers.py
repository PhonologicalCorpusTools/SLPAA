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


def build_hierarchy(components, res):
    if not components:
        return {}
    hierarchy = current = {}
    for c in components[:-1]:
        current[c] = {}
        current = current[c]
    current[components[-1]] = res[components[-1]]
    return hierarchy


def compare_elements(e1: str, e2: str, btn_types1: dict, btn_types2: dict, pairwise=True):
    components1 = e1.split('>')
    components2 = e2.split('>')

    res1 = {}
    res2 = {}

    # special case: non-pairwise
    if not pairwise:
        if components1:
            # e2 is missing; mark all components in e1 as unmatched
            for idx, c1 in enumerate(components1):
                path1 = '>'.join(components1[:idx+1])
                btn_type1 = btn_types1.get(path1, 'unknown')
                res1[c1] = {'match': False, 'button_type': btn_type1}
        if components2:
            # e1 is missing; mark all components in e2 as unmatched
            for idx, c2 in enumerate(components2):
                path2 = '>'.join(components2[:idx+1])
                btn_type2 = btn_types2.get(path2, 'unknown')
                res2[c2] = {'match': False, 'button_type': btn_type2}
        hierarchical_res1 = build_hierarchy(components1, res1)
        hierarchical_res2 = build_hierarchy(components2, res2)
        return hierarchical_res1, hierarchical_res2

    # regular cases
    for idx, (c1, c2) in enumerate(zip(components1, components2)):
        # Build the path up to this point
        path1 = '>'.join(components1[:idx + 1])
        path2 = '>'.join(components2[:idx + 1])

        btn_type1 = btn_types1.get(path1, 'unknown')
        btn_type2 = btn_types2.get(path2, 'unknown')

        match = c1 == c2
        res1[c1] = {'match': match, 'button_type': btn_type1}
        res2[c2] = {'match': match, 'button_type': btn_type2}

    # Handle extra components in either e1 or e2
    if len(components1) > len(components2):
        for idx, c in enumerate(components1[len(components2):], start=len(components2)):
            path1 = '>'.join(components1[:idx + 1])
            btn_type1 = btn_types1.get(path1, 'unknown')
            res1[c] = {'match': False, 'button_type': btn_type1}
    elif len(components2) > len(components1):
        for idx, c in enumerate(components2[len(components1):], start=len(components1)):
            path2 = '>'.join(components2[:idx + 1])
            btn_type2 = btn_types2.get(path2, 'unknown')
            res2[c] = {'match': False, 'button_type': btn_type2}
    hierarchical_res1 = build_hierarchy(components1, res1)
    hierarchical_res2 = build_hierarchy(components2, res2)

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


#  Traverse the path and return the button types (i.e., either 'rb' or 'cb') of each element in the path.
def get_btn_type_for_mvmtpath(path, root_node):
    parts = path.split('>')
    btn_types = []

    def traverse(node, path_parts):
        if not path_parts:
            return True  # Reached the end successfully
        part = path_parts[0]

        # First, check if the current node's children have the desired part
        matching_child = None
        for child in node.children:
            if child.display_name == part:
                matching_child = child
                break

        if matching_child:
            btn_types.append(matching_child.button_type)
            return traverse(matching_child, path_parts[1:])
        else:
            # Recursively search in all children
            for child in node.children:
                if traverse(child, path_parts):
                    return True
            return False  # Not found in this branch

    found = traverse(root_node, parts)

    if found:
        return '>'.join(btn_types)
    else:
        return 'Path not found'


def parse_button_type(node_data):
    # helper function that parses 'button_type' information created by get_btn_type_for_mvmtpath()
    if not isinstance(node_data, dict):
        return []
    if 'button_type' in node_data:
        return node_data['button_type'].split('>')
    for k, v in node_data.items():
        if isinstance(v, dict):
            deeper = parse_button_type(v)
            if deeper:
                return deeper
    return []

def rb_red_buttons(children: list, parents: list, should_paint_red, yellow_brush):
    # helper function that colours of children and their parents which are all CompareTreeWidgetItem objects
    # children, parents: lists of CompareTreeWidgetItem
    # should_paint_red: list.
    # yellow_brush: QBrush object to check for parent's colour
    # called only if
    # - both item in children are radiobuttons but not identical
    # - itentical parents
    item1, item2 = children
    parent1, parent2 = parents

    item1.initilize_bg_color('red')  # red
    item2.initilize_bg_color('red')
    should_paint_red[0] = True
    should_paint_red[1] = True
    if parent1.background(0).color() != yellow_brush:
        parent1.initilize_bg_color('red')
    if parent2.background(0).color() != yellow_brush:
        parent2.initilize_bg_color('red')
    parent1.addChild(item1)
    parent2.addChild(item2)
    return [should_paint_red[0], should_paint_red[1]]

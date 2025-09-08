# helper functions for compare signs
from collections import defaultdict
from PyQt5.QtCore import Qt
import re
from itertools import count, product

from constant import ARTICULATOR_ABBREVS, userdefinedroles as udr
from lexicon.module_classes import Direction
from gui.handconfigspecification_view import ConfigField  # for predefined handshape labels

_pair_id_counter = count(1)  # for


# return a unique int for pair_id (the anchor for comparing two tree widget items)
def next_pair_id() -> int:
    return next(_pair_id_counter)


def summarize_path_comparison(ld):
    def fuse_two_dicts(d1, d2):
        merged = defaultdict(dict)

        # the keys are ordered in this manner:
        # everything in dictionary 1 comes first, and then anything new from dictionary 2 follows.
        keys_from_both = list(d1) + [k for k in d2 if k not in d1]
        for key in keys_from_both:  # for each key in either d1 or d2
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


def update_path_text(has_usr_text: str, path_text: str) -> str:
    if len(has_usr_text) < 1 or has_usr_text == path_text:
        return path_text

    match = re.match(r'(.+?) (\[.+\])$', has_usr_text)  # e.g., has_usr_text = 'a>b [3]'
    base_path, usr_specified_value = match.groups()  # e.g., base_path = 'a>b', usr_s... = '[3]'

    base_parts = base_path.split('>')  # e.g., ['a', 'b']
    path_parts = path_text.split('>')  # e.g., ['a', 'b', 'c']

    # check if path_text is a proper superset of base_path
    if path_parts[:len(base_parts)] == base_parts and usr_specified_value:
        path_parts[len(base_parts) - 1] += f' {usr_specified_value}'  # if so, append user-specified value to path_text

    return '>'.join(path_parts)  # reassemble path_text and return


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


def get_checked_paths_from_list(treemodel):
    # Each MovementModule has a .movementtreemodel, which in turn has a .listmodel
    list_model = treemodel.listmodel

    selected_paths = []  # this will be the output
    has_usr_text = ''  # to remember the most recent 'user text' temporarily

    # The following iterates over each possible mvmt model path and check if selected
    for row in range(list_model.rowCount()):
        item = list_model.item(row)
        if item:
            is_selected = item.data(Qt.UserRole + udr.selectedrole)  # True if checked in the tree
            if is_selected:
                # item.text() is something like "Movement type>Perceptual shape>Shape>Other [this shape]"
                path_text = item.text()
                has_usr_text = path_text if '[' in path_text else has_usr_text
                path_text = update_path_text(has_usr_text, path_text)
                selected_paths.append(path_text)
    return selected_paths

# this method combines base path and surface/subarea/bonejoint
def gen_detailed_paths(base, surfaces, subdetails):
    if surfaces and subdetails:
        # one than one surfaces and subdetails (i.e., subarea or bone/joint) selected.
        return [f"{base}>{s}>{d}" for s, d in product(surfaces, subdetails)]
    elif surfaces:
        # only surface
        return [f"{base}>{s}" for s in surfaces]
    elif subdetails:
        return [f"{base}>{d}" for d in subdetails]
    else:
        return [f"{base}"]


# retrieve location path while treating surface and subarea as if they are paths
def get_detailed_checked_paths_location(treemodel):
    # Each LocationModule has a .locationtreemodel, which in turn has a .listmodel
    list_model = treemodel.listmodel
    detailed_paths = []  # this will be the output

    has_usr_text = ''  # to remember the most recent 'user text' temporarily

    # The following iterates over each possible location model path and check if selected
    for row in range(list_model.rowCount()):
        item = list_model.item(row)
        if not item:
            continue

        if not item.data(Qt.UserRole + udr.selectedrole):  # False if not checked in the tree
            continue

        # item.text() is something like "Movement type>Perceptual shape>Shape>Other [this shape]"
        path_text = item.text()
        has_usr_text = path_text if '[' in path_text else has_usr_text
        path_text = update_path_text(has_usr_text, path_text)

        treeitem = item.treeitem
        detailed_dict = treeitem.detailstable.get_checked_values()

        surfaces = detailed_dict.get('Surface', [])
        subdetails = (   # subdetails are either sub-area or bone/joint. they are mutually exclusive
            detailed_dict.get('Sub-area', []) +
            detailed_dict.get('Bone/joint', [])
        )

        detailed_paths.extend(gen_detailed_paths(path_text, surfaces, subdetails))

    return detailed_paths


def get_detailed_selections_orientation(ori) -> list:
    # ori: OrientationModule
    # extract Each OrientationModule has palm and finger root specifications: .palm and .root, respectively.

    # the nested function re-implements the logic of parsing Direction attributes
    def parse_dir(direc) -> str:
        # direc: Direction instance
        axis = direc.axis
        r = [axis.capitalize()]

        axis_labels = {   # mapping between plus minus and their meaning by each axis
            Direction.HORIZONTAL: ('Ipsilateral', 'Contralateral'),
            Direction.VERTICAL:   ('Up', 'Down'),
            Direction.SAGITTAL:   ('Proximal', 'Distal'),
        }

        plus_label, minus_label = axis_labels[axis]

        if direc.plus:
            r.append(plus_label)
        elif direc.minus:
            r.append(minus_label)

        if direc.inline:
            r.append("in line")

        return '>'.join(r)

    res = []
    palm = ori.palm
    root = ori.root

    for p in palm:
        if p.axisselected:
            palm_text = 'Direction of palm'
            this_selection = parse_dir(p)
            res.append(f'{palm_text}>{this_selection}')

    for ro in root:
        if ro.axisselected:
            root_text = 'Direction of finger root'
            this_selection = parse_dir(ro)
            res.append(f'{root_text}>{this_selection}')

    return res


# extract handshape slots hierarchically for hand configuration comparison
def extract_handshape_slots(hcm, linear=False):
    # hcm: HandConfigurationModule

    def linearize(obj, path=''):
        paths = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k:
                    new_path = f"{path}>{k}" if path else k
                else:
                    new_path = path
                paths.extend(linearize(v, new_path))

        elif isinstance(obj, list):
            for item in obj:
                paths.extend(linearize(item, path))

        else:  # Base case
            final_path = f"{path}>{obj}" if path else obj
            paths.append(final_path)

        return paths

    res = {}
    for field in hcm:
        field_num = field['field_number']
        this_field_details = ConfigField(field_num)
        for slot, slot_info in zip(this_field_details, field['slots']):
            # slot is a ConfigSlot object (empty slot template) Useful properties in it and examples:
            # slot.field_type 'thumb'
            # slot.num '3'
            # slot.slot_type 'thumb abduction/adduction (CM adduction)'
            #
            # slot_info is the specified slot information in Sign at hand
            this_field_name = f'{field_num} {slot.field_type.capitalize()}'

            if slot.slot_type == '':
                continue

            if this_field_name not in res:
                res[this_field_name] = []

            res[this_field_name].append({slot.slot_type: slot_info['symbol']})

    if linear:
        return linearize(res)
    return res


#  Traverse the path and return the button types of each element in the path.
def get_btn_type_for_path(module_type, path, root_node):
    # btn_types are in two types: basic and additional
    # basic types are radio_button and checkbox, which are decided by the module spec gui
    # additional types are 'major loc' and 'autogen label'
    #
    # basic btn_types are needed because mismatching rb's and cb's are treated differently in sign comparison
    # mismatching rb's with same parents are aligned and painted red, while mismatching cb's are in yellow separately.
    #
    # 'major loc' matters in Location Comparison. Such as 'Body anchored,' or ' Purely Spatial,'
    # where two lines are always aligned even if they mismatch
    # 'autogen label' (automatically generated label) relates to handconfig comparision. it should be transparent when
    # expanded.

    parts = path.split('>')
    btn_types = []  # this will be the output

    if module_type == 'handconfig':
        # by default, all lines should be transparent when expanded,
        # except the terminal line.
        # the line 'Handshape' per se should be 'major loc' because the two correspondents should always align.
        part_len = len(parts) - 1
        for i, part in enumerate(parts):
            part = part.lower()
            this_btn = 'autogen label'
            if i == part_len:  # terminal
                this_btn = 'radio button'
            elif 'handshape' in part:
                this_btn = 'major loc'
            btn_types.append(this_btn)
        return '>'.join(btn_types)

    elif module_type == 'signtype':
        # by default, all lines should preserve colours when expanded,
        # except for category names (category names not implemented)

        #btn_types = ['major loc']
        #for i, part in enumerate(parts[2:]):

        for i, part in enumerate(parts[1:]):    # [1:] because the 'Sign type' part is the top level and do not count.

            btn_types.append('radio button')
        return '>'.join(btn_types)

    def traverse(path_parts: list, node):
        if not path_parts:
            return True  # Reached the end successfully
        # .partition splits at the ' [' juncture, effectively removing any '[....]' part i.e., user's lineEdit input
        part = path_parts[0].partition(' [')[0]

        # First, check if the current node's children have the desired part
        matching_child = None
        for child in node.children:   # node: XXOptionsNode, node.children: list of XXOptionsNodes
            if child.display_name == part:
                matching_child = child
                break

        if matching_child:   # matching_children is a XXOptionsNode instance, with .button_type
            # temporary solution: if user specified, just return radiobutton
            if part != path_parts[0]:
                btn_types.append('radio button')
            else:
                btn_types.append(matching_child.button_type)
            return traverse(path_parts[1:], matching_child)
        else:
            # Recursively search in all children
            for child in node.children:
                if traverse(path_parts, child):
                    return True
            return False  # Not found in this branch

    found = traverse(parts, root_node)

    if found:
        return '>'.join(btn_types)
    else:
        return 'Path not found'


# it parses 'button_type' information created by get_btn_type_for_path()
def parse_button_type(node_data: dict, k: str = ''):
    def pick_btn_type(branch: dict):
        if not isinstance(branch, dict):
            return []
        if 'button_type' in branch:
            return branch['button_type'].split('>')
        for child in branch.values():
            if isinstance(child, dict):
                hit = pick_btn_type(child)
                if hit:
                    return hit
        return []

    # fallback. if k is not given
    if not k:
        return pick_btn_type(node_data)

    # regular cases
    elif k in node_data:
        return pick_btn_type(node_data[k])

    for child in node_data.values():
        if isinstance(child, dict):
            hit = parse_button_type(child, k)
            if hit:
                return hit
    return []


def rb_red_buttons(children: list, parents: list, should_paint_red, yellow_brush):
    # helper function that colours children and their parents which are all CompareTreeWidgetItem objects
    # children, parents: lists of CompareTreeWidgetItem
    # should_paint_red: list.
    # yellow_brush: QBrush object to check for parent's colour
    # called only if
    # - both items in children are radiobuttons but not identical
    # - identical parents
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


# parses the whitespace-separated components of a handshape's predefined name into bases and variants
def get_bases_and_variants(components):
    b = []
    v = []
    combined_base_processed = False
    for component in components:
        if '+' in component:
            b = [c for c in component.split('+')]
            combined_base_processed = True
        else:
            v.append(component)
    if not combined_base_processed:
        b = components[-1]  # if no multiple bases, then the last in components should be the only base
    return b, v


# it parses one sign's handshape predefined name into bases and variants.
def parse_predefined_names(pred_name: str, viz_name: str, counterpart_name: str) -> list:
    # pred_name: str. predefined_names like 'extended A'
    # viz_name: str. the handshape name visible to the user in the form of "name ([slots])"
    # returns list of strings

    def in_path_form():
        return [f'Handshape: {viz_name}>{category_name}>{detail}'
                for category_name, category in [('Base', bases), ('Variant', variants)]
                for detail in category]

    bases = []
    variants = []

    # very special case of 'combined ILY'
    pred_name, counterpart_name = map(lambda name: 'combined I+L+Y' if name == 'combined ILY' else name,
                                      (pred_name, counterpart_name))

    pname_comp = pred_name.split(' ')

    # process 'combined'
    if 'combined' in pname_comp:
        # combination of two or more bases
        bases, variants = get_bases_and_variants(pname_comp)
        counterpart_bases, _ = get_bases_and_variants(counterpart_name.split(' '))

        # align bases
        if bases != counterpart_bases:
            order = {v: i for i, v in enumerate(counterpart_bases)}  # because there is only one instance of base
            bases = sorted(bases, key=lambda b: (b not in order, order.get(b, float('inf'))))  # unique base to the back

        return in_path_form()

    # process 'variants'
    if 'index' in pname_comp:
        # first 'index' is variant of variants. it appears at the end of the name, unlike other variants.
        # so it should switch seats with the 'base'
        pname_comp[-2], pname_comp[-1] = pname_comp[-1], pname_comp[-2]

    # the last of pname_comp is always the base name except for 'middle finger'
    if pred_name == 'middle finger':
        bases.append(pred_name)
        return in_path_form()
    else:
        bases.append(pname_comp.pop())

    # variants delimited by space
    variants.extend(pname_comp)

    return in_path_form()

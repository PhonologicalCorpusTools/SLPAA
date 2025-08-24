from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes, BodypartInfo, MovementModule, LocationModule, RelationModule
from models.location_models import locn_options_body, locn_options_hand, locn_options_purelyspatial
from compare_signs.compare_helpers import (analyze_modules, extract_handshape_slots, parse_predefined_names,
                                           summarize_path_comparison, get_informative_elements, compare_elements,
                                           get_btn_type_for_path, get_checked_paths_from_list,
                                           get_detailed_checked_paths_location, get_detailed_selections_orientation)
from compare_signs.align_modules import alignmodules
from constant import PREDEFINED_MAP  # for predefined hand config name

PREDEFINED_MAP = {handshape.canonical: handshape for handshape in PREDEFINED_MAP.values()}


class CompareModel:
    def __init__(self, sign1, sign2):
        self.sign1 = sign1
        self.sign2 = sign2
        self.implemented = ['handconfig', 'movement', 'location', 'orientation']
        self.yet_to_implement = ['relation', 'nonmanual']

    # this is the main compare function that dispatches each module comparison!
    def compare_sign_pair(self, options) -> tuple[dict, list]:
        result = {'sign1': {}, 'sign2': {}}  # this is the output

        # signtype comparison before all module comparisons
        signtype_comparison_results = self.compare_signtype(options)
        result['sign1']['Sign type'] = {
            k: v for d in signtype_comparison_results['sign1'] for k, v in d.items()
        }
        result['sign2']['Sign type'] = {
            k: v for d in signtype_comparison_results['sign2'] for k, v in d.items()
        }

        # list of modules to compare
        module_attributes = [attr for attr in dir(self.sign1) if attr.endswith('modules')]
        module_attributes = [attr for attr in module_attributes if not callable(getattr(self.sign1, attr))]

        never_implement = ['handpart']
        clean_module_lists = self.module_list_helper([self.implemented, self.yet_to_implement, never_implement])
        implemented_modules, yet_to_implement_modules, never_implement_modules = clean_module_lists
        known_modules = [component_module for sublist in clean_module_lists for component_module in sublist]
        del clean_module_lists

        # if signs do not include required modules, stop the process
        missing_modules = [m for m in known_modules if m not in module_attributes]
        if missing_modules:
            raise ValueError(f"Sign comparison couldn't find these modules -- {', '.join(missing_modules)}")

        # future proofing: if the signs contain a unknown module, prompt a warning message
        unknown_modules = [m for m in module_attributes if m not in known_modules]

        # strict order of module comparison.
        module_comparison_results = {
            'Handconfig': self.compare_handconfigs(options['handconfig']),
            'Movement': self.compare_movements(),
            'Location': self.compare_locations(),
            #'Relation': self,   # not impplemented yet
            'Orientation': self.compare_orientations(),
            #'Nonmanual': self,  # not implemented yet
        }

        for module_name, comparison in module_comparison_results.items():
            result['sign1'][module_name] = {
                k: {key: value for d in v for key, value in d.items()}
                for k, v in comparison['sign1'].items()
            }
            result['sign2'][module_name] = {
                k: {key: value for d in v for key, value in d.items()}
                for k, v in comparison['sign2'].items()
            }

        return result, unknown_modules

    def module_list_helper(self, module_list) -> list:
        suffix = "modules"
        if isinstance(module_list[0], list):
            r = []
            for nested in module_list:
                r.append(self.module_list_helper(nested))
            return r
        return [f"{name}{suffix}" for name in module_list]

    def get_module_labels(self, module_pair: tuple) -> (str, str):
        try:
            module1_label = self.sign1.getmoduleabbreviation(module_pair[0])
        except KeyError:
            module1_label = None
        try:
            module2_label = self.sign2.getmoduleabbreviation(module_pair[1])
        except KeyError:
            module2_label = None

        return module1_label, module2_label

    def compare_signtype(self, options) -> dict:
        results1, results2 = [], []
        if self.sign1.signtype is None or self.sign2.signtype is None:
            return {'sign1': {}, 'sign2': {}}
        s1path = self.parse_st_representations(self.sign1.signtype.specslist)
        s2path = self.parse_st_representations(self.sign2.signtype.specslist)

        s1_path_element = get_informative_elements(s1path)
        s2_path_element = get_informative_elements(s2path)

        s1_path_btn_types = {
            path: get_btn_type_for_path('signtype', path, None) for path in s1_path_element
        }
        s2_path_btn_types = {
            path: get_btn_type_for_path('signtype', path, None) for path in s2_path_element
        }

        finished_roots = []

        for e1 in s1_path_element:
            matched = False
            for e2 in s2_path_element:
                if e1.split('>')[0] == e2.split('>')[0]:  # Compare only if they share the same root
                    matched = True
                    finished_roots.append(e2.split('>')[0])
                    res1, res2 = compare_elements(
                        e1=e1,
                        e2=e2,
                        btn_types1=s1_path_btn_types,
                        btn_types2=s2_path_btn_types,
                        pairwise=True
                    )
                    results1.append(res1)
                    results2.append(res2)

            if not matched:
                res1, _ = compare_elements(e1, '', s1_path_btn_types, {}, pairwise=False)
                results1.append(res1)

        for e2 in s2_path_element:
            if e2.split('>')[0] not in finished_roots:
                _, res2 = compare_elements('', e2, {}, {}, pairwise=False)
                results2.append(res2)

        results1 = summarize_path_comparison(results1)
        results2 = summarize_path_comparison(results2)

        return {'sign1': results1, 'sign2': results2}

    def parse_st_representations(self, signtype_specs: list):
        hands = []
        arms = []
        legs = []
        for spec in signtype_specs:
            # articulator number actively unspecified
            if 'Unspecified' in spec:
                whats_unspecified = spec.split('_')[1]
                if 'hands' in whats_unspecified:
                    hands.append('Unspecified')
                elif 'arms' in whats_unspecified:
                    arms.append('Unspecified')
                elif 'legs' in whats_unspecified:
                    legs.append('Unspecified')
                continue

            # default case: articulator specified
            descriptions_list = spec.split('.')
            articulator, *descriptors = descriptions_list
            descriptions = '>'.join(descriptors) if len(descriptors) > 0 else None


            # parse articulator info e.g., 1h, 2l, etc
            articulator_fullname = {'h': 'hand', 'a': 'arm', 'l': 'leg'}

            articulator_count, articulator_shortname = articulator
            if articulator_count == '1':
                art_discription = f'One {articulator_fullname[articulator[1]]}'
            elif articulator_count == '2':
                art_discription = f'Two {articulator_fullname[articulator[1]]}s'
            _ = [art_discription, descriptions]
            descriptions = '>'.join([element for element in _ if element is not None])

            if articulator_shortname == 'h':
                hands.append(descriptions)
            elif articulator_shortname == 'a':
                arms.append(descriptions)
            elif articulator_shortname == 'l':
                legs.append(descriptions)

        result = []
        for label, specs in (("Hands", hands), ("Arms", arms), ("Legs", legs)):
            for s in specs:
                result.append(f"{label}>{s}")

        return result

    def compare_movements(self) -> dict:
        def compare_module_pair(pair: tuple, pairwise: bool = True) -> (list, list):
            # pair = pair of movementModule
            # pairwise = False if not comparing one pair
            # return tuple of two dict each contains true or false at each level of granularity
            results1 = []
            results2 = []

            # articulator comparison
            # no more articulator comparison due to compare on aligned
            # (articulators are already taken into consideration in sign align!)

            # path comparison
            s1path = get_checked_paths_from_list(pair[0].movementtreemodel)
            s2path = get_checked_paths_from_list(pair[1].movementtreemodel)

            s1_path_element = get_informative_elements(s1path)
            s2_path_element = get_informative_elements(s2path)

            s1_path_btn_types = {
                path: get_btn_type_for_path('mvmt', path, pair[0].movementtreemodel.optionstree) for path in s1_path_element
            }
            s2_path_btn_types = {
                path: get_btn_type_for_path('mvmt', path, pair[1].movementtreemodel.optionstree) for path in s2_path_element
            }

            finished_roots = []  # to track compared roots

            for e1 in s1_path_element:
                matched = False
                for e2 in s2_path_element:
                    if e1.split('>')[0] == e2.split('>')[0]:  # Compare only if they share the same root
                        matched = True
                        finished_roots.append(e2.split('>')[0])
                        res1, res2 = compare_elements(
                            e1=e1,
                            e2=e2,
                            btn_types1=s1_path_btn_types,
                            btn_types2=s2_path_btn_types,
                            pairwise=pairwise
                        )
                        results1.append(res1)
                        results2.append(res2)

                if not matched:
                    res1, _ = compare_elements(e1, '', s1_path_btn_types, {}, pairwise=False)
                    results1.append(res1)

            for e2 in s2_path_element:
                if e2.split('>')[0] not in finished_roots:
                    _, res2 = compare_elements('', e2, {}, {}, pairwise=False)
                    results2.append(res2)

            results1 = summarize_path_comparison(results1)
            results2 = summarize_path_comparison(results2)
            return results1, results2

        aligned_modules = alignmodules(self.sign1, self.sign2, moduletype=ModuleTypes.MOVEMENT)

        pair_comparison = {'sign1': {}, 'sign2': {}}  # compare results stored here and to be returned

        for i, module in enumerate(aligned_modules):
            sign1_module_label, sign2_module_label = self.get_module_labels(module)

            if all(module):  # pair of modules
                r_sign1, r_sign2 = compare_module_pair(module)
                pair_comparison['sign1'][str(i) + ':' + sign1_module_label] = r_sign1  # the key is like '0:Mov1'
                pair_comparison['sign2'][str(i) + ':' + sign2_module_label] = r_sign2  # int preceding : is for aligning when drawing trees
            elif module[0]:  # only sign 1 has this module
                r_sign1, _ = compare_module_pair((module[0], module[0]), pairwise=False)
                pair_comparison['sign1'][str(i) + ':' + sign1_module_label] = r_sign1
            else:            # only sign 2 has this module
                _, r_sign2 = compare_module_pair((module[1], module[1]), pairwise=False)
                pair_comparison['sign2'][str(i) + ':' + sign2_module_label] = r_sign2

        return pair_comparison

    def compare_locations(self) -> [bool]:
        # ad hoc solution to add major location (e.g., Body > Body)
        # on top of the hierarchical comparison results
        def add_major_loc(compare_result_dict: dict, loc_type) -> dict:
            # compare_result_dict: dict. hierarchical structure representing a Sign's loc modules
            #   and its comparison to the other Sign
            # loc_type: LocationType object. to specify between "Body," "BodyAnchored," "PurelySpacial"

            # Add major location to existing dict
            if loc_type._body:
                r = {'Body': {'Body': compare_result_dict}}
            elif loc_type._bodyanchored:
                r = {'Signing space': {'Body anchored': compare_result_dict}}
            elif loc_type._purelyspatial:
                r = {'Signing space': {'Purely spatial': compare_result_dict}}
            else:
                print("[DEBUG] Major location type unspecified.")
                return {}

            # Add btn info
            modify_button_type = lambda d: (
                d.update({'button_type': f"major loc>major loc>{d['button_type']}"}) if 'button_type' in d else
                [modify_button_type(v) for v in d.values() if isinstance(v, dict)]
            )
            modify_button_type(r)
            return r

        def compare_module_pair(pair: tuple, pairwise: bool = True) -> (list, list):
            # pair = tuple of LocationModules
            # pairwise = False if not comparing one pair
            # return tuple of two dict each contains true or false at each level of granularity
            results1 = []
            results2 = []

            # paths
            s1path = get_detailed_checked_paths_location(pair[0].locationtreemodel)
            s2path = get_detailed_checked_paths_location(pair[1].locationtreemodel)
            s1_path_element = get_informative_elements(s1path)
            s2_path_element = get_informative_elements(s2path)

            # get button types
            s1_location_type = pair[0].locationtreemodel.locationtype
            s2_location_type = pair[1].locationtreemodel.locationtype

            # start debug just to identify the class selection
            what_selected = []
            if s1_location_type._body:
                what_selected.append('Body')
            elif s1_location_type._bodyanchored:
                what_selected.append('Signing space > BodyAnchored')
            elif s1_location_type._purelyspatial:
                what_selected.append('Signing space > PurelySpatial')
            if s2_location_type._body:
                what_selected.append('Body')
            elif s2_location_type._bodyanchored:
                what_selected.append('Signing space > BodyAnchored')
            elif s2_location_type._purelyspatial:
                what_selected.append('Signing space > PurelySpatial')
            del what_selected

            if s1_location_type.usesbodylocations():
                s1_root_node = locn_options_body
            elif s1_location_type.purelyspatial:
                s1_root_node = locn_options_purelyspatial

            if s2_location_type.usesbodylocations():
                s2_root_node = locn_options_body
            elif s2_location_type.purelyspatial:
                s2_root_node = locn_options_purelyspatial

            s1_path_btn_types = {
                path: get_btn_type_for_path("locn", path, s1_root_node) for path in s1_path_element
            }
            s2_path_btn_types = {
                path: get_btn_type_for_path("locn", path, s2_root_node) for path in s2_path_element
            }

            finished_roots = []  # to track compared roots
            for e1 in s1_path_element:
                matched = False
                for e2 in s2_path_element:
                    if e1.split('>')[0] == e2.split('>')[0]:  # Compare only if they share the same root
                        matched = True
                        finished_roots.append(e2.split('>')[0])
                        res1, res2 = compare_elements(
                            e1=e1,
                            e2=e2,
                            btn_types1=s1_path_btn_types,
                            btn_types2=s2_path_btn_types,
                            pairwise=pairwise
                        )
                        res1 = add_major_loc(res1, s1_location_type)
                        res2 = add_major_loc(res2, s2_location_type)
                        results1.append(res1)
                        results2.append(res2)

                if not matched:
                    res1, _ = compare_elements(e1, '', {}, {}, pairwise=False)
                    res1 = add_major_loc(res1, s1_location_type)
                    results1.append(res1)

            for e2 in s2_path_element:
                if e2.split('>')[0] not in finished_roots:
                    _, res2 = compare_elements('', e2, {}, {}, pairwise=False)
                    res2 = add_major_loc(res2, s2_location_type)
                    results2.append(res2)

            results1 = summarize_path_comparison(results1)
            results2 = summarize_path_comparison(results2)
            return results1, results2

        aligned_modules = alignmodules(self.sign1, self.sign2, ModuleTypes.LOCATION)

        pair_comparison = {'sign1': {}, 'sign2': {}}

        for i, module in enumerate(aligned_modules):
            sign1_module_label, sign2_module_label = self.get_module_labels(module)

            if all(module):  # pair of modules
                r_sign1, r_sign2 = compare_module_pair(module)
                pair_comparison['sign1'][str(i) + ':' + sign1_module_label] = r_sign1  # the key is like '0:Mov1'
                pair_comparison['sign2'][str(i) + ':' + sign2_module_label] = r_sign2  # int preceding : is for aligning when drawing trees
            elif module[0]:  # only sign 1 has this module
                r_sign1, _ = compare_module_pair((module[0], module[0]), pairwise=False)
                pair_comparison['sign1'][str(i) + ':' + sign1_module_label] = r_sign1
            else:            # only sign 2 has this module
                _, r_sign2 = compare_module_pair((module[1], module[1]), pairwise=False)
                pair_comparison['sign2'][str(i) + ':' + sign2_module_label] = r_sign2

        return pair_comparison

    def compare_orientations(self) -> [bool]:
        def compare_module_pair(pair: tuple, pairwise: bool = True) -> (list, list):
            # pair = tuple of OrientationModules
            # pairwise = False if not comparing one pair
            # return tuple of two dict each contains true or false at each level of granularity
            results1 = []
            results2 = []

            # paths
            s1path = get_detailed_selections_orientation(pair[0])
            s2path = get_detailed_selections_orientation(pair[1])
            s1_path_element = get_informative_elements(s1path)
            s2_path_element = get_informative_elements(s2path)

            finished_roots = []  # to track compared roots
            for e1 in s1_path_element:
                matched = False
                for e2 in s2_path_element:
                    if e1.split('>')[0] == e2.split('>')[0]:  # Compare only if they share the same root
                        matched = True
                        res1, res2 = compare_elements(
                            e1=e1,
                            e2=e2,
                            btn_types1={},
                            btn_types2={},
                            pairwise=pairwise
                        )
                        results1.append(res1)
                        results2.append(res2)

                if not matched:
                    res1, _ = compare_elements(e1, '', {}, {}, pairwise=False)
                    results1.append(res1)

            for e2 in s2_path_element:
                if e2.split('>')[0] not in finished_roots:
                    _, res2 = compare_elements('', e2, {}, {}, pairwise=False)
                    results2.append(res2)

            results1 = summarize_path_comparison(results1)
            results2 = summarize_path_comparison(results2)
            return results1, results2

        aligned_modules = alignmodules(self.sign1, self.sign2, moduletype=ModuleTypes.ORIENTATION)

        pair_comparison = {'sign1': {}, 'sign2': {}}

        for i, module in enumerate(aligned_modules):
            sign1_module_label, sign2_module_label = self.get_module_labels(module)

            if all(module):  # pair of modules
                r_sign1, r_sign2 = compare_module_pair(module)
                pair_comparison['sign1'][str(i) + ':' + sign1_module_label] = r_sign1  # the key is like '0:Mov1'
                pair_comparison['sign2'][str(i) + ':' + sign2_module_label] = r_sign2  # int preceding : is for aligning when drawing trees
            elif module[0]:  # only sign 1 has this module
                r_sign1, _ = compare_module_pair((module[0], module[0]), pairwise=False)
                pair_comparison['sign1'][str(i) + ':' + sign1_module_label] = r_sign1
            else:            # only sign 2 has this module
                _, r_sign2 = compare_module_pair((module[1], module[1]), pairwise=False)
                pair_comparison['sign2'][str(i) + ':' + sign2_module_label] = r_sign2

        return pair_comparison

    def compare_handconfigs(self, options) -> dict:
        def compare_module_pair(pair: tuple, pairwise: bool = True, options: dict = None) -> (list, list):
            # pair = tuple of HandConfigurationModule
            # pairwise = False if not comparing one pair
            # return tuple of two dict. each contains true or false at each level of granularity
            results1 = []
            results2 = []

            s1_path_element = []
            s2_path_element = []

            sign1_hcm = pair[0]
            sign2_hcm = pair[1]

            sign1_slot_specs = sign1_hcm.config_tuple()  # tuple containing all (33) specified configuration value.
            sign2_slot_specs = sign2_hcm.config_tuple()

            # deal with forearm.
            s1_forearm_element = 'Forearm>Included' if sign1_hcm.overalloptions['forearm'] else 'Forearm>Not included'
            s2_forearm_element = 'Forearm>Included' if sign2_hcm.overalloptions['forearm'] else 'Forearm>Not included'

            s1_path_element.append(s1_forearm_element)
            s2_path_element.append(s2_forearm_element)

            # handshape name. used for direct comparison or as top-layer label.
            handshape_names = [''.join(sign1_slot_specs), ''.join(sign2_slot_specs)]

            predefined = [False, False]
            # if shorthand exists for handshape code, use it.
            str_visible_names = ['', '']  # string visible to the user as a handshape name
            if sign1_slot_specs in PREDEFINED_MAP:
                predefined[0] = True
                str_visible_names[0] = f"{PREDEFINED_MAP[sign1_slot_specs].name} ({handshape_names[0]})"
                handshape_names[0] = PREDEFINED_MAP[sign1_slot_specs].name

            if sign2_slot_specs in PREDEFINED_MAP:
                predefined[1] = True
                str_visible_names[1] = f"{PREDEFINED_MAP[sign2_slot_specs].name} ({handshape_names[1]})"
                handshape_names[1] = PREDEFINED_MAP[sign2_slot_specs].name

            # listen to 'options' and decide the comparison target
            if options['compare_target'] == 'predefined':
                # deal with predefined names
                if options['details']:
                    # base-variant hierarchy required
                    s1_path_element.extend(parse_predefined_names(pred_name=handshape_names[0],   # predefined name
                                                                  viz_name=str_visible_names[0],  # name that user sees
                                                                  counterpart_name=handshape_names[1]))
                    s2_path_element.extend(parse_predefined_names(pred_name=handshape_names[1],
                                                                  viz_name=str_visible_names[1],
                                                                  counterpart_name=handshape_names[0]
                                                                  ))
                else:
                    # not required
                    s1_path_element.append(f'Handshape: >{str_visible_names[0]}')
                    s2_path_element.append(f'Handshape: >{str_visible_names[1]}')

            else:
                # deal with handshape slots
                hand1_slots = extract_handshape_slots(hcm=sign1_hcm.handconfiguration, linear=True)
                hand2_slots = extract_handshape_slots(hcm=sign2_hcm.handconfiguration, linear=True)

                for path1, path2 in zip(hand1_slots, hand2_slots):
                    s1_path_element.append(f'Handshape: {str_visible_names[0]}>{path1}')
                    s2_path_element.append(f'Handshape: {str_visible_names[1]}>{path2}')

            # button types
            s1_path_btn_types = {
                path: get_btn_type_for_path("handconfig", path, None) for path in s1_path_element
            }
            s2_path_btn_types = {
                path: get_btn_type_for_path("handconfig", path, None) for path in s2_path_element
            }

            # quick patch to the btn_types
            # only the first child of Base should be radio button. other children should be checkbox
            for btn_types in [s1_path_btn_types, s2_path_btn_types]:
                first_child_flag = True
                for path_btn in btn_types.keys():
                    if '>Base' in path_btn and not first_child_flag:
                        path_chunks = btn_types[path_btn].split('>')
                        path_chunks[-1] = 'checkbox'
                        btn_types[path_btn] = '>'.join(path_chunks)
                    elif '>Base' in path_btn and first_child_flag:
                        first_child_flag = False

            # now start comparing
            finished_roots = []  # to track compared roots
            for e1 in s1_path_element:
                found_counterpart = False
                for e2 in s2_path_element:
                    if e1.split('>')[0] == e2.split('>')[0] or e1.split(' ')[0] == e2.split(' ')[0] == 'Handshape:':  # Compare only if they share the same root
                        found_counterpart = True
                        res1, res2 = compare_elements(
                            e1=e1,
                            e2=e2,
                            btn_types1=s1_path_btn_types,
                            btn_types2=s2_path_btn_types,
                            pairwise=pairwise
                        )
                        results1.append(res1)
                        results2.append(res2)
                        finished_roots.append(e2.split('>')[0])

                if not found_counterpart:
                    res1, _ = compare_elements(e1, '', {}, {}, pairwise=False)
                    results1.append(res1)

            for e2 in s2_path_element:
                if e2.split('>')[0] not in finished_roots:
                    _, res2 = compare_elements('', e2, {}, {}, pairwise=False)
                    results2.append(res2)

            results1 = summarize_path_comparison(results1)
            results2 = summarize_path_comparison(results2)
            return results1, results2

        aligned_modules = alignmodules(self.sign1, self.sign2, moduletype=ModuleTypes.HANDCONFIG)
        pair_comparison = {'sign1': {}, 'sign2': {}}

        for i, module in enumerate(aligned_modules):
            sign1_module_label, sign2_module_label = self.get_module_labels(module)

            if all(module):  # pair of modules
                r_sign1, r_sign2 = compare_module_pair(module, options=options)
                pair_comparison['sign1'][str(i) + ':' + sign1_module_label] = r_sign1  # the key is like '0:Mov1'
                pair_comparison['sign2'][str(i) + ':' + sign2_module_label] = r_sign2

            elif module[0]:  # only sign 1 has this module
                r_sign1, _ = compare_module_pair((module[0], module[0]), pairwise=False, options=options)
                pair_comparison['sign1'][str(i) + ':' + sign1_module_label] = r_sign1
            else:  # only sign 2 has this module
                _, r_sign2 = compare_module_pair((module[1], module[1]), pairwise=False, options=options)
                pair_comparison['sign2'][str(i) + ':' + sign2_module_label] = r_sign2

        return pair_comparison
    def compare_relation(self) -> dict:
        # not implemented
        pass

from PyQt5.QtCore import pyqtSignal, QObject
from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes, BodypartInfo, MovementModule, LocationModule, RelationModule
from models.location_models import locn_options_body, locn_options_hand, locn_options_purelyspatial
from compare_signs.compare_helpers import (analyze_modules, extract_handshape_slots, parse_predefined_names,
                                           summarize_path_comparison, get_informative_elements, compare_elements,
                                           get_btn_type_for_path, get_checked_paths_from_list,
                                           get_detailed_checked_paths_location, get_detailed_selections_orientation,
                                           inject_signtype_intermediates)
from compare_signs.align_modules import AlignModel
from constant import PREDEFINED_MAP  # for predefined hand config name

PREDEFINED_MAP = {handshape.canonical: handshape for handshape in PREDEFINED_MAP.values()}


class CompareModel(QObject):
    warning_signal = pyqtSignal(str)

    def __init__(self, sign1, sign2, parent=None):
        super().__init__(parent)
        self.sign1 = sign1
        self.sign2 = sign2
        self.alignmodel = AlignModel(self.sign1, self.sign2)
        self.implemented = ['handconfig', 'movement', 'location', 'orientation']
        self.yet_to_implement = ['relation', 'nonmanual']
        self._last_warn_msg = None

    # emit warnings
    def _warn(self, msg: str, dedupe=True):
        if dedupe and msg == self._last_warn_msg:  # do not prompt the same warning twice
            return
        self._last_warn_msg = msg
        self.warning_signal.emit(msg)

    # this is the main compare function that dispatches each module comparison!
    def compare_sign_pair(self, options) -> tuple[dict, list]:
        result = {'sign1': {}, 'sign2': {}}  # this is the output

        # signtype comparison before all module comparisons
        signtype_comparison_results = self.compare_signtype(options['signtype'])
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
            'Relation': self.compare_relation(),   # not impplemented yet
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
        s1_conflict_warning, s1path = self.parse_st_representations(self.sign1.signtype.specslist, merger=options['articulator_merger'])

        s2_conflict_warning, s2path = self.parse_st_representations(self.sign2.signtype.specslist,
                                                                    merger=options['articulator_merger'] if not s1_conflict_warning else False,
                                                                    )

        warning_msg_base = 'has more than one articulator. Multiple articulators in one sign cannot be abstracted over.'
        if s1_conflict_warning:
            # untoggle merge checkbox
            self._warn(msg=f'Sign 1 ({self.sign1.signlevel_information.idgloss}) {warning_msg_base}')
        if s2_conflict_warning:
            # impacts the opposite direction... better to rerun s1path
            s1_conflict_warning, s1path = self.parse_st_representations(self.sign1.signtype.specslist,
                                                                        merger=False)
            self._warn(msg=f'Sign 2 ({self.sign2.signlevel_information.idgloss}) {warning_msg_base}')
        del warning_msg_base

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

    def parse_st_representations(self, signtype_specs: list, merger: bool):
        hands = []
        arms = []
        legs = []
        conflict_flag = False   # True if articulator conflict
        conflict_warning = False
        abstract_articulator = []

        for spec in signtype_specs:
            if 'Unspecified' in spec:  # articulator number actively unspecified
                abstract_articulator.append('Unspecified')
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
            if merger:
                articulator_fullname = {'h': 'articulator', 'a': 'articulator', 'l': 'articulator'}
            articulator_count, articulator_shortname = articulator
            if articulator_count == '1':
                art_discription = f'One {articulator_fullname[articulator[1]]}'
            elif articulator_count == '2':
                art_discription = f'Two {articulator_fullname[articulator[1]]}s'
            _ = [art_discription, descriptions]
            descriptions = '>'.join([element for element in _ if element is not None])

            abstract_articulator.append(descriptions)  # in case of merging hands, arms and legs.

            if articulator_shortname == 'h':
                hands.append(descriptions)
            elif articulator_shortname == 'a':
                arms.append(descriptions)
            elif articulator_shortname == 'l':
                legs.append(descriptions)

        result = []

        specified_articulator_count = sum(bool(art) for art in (hands, arms, legs))
        if specified_articulator_count > 1:
            conflict_flag = True

        if merger and conflict_flag:
            conflict_warning = True

        if merger and not conflict_flag:
            for s in abstract_articulator:
                s = inject_signtype_intermediates(s)
                result.append(f'Articulator>{s}')
            return conflict_warning, result

        for label, specs in (("Hands", hands), ("Arms", arms), ("Legs", legs)):
            for s in specs:
                s = inject_signtype_intermediates(s)
                result.append(f"{label}>{s}")

        return conflict_warning, result

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

        aligned_modules, warningstring = self.alignmodel.alignmodules(ModuleTypes.MOVEMENT)
        if warningstring:
            self._warn(warningstring)

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

        aligned_modules, warningstring = self.alignmodel.alignmodules(ModuleTypes.LOCATION)
        if warningstring:
            self._warn(warningstring)

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

        aligned_modules, warningstring = self.alignmodel.alignmodules(ModuleTypes.ORIENTATION)
        if warningstring:
            self._warn(warningstring)

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

        aligned_modules, warningstring = self.alignmodel.alignmodules(ModuleTypes.HANDCONFIG)
        if warningstring:
            self._warn(warningstring)
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
        def _parse_articulator_XY(raw_rel, bodyparts_dict):
            # to convert front <--> back
            articulator_flags = {'Both hands': 'hboth',  'H1':   'h1',    'H2':   'h2',
                                 'Both arms':  'aboth',  'Arm1': 'arm1',  'Arm2': 'arm2',
                                 'Both legs':  'lboth',  'Leg1': 'leg1',  'Leg2': 'leg2'}
            articulator_front = {'h': 'H', 'a': 'Arm', 'l': 'Leg'}

            path = []  # this will be returned

            rel_type = type(raw_rel).__name__[-1]  # 'X' or 'Y'
            selected_articulator = next(k for k, attr in articulator_flags.items() if getattr(raw_rel, attr, False))
            articulator_code = articulator_flags[selected_articulator]  # e.g., 'h1', 'hboth', 'lboth'
            articulator_type = articulator_front[articulator_code[0]]
            articulator_type_intermediate = 'Hand selected' if articulator_type == 'H' \
                else f'{articulator_type} selected'

            list_by_art_module = (    # this will have two elements if '..both' or one if 'h1', 'h2', etc.
                [f'{articulator_type}{i}' for i in (2, 1)]
                if articulator_code.endswith('both') else [selected_articulator]
            )

            for single_articulator in list_by_art_module:
                parts = [rel_type, articulator_type_intermediate, single_articulator]
                bodypart = bodyparts_dict.get(f'{single_articulator}')
                if bodypart:
                    parts.append(bodypart)
                path.append('>'.join(parts))

            return path

        def convert_to_path(sign, upstream) -> list:

            # Distance
            path = ['Distance']

            distance_raw = sign.contactrel.distances  # list

            for d in distance_raw:
                close = d.close
                med = d.medium
                far = d.far
                flag = {
                    'Close': close,
                    'Medium': med,
                    'Far': far
                }
                if any(flag.values()):
                    axis = d.axis
                    specified = next(key for key, value in flag.items() if value)
                    path.append(f'Distance>{axis}>{specified}')

            # direction
            direction_raw = sign.directions
            direction_spec_bool = [d.axisselected for d in direction_raw]
            if any(direction_spec_bool):
                for i, b in enumerate(direction_spec_bool):
                    if not b:
                        continue
                    direction = direction_raw[i]
                    direction_abbr = direction.getabbreviation()
                    to_append = f'Direction>{direction.axis}'

                    if direction_abbr != 'any':
                        to_append += f'>{direction_abbr}'
                    path.append(to_append)

            cross_linked_raw = [sign.xy_crossed, sign.xy_linked]
            if cross_linked_raw[1]:
                path.append(f'Direction>X and Y are linked')
            if cross_linked_raw[0]:
                path.append(f'Direction>X and Y are crossed')

            # contact
            contact_raw = sign.contactrel
            if contact_raw.contact:  # bool
                to_append = 'Contact>Contact'

                # check for further specifications
                contacttype_types = ['light', 'firm', 'other']


                selected_contacttype = next(
                    (t for t in contacttype_types    # for each possible contact type
                     if getattr(contact_raw.contacttype, t, False)),  # check whether selected
                    None  # fallback case
                )

                if selected_contacttype:
                    to_append += f'>{selected_contacttype}'
                path.append(to_append)

                # now contact manner
                contactmanner_types = ['continuous', 'holding', 'intermittent']
                selected_manner = next(
                    (t for t in contactmanner_types    # for each possible type
                     if getattr(contact_raw.manner, t, False)),  # check whether selected
                    None  # fallback case
                )
                if selected_manner:
                    path.append(f'Contact>Contact>Manner>{selected_manner}')
            else:
                path.append('Contact>No contact')

            # optional body parts to be attached to X or Y
            bodyparts_raw = sign.bodyparts_dict
            bodyparts_dict = {}
            for art in bodyparts_raw.values():
                bodypart_art = art[1].bodyparttreemodel.bodyparttype
                bodypart_art = bodypart_art[0] if bodypart_art == 'Hand' else bodypart_art
                bodypart_art += '1'
                for bp_tree in art[1].bodyparttreemodel.checked:
                    bodyparts_dict[f'{bodypart_art}'] = bp_tree

                bodypart_art = art[2].bodyparttreemodel.bodyparttype
                bodypart_art = bodypart_art[0] if bodypart_art == 'Hand' else bodypart_art
                bodypart_art += '2'

                for bp_tree in art[2].bodyparttreemodel.checked:
                    bodyparts_dict[f'{bodypart_art}'] = bp_tree

            # Y
            Y_raw = sign.relationy
            if Y_raw.existingmodule:
                # Y is connected to an existing module and is either location or movement
                linked_modules = getattr(upstream, f'{Y_raw.linkedmoduletype}modules')
                for _, m in linked_modules.items():
                    path.append(f'Y>Existing module>{m.moduletype}>{m.getabbreviation()}')
            else:
                artipath_list = _parse_articulator_XY(raw_rel=Y_raw, bodyparts_dict=bodyparts_dict)
                path.extend(artipath_list)

            # X
            X_raw = sign.relationx
            artipath_list = _parse_articulator_XY(raw_rel=X_raw, bodyparts_dict=bodyparts_dict)
            path.extend(artipath_list)

            return path

        def compare_module_pair(pair: tuple, upstream, pairwise: bool = True) -> (list, list):
            # pair: pair of relationModule
            # upstream: tuple of two Sign objects
            # relation module has relatively fixed set of sub-modules.
            # X, Y, Contact, Body parts, Distance between X and Y
            sign1 = pair[0]  # RelationModule
            sign2 = pair[1]
            results1 = []
            results2 = []
            sign1_upstream, sign2_upstream = upstream

            # for sign1
            s1path = convert_to_path(sign1, sign1_upstream)

            # for sign2
            s2path = convert_to_path(sign2, sign2_upstream)

            s1_path_element = get_informative_elements(s1path)
            s2_path_element = get_informative_elements(s2path)

            # btn types for colouring and collapsing.
            s1_path_btn_types = {
                path: get_btn_type_for_path('rel', path, None) for path in s1_path_element
            }
            s2_path_btn_types = {
                path: get_btn_type_for_path('rel', path, None) for path in s2_path_element
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



        signpair = (self.sign1, self.sign2)

        # currently, compare modules naively. eventually, it should compare aligned modules as the line below!
        # aligned_modules, warningstring = self.alignmodel.alignmodules(ModuleTypes.RELATION)

        # --- for now, assume all relation modules are properly aligned already.
        pair_comparison = {'sign1': {}, 'sign2': {}}  # compare results stored here and to be returned

        if len(self.sign1.relationmodules) + len(self.sign1.relationmodules) == 0:
            return pair_comparison

        sign1_relmodule = list(self.sign1.relationmodules.values())
        sign1_relmodule_count = len(sign1_relmodule)

        sign2_relmodule = list(self.sign2.relationmodules.values())
        sign2_relmodule_count = len(sign2_relmodule)

        aligned_modules = []

        for i in range(max(sign1_relmodule_count, sign2_relmodule_count)):
            value1 = sign1_relmodule[i] if i < len(sign1_relmodule) else None
            value2 = sign2_relmodule[i] if i < len(sign2_relmodule) else None
            aligned_modules.append((value1, value2))
        # --- end

        for i, module in enumerate(aligned_modules):
            sign1_module_label, sign2_module_label = self.get_module_labels(module)

            if all(module):  # pair of modules
                r_sign1, r_sign2 = compare_module_pair(module, upstream=signpair)
                pair_comparison['sign1'][str(i) + ':' + sign1_module_label] = r_sign1  # the key is like '0:Mov1'
                pair_comparison['sign2'][str(i) + ':' + sign2_module_label] = r_sign2  # int preceding : is for aligning when drawing trees
            elif module[0]:  # only sign 1 has this module
                r_sign1, _ = compare_module_pair((module[0], module[0]), upstream=signpair, pairwise=False)
                pair_comparison['sign1'][str(i) + ':' + sign1_module_label] = r_sign1
            else:            # only sign 2 has this module
                _, r_sign2 = compare_module_pair((module[1], module[1]), upstream=signpair, pairwise=False)
                pair_comparison['sign2'][str(i) + ':' + sign2_module_label] = r_sign2

        return pair_comparison

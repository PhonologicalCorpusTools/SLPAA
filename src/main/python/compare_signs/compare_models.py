from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes, BodypartInfo, MovementModule, LocationModule, RelationModule
from models.location_models import locn_options_body, locn_options_hand, locn_options_purelyspatial
from search.helper_functions import relationdisplaytext, articulatordisplaytext, phonlocsdisplaytext, loctypedisplaytext, signtypedisplaytext, module_matches_xslottype
from compare_signs.compare_helpers import (analyze_modules, get_informative_elements,
                                           compare_elements, summarize_path_comparison,
                                           get_btn_type_for_path, get_checked_paths_from_list,
                                           get_detailed_checked_paths_location, get_detailed_selections_orientation)
from compare_signs.align_modules import alignmodules

# for temporarily showing debug info
from PyQt5.QtWidgets import QMessageBox


class CompareModel:
    def __init__(self, sign1, sign2):
        self.sign1 = sign1
        self.sign2 = sign2

    # this is the main compare function that dispatches each module comparison!
    def compare(self) -> dict:
        # list of modules to compare
        module_attributes = [attr for attr in dir(self.sign1) if attr.endswith('modules')]
        module_attributes = [attr for attr in module_attributes if not callable(getattr(self.sign1, attr))]

        result = {'sign1': {}, 'sign2': {}}

        for module in module_attributes:
            if 'movement' in module:
                mvmt_res = self.compare_movements()
                # For 'sign1'
                result['sign1']['movement'] = {
                    k: {key: value for d in v for key, value in d.items()}
                    for k, v in mvmt_res['sign1'].items()
                }

                # For 'sign2'
                result['sign2']['movement'] = {
                    k: {key: value for d in v for key, value in d.items()}
                    for k, v in mvmt_res['sign2'].items()
                }

            elif 'location' in module:
                loc_res = self.compare_locations()
                # For 'sign1'
                result['sign1']['location'] = {
                    k: {key: value for d in v for key, value in d.items()}
                    for k, v in loc_res['sign1'].items()
                }

                # For 'sign2'
                result['sign2']['location'] = {
                    k: {key: value for d in v for key, value in d.items()}
                    for k, v in loc_res['sign2'].items()
                }

            elif 'relation' in module:
                #reln_res = self.compare_relation()
                #result['relation'] = reln_res
                #print(f'relation_compare:{reln_res}')
                pass
            elif 'orientation' in module:
                ori_res = self.compare_orientations()
                # For 'sign1'
                result['sign1']['orientation'] = {
                    k: {key: value for d in v for key, value in d.items()}
                    for k, v in ori_res['sign1'].items()
                }
                # and for 'sign2'
                result['sign2']['orientation'] = {
                    k: {key: value for d in v for key, value in d.items()}
                    for k, v in ori_res['sign2'].items()

                }
        return result

    def get_module_ids(self, module_type: str) -> (dict, dict):
        mt_arg_map = {'location': ModuleTypes.LOCATION,
                      'movement': ModuleTypes.MOVEMENT,
                      'relation': ModuleTypes.RELATION}

        signs = ['sign1', 'sign2']
        moduletypeabbrev = ModuleTypes.abbreviations[module_type]

        modules_pair = []
        for s in signs:
            sign = getattr(self, s)
            module_numbers = getattr(sign, f'{module_type}modulenumbers')
            modules = analyze_modules(modules=[m for m in sign.getmoduledict(mt_arg_map[module_type]).values()],
                                      module_numbers=module_numbers,
                                      module_abbrev=moduletypeabbrev)
            modules_pair.append(modules)

        return modules_pair

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

    def compare_movements(self) -> dict:
        def compare_module_pair(pair: tuple, pairwise: bool = True) -> (list, list):
            # pair = pair of movementModule
            # pairwise = False if not comparing one pair
            # return tuple of two dict each contains true or false at each level of granularity
            results1 = []
            results2 = []

            # articulator comparison
            #s1art = articulatordisplaytext(pair[0].articulators, pair[0].inphase)
            #s2art = articulatordisplaytext(pair[0].articulators, pair[0].inphase)
            #if set(s1art) == set(s2art):
            #    r_sign1['articulator'] = True
            #    r_sign2['articulator'] = True

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

        aligned_modules = alignmodules(self.sign1, self.sign2, moduletype='movement')

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


        """
        for module_id in sign1_modules:  # module_id is something like H1.Mov1
            if module_id in sign2_modules:
                r_sign1, r_sign2 = compare_module_pair((sign1_modules[module_id], sign2_modules[module_id]))
                pair_comparison['sign1'][module_id] = r_sign1
                pair_comparison['sign2'][module_id] = r_sign2
            else:
                # the module_id exists in sign1 but not in sign2
                r_sign1, _ = compare_module_pair((sign1_modules[module_id], sign1_modules[module_id]), pairwise=False)
                pair_comparison['sign1'][module_id] = r_sign1

        for module_id in sign2_modules:
            # another for-loop to consider module_ids that only exist in sign2
            if module_id not in sign1_modules:
                # the module_id exists in sign2 but not in sign1
                _, r_sign2 = compare_module_pair((sign2_modules[module_id], sign2_modules[module_id]), pairwise=False)
                pair_comparison['sign2'][module_id] = r_sign2
        """

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
                r = {'Signing space': {'Purely spacial': compare_result_dict}}
            else:
                return 0

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

            # articulator
            #s1art = articulatordisplaytext(pair[0].articulators, pair[0].inphase)
            #s2art = articulatordisplaytext(pair[1].articulators, pair[1].inphase)
            #r.append(True) if set(s1art) == set(s2art) else r.append(False)

            # location type
            #s1loctype = loctypedisplaytext(pair[0].locationtreemodel.locationtype)
            #s2loctype = loctypedisplaytext(pair[1].locationtreemodel.locationtype)
            #r.append(True) if set(s1loctype) == set(s2loctype) else r.append(False)

            # phonological locations
            #s1pl = phonlocsdisplaytext(pair[0].phonlocs)
            #slpl = phonlocsdisplaytext(pair[1].phonlocs)
            #r.append(True) if set(s1pl) == set(slpl) else r.append(False)

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
            QMessageBox.information(None, 'Loc selection', f'[DEBUG] Major location selection info\n\nSign1: {what_selected[0]}\nSign2: {what_selected[1]}')
            del what_selected
            # end debug

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

        aligned_modules = alignmodules(self.sign1, self.sign2, moduletype='location')

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

            """
            s1_path_btn_types = {
                path: get_btn_type_for_mvmtpath(path, pair[0].locationtreemodel.optionstree) for path in s1_path_element
            }
            s2_path_btn_types = {
                path: get_btn_type_for_mvmtpath(path, pair[1].locationtreemodel.optionstree) for path in s2_path_element
            }
            """
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

        aligned_modules = alignmodules(self.sign1, self.sign2, moduletype='orientation')

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

    def compare_relation(self) -> dict:
        def compare_one(pair: tuple) -> [bool, bool]:
            r = []  # return list of two bools each for articulators, location types, phonological locations, paths

            # relation
            s1reln = relationdisplaytext(pair[0])
            s2reln = relationdisplaytext(pair[1])
            r.append(True) if set(s1reln) == set(s2reln) else r.append(False)

            return r

        sign1_modules = [m for m in self.sign1.getmoduledict(ModuleTypes.RELATION).values()]
        sign2_modules = [m for m in self.sign2.getmoduledict(ModuleTypes.RELATION).values()]

        if (len(sign1_modules) * len(sign2_modules) < 1 or  # if either does not have any movement module
                len(sign1_modules) != len(sign2_modules)):  # if the number of xslots does not match
            return {'X-slots not matching': False}
        to_compare = zip(sign1_modules, sign2_modules)
        comparison_result = {
            'relation': True,
        }

        for pair in to_compare:
            compare_r = compare_one(pair)
            for b, (key, _) in zip(compare_r, comparison_result.items()):
                if not b:
                    comparison_result[key] = b
        return comparison_result

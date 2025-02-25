from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes, BodypartInfo, MovementModule, LocationModule, RelationModule
from search.helper_functions import relationdisplaytext, articulatordisplaytext, phonlocsdisplaytext, loctypedisplaytext, signtypedisplaytext, module_matches_xslottype
from compare_signs.compare_helpers import (analyze_modules, get_informative_elements,
                                           compare_elements, summarize_path_comparison,
                                           get_btn_type_for_mvmtpath, get_checked_paths_from_list)

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
                mvmt_res = self.compare_mvmts()
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
                #result['location'] = loc_res
                #print(f'location_compare:{loc_res}')
                pass
            elif 'relation' in module:
                #reln_res = self.compare_relation()
                #result['relation'] = reln_res
                #print(f'relation_compare:{reln_res}')
                pass
            elif 'orientation' in module:
                pass
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

    def compare_mvmts(self) -> dict:
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

            """ old version
            s1path = pair[0].movementtreemodel.get_checked_items()
            s2path = pair[1].movementtreemodel.get_checked_items()
            """

            s1_path_element = get_informative_elements(s1path)
            s2_path_element = get_informative_elements(s2path)

            s1_path_btn_types = {
                path: get_btn_type_for_mvmtpath(path, pair[0].movementtreemodel.optionstree) for path in s1_path_element
            }
            s2_path_btn_types = {
                path: get_btn_type_for_mvmtpath(path, pair[1].movementtreemodel.optionstree) for path in s2_path_element
            }

            for e1 in s1_path_element:
                matched = False
                for e2 in s2_path_element:
                    if e1.split('>')[0] == e2.split('>')[0]:  # Compare only if they share the same root
                        matched = True
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

            results1 = summarize_path_comparison(results1)
            results2 = summarize_path_comparison(results2)
            return results1, results2

        sign1_modules, sign2_modules = self.get_module_ids(module_type='movement')

        #if (len(sign1_modules) * len(sign2_modules) < 1 or  # if either does not have any movement module
        #        len(sign1_modules) != len(sign2_modules)):  # if the number of xslots does not match
        #    return {'X-slots not matching': False}

        pair_comparison = {'sign1': {}, 'sign2': {}}

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

        return pair_comparison

    def compare_locations(self) -> [bool]:
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
            s1path = get_checked_paths_from_list(pair[0].locationtreemodel)
            s2path = get_checked_paths_from_list(pair[1].locationtreemodel)
            s1_path_element = get_informative_elements(s1path)
            s2_path_element = get_informative_elements(s2path)

            s1_path_btn_types = {
                path: get_btn_type_for_mvmtpath(path, pair[0].locationtreemodel.optionstree) for path in s1_path_element
            }
            s2_path_btn_types = {
                path: get_btn_type_for_mvmtpath(path, pair[1].locationtreemodel.optionstree) for path in s2_path_element
            }

            for e1 in s1_path_element:
                matched = False
                for e2 in s2_path_element:
                    if e1.split('>')[0] == e2.split('>')[0]:  # Compare only if they share the same root
                        matched = True
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

            results1 = summarize_path_comparison(results1)
            results2 = summarize_path_comparison(results2)
            return results1, results2

        sign1_modules, sign2_modules = self.get_module_ids(module_type='location')

        pair_comparison = {'sign1': {}, 'sign2': {}}

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

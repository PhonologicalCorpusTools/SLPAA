
def count_points_and_interval(sign_pair):
    def decide_point_interval(timing):
        start_point = timing.startpoint
        end_point = timing.endpoint
        if start_point == end_point:
            return 'point'
        else:
            return 'interval'
    s1_timings = sign_pair[0].timingintervals
    s2_timings = sign_pair[1].timingintervals
    s1_results = {'interval': None,
                  'point': None}
    s2_results = {'interval': None,
                  'point': None}
    for s1_t in s1_timings:
        unit = decide_point_interval(s1_t)
        if s1_results[f'{unit}'] == None:
            s1_results[f'{unit}'] = 'Single'
        elif s1_results[f'{unit}'] == 'Single':
            s1_results[f'{unit}'] = 'Multiple'
    for s2_t in s2_timings:
        unit = decide_point_interval(s2_t)
        if s2_results[f'{unit}'] == None:
            s2_results[f'{unit}'] = 'Single'
        elif s2_results[f'{unit}'] == 'Single':
            s2_results[f'{unit}'] = 'Multiple'
    s1_output = ''
    if s1_results['interval']:
        s1_output += f"{s1_results['interval']} interval"
    elif s1_results['point']:
        s1_output += f"{s1_results['point']} point"
    s2_output = ''
    if s2_results['interval']:
        s2_output += f"{s2_results['interval']} interval"
    elif s2_results['point']:
        s2_output += f"{s2_results['point']} point"

    return s1_output, s2_output

def check_point_interval(s1_timing, s2_timing):


    return {}, {}
def check_whole_sign(sign1_timing, sign2_timing, xslotstruc, point_interval, sign1_n_xslot, sign2_n_xslot):
    sign1_xslotstruc = xslotstruc[0]
    sign2_xslotstruc = xslotstruc[1]

    xslot_count = '', ''
    is_sign1_whole = sign1_timing.startpoint.wholepart == sign1_timing.endpoint.wholepart == 0
    is_sign2_whole = sign2_timing.startpoint.wholepart == sign2_timing.endpoint.wholepart == 0

    res = [{'Timing': {'Whole sign': {f'{is_sign1_whole}': xslot_count[0]}}},
           {'Timing': {'Whole sign': {f'{is_sign2_whole}': xslot_count[1]}}}]

    if is_sign1_whole != is_sign2_whole:
        return res

    xslot_count = [{f'{sign1_xslotstruc.number}': ''},
                   {f'{sign2_xslotstruc.number}': ''}]

    if sign1_timing.endpoint.wholepart != 0:
        xslot_count[0] = {f'{sign1_n_xslot}': ''}
    if sign2_timing.endpoint.wholepart != 0:
        xslot_count[1] = {f'{sign2_n_xslot}': ''}

    if sign1_xslotstruc.number != sign2_xslotstruc.number or is_sign1_whole:
        return [{'Timing': {'Whole sign': {f'{is_sign1_whole}': ''},
                            'Number of x-slots': xslot_count[0]}},
                {'Timing': {'Whole sign': {f'{is_sign2_whole}': ''},
                            'Number of x-slots': xslot_count[1]}}]

    # Check point/interval associations
    point_interval = [{f'{point_interval[0]}': ''},
                      {f'{point_interval[1]}': ''}]

    return [{'Timing': {'Whole sign': {f'{is_sign1_whole}': ''},
                        'Number of x-slots': xslot_count[0],
                        'Type of association': point_interval[0]}},
            {'Timing': {'Whole sign': {f'{is_sign2_whole}': ''},
                        'Number of x-slots': xslot_count[1],
                        'Type of association': point_interval[1]}}]


def compare_timings(pair, xslotstruc):
    sign1_n_xslot = len(pair[0].timingintervals)
    sign1_timing = pair[0].timingintervals[0]  # assuming only one timing interval

    sign2_n_xslot = len(pair[1].timingintervals)
    sign2_timing = pair[1].timingintervals[0]  # assuming only one timing interval
    point_int = count_points_and_interval(pair)
    # step one: check whether whole sign or not
    return check_whole_sign(sign1_timing, sign2_timing, xslotstruc, point_int, sign1_n_xslot, sign2_n_xslot)




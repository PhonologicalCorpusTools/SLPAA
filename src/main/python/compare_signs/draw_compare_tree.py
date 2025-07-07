
def trunc_count_and_label(data1_keys, data2_keys, data1_btn_types, data2_btn_types, depth):
    item_labels = []
    trunc_counts = []

    for kay, btn_t in [(data1_keys, data1_btn_types), (data2_keys, data2_btn_types)]:
        label = str(list(kay)[0])
        trunc_n = len(btn_t[depth + 1:])
        if trunc_n > 0:
            label += f" (+ {trunc_n} truncated for lack of correspondence)"
        item_labels.append(label)
        trunc_counts.append(trunc_n)

    return item_labels, trunc_counts

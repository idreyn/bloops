def get_n_longest_segments(segments, n):
    segs_and_idxs = []
    for idx, segment in enumerate(segments):
        segs_and_idxs.append((segment, idx))
    segs_by_length = list(sorted(segs_and_idxs, key=lambda pair: -len(pair[0])))
    longest_segs_unsorted = segs_by_length[0:n]
    return [
        pair[0]
        for pair in list(sorted(longest_segs_unsorted, key=lambda pair: pair[1]))
    ]

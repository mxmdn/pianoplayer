"""
TARGETS

        S     E  E  E  E  E  E  E  S  S
     |-----|-----------------------------|
 --- |  E ---(E) F     F  G  F  E     E --
| R  |  C ---(C) D <r> D  D  D  C  D  C --
| H  |  G ---(G) A     A  B  A  G     G --
 --- |-----|-----------------------------|
     |     |                             |
 --- |-----|-----------------------------|
| L  |     |  A     A     A     A        |
| H  | <r> |  A <r> A <r> A <r> A <r>    |
 --- |-----|-----------------------------|

          S     E  E  E  E  E  E  E  S  S
       |-----|-----------------------------|
 ---  p|  E ---(E)          G     E     E --
| R   r|     |     F     F     F           |
|     M|  C ---(C)   <r>          C  D  C --
| H   I|     |     D     D  D  D           |
 ---  T|  G ---(G) A     A  B  A  G     G --
       |-----|-----------------------------|
       |     |                             |
       |-----|-----------------------------|
 ---  T|     |  A     A     A     A        |
| L   I|     |                             |
|     M| <r> |    <r>   <r>   <r>   <r>    |
| H   r|     |                             |
 ---  p|     |  A     A     A     A        |
       |-----|-----------------------------|

DURATIONS

    Humdrum : 1, 2, 4...
    Tab :
    // W - whole
    // H - half
    // Q - quarter
    // E - 8th
    // S - 16th
    // T - 32nd
    // X - 64th
    // . - note dotted
    // |-n-| - n-tuplets

"""
from collections import OrderedDict

NOTES_CYCLE_FLATS = ["c", "db", "d", "eb", "e", "f", "gb", "g", "ab", "a", "bb", "b"]
NOTES_CYCLE_SHARPS = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]


class Event:
    pass


class NoteEvent(Event):

    def __init__(self, duration, notes_left_hand=None, notes_right_hand=None):
        self.duration = duration
        self.notes_left_hand = notes_left_hand if notes_left_hand else []
        self.notes_right_hand = notes_right_hand if notes_right_hand else []


class MeasureEvent(Event):
    """
    """
    _choices = ["simple", "double", "rpt_start", "rpt_stop", "end"]

    def __init__(self, bartype):
        self.bartype = bartype

"""
Input file contents:
13	3.0000	3.2500	53	None	None	1	-2	3.1287025174525187	3	1
14	3.2500	3.5000	50	None	None	1	-4	3.4349447522661807	4	1
15	3.5000	4.0000	72	None	None	0	4	1.1023197536590195	10	1
16	3.5000	3.7500	52	None	None	1	-3	3.7481172940101493	5	1
17	3.7500	4.0000	48	None	None	1	-5	3.715362191969332	6	1
18	4.0000	4.2500	74	None	None	0	5	1.5254643372500314	11	2
19	4.0000	4.5000	55	None	None	1	-1	3.4705673043172998	7	2
"""

def parse_line(line):
    print(line)
    parts = line.split("\t")
    d_infos = OrderedDict()
    d_infos["t_start"] = float(parts[1])
    d_infos["t_end"] = float(parts[2])
    d_infos["pitch"] = int(parts[3])
    d_infos["finger"] = parts[7]
    d_infos["note_id"] = parts[9]
    d_infos["measure"] = parts[10]
    return d_infos


def parse_txt_file(filename):
    d_out = OrderedDict()
    with open(filename, "r+") as f_in:
        for line in f_in.readlines():
            d_infos = parse_line(line)
            finger = d_infos["finger"]
            measure = d_infos["measure"]
            if measure not in d_out:
                d_out[measure] = OrderedDict()

            if finger in d_out[measure]:
                d_out[measure][finger].append(d_infos)
            else:
                d_out[measure][finger] = [d_infos]

    return d_out


def draw_measure(d_measure):
    """
    d_measure[finger] = l_d_infos

    size factors 1 2 4 6
    """
    MAX_SIZE_FACTOR = 6

    # Get min duration
    # min and max([abs(tstart1 - tstart2)] + [tstart - tend])
    l_starts = sum([[d["t_start"] for d in v]
                    for v in list(d_measure.values())], [])
    l_starts = list(set(list(l_starts)))
    l_starts.sort()
    l_ends = sum([[d["t_start"] for d in v]
                  for v in list(d_measure.values())], [])
    l_ends = list(set(list(l_ends)))
    l_ends.sort()
    l_start_diffs = sum([[abs(v - w) for w in l_starts if w != v]
                         for v in l_starts],
                         [])
    l_starts_diffs2 = [v - u for v, u in zip(l_starts[1:], l_starts[:-1])]
    d_tstart_to_diff = OrderedDict()
    for v, u in zip(l_starts[1:], l_starts[:-1]):
        d_tstart_to_diff[u] = v - u

    d_tstart_to_diff[l_starts[-1]] = l_ends[-1] - l_starts[-1]

    print("l_starts", l_starts)
    print("l_start_diff", l_start_diffs)
    l_durs = sum([[d["t_end"] - d["t_start"] for d in v]
                 for v in list(d_measure.values())], [])
    l_durs = list(set(l_durs))
    print("l_durs", l_durs)

    # Gather notes by tstart
    d_notes_by_t_start = OrderedDict()
    for finger_notes in d_measure.values():
        for d in finger_notes:
            if d["t_start"] in d_notes_by_t_start:
                d_notes_by_t_start.append(d)
            else:
                d_notes_by_t_start = [d]

    # Compute all separate distances size factors
    BASE_LEN = 1
    MAX_LEN = 10

    # into a dictionary with tstart as keys
    l_unique_start_diffs = list(set(list(l_starts_diffs2)))
    l_unique_start_diffs.sort()
    l_unique_start_diffs_ratio = []
    for diff2 in l_unique_start_diffs:
        l_unique_start_diffs_ratio.append(diff2 * 1. / l_unique_start_diffs[0])

    nb_distances = len(l_unique_start_diffs_ratio)
    if 0:
        l_in = l_unique_start_diffs_ratio
    else:
        l_in = l_unique_start_diffs

    min_d = min(l_in)
    max_d = max(l_in)
    print(l_in)
    #d_length = {l_unique_start_diffs[i]:
    #            MAX_LEN*(e - min_d)/(max_d - min_d + 1e-5) + BASE_LEN
    #            for i, e in enumerate(l_in)}
    d_length = OrderedDict()
    for i, e in enumerate(l_in):
        d_length[l_unique_start_diffs[i]] = int(MAX_LEN*e)

    print("\nl_starts")
    print(l_starts)
    print("\nd_length")
    print("\n".join([f"{k}: {v}" for k, v in d_length.items()]))

    print("\nd_tstart_to_diff")
    print("\n".join([f"{k}: {v}" for k, v in d_tstart_to_diff.items()]))
    d_tstart_to_len = OrderedDict()
    for i, tstart in enumerate(l_starts):
        diff = d_tstart_to_diff[tstart]
        print(diff)
        if diff:
            if diff in d_length:
                d_tstart_to_len[tstart] = d_length[diff]
            else:
                d_tstart_to_len[tstart] = d_length[diff]

    print("\nd_tstart_to_len")
    print("\n".join([f"{k}: {v}" for k, v in d_tstart_to_len.items()]))

    #if nb_distances > 1:
    #    import pdb; pdb.set_trace()

    # Draw beginning



    # Loop over all notes/chords

    #


def main(filename):
    print(filename)
    d_info = parse_txt_file(filename)
    for d_meas in d_info.values():
        draw_measure(d_meas)


if __name__ == "__main__":
    import sys
    main(sys.argv[1])





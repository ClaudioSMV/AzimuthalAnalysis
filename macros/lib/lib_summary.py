from lib_cuts import cuts_list_short, get_ordered_cuts_at_this_stage, cuts_legend
from lib_error import check_list_has_one_element
from lib_constants import list_of_targets_sets

def get_set_of_targets(input_cuts, get_set_tag = False):
# Return list with targets used in liquid or solid set
    possible_sets = get_ordered_cuts_at_this_stage("Summary", True)
    cut_tags = cuts_list_short(input_cuts, include_binvars=False)
    sets_chosen = [cut for cut in cut_tags if cut in possible_sets]
    check_list_has_one_element(sets_chosen, "get_list_summary_targets", is_error=True)
    this_set = sets_chosen[0]
    if get_set_tag:
        return this_set
    else:
        return list_of_targets_sets[this_set]

def get_legend_set_of_targets(cut_str):
# Return legend of the set of targets
    return cuts_legend[get_set_of_targets(cut_str, get_set_tag=True)]


                                    #################
######################################    STYLE    #######################################
######################################  Constants  #######################################
                                    #################

MARGINS = {"T": 0.05, "R": 0.05, "B": 0.10, "L": 0.10}
FONT = 43 # Helvetica
SIZE_TEXT = 38
SIZE_TITLE = SIZE_TEXT - 3
SIZE_LABEL = SIZE_TEXT - 9
OFFSET_TITLE = {"X": 1.0, "Y": 1.0}


                             ###############################
###############################          UPDATE           ################################
###############################  Update global variables  ################################
                             ###############################

def update_margins(new_values):
    global MARGINS
    for side in MARGINS.keys():
        if side in new_values.keys():
            MARGINS[side] = new_values[side]

def update_font(new_value):
    global FONT
    FONT = new_value

def update_size(new_value):
    global SIZE_TEXT
    SIZE_TEXT = new_value

def update_offset(new_values):
    global OFFSET_TITLE
    for axis in OFFSET_TITLE.keys():
        if axis in new_values.keys():
            OFFSET_TITLE[axis] = new_values[axis]

                                  #####################
####################################      STYLE      #####################################
####################################  Color palette  #####################################
                                  #####################

color_palette = {
    "blue": (51,34,136),
    "light_blue": (51,187,238),
    "green": (17,119,51),
    "mustard": (153,153,51),
    "light_red": (204,102,119),
    "wine": (136,34,85),
    "gray": (128,128,128),
}

                               ############################
#################################       VARIABLES        #################################
#################################  Naming and axes info  #################################
                               ############################

variable_info = { # <initial>: [<name>, <axis_name_latex>, <units>]
    'Q': ["Q2",     "Q^{2}",        "(GeV^{2})"],
    'N': ["Nu",     "#nu",          "(GeV)"    ],
    'Z': ["Zh",     "Z_{h}",        ""         ],
    'P': ["Pt2",    "P_{t}^{2}",    "(GeV^{2})"],
    'I': ["PhiPQ",  "#phi_{PQ}",    "(deg)"    ],
    'X': ["Xb",     "X_{b}",        ""         ],
}

def get_variables_order(reference, use_only_reference = True):
# Return vars in order. Reference is used to select a var when there are multiple options
    variables_order = [["Q"], ["N", "X"], ["Z"], ["P"], ["I"]]
    final_string = ""
    for possible_vars in variables_order:
        chosen = possible_vars[0]
        if (len(possible_vars) > 1):
            for var in possible_vars:
                if var in reference:
                    chosen = var
                    break
        if (use_only_reference) and (chosen not in reference):
            continue
        final_string += chosen

    return final_string

                         ########################################
###########################                CUTS                ###########################
###########################  Dictionary Short to Long cut-tag  ###########################
                         ########################################

cuts_StoL = {
    # Used at Acceptance stage
    "Xf": "CFR", "XT": "TFR", "DS": "DS", "BS": "rS", "PF": "PFid", "MM": "MM",
    "M2": "MM2",
    # Used at Correction stage
    "FE": "Err", "AQ": "AQ", "Pe": "rmTheLine",
    # Used at Fit stage
    "Fs": "fSin", "NP": "NP", "Nm": "PreNorm",
    # Used at Summary stage
    "MD": "mergeD",
    "sl": "Sol", "lq": "Liq",
    # Fit methods
    "Sh": "Shift", "Fd": "Fold", "LR": "LR", "Ff": "FullRng",
}

cuts_StoL_processed_files = {
    # Used at Acceptance stage
    "Xf": "Xf", "XT": "XTFR", "DS": "DSect0", "BS": "NoBadSec", "PF": "PiFid",
    "MM": "MMtch", "M2": "MMtch2",
    # Used at Correction stage
    "FE": "FErr", "AQ": "AccQlt", "Pe": "dfNphe",
}

cuts_legend = {
    # Used at Acceptance stage
    "Xf": "#X_f CFR", "XT": "#X_f TFR", "DS": "#Delta Sect #neq 0",
    "BS": "No bad Sect", "PF": "Fidual cut #pi",
    "MM": "Mirror Matching", "M2": "Mirror Matching 2",
    # Used at Correction stage
    "FE": "", "AQ": "", "Pe": "N_{phe}^{el} #neq N_{phe}^{h}",
    # Used at Fit stage
    "Fs": "Fit with Sin(x)", "NP": "Skip central peak",
    "Nm": "Previously normalized",
    # Used at Summary stage
    "MD": "Merge all D",
    "sl": "Solid targets", "lq": "Liquid targets",
    # Fit methods
    "Sh": "Shift", "Fd": "Fold", "LR": "LR", "Ff": "Full range",
}

                               ###########################
#################################          CUTS         ##################################
#################################  List with cut order  ##################################
                               ###########################

ordered_stages = ["Acceptance", "Correction", "Fit", "Summary"]

ordered_cuts_per_stage = [
    ("SummaryTarget", ["sl", "lq",]),
    ("FitMethod", ["Sh", "Fd", "LR", "Ff",]),
    ("Acceptance", ["Xf", "XT", "DS", "BS", "PF", "MM", "M2",]),
    ("Correction", ["Sh", "FE", "AQ", "Pe",]),
    ("Fit", ["Fs", "NP", "Nm",]),
    ("Summary", ["MD",]),
]

                               ###########################
#################################         SUMMARY       ##################################
#################################    Sets of targets    ##################################
                               ###########################

available_targets = ["C", "Fe", "Pb", "D", "DC", "DFe", "DPb"]

list_of_targets_sets = {
    "sl": ["C", "Fe", "Pb"], # Solid targets
    "lq": ["DC", "DFe", "DPb"], # Liquid targets
}

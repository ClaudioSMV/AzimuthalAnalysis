from lib_style import axes_title
from lib_constants import get_variables_order
from lib_naming import extract_indices_dict
from lib_cuts import format_output_binvars, extract_indices_dict
from ROOT import TH1D

                              #############################
################################        Functions        #################################
################################  PhiPQ and projections  #################################
                              #############################

def create_phipq_copy(input_phipq, new_name, shift_center = False):
# Create a copy of the phi_PQ 1d projection
    xmin = input_phipq.GetXaxis().GetXmin() # -180.
    xmax = input_phipq.GetXaxis().GetXmax() #  180.
    nbins = input_phipq.GetNbinsX()
    if (shift_center): # change x-limits so they match bin edges
        central_bin = input_phipq.FindBin(0.0)
        xmin = 0.0 + input_phipq.GetBinLowEdge(central_bin)
        xmax = 360. + input_phipq.GetBinLowEdge(central_bin)

    axes_tag = axes_title("I", "Counts", x_is_variable=True)
    if (new_name[0] == "+"):
        new_name = input_phipq.GetName() + "_" + new_name[1:]
    histogram_new_phipq = TH1D(new_name, axes_tag, nbins, xmin, xmax)

    # Fill histogram bin by bin
    for input_bin in range(1, nbins+1):
        value = input_phipq.GetBinContent(input_bin)
        if (value == 0): # Avoid errors by skipping empty bins
            continue
        error = input_phipq.GetBinError(input_bin)
        new_bin = input_bin
        if (shift_center) and (input_bin < central_bin): # Move first half to the end
            new_bin = input_bin + (nbins - central_bin) + 1
        elif (shift_center) and (input_bin >= central_bin): # Draw second half first
            new_bin = input_bin - central_bin + 1
        histogram_new_phipq.SetBinContent(new_bin, value)
        histogram_new_phipq.SetBinError(new_bin, error)

    return histogram_new_phipq

def create_1D_projection_from_sparse(input_histogram, new_name, bincode, shift = False):
    reference_vars = get_variables_order(bincode, use_only_reference=False)
    bincode_vars = get_variables_order(bincode, use_only_reference=True)
    bincode_indices = extract_indices_dict(bincode)
    for var in bincode_vars: # Select proper bin for binned axes. Integrate the rest!
        axis_idx = reference_vars.index(var) # First axis is 0 by convention
        bin = bincode_indices[var] + 1 # First bin is 1 by convention
        input_histogram.GetAxis(axis_idx).SetRange(bin, bin) # Just that bin!

    projection = input_histogram.Projection(4) # phipq axis
    projection.SetName(new_name)
    final_phipq = create_phipq_copy(projection, "+%s"(bincode), shift)
    projection.Delete()

    return final_phipq

from ROOT import TH1I,TH1D,TH1F,TH2D,TH2F,TEfficiency,TGraphAsymmErrors,\
    gROOT,gPad,TPad,TF1,gStyle,kBlack,kWhite,TH1, TCanvas
import ctypes ## Needed to get pointer values
import myStyle as ms

mgn = ms.get_margin()

def pad_name(title, x, y):
# Create name of the pad using its coordinate position x,y
    name = "%s_%i_%i"%(title, x, y)

    return name

def get_pad_coord(name):
# Obtain pair of coordinates for the pad x,y
    list_elements = name.split("_")
    x, y = list_elements[-2], list_elements[-1]

    return int(x), int(y)

def canvas_partition(canvas, nx, ny, lMarg = 2*mgn, rMarg = mgn,
                     bMarg = 2*mgn, tMarg = mgn, extra_name=""):
# Separate canvas in nx by ny pads
    ## Labelling xy:
    ##  ------------
    ##  - 02 12 22 -
    ##  - 01 11 21 -
    ##  - 00 10 20 -
    ##  ------------

    vSpacing = 0.0
    vStep  = (1.- bMarg - tMarg - (ny-1) * vSpacing) / ny
    
    hSpacing = 0.0
    hStep  = (1.- lMarg - rMarg - (nx-1) * hSpacing) / nx

    for i in range(nx):
        if (i==0):
            hposl = 0.0
            hposr = lMarg + hStep
            hfactor = hposr-hposl
            hmarl = lMarg / hfactor
            hmarr = 0.0
        elif (i == nx-1):
            hposl = hposr + hSpacing
            hposr = hposl + hStep + rMarg
            hfactor = hposr-hposl
            hmarl = 0.0
            hmarr = rMarg / (hposr-hposl)
        else:
            hposl = hposr + hSpacing
            hposr = hposl + hStep
            hfactor = hposr-hposl
            hmarl = 0.0
            hmarr = 0.0

        for j in range(ny):
            if (j==0):
                vposd = 0.0
                vposu = bMarg + vStep
                vfactor = vposu-vposd
                vmard = bMarg / vfactor
                vmaru = 0.0
            elif (j == ny-1):
                vposd = vposu + vSpacing
                vposu = vposd + vStep + tMarg
                vfactor = vposu-vposd
                vmard = 0.0
                vmaru = tMarg / (vposu-vposd)
            else:
                vposd = vposu + vSpacing
                vposu = vposd + vStep
                vfactor = vposu-vposd
                vmard = 0.0
                vmaru = 0.0

            canvas.cd(0)
            name = pad_name(extra_name,i,j)
            pad = gROOT.FindObject(name)
            if pad:
                pad.Delete()
            pad = TPad(name,"",hposl,vposd,hposr,vposu)

            pad.SetLeftMargin(hmarl)
            pad.SetRightMargin(hmarr)
            pad.SetBottomMargin(vmard)
            pad.SetTopMargin(vmaru)
    
            pad.SetFrameBorderMode(0)
            pad.SetBorderMode(0)
            pad.SetBorderSize(0)
    
            pad.Draw()

def x_pad(x):
# Get x position in pad coordinate system
    xl, xr = ctypes.c_double(0.0), ctypes.c_double(0.0)
    yd, yu = ctypes.c_double(0.0), ctypes.c_double(0.0)
    gPad.GetPadPar(xl, yd, xr, yu)
    pw = xr.value-xl.value
    lm = gPad.GetLeftMargin()
    rm = gPad.GetRightMargin()
    fw = pw-pw*lm-pw*rm

    return (x*fw+pw*lm)/pw

def y_pad(y):
# Get y position in pad coordinate system
    xl, xr = ctypes.c_double(0.0), ctypes.c_double(0.0)
    yd, yu = ctypes.c_double(0.0), ctypes.c_double(0.0)
    gPad.GetPadPar(xl, yd, xr, yu)
    ph = yu.value-yd.value
    tm = gPad.GetTopMargin()
    bm = gPad.GetBottomMargin()
    fh = ph-ph*bm-ph*tm

    return (y*fh+bm*ph)/ph

def create_l_canvas(l_names, nx, ny, lMarg = 2*mgn, rMarg = mgn,
                    bMarg = 2*mgn, tMarg = mgn):
# Create list of canvases, each with a partition of nx by ny subpads
    l_canvas = []
    for name in l_names:
        cv = ms.create_canvas(name)
        canvas_partition(cv, nx,ny,lMarg,rMarg,bMarg,tMarg, name)
        l_canvas.append(cv)

    return l_canvas

def get_yaxis_label(parameter_idx, y_axis_type, is_solid_target):
# y_axis_type is "asymmetry" or "ratio"
    index_to_symbol = {"0": "1", "1": "cos#phi",
                       "2": "cos2#phi", "3": "sin#phi"}
    target = "A" if is_solid_target else "D"

    axis_label = "#LT%s#GT_{e%s}"%(index_to_symbol[parameter_idx], target)
    if "ratio" in y_axis_type.lower():
        axis_label+= "/#LT%s#GT_{eD}"%(index_to_symbol[parameter_idx])

    return axis_label

def get_parameters_type(input_opt):
# Return dictionary with boolean of type selected and short and long name of
# the type of parameter to show
    d_tp_bool = {"par": False, "norm": False, "ratio": False}
    l_tp_nameS = ["par", "norm", "ratio"]
    l_tp_nameL = ["Parameters", "Norm", "Ratio"]

    # Select type of plot
    for t,sname in enumerate(l_tp_nameS):
        if sname in input_opt.lower():
            d_tp_bool[sname] = True
            tp_idx = t
            break
    
    # Check a proper type was introduced
    if True not in d_tp_bool.values():
        ms.error_msg("ParameterType", "Type chosen not found!!")

    my_tp_nameS = l_tp_nameS[tp_idx]
    my_tp_nameL = l_tp_nameL[tp_idx]

    return d_tp_bool, my_tp_nameS, my_tp_nameL

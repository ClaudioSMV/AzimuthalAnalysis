from ROOT import TH1I,TH1D,TH1F,TH2D,TH2F,TEfficiency,TGraphAsymmErrors,\
    gROOT,gPad,TPad,TF1,gStyle,kBlack,kWhite,TH1, TCanvas
import ctypes ## Needed to get pointer values
import myStyle as ms


def pad_name(info, x,y):
# Create name of the pad using its coordinate position x,y
    name = "%s_%i_%i"%(info,x,y)

    return name

def canvas_partition(canvas, nx, ny, lMarg, rMarg, bMarg, tMarg, extra_name=""):
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

mgn = ms.get_margin()
def create_l_canvas(l_names, nx, ny, lMarg = 2*mgn, rMarg = mgn,
                    bMarg = 2*mgn, tMarg = mgn):
# Create list of canvases, each with a partition of nx by ny subpads
    l_canvas = []
    for name in l_names:
        cv = ms.create_canvas(name)
        canvas_partition(cv, nx,ny,lMarg,rMarg,bMarg,tMarg, name)
        l_canvas.append(cv)

    return l_canvas

def yaxis_label(par, ntype, tar):
# ntype -> l_tp_nameS = ["par", "norm", "ratio"]
    d_func = {"0": "1", "1": "cos#phi", "2": "cos2#phi", "3": "sin#phi"}
    tar = "A" if "D" not in tar else "D"

    my_axis = "#LT%s#GT_{e%s}"%(d_func[par], tar)

    if "par" in ntype:
        d_axis = {"0": "A", "1": "B", "2": "C", "3": "D"}
        my_axis = "%s [A.U.]"%(d_axis[par])

    elif "ratio" in ntype:
        my_axis+= "/#LT%s#GT_{eD}"%(d_func[par])

    return my_axis

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

def get_parameters_limits(d_bools, par, xvar_init):
# Give y-axis limits for summary plot depending on the type and parameter
    par = str(par)

    # Limits for Zh
    type_par_Z = {"0": [-4.0e4, 10.0e5], "1": [-4.0e4, 10.0e5],
                "2": [-4.0e4, 10.0e5], "3": [-4.0e4, 10.0e5]}
    type_norm_Z = {"0": [0.0, 2.0], "1": [-0.599,0.099],
                 "2": [-0.299,0.099], "3": [-0.599,0.599]}
    type_ratio_Z = {"0": [0.0, 2.0], "1": [0.201,1.799],
                 "2": [0.001,1.999], "3": [0.001,1.999]}

    d_limits_Z = {"par": type_par_Z, "norm": type_norm_Z,
                  "ratio": type_ratio_Z}
    
    # Limits for Pt
    type_par_P = {"0": [-4.0e4, 10.0e5], "1": [-4.0e4, 10.0e5],
                "2": [-4.0e4, 10.0e5], "3": [-4.0e4, 10.0e5]}
    type_norm_P = {"0": [0.0, 2.0], "1": [-0.299,0.049],
                 "2": [-0.049,0.099], "3": [-0.599,0.599]}
    type_ratio_P = {"0": [0.0, 2.0], "1": [0.301, 1.299],
                 "2": [0.001,1.999], "3": [0.001,1.999]}

    d_limits_P = {"par": type_par_P, "norm": type_norm_P,
                  "ratio": type_ratio_P}
    
    d_limits_var = {"Z": d_limits_Z, "P": d_limits_P}

    d_limits = d_limits_var[xvar_init]
    for tp in d_limits:
        if not d_bools[tp]:
            continue
        d_par = d_limits[tp]
        limits = d_par[par]

        return limits

# AzimuthalAnalysis

Backup repository of Phi PQ study for positive Pions.

## Data and Simulation files
The study uses as input files with a format given by [`GetSimpleTuple`](https://github.com/utfsm-eg2-data-analysis/GetSimpleTuple/tree/csanmart/analysis-pion-phipq), `development` branch (vectorial tuples).

## Run code
The main part of the code is located in [include](https://github.com/ClaudioSMV/AzimuthalAnalysis/tree/main/include). Using ROOT you can run it by following:
```
root -l
// Inside ROOT
root [0] >> .L Acceptance.C+
```
After that, you can run any C script, for instance:
```
root [1] >> .x process.C("Fe") // Get Acceptance for all of the Fe simulation files
root [2] >> .x ../run/getClosureTest.C("Fe",0,2) // Get Closure test for Fe target with binning "0" and 2D final plots
root [3] >> .x ../run/runAll_ClosureTest.C(0,2) // Get Closure test for **all targets** with binning "0" and 2D final plots
```
This creates .root files with the 'raw' plots.

To get them with a better style, run the [python macros](https://github.com/ClaudioSMV/AzimuthalAnalysis/tree/main/macros):
```
python PlotClosureTest.py -D Fe_0_2 // The format is <targ>_<binType>_<Ndims> as in the C scripts
```
If the code was run in the JLab cluster, remember to copy them into the folder `<AzimuthalAnalysis>/output/JLab_cluster` with
```
scp <user>@ftp.jlab.org:/home/<user>/work/AzimuthalAnalysis/output/<folder> <AzimuthalAnalysis>/output/JLab_cluster/.
```
Later, you can run the macros adding an extra option `-J`.
Remember to call `-h` for help with the macros' options.

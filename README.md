# AzimuthalAnalysis

Backup repository of Phi PQ study for positive Pions.

## Data and Simulation files
The study uses as input files with a format given by [`GetSimpleTuple`](https://github.com/utfsm-eg2-data-analysis/GetSimpleTuple/tree/csanmart/analysis-pion-phipq), `development` branch (vectorial tuples).

## Run code
The main part of the code is located in [include](https://github.com/ClaudioSMV/AzimuthalAnalysis/tree/main/include). To run any part of the code you MUST compile it before. Using ROOT you can compile it by following:
```
root -l
// Inside ROOT
root [0] >> .L Acceptance.C+
```
After that, you can run any C script, for instance:
```
root [1] >> .x process.C("Fe") // Get Acceptance for all of the Fe simulation files
root [2] >> .x ../run/getClosureTest.C("Fe",2,1) // Get Closure test for Fe target with binning "0" and 2D final plots
root [3] >> .x ../run/runAll_ClosureTest.C(2,1) // Get Closure test for **all targets** with binning "0" and 2D final plots
```
This creates .root files with the 'raw' plots.

## Running in JLab's cluster
If the code is run in the JLab cluster, remember to copy the output files into a local folder `<AzimuthalAnalysis>/output/JLab_cluster` with
```
scp <user>@ftp.jlab.org:/home/<user>/work/AzimuthalAnalysis/output/<folder> <AzimuthalAnalysis>/output/JLab_cluster/.
```
Later, you can run the macros using an extra option `-J`.
Remember to call `-h` for extra help with the macros' options.

## Getting plots
To get the plots with a better style, run the [python macros](https://github.com/ClaudioSMV/AzimuthalAnalysis/tree/main/macros) following:
```
// The format for the sample is <targ>_<binType>_<Ndims>
python PlotClosureTest.py   -D Fe_10_1 -i FE_AQ     -o FE_AQ_Zx -f 50
python PlotCorrection.py    -D Fe_10_1 -i FE_AQ     -o FE_AQ_Zx
python PlotFit.py           -D Fe_10_1 -i FE_AQ_Zx  -o FE_AQ_Zx_NP_Fd
```
If you want to run the whole process (this is, Correct data -> Fit -> GetParameters) you can run the script:
```
./FitCrossSection.sh Fe 10 1 FE_AQ_Zx_NP_Fd // For a further description of the options call without arguments: ./FitCrossSection.sh
```
Summary plots are available after running the script over all sensors. Summaries are given by:
```
python Summary_ParametersNorm.py -D 2_1
python Summary_ParameterRatioOverD.py -D 2_1
```

The whole process can be done all at once by using the 'RunAll' scripts.
They run over all targets and accept arguments to run over all fit methods and Zh ot Pt2 dependency.
```
./RunAllFitAndSummary 10 1 FE_AQ_Zx_NP_Fd
```


# AzimuthalAnalysis

Analysis of the effect (anisotropy) of different nuclear media in the azimuthal ($\phi_{PQ}$) distribution for $\pi^+$/$\pi^-$ production at Clas6 (and Clas12; *WIP*).

## Data and Simulation files
The study requires as input a file in *.root* format, with tuples saved in the format given by [`GetSimpleTuple`](https://github.com/utfsm-eg2-data-analysis/GetSimpleTuple/tree/csanmart/analysis-pion-phipq), `development` branch (i.e. vectorial tuples).

**Clas12 support is under development.**
Since the new tuples are saved in a slightly different way, a *translator* from Clas12 to Clas6 format was developed ([check here](https://github.com/ClaudioSMV/GetVectorTuple)).

## Workflow
The workflow of this analysis considers two steps, so called: *initial processing* and *analysis & plots*.
The main difference between the steps is in the way the files are created.
- In the *Initial processing* step, a set of 'light weight' **processed files** are created directly from data/simulations with a C/C++ approach (defined mostly in `/include`).
Roughly speaking, the ROOT vectorial tuples are taken and **only histograms** are saved.
These histograms have some selection cuts already applied and contain quantities of interest, such as distributions of $Q^2$, $\nu$, $Z_h$, efficiencies, maps, etc...
- The *Analysis & plots* step manipulates the processed histograms.
Its main purpose is to save the results of each stage (say, data correction, fitting, etc.) in two ways: as histogram objects in ROOT files (so called, **analysis files**) to be used in following analysis stages, and as plots in `.png` or `.pdf` format, with a defined style.
This section uses Python and is defined in `/macros`.
*Future tasks: Update visuals using libraries such as matplotlib for ease of implementation.*

## Initial processing
The main part of the code is located in [include](https://github.com/ClaudioSMV/AzimuthalAnalysis/tree/main/include).
Similarly, a set of macros to actually run the analysis are saved in `/run`.
You must load/compile the code before running macros.
This section doesn't has a Makefile since it expects to be handled by the ROOT internal compiler.
First, move to the `/include` folder and do:
```
root -l
// Inside ROOT, do only what's after the ">>" symbol
root [0] >> .L AzimuthalAnalysis.C+
```
After that, you can run any C script that uses the analysis class, for instance:
```
root [1] >> .x ../run/getAcceptance.C("Fe", 10) // Get Acceptance using Fe files and "10" binning
root [2] >> .x ../run/getClosureTest.C("Fe", 2, 1) // Get Closure Test using Fe target and "2" binning, all variables irregular ("1"), and no cuts
root [3] >> .x ../run/runAll_ClosureTest.C(10, 1) // Get Closure Test for **all targets** with binning "10", all variables irregular ("1"), and no cuts
```
These commands will create the *processed files* that will be used in next steps.

### Running in JLab's cluster (ifarm)
You can send jobs to the job's handle manager of the ifarm to accelerate the processing.
Bash scripts for this are defined in `/run/sh`.
These assume you are working in the ifarm and using SLURM.

If you want to run something locally (and wants it to be treated differently from the ifarm's files), create the  *processed files* and move them into a folder `/output/local`.
Later, you can use these files in the analysis section by adding the `-L` option in the python macros.

**NOTE**: If you want to copy files from the ifarm to `/output`, you can do:
```
scp -J <user>@login.jlab.org. <user>@ifarm:<file_full_path> <local_path>
// Example
scp -J csanmart@login.jlab.org. csanmart@ifarm:/home/csanmart/work/AzimuthalAnalysis/output/Acceptance/file.root /output/Acceptance
```

## Analysis & plots (Analysis files)
A series of [python macros](https://github.com/ClaudioSMV/AzimuthalAnalysis/tree/main/macros) were created to handle each stage of the analysis separated.
These macros use functions stored in `/macros/lib` to work, and the different cuts and definition of fit methods, among other selections, are defined along them.
The options required/available for each macro could be printed by calling the macro with option `-h`.
To get the output (files and plots) from a macro, run:
```
// NOTE: Dataset format is <targ>_<binType>_<Ndims>
python PlotCorrection.py    -D Fe_10_1 -B QNZ -C FE_AQ -A
python PlotFit.py           -D Fe_10_1 -B QNZ -C FE_AQ_NP -F Fd
// python PlotClosureTest.py   -D Fe_10_1 -i FE_AQ     -o FE_AQ_Zx -f 50 // TODO: NEED TO BE UPDATED!
```
If you want to run the whole analysis (this is, Correct data -> Fit -> GetParameters -> Obtain final summary plots) you can run the script:
```
./run_analysis.sh <target> <bin_code> <irregular_bins_code> <bin_variables> <cuts> <fit_method>
// Example
./run_analysis.sh Fe 10 1 QNZ FE_AQ_NP Fd
```
For a further description of the options available, run the script without arguments to see the helper: `./run_analysis.sh`.

If you are running some stages manually, remember that the summary plots are available only after running the scripts over all targets. 

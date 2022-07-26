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
After that, you can run any 'macro', for instance:
```
root [1] >> .x process.C("Fe") // Get Acceptance for all of the Fe simulation files
root [2] >> .x runAll_2DProj.C // Get all 2D projections of all of the data and simulation targets
```

#!/bin/dash

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /afs/cern.ch/user/h/hbakhshi/work/PU/CMSSW_8_0_26_patch2/src/Haamm/HaNaMiniAnalyzer/test/
eval `scramv1 runtime -sh`

echo $LSB_JOBINDEX
./Plotter.py $1 $2 $3


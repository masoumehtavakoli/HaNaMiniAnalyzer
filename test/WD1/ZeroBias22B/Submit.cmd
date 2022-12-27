executable              = /eos/home-m/mkhalife/CMSSW_12_4_0/src/Haamm/HaNaMiniAnalyzer/test/WD1/ZeroBias22B/SetupAndRun.sh
output                  = $(ClusterId)_$(ProcId).out
error                   = $(ClusterId)_$(ProcId).err
log                     = $(ClusterId)_$(ProcId).log
+JobFlavour             = "tomorrow"
environment             = CONDORJOBID=$(ProcId)
notification            = Error

arguments               = /eos/home-m/mkhalife/CMSSW_12_4_0/src/Haamm/HaNaMiniAnalyzer/test/WD1/.x509up_u154935 slc7_amd64_gcc10 CMSSW_12_4_0 UL2018 ZeroBias22B out /eos/home-m/mkhalife/Run1/ 2
queue 164


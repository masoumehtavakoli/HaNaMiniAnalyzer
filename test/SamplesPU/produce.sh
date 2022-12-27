#/afs/cern.ch/user/h/helfaham/CMSSW_10_6_4_patch1/src/Haamm/HaNaMiniAnalyzer/test/SamplesPU

#dasgoclient --limit=0 --query="file dataset=/SingleNeutrino/RunIISummer19UL18MiniAOD-FlatPU0to70_106X_upgrade2018_realistic_v11_L1v1-v1/MINIAODSIM" > SingleNeutrino_FlatPU.list
#dasgoclient --limit=0 --query="file dataset=/SingleNeutrino/RunIISummer19UL18MiniAOD-UL18HEMreReco_pilot_106X_upgrade2018_realistic_v11_L1v1-v2/MINIAODSIM" > SingleNeutrino.list

dasgoclient --limit=0 --query="file dataset=/SingleNeutrino/RunIISummer19UL18MiniAOD-FlatPU0to75_106X_upgrade2018_realistic_v11_L1v1_ext2-v2/MINIAODSIM" > SingleNeutrino_CP1.list
dasgoclient --limit=0 --query="file dataset=/SingleNeutrino/RunIISummer19UL18MiniAOD-FlatPU0to75_106X_upgrade2018_realistic_v11_L1v1_ext1-v1/MINIAODSIM " > SingleNeutrino_CP5.list

#dasgoclient --limit=0 --query="file dataset=/ZeroBias/Run2018A-12Nov2019_UL2018-v2/MINIAOD  " > ZeroBiasA.list
#dasgoclient --limit=0 --query="file dataset=/ZeroBias/Run2018B-12Nov2019_UL2018-v2/MINIAOD  " > ZeroBiasB.list

#dasgoclient --limit=0 --query="file dataset=/MinimumBias/Run2018A-12Nov2019_UL2018-v1/MINIAOD  " > MinBiasA.list
#dasgoclient --limit=0 --query="file dataset=/MinimumBias/Run2018B-12Nov2019_UL2018-v1/MINIAOD  " > MinBiasB.list
#dasgoclient --limit=0 --query="file dataset=/MinimumBias/Run2018C-12Nov2019_UL2018-v1/MINIAOD  " > MinBiasC.list
#dasgoclient --limit=0 --query="file dataset=/MinimumBias/Run2018D-12Nov2019_UL2018-v1/MINIAOD  " > MinBiasD.list

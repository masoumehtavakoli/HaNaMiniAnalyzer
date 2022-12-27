#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /afs/cern.ch/user/h/helfaham/CMSSW_10_6_4_patch1/src/Haamm/HaNaMiniAnalyzer/test/PUStudies
eval `scramv1 runtime -sh`

if [ ! -z "$CONDORJOBID" ];
then
    #export FILEID=$CONDORJOBID #you might want to add this.
    echo $CONDORJOBID
    export xsecvariation=`expr $CONDORJOBID + 840` #you might want to subtract zero.
    echo $xsecvariation
fi
#variations[1000-1170][840-1000]

xsec=`echo 69200 \* $xsecvariation / 1000. | bc`
echo $xsec

nBins1=100
#nBins2=200 #that was a special configuration for ZeroBiasEraE normally both are 100

#TODO always specify the JSON file you are using here, the script automatically takes it from certification directly and I don't know why

#ANJSON=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt
ANJSON=$1
appendixName=$2

function produce {
    pileupCalc.py -i $ANJSON --inputLumiJSON $1 --calcMode true --minBiasXsec $xsec --maxPileupBin $nBins1 --numPileupBins $nBins1 --pileupHistName=h_${xsecvariation} /eos/home-h/helfaham/data_$2_${xsecvariation}_${appendixName}.root
    
    echo pileupCalc.py -i $ANJSON --inputLumiJSON $1 --calcMode true --minBiasXsec $xsec --maxPileupBin $nBins1 --numPileupBins $nBins1 --pileupHistName=h_${xsecvariation} /eos/home-h/helfaham/data_$2_${xsecvariation}_${appendixName}.root

#echo pileupCalc.py -i $ANJSON --inputLumiJSON $1  --calcMode true --minBiasXsec $xsecDown --maxPileupBin $nBins --numPileupBins $nBins ./data_$2_${xsecvariation}_down.root
    #echo pileupCalc.py -i $ANJSON --inputLumiJSON $1  --calcMode true --minBiasXsec $xsecUp --maxPileupBin $nBins --numPileupBins $nBins ./data_$2_${xsecvariation}_up.root
}

#produce ./datacert2016ReRecoByLS_Pre3puJSON.txt pcc
#produce /eos/cms/store/user/jsalfeld/datacert2016ReRecoByLSpuJSON.txt bestFit
produce /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PileUp/pileup_latest.txt latest  
#produce ./pileup_JSON.txt JSON  


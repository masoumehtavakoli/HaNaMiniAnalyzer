#!/bin/bash

export X509_USER_PROXY=$1
source /cvmfs/cms.cern.ch/cmsset_default.sh
voms-proxy-info

export SCRAM_ARCH=$2
scramv1 project CMSSW $3
cd $3/src/
export SCRAM_ARCH=$2
eval `scramv1 runtime -sh`

mkdir Haamm/
cd Haamm
git clone -b $4 https://github.com/masoumehtavakoli/HaNaMiniAnalyzer.git
cd HaNaMiniAnalyzer/
git checkout $4
scram b
cd test
if [ ! -z "$LSB_JOBINDEX" ];
then
    echo $LSB_JOBINDEX
    export FILEID=`expr $LSB_JOBINDEX - 1`
    echo $FILEID
else
    if [ ! -z "$CONDORJOBID" ];
    then
	export FILEID=$CONDORJOBID
	echo $FILEID
    fi
fi

echo cmsRun SimplePUAnalyzer_cfg.py sample=$5 job=$FILEID output=$6 nFilesPerJob=$8
cmsRun SimplePUAnalyzer_cfg.py sample=$5 job=$FILEID output=$6 nFilesPerJob=$8

outfilename=`ls $6*$5*.root`
outfilenames=`ls *$6*$5*.root`

ls -l $outfilenames

eval `scram unsetenv -sh`
source /cvmfs/sft.cern.ch/lcg/views/LCG_102b_cuda/x86_64-centos7-gcc8-opt/setup.sh

./ConvertToHD5.py --input $outfilenames
#python3 main_script.py -R $outfilenames

rm -f $outfilenames

outfilename=`ls $6*$5*.h5`
outfilenames=`ls *$6*$5*.*`

ls -l $outfilenames


if [[ $7 == eos* ]] ;
then
    #first try to copy to /eos
    if [[ -d "/eos" && -x "/eos" ]]; then
	mkdir -p /$7

	if [ -f  /$7/$outfilename ]; then
	    echo "the file exists, is being renamed"
	    rm -f /$7/${outfilename}_
	    rm -f /$7/$outfilename
	fi

	COUNTER2=0
	while [ ! -f  /$7/$outfilename ]
	do
	    if [ $COUNTER2 -gt 20 ]; then
		break
	    fi
	    cp $outfilenames /$7/
	    let COUNTER2=COUNTER2+1
	    echo ${COUNTER2}th Try
	    sleep 10
	done

	if [ -f  /$7/$outfilename ]; then
	    echo "The file was copied succesfully via the /eos mounting point on machine"
	    rm $outfilenames
	    exit 0
	fi
    fi

    #second try to copy via eoscp command
    eos mkdir -p /$7
    if [ $? -eq 0 ] || [ $? -eq 17 ] ;
    then
	for file in *$6*$5*.root; do
	    eoscp  $file /$7/$file
	done 
    fi

    COPIED=0
    for file in *$6*$5*.root; do
	eos ls /$7/$file
	if [ $? -ne 0 ];
	then
	    echo $file is not copied via the eoscp method
	    let COPIED=COPIED+1
	fi
    done 
    
    if [ $COPIED -eq 0 ];
    then
	rm $outfilenames
	exit 0
    fi

    #third try : to copy via mounting eos in local directory
    echo is mounting eos
    mkdir eos


    COUNTER1=0
    /afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select -b fuse mount eos
    mountpoint eos
    while [ $? -ne 0 ]; 
    do
	if [ $COUNTER1 -gt 20 ]; then
	    break
	fi
	/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select -b fuse mount eos
	let COUNTER1=COUNTER1+1
	echo ${COUNTER1}th Try to mount eos
	sleep 10
	mountpoint eos
    done

    mountpoint eos
    if [ $? -ne 0 ]; then
	echo Eos not mounted after 20 tries
	exit 1
    fi

    mkdir -p $7

    if [ -f  $7/$outfilename ]; then
	echo "the file exists, is being renamed"
	rm -f $7/${outfilename}_
	mv $7/$outfilename $7/${outfilename}_
    fi

    COUNTER2=0
    while [ ! -f  $7/$outfilename ]
    do
	if [ $COUNTER2 -gt 20 ]; then
	    break
	fi
	cp $outfilenames $7/
	let COUNTER2=COUNTER2+1
	echo ${COUNTER2}th Try
	sleep 10
    done

    if [ ! -f  $7/$outfilename ]; then
	echo "The file was not copied to destination after 20 tries"
	exit 1
    fi


    /afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select -b fuse umount eos
    rm -rf eos
else
    mkdir -p $7


    if [ -f  $7/$outfilename ]; then
	echo "the file exists, is being renamed"
	rm -f $7/${outfilename}_
	mv $7/$outfilename $7/${outfilename}_
    fi

    COUNTER2=0
    while [ ! -f  $7/$outfilename ]
    do
	if [ $COUNTER2 -gt 20 ]; then
	    break
	fi
	cp $outfilenames $7/
	let COUNTER2=COUNTER2+1
	echo ${COUNTER2}th Try
	sleep 10
    done

    if [ ! -f  $7/$outfilename ]; then
	echo "The file was not copied to destination after 20 tries"
	exit 1
    fi
    rm $outfilenames
fi

#!/usr/bin/env python3
nFilesPerJob=1
import sys
import getpass
user = getpass.getuser()
if not len(sys.argv) == 3 :
    print("exactly two options are needed : ")
    print("%s [working dir] [output dir on eos]" % (sys.argv[0]))
    exit()

prefix = "out"
#OutPath = "/%s/%s/" % (sys.argv[2], user )
#OutPath = "/eos/cms/store/user/%s/%s/" % (user, sys.argv[2] )
OutPath = "/eos/home-m/mjalava/Run1/"

from SamplesPU.Samples import MINIAOD22 as samples
for sample in samples:
    sample.MakeJobs( nFilesPerJob , "%s/%s" % (OutPath , prefix) )

import os
from shutil import copy

workingdir = sys.argv[1]
while os.path.isdir( "./%s" % (workingdir) ):
    workingdir += "_"
os.mkdir( workingdir )

from subprocess import call
call(["voms-proxy-init" , "--out" , "./%s/.x509up_u%d" % ( workingdir , os.getuid()) , "--voms" , "cms" , "--valid" , "1000:0"])


file_sh = open("%s/Submit.sh" % (workingdir) , "w" )


for sample in samples:
    #if not sample.Name.count("CP"):
    #    continue

    os.mkdir( "%s/%s" % (workingdir , sample.Name) )
    copy( "SetupAndRun.sh" , "./%s/%s" % (workingdir , sample.Name) )

    file = open("%s/%s/Submit.cmd" % (workingdir , sample.Name) , "w" )
    #print >> file, 'requirements            = (OpSysAndVer =?= "SLCern6")'
    print("executable              = %s/%s/%s/SetupAndRun.sh" % (os.getcwd() , workingdir , sample.Name) , file=file)
    print("output                  = $(ClusterId)_$(ProcId).out" , file=file)
    print( "error                   = $(ClusterId)_$(ProcId).err" , file=file)
    print( "log                     = $(ClusterId)_$(ProcId).log" , file=file)
    print( '+JobFlavour             = "testmatch"' , file=file)
    print( "environment             = CONDORJOBID=$(ProcId)" , file=file)
    print( "notification            = Error" , file=file)
    print( "" , file=file)
    print( "arguments               = %(vomsaddress)s %(scram)s %(cmsver)s %(gitco)s %(sample)s %(out)s %(outdir)s %(nFilesPerJob)d" % { 
        "vomsaddress":"%s/%s/.x509up_u%d" % (os.getcwd() , workingdir , os.getuid()) ,
        "scram":os.getenv("SCRAM_ARCH") ,
        "cmsver":os.getenv("CMSSW_VERSION"),
        "gitco":"PUGNN" ,
        "sample":sample.Name ,
        "out":prefix,
        "outdir":OutPath,
        "nFilesPerJob":nFilesPerJob
        } , file=file)
           
    print( "queue %d" % (len(sample.Jobs)) , file=file)

    print( "" , file=file)

    file.close()

    print( "cd %s" % (sample.Name)  , file=file_sh)
    print( "condor_submit -batch-name %s Submit.cmd" % (sample.Name)  , file=file_sh)
    print( "cd .." , file=file_sh)


print("to submit the jobs, you have to run the following commands :")
print("cd %s" % (workingdir))
print("source Submit.sh")
file_sh.close()

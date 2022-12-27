#!/usr/bin/env python
nFilesPerJob=4
CheckFailedJobs=True
hname = "PUAnalyzer/CutFlowTable/CutFlowTable"
prefix = "out"

from ROOT import TFile, TH1
import sys
import getpass
user = getpass.getuser()

if not len(sys.argv) == 3 :
    print "exactly two options are needed : "
    print "%s [working dir] [output dir on eos]" % (sys.argv[0])
    exit()

OutPath = "eos/cms/store/user/%s/%s/" % (user, sys.argv[2] )
from SamplesPU.Samples import MINIAOD as samples
for sample in samples:
    print sample.Name
    print sample.MakeJobs( nFilesPerJob , "%s/%s" % (OutPath , prefix) )

import os
from shutil import copy
from os import listdir
from os.path import isfile, join, splitext, basename

workingdir = sys.argv[1]
while os.path.isdir( "./%s" % (workingdir) ):
    workingdir += "_"
os.mkdir( workingdir )

copy( "SetupAndRun.sh" , "./%s/" % (workingdir) )

from subprocess import call
call(["voms-proxy-init" , "--out" , "./%s/.x509up_u%d" % ( workingdir , os.getuid()) , "--voms" , "cms" , "--valid" , "1000:0"])


FailedJobs = {}
if CheckFailedJobs:
    for sample in samples:

        ListOfFailedJobs = []
        for job_ in sample.Jobs :
            outfile = job_.Output
            job = job_.Index + 1
            if isfile( outfile ) :
                ff = TFile.Open(outfile)
                h = ff.Get("%s_%s"% ( hname , sample.Name) )
                if not h == None :
                    ntotal = h.GetBinContent(1)
                    if ntotal == 0:
                        if not sample.IsData : #data may be is null because of json
                            print outfile + " : Exists with no entry"
                            ListOfFailedJobs.append( str(job))
                else :
                    ListOfFailedJobs.append(str( job ))
                    print job
                    print outfile + " : Exists, without histogram"

            else :
                ListOfFailedJobs.append( str(job))
                print outfile + " : file doesn't exist  " 

        FailedJobs[ sample.Name ] = ListOfFailedJobs
    print FailedJobs

file = open("%s/submit.sh" % (workingdir) , "w" )
for sample in samples:

    if CheckFailedJobs:
        if len(FailedJobs[ sample.Name ]) > 0:
            #command = 'bsub -q 8nh -J "%(sample)s%(countor)s[%(list)s]"  -o %(sample)s%%I.out `pwd`/SetupAndRun.sh %(vomsaddress)s %(scram)s %(cmsver)s %(gitco)s %(sample)s %(out)s %(outdir)s %(nFilesPerJob)d' % {
            command = 'bsub -q 8nh -J "%(sample)s%(countor)s[%(list)s]"  -o %(sample)s%%I.out `pwd`/SetupAndRun.sh %(vomsaddress)s %(scram)s %(cmsver)s %(gitco)s %(sample)s %(out)s %(outdir)s %(nFilesPerJob)d' % {
                "vomsaddress":"`pwd`/.x509up_u%d" % (os.getuid()) ,
                "scram":os.getenv("SCRAM_ARCH") ,
                "cmsver":os.getenv("CMSSW_VERSION"),
                "gitco":"HamedPU" ,
                "sample":sample.Name ,
                "out":prefix ,
                "outdir":OutPath,
                "countor":"RS",
                "list":",".join( FailedJobs[sample.Name] ),
                "nFilesPerJob":nFilesPerJob
                }
            print >> file, command
        

    else :
        initlen = len(sample.Jobs)
        print sample.Jobs
        steps = range( 0 , initlen , 1000 )
        print steps
        if not steps[-1] == initlen :
            steps.append( initlen )
        print "%s : %d"% ( sample.Name , initlen )
        print steps
        for i in range( 0 , len(steps)-1):
            #command = 'bsub -q 8nh -J "%(sample)s%(countor)d[%(init)d-%(nfiles)d]" -o %(sample)s%%I.out `pwd`/SetupAndRun.sh %(vomsaddress)s %(scram)s %(cmsver)s %(gitco)s %(sample)s %(out)s %(outdir)s %(nFilesPerJob)d' % {
            command = 'bsub -q 8nh -J "%(sample)s%(countor)d[%(init)d-%(nfiles)d]" -o %(sample)s%%I.out `pwd`/SetupAndRun.sh %(vomsaddress)s %(scram)s %(cmsver)s %(gitco)s %(sample)s %(out)s %(outdir)s %(nFilesPerJob)d' % {
                "vomsaddress":"`pwd`/.x509up_u%d" % (os.getuid()) ,
                "scram":os.getenv("SCRAM_ARCH") ,
                "cmsver":os.getenv("CMSSW_VERSION"),
                "gitco":"HamedPU" ,
                "sample":sample.Name ,
                "out":prefix ,
                "outdir":OutPath,
                "nfiles":steps[i+1],
                "init":steps[i]+1,
                "countor":i,
                "nFilesPerJob":nFilesPerJob
                }
            print >> file, command


file.close()
print "to submit the jobs, you have to run the following commands :"
print "cd %s" % (workingdir)
print "source submit.sh"


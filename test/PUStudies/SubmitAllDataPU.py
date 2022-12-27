#!/usr/bin/env python
import sys
import getpass
user = getpass.getuser()

#prefix   = "data"
OutPath  = "/%s/%s/" % (sys.argv[2],user) 

import os
from os import listdir
#variations = range( 84 , 117 )
jsons = {"All":"/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt"} 
dir="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/Era/Prompt/"
for f in listdir(dir):
    era = f.split("_")[-1].split(".")[0]
    jsons[era] = dir+f
#    era.MakeJobs(nFilesPerJob, "%s/%s" %(OutPath, prefix))

workingdir = sys.argv[1] 
while os.path.isdir( "./%s" % (workingdir) ):
    workingdir += "_"
os.mkdir( workingdir )

from subprocess import call
call(["voms-proxy-init" , "--out" , "/tmp/.x509up_u%d" % (os.getuid()) , "--voms" , "cms" , "--valid" , "1000:0"])

file_sh = open ("%s/Submit.sh" % (workingdir), "w")
import shutil
from shutil import copy
#queue = "8nm"
for era in jsons:
#    command = "produceDataPU.sh {json:s} {era:s}"
#    submit = ('bsub -q {que:s} -J "{era:s}[840-1170]" -o datapu/{era:s}_{var:s}.out ' + command).format( var="%I" , json=jsons[era] , era=era , que=queue )
#    print submit
    
    if not era.count("eraC"):
        continue

    os.mkdir( "%s/%s" % (workingdir , era) )
    shutil.copy( "produceDataPU.sh" , "./%s/%s" % (workingdir,era))

    file = open ("%s/%s/Submit.cmd" % (workingdir, era), "w")
    print >> file, "executable              = %s/%s/%s/produceDataPU.sh" % (os.getcwd() , workingdir , era)
    print >> file, "output                  = $(ClusterId)_$(ProcId).out"
    print >> file, "error                   = $(ClusterId)_$(ProcId).err"
    print >> file, "log                     = $(ClusterId)_$(ProcId).log"
    print >> file, '+JobFlavour             = "tomorrow"'
    print >> file, "environment             = CONDORJOBID=$(ProcId)"
    print >> file, "notification            = Error"
#    print >> file, "should_transfer_files   = YES"
#    print >> file, "when_to_transfer_output = ON_EXIT"
    print >> file, ""
    print >> file, "arguments               = %(JSON)s %(Appendix)s " % {
        "JSON":jsons[era],
        "Appendix":era
        }
    #print >> file, "queue %d" % (len(era))
    print >> file, "queue 160" #[from 840-999, you need 160 jobs that ranges from 0 to 159 which plus 840 in produceDataPU gives from h_840-h_999]
    #print >> file, "queue 171" #[from 1000-1170, you need 171 jobs that ranges from 0 to 170 which plus 1000 in produceDataPU gives from h_1000-h_1170]
    print >> file, ""

    file.close()

    print >> file_sh, "cd %s" % (era)
    print >> file_sh, "condor_submit -batch-name %s Submit.cmd" % (era)
    print >> file_sh, "cd .."


print "to submit the jobs, you have to run the following commands :"
print "cd %s" % (workingdir)
print "source Submit.sh"
file_sh.close()

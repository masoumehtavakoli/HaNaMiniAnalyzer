import sys
from os import listdir
from os.path import isfile, join
import Utilities.General.cmssw_das_client as das_client
#from das_client import *
from subprocess import call
import os, ntpath
import os.path
from Haamm.HaNaMiniAnalyzer.JSONSample import *
import json
####NEVER TRY TO IMPORT ROOT MODULES IN THE PYTHON CONFIGURATION, Oherwise CMSSW fails in initiating the tree
#kGray = 920
#kGreen = 416
#kOrange = 800
#kRed = 632
#kBlack = 1
#kCyan = 432
#kBlue = 600
######################################################################

def GetUserName(arg=2):
    user=""
    if len(sys.argv) > arg :
        user = sys.argv[arg]
    else:
        import getpass
        user = getpass.getuser()
    return user


##recommended code to group a list : https://docs.python.org/2/library/itertools.html#recipes
from itertools import zip_longest
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)
#### grouper code

class JobInformation:
    def __init__( self, sample , index , inputs , output ):
        self.Sample = sample 
        self.Index = index
        self.Inputs = inputs
        bn = os.path.basename( output )
        dn = os.path.dirname( output )
        if dn == "":
            self.Output2 = ("edm_output_" + output)
        else :
            self.Output2 = dn +  "/edm_output_" + bn

        if dn.startswith( "/store/user/" ) :
            output = "eos/cms" + output

        self.Output = output
class Sample :
    WD = './'

    def __str__(self):
        return self.Name
    
    def __init__(self , name , xsection , lheW , datasetname , appendix = "" , dbsInstance = "phys03" , info_from_json = None , treeName = None ):
        self.Jobs = []
        self.Name = name
        self.XSection = xsection
        self.IsData = (self.XSection == 0)
        self.LHEWeight = lheW
        
        self.Files = []

        self.DSName = datasetname
        self.Prefix = appendix

        self.DBSInstance = dbsInstance
        #for the samples created from the outputs of another sample, the histo files are needed to 
        #count the total number of events without cuts
        self.ParentSample = None

        
        self.JSONInfo = info_from_json
        if info_from_json:
            if os.path.exists( self.JSONInfo["jsonfile"] ):
                f = open( self.JSONInfo['jsonfile'] , 'r')
                self.JSONFile = json.load(f)[self.DSName]
                f.close()

        
        if not datasetname == "" :
            self.InitiateFilesFromListOrDAS( datasetname , appendix )

        if treeName :
            self.TreeName = treeName
            
    def AddFiles( self , directory ):
        files = [join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]
        self.Files.extend( files )

    def GetListFileName( self ):
        return Sample.WD + "/" + self.Name + ".list"

    def WriteFileListToFile( self ):
        if os.path.exists(self.GetListFileName() ):
            os.remove( self.GetListFileName() )

        with open(self.GetListFileName() , 'w') as f :
            for fline in self.Files :
                f.write( fline + "\n" )

    def LoadFilesFromList(self):
        if os.path.exists( self.GetListFileName() ):
            with open(self.GetListFileName() , 'r') as f :
                for line in f.readlines() :
                    self.Files.append( line.strip() )

    def InitiateFilesFromListOrDAS( self , sample , prefix = "" ):
        self.Files = []
        self.LoadFilesFromList()

        if len(self.Files) == 0 and hasattr( self , "JSONFile") :
            json_sample = JSONSample( self.DSName , self.JSONFile ,self.JSONInfo['jsonfile'] )
            for f in json_sample.Files:
                self.Files.append( str(f.name) )
                self.WriteFileListToFile()
        
        if len(self.Files) == 0 :
            self.AddDASFiles( sample , prefix )
            self.WriteFileListToFile()

    def MakeSampleFromOutputs(self):
        ret = Sample( self.Name , self.XSection , self.LHEWeight , "" , dir )
        ret.DSName = self.DSName
        for j in self.Jobs:
            ret.Files.append( "%s" % ( j.Output2 ) )
        ret.ParentSample = self
        return ret

    def AddDASFiles( self , sample , prefix = "" ):
        return
        jsondict = get_data( "https://cmsweb.cern.ch" , 
                             "file dataset=%(sample)s instance=prod/%(dbs)s"  %  {'sample':sample , 'dbs':self.DBSInstance} ,
                             0 , #idx
                             0 , #limit
                             0 , #verbose
                             300 , #waiting time
                             "~/.globus/userkey.pem"  ,   #ckey
                             "~/.globus/usercert.pem" , #cert
                             )
        
        cli_msg  = jsondict.get('client_message', None)
        if  cli_msg:
            print ("DAS CLIENT WARNING: %s" % cli_msg)
        if  'status' not in jsondict:
            print ('DAS record without status field:\n%s' % jsondict)
            sys.exit(EX_PROTOCOL)
        if  jsondict['status'] != 'ok':
            print ("status: %s, reason: %s" \
                % (jsondict.get('status'), jsondict.get('reason', 'N/A')))
            sys.exit(EX_TEMPFAIL)

        data = jsondict['data']
        iii = 1
        for jjj in data:
            #print "%d/%d : %s" % ( iii , len(data) , ntpath.basename(str(prim_value(jjj))) )
            iii += 1
            self.Files.append( prefix + str( prim_value(jjj) ) )


    def MakeJobs( self , nFilesPerRun , prefix_out ):
        self.Jobs = []
        indices = range(0 , len( self.Files) )
        job_counter = 0
        for input_files_in_job in grouper( indices , nFilesPerRun , -1000 ):
            inputfiles = [ self.Files[i] for i in input_files_in_job if i > -100 ]

            outputfilename = ""
            if nFilesPerRun == 1:
                outputfilename = "%(prefix)s_%(sample)s_%(input)s.root" % {
                    "prefix":prefix_out , 
                    "sample":self.Name , 
                    "input":os.path.splitext( os.path.basename( inputfiles[0] ))[0]
                    }
            else:
                outputfilename = "%(prefix)s_%(sample)s_%(input)s_%(nFiles)d.root" % {
                    "prefix":prefix_out , 
                    "sample":self.Name , 
                    "input":os.path.splitext( os.path.basename( inputfiles[0] ))[0],
                    "nFiles":nFilesPerRun
                    }
            jjj =JobInformation( self.Name, job_counter , inputfiles , outputfilename )
            setattr( self, "Job%d" % (job_counter) , jjj )
            self.Jobs.append( getattr( self , "Job%d" % (job_counter) ) )
            job_counter+=1
            
        return job_counter

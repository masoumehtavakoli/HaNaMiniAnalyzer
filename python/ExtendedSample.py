from ROOT import TDirectory, TFile, TCanvas , TH1D , TH1 , THStack, TList, gROOT, TLegend, TPad, TLine, gStyle, TTree , TObject , gDirectory, TChain

import os
import sys
import Sample
import fnmatch

from Sample import *

class ExtendedSample: #extend the sample object to store histograms
    def __init__( self , sample , additionalCut = None  ):
        self.Name = sample.Name 
        self.XSection = sample.XSection 
        self.XSections = {0:self.XSection}
        self.LHEWeight = sample.LHEWeight 
        self.DSName = sample.DSName 
        self.Prefix = sample.Prefix
        self.IsData = sample.IsData

        self.JSONInfo = sample.JSONInfo
        
        self.Files = sample.Files
        self.Jobs = sample.Jobs

        if sample.ParentSample :
            self.ParentSample = ExtendedSample( sample.ParentSample )
        else :
            self.ParentSample = None

        if hasattr(sample, "TreeName") :
            self.TreeName = sample.TreeName

        self.AdditionalCut = additionalCut
        
    def LoadJobs(self , Dir , pattern_ = "%s.root" ):
        Dirs = Dir.split(";")            
        self.JobFilesDir = Dirs[0]
        self.Jobs = []
        pattern = ( pattern_ % (self.Name) )
        for fn, ff in [("%s/%s" % ( Dirs[0] , f) , f) for f in os.listdir(Dirs[0])]:
            #print fn
            if os.path.isfile(fn):
                if fnmatch.fnmatch(ff , pattern):
                    self.Jobs.append( JobInformation( self , 0 , self.Files , fn ) )
        if self.ParentSample and (len(Dirs) == 2):
            self.ParentSample.LoadJobs( Dirs[1] , pattern_)
        print (self.Name)
        #print self.Jobs
        
    def GetCFT(self , index = 0):
        if not hasattr( self, "CutFlowTableName" ):
            return None
        if not self.CutFlowTableName in self.AllHists:
            return None
        return self.AllHists[self.CutFlowTableName][index]

    def SetNTotal(self, n):
        self.NTotal = n
    
    def GetNTotal(self , index = 0) :
        if hasattr(self, "NTotal") :
            return self.NTotal
        if self.ParentSample :
            if not self.ParentSample.GetCFT(index) :
                print ("\tLoading parent sample")
                self.ParentSample.LoadHistos( self.DirName , self.CutFlowTableName , [self.CutFlowTableName] , self.LoadedIndices )
                print ("\tLoaded %s = %d" % ( self.Name , self.ParentSample.GetNTotal(index) ))
            return self.ParentSample.GetNTotal(index)
        else :
            if not self.GetCFT(index) :
                return -1
            print ("\t%s is read for total number of events" % (self.GetCFT(index).GetName() ))
            return self.GetCFT(index).GetBinContent( 1 )

    def NormalizeHistos(self, lumi):
        if self.IsData :
            return
        for index in self.LoadedIndices:
            if self.XSection < 0 :
                self.XSFactor = lumi
            else:
                self.nTotal = self.GetNTotal()
                if self.nTotal == 0:
                    print ("\tSample %s has no entries" % (self.Name))
                    return
                self.XSFactor = lumi*self.XSections[index]/self.nTotal
            print ("\t\tXSFactor[%d] for lumi %d is : %.4f" % (index , lumi , self.XSFactor))
            #print "%s factor : (%.2f*%.2f)/%.0f = %.3f" % (sample , lumi , self.XSections[sample] , ntotal  , factor)
            for h in self.AllHists :
                if len(self.AllHists[h]):
                    before = self.AllHists[h][index].Integral()
                    self.AllHists[h][index].Scale(self.XSFactor)
                    after = self.AllHists[h][index].Integral()
                    #print "\t\tBefore : %f , after : %f" % (before, after)

    def SetFriendTreeInfo(self , friendsDir , friendTreeName ):
        self.FriendsDir = friendsDir
        self.FriendTreeName = friendTreeName
        
    def LoadTree(self , treeName ):
        if hasattr(self,"Tree"):
            return

        self.Tree = TChain( treeName )
        for Job in self.Jobs:
            self.Tree.Add( Job.Output )

        if hasattr( self , "FriendsDir"):
            self.FriendFile = TFile.Open( "%s/%s.root" % (self.FriendsDir , self.Name ) )
            self.FriendTree = self.FriendFile.Get( self.FriendTreeName )
            self.Tree.AddFriend( self.FriendTree )
            
        
    def DrawTreeHistos( self , treeselections ,  treeName = "tHq/Trees/Events"):
        if hasattr(self, "TreeName" ):
            treeName = self.TreeName
            print ("Tree Name is : %s" % (treeName))
        self.LoadTree(treeName)
        
        if not hasattr( self, "LoadedIndices" ):
            print ("call DrawTreeHistos after LoadHistos")

        for selection in treeselections:
            treehists = selection.LoadHistos( self.Name , self.IsData , self.Tree , self.LoadedIndices , self.AdditionalCut )
            for hist in treehists :
                if not hist in self.AllHists:
                    self.AllHists[hist] = {}
                for n in treehists[hist]:
                    self.AllHists[hist][n] = treehists[hist][n]

        self.Tree.GetFile().Close()
                    
    def LoadHistos(self , dirName = "tHq" , cftName = "CutFlowTable" , loadonly = [] , indices = [0]):
        self.LoadedIndices = indices
        self.CutFlowTableName = cftName
        self.DirName = dirName
        self.AllHists = {}
        for Job in self.Jobs :
            finame = Job.Output
            #sys.stdout.write("\r%s : %d of %d" % (self.Name , Job.Index+1 , len(self.Jobs)))
            #sys.stdout.flush()
            ff = None
            if os.path.isfile( finame ):
                ff = TFile.Open(finame)
            else:
                print ("File %d of sample %s doesn't exist, skip it , %s" % (Job.Index , self.Name , finame))
                continue
            dir = ff.GetDirectory(dirName)
            if not dir :
                print ("File %d of sample %s is not valid, skip it , %s" % (Job.Index , self.Name , finame))
                continue
            for dir__ in dir.GetListOfKeys() :
                if not dir__.IsFolder():
                    continue
                propname = dir__.GetName()
                if len(loadonly) > 0 and not propname in loadonly :
                    continue
                print ("\t\tloading %s (indices = %s)" % ( propname, str(indices) ))
                dir_ = dir.GetDirectory( propname )
                dircontents = dir_.GetListOfKeys()
                selectedHistos = {}
                for index in indices:
                    if dircontents.GetEntries() <= index:
                        continue                    
                    thehisto = None
                    for dirindex in range( 0,dircontents.GetEntries() ):
                        dircont = dircontents.At(dirindex).GetName()
                        searchfor = "_%d" % (index)
                        isitthat = dircont.endswith( searchfor  )
                        #print "%s.endswith( %s ) = %r" % (dircont , searchfor , isitthat )
                        if isitthat:
                            thehisto = dir_.Get( dircont )
                            break
                    #print [propname , index]
                    if thehisto and thehisto.ClassName().startswith("TH"):
                        selectedHistos[index] = thehisto 

                if propname in self.AllHists.keys() :
                    for index in selectedHistos:
                        firsthisto = selectedHistos[index]
                        self.AllHists[propname][index].Add( firsthisto )
                else :
                    gROOT.cd()
                    self.AllHists[propname] = {}
                    for index in selectedHistos:
                        firsthisto = selectedHistos[index]
                        hnew = firsthisto.Clone("%s_%s_%d" % ( propname , self.Name , index ) )
                        hnew.SetBit(TH1.kNoTitle)
                        #hnew.Reset()
                        setattr( self , "%s_%d" % (propname, index) , hnew )
                        hhh = getattr( self , "%s_%d" % (propname, index) )
                        hhh.SetLineColor( 1 )
                        hhh.SetLineWidth( 2 )
                        if not self.IsData :
                            hhh.SetFillStyle( 1001 )
                        else:
                            hhh.SetStats(0)

                        self.AllHists[propname][index] = hhh    
                    
            ff.Close()

        if len(self.AllHists)==0 :
            return False
        else:
            return True


    def readKeys(self , directory):
        """Return a list of objects in directory that inherit from tree or histo. """

        if not directory.InheritsFrom("TDirectory"):
            return []
        selKeys = [key for key in directory.GetListOfKeys() if key.ReadObj().InheritsFrom("TH1") or key.ReadObj().InheritsFrom("TTree") or key.ReadObj().InheritsFrom("TDirectory")]
        ret = {}
        for k in selKeys:
            kcycle = k.GetCycle()
            kname = k.GetName()

            lastCycle = -1
            if kname in ret :
                lastCycle = ret[ kname ][0]
            if not (kcycle > lastCycle):
                continue
            elif (kcycle == lastCycle):
                print ("%s has two similar cycle values %d and %d" % (kname , kcycle , lastCycle ))

            ret[ kname ] = ( kcycle , k.ReadObj() )

        return [ ret[s][1] for s in ret ]

    def loop(self , directory):
        """Traverse directory recursively and return a list of (path, name) pairs of
        all objects inheriting from classname."""
        
        contents = []

        for d in self.readKeys(directory):
            if not d.InheritsFrom("TDirectory") :
                contents.append((directory.GetPath().split(':')[-1], d.GetName() ))
            else :
                contents += self.loop(d)

        return contents

    def fhadd(self, prefix = "" , force=False, verbose=False, slow=True):
        """ taken from https://root.cern.ch/phpBB3/viewtopic.php?t=14881
        This function will merge objects from a list of root files and write them    
        to a target root file. The target file is newly created and must not
        exist, or if -f ("force") is given, must not be one of the source files.
        
        IMPORTANT: It is required that all files have the same content!

        Fast but memory hungry alternative to ROOT's hadd.
        
        Arguments:

        target -- name of the target root file
        sources -- list of source root files
        classname -- restrict merging to objects inheriting from classname
        force -- overwrite target file if exists
        """

        target = prefix + self.Name + ".root"
        sources = [j.Output for j in self.Jobs]

        TH1.AddDirectory(False)
        # check if target file exists and exit if it does and not in force mode
        if not force and os.path.exists(target):
            raise RuntimeError("target file %s exists" % target)

        # open the target file
        print ("fhadd Target file:", target)
        outfile = TFile.Open(target, "RECREATE")

        # open the seed file - contents is looked up from here
        seedindex = 1
        seedfilename = sources[seedindex-1]
        while (not os.path.exists(seedfilename)) and (seedfilename < 2) : #len(sources)): 
            seedfilename = sources[seedindex]
            seedindex += 1
            print ("Seed file doesn't exist, moving to the next one")
        if seedindex > len(sources) :
            raise RuntimeError("none of the files are available")

        print ("fhadd Source file %d : %s" % (seedindex , seedfilename))
        seedfile = TFile.Open(seedfilename)


        # get contents of seed file
        print ("looping over seed file")
        contents = self.loop(seedfile)
        print ("done %d objects are ready to be merged" % len(contents))
        if( verbose or True ):
            for c in contents:
                print (c)
                

        # open remaining files
        otherfiles = []
        notexistingfiles=[]
        for n, f in enumerate(sources[seedindex:]):
            print ("fhadd Source file %d: %s" % (n+2, f))
            if not os.path.exists(f):
                notexistingfiles.append( f )
                continue
            otherfiles.append(TFile.Open(f))

        print ("The following files don't exist %s" % notexistingfiles)
        
        # loop over contents and merge objects from other files to seed file objects
        for n, (path, hname) in enumerate(contents):

            print ("fhadd Target object: %s" % os.path.join(path, hname))
            obj_path = os.path.join(path, hname)
            obj_ = seedfile.Get(obj_path[1:])

            outfile.cd('/')
            # create target directory structure
            for d in path.split('/')[1:]:
                directory = gDirectory.GetDirectory(d)
                if not directory:
                    gDirectory.mkdir(d).cd()
                else:
                    gDirectory.cd(d)
            obj = None
            if obj_.InheritsFrom("TTree"):
                obj = obj_.CloneTree()
            else:
                obj = obj_.Clone()

            # merge objects
            l = TList()
            for o in [of.Get(obj_path[1:]) for of in otherfiles]:
                l.Add(o)
            obj.Merge(l)

            # delete objects if in slow mode
            if slow:
                print ("Deleting %d object(s)", l.GetEntries())
                l.Delete()

            # write object to target
            obj.Write(obj.GetName(), TObject.kOverwrite)

        print ("Writing and closing file")

        # let ROOT forget about open files - prevents deletion of TKeys
        for f in [outfile, seedfile]+otherfiles:
            gROOT.GetListOfFiles().Remove(f);

        outfile.Write()
        outfile.Close()

        for f in [seedfile]+otherfiles:
            f.Close()   


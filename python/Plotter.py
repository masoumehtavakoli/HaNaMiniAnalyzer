from ROOT import TDirectory, TFile, TCanvas , TH1D , TH1 , TH2D , THStack, TList, gROOT, TLegend, TPad, TLine, gStyle, TTree , TObject , gDirectory, TEntryList, TEventList

import os
import sys
import Sample
from array import array
from collections import OrderedDict
from ExtendedSample import *
from SampleType import *
from Property import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class HistInfo:
    def __init__(self , name , varname = None , nbins = None , _from = None , to = None , title = "" , Auto = False , dirName = None):
        self.DirName = dirName
        self.Title = title
        self.TwoD = False
        if isinstance(name, HistInfo) and type(varname) == str and nbins == None and _from == None and to == None :
            s = name.Name
            if len(name.Name.split("_")) > 1 :
                s = name.Name.split("_")[-1]
            self.Name = varname + "_" + s
            self.VarName = name.VarName
            
            self.nBins = name.nBins
            self.From = name.From
            self.To = name.To
            self.Auto = name.Auto

            self.DirName = name.DirName
        elif type(name) == str and type(varname) == str and type(nbins) == int and ( type(_from) == float or type(_from) == int ) and ( type(to) == float or type(to) == int ) :
       
            self.Name = name
            self.VarName = varname

            self.nBins = nbins
            self.From = float(_from)
            self.To = float(to)
            self.Auto = False
        elif type(name) == str and type(varname) == str and type(nbins) == int and Auto :
            self.Name = name
                
            self.VarName = varname

            self.nBins = nbins
            self.From = float(0)
            self.To = float(0)
            self.Auto = True
            
        elif isinstance(name, HistInfo) and isinstance(varname, HistInfo) and type(nbins) == str  and _from == None and to == None : #2d
            s = name.Name
            if len(name.Name.split("_")) > 1 :
                s = name.Name.split("_")[-1]
                
            s2 = varname.Name
            if len(s2.split("_")) > 1 :
                s2 = s2.split("_")[-1]

            self.Name = nbins + "_" + s + "vs" + s2
            self.VarName = name.VarName + ":" + varname.VarName

            self.H1 = name
            self.H2 = varname
            self.TwoD = True
            self.Auto = False

        else:
            print ("Initiate histinfo correctly, the given parameters are not allowd")

    def MakeEmptyHist(self , sName , index = 0):
        hname = self.MakeName( sName , index )
        if hasattr(self, "emptyhist" ):
            return self.emptyhist
        elif self.TwoD:
            self.emptyhist = TH2D( hname , self.Title , self.H2.nBins , float( "{0:.2g}".format(self.H2.From)) , float( "{0:.2g}".format(self.H2.To)) , self.H1.nBins , float( "{0:.2g}".format(self.H1.From)) , float( "{0:.2g}".format(self.H1.To)) )
        else:
            self.emptyhist = TH1D( hname , self.Title , self.nBins , float( "{0:.2g}".format(self.From) ) , float( "{0:.2g}".format(self.To)) )

        return self.emptyhist
        
    def Bins(self):
        if self.TwoD:
            return "%s,%s" % (self.H2.Bins() , self.H1.Bins())
        else:
            return "%d,%.2g,%.2g" % (self.nBins , self.From , self.To)
            
    def MakeName(self , sName , index = 0 ):
        return "%s_%s_%d" % (sName , self.Name , index )

class CutInfo:
    def __init__(self, name , cut , weight , title = ""):
        self.Name = name
        self.Cut = cut
        self.Weight = weight

        self.ListOfEvents = {}
        self.ListOfHists = []
        self.AllTH1s = {}

        self.Title = name if title == "" else title
        
    def AddHist(self, name , varname = None , nbins = None , _from = None , to = None , Title = "" , Auto = False , dirName = None ):
        Title = self.Title + ";" + Title 
        if isinstance(name , HistInfo) and varname == None and nbins == None and _from == None and to == None :
            OrigTitle = name.Title.split(";")
            if len(OrigTitle) > 1 :
                Title = ";".join( [ self.Title ] + OrigTitle[1:] )
            else :
                Title = self.Title
            self.ListOfHists.append( HistInfo(name , self.Name , title = Title , dirName = dirName ) )
        elif type(name) == str and type(varname) == str and type(nbins) == int and ( type(_from) == float or type(_from) == int ) and ( type(to) == float or type(to) == int ) :
            self.ListOfHists.append( HistInfo( self.Name + "_" + name , varname , nbins , _from , to , title = Title , dirName = dirName) )
        elif type(name) == str and type(varname) == str and type(nbins) == int and Auto :
            name = name.replace("_" , "")
            self.ListOfHists.append( HistInfo( self.Name + "_" + name , varname , nbins , title = Title , Auto = True , dirName = dirName ) )
        elif isinstance(name , HistInfo) and isinstance(varname , HistInfo) and nbins == None and _from == None and to == None : #2d histogram
            self.ListOfHists.append( HistInfo(name , varname , self.Name , title = Title , dirName = dirName) )
        else:
            print ("Initiate histinfo correctly, the given parameters to AddHists are not allowd(%s=%s,%s=%s,%s=%s,%s=%s,%s=%s)" % (type(name),name,type(varname),varname,type(nbins),nbins,type(_from),_from,type(to),to))

        return self.ListOfHists[-1]
        
    def SetWeight(self, w):
        self.Weight = w
        
    def Weights(self, index = 0 , samplename = "" , isdata = False):
        if hasattr( self , "Weight"):
            if type(self.Weight) == str:
                return self.Weight
            elif type( self.Weight) == dict:
                if samplename in self.Weight:
                    return self.Weight[ samplename ]
                elif isdata and "data" in self.Weight:
                    return self.Weight["data"]
                else:
                    return self.Weight["all"]
        else:
            return ("Weight.W%d" % (index) )

    def LoadHistos( self , samplename , isdata , tree , indices=[0] , additionalCut = None ):
        tree.SetEventList( None )
        cut_ = self.Cut
        if(additionalCut):
            cut_ += " && " + additionalCut
            
        nLoaded = tree.Draw( ">>list_%s_%s"%(samplename, self.Name) , cut_ ) # , "entrylist" )
        #gDirectory.ls()
        lst = gDirectory.Get( "list_%s_%s"%(samplename, self.Name) )
        print ("%s\t\tEvents from tree are loaded (%s , %s), %d" % (bcolors.UNDERLINE, self.Name , cut_ , nLoaded ))
        print ("\t\tHistograms from tree are being created" + bcolors.ENDC)
        if nLoaded < 0:
            print ("Error in loading events with cut (%s) from dataset (%s), nLoaded = %d" % (cut_,samplename , nLoaded))
        if nLoaded < 1 :
            self.ListOfEvents[samplename] = TEventList( "list_%s" % (samplename) , cut_ ) # , tree ) #TEntryList(
        else:
            self.ListOfEvents[samplename] = lst

        #print self.ListOfEvents[samplename]
        #self.ListOfEvents[samplename].Print()
        #self.ListOfEvents[samplename].SetTreeName( tree.GetName() )
        tree.SetEventList( self.ListOfEvents[samplename] )

            
        ret = {}
        for hist in self.ListOfHists:
            ret[hist.Name] = {}
            for n in indices:
                hname =  hist.MakeName(samplename , n)
                gROOT.cd()
                
                tocheck = [] #"jPt","jEta" , "jPhi","bjPt" ]
                for sss in tocheck:
                    if sss in hist.Name:
                        print ("%s : %d , %.2f , %.2f" % (hist.Name , hist.nBins , hist.From , hist.To))

                if nLoaded > 0:
                    if hist.Auto :
                        hist.From = tree.GetMinimum( hist.VarName )
                        hist.To = tree.GetMaximum( hist.VarName )
                        if hist.nBins < 1 :
                            hist.nBins = 10
                        hist.Auto = False
                        import __main__ as main
                        with open(main.__file__ , "a") as f:
                            f.write("#{0:s}:[{1:d},{2:.2g},{3:.2g}]".format( hist.VarName , hist.nBins , hist.From , hist.To ) )
                        

                            
                    tree.Draw( "%s>>cloned_%s(%s)" % ( hist.VarName , hname , hist.Bins() ) ,
                               "" if isdata else self.Weights( n , samplename , isdata) )
                    print (self.Weights(n,samplename,isdata))
                    setattr( self , hname , gDirectory.Get( "cloned_"+hname ).Clone( hname ) )
                else :
                    hcloned_empty = hist.MakeEmptyHist( samplename , n )
                    setattr( self , hname , hcloned_empty )
                hhh = getattr( self , hname )
                hhh.SetTitle( hist.Title )
                #hhh.SetTitle( self.Title )
                rebined = False
                correct = True
                color = bcolors.OKBLUE
                if not hist.TwoD :
                    if not hhh.GetNbinsX() == hist.nBins :
                        if hhh.GetNbinsX()%hist.nBins == 0:
                            hhh.Rebin( hhh.GetNbinsX()/hist.nBins )
                            rebined = True
                            color = bcolors.WARNING
                        else:
                            correct = False
                            color = bcolors.FAIL
                        
                print ("%s\t\t\tHisto %s[%d] created ([%d,%.1f,%1f] and integral=%.2f, average=%.2f)%s" % (color, hist.Name , n , hhh.GetXaxis().GetNbins() , hhh.GetXaxis().GetBinLowEdge(1) , hhh.GetXaxis().GetBinLowEdge( hhh.GetXaxis().GetNbins() ) + hhh.GetXaxis().GetBinWidth( hhh.GetXaxis().GetNbins() ) , hhh.Integral() , hhh.GetMean() , bcolors.ENDC ))
                        
                    
                hhh.SetLineColor( 1 )
                hhh.SetLineWidth( 2 )
                #hhh.SetBit(TH1.kNoTitle)
                if not isdata :
                    hhh.SetFillStyle( 1001 )
                else:
                    hhh.SetStats(0)

                ret[hist.Name][n] = hhh

        return ret
        
class Plotter:
    def __init__(self):
        TH1.SetDefaultSumw2(True)
        self.Samples = []
        self.Props = {}
        self.TreePlots = []

    def FindGRE(self, histname):
        #print "In Find method: %s" %histname
        found = False
        gre = True
        for i in range(0, len(self.TreePlots)):
            for j in range(0, len(self.TreePlots[i].ListOfHists)):
                #print "%s" %self.TreePlots[i].ListOfHists[j].Name
                if self.TreePlots[i].ListOfHists[j].Name == histname:
                    gre = self.TreePlots[i].GREs[j]
                    found = True
                    break;
            if(found):
                break
        return gre	        

    def AddTreePlots( self , selection ):
        self.TreePlots.append( selection )
        
    def AddSampleType(self , st):
        self.Samples.append(st)
              
    def AddLabels(self , hist , labels ):
        if labels :
            self.Props[hist].SetLabels(labels)

    def Rebin(self , hist , newbins):
        self.Props[hist].Rebin( newbins )
                        
    def GetData(self, propname):
        for st in self.Samples:
            if st.IsData():
                return st.AllHists[propname]
        return None

    def LoadHistos(self  , lumi , dirName = "tHq" , cftName = "CutFlowTable"):
        for st in self.Samples :
            print ("%sCreating histos for : %s%s" % (bcolors.OKGREEN , st.Name , bcolors.ENDC))
            st.LoadHistos( lumi , dirName , cftName , self.TreePlots )
            for prop in st.AllHists:
                if not prop in self.Props:
                    self.Props[prop] = Property( prop , OrderedDict() , None, None , [] )
                append = []
                for s in st.Samples:
                    if prop in s.AllHists:
                        append.append( s.AllHists[prop][0] )
                    else:
                        print ("prop %s doesn't exist in %s!" % (prop , s.Name ))
                self.Props[prop].Samples += append #[ s.AllHists[prop][0] for s in st.Samples ]
                if st.IsData():
                    self.Props[prop].Data = st.AllHists[prop]
                elif st.IsSignal:
                    self.Props[prop].Signal = st.AllOtherHists[prop].values()
                else :
                    self.Props[prop].Bkg[st.Name] = st.AllHists[prop]

    def DrawAll(self , normtodata ):
        gStyle.SetOptTitle(0)
        for prop in self.Props :
            self.Props[prop].Draw(normtodata)

    def GetProperty(self , propname):
        return self.Props[propname]

    def CalcSignificances(self, method=1):
        print ("Significance calculation with method %d"%method)
        if method > 4:
            print ("Illigal method!")
            return
        for prop in self.Props:
            self.Props[prop].SetSignificances(method)    
    		
    def CalcExpLimits(self):
        print ("Limit calculation")
        for prop in self.Props:
            self.Props[prop].SetExpectedLimits()
    
    def Write(self, fout , normtodata ):
        print ("%sStarted writing the plots to the output file (%s)...%s" % (bcolors.BOLD, fout.GetPath() , bcolors.ENDC))
        for propname in self.Props :
            propdir = None
            for selection in self.TreePlots:
                for t in selection.ListOfHists:
                    if t.Name == propname :
                        seldirname = selection.Name
                        seldir = fout.GetDirectory(seldirname)
                        if not seldir:
                            seldir = fout.mkdir( seldirname )
                        subdir = seldir
                        if t.DirName and not seldir.GetDirectory(t.DirName) :
                            subdir = seldir.mkdir( t.DirName )
                        elif t.DirName :
                            subdir = seldir.GetDirectory(t.DirName)
                        propdirname = propname
                        if len(propname.split("_")) > 1 :
                            propdirname = propname.split("_")[-1]
                        propdir = subdir.GetDirectory( propdirname )
                        if not propdir :
                            propdir = subdir.mkdir( propdirname )
            if not propdir :
                propdir = fout.mkdir( propname )
            self.Props[propname].Write(propdir, normtodata)
            fout.cd()

#!/usr/bin/env python

from Haamm.HaNaMiniAnalyzer.ExtendedSample import *
from ROOT import TSystem, gSystem, gROOT, TCanvas, TH1D, TDirectory, gDirectory, TFile, TH1, TH2D, TGraph, kRed
import sys
import array
import os

class PUWeightInfo:
    def __init__(self, method , runEra , xsec , hweight):
        self.Method = method
        self.RunEra = runEra
        self.XSec = xsec
        self.Histo = hweight.Clone( "W_%s_%s_%s"%(method,runEra,xsec) )
        self.nBins = self.Histo.GetNbinsX()
        self.Min = self.Histo.GetBinLowEdge(1)
        self.Max = self.Histo.GetBinLowEdge( 1+self.nBins )

    def ReWeight(self, var ):
        gROOT.cd()
        hW2D = TH2D("htemp" , "" , var.nBins , var.Min , var.Max , self.nBins , self.Min , self.Max )
        for nInt in range(1 , self.nBins+1):
            w_nInt = self.Histo.GetBinContent( nInt )
            for var_bin in range( 1, var.nBins+1 ):
                hW2D.SetBinContent( var_bin , nInt , w_nInt )

        hW2D.Multiply( var.MC )
        setattr( self, var.Name , hW2D.ProjectionX( "%s_%s_%s_%s"%(var.Name , self.Method,self.RunEra,self.XSec) ) )
        del hW2D

        return getattr( self, var.Name )
        
class Variable:
    def __init__(self, method , runEra , data , mc , name , title , nBins , min_ , max_):
        self.nBins = nBins
        self.Min = min_
        self.Max = max_
        self.Name = name
        self.Method = method
        self.RunEra = runEra
        gROOT.cd()
        self.Data = data.MakeHisto( runEra , name , title , nBins , min_ , max_ )
        self.MC = mc.MakeHisto( name , title , nBins , min_ , max_ )
        self.MCHistos = {}
        for i in mc.DataFiles :
            if mc.DataFiles[i].Method == self.Method and mc.DataFiles[i].RunEra == self.RunEra :
                self.MCHistos[ mc.DataFiles[i].XSec ] = mc.DataFiles[i].ReWeight( self )

    def Write(self, fout):
        fout.mkdir( "%s/%s" % (  self.Method , self.RunEra ) )
        fout.cd( "%s/%s" % ( self.Method , self.RunEra ) )
        self.Data.Write()
        self.MC.Write()
        self.KTestGraph = TGraph( len(self.MCHistos) )
        self.KTestGraph.SetName("KTestGraph")

        self.Chi2TestGraph = TGraph( len(self.MCHistos) )
        self.Chi2TestGraph.SetName("Chi2TestGraph")

        counter = 0
        self.XSectionMinChi2 = [ 0 , -1 ]
        self.XSectionMinKTest = [ 0 , -1 ]
        for xsec in sorted( self.MCHistos.keys() ):
            #self.MCHistos[ xsec ].Scale( self.Data.Integral() / self.MCHistos[ xsec ].Integral() )
            self.MCHistos[xsec].Write()

            ktestval = self.Data.KolmogorovTest( self.MCHistos[ xsec ] , "M" )
            if self.XSectionMinKTest[1] < 0 or ktestval < self.XSectionMinKTest[1] : self.XSectionMinKTest = [ xsec , ktestval ]
            self.KTestGraph.SetPoint( counter ,  xsec , ktestval )
		
            chi2testval = self.Data.Chi2Test( self.MCHistos[ xsec ] , "UW CHI2/NDF" )
            if self.XSectionMinChi2[1] < 0 or chi2testval < self.XSectionMinChi2[1] : self.XSectionMinChi2 = [ xsec , chi2testval ]
            self.Chi2TestGraph.SetPoint( counter , xsec ,  chi2testval )

            print counter, xsec , ktestval , chi2testval
            counter += 1
        cChi2 = TCanvas("Chi2")
        self.Chi2TestGraph.SetMarkerColor( kRed )
        self.Chi2TestGraph.SetMarkerStyle( 20 )
        self.Chi2TestGraph.Draw("AP")
        cChi2.Write()

        cKTest = TCanvas("KTest")
        self.KTestGraph.SetMarkerColor( kRed )
        self.KTestGraph.SetMarkerStyle( 20 )
        self.KTestGraph.Draw("AP")
        cKTest.Write()
        
        fout.cd()

class DatasetController :
    def __init__(self , path = "/eos/home-h/helfaham/PU_work/UL/2018/samples_hadd/" , fileName = "MinBias%s.root"):
        self.runEras = {} #"B":{},"C":{},"D":{},"E":{},"F":{},"G":{},"H":{}}
        self.nTuples = path
        self.All = TChain("PUAnalyzer/Trees/Events")
        #for runEra in ['A','B','C','D','E']: #self.runEras :
        for runEra in ['A','B']: #self.runEras :
            fname = path + fileName%(runEra)
            if os.path.isfile( fname ):
                self.runEras[ runEra ] = {}
            else:
                print "data file" , fname , "doesn't exist"
                continue
            self.runEras[runEra]["fname"] = fname
            self.runEras[runEra]["file"] = TFile.Open( self.runEras[runEra]["fname"]  )
            self.runEras[runEra]["tree"] = self.runEras[runEra]["file"].Get("PUAnalyzer/Trees/Events")
            self.All.Add( self.runEras[runEra]["fname"] )

            print fname , runEra , self.runEras[runEra]["tree"].GetEntries()
        print "All" , self.All.GetEntries()
        
    def MakeHisto(self, runEra , name , title , nBins , min_ , max_ ):
        attrname = "%s_%s" % (runEra , name )
        if hasattr( self , attrname  ):
            return getattr( self , attrname )

        gROOT.cd()
        tree = None
        if runEra == "All" :
            tree = self.All
        else :
            tree = self.runEras[ runEra[-1] ]["tree"]
        
        draw_ret = tree.Draw( "%s>>cloned_%s(%d, %.2g, %.2g)" % (name , attrname , nBins , min_ , max_) )

        if draw_ret < 0 :
            print tree.GetEntries()
            print name ,  "cloned_%s(%d, %.2g, %.2g)" % (attrname , nBins , min_ , max_)
        setattr( self , attrname , gDirectory.Get( "cloned_%s" % (attrname) ).Clone( attrname ) )
        return getattr( self , attrname )
        
class MCSampleContainer :
    def __init__(self, name , nTuples = "/eos/home-h/helfaham/PU_work/UL/2018/samples_hadd/" , runEras = []):
        self.nTuples=nTuples

        self.SampleName = name
        self.FileName = nTuples + self.SampleName + ".root"
        self.File = TFile.Open( self.FileName )
        self.hnTrueIntMCName = "PUAnalyzer/nTruInteractions/nTruInteractions_" + self.SampleName
        self.hnTrueInt = self.File.Get( self.hnTrueIntMCName )
        print self.File, self.hnTrueInt
        self.nIntNBins = self.hnTrueInt.GetNbinsX()
        self.nIntMin = self.hnTrueInt.GetBinLowEdge(1)
        self.nIntMax = self.hnTrueInt.GetBinLowEdge( 1+self.nIntNBins )
        self.Tree = self.File.Get("PUAnalyzer/Trees/Events")
        self.hnTrueInt.Scale( 1.0 / self.hnTrueInt.Integral() )

        xsec_variations =  range( 840 , 1170 )
        #print xsec_variations
        self.runEras = ["era%s"%era for era in runEras] #{"All","eraB","eraC","eraD","eraE","eraF","eraG","eraH"}
        self.runEras.append("All")
        datapumethods={"latest"} # "bestFit" , , "pcc"}

        self.DataFiles = {}
        for runEra in self.runEras:
            for method in datapumethods:
                fdata = None
                datafilename = nTuples + "../datapu_hadd/data_%s_%s.root" % (method, runEra)
                print datafilename
                if os.path.isfile( datafilename ):
                    fdata = TFile.Open( datafilename )
                else:
                    print datafilename, "doesn't exit"
                    continue
                for xsec in xsec_variations:
                    xsec_val = 69200.0*xsec/1000 
                    hdata = fdata.Get("h_" + str(xsec) )
                    if hdata == None :
                        print "Histo for ", runEra, " for xsec " , xsec_val , "doesn't exist in the file"
                        continue
                    hdata.Scale( 1.0 / hdata.Integral() )
                    hdata.Divide( self.hnTrueInt )
                    gROOT.cd()
                    self.DataFiles[ (method,runEra,xsec_val) ] = PUWeightInfo( method, runEra , xsec_val , hdata )
                fdata.Close()

    def MakeHisto( self, name , title , nBins , min_ , max_ ):
        attrname = "%s" % (name )
        if hasattr( self , attrname  ):
            return getattr( self , attrname )

        gROOT.cd()
        self.Tree.Draw( "nInt:%s>>cloned_%s(%d, %.2g, %.2g , %d , %.2g, %.2g )" % (name , attrname , nBins , min_ , max_ , self.nIntNBins , self.nIntMin , self.nIntMax) )
        setattr( self , attrname , gDirectory.Get( "cloned_%s" % (attrname) ).Clone( attrname ) )
        return getattr( self , attrname )
        

class EraTuneHandler :
    def Make2DSummaryPlot(self , varName , ext):
        name = "hBestXSections_%s_%s" % (varName , ext)
        setattr( self, name , TH2D( name , "Best XSections (%s,%s);Era;Tune" % (ext, varName) , len(self.data.runEras)+1 , 0 , len(self.data.runEras)+1 , 4 , 0 , 4 ) )
        h = getattr( self, name)
        h.GetXaxis().SetBinLabel( 1 , "All")
        index = 2
        for runera in sorted( self.data.runEras.keys() ):
            h.GetXaxis().SetBinLabel( index , "era%s" % (runera) )
            index += 1
        index = 1
        for tune in self.Tunes : #[1,2,3,4]:
            h.GetYaxis().SetBinLabel( index , "TuneCP%d"%(tune) )
            index += 1
        return h
    
    def __init__(self, name , datafiles , mcfiles , fout , tunes = [1,2,3,4,5] ):
        self.Tunes = tunes 
        self.data = DatasetController(fileName = datafiles)
        self.Dir = fout.mkdir( name )
        self.Dir.cd()

        variables = { "nVertices" : ( "nVertices" , 65 , 0 , 65 ) ,
                      "nGoodVertices" : ("nGoodVertices", 54, 5 , 59) ,
                      "nEles" : ("nEles" , 5 , 0 , 5 ) ,
                      "nMus" : ("nMus" , 10 , 0 , 10),
                      "nChargedHadrons" : ("nChargedHadrons" , 2000 , 0 , 2000 ),
                      "nLostTracks": ("nLostTracks" , 55 , 0 , 55 ),
                      "nPhotons" : ("nPhotons" , 450 , 0 , 450 ),
                      "nNeutralHadrons" : ("nNeutralHadrons" , 160 , 0 , 160 ),
                      "fixedGridRhoAll" : ("fixedGridRhoAll" , 50 , 0 , 50 ),
                      "fixedGridRhoFastjetAll" : ("fixedGridRhoFastjetAll" , 45 , 0 , 45 ),
                      "fixedGridRhoFastjetAllCalo" : ("fixedGridRhoFastjetAllCalo" , 40 , 0 , 40 ),
                      "fixedGridRhoFastjetCentral" : ("fixedGridRhoFastjetCentral" , 50 , 0 , 50 ),
                      "fixedGridRhoFastjetCentralCalo" : ("fixedGridRhoFastjetCentralCalo" , 25 , 0 , 25 ),
                      "fixedGridRhoFastjetCentralChargedPileUp" : ("fixedGridRhoFastjetCentralChargedPileUp" , 35 , 0 , 35 ),
                      "fixedGridRhoFastjetCentralNeutral" : ("fixedGridRhoFastjetCentralNeutral" , 12 , 0 , 12 ) 
}
        bestXsecPlots = {}

        for var in variables:
            varDir = self.Dir.mkdir( var )
            chi2bestxsec = self.Make2DSummaryPlot( var , "Chi2" )
            ktestbestxsec = self.Make2DSummaryPlot( var , "KTest")
            for tune in tunes : #[1,2,3,4]:
                tuneName = "TuneCP%d" % (tune)
                setattr( self, "MC_" + tuneName , MCSampleContainer( name=mcfiles % (tune) , runEras=self.data.runEras.keys() ) )
                mc = getattr( self, "MC_" + tuneName )
                tunedir = varDir.mkdir(tuneName )
                tunedir.cd()

                for runEra in sorted( mc.runEras ):
                    Var = Variable("latest" , runEra , self.data , mc , var , variables[var][0] , variables[var][1] , variables[var][2]  , variables[var][3] )
                    Var.Write( tunedir )

                    chi2bestxsec.Fill( runEra , tuneName , Var.XSectionMinChi2[0] )
                    ktestbestxsec.Fill( runEra , tuneName , Var.XSectionMinKTest[0] )
                
            varDir.cd()
            chi2bestxsec.Write()
            ktestbestxsec.Write()
        
fout = TFile.Open("out_2018_SingleNeutrinovsZeroBias.root" , "recreate")
EraTuneHandler( "SingleNuZeroBias" , "ZeroBias%s.root",  "SingleNeutrino_CP%d" , fout,[1,5] )
#EraTuneHandler( "DY" , "SingleMu%s.root",  "ZmuMuM%d" , fout )
#EraTuneHandler( "NuGunZeroBias" , "ZeroBias%s.root",  "NuGunM%d" , fout )
#EraTuneHandler( "NuGunMinBias" , "MinBias%s.root",  "NuGunM%d" , fout )
#EraTuneHandler( "SingleNuMinBias" , "MinBias%s.root",  "SingleNeutrinoType%d" , fout , [1,2] )

fout.Close()

exit()

from SamplesPU.Samples import *
for s in MINIAOD:
    if s.IsData: # not s.IsData: #not s.Name == "ttH"
        print "Skipping sample %s" % s.Name
        continue
    else:
        print s.Name

    es = ExtendedSample( s )
    es.LoadJobs( nTuples , "out%s.root" )
    es.LoadTree("PUAnalyzer/Trees/Events")

    vals_template = []
    leaves = ""
    for df in DataFiles:
        for oot in ["it"]:
            if not leaves == "" :
                leaves += ":"
            leaves += ("%s_%s" % (df, oot))
            vals_template.append( 0.0 )

    leafValues = array.array("f", vals_template )

    fNew = TFile( s.Name + "2.root" , "recreate" )
    es.Tree.GetEntry(0)
    friendT = es.Tree.GetTree().Clone(0) #TTree("friend", "friend")

    friendT.Branch( "PUWeights"  , leafValues , leaves)
    
    ccc = 0
    total=es.Tree.GetEntries()
    #for event in es.Tree:
    for i in range(0 , total):
        es.Tree.GetEntry(i)
        if (ccc % 1000) == 0 :
            print("\r%d out of %d (%.2f)"%(ccc , total , ccc*100./total )),
            sys.stdout.flush()
        nInt = es.Tree.GetLeaf("nInt").GetValue()
        #print nInt
        nInt50ns = es.Tree.GetLeaf("nInt50ns").GetValue()
        #print nInt, nInt50ns
        #print nInt
        #print nInt50ns
        counter = 0
        for df in DataFiles:
            wIn = 0.0
            wOut = 0.0
            if nInt >= 0:
                bin = DataFiles[df].FindBin( nInt )
                wIn = DataFiles[df].GetBinContent( bin )
                if nInt50ns >=0 :
                    wOut = wIn
                
            leafValues[counter] = wIn
            counter += 1
            # leafValues[counter] = wOut
            # counter += 1

        #print leafValues
        friendT.Fill()
        ccc += 1

    friendT.Write()
    fNew.Close()

from ROOT import TDirectory, TFile, TCanvas , TH1D , TH1 , THStack, TList, gROOT, TLegend, TPad, TLine, gStyle, TTree , TObject , gDirectory

import os
import sys
import Sample

from ExtendedSample import *

class SampleType:
    def __init__(self , name , color , samples = [] , LoadJobDir = "" , signal = False , additionalCut = None ):
        self.Name = name
        if type(color) is int:
            self.Color = color
            self.MultiPlot = False
            
        self.Samples = [ExtendedSample(s , additionalCut) for s in samples]
        if not LoadJobDir == "":
            Dirs = LoadJobDir.split(";")
            for ss in self.Samples:
                ss.LoadJobs( LoadJobDir )
                print ([j.Output for j in ss.Jobs])
                if len(Dirs)==2 :
                    print ("    Parent Files : %s" % ( [j.Output for j in ss.ParentSample.Jobs] ))
                    
        if type(color) is dict: #{ index:(color,xsec,title) }
            self.MultiPlot = True
            self.Colors = color
            self.Color = color[ color.keys()[0] ][0]
            for s in self.Samples:
                s.XSections = {}
                for c in color:
                    s.XSections[c] = color[c][1]
            
        self.IsSignal = signal

    def IsData(self):
        if len(self.Samples) == 0 :
            return False
        return self.Samples[0].IsData

    def LoadHistos(self , lumi , dirName = "tHq" , cftName = "CutFlowTable" , treeHistos = []):
        self.AllHists = {}
        self.AllOtherHists = {}
        Indices = [0]
        if self.MultiPlot:
            Indices = self.Colors.keys()
        #print self.Name
        #print Indices
        for s in self.Samples :
            print ("\tSample %s is loading :" % (s.Name))
            if s.LoadHistos( dirName , cftName , [] , Indices ):
                if len(treeHistos):
                    s.DrawTreeHistos( treeHistos )
                s.NormalizeHistos( lumi )
                print ("\tAll Loaded and normalized, now they are being organized")
            for propname in s.AllHists:
                if not propname in self.AllOtherHists.keys():
                    self.AllOtherHists[propname] = {}
                if propname in self.AllHists.keys() :
                    #print propname
                    if self.AllHists[propname].GetNbinsX() != s.AllHists[propname][0].GetNbinsX() :
                        #self.AllHists[propname].Print("base")
                        #s.AllHists[propname][0].Print("base")
                        print ("\tHisto %s from sub-sample %s(%d,%.2f,%.2f) has different bins from the sample type %s(%d,%.2f,%.2f)"%(propname, s.Name , s.AllHists[propname][0].GetNbinsX() , s.AllHists[propname][0].GetXaxis().GetXmin() , s.AllHists[propname][0].GetXaxis().GetXmax() , self.Name , self.AllHists[propname].GetNbinsX() , self.AllHists[propname].GetXaxis().GetXmin() , self.AllHists[propname].GetXaxis().GetXmax() ))
                        continue
                    self.AllHists[propname].Add(s.AllHists[propname][0])
                    for i in Indices:
                        if not i == 0:
                            self.AllOtherHists[propname][i].Add(s.AllHists[propname][i])
                else :
                    gROOT.cd()
                    if len(s.AllHists[propname]) == 0:
                        print ("\t%s skipped" % propname)
                        continue
                    for i in Indices:
                        hnew = None
                        color = self.Color
                        if i==0:
                            hnew = s.AllHists[propname][0].Clone("%s_%s" % ( propname , self.Name ) )
                            #hnew.SetTitle( self.Name )
                        else:
                            hnew = s.AllHists[propname][i].Clone("%s_%s_%d" % ( propname , self.Name , i) )
                            color = self.Colors[i][0]
                            hnew.SetTitle( self.Colors[i][2] )

                        #hnew.SetBit(TH1.kNoTitle) 
                        setattr( self , "%s_%d" % (propname,i) , hnew )
                        hhh = getattr( self , "%s_%d" % (propname,i) )
                        if self.IsSignal:
                            hhh.SetLineColor( color )
                            hhh.SetLineWidth( 3 )
                            hhh.SetLineStyle( 1 )
                            hhh.SetFillColor(0)
                            hhh.SetFillStyle(0)
                        else:
                            hhh.SetLineColor( 1 )
                            hhh.SetLineWidth( 2 )
                            hhh.SetLineStyle( 1 )
                            if not self.IsData() :
                                hhh.SetFillColor( color )
                                hhh.SetLineColor( color )
                                hhh.SetFillStyle( 1001 )
                                hhh.SetLineWidth( 2 )
                                hhh.SetLineStyle( 2 )
                            else:
                                hhh.SetStats(0)

                        if i==0:
                            self.AllHists[propname] = hhh
                        
                        self.AllOtherHists[propname][i] = hhh
                        print ("\t%s[%d] is created for %s : (%d, %.2f, %.2f)" % (propname , i , self.Name , hhh.GetXaxis().GetNbins() , hhh.GetXaxis().GetBinLowEdge(1) , hhh.GetXaxis().GetBinLowEdge( hhh.GetXaxis().GetNbins() ) + hhh.GetXaxis().GetBinWidth( hhh.GetXaxis().GetNbins() ) ))

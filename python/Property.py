from ROOT import TDirectory, TFile, TCanvas , TH1D , TH1 , THStack, TList, gROOT, TLegend, TPad, TLine, gStyle, TTree , TObject , gDirectory, gPad, TLimit, Double, TLimitDataSource, TString, TObject,  TLatex, TH2D , TH2 #TRatioPlot
from ROOT import RooFit,RooDataHist, RooHistPdf,RooAddPdf,RooFitResult, RooRealVar, RooArgSet, RooArgList

from math import sqrt, log
import os
import sys
import Sample
from array import array
import string
from collections import OrderedDict
 
class Property:
    @staticmethod
    def FromDir( dir , GRE = True ):
        name = dir.GetName()
        ret = Property( name , OrderedDict() , None , [] , [] , GRE )
        
        cats_dir = dir.GetDirectory("cats")
        for cat_ in cats_dir.GetListOfKeys() :
            cat = cat_.GetName()
            if cat.endswith("_Data"):
                gROOT.cd()
                ret.Data = cats_dir.Get( cat ).Clone()
            elif cat != "SumMC" :
                gROOT.cd()
                ret.Bkg[cat.split("_")[-1]] =  cats_dir.Get( cat ).Clone()

        sigs_dir = dir.GetDirectory("signals")
        for sig_ in sigs_dir.GetListOfKeys() :
            sig = sig_.GetName()
            gROOT.cd()
            ret.Signal.append( sigs_dir.Get(sig).Clone() )

        samples_dir = dir.GetDirectory("samples")
        for sam_ in samples_dir.GetListOfKeys() :
            sam = sam_.GetName()
            gROOT.cd()
            ret.Samples.append( samples_dir.Get(sam).Clone() )
            
        return ret
    
    def __init__(self , name , bkg_hists , data_hist , signal_hists , sample_hists, GRE = True):
        self.Name = nam
        self.Bkg = bkg_hists
        self.Data = data_hist
        self.Signal = signal_hists
        self.Samples = sample_hists
        self.greater = GRE
        self.isSoB = False
        self.isSoSqrtB = False
        self.isSoSqrtBdB2 = False
        self.isLnSoSqrtSB = False
        self.isLnSoSqrtSBdB = False
        self.SigSignificance = []
        self.AdditionalInfo = []
                
    def is2D(self):
        if self.Data :
            if "th2" in self.Data.ClassName().lower():
                return True
            else :
                return False
        else :
            raise RunTimeError( "Data hist of property %s is not set, so it is not clear if it is 2d or 1d" % (self.Name) )
        
    @staticmethod
    def AddOFUF(h):
        UF = h.GetBinContent(0)
        UF_E = h.GetBinError(0)

        b1 = h.GetBinContent(1)
        b1_e = h.GetBinError(1)

        h.SetBinContent( 1 , UF+b1 )
        h.SetBinError( 1 , sqrt( UF_E*UF_E + b1_e*b1_e ) )

        h.SetBinContent( 0 , 0.0 )
        h.SetBinError( 0 , 0.0 )
        
        lastBin = h.GetNbinsX()
        OF = h.GetBinContent(lastBin+1)
        OF_E = h.GetBinError(lastBin+1)

        bL = h.GetBinContent(lastBin)
        bL_e = h.GetBinError(lastBin)
        
        h.SetBinContent( lastBin , OF+bL )
        h.SetBinError( lastBin , sqrt( OF_E*OF_E + bL_e*bL_e ) )
        
        h.SetBinContent( lastBin+1 , 0.0 )
        h.SetBinError( lastBin+1 , 0.0 )
        
    def AddOF_UF_Bins(self):
        Property.AddOFUF( self.Data )
        for s in self.Signal:
            Property.AddOFUF(s)
        for s in self.Bkg:
            Property.AddOFUF(self.Bkg[s])
        for s in self.Samples:
            Property.AddOFUF(s)
    
            
    def GetBkgFromCR(self, CRProp , Bkgs , replacement , yieldsMethod=1) :
        """ 
        extract the shape of bkg from CRProp using data minus all Bkgs
        for the normalization in SR (which is the current property) several methods are foreseen :
        yieldsMethod = 1 : sum of the integral of Bkgs in CR (so taken from the simulation and cross section of backgrounds, trusted in signal region)
        yieldsMethod = 2 : data minus other MC's except Bkgs
        yieldsMethod = 3 : template fit

        replacement is a list with this format : [ NewName , NewColor ]
        """

        notInBkg = [item for item in self.Bkg if item not in Bkgs]
        template = CRProp.SubtractDataMC( notInBkg , self.Name )
        if template.Integral() == 0:
            return -1
        nMCBkgsSR = 0
        nDataMinusBkgsSR = self.Data.Integral()
        for bkg in Bkgs:
            nMCBkgsSR += self.Bkg.pop(bkg).Integral()
        for bkg in self.Bkg:
            nDataMinusBkgsSR -= self.Bkg[bkg].Integral()


        nNormalization = 0
        if yieldsMethod == 1:
            nNormalization = nMCBkgsSR
        elif yieldsMethod == 2:
            nNormalization = nDataMinusBkgsSR
        elif yieldsMethod == 3:
            nFit = 1.0
            var = RooRealVar( self.Name, self.Name , self.Data.GetXaxis().GetXmin() , self.Data.GetXaxis().GetXmax() )
            templatehist = RooDataHist( "%s_bkg_templateHist" %(self.Name) , self.Name , RooArgList(var) , template)
            templatepdf = RooHistPdf("%s_bkg_templatePDF" %(self.Name), self.Name , RooArgSet(var) ,templatehist);

            SumNonBkg = self.Data.Clone( "sum_%s_%s_th1" % (self.Name , "_".join(notInBkg) ) )
            SumNonBkg.Reset()
            for bkg in notInBkg:
                SumNonBkg.Add( self.Bkg[bkg] )
            SumNonBkgHist = RooDataHist( "sum_%s_%s_Hist" % (self.Name , "_".join(notInBkg) ),
                                         self.Name , RooArgList(var) , SumNonBkg )
            SumNonBkgpdf = RooHistPdf( "sum_%s_%s_PDF" % (self.Name , "_".join(notInBkg) ),
                                       self.Name , RooArgSet(var) , SumNonBkgHist )

            DataHist = RooDataHist( "data_%s_Hist" % (self.Name) ,
                                    self.Name , RooArgList(var) , self.Data )

            
            nBkgs = None
            if nDataMinusBkgsSR > 0 :
                nBkgs = RooRealVar("nBkgs","NBkgs", nDataMinusBkgsSR , 0.5*nDataMinusBkgsSR , 2*nDataMinusBkgsSR)
            elif nDataMinusBkgsSR < 0:
                nBkgs = RooRealVar("nBkgs","NBkgs", nDataMinusBkgsSR , 2*nDataMinusBkgsSR , -2*nDataMinusBkgsSR)
            else:
                nBkgs = RooRealVar("nBkgs","NBkgs", nDataMinusBkgsSR , -10 , 10 )
            nFixed = RooRealVar("nFixed","NFIXED", SumNonBkg.Integral() , SumNonBkg.Integral() , SumNonBkg.Integral() )
            model = RooAddPdf("model","model",RooArgList(SumNonBkgpdf,templatepdf),RooArgList(nFixed , nBkgs ) )
            res = model.fitTo( DataHist , RooFit.Extended( True ) , RooFit.Save(True) , RooFit.SumW2Error(True) )
            nNormalization = nBkgs.getVal()

        template.Scale( nNormalization/template.Integral() )
        template.SetLineWidth(2)
        template.SetLineColor(1)
        template.SetFillColor( replacement[1] )
        template.SetFillStyle( 1001 )
        self.Bkg[ replacement[0] ] = template

        return nNormalization
    
    def Rebin(self , newbins):
        bins = sorted(newbins)
        runArray = array('d',bins)
        self.Data = self.Data.Rebin( len(newbins)-1 , self.Data.GetName() + "_rebined" , runArray )
        if self.Signal:
            for i in range(0 , len(self.Signal) ):
                self.Signal[i] = self.Signal[i].Rebin( len(newbins)-1 , self.Signal[i].GetName() + "_rebined" , runArray )
        for bkg in self.Bkg:
            self.Bkg[bkg] = self.Bkg[bkg].Rebin( len(newbins)-1 , self.Bkg[bkg].GetName() + "_rebined" , runArray )
        
    @staticmethod
    def addLabels(histo , labels):
        if not histo:
            return
        for i in range(1, histo.GetNbinsX()+1 ):
            if not i > len(labels) :
                histo.GetXaxis().SetBinLabel( i , labels[i-1] )

    def SetLabels(self , labels):
        Property.addLabels( self.Data , labels )
        for s in self.Signal:
            Property.addLabels( s , labels )
        for bkg in self.Bkg:
            Property.addLabels( self.Bkg[bkg] , labels )
        for smpl in self.Samples:
            Property.addLabels( smpl , labels )
        
    def Clone(self , newname , allsamples = False):
        ret = Property( newname , {} , None , None , [] )
        ret.Data = self.Data.Clone( string.replace( self.Data.GetName() , self.Name , newname ) )
        if self.Signal :
            ret.Signal = []
            for i in range(0 , len(self.Signal) ):
                ret.Signal.append( self.Signal[i].Clone( string.replace( self.Signal[i].GetName() , self.Name , newname ) ) )
        for bkg in self.Bkg:
            ret.Bkg[bkg] = self.Bkg[bkg].Clone( string.replace( self.Bkg[bkg].GetName() , self.Name , newname ) )
        if allsamples:
            ret.Samples = [ h.Clone( string.replace( h.GetName() , self.Name , newname ) ) for h in self.Samples ]

        return ret
        
    def SubtractDataMC( self , tosubtract , appendix = "" ):
        tokeep = [item for item in self.Bkg if item not in tosubtract]
        ret = self.Data.Clone( "%s_%s_template_%s" % ( self.Name , "_".join(tokeep) , appendix ) )
        for bkg in tosubtract:
            ret.Add( self.Bkg[bkg] , -1 )
        return ret
        
    def GetStack(self, normtodata = False):
        if not hasattr(self , "Stack"):
            stackname = "%s_stack" % (self.Name)
            scale = 1.0
            if normtodata:
                totalmc = 0.
                for st in self.Bkg:
                    totalmc += self.Bkg[st].Integral()
                if totalmc > 0.000001 and self.Data.Integral() != 0 :
                    scale = self.Data.Integral()/totalmc
                else :
                    print ("\t%s was not normalized to data as the mc yield is %.2f and data yield is %d" % (self.Name , totalmc , int(self.Data.Integral()) ))
            #print "in getStack, normtodata = %s and scale is %f" % (str(normtodata) , scale)
            self.Stack = THStack( stackname , self.Name ) 
            for st in self.Bkg:
                if normtodata:
                    self.Bkg[st].Scale( scale )
                self.Stack.Add( self.Bkg[st] )

        return self.Stack

    def CompareNormalizedDists(self , name = "", drawdata = False , signals = None, bkgs = None , option = "" ):
        if not signals :
            signals = range(0, len(self.Signal) )
        if not bkgs :
            bkgs = self.Bkg.keys()
        canvasname = "%s_normalized_canvas_%s" % (self.Name , name)
        if hasattr(self , canvasname):
            raise RunTimeError( "Normalized canvas with name %s has already been drawn" % (canvasname) )
        if len(bkgs)+len(signals)+drawdata < 2 :
            raise RunTimeError( "To draw normalized data, at least two components are needed : data=%s, sig=%s , bkg=%s" % ( drawdata , signals, bkgs) )
        setattr( self, canvasname , TCanvas( canvasname) )
        canvas = getattr( self, canvasname )
        canvas.cd()

        if drawdata:
            self.Data.DrawNormalized( option )
            option += " same"
        for sig in signals:
            self.Signal[sig].DrawNormalized(option)
            if not "same" in option :
                option += " same"
        for bkg in bkgs:
            self.Bkg[bkg].DrawNormalized(option)
            if not "same" in option :
                option += " same"
        canvas.BuildLegend()
        self.AdditionalInfo.append( canvas )
        return canvas
        
    def GetSignalCanvas(self):
        canvasname = "%s_signal_canvas" % (self.Name)
        if not hasattr(self , "SignalCanvas" ):
            self.SignalCanvas = TCanvas(canvasname)

            if self.Signal:
                for s in self.Signal:
                    s.DrawNormalized("E SAME HIST")
                self.GetSLegend().Draw()
        return self.SignalCanvas
    
    def GetCanvas(self, padid , padOrCanvas=0):
        canvasname = "%s_canvas" % (self.Name)
        pad1name = "%s_pad1" % (self.Name)
        pad2name = "%s_pad2" % (self.Name)
        if not hasattr(self , "Canvas"):
            #print canvasname
            if padOrCanvas == 0:
                if self.is2D():
                    self.Canvas = TCanvas( canvasname , "" , 1000 , 1000 )
                    self.Canvas.cd()
                    return self.Canvas
                else:
                    self.Canvas = TCanvas( canvasname )
            elif padOrCanvas==1:
                self.Canvas = gPad
            elif padOrCanvas ==2:
                self.Canvas = TCanvas(canvasname)
                return
            
            self.Canvas.cd()
                
            self.Pad1 =  TPad(pad1name ,pad1name,0,0.25,1,1)
            self.Pad1.SetBottomMargin(0.1)
            self.Pad1.Draw()

            self.Canvas.cd()

            self.Pad2 = TPad( pad2name,pad2name,0,0,1,0.24)
            self.Pad2.SetTopMargin(0.1)
            self.Pad2.SetBottomMargin(0.1)
            self.Pad2.Draw()

        if self.is2D() or padOrCanvas==2:
            self.Canvas.cd()
            return self.Canvas
            
        if padid == 0:
            self.Canvas.cd()
        elif padid == 1:
            self.Pad1.cd()
        if padid == 2:
            self.Pad2.cd()

        return self.Canvas


    def GetLegend(self):
        legendname = "%s_legend" % (self.Name)
        if not hasattr(self , "Legend"):
            self.Legend = TLegend(0.9,0.5,1.,0.89,"","brNDC") 
            self.Legend.SetName( legendname )
            self.Legend.AddEntry( self.Data , "Data" , "lp" )
            for st in reversed( self.Bkg.keys() ):
                self.Legend.AddEntry( self.Bkg[st] , st , "f" )
            self.Legend.SetBorderSize(0)
            self.Legend.SetFillStyle(0)
        return self.Legend

    def GetSLegend(self):
        legendname = "%s_Slegend" % (self.Name)
        if not hasattr(self , "SLegend"):
            self.SLegend = TLegend(0.9,0.4,1.,0.49,"","brNDC") 
            self.SLegend.SetName( legendname )
            for st in self.Signal:
                self.SLegend.AddEntry( st , st.GetTitle() , "l" )
            self.SLegend.SetBorderSize(0)
            self.SLegend.SetFillStyle(0)
        return self.SLegend
    

    def GetRatioPlot(self):
        rationame = "%s_Ratio" % (self.Name)
        if not hasattr(self, "Ratio"):
            self.Ratio = self.Data.Clone( rationame )
            self.Ratio.SetBit(TH1.kNoTitle) 
            self.Ratio.SetStats(0)
            self.Ratio.Divide( self.GetStack().GetStack().Last() )
            for i in range(1 , self.Data.GetNbinsX()+1 ):
                self.Ratio.GetXaxis().SetBinLabel(i , "")
            self.Ratio.SetMarkerStyle(20)
            self.Ratio.GetXaxis().SetLabelSize( 0.)
            self.Ratio.GetXaxis().SetTitle("")
            self.Ratio.GetYaxis().SetRangeUser(0,3)
            self.Ratio.GetYaxis().SetTitle("Data / MC")
            self.Ratio.GetXaxis().SetTitleSize(0.2) 
            self.Ratio.GetXaxis().SetTitleOffset(0.25)
            self.Ratio.GetXaxis().SetTickLength(0.09)
            self.Ratio.GetYaxis().SetLabelSize(0.1)
            self.Ratio.GetYaxis().SetTitleSize(0.18)
            self.Ratio.GetYaxis().SetNdivisions(509)
            self.Ratio.GetYaxis().SetTitleOffset(0.25)
            self.Ratio.SetFillStyle(3001)
        return self.Ratio

    def GetRatioUnc(self):
        rationame = "%s_RatioUncert" % (self.Name)
        if not hasattr(self, "RatioUncert"):
            mc = self.GetStack().GetStack().Last()
            self.RatioUncert = mc.Clone( rationame )
            self.RatioUncert.SetBit(TH1.kNoTitle) 
            self.RatioUncert.SetStats(0)
            self.RatioUncert.Divide(mc)
            for i in range(1 , self.Data.GetNbinsX()+1 ):
                self.RatioUncert.GetXaxis().SetBinLabel(i , "")
            #self.RatioUncert.SetMarkerStyle(20)
            self.RatioUncert.GetYaxis().SetRangeUser(0,2)
            #self.RatioUncert.GetXaxis().SetLabelSize( 0.)
            self.RatioUncert.GetYaxis().SetTitle("Data / MC")
            self.RatioUncert.GetXaxis().SetTitleSize(0.2) 
            self.RatioUncert.GetXaxis().SetTitleOffset(0.25)
            self.RatioUncert.GetYaxis().SetLabelSize(0.1)
            self.RatioUncert.GetXaxis().SetTickLength(0.09)
            self.RatioUncert.GetYaxis().SetTitleSize(0.18)
            self.RatioUncert.GetYaxis().SetNdivisions(509)
            self.RatioUncert.GetYaxis().SetTitleOffset(0.25)
            self.RatioUncert.SetFillStyle(3001)
            self.RatioUncert.SetFillColor(1)
            self.RatioUncert.GetXaxis().SetTitle("")
            
        return self.RatioUncert


    def GetLineOne(self):
        linename = "%s_lineone" % (self.Name)
        if not hasattr(self, "LineOne"):
            self.LineOne = TLine(self.GetRatioPlot().GetXaxis().GetXmin(), 1.00, self.GetRatioPlot().GetXaxis().GetXmax(), 1.00)
            self.LineOne.SetLineWidth(2)
            self.LineOne.SetLineStyle(7)

        return self.LineOne

    def GetTitleBox(self):
        title = self.Samples[0].GetTitle()
        if not hasattr(self , "TitleBox"):
            self.TitleBox = TLatex()
            self.TitleBox.SetNDC()
            self.TitleBox.SetTextSize(0.06)
            self.TitleBox.DrawLatex(0.6,0.943,title)
        return self.TitleBox

    def Draw(self, normalizetodata = False , padOrCanvas = 0 ):
        istwo = self.is2D()
        optionData0 = "E"
        optionStack = "" if istwo else "HIST SAME"
        optionData1 = "E SAME" if istwo else "E SAME P"
        optionRatioPlot = "COLZ" if istwo else "ep same"
        gStyle.SetOptTitle(0)
        #self.AddOF_UF_Bins()
        self.GetCanvas(1, padOrCanvas)        
        if padOrCanvas == 2:
            #self.Ratio = TRatioPlot( self.GetStack(normalizetodata) ,
            #self.Data )
            self.Ratio.Draw()
            self.Ratio.GetLowerRefYaxis().SetTitle("ratio")
            self.Ratio.GetUpperRefYaxis().SetTitle("entries")
            self.Ratio.GetLowerRefXaxis().SetTitle( self.Name )
            self.GetLegend().Draw()
            return
        
        if not istwo:
            self.Data.Draw(optionData0)
        #if normalizetodata:
        #    print "Norm to data"
        self.GetStack(normalizetodata).Draw(optionStack)
        self.Data.Draw(optionData1)

        minY = 0.00001
        maxY = max( self.GetStack(normalizetodata).GetStack().Last().GetMaximum() , self.Data.GetMaximum() )*1.4
        self.Data.GetYaxis().SetRangeUser( minY , maxY )
        
        if istwo:
            return

        if self.Signal :
            for s in self.Signal:
                s.Draw("E SAME HIST")
            self.GetSLegend().Draw()
        self.GetLegend().Draw()
        self.GetTitleBox().Draw()
        self.GetCanvas(2)
        if not istwo :
            self.GetRatioUnc().Draw("E2")
        self.GetRatioPlot().Draw(optionRatioPlot)
        if not istwo :
            self.GetLineOne().Draw()

    def Write(self , propdir , normtodata , mkdir=False ):
        #print self.greater
        if mkdir:
            propdir = propdir.mkdir( self.Name )
        propdir.cd()
        catdir = propdir.mkdir( "cats" )
        catdir.cd()

        self.Data.GetXaxis().SetTitleSize(0.05) 
        self.Data.GetXaxis().SetTitleOffset(0.95)
        self.Data.GetYaxis().SetTitleSize(0.07)
        self.Data.GetYaxis().SetTitleOffset(0.72)
        
        self.Data.Write()
        for bkg in self.Bkg :
            self.Bkg[bkg].Write()
        self.GetStack(normtodata).GetStack().Last().Write("SumMC")

        if self.Signal :
            sigdir = propdir.mkdir( "signals" )
            sigdir.cd()
            for i in range(0 , len(self.Signal) ):
                self.Signal[i].Write()

        sampledir = propdir.mkdir( "samples" )
        sampledir.cd()
        for ss in self.Samples:
            ss.Write()

        additionaldir = propdir.mkdir("AdditionalInfo")
        additionaldir.cd()
        for add in self.AdditionalInfo:
            add.Write()

        if self.Data :
            self.Draw(normtodata)
            self.GetStack(normtodata).Write()
            self.GetLegend().Write()
            self.GetRatioPlot().Write()
                    
        propdir.cd()
        if self.Data is not None:
            self.Draw(normtodata)
            self.GetCanvas(0).Write()

        if hasattr(self, "SignalROC"):
            roc = propdir.mkdir( "ROCs" )
            roc.cd()
            self.DataROC.Write()
            self.BkgROC.Write()
            for iSig in range(0, len(self.SignalROC)):
                self.SignalROC[iSig].Write()
            propdir.cd()

        if hasattr(self, "SigSignificance"):	
            sigdir = propdir.mkdir( "Significances" )
            sigdir.cd()
            if self.isSoB:
                sob = sigdir.mkdir("SoB")
                sigdir.cd()
            if self.isSoSqrtB:
                sosqrtb = sigdir.mkdir("SoSqrtB")
                sigdir.cd()
            if self.isSoSqrtBdB2:
                sosqrtbdb2 = sigdir.mkdir("SoSqrtBdB2")
                sigdir.cd()
            if self.isLnSoSqrtSB:
                lnsosqrtb = sigdir.mkdir("LnSoSqrtSB")
                sigdir.cd()
            if self.isLnSoSqrtSBdB:
                lnsosqrtbdb = sigdir.mkdir("LnSoSqrtSBdB")
                sigdir.cd()				

            for iSig in range(0, len(self.SigSignificance)):
                if TString(self.SigSignificance[iSig].GetName()).Contains("_SoB"):
                    sob.cd()
                elif TString(self.SigSignificance[iSig].GetName()).Contains("_LnSoSqrtSBdB"):
                    lnsosqrtbdb.cd()
                elif TString(self.SigSignificance[iSig].GetName()).Contains("_LnSoSqrtSB"):
                    lnsosqrtb.cd()
                elif TString(self.SigSignificance[iSig].GetName()).Contains("_SoSqrtBdB2"):
                    sosqrtbdb2.cd()
                elif TString(self.SigSignificance[iSig].GetName()).Contains("_SoSqrtB"):
                    sosqrtb.cd()
                self.SigSignificance[iSig].Write()
                sigdir.cd()
            propdir.cd()

        if hasattr(self, "ExpLimits"):		
            expdir = propdir.mkdir( "ExpLimits" )
            expdir.cd()
            for iSig in range(0, len(self.ExpLimits)):
                self.ExpLimits[iSig].Write()
            propdir.cd()		
            


    def ROCMaker(self, inputHist):
        tmp = inputHist.Clone("ROC_%s" %inputHist.GetName())
        tmp.Sumw2()
        for iBin in range(0, inputHist.GetXaxis().GetNbins()):
            n = 0
            nError = Double(-1.)
            if self.greater:
                n = inputHist.IntegralAndError(iBin,-1,nError)
            else:
                n = inputHist.IntegralAndError(0, iBin, nError)
            tmp.SetBinContent(iBin, n)
            tmp.SetBinError(iBin, nError)
        return tmp

    def SetPropertyROCs(self):
        self.SignalROC = []
        for iSig in range(0, len(self.Signal)):
            self.SignalROC.append(self.ROCMaker(self.Signal[iSig]))
        self.BkgROC = self.ROCMaker(self.GetStack().GetStack().Last().Clone("AllBkgs") )
        self.DataROC = self.ROCMaker(self.Data)

    def Significance(self, signal, bkg, method=1):
        signame = "SoB"
        if method == 2:
            signame = "SoSqrtB"
        elif method == 3:
            signame = "SoSqrtBdB2"
        elif method == 4:
            signame = "LnSoSqrtSB"
        elif method == 5:
            signame = "LnSoSqrtSBdB"			
        elif method > 5:
            print ("Significance method not defined! Null histogram is returned!!!")
            return
        significance = signal.Clone("%s_%s" %(signal.GetName(),signame))
        significance.Sumw2(False)
        for iBin in range(0, signal.GetXaxis().GetNbins()):
            u = 0
            if bkg.GetBinContent(iBin) <= 0:
                u = -1.
                continue
            if method == 1:
                u = signal.GetBinContent(iBin) / bkg.GetBinContent(iBin)
            elif method == 2:
                u = signal.GetBinContent(iBin) / sqrt(bkg.GetBinContent(iBin))
            elif method == 3:
                u = signal.GetBinContent(iBin) / sqrt(bkg.GetBinContent(iBin) + (bkg.GetBinError(iBin)*bkg.GetBinError(iBin)))
            elif method == 4:
                u = sqrt(2)*sqrt((signal.GetBinContent(iBin)+bkg.GetBinContent(iBin))*log(1+(signal.GetBinContent(iBin)/bkg.GetBinContent(iBin))) - signal.GetBinContent(iBin))
            elif method == 5:
                s =  signal.GetBinContent(iBin) 
                b = bkg.GetBinContent(iBin)
                sigb =  bkg.GetBinError(iBin)
                ln1 = ((s+b)*(b+(sigb*sigb)))/((b*b)+((s+b)*sigb*sigb))
                ln2 = 1+ (sigb*sigb*s)/(b*(b+(sigb*sigb)))
                Sum = ((s+b)*ln1) - ((b*b/(sigb*sigb))*ln2)
                if Sum >= 0:
                    u = sqrt(2*Sum)
                    u = -1

            significance.SetBinContent(iBin, u)
        return significance

    def SetSignificances(self,method = 1):
        if not (hasattr(self,"BkgROC") and hasattr(self,"DataROC") and hasattr(self,"SignalROC")):
            self.SetPropertyROCs()
        if method == 1:
            self.isSoB = True
        elif method == 2:
            self.isSoSqrtB = True
        elif method == 3:
            self.isSoSqrtBdB2 = True
        elif method == 4:
            self.isLnSoSqrtSB = True
        elif method == 5:
            self.isLnSoSqrtSBdB = True		
        for iSig in range(0, len(self.Signal)):
            self.SigSignificance.append(self.Significance(self.SignalROC[iSig], self.BkgROC, method))

    def ExpectedLimits(self, signal, bkg_, data_):
        sig = TH1D(("sig_%s" %signal.GetName()),"sig",1,0,1)
        bkg = TH1D(("bkg_%s" %signal.GetName()),"bkg",1,0,1)
        data = TH1D(("data_%s" %signal.GetName()),"data",1,0,1)
        limits = signal.Clone("%s_ExpLimit" %signal.GetName())
        limits.Sumw2(False)
        for iBin in range(1, signal.GetXaxis().GetNbins()+1):
            sig.SetBinContent(1, signal.GetBinContent(iBin))
            sig.SetBinError(1, signal.GetBinError(iBin))
            bkg.SetBinContent(1, bkg_.GetBinContent(iBin))
            bkg.SetBinError(1, bkg_.GetBinError(iBin))
            data.SetBinContent(1, data_.GetBinContent(iBin))
            data.SetBinError(1, data_.GetBinError(iBin))
            mydatasource = TLimitDataSource(sig,bkg,data)
            myconfidence = TLimit.ComputeLimit(mydatasource,50000);
            limits.SetBinContent(iBin, myconfidence.GetExpectedCLs_b(0))
        del sig
        del bkg
        del data
        return limits

    def SetExpectedLimits(self):
        self.ExpLimits = []
        if not (hasattr(self,"BkgROC") and hasattr(self,"DataROC") and hasattr(self,"SignalROC")):
            self.SetPropertyROCs()
        for iSig in range(0, len(self.Signal)):
            self.ExpLimits.append(self.ExpectedLimits(self.SignalROC[iSig], self.BkgROC, self.BkgROC))


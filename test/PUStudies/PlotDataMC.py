from ROOT import TFile, TH1, TH1F, TF1, TCanvas, kRed, kBlack, kBlue, kGreen, TGraph, TGraphErrors , TGraphAsymmErrors, TMultiGraph, TAttMarker, TLatex, TStyle, Double, TH1D, TLegend, TLine, TString, gStyle, gROOT
import array
import math

t = TLatex()
t.SetTextAlign(32)
t.SetTextSize(0.035)
t.SetTextFont(72)



AllBestXSections = {}
fin = TFile.Open("/afs/cern.ch/user/h/helfaham/CMSSW_10_6_4_patch1/src/Haamm/HaNaMiniAnalyzer/test/PUStudies/out_2018_SingleNeutrinovsZeroBias.root")

TuneCP1_All=[]
TuneCP1_eraA=[]
TuneCP1_eraB=[]

TuneCP5_All=[]
TuneCP5_eraA=[]
TuneCP5_eraB=[]

objs = []
def PlotVariable( DirName , varName , MCName, runEra ):
    allHists = {}
    twoDHist = fin.Get( "%s/%s/hBestXSections_%s_Chi2" % ( DirName , varName  , varName ) )
    if twoDHist == None:
        print "failed"
        return
    mc_bin = twoDHist.GetYaxis().FindBin( MCName )
    data_bin = twoDHist.GetXaxis().FindBin( runEra )
    bestXSec = twoDHist.GetBinContent( data_bin , mc_bin )
    #print bestXSec
    if MCName   == "TuneCP1":
        if runEra       == "eraA":
            TuneCP1_eraA.append(bestXSec)
        elif runEra     == "eraB":
            TuneCP1_eraB.append(bestXSec)
        elif runEra     == "All":
            TuneCP1_All.append(bestXSec)
    elif MCName   == "TuneCP5":
        if runEra       == "eraA":
            TuneCP5_eraA.append(bestXSec)
        elif runEra     == "eraB":
            TuneCP5_eraB.append(bestXSec)
        elif runEra     == "All":
            TuneCP5_All.append(bestXSec)
    
    DataHistName = "%s/%s/%s/latest/%s/%s_%s" % ( DirName , varName , MCName , runEra , runEra , varName )
    MCHistName = "%s/%s/%s/latest/%s/%s_latest_%s" % ( DirName , varName , MCName , runEra , varName, runEra  )
    MCHistName += "_%.1f"

    cOut = TCanvas("DataMC")
    objs.append(cOut)
    
    dataHist = fin.Get( DataHistName )
    objs.append( dataHist )
    
    dataHist.SetLineColor( kBlack )
    dataHist.SetLineWidth( 1 )
    dataHist.SetTitle("Data;%s (%s)" % (varName,MCName)  )
    #dataHist.Rebin(8)
    allHists[dataHist.GetMaximum()/dataHist.GetEntries()] = dataHist
    gStyle.SetOptTitle(False)
    dataHist.SetStats(False)
    dataNorm = dataHist.DrawNormalized()
    #dataNorm = dataHist.DrawNormalized("E PLC PMC")
    for xsec in [ 0.0 + (ratio*69200./1000.) for ratio in range(840,1170) ][::-1]:
        if abs( xsec - bestXSec )/bestXSec > 0.1 or abs( xsec - bestXSec )/ bestXSec < 0.2: 
            if not xsec == bestXSec :
                #print xsec, "skipped"
                continue
        hName = MCHistName % (xsec)
        hMC = fin.Get( hName  )
        if not hMC == None:
            #hMC.Rebin(8)
            allHists[hMC.GetMaximum()/hMC.GetEntries()] = hMC
            gROOT.ForceStyle() 
            if xsec == bestXSec:
                hMC.SetTitle( "Best Cross Section (%s): %.1f" %(runEra, xsec) )
                hMC.SetLineColor(2)
                hMC.SetLineWidth(1)
            elif xsec > bestXSec :
                hMC.SetTitle( "Cross Section (%s) : %.1f" %(runEra, xsec) )
                hMC.SetLineColor(6)
                hMC.SetLineWidth(1)
            elif xsec < bestXSec :
                hMC.SetTitle( "Cross Section (%s) : %.1f" %(runEra, xsec) )
                hMC.SetLineColor(4)
                hMC.SetLineWidth(1)


            hMC.DrawNormalized("SAME")
            #hMC.DrawNormalized("SAME E PLC PMC")
            hMC.SetStats(False)
        else:
            print hName , "null"

    maxvals = allHists.keys()
    maxvals.sort(reverse=True)
    print varName, MCName, maxvals, bestXSec
    option = ""
    maX = maxvals[0]
    dataNorm.GetYaxis().SetRangeUser(0 , maX*1.2)
    # for m in maxvals :
    #     #print m
    #     allHists[m].SetStats(False)
    #     allHists[m].DrawNormalized(option)
    #     option = "SAME"

    #cOut.BuildLegend(0.1,0.7,0.48,0.9) #left
    cOut.BuildLegend(0.5,0.67,0.88,0.88) #right
    cOut.SaveAs("FitRes/new_test_plots/%s/%s_%s_%s.png" % (runEra, varName , MCName, runEra) )
    return cOut


#a = PlotVariable( "SingleNuZeroBias" , "nVertices" , "tuneM2" , "All" )                    
#exit()
def GaussFit(list_bestXSec):

    print "final list" + str(list_bestXSec)
    cOut1 = TCanvas("Fit")
    gStyle.SetOptFit(111) #Fit
    gStyle.SetOptTitle(0);
    hist_fit = TH1F("hist_fit","hist_fit",50,40000,100000)
    hist_fit.SetStats(True) #Fit
    Legend_fit = TLegend(0.25,0.79,0.45,0.95) #fit
    ar_mean= sum(list_bestXSec)/len(list_bestXSec)
    ar_mean_round=round(ar_mean)
    for i in range(len(list_bestXSec)):
        hist_fit.Fill(list_bestXSec[i])
    cOut1.cd()
    Fit = hist_fit.Fit("gaus") #Fit
    Legend_fit.AddEntry(hist_fit ,'{} {}'.format("ar. mean = ", ar_mean_round) ,"l")
    hist_fit.Draw()

    if list_bestXSec == TuneCP1_All:
        hist_fit.GetXaxis().SetTitle("BestFit Xsec[mb]_TuneCP1_All")
    elif list_bestXSec  == TuneCP1_eraA:
        hist_fit.GetXaxis().SetTitle("BestFit Xsec[mb]_TuneCP1_eraA")
    elif list_bestXSec  == TuneCP1_eraB:
        hist_fit.GetXaxis().SetTitle("BestFit Xsec[mb]_TuneCP1_eraB")

    elif list_bestXSec  == TuneCP5_All:
        hist_fit.GetXaxis().SetTitle("BestFit Xsec[mb]_TuneCP5_All")
    elif list_bestXSec  == TuneCP5_eraA:
        hist_fit.GetXaxis().SetTitle("BestFit Xsec[mb]_TuneCP5_eraA")
    elif list_bestXSec  == TuneCP5_eraB:
        hist_fit.GetXaxis().SetTitle("BestFit Xsec[mb]_TuneCP5_eraB")

    hist_fit.GetYaxis().SetTitle("Frequency")
    hist_fit.SetTitle("UL2018")
    Legend_fit.SetFillStyle(0)
    Legend_fit.SetLineColor( 0 )
    Legend_fit.Draw()

    if list_bestXSec == TuneCP1_All:
        cOut1.SaveAs("./gaussfits/gaussianfit_UL_2018_CP1_All_test.png")
    elif list_bestXSec == TuneCP5_All:
        cOut1.SaveAs("./gaussfits/gaussianfit_UL_2018_CP5_All_test.png")

    elif list_bestXSec == TuneCP1_eraA:
        cOut1.SaveAs("./gaussfits/gaussianfit_UL_2018_CP1_eraA_test.png")
    elif list_bestXSec == TuneCP1_eraB:
        cOut1.SaveAs("./gaussfits/gaussianfit_UL_2018_CP1_eraB_test.png")

    elif list_bestXSec == TuneCP5_eraA:
        cOut1.SaveAs("./gaussfits/gaussianfit_UL_2018_CP5_eraA_test.png")
    elif list_bestXSec == TuneCP5_eraB:
        cOut1.SaveAs("./gaussfits/gaussianfit_UL_2018_CP5_eraB_test.png")

    return cOut1


def CalcChi2( DirName , varName , MCName , runEra , xsec ):
    DataHistName = "%s/%s/%s/latest/%s/%s_%s" % ( DirName , varName , MCName , runEra , runEra , varName )
    MCHistName = "%s/%s/%s/latest/%s/%s_latest_%s_%.1f" % ( DirName , varName , MCName , runEra , varName, runEra , xsec )

    dataHist = fin.Get( DataHistName )

    MCHist = fin.Get( MCHistName )
    chi2 = dataHist.Chi2Test( MCHist , "UW CHI2/NDF" )
    return chi2
        


variables = { #"nVertices" : ( "nVertices" , 74 , 6 , 80 ) ,
              #"nGoodVertices" : ("nGoodVertices", 54, 5 , 59) ,
              #"nChargedHadrons" : ("nChargedHadrons" , 2000 , 0 , 2000 ),
              #"fixedGridRhoAll" : ("fixedGridRhoAll" , 60 , 0 , 60 ),
              #"fixedGridRhoFastjetAll" : ("fixedGridRhoFastjetAll" , 40 , 0 , 40 ),
              #"fixedGridRhoFastjetAllCalo" : ("fixedGridRhoFastjetAllCalo" , 25 , 0 , 25 ),
              #"fixedGridRhoFastjetCentral" : ("fixedGridRhoFastjetCentral" , 50 , 0 , 50 ),
              #"fixedGridRhoFastjetCentralCalo" : ("fixedGridRhoFastjetCentralCalo" , 20 , 0 , 20 ),
              #"fixedGridRhoFastjetCentralChargedPileUp" : ("fixedGridRhoFastjetCentralChargedPileUp" , 35 , 0 , 35 ),
              
              #"fixedGridRhoFastjetCentralNeutral" : ("fixedGridRhoFastjetCentralNeutral" , 12 , 0 , 12 ),
              #"nMus" : ("nMus" , 10 , 0 , 10 ),
              #"nEles" : ("nEles" , 10 , 0 , 10 ) ,
              #"nLostTracks": ("nLostTracks" , 35 , 0 , 35 ),
              #"nPhotons" : ("nPhotons" , 600 , 0 , 600 ),
              #"nNeutralHadrons" : ("nNeutralHadrons" , 120 , 0 , 120 )
}

varNames = ["nVertices",
            "nGoodVertices",
            "fixedGridRhoFastjetCentralChargedPileUp",
            "nChargedHadrons",
            "fixedGridRhoAll",
            "fixedGridRhoFastjetAll",
            "fixedGridRhoFastjetAllCalo",
            "fixedGridRhoFastjetCentral",
            "fixedGridRhoFastjetCentralCalo",
            "fixedGridRhoFastjetCentralNeutral",
            "nMus",
            "nEles",
            "nLostTracks",
            "nPhotons",
            "nNeutralHadrons"

]
for var in varNames :
    for tune in [ "TuneCP1", "TuneCP5" ] :
	for runEra in ["All", 'eraA', 'eraB' ]:
        	a = PlotVariable( "SingleNuZeroBias" , var ,tune, runEra )                    
for list_bestXSec in [TuneCP1_All, TuneCP1_eraA, TuneCP1_eraB, TuneCP5_All, TuneCP5_eraA, TuneCP5_eraB]:
        b = GaussFit(list_bestXSec)

#exit()
        
allGraphs = {}
allMultiGraphs = {}
canvases = {}

tunes = [  "TuneCP1", "TuneCP5" ]

for runEra in ["All",'eraA','eraB']:
    mg = TMultiGraph()
    mg.SetName( runEra )
    allMultiGraphs[ runEra ] = mg
    marker_info = {"TuneCP1":(20, 2 , 0   ) ,
                   "TuneCP5":(21, 8 , 0   ) ,
		}
    #Legend = TLegend( 0.7,0.8,0.88,0.88 )
    Legend = TLegend(0.25,0.79,0.45,0.95) #fit
    
    xCMS = array.array( 'd' , range(0, len(varNames) ) )
    xCMS[0] -= 0.2
    xCMS[-1] += 0.2
    yCMS = array.array( 'd' , [69200]*len(varNames) )
    xeCMS = array.array( 'd' , [0]*len(varNames) )
    yeCMS = array.array( 'd' ,  [0.046*69200]*len(varNames) )
    gCMS = TGraphErrors(len(varNames) , xCMS , yCMS , xeCMS , yeCMS )
    gCMS.SetFillStyle( 3005 )
    gCMS.SetFillColor( 9 )
    gCMS.SetMarkerColor( 11 )
    gCMS.SetMarkerStyle( 23 )
    gCMS.SetLineColor( gCMS.GetMarkerColor() )
    gCMS.SetTitle( "69200 #pm 4.6%" )
    allGraphs["CMS"] = gCMS
    mg.Add( gCMS , "p3" )
    Legend.AddEntry( gCMS , gCMS.GetTitle() , "lfp")

    gCMSLine = TGraph(len(varNames) , xCMS , yCMS )
    gCMSLine.SetLineColor( gCMS.GetMarkerColor() )
    mg.Add( gCMSLine , "l" )

    
    for MCName in tunes : 
        x = array.array( 'd' )
        y = array.array( 'd' )
        exl = array.array( 'd' )
        exh = array.array( 'd' )
        eyl = array.array( 'd' )
        eyh = array.array( 'd' )
        count = marker_info[ MCName ][2]
        new_vals = []
        for varName in varNames:
            vals = []
            for DirName in [ "SingleNuZeroBias" ] : #"DY" , "NuGunZeroBias" , "NuGunMinBias" ] :
                twoDHist = fin.Get( "%s/%s/hBestXSections_%s_Chi2" % ( DirName , varName  , varName ) )
                if twoDHist == None:
                    continue
                mc_bin = twoDHist.GetYaxis().FindBin( MCName )
                data_bin = twoDHist.GetXaxis().FindBin( runEra )
                bestXSec = twoDHist.GetBinContent( data_bin , mc_bin )
                AllBestXSections[ (varName , runEra , MCName , DirName) ] = bestXSec
                if bestXSec > 0. :
                    vals.append( bestXSec )
                    #vals.append( CalcChi2( DirName , varName , MCName , runEra , bestXSec ) )
            if bestXSec > 0.:
	       new_vals.append(bestXSec)
            print (" this is new vals " + str(new_vals))
            vals = [val for val in set( vals )]
            vals = sorted(vals)
            print (" this is vals " + str(vals))
            if len(vals) > 3 :
                central = 0
                errorUp = 0
                errorLow = 0
                for val in vals :
                    central += val
                central /= len(vals)
                for val in vals :
                    errorLow += (val-central)*(val-central)
                errorLow /= len(vals)
                errorLow = math.sqrt( errorLow )
                errorUp = errorLow
            elif len(vals) == 3 :
                central  = vals[1]
                errorUp  = vals[2] - vals[1]
                errorLow = vals[1] - vals[0]
            elif len(vals) == 2 :
                central = (vals[0] + vals[1]) / 2
                errorLow = abs(vals[0] - vals[1]) / 2
                errorUp = errorLow
            elif len(vals) == 1 :
                central = vals[0]
                errorLow = 0
                errorUp = 0
            x.append( count )
            y.append( central )
            exl.append( 0 )
            exh.append( 0 )
            eyl.append( errorLow )
            eyh.append( errorUp  )
            count += 1
    	mean_vals = sum(new_vals)/len(new_vals)
        mean_vals_r = round(mean_vals)
    	print ("is the arthimetic mean " + str(mean_vals)) 
        graph = TGraphAsymmErrors( len(x) , x , y , exl , exh , eyl , eyh )
        # Fit
        #gROOT.SetStyle("Plain")
        #gStyle.SetOptFit(111)
        #graph.SetTitle( MCName  )
        #graphFit = graph.Fit("gaus", "P")
        #myfunc = graph.GetFunction("gaus")
        #graphFitMean = myfunc.GetParameter(1)
        #print ("this is the fit mean " + str(graphFitMean))
        #valueFit = graph.Eval(graphFitMean)
        #valueFit_r = round(valueFit)
        #print valueFit
        # end Fit
        graph.SetTitle( MCName  )
        graph.SetName( runEra + "_" + MCName )
        graph.SetLineColor(  marker_info[ MCName ][1] )
        graph.SetLineStyle(  3 )
        graph.SetLineWidth( 1 )
        graph.SetFillColor( 0 )
        graph.SetFillStyle( 0 )
        graph.SetMarkerSize( 1.6 )
        graph.SetMarkerStyle( marker_info[ MCName ][0] )
        graph.SetMarkerColor( marker_info[ MCName ][1] )
        allGraphs[(runEra,MCName)] =  graph
        mg.Add( graph , "pl" )
        Legend.AddEntry( graph , graph.GetTitle() , "lp")
        #Legend.AddEntry( graph ,'{} {}'.format("ar. mean = ", mean_vals_r) ,"l")
        #Legend.AddEntry( graph ,'{} {}'.format("fit mean = ", valueFit_r) ,"l")
   
    canvas = TCanvas( runEra + "_AvgDataset" , runEra + "_AvgDataset" , 0 , 0 , 1335 , 5*200 )
    canvas.Range(-2.739156,63227.16,8.503012,75975.37)
    canvas.SetLeftMargin(0.168042)
    canvas.SetRightMargin(0.1470368)
    canvas.SetTopMargin(0.1314168)
    canvas.SetBottomMargin(0.187885)
    
    mg.Draw("AP SAME")

    Legend.SetFillStyle(0)
    Legend.SetLineColor( 0 )
    Legend.Draw()
    #canvases["text" + runEra] = t.DrawTextNDC( 0.2, 0.8 , runEra )
    canvases["Leg" + runEra] = Legend
    canvases[runEra] = canvas
    mg.GetHistogram().GetYaxis().SetTitle( "Best Fit XSection" )
    mg.GetHistogram().GetYaxis().SetTitleOffset(2)

    labels = varNames
    xax = mg.GetHistogram().GetXaxis()
    xax.SetNdivisions(len(varNames) )
    canvas.SetGridx(1)
    minXax = xax.GetBinLowEdge(1)
    maxXax = xax.GetBinUpEdge( xax.GetNbins() )
    xax.Set( len(labels) , minXax , maxXax )
    i = 1
    for lbl in labels:
        xax.SetBinLabel(i, lbl)
        i+=1

    canvas.SaveAs( canvas.GetName() + ".png" )

#TODO you exit here why?
exit()                

allGraphs_2 = {}
allMultiGraphs_2 = {}
canvases_2 = {}
for runEra in ["All", 'eraA','eraB','eraC']:
    mg = TMultiGraph()
    mg.SetName( runEra )
    allMultiGraphs_2[ runEra ] = mg
    marker_info = {#"DY":(20, 2 , 0   ) ,
                   #"NuGunMinBias":(22, 4 , 0.1) ,
                   #"NuGunZeroBias":(23, 6 , 0.2),
                   "SingleNuZeroBias" : (20,2,0) }
    Legend = TLegend( 0.8 , 0.7 , 1 , 1 )
    for DirName in [ "SingleNuZeroBias" ] : #["DY" , "NuGunZeroBias" , "NuGunMinBias" ] :
        x = array.array( 'd' )
        y = array.array( 'd' )
        exl = array.array( 'd' )
        exh = array.array( 'd' )
        eyl = array.array( 'd' )
        eyh = array.array( 'd' )
        count = marker_info[ DirName ][2]
        for varName in varNames:
            vals = []
            for MCName in tunes:
                twoDHist = fin.Get( "%s/%s/hBestXSections_%s_Chi2" % ( DirName , varName  , varName ) )
                if twoDHist == None:
                    continue
                mc_bin = twoDHist.GetYaxis().FindBin( MCName )
                data_bin = twoDHist.GetXaxis().FindBin( runEra )
                bestXSec = twoDHist.GetBinContent( data_bin , mc_bin )
                AllBestXSections[ (varName , runEra , MCName , DirName) ] = bestXSec
                if bestXSec > 0. :
                    vals.append( bestXSec )
                    #vals.append( CalcChi2( DirName , varName , MCName , runEra , bestXSec ) )
            vals = [val for val in set( vals )]
            vals = sorted(vals)
            if len(vals) > 3 :
                central = 0
                errorUp = 0
                errorLow = 0
                for val in vals :
                    central += val
                central /= len(vals)
                for val in vals :
                    errorLow += (val-central)*(val-central)
                errorLow /= len(vals)
                errorLow = math.sqrt( errorLow )
                errorUp = errorLow
            elif len(vals) == 3 :
                central  = vals[1]
                errorUp  = vals[2] - vals[1]
                errorLow = vals[1] - vals[0]
            elif len(vals) == 2 :
                central = (vals[0] + vals[1]) / 2
                errorLow = abs(vals[0] - vals[1]) / 2
                errorUp = errorLow
            elif len(vals) == 1 :
                central = vals[0]
                errorLow = 0
                errorUp = 0
            x.append( count )
            y.append( central )
            exl.append( 0 )
            exh.append( 0 )
            eyl.append( errorLow )
            eyh.append( errorUp  )
            count += 1
        graph = TGraphAsymmErrors( len(x) , x , y , exl , exh , eyl , eyh )
        graph.SetTitle( DirName )
        graph.SetName( runEra + "_" + DirName )
        graph.SetLineColor(  marker_info[ DirName ][1] )
        graph.SetLineWidth( 3 )
        graph.SetFillColor( 0 )
        graph.SetFillStyle( 0 )
        graph.SetMarkerStyle( marker_info[ DirName ][0] )
        graph.SetMarkerColor( marker_info[ DirName ][1] )
        allGraphs_2[(runEra,DirName)] =  graph
        mg.Add( graph , "p" )
        Legend.AddEntry( graph, graph.GetTitle() , "lp")
    canvas = TCanvas( runEra + "_AvgMC" , runEra  + "_AvgMC" , 0 , 0 , 5*167 , 5*200 )
    mg.Draw("AP")
    Legend.Draw()
    canvases_2["text" + runEra] = t.DrawTextNDC( 0.2, 0.8 , runEra )
    canvases_2["Leg" + runEra] = Legend
    canvases_2[runEra] = canvas
    mg.GetHistogram().GetYaxis().SetTitle( "Best Fit XSection #pm [MCTunes]" ) #Minimum #chi^{2}
    mg.GetHistogram().GetYaxis().SetTitleOffset(1.82)
    labels = varNames
    xax = mg.GetHistogram().GetXaxis()
    minXax = xax.GetBinLowEdge(1)
    maxXax = xax.GetBinUpEdge( xax.GetNbins() )
    xax.Set( len(labels) , minXax , maxXax )
    i = 1
    for lbl in labels:
        xax.SetBinLabel(i, lbl)
        i+=1
                
exit()
allGraphs_3 = {}
allMultiGraphs_3 = {}
canvases_3 = {}
for MCName in tunes [ "tuneM1"  "tuneM5" ]:
    #print MCName
    mg = TMultiGraph()
    mg.SetName( runEra )
    allMultiGraphs_3[ MCName ] = mg
    marker_info = {"All":(20, 1 , 0   ) ,
                   "eraG":(26, 8 , 0.1) ,
                   "eraH":(27, 2 , 0.2 ) ,
                   "eraD":(21, 3 , 0.3) ,
                   "eraE":(24, 6 , 0.4) ,
                   "eraF":(25, 7 , 0.5) ,
                   "eraC":(23, 46 , 0.6) ,
                   "eraB":(22, 4 , 0.7)  }

    Legend = TLegend( 0.8 , 0.7 , 1 , 1 )
    for runEra in ["All",'eraG','eraH','eraD','eraE','eraF' , 'eraC','eraB']:
        x = array.array( 'd' )
        y = array.array( 'd' )
        exl = array.array( 'd' )
        exh = array.array( 'd' )
        eyl = array.array( 'd' )
        eyh = array.array( 'd' )
        count = marker_info[ runEra ][2]
        for varName in varNames:
            vals = []
            for DirName in  [ "SingleNuZeroBias" ] : #["DY" , "NuGunZeroBias" , "NuGunMinBias" ] :
                twoDHist = fin.Get( "%s/%s/hBestXSections_%s_Chi2" % ( DirName , varName  , varName ) )
                if twoDHist == None:
                    continue
                mc_bin = twoDHist.GetYaxis().FindBin( MCName )
                data_bin = twoDHist.GetXaxis().FindBin( runEra )
                bestXSec = twoDHist.GetBinContent( data_bin , mc_bin )
                AllBestXSections[ (varName , runEra , MCName , DirName) ] = bestXSec
                if bestXSec > 0. :
                    vals.append( bestXSec )
                    #vals.append( CalcChi2( DirName , varName , MCName , runEra , bestXSec ) )
            vals = [val for val in set( vals )]
            vals = sorted(vals)
            #print varName, MCName, runEra , len(vals), vals
            if len(vals) > 3 :
                central = 0
                errorUp = 0
                errorLow = 0
                for val in vals :
                    central += val
                central /= len(vals)
                for val in vals :
                    errorLow += (val-central)*(val-central)
                errorLow /= len(vals)
                errorLow = math.sqrt( errorLow )
                errorUp = errorLow
            elif len(vals) == 3 :
                central  = vals[1]
                errorUp  = vals[2] - vals[1]
                errorLow = vals[1] - vals[0]
            elif len(vals) == 2 :
                central = (vals[0] + vals[1]) / 2
                errorLow = abs(vals[0] - vals[1]) / 2
                errorUp = errorLow
            elif len(vals) == 1 :
                central = vals[0]
                errorLow = 0
                errorUp = 0
            x.append( count )
            y.append( central )
            exl.append( 0 )
            exh.append( 0 )
            eyl.append( errorLow )
            eyh.append( errorUp  )
            count += 1
        graph = TGraphAsymmErrors( len(x) , x , y , exl , exh , eyl , eyh )
        graph.SetTitle( runEra )
        graph.SetName( MCName + "_" + runEra )
        graph.SetLineColor(  marker_info[ runEra ][1] )
        graph.SetLineWidth( 3 )
        graph.SetFillColor( 0 )
        graph.SetFillStyle( 0 )
        graph.SetMarkerStyle( marker_info[ runEra ][0] )
        graph.SetMarkerColor( marker_info[ runEra ][1] )
        allGraphs_3[(runEra,MCName)] =  graph
        mg.Add( graph , "p" )
        Legend.AddEntry( graph , graph.GetTitle()  , "lp" )
    canvas = TCanvas( MCName + "_AvgDataset" , MCName  + "_AvgDataset" , 0 , 0 , 5*167 , 5*200 )
    mg.Draw("AP")
    Legend.Draw()
    canvases_3["text" + MCName] = t.DrawTextNDC( 0.2, 0.8 , MCName )
    canvases_3["Leg" + MCName] = Legend
    mg.GetHistogram().GetYaxis().SetTitle( "Best Fit XSection #pm [DY, MiniBias, ZeroBias]" ) 
    mg.GetHistogram().GetYaxis().SetTitleOffset(1.82)
    canvases_3[MCName] = canvas
    labels = varNames
    xax = mg.GetHistogram().GetXaxis()
    minXax = xax.GetBinLowEdge(1)
    maxXax = xax.GetBinUpEdge( xax.GetNbins() )
    xax.Set( len(labels) , minXax , maxXax )
    i = 1
    for lbl in labels:
        xax.SetBinLabel(i, lbl)
        i+=1
                
    canvas.SaveAs( canvas.GetName() + ".png" )
    print canvas.GetName()
    

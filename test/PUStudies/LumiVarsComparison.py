import json, os, numpy, csv
from sys import stdout, argv
from ROOT import TFile, TChain, gROOT, TEventList, TH2D, TCanvas, TLegend, gStyle

class VarsMaker :
    def __init__(self, dataset):
        self.FileName = dataset + "%s.root"
        self.Titles = {"AVGnGoodVertices":"<#Good Vertices>",
                       "AVGnVertices":"<#Vertices>",
                       "AVGnEles":"<#Electrons>",
                       "AVGnMus":"<##mu's>",
                       "AVGnChargedHadrons":"<#Charged Hadrons>", 
                       "AVGnLostTracks":"<#Lost Tracks>",     
                       "AVGnPhotons":"<##gamma's>",        
                       "AVGnNeutralHadrons":"<#Neutral Hadrons>", 
                       "nEventsInLumi":"#Events In Lumisectoin" ,
                       "AVGfixedGridRhoFastjetCentralNeutral":"<#rho Central Neutral>",
                       "AVGfixedGridRhoAll":"<#rho All>",
                       "AVGfixedGridRhoFastjetAll":"<#rho All Fastjets>",
                       "AVGfixedGridRhoFastjetAllCalo":"<#rho All Calo>",
                       "AVGfixedGridRhoFastjetCentral":"<#rho Central>",
                       "AVGfixedGridRhoFastjetCentralCalo":"<#rho Central Calo>",
                       "AVGfixedGridRhoFastjetCentralChargedPileUp":"<#rho Central Charged Pileup>"}
        if dataset == "SingleMu" :
            self.vars = {"AVGnGoodVertices":[100,0,25],
                         "AVGnVertices":[120,0,30 ],
                         #"AVGnInt",            
                         #"AVGnInt50ns",        
                         "AVGnEles":[20,0,1 ],
                         "AVGnMus":[100,2,5] ,
                         "AVGnChargedHadrons":[200,200,700],
                         "AVGnLostTracks":[30,0,3 ],
                         "AVGnPhotons":[500 , 50 , 300] ,
                         "AVGnNeutralHadrons":[200,30,80 ],
                         "nEventsInLumi":[1000, 0 , 1000 ],
                         "AVGfixedGridRhoFastjetCentralNeutral":[70 , 0 , 7 ],}
            for rho in ["fixedGridRhoAll",
                        "fixedGridRhoFastjetAll",
                        "fixedGridRhoFastjetAllCalo",
                        "fixedGridRhoFastjetCentral",
                        "fixedGridRhoFastjetCentralCalo",
                        "fixedGridRhoFastjetCentralChargedPileUp"] :
                self.vars[ "AVG" + rho ] = [100,0,20 ]
#do you need to adjust the x-axis for the below var same as in plotdatamc and makefriends?
        elif dataset == "ZeroBias" :
            self.vars = {"AVGnGoodVertices":[100,5,25],
                         "AVGnVertices":[100,6,50],
                         #"AVGnInt",            
                         #"AVGnInt50ns",        
                         #"AVGnEles":[10,0,1],
                         #"AVGnMus":[60,0,3],
                         "AVGnChargedHadrons":[600,100,1400], 
                         #"AVGnLostTracks":[60,0,3],     
                         "AVGnPhotons":[500 , 50 , 300 ],        
                         "AVGnNeutralHadrons":[80,30,90], 
                         #"nEventsInLumi":[1000, 0 , 1000],
                         "AVGfixedGridRhoFastjetCentralNeutral":[50 , 0 , 6],
                         "AVGfixedGridRhoFastjetAllCalo":[70, 0 , 20],
                         "AVGfixedGridRhoFastjetCentralCalo":[50 , 0 , 10 ],
                         "AVGfixedGridRhoAll":[80 , 4, 40],
                         "AVGfixedGridRhoFastjetAll":[80 , 4, 25],
                         "AVGfixedGridRhoFastjetCentral":[80 , 4 , 25],
                         "AVGfixedGridRhoFastjetCentralChargedPileUp":[100, 0 , 25]
}
        elif dataset == "MinBias" :
            self.vars = {"AVGnGoodVertices":[100,0,0.4],
                         "AVGnVertices":[100,0,0.4],
                        #"AVGnInt",            
                         #"AVGnInt50ns",        
                         #"AVGnEles":[100,0,0.5],
                         #"AVGnMus":[100,0,0.1],
                         "AVGnChargedHadrons":[100,0,100], 
                         #"AVGnLostTracks":[20,0.,.5],     
                         "AVGnPhotons":[ 100 , 0 , 100 ],
                         "AVGnNeutralHadrons":[60,0,30], 
                         "nEventsInLumi":[10, 0 , 10] }
            for rho in ["fixedGridRhoAll",
                        "fixedGridRhoFastjetAll",
                        "fixedGridRhoFastjetAllCalo",
                        "fixedGridRhoFastjetCentral",
                        "fixedGridRhoFastjetCentralCalo",
                        "fixedGridRhoFastjetCentralChargedPileUp",
                        "fixedGridRhoFastjetCentralNeutral"] :
                self.vars[ "AVG" + rho ] = [100,0,0.5]

        for var in self.vars:
            self.vars[var].append( self.Titles[var] )
                
class LumiCorrelationStudiesPerRun :
    def __init__(self, run , file_in , vars , title):
        self.File = TFile.Open( file_in )
        self.Tree = self.File.Get("PUAnalyzer/Trees/Lumis")
        self.Tree.BuildIndex( "run" , "lumi" )

        if run == "A":
            self.RunMin = 315252 
            self.RunMax =  316995
            self.Color = 4 
        elif run == "B":
            self.RunMin = 316998
            self.RunMax = 319311
            self.Color = 5
        elif run == "C":
            self.RunMin = 319313
            self.RunMax = 320393
            self.Color = 6
        #elif run == "D":
            #self.RunMin = 320413
            #self.RunMax = 321413
            #self.Color = 7
        #elif run == "D":
            #self.RunMin = 321414
            #self.RunMax = 322414
            #self.Color = 7 
        #elif run == "D":
            #self.RunMin = 322415
            #self.RunMax = 323415
            #self.Color = 7
        #elif run == "D":
            #self.RunMin = 323416
            #self.RunMax = 324416
            #self.Color = 7
        #elif run == "D":
            #self.RunMin = 324417
            #self.RunMax = 325273
            #self.Color = 7
        elif run == "D":
            self.RunMin = 320413
            self.RunMax = 325273
            self.Color = 7
        elif run == "E":
            self.RunMin = 325308
            self.RunMax = 325310
            self.Color = 8 
        else:
            self.RunMin = self.Tree.GetMinimum("run")
            self.RunMax = self.Tree.GetMaximum("run")
        
        self.Name = run
        self.Vars = vars
        self.AllHistos = {}
        for var in self.Vars:
            bins = self.Vars[var]
            if argv[2] == "p1":
                self.AllHistos[var] = TH2D( "h" + run +var , run+";Integrated Luminosity (/ub);" + bins[3] , 3000 , 50000 , 350000 , bins[0] , bins[1] , bins[2] ) # for integrated lumi from pu_latest.txt
            elif argv[2] == "p3" :
                self.AllHistos[var] = TH2D( "h" + run +var , run+";Average bunch instantaneous luminosity (/ub/Xing);" + bins[3] , 300, 0.00001 , 0.001 , bins[0] , bins[1] , bins[2] ) # for avg lumi from pu_latest.txt
            elif argv[2] == "b" :
                self.AllHistos[var] = TH2D( "h" + run +var , run+";Normalized Integrated luminosity (/ub);" + bins[3] , 350, 0.0 , 10 , bins[0] , bins[1] , bins[2] ) # for avg recorded lumi from brilcalc
            if run == "E": 
               self.AllHistos[var].SetMarkerColorAlpha(self.Color , 20)
            else:
                 self.AllHistos[var].SetMarkerColorAlpha(self.Color , 0.5)
            self.AllHistos[var].SetFillColor(self.Color)
            self.AllHistos[var].SetTitle("")

    def RunIsHere( self, run):
        
        ret = not ( (float(run) > self.RunMax) or (float(run) < self.RunMin) )
        #print self.Name , float(run), float( run)-self.RunMin , self.RunMax-float(run) , ret
        return ret

    def FillHists(self, run , lumisection , instantLumi):
        #print run,lumisection
        self.Tree.GetEntryWithIndex (int(run) , int(lumisection) )
        for var in self.Vars :
            self.AllHistos[ var ].Fill( instantLumi , self.Tree.GetLeaf(var).GetValue() )

    def Write( self, fout ):
        fout.mkdir( self.Name ).cd()
        for h in self.AllHistos:
            self.AllHistos[h].Write()


class LumiValsFromBrilCalc :
    def __init__(self , fname , nbx_perfill):
        self.FillInfo = {}
        self.AllInfo = {}
        self.Min = None
        self.Max = None

        with open(nbx_perfill , 'rb' ) as csvfile:
            nbxreader = csv.reader( csvfile , delimiter="," )
            for row in nbxreader:
                self.FillInfo[ int(row[0]) ] = {'nbx':int(row[1]) , 'runs':[] }
        
        with open(fname , 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                if row[0][0] == "#" :
                    continue
                self.add( row )

    def add(self , row ):
        #run:fill,ls,time,beamstatus,E(GeV),delivered(hz/ub),recorded(hz/ub),avgpu,source
        fill = int(row[0].split(':')[1])
        nbx = 1
        if fill not in self.FillInfo :
            print "fill " , fill , "was not found in nbxfile"
        nbx = self.FillInfo[fill]['nbx']
        run = int(row[0].split(':')[0])
        self.FillInfo[fill]['runs'].append( run )
        if run not in self.AllInfo :
            self.AllInfo[ run ] = {}
        ls = int( row[1].split(':')[0] )
        delivered = float( row[5] )
        recorded = float( row[6] )
        avgpu = float( row[7] )
        recavg =  recorded/nbx
        self.AllInfo[run][ls] = [ delivered , recorded ,  delivered/nbx ,recavg , avgpu ]
        if self.Min == None or self.Min > recavg:
            self.Min = recavg
        if self.Max == None or self.Max < recavg:
            self.Max = recavg
    def Print(self):
        for run in self.AllInfo :
            print run
            for ls in self.AllInfo[run] :
                delivered , recorded , avgdel , avgrec , avgpu = self.AllInfo[run][ls]
                print "\t" , ls , delivered , recorded , avgdel , avgrec , avgpu

    def getLumi(self, run , ls , del_or_rec = 'rec' , avg_or_total = 'avg'):
        delivered , recorded , avgdel , avgrec , avgpu = self.AllInfo[run][ls]
        #print del_or_rec , avg_or_total , delivered , recorded , avgdel , avgrec , avgpu
        if del_or_rec == 'rec' :
            if avg_or_total == 'avg' :
                return avgrec
            elif avg_or_total == 'total' :
                return recorded
        elif del_or_rec == 'del' :
            if avg_or_total == 'avg' :
                return avgdel
            elif avg_or_total == 'total' :
                return delivered
        else :
            return avgpu
        
class LumiCorrelationStudies :
    def __init__(self, path , dataset , title):
        self.Dataset = dataset
        self.Vars = VarsMaker( dataset )
        self.FileName = dataset + "%s.root"

        self.AllRuns = {}
        self.AllRunNames = []
        #for runEra in ['A','B','C','D','E']:
        for runEra in ['A','B']:
            fname = path + self.FileName%(runEra)
            if not os.path.isfile( fname ):
                print "data file" , fname , "doesn't exist"
                continue
            self.AllRunNames.append( runEra )
            self.AllRuns[ runEra ] = LumiCorrelationStudiesPerRun( runEra , fname , self.Vars.vars , title )

        self.PULumiData = None
	#with open('pileup_new.txt') as data_file:    
            #self.PULumiData = json.load(data_file)
        if runEra == "E":
	   with open('pileup_JSON.txt') as data_file:    
	       self.PULumiData = json.load(data_file)
        else:
	     with open('pileup_latest.txt') as data_file:    
 	         self.PULumiData = json.load(data_file)
        self.ntot_runs = len(self.PULumiData)
        self.ntot_lumis = 0
        for run in self.PULumiData:
            runinfo = self.PULumiData[run]
            self.ntot_lumis += len( runinfo )

        self.BrilCalcLumis = LumiValsFromBrilCalc('LumiPerLumiSection.csv' , 'NBX_perFill_2018_only18.csv')
        #print self.BrilCalcLumis.Min , self.BrilCalcLumis.Max
        
        
    def LoopBrilCalc(self):
        current_run = 0
        current_lumi = 0
        for run in self.BrilCalcLumis.AllInfo:
            thisRun = None
            for r in self.AllRuns:
                if self.AllRuns[r].RunIsHere( run ) :
                    thisRun = self.AllRuns[r]
                    #print "run set"
            if thisRun == None :
                stdout.write("\n") 
                print "run : ", run , " was not found in any tree"
                continue
            runinfo = self.BrilCalcLumis.AllInfo[run]
            current_run += 1
            for lumi in runinfo:
                current_lumi += 1
                if current_lumi % 100:
                    stdout.write("\r%d out of %d runs and lumi : %d out of %d" % ( current_run  , self.ntot_runs,  current_lumi  ,self.ntot_lumis ) )
                    stdout.flush()
        
                lumisection = lumi
                luminosity = self.BrilCalcLumis.getLumi( run , lumi )
                if luminosity > 7 :
                    print luminosity
                thisRun.FillHists(run , lumisection , luminosity )
                #val2 = lumi[2]
                #val3 = lumi[3]

        
    def Loop(self , index = 1):
        current_run = 0
        current_lumi = 0
        for run in self.PULumiData:
            thisRun = None
            for r in self.AllRuns:
                if self.AllRuns[r].RunIsHere( run ) :
                    thisRun = self.AllRuns[r]
                    #print "run set"
            if thisRun == None :
                stdout.write("\n") 
                print "run : ", run , " was not found in any tree"
                continue
            runinfo = self.PULumiData[run]
            current_run += 1
            for lumi in runinfo:
                current_lumi += 1
                if current_lumi % 100:
                    stdout.write("\r%d out of %d runs and lumi : %d out of %d" % ( current_run  , self.ntot_runs,  current_lumi  ,self.ntot_lumis ) )
                    stdout.flush()
        
                lumisection = lumi[0]
                #luminosity = lumi[1]
                luminosity = lumi[index]
                thisRun.FillHists(run , lumisection , luminosity )
                #val2 = lumi[2]
                #val3 = lumi[3]

    def Write(self , appendix):
        self.fout = TFile.Open("LumiAnalysis_%s_%s.root" % (self.Dataset , appendix) , "recreate")
        for run in self.AllRuns:
            self.AllRuns[run].Write( self.fout )

        gROOT.SetBatch(True)
        gStyle.SetOptStat(0)
        self.Canvases = {}
        self.fout.mkdir("Canvases").cd()
        for var in self.Vars.vars :
            l = TLegend(0.65 , 0.1 , 0.9 , 0.4 )
            l.SetName( var + "_legend" )
            c = TCanvas( var )
            option = ""
            for run in self.AllRunNames:
                self.AllRuns[run].AllHistos[var].Draw( option )
                l.AddEntry( self.AllRuns[run].AllHistos[var] , "Run" + self.AllRuns[run].Name , "f" )
                if not "SAME" in option :
                    option += " SAME"
            l.Draw()
            l.Write()
            self.Canvases[ var + "_l" ] = l
            c.Write()
            c.SaveAs("./corr/%s.png" %(var))
            self.Canvases[ var ] = c
        #gROOT.SetBatch(False)
        #gStyle.SetOptStat(1)
                
        self.fout.Close()
            
path = "/eos/home-h/helfaham/PU_work/UL/2018/samples_hadd/"
lcs = LumiCorrelationStudies( path , argv[1] , argv[2]) 
#arg1 is the sample, arg2 is the plot type(see above)
if argv[2] == "p1":
    lcs.Loop( 1 )
elif argv[2] == "p3" :
    lcs.Loop(3 )
elif argv[2] == "b" :
    lcs.LoopBrilCalc()
lcs.Write(argv[2])

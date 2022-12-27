from ROOT import TH1, TFile, TDirectory, TGraphAsymmErrors , gDirectory, TIter, kRed
import array

def plotIt( dir_ , era , prop , jsonName = "latest" ):
    canvas_name = "{json:s}_100_{era:s}/{json:s}_100_{era:s}/{prop:s}/{json:s}_100_{era:s}_{prop:s}_canvas".format( json=jsonName , prop=prop , era=era )
    print canvas_name
    main_canvas = dir_.Get(canvas_name).Clone()

    ratio_name = "{json:s}_{{0}}_{era:s}/{json:s}_{{0}}_{era:s}/{prop:s}/AdditionalInfo/{json:s}_{{0}}_{era:s}_{prop:s}_Ratio".format( json=jsonName , prop=prop  , era=era )
    #print ratio_name.format("nominal")
    main_ratio = dir_.Get(ratio_name.format("100"))
    up_ratio = dir_.Get(ratio_name.format("105"))
    down_ratio = dir_.Get(ratio_name.format("95"))

    x = []
    y_low = []
    y_up = []
    y_center = []
    dy_u = []
    dy_d = []
    dx = []
    ymax = 0
    for i in range(1 , up_ratio.GetNbinsX()+1):
        x.append( up_ratio.GetBinCenter( i ) )
        dx.append(0)
        y1 = up_ratio.GetBinContent( i )
        y2 = down_ratio.GetBinContent( i )
        y_low.append( min(y1,y2) )
        ym = max(y1,y2)
        y_up.append( ym )
        
        y_center.append( main_ratio.GetBinContent(i) )
        if max( ym , y_center[-1] ) > ymax:
            ymax = max( ym , y_center[-1] )
        
        dy_u.append( y_up[-1] - y_center[-1] )
        dy_d.append( y_center[-1] - y_low[-1])

    ret = TGraphAsymmErrors( len(x) , array.array( 'f' , x ) ,
                             array.array( 'f',y_center) , array.array( 'f',dx) , array.array( 'f',dx),
                             array.array( 'f', dy_d ) , array.array( 'f', dy_u ) )
    ret.SetLineColor( kRed )
    ret.SetLineStyle( 3 )
    ret.SetLineWidth( 10 )
    
    itr = TIter( main_canvas.GetListOfPrimitives() )
    itr.Next()
    itr.Next()
    itr.cd()
    ret.Draw("LP")
    return main_canvas,ret


mainDirs = ["All" , "eraB" , "eraC" , "eraD", "eraE","eraF","eraG","eraH"]
jsons = [ "latest" ]
props = ["nVertices" , "RhoAll" , "nChargedParticles" ]

f = TFile.Open("out_latest.root")

allNC = []
allGr = []
for mdir in mainDirs :
    #f.cd( mdir )
    for js in jsons:
        for prp in props:
            canvas,graph = plotIt( gDirectory , mdir , prp , js )
            print canvas.GetName()
            canvas.Draw()
            canvas.SaveAs(canvas.GetName() + ".png")
            allNC.append( canvas )
            allGr.append( graph )


from ROOT import TCanvas
c = TCanvas()
allGr[0].Draw("AP")

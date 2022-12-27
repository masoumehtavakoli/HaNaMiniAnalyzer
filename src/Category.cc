#include "../interface/Category.h"
#include <iostream>
using namespace std;
Category::Category( TString name, TString SampleName) : Name(name){
    hNPV_pv = new Histograms(Name, SampleName, "NPV_pv", 100, -0.5, 99.5);
    hMuMult = new Histograms(Name, SampleName, "MuMult", 10, -0.5, 9.5);
    hJetMult = new Histograms(Name, SampleName, "JetMult", 10, -0.5, 9.5);
    hBJetMult = new Histograms(Name, SampleName, "BJetMult", 10, -0.5, 9.5);
    hNPV_final = new Histograms(Name, SampleName, "NPV_final", 100, -0.5, 99.5);
    hMuPt = new Histograms(Name, SampleName, "MuPt", 30, 0., 150.);
    hMuEta = new Histograms(Name, SampleName, "MuEta", 30, -3.0, 3.0);
    hLeadMuPt = new Histograms(Name, SampleName, "LeadMuPt", 30, 0., 150.);
    hLeadMuEta = new Histograms(Name, SampleName, "LeadMuEta", 30, -3.0, 3.0);
    hSubLeadMuPt = new Histograms(Name, SampleName, "SubLeadMuPt", 30, 0., 150.);
    hSubLeadMuEta = new Histograms(Name, SampleName, "SubLeadMuEta", 30, -3.0, 3.0);
    hDiMuMass = new Histograms(Name, SampleName, "DiMuMass", 85, 10., 180.);
    hDiMuPt = new Histograms(Name, SampleName, "DiMuPt", 40, 0., 200.);
    hDiMuDr = new Histograms(Name, SampleName, "DiMuDr", 50, 0, 5.0);
    hJetPt = new Histograms(Name, SampleName, "JetPt", 30, 0., 150.);
    hJetEta = new Histograms(Name, SampleName, "JetEta", 50, -5.0, 5.0);
    hJetBTag = new Histograms(Name, SampleName, "JetBTag", 20, 0, 1.);
    hLeadJetPt = new Histograms(Name, SampleName, "LeadJetPt", 30, 0., 150.);
    hLeadJetEta = new Histograms(Name, SampleName, "LeadJetEta", 50, -5.0, 5.0);
    hLeadJetBTag = new Histograms(Name, SampleName, "LeadJetBTag", 20, 0, 1.);
    hSubLeadJetPt = new Histograms(Name, SampleName, "SunLeadJetPt", 30, 0., 150.);
    hSubLeadJetEta = new Histograms(Name, SampleName, "SubLeadJetEta", 50, -5.0, 5.0);
    hSubLeadJetBTag = new Histograms(Name, SampleName, "SubLeadJetBTag", 20, 0, 1.);
    hDiBJetMass = new Histograms(Name, SampleName, "DiBJetMass", 30, 0., 300.);
    hDiBJetPt = new Histograms(Name, SampleName, "DiBJetPt", 15, 0., 150.);
    hDiBJetDr = new Histograms(Name, SampleName, "DiBJetDr", 50, 0, 5.0);
    hFourBodyMass = new Histograms(Name, SampleName, "FourBodyMass", 120, 0., 1200.);
    hFourBodyPt = new Histograms(Name, SampleName, "FourBodyPt", 20, 0., 200.);
    hDiffMassMuB = new Histograms(Name, SampleName, "DiffMassMuB", 15, 0., 150.);
    hRelDiffMassMuB = new Histograms(Name, SampleName, "RelDiffMassMuB", 20, 0, 1.);
    hMET = new Histograms(Name, SampleName, "MET", 20, 0., 200.);
    hMETSignificance = new Histograms(Name, SampleName, "METSignificance", 100, 0, 100.);
}


void Category::Fill( std::vector<float> v , double w = 1., double PU = -1. ){
    if(PU != -1)
    	hNPV_pv->Fill(v[0],w/(PU==0. ? 1.0 : PU));
    else
        hNPV_pv->Fill(v[0],w);
    hMuMult->Fill(v[1], w);
    hJetMult->Fill(v[2], w);
    hBJetMult->Fill(v[3], w);
    hNPV_final->Fill(v[4], w);
    hMuPt->Fill(v[5], w);
    hMuEta->Fill(v[6], w);
    hMuPt->Fill(v[32], w);
    hMuEta->Fill(v[33], w);
    hLeadMuPt->Fill(v[7], w);
    hLeadMuEta->Fill(v[8], w);
    hSubLeadMuPt->Fill(v[9], w);
    hSubLeadMuEta->Fill(v[10], w);
    hDiMuMass->Fill(v[11], w);
    hDiMuPt->Fill(v[12], w);
    hDiMuDr->Fill(v[13], w);
    hJetPt->Fill(v[14], w);
    hJetEta->Fill(v[15], w);
    hJetBTag->Fill(v[16], w);
    hLeadJetPt->Fill(v[17], w);
    hLeadJetEta->Fill(v[18], w);
    hLeadJetBTag->Fill(v[19], w);
    hSubLeadJetPt->Fill(v[20], w);
    hSubLeadJetEta->Fill(v[21], w);
    hSubLeadJetBTag->Fill(v[22], w);
    hDiBJetMass->Fill(v[23], w);
    hDiBJetPt->Fill(v[24], w);
    hDiBJetDr->Fill(v[25], w);
    hFourBodyMass->Fill(v[26], w);
    hFourBodyPt->Fill(v[27], w);
    hDiffMassMuB->Fill(v[28], w);
    hRelDiffMassMuB->Fill(v[29], w);
    hMET->Fill(v[30], w);
    hMETSignificance->Fill(v[31], w);
    int diff = v.size() - 34;
    if(diff <= 0) return;
    if((diff % 3) != 0) {
	cout<<"Problem with number of jet quantities, pt, eta, btag"<<endl;
	return;
    }
    for(int i = 0; i < (int)(diff/3); i++){
	hJetPt->Fill(v[i], w);
	hJetEta->Fill(v[i], w);
	hJetBTag->Fill(v[i], w);
    }
}


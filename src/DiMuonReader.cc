#include "Haamm/HaNaMiniAnalyzer/interface/DiMuonReader.h"

using namespace edm;
using namespace pat;

DiMuonReader::DiMuonReader( edm::ParameterSet const& iConfig, edm::ConsumesCollector && iC , bool isData , string SetupDir) :
  BaseEventReader< pat::MuonCollection >( iConfig , &iC ),
  MuonLeadingPtCut( iConfig.getParameter<double>( "MuonLeadingPtCut" ) ),
  MuonSubLeadingPtCut( iConfig.getParameter<double>( "MuonSubLeadingPtCut" ) ),
  MuonIsoCut( iConfig.getParameter<double>( "MuonIsoCut" ) ),
  MuonEtaCut( iConfig.getParameter<double>( "MuonEtaCut" ) ),
  DiMuLowMassCut( iConfig.getParameter<double>( "DiMuLowMassCut" ) ),
  DiMuZMassWindow( iConfig.getParameter<double>( "DiMuZMassWindow" ) ),
  MuonID( iConfig.getParameter<int>( "MuonID" ) ), // 0 no id, 1 loose, 2 medium, 3 tight, 4 soft
  DiMuCharge( iConfig.getParameter<int>( "DiMuCharge" ) ),
  IsData(isData),
  isHamb(iConfig.getParameter<bool>( "isHamb" ))
{
  if( !IsData ){
    TFile* f1 = TFile::Open( TString(SetupDir + "/MuonIDSF.root") );
    gROOT->cd();
    hMuSFID = NULL;
    if(MuonID == 1 ) // Loose ID
      hMuSFID = (TH2*)( f1->Get("MC_NUM_LooseID_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio")->Clone("MuSFID") );
    else if(MuonID == 2 ) // Medium ID
      hMuSFID = (TH2*)( f1->Get("MC_NUM_MediumID_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio")->Clone("MuSFID") );
    else if(MuonID == 3 ) // Tight ID
      hMuSFID = (TH2*)( f1->Get("MC_NUM_TightIDandIPCut_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio")->Clone("MuSFID") );
    else if(MuonID == 4 ) // Soft ID
      hMuSFID = (TH2*)( f1->Get("MC_NUM_SoftID_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio")->Clone("MuSFID") );
    else
      cout << "No scale factor is availabel for Muon ID " << MuonID << endl;
    f1->Close();
    
    f1 = TFile::Open( TString(SetupDir + "/MuonIsoSF.root") );
    gROOT->cd();
    if( MuonIsoCut == 0.15 )
      hMuSFIso = (TH2*)( f1->Get("MC_NUM_TightRelIso_DEN_TightID_PAR_pt_spliteta_bin1/pt_abseta_ratio")->Clone("MuSFIso") );
    else if( MuonIsoCut == 0.25 )
      hMuSFIso = (TH2*)( f1->Get("MC_NUM_LooseRelIso_DEN_TightID_PAR_pt_spliteta_bin1/pt_abseta_ratio")->Clone("MuSFIso") );
    else
      cout << "No scale factor is availabel for Muon Iso " << MuonIsoCut << endl;
    f1->Close();
  }

  cout << MuonSubLeadingPtCut << "  " << MuonEtaCut << "  " << MuonLeadingPtCut << "    " << MuonIsoCut << "    " << MuonID << endl;
}

DiMuonReader::SelectionStatus DiMuonReader::Read( const edm::Event& iEvent, const reco::Vertex* PV ){ 
  BaseEventReader< pat::MuonCollection >::Read( iEvent );
    
  W = 1.0;
  goodMus.clear();
  for (const pat::Muon &mu : *handle) {
    if (mu.pt() < MuonSubLeadingPtCut || fabs(mu.eta()) > MuonEtaCut )
      continue;
    if( (goodMus.size() == 0) && (mu.pt() < MuonLeadingPtCut) )
      continue;

    if( MuonID == 1 ){
      if (!muon::isLooseMuon( mu ) ) continue;
    }
    else if(MuonID == 2){
      if (!muon::isMediumMuon( mu ) ) continue;
    }
    else if(MuonID == 3){
      if (!muon::isTightMuon(mu ,*PV) ) continue;
    }
    else if(MuonID == 4){
      if (!muon::isSoftMuon( mu ,*PV) ) continue;
    }
    reco::MuonPFIsolation iso = mu.pfIsolationR04();
    double reliso = (iso.sumChargedHadronPt+TMath::Max(0.,iso.sumNeutralHadronEt+iso.sumPhotonEt-0.5*iso.sumPUPt))/mu.pt();
    if( reliso > MuonIsoCut) continue;
    goodMus.push_back( mu );
  }
    
  if( goodMus.size() < 2 ) return DiMuonReader::LessThan2Muons ;
  
  for ( pat::MuonCollection::iterator i = goodMus.begin(); i != goodMus.end(); ++i) {
    goodMusOS.clear();
    int mu0charge= i->charge();
    goodMusOS.push_back( *i );
    for(pat::MuonCollection::iterator j = i ; j != goodMus.end(); ++j) 
      if( (mu0charge * j->charge()) == DiMuCharge ){
	goodMusOS.push_back( *j );
	break;
      }
    if( goodMusOS.size() == 2 )
      break;
  }
  if( goodMusOS.size() != 2 )
    return DiMuonReader::NoPairWithChargeReq;

  if( !IsData ){
    if( MuonIsoCut == 0.25 )
      W = MuonSFLoose(  goodMusOS[0].eta() , goodMusOS[0].pt() , goodMusOS[1].eta() , goodMusOS[1].pt() ); 
    else if( MuonIsoCut == 0.15 )
      W = MuonSFMedium( goodMusOS[0].eta() , goodMusOS[0].pt() , goodMusOS[1].eta() , goodMusOS[1].pt() ); 
  }
    
  DiMuon = DiObjectProxy( goodMusOS[0] , goodMusOS[1] );
  
  if( DiMuon.totalP4().M() < DiMuLowMassCut ) return DiMuonReader::LowMassPair;

  if(!isHamb){  
  	if( DiMuon.totalP4().M() > (91.0-DiMuZMassWindow) && DiMuon.totalP4().M() < (91.0+DiMuZMassWindow) ) return DiMuonReader::UnderTheZPeak;
  } else {
  	if( DiMuon.totalP4().M() > (91.0-DiMuZMassWindow) ) return DiMuonReader::UnderTheZPeak;
  }
  
  return DiMuonReader::Pass;
}

double DiMuonReader::MuonSFMedium( double etaL , double ptL , double etaSL , double ptSL ){
  // To accound for boundary effects
  if( ptSL < 20 ) ptSL = 20.01;
  if( ptL < 20 ) ptL = 20.01;
  if( ptSL > 120 ) ptSL = 119;
  if( ptL > 120 ) ptL = 119;
  //AN2016_025_v7 Figure 6, Middle Row, Right for trigger
  double ret = 1.0;

  double el = fabs(etaL);
  double esl = fabs(etaSL);
  if(el < 1.2 && esl < 1.2 )
    ret = 0.926 ;				
  else if( el < 1.2 )
    ret = 0.943;
  else if( esl < 1.2 )
    ret = 0.958 ;
  else 
    ret = 0.926 ;

  ret *= ( hMuSFID->GetBinContent( hMuSFID->FindBin( ptL , el ) ) * hMuSFID->GetBinContent( hMuSFID->FindBin( ptSL , esl ) ) );
  ret *= (hMuSFIso->GetBinContent(hMuSFIso->FindBin(ptL ,el ) ) * hMuSFIso->GetBinContent( hMuSFIso->FindBin( ptSL , esl ) ) );

  return ret;
}
double DiMuonReader::MuonSFLoose( double etaL , double ptL , double etaSL , double ptSL ){
  //AN2016_025_v7 Figure 19, Middle Row, Right for trigger
  double ret = 1.0;
    
  double el = fabs(etaL);
  double esl = fabs(etaSL);
  if(el < 1.2 && esl < 1.2 )
    ret = 0.930 ;				
  else if( el < 1.2 )
    ret = 0.933;
  else if( esl < 1.2 )
    ret = 0.951 ;
  else 
    ret = 0.934 ;

  if( ptSL < 20 || ptL < 20 )
    return ret;

  ret *= ( hMuSFID->GetBinContent( hMuSFID->FindBin( ptL , el ) ) * hMuSFID->GetBinContent( hMuSFID->FindBin( ptSL , esl ) ) );
  ret *= (hMuSFIso->GetBinContent(hMuSFIso->FindBin(ptL ,el ) ) * hMuSFIso->GetBinContent( hMuSFIso->FindBin( ptSL , esl ) ) );

  return ret;
}

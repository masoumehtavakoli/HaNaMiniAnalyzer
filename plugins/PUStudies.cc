#include "Haamm/HaNaMiniAnalyzer/interface/HaNaBaseMiniAnalyzer.h"

#include <iostream>
#include "TTree.h"

using namespace std;

// class UIntReader : public BaseEventReader< unsigned int  > {
// public:
//   UIntReader( std::string tag , edm::ConsumesCollector && iC) :
//     BaseEventReader< unsigned int  >(tag , &iC)
//   {
//   };

//   virtual double Read( const edm::Event& iEvent ){
//     BaseEventReader< unsigned int  >::Read( iEvent );
//     Value =*(BaseEventReader< unsigned int  >::handle);
//     return Value;
//   }
   
//   unsigned int Value ;
// };

class DoubleReader : public BaseEventReader< double  > {
public:

  DoubleReader( std::string tag , edm::ConsumesCollector && iC) :
    BaseEventReader< double  >(tag , &iC)
  {
    tagName = tag;
    Value = -1;
  };

  std::string tagName ;

  virtual double Read( const edm::Event& iEvent ){
    BaseEventReader< double  >::Read( iEvent );
    Value =*(BaseEventReader< double  >::handle);
    //std::cout << tagName << " : " << Value << std::endl;
    AVG += Value;
    n ++ ;

    return Value;
  }

  void CalcAVG(){
    if(n != 0)
      AVG /= n;
    else
      AVG = -999;
  }
  void ResetAVG(){
    AVG = 0 ;
    n = 0 ;
  }

  float Value ;
  float AVG;
  int n;
};

class PUAnalyzer : public HaNaBaseMiniAnalyzer{
public:
  explicit PUAnalyzer(const edm::ParameterSet&);
  ~PUAnalyzer();

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions){ HaNaBaseMiniAnalyzer::fillDescriptions( descriptions ); }

  Histograms* hnTruInt;

  TTree* theTree;
  TTree* theLumiTree;
  //TREE VALS
  unsigned int runNumber, lumiNumber;
  // unsigned long long EventN;
  int bxNumber, orbitNumber;
  // char nVertices, nGoodVertices , nInt , nInt50ns ;
  int nLostTracks; // ,nEles , nMus , nChargedHadrons ,  nPhotons, nNeutralHadrons ;
  float InvMass , reliso1 , reliso2;
  bool ZSelection, passDiMuMedium, passDiMuTight;
  bool mu1positive, mu2positive;
  float mu1pt, mu2pt, mu1eta , mu2eta;

  float AVGnGoodVertices, AVGnVertices, AVGnInt, AVGnInt50ns , AVGnEles , AVGnMus , AVGnChargedHadrons , AVGnLostTracks , AVGnPhotons , AVGnNeutralHadrons ;
  int nEventsInLumi;
  void ResetAVGs(){
    nEventsInLumi = 0;
    AVGnGoodVertices= AVGnVertices= AVGnInt= AVGnInt50ns = AVGnEles = AVGnMus = AVGnChargedHadrons = AVGnLostTracks = AVGnPhotons = AVGnNeutralHadrons = 0;
    for(auto rho : Rhos )
      rho->ResetAVG();
  };
  void CalcAVGs(){
    if(nEventsInLumi != 0){
      AVGnGoodVertices /= nEventsInLumi; 
      AVGnVertices/= nEventsInLumi; 
      AVGnInt/= nEventsInLumi; 
      AVGnInt50ns /= nEventsInLumi; 
      AVGnEles /= nEventsInLumi; 
      AVGnMus /= nEventsInLumi; 
      AVGnChargedHadrons /= nEventsInLumi; 
      AVGnLostTracks /= nEventsInLumi; 
      AVGnPhotons /= nEventsInLumi; 
      AVGnNeutralHadrons /= nEventsInLumi;
    }else{
      AVGnGoodVertices= AVGnVertices= AVGnInt= AVGnInt50ns = AVGnEles = AVGnMus = AVGnChargedHadrons = AVGnLostTracks = AVGnPhotons = AVGnNeutralHadrons = -999;
    }
    for(auto rho : Rhos )
      rho->CalcAVG();
  }
  
  std::vector< DoubleReader* > Rhos ;
  //-------------
protected:
  virtual void beginJob() override;
  virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
  virtual void beginLuminosityBlock(LuminosityBlock const &, EventSetup const &) override {
    this->ResetAVGs();
    // cout << "New Lumi Started : " << nEventsInLumi << endl;
  };
  virtual void endLuminosityBlock(LuminosityBlock const &, EventSetup const &) override {
    this->CalcAVGs();
     // cout << nEventsInLumi << "  " ;
    this->theLumiTree->Fill();
    // cout << "Lumi ended : " <<  nEventsInLumi << endl;
  };

};

DEFINE_FWK_MODULE(PUAnalyzer);

PUAnalyzer::~PUAnalyzer() {}
PUAnalyzer::PUAnalyzer( const edm::ParameterSet& ps ) :
  HaNaBaseMiniAnalyzer( ps ) 
{
  cout << "constructor" << endl;
  for(auto s : ps.getParameter< std::vector<string> >("Rhos") ){
    Rhos.push_back( new DoubleReader( s , consumesCollector() ) ); 
    //cout << *(Rhos.rbegin())->tagName << endl;
  }

  ZSelection = ps.getParameter<bool>("ZSelection");
}
// ------------ method called once each job just before starting event loop  ------------
void PUAnalyzer::beginJob()
{
  cout << "beginjob" << endl;

  hnTruInt = new Histograms( SampleName , "nTruInteractions" , 100 , 0 , 100);
  hCutFlowTable = new Histograms( SampleName , "CutFlowTable" , 10 , 0.5 , 10.5);


  edm::Service<TFileService> fs;
  //fs->cd();
  TFileDirectory treeDir = fs->mkdir( "Trees" );
  //treeDir.cd();

  // TFile* f = TFile::Open("tree.root" , "RECREATE");
  // f->cd();
  // gDirectory->Print();
  theLumiTree = treeDir.make<TTree>("Lumis" , "Lumis");
  theLumiTree->Branch( "run" , &runNumber );
  theLumiTree->Branch( "lumi" , &lumiNumber );
  theLumiTree->Branch( "AVGnGoodVertices" , &AVGnGoodVertices );
  theLumiTree->Branch( "AVGnVertices" , &AVGnVertices );
  theLumiTree->Branch( "AVGnInt" , &AVGnInt );
  theLumiTree->Branch( "AVGnInt50ns" , &AVGnInt50ns );
  theLumiTree->Branch( "AVGnEles" , &AVGnEles );
  theLumiTree->Branch( "AVGnMus" , &AVGnMus );
  theLumiTree->Branch( "AVGnChargedHadrons" , &AVGnChargedHadrons );
  theLumiTree->Branch( "AVGnLostTracks" , &AVGnLostTracks );
  theLumiTree->Branch( "AVGnPhotons" , &AVGnPhotons );
  theLumiTree->Branch( "AVGnNeutralHadrons" , &AVGnNeutralHadrons );
  theLumiTree->Branch( "nEventsInLumi" , &nEventsInLumi );
  

  theTree = treeDir.make<TTree>("Events" , "Events");
  //fs->make<TTree>("SelectedEventNumbers" , "SelectedEventNumbers");

  theTree->Branch("run" , &runNumber );
  theTree->Branch("lumi" , &lumiNumber );
  theTree->Branch("bx" , &bxNumber );
  theTree->Branch("orbit" , &orbitNumber );

  // gDirectory->Print();
  theTree->Branch("nGoodVertices" , &(vertexReader->nGoodVtx) );
  theTree->Branch("nVertices" , &(vertexReader->vtxMult));
  theTree->Branch("nInt" , &(vertexReader->npv));
  theTree->Branch("nInt50ns" , &(vertexReader->npv50ns) );
  theTree->Branch("nEles" , &(packedReader->nEles));
  theTree->Branch("nMus" , &(packedReader->nMus));
  theTree->Branch("nChargedHadrons" , &(packedReader->nChargedHadrons) );
  theTree->Branch("nLostTracks" , &nLostTracks);
  theTree->Branch("nPhotons" , &(packedReader->nPhotons) );
  theTree->Branch("nNeutralHadrons" , &(packedReader->nNeutralHadrons) );
  
  

  for(auto rho : Rhos ){
    theTree->Branch(rho->tagName.c_str() , &(rho->Value) );
    theLumiTree->Branch( ("AVG"+rho->tagName).c_str() , &(rho->AVG) );
    //std::cout << rho->tagName << std::endl ;
  }


  if( ZSelection ){
    theTree->Branch("passDiMuTight", &passDiMuTight );
    theTree->Branch("passDiMuMedium", &passDiMuMedium );
    theTree->Branch("InvMass" , &InvMass);
    theTree->Branch("reliso2" , &reliso2);
    theTree->Branch("reliso1" , &reliso1);
    theTree->Branch("mu1positive" , &mu1positive);
    theTree->Branch("mu2positive" , &mu2positive);
    theTree->Branch("mu1pt" , &mu1pt);
    theTree->Branch("mu2pt" , &mu2pt);
    theTree->Branch("mu1eta" , &mu1eta);
    theTree->Branch("mu2eta" , &mu2eta);
  }
  theTree->Branch("W" , &W);
}



void PUAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{

  W = 1.0;
  stepEventSelection = 0;

  if( !IsData )
    W *= geninfoReader->Read( iEvent );
  hCutFlowTable->Fill( ++stepEventSelection , W );

  if(hltReader->Read( iEvent ) < 0 ){
    return;
  }
  hCutFlowTable->Fill( ++stepEventSelection , W );
  if( vertexReader->Read( iEvent ) < 0 )
    return;
  //auto vOutput = vertexReader->Read( iEvent );
  //cout << vOutput << endl;

  //if( vOutput < 0 )
    //return;
  hCutFlowTable->Fill( ++stepEventSelection , W );

  if(!IsData)
    hnTruInt->Fill( vertexReader->npv  , 1.0 );

  runNumber = iEvent.eventAuxiliary().run();
  lumiNumber = iEvent.eventAuxiliary().luminosityBlock();

  bxNumber = iEvent.eventAuxiliary().bunchCrossing();
  orbitNumber = iEvent.eventAuxiliary().orbitNumber();

  packedReader->Read( iEvent );

  lostReader->Read( iEvent );
  nLostTracks = lostReader->size();


  for(auto _Rho_ : Rhos ){
    _Rho_->Read(iEvent);
  }

  if( ZSelection ){
    //cout << vertexReader->PV()->ndof() << endl;
    switch( diMuReader->Read( iEvent , vertexReader->PV() ) ){
    case DiMuonReader::Pass :
    case DiMuonReader::UnderTheZPeak:   
      W *= (diMuReader->W) ;
      hCutFlowTable->Fill( ++stepEventSelection , W );
      break;
    case DiMuonReader::LowMassPair:
    case DiMuonReader::NoPairWithChargeReq:
    case DiMuonReader::LessThan2Muons :
      return ;
    }

    AVGnGoodVertices += vertexReader->nGoodVtx;
    AVGnVertices += vertexReader->vtxMult;
    AVGnInt += vertexReader->npv ;
    AVGnInt50ns += vertexReader->npv50ns;
    AVGnEles += packedReader->nEles;
    AVGnMus += packedReader->nMus;
    AVGnChargedHadrons += packedReader->nChargedHadrons;
    AVGnLostTracks += nLostTracks;
    AVGnPhotons += packedReader->nPhotons;
    AVGnNeutralHadrons += packedReader->nNeutralHadrons;
  

    InvMass = diMuReader->DiMuon.totalP4().M();
    passDiMuMedium = true;

    passDiMuTight = ( muon::isTightMuon( diMuReader->DiMuon.mu1() , *vertexReader->PV() )
		      && muon::isTightMuon( diMuReader->DiMuon.mu2() , *vertexReader->PV() ) );

    mu1pt = diMuReader->DiMuon.mu1().pt();
    mu2pt = diMuReader->DiMuon.mu2().pt();

    reco::MuonPFIsolation iso = diMuReader->DiMuon.mu1().pfIsolationR04();
    reliso1 = (iso.sumChargedHadronPt+TMath::Max(0.,iso.sumNeutralHadronEt+iso.sumPhotonEt-0.5*iso.sumPUPt))/mu1pt;
    iso = diMuReader->DiMuon.mu2().pfIsolationR04();
    reliso2 = (iso.sumChargedHadronPt+TMath::Max(0.,iso.sumNeutralHadronEt+iso.sumPhotonEt-0.5*iso.sumPUPt))/mu2pt;

    mu1eta = diMuReader->DiMuon.mu1().eta();
    mu2eta = diMuReader->DiMuon.mu2().eta();

    mu1positive = diMuReader->DiMuon.mu1().charge() > 0;
    mu2positive = diMuReader->DiMuon.mu2().charge() > 0;
  }else{
    AVGnGoodVertices += vertexReader->nGoodVtx;
    AVGnVertices += vertexReader->vtxMult;
    AVGnInt += vertexReader->npv ;
    AVGnInt50ns += vertexReader->npv50ns;
    AVGnEles += packedReader->nEles;
    AVGnMus += packedReader->nMus;
    AVGnChargedHadrons += packedReader->nChargedHadrons;
    AVGnLostTracks += nLostTracks;
    AVGnPhotons += packedReader->nPhotons;
    AVGnNeutralHadrons += packedReader->nNeutralHadrons;
  }

  nEventsInLumi++;
  theTree->Fill();
}


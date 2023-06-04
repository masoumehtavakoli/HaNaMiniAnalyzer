#include "Haamm/HaNaMiniAnalyzer/interface/HaNaBaseMiniAnalyzer.h"

#include <iostream>
#include "TTree.h"


using namespace std;


class SimplePUAnalyzer : public HaNaBaseMiniAnalyzer{
public:
  explicit SimplePUAnalyzer(const edm::ParameterSet& ps) :
    HaNaBaseMiniAnalyzer( ps ) {
    cout << "constructor" << endl;  
  };
  ~SimplePUAnalyzer(){
    cout << "destructor" << endl;
  };

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions){ HaNaBaseMiniAnalyzer::fillDescriptions( descriptions ); }
  Histograms* hnTruInt;
  TTree* theTree;

  virtual void beginJob() override{
    cout << "beginjob" << endl;    

    edm::Service<TFileService> fs;
    TFileDirectory treeDir = fs->mkdir( "Trees" );
    theTree = treeDir.make<TTree>("Events" , "Events");
    theTree->Branch("nGoodVertices" , &(vertexReader->nGoodVtx) );
    theTree->Branch("nVertices" , &(vertexReader->vtxMult));
    theTree->Branch("nVGoodVertices", &(vertexReader->nVeryGoodVtx));
    theTree->Branch("nVVGoodVertices", &vertexReader->nVVeryGoodVer) ;

    theTree->Branch("nEles" , &(packedReader->nEles));
    theTree->Branch("nMus" , &(packedReader->nMus));
    theTree->Branch("nChargedHadrons" , &(packedReader->nChargedHadrons));
    theTree->Branch("nNeutralHadrons" , &(packedReader->nNeutralHadrons));
    theTree->Branch("nPhotons" , &(packedReader->nPhotons));
    theTree->Branch("nParticles" , &(packedReader->nParticles));

    theTree->Branch("Pt" , &packedReader->Pt , "Pt[nParticles]/F");
    theTree->Branch("P" , &packedReader->P , "P[nParticles]/F");
    theTree->Branch("Phi" , &packedReader->Phi , "Phi[nParticles]/F");
    theTree->Branch("Eta" , &packedReader->Eta , "Eta[nParticles]/F");
    theTree->Branch("Charge" , &packedReader->Charge , "Charge[nParticles]/I");
    theTree->Branch("dxy" , &packedReader->dxy , "dxy[nParticles]/F");
    theTree->Branch("dz" , &packedReader->dz , "dz[nParticles]/F");
    theTree->Branch("Energy" , &packedReader->Energy , "Energy[nParticles]/F");
    theTree->Branch("Type" , &packedReader->type , "Type[nParticles]/I");

    theTree->Branch("nInt" , &(vertexReader->npv));
    theTree->Branch("nInt50ns" , &(vertexReader->npv50ns) );

  };
  virtual void analyze(const edm::Event& iEvent, const edm::EventSetup&) override{

    //std::cout << "analyze1" << endl;
    double vertexOutput = vertexReader->Read( iEvent );
    if( vertexOutput < 0 ){
      return ;
    }
    //std::cout << "analyze2" << endl;
    packedReader->Read( iEvent );
    theTree->Fill();
  
    //std::cout << "analyze1" << endl;
    //if(!IsData){
    //  hnTruInt->Fill( vertexReader->npv  , 1.0 );
    //}
  }
};

DEFINE_FWK_MODULE(SimplePUAnalyzer);

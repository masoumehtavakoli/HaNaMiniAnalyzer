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

    //theTree->Branch("ndof",&vertexReader->ndof ,  "ndof[nVVGoodVertices]/D");

    theTree->Branch("nEles" , &(packedReader->nEles));
    theTree->Branch("nMus" , &(packedReader->nMus));
    theTree->Branch("nChargedHadrons" , &(packedReader->nChargedHadrons));
    theTree->Branch("nNeutralHadrons" , &(packedReader->nNeutralHadrons));
    theTree->Branch("nPhotons" , &(packedReader->nPhotons));

    theTree->Branch("ElesPt" , &packedReader->ElesPt , "ElesPt[nEles]/D");
    theTree->Branch("MusPt" , &packedReader->MusPt , "MusPt[nMus]/D");
    theTree->Branch("ChargedHadronsPt" , &packedReader->ChargedHadronsPt , "ChargedHadronsPt[nChargedHadrons]/D");
    theTree->Branch("NeutralHadronsPt" , &packedReader->NeutralHadronsPt , "NeutralHadronsPt[nNeutralHadrons]/D");
    theTree->Branch("PhotonsPt" , &packedReader->PhotonsPt , "PhotonsPt[nPhotons]/D");

    theTree->Branch("ElesP" , &packedReader->ElesP , "ElesP[nEles]/D");
    theTree->Branch("MusP" , &packedReader->MusP , "MusP[nMus]/D");
    theTree->Branch("ChargedHadronsP" , &packedReader->ChargedHadronsP , "ChargedHadronsP[nChargedHadrons]/D");
    theTree->Branch("NeutralHadronsP" , &packedReader->NeutralHadronsP , "NeutralHadronsP[nNeutralHadrons]/D");
    theTree->Branch("PhotonsP" , &packedReader->PhotonsP , "PhotonsP[nPhotons]/D");

    theTree->Branch("ElesTheta" , &packedReader->ElesTheta , "ElesTheta[nEles]/D");
    theTree->Branch("MusTheta" , &packedReader->MusTheta , "MusTheta[nMus]/D");
    theTree->Branch("ChargedHadronsTheta" , &packedReader->ChargedHadronsTheta , "ChargedHadronsTheta[nChargedHadrons]/D");
    theTree->Branch("NeutralHadronsTheta" , &packedReader->NeutralHadronsTheta , "NeutralHadronsTheta[nNeutralHadrons]/D");
    theTree->Branch("PhotonsTheta" , &packedReader->PhotonsTheta , "PhotonsTheta[nPhotons]/D");

    theTree->Branch("ElesPhi" , &packedReader->ElesPhi , "ElesPhi[nEles]/D");
    theTree->Branch("MusPhi" , &packedReader->MusPhi , "MusPhi[nMus]/D");
    theTree->Branch("ChargedHadronsPhi" , &packedReader->ChargedHadronsPhi , "ChargedHadronsPhi[nChargedHadrons]/D");
    theTree->Branch("NeutralHadronsPhi" , &packedReader->NeutralHadronsPhi , "NeutralHadronsPhi[nNeutralHadrons]/D");
    theTree->Branch("PhotonsPhi" , &packedReader->PhotonsPhi , "PhotonsPhi[nPhotons]/D");

    theTree->Branch("ElesEta" , &packedReader->ElesEta , "ElesEta[nEles]/D");
    theTree->Branch("MusEta" , &packedReader->MusEta , "MusEta[nMus]/D");
    theTree->Branch("ChargedHadronsEta" , &packedReader->ChargedHadronsEta , "ChargedHadronsEta[nChargedHadrons]/D");
    theTree->Branch("NeutralHadronsEta" , &packedReader->NeutralHadronsEta , "NeutralHadronsEta[nNeutralHadrons]/D");
    theTree->Branch("PhotonsEta" , &packedReader->PhotonsEta , "PhotonsEta[nPhotons]/D");

    theTree->Branch("ElesCharge" , &packedReader->ElesCharge , "ElesCharge[nEles]/I");
    theTree->Branch("MusCharge" , &packedReader->MusCharge , "MusCharge[nMus]/I");
    theTree->Branch("ChargedHadronsCharge" , &packedReader->ChargedHadronsCharge , "ChargedHadronsCharge[nChargedHadrons]/I");
    theTree->Branch("NeutralHadronsCharge" , &packedReader->NeutralHadronsCharge , "NeutralHadronsCharge[nNeutralHadrons]/I");
    theTree->Branch("PhotonsCharge" , &packedReader->PhotonsCharge , "PhotonsCharge[nPhotons]/I");

    theTree->Branch("ElesRapidity" , &packedReader->ElesRapidity , "ElesRapidity[nEles]/D");
    theTree->Branch("MusRapidity" , &packedReader->MusRapidity , "MusRapidity[nMus]/D");
    theTree->Branch("ChargedHadronsRapidity" , &packedReader->ChargedHadronsRapidity , "ChargedHadronsRapidity[nChargedHadrons]/D");
    theTree->Branch("NeutralHadronsRapidity" , &packedReader->NeutralHadronsRapidity , "NeutralHadronsRapidity[nNeutralHadrons]/D");
    theTree->Branch("PhotonsRapidity" , &packedReader->PhotonsRapidity , "PhotonsRapidity[nPhotons]/D");

    theTree->Branch("Eles_dxy" , &packedReader->Eles_dxy , "Eles_dxy[nEles]/F");
    theTree->Branch("Mus_dxy" , &packedReader->Mus_dxy , "Mus_dxy[nMus]/F");
    theTree->Branch("ChargedHadrons_dxy" , &packedReader->ChargedHadrons_dxy , "ChargedHadrons_dxy[nChargedHadrons]/F");
    theTree->Branch("NeutralHadrons_dxy" , &packedReader->NeutralHadrons_dxy , "NeutralHadrons_dxy[nNeutralHadrons]/F");
    theTree->Branch("Photons_dxy" , &packedReader->Photons_dxy , "Photons_dxy[nPhotons]/F");

    theTree->Branch("Eles_dz" , &packedReader->Eles_dz , "Eles_dz[nEles]/F");
    theTree->Branch("Mus_dz" , &packedReader->Mus_dz , "Mus_dz[nMus]/F");
    theTree->Branch("ChargedHadrons_dz" , &packedReader->ChargedHadrons_dz , "ChargedHadrons_dz[nChargedHadrons]/F");
    theTree->Branch("NeutralHadrons_dz" , &packedReader->NeutralHadrons_dz , "NeutralHadrons_dz[nNeutralHadrons]/F");
    theTree->Branch("Photons_dz" , &packedReader->Photons_dz , "Photons_dz[nPhotons]/F");

    //    theTree->Branch("ElesMass" , &packedReader->ElesMass , "ElesP[nEles]/D");
    //    theTree->Branch("MusMass" , &packedReader->MusMass , "MusMass[nMus]/D");
    //    theTree->Branch("ChargedHadronsMass" , &packedReader->ChargedHadronsMass , "ChargedHadronsMass[nChargedHadrons]/D");
    //    theTree->Branch("NeutralHadronsMass" , &packedReader->NeutralHadronsMass , "NeutralHadronsMass[nNeutralHadrons]/D");
    //    theTree->Branch("PhotonsMass" , &packedReader->PhotonsMass , "PhotonsMass[nPhotons]/D");

    theTree->Branch("ElesEnergy" , &packedReader->ElesEnergy , "ElesEnergy[nEles]/D");
    theTree->Branch("MusEnergy" , &packedReader->MusEnergy , "MusEnergy[nMus]/D");
    theTree->Branch("ChargedHadronsEnergy" , &packedReader->ChargedHadronsEnergy , "ChargedHadronsEnergy[nChargedHadrons]/D");
    theTree->Branch("NeutralHadronsEnergy" , &packedReader->NeutralHadronsEnergy , "NeutralHadronsEnergy[nNeutralHadrons]/D");
    theTree->Branch("PhotonsEnergy" , &packedReader->PhotonsEnergy , "PhotonsEnergy[nPhotons]/D");

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



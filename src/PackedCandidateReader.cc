

#include "Haamm/HaNaMiniAnalyzer/interface/PackedCandidateReader.h"

PackedCandidateReader::PackedCandidateReader( edm::ParameterSet const& iPS, edm::ConsumesCollector && iC) :
  BaseEventReader< pat::PackedCandidateCollection >( iPS , &iC )
{
  
}

double PackedCandidateReader::Read( const edm::Event& iEvent ){
  BaseEventReader< pat::PackedCandidateCollection >::Read( iEvent );
  
  nNeutralHadrons = nPhotons = nEles = nMus = nChargedHadrons = 0;

  
  for(auto cand : *handle){
    int id = abs(cand.pdgId());
    if( id == 11 ){
      ElesPt[ nEles ] = cand.pt();
      ElesEta[ nEles ] = cand.eta();
      ElesCharge[ nEles ] = cand.charge();
      ElesRapidity[ nEles ] = cand.rapidity();
      ElesP[ nEles ] = cand.p();
      ElesTheta[ nEles ] = cand.theta();
      ElesPhi[ nEles ] = cand.phi();
      Eles_dxy[ nEles ] = cand.dxy();
      Eles_dz[ nEles ] = cand.dz();
      //      ElesMass[ nEles ] = cand.mass();
      ElesEnergy[ nEles ] = cand.energy();
      nEles ++;
    }else if(id == 13){
      MusPt[ nMus ] = cand.pt();
      MusEta[ nMus ] = cand.eta();
      MusCharge[ nMus ] = cand.charge();
      MusRapidity[ nMus ] = cand.rapidity();
      MusP[ nMus ] = cand.p();
      MusPhi[ nMus ] = cand.phi();
      MusTheta[ nMus ] = cand.theta();
      Mus_dxy[ nMus ] = cand.dxy();
      Mus_dz[ nMus ] = cand.dz();
      //      ElesMass[ nEles ] = cand.mass();
      MusEnergy[ nMus ] = cand.energy();
      nMus ++;
    }else if( id == 211 ){
      ChargedHadronsPt[ nChargedHadrons ] = cand.pt();
      ChargedHadronsEta[ nChargedHadrons ] = cand.eta();
      ChargedHadronsCharge[ nChargedHadrons ] = cand.charge();
      ChargedHadronsRapidity[ nChargedHadrons ] = cand.rapidity();
      ChargedHadronsP[ nChargedHadrons ] = cand.p();
      ChargedHadronsTheta[ nChargedHadrons ] = cand.theta();
      ChargedHadronsPhi[ nChargedHadrons ] = cand.phi();
      ChargedHadrons_dxy[ nChargedHadrons ] = cand.dxy();
      ChargedHadrons_dz[ nChargedHadrons ] = cand.dz();
      //      ChargedHadronsMass[ nChargedHadrons ] = cand.mass();
      ChargedHadronsEnergy[ nChargedHadrons ] = cand.energy();
      nChargedHadrons++;
    }else if( id == 130 ){
      NeutralHadronsPt[ nNeutralHadrons ] = cand.pt();
      NeutralHadronsEta[ nNeutralHadrons ] = cand.eta();
      NeutralHadronsCharge[ nNeutralHadrons  ] = cand.charge();
      NeutralHadronsRapidity[ nNeutralHadrons  ] = cand.rapidity();
      NeutralHadronsP[ nNeutralHadrons ] = cand.p();
      NeutralHadronsTheta[ nNeutralHadrons ] = cand.theta();
      NeutralHadronsPhi[ nNeutralHadrons ] = cand.phi();
      NeutralHadrons_dxy[ nNeutralHadrons ] = cand.dxy();
      NeutralHadrons_dz[ nNeutralHadrons ] = cand.dz();
      //      NeutralHadronsMass[ nNeutralHadrons ] = cand.mass();
      NeutralHadronsEnergy[ nNeutralHadrons  ] = cand.energy();
      nNeutralHadrons++;

    }else if( id == 22 ){
      PhotonsPt[ nPhotons ] = cand.pt();
      PhotonsEta[ nPhotons ] = cand.eta();
      PhotonsCharge[ nPhotons ] = cand.charge();
      PhotonsRapidity[ nPhotons ] = cand.rapidity();
      PhotonsP[ nPhotons ] = cand.p();
      PhotonsTheta[ nPhotons ] = cand.theta();
      PhotonsPhi[ nPhotons ] = cand.phi();
      Photons_dxy[ nPhotons ] = cand.dxy();
      Photons_dz[ nPhotons ] = cand.dz();
      //      PhotonsMass[ nPhotons ] = cand.mass();
      PhotonsEnergy[ nPhotons ] = cand.energy();
      nPhotons++;
    }else{
      //cout << "this particle id is missing :" << id  << endl;
      
    }
  }

  return (nEles+nMus+nChargedHadrons);

}

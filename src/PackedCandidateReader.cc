#include "Haamm/HaNaMiniAnalyzer/interface/PackedCandidateReader.h"

PackedCandidateReader::PackedCandidateReader( edm::ParameterSet const& iPS, edm::ConsumesCollector && iC) :
  BaseEventReader< pat::PackedCandidateCollection >( iPS , &iC )
{
  nParticles = nNeutralHadrons = nPhotons = nEles = nMus = nChargedHadrons = 0;
  memset(Pt, 0, sizeof(Pt));
  memset(Eta, 0, sizeof(Eta));
  memset(Charge, 0, sizeof(Charge));
  memset(Energy, 0, sizeof(Energy));
  memset(P, 0, sizeof(P));
  memset(Phi, 0, sizeof(Phi));
  memset(dxy, 0, sizeof(dxy));
  memset(dz, 0, sizeof(dz));
  memset(type, 0, sizeof(type));

}

double PackedCandidateReader::Read( const edm::Event& iEvent ){
  BaseEventReader< pat::PackedCandidateCollection >::Read( iEvent );

  nParticles = nNeutralHadrons = nPhotons = nEles = nMus = nChargedHadrons = 0;

  for(auto cand : *handle){
    int id = abs(cand.pdgId());
    if( id == 11 ){
      nEles ++;
    }else if(id == 13){
      nMus ++;
    }else if( id == 211 ){
      nChargedHadrons++;
    }else if( id == 130 ){
      nNeutralHadrons++;
    }else if( id == 22 ){
      nPhotons++;
    }

    Pt[nParticles] = cand.pt();
    Eta[nParticles] = cand.eta();
    Charge[nParticles] = cand.charge();
    Energy[nParticles] = cand.energy();
    P[nParticles] = cand.p();
    Phi[nParticles] = cand.phi();
    dxy[nParticles] = cand.dxy();
    dz[nParticles] = cand.dz();
    type[nParticles] = cand.pdgId();

    nParticles++;
  }

    
  return nParticles;

  }



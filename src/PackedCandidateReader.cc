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
    if( id == 11 )
      nEles ++;
    else if(id == 13)
      nMus ++;
    else if( id == 211 )
      nChargedHadrons++;
    else if( id == 130 )
      nNeutralHadrons++;
    else if( id == 22 )
      nPhotons++;

  }

  return (nEles+nMus+nChargedHadrons);

}


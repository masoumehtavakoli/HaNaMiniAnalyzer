#ifndef PackedCandidateReader_H
#define PackedCandidateReader_H


#include "BaseEventReader.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"

using namespace edm;
//using namespace reco;

class PackedCandidateReader : public BaseEventReader< pat::PackedCandidateCollection > {
public:
  PackedCandidateReader( edm::ParameterSet const& iPS, edm::ConsumesCollector && iC);
  double Read( const edm::Event& iEvent ) override;

  int nNeutralHadrons;
  int nPhotons;
  int nEles;
  int nMus;
  int nChargedHadrons;
  int size() const {
    return handle->size();
  }
private :

};

#endif

#ifndef PackedCandidateReader_H
#define PackedCandidateReader_H


#include "BaseEventReader.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include <bitset>
#define MAX_Particles 40000

using namespace edm;
//using namespace reco;

class PackedCandidateReader : public BaseEventReader< pat::PackedCandidateCollection > {
 public:
  PackedCandidateReader( edm::ParameterSet const& iPS, edm::ConsumesCollector && iC);
  double Read( const edm::Event& iEvent ) override;

  float Pt [MAX_Particles];
  float Eta [MAX_Particles];
  float Energy [MAX_Particles];
  float P [MAX_Particles];
  float Phi [MAX_Particles];
  float dxy [MAX_Particles];
  float dz [MAX_Particles];
  int type[MAX_Particles];
  int Charge [MAX_Particles];
  int nEles;
  int nMus;
  int nChargedHadrons;
  int nNeutralHadrons;
  int nPhotons;
  int nParticles;

  int size() const {
    return handle->size();
  }

};

#endif

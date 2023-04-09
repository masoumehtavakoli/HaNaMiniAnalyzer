#ifndef PackedCandidateReader_H
#define PackedCandidateReader_H


#include "BaseEventReader.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"

#define MAX_ELE 250
#define MAX_MUS 100
#define MAX_CHARGEHAD 2500
#define MAX_NEUTHAD 350
#define MAX_PHOT 250

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

  double ElesPt [ MAX_ELE ];
  double MusPt [MAX_MUS];
  double ChargedHadronsPt [MAX_CHARGEHAD];
  double NeutralHadronsPt [MAX_NEUTHAD];
  double PhotonsPt [MAX_PHOT];

  double ElesEta [MAX_ELE];
  double MusEta [MAX_MUS];
  double ChargedHadronsEta [MAX_CHARGEHAD];
  double NeutralHadronsEta [MAX_NEUTHAD];
  double PhotonsEta [MAX_PHOT];

  int ElesCharge [MAX_ELE];
  int MusCharge [MAX_MUS];
  int ChargedHadronsCharge [MAX_CHARGEHAD];
  int NeutralHadronsCharge [MAX_NEUTHAD];
  int PhotonsCharge [MAX_PHOT];

  double ElesEnergy [MAX_ELE];
  double MusEnergy [MAX_MUS];
  double ChargedHadronsEnergy [MAX_CHARGEHAD];
  double NeutralHadronsEnergy [MAX_NEUTHAD];
  double PhotonsEnergy [MAX_PHOT];

  //double ElesMass [MAX_ELE];                                                                                                                                                                       
  //  double MusMass [50];                                                                               
  //  double ChargedHadronsMass [2500];                                                                                                                                                                   
  //  double NeutralHadronsMass [350];                                                                                                                                                                    
  //  double PhotonsMass [MAX_ELE];
   
  double ElesRapidity [MAX_ELE];
  double MusRapidity [MAX_MUS];
  double ChargedHadronsRapidity [MAX_CHARGEHAD];
  double NeutralHadronsRapidity [MAX_NEUTHAD];
  double PhotonsRapidity [MAX_PHOT];

  double ElesP [MAX_ELE];
  double MusP [MAX_MUS];
  double ChargedHadronsP [MAX_CHARGEHAD];
  double NeutralHadronsP [MAX_NEUTHAD];
  double PhotonsP [MAX_PHOT];

  double ElesTheta [MAX_ELE];
  double MusTheta [MAX_MUS];
  double ChargedHadronsTheta [MAX_CHARGEHAD];
  double NeutralHadronsTheta [MAX_NEUTHAD];
  double PhotonsTheta [MAX_ELE];
  
  double ElesPhi [MAX_ELE];
  double MusPhi [MAX_MUS];
  double ChargedHadronsPhi [MAX_CHARGEHAD];
  double NeutralHadronsPhi [MAX_NEUTHAD];
  double PhotonsPhi [MAX_PHOT];

  float Eles_dxy [MAX_ELE];
  float Mus_dxy [MAX_MUS];
  float ChargedHadrons_dxy [MAX_CHARGEHAD];
  float NeutralHadrons_dxy [MAX_NEUTHAD];
  float Photons_dxy [MAX_PHOT];

  float Eles_dz [MAX_ELE];
  float Mus_dz [MAX_MUS];
  float ChargedHadrons_dz [MAX_CHARGEHAD];
  float NeutralHadrons_dz [MAX_NEUTHAD];
  float Photons_dz [MAX_PHOT];

  int size() const {
    return handle->size();
  }
 private :

};

#endif

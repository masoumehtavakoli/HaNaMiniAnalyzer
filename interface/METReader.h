#ifndef METReader_H
#define METReader_H

#include "BaseEventReader.h"
#include "DataFormats/PatCandidates/interface/MET.h"
#include "DataFormats/PatCandidates/interface/Jet.h"

using namespace edm;
using namespace reco;

class METReader : public BaseEventReader< pat::METCollection > {
public:
  METReader( edm::ParameterSet const& iPS, edm::ConsumesCollector && iC , bool isData);

  double Read( const edm::Event& iEvent , pat::JetCollection* newJets = NULL );
  double ReadMetSig (const edm::Event& iEvent);
  reco::Candidate::LorentzVector met;
  reco::Candidate::LorentzVector oldht;
  reco::Candidate::LorentzVector newht;
private :
  double MetCut;
  
  reco::Candidate::LorentzVector HT4( pat::JetCollection jets );

  bool ReadOldJets ;
  edm::Handle<pat::JetCollection> oldjets;
  edm::EDGetTokenT<pat::JetCollection> oldjetToken_;
  edm::Handle<double> metsig;
  edm::EDGetTokenT<double> metsigToken_;//("METSignificance:METSignificance:HaNa");
};

#endif

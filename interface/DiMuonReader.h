#ifndef DiMuonReader_H
#define DiMuonReader_H

#include "BaseEventReader.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/MuonReco/interface/MuonSelectors.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "PhysicsTools/PatUtils/interface/PATDiObjectProxy.h"

#include "TH2.h"
#include "TROOT.h"
#include "TFile.h"

using namespace edm;
using namespace pat;

class DiMuonReader : public BaseEventReader< pat::MuonCollection > {
public:
  DiMuonReader( edm::ParameterSet const& iConfig, edm::ConsumesCollector && iC , bool isData , string SetupDir);
  enum SelectionStatus{
    LessThan2Muons,
    NoPairWithChargeReq,
    LowMassPair,
    UnderTheZPeak,
    Pass
  };
  SelectionStatus Read( const edm::Event& iEvent, const reco::Vertex* PV );

  pat::MuonCollection goodMus;
  pat::MuonCollection goodMusOS;
  pat::DiObjectProxy DiMuon;
  double W;

private :
  /* MUON SF TOOLS */
  double MuonSFMedium( double etaL , double ptL , double etaSL , double ptSL );
  double MuonSFLoose( double etaL , double ptL , double etaSL , double ptSL );
  TH2* hMuSFID;
  TH2* hMuSFIso;
  /* MUON SF TOOLS */

  /* MUON SELECTION PARAMS */
  double MuonLeadingPtCut, MuonSubLeadingPtCut , MuonIsoCut, MuonEtaCut , DiMuLowMassCut, DiMuZMassWindow ;
  int MuonID , DiMuCharge;
  bool IsData, isHamb;
  /* MUON SELECTION PARAMS */
};
#endif

#ifndef Category_H
#define Category_H


#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include <vector>
#include "Histograms.h"

using namespace std;

class Category {
public:
  TString Name;

  Category( TString name, TString SampleName);

  void Fill( std::vector<float> , double , double  );
  Histograms* hCutFlowTable;
  Histograms* hNPV_pv;
  Histograms* hMuMult;
  Histograms* hJetMult;
  Histograms* hBJetMult;
  Histograms* hNPV_final;
  Histograms* hMuPt;
  Histograms* hMuEta;
  Histograms* hLeadMuPt;
  Histograms* hLeadMuEta;
  Histograms* hSubLeadMuPt;
  Histograms* hSubLeadMuEta;
  Histograms* hDiMuMass;
  Histograms* hDiMuPt;
  Histograms* hDiMuDr;
  Histograms* hJetPt;
  Histograms* hJetEta;
  Histograms* hJetBTag;
  Histograms* hLeadJetPt;
  Histograms* hLeadJetEta;
  Histograms* hLeadJetBTag;
  Histograms* hSubLeadJetPt;
  Histograms* hSubLeadJetEta;
  Histograms* hSubLeadJetBTag;
  Histograms* hDiBJetMass;
  Histograms* hDiBJetPt;
  Histograms* hDiBJetDr;
  Histograms* hFourBodyMass;
  Histograms* hFourBodyPt;
  Histograms* hDiffMassMuB;
  Histograms* hRelDiffMassMuB;
  Histograms* hMET;
  Histograms* hMETSignificance;
};
#endif

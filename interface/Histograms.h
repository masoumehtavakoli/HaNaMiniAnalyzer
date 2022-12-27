#ifndef Histograms_H
#define Histograms_H


#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "TH1D.h"

using namespace std;

class Histograms {
public:
  TH1* theHist;
  TH1* theHistNoW;
  TString SampleName;
  TString PropName;
  TString SelectionLevel;

  Histograms( TString samplename , TString propname , int nbins , double from , double to );
  Histograms( TString samplename , TString propname , int nbins , double* bins );

  Histograms( TString selLev , TString samplename , TString propname , int nbins , double from , double to );
  Histograms( TString selLev , TString samplename , TString propname , int nbins , double* bins );

  void Fill( double v , double w=1.0 );
  
};
#endif

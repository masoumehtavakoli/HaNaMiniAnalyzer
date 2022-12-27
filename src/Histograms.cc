#include "../interface/Histograms.h"

Histograms::Histograms( TString samplename , TString propname , int nbins , double from , double to ) : SampleName(samplename),
													PropName(propname),
													SelectionLevel(""){
  edm::Service<TFileService> fs;
  TFileDirectory subDir = fs->mkdir( PropName.Data() );
  theHist = subDir.make<TH1D>( propname + "_" + samplename , propname , nbins , from , to );
  theHistNoW = subDir.make<TH1D>( propname + "_NoW_" + samplename , propname , nbins , from , to );
}

Histograms::Histograms( TString samplename , TString propname , int nbins , double* bins) : SampleName(samplename),
											    PropName(propname),
											    SelectionLevel(""){
  edm::Service<TFileService> fs;
  TFileDirectory subDir = fs->mkdir( PropName.Data() );
  theHist = subDir.make<TH1D>( propname + "_" + samplename , propname , nbins , bins );
  theHistNoW = subDir.make<TH1D>( propname + "_NoW_" + samplename , propname , nbins , bins );
}

Histograms::Histograms( TString selLev , TString samplename , TString propname , int nbins , double from , double to ) : SampleName(samplename),
															 PropName(propname),
															 SelectionLevel(selLev){
  edm::Service<TFileService> fs;
  TFileDirectory catDir = fs->mkdir( SelectionLevel.Data() );
  TFileDirectory subDir = catDir.mkdir( PropName.Data() );
  theHist = subDir.make<TH1D>( selLev + "_" + propname + "_" + samplename , propname , nbins , from , to );
  theHistNoW = subDir.make<TH1D>( selLev + "_" + propname + "_NoW_" + samplename , propname , nbins , from , to );
}

Histograms::Histograms( TString selLev , TString samplename , TString propname , int nbins , double* bins) : SampleName(samplename),
													     PropName(propname),
													     SelectionLevel(selLev){
  edm::Service<TFileService> fs;
  TFileDirectory catDir = fs->mkdir( SelectionLevel.Data() );
  TFileDirectory subDir = catDir.mkdir( PropName.Data() );
  theHist = subDir.make<TH1D>( selLev + "_" + propname + "_" + samplename , propname , nbins , bins );
  theHistNoW = subDir.make<TH1D>( selLev + "_" + propname + "_NoW_" + samplename , propname , nbins , bins );
}


void Histograms::Fill( double v , double w ){
  theHist->Fill( v , w );
  theHistNoW->Fill( v , 1.0 ) ; //w == 0 ? 1 : (w/fabs(w)) );
}


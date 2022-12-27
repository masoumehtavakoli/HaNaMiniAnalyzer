#ifndef VertexReader_H
#define VertexReader_H

#include "BaseEventReader.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "PhysicsTools/Utilities/interface/LumiReWeighting.h"

#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"

using namespace edm;
using namespace reco;

class VertexReader : public BaseEventReader< VertexCollection > {
public:
  VertexReader( edm::ParameterSet const& iPS, edm::ConsumesCollector && iC , bool isData , string SetupDir) ;

  double Read( const edm::Event& iEvent ) override ;

  double puWeight;
  int vtxMult;
  int nGoodVtx;
  int npv;
  int npv50ns;

  int nTracksPV;
  int nTracksW05PV;

  int nTracksAll;
  int nTracksW05All;
 
  const reco::Vertex * PV();
private :
  bool IsData ;
  bool CheckVertex(VertexCollection::value_type vtx);

  edm::Handle<std::vector< PileupSummaryInfo > >  PupInfo;
  edm::EDGetTokenT< std::vector< PileupSummaryInfo > > PileupToken_;
  edm::LumiReWeighting LumiWeights_;
};

#endif

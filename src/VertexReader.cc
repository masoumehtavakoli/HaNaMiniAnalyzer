#include "Haamm/HaNaMiniAnalyzer/interface/VertexReader.h"

VertexReader::VertexReader( edm::ParameterSet const& iPS, edm::ConsumesCollector && iC , bool isData , string SetupDir) :
    BaseEventReader< VertexCollection >( iPS , &iC ),
    IsData( isData )
{
  if( !IsData ){
    PileupToken_ = iC.consumes<std::vector<PileupSummaryInfo>>(iPS.getParameter<edm::InputTag>("pileupSrc")) ;
    //LumiWeights_ = edm::LumiReWeighting( SetupDir + "/pileUpMC.root" ,
    //SetupDir + "/pileUpData.root", 
    //std::string("pileup"), std::string("pileup") );
  }
}

bool VertexReader::CheckVertex(VertexCollection::value_type vtx){ 
  if( !IsData ) return true;
  //cout << vtx.position().z() << " " << vtx.ndof() << "  " << vtx.position() << endl;
  return (fabs(vtx.position().z()) < 24.0 &&
	  vtx.ndof() > 4.0 &&
	  vtx.position().rho() < 2.0 ); 
};

const reco::Vertex * VertexReader::PV(){
  return &( handle->front() );
};

double VertexReader::Read( const edm::Event& iEvent ){
    BaseEventReader< VertexCollection >::Read( iEvent );
    vtxMult = handle->size();
    nGoodVtx = 0;
    auto vtx = handle->front();
    //cout << handle->size() << endl;
    if(!CheckVertex(vtx) )
      return -1.0;
    else{
      nTracksPV = vtx.tracksSize();
      nTracksW05PV = vtx.nTracks(0.5);

      nTracksAll = nTracksW05All = 0;
    }

    for( auto vtx1 : *handle )
      if( CheckVertex(vtx1) ){
	nGoodVtx++;

	nTracksAll += vtx.tracksSize();
	nTracksW05All += vtx.nTracks(0.5);
      }

    if( !IsData ){
      iEvent.getByToken(PileupToken_, PupInfo);
      // auto PVI = PupInfo->begin();
      // for(; PVI != PupInfo->end(); ++PVI) {
      //   puBX->push_back(  PVI->getBunchCrossing() ); 
      //   puNInt->push_back( PVI->getPU_NumInteractions() );
      // }
      npv = -1;
      npv50ns = -1;
      
      for(std::vector<PileupSummaryInfo>::const_iterator PVI = PupInfo->begin(); PVI != PupInfo->end(); ++PVI) {
	
	int BX = PVI->getBunchCrossing();
 
	if(BX == 0) { 
	  npv = PVI->getPU_NumInteractions();
	}
 
	if(BX == 1) { 
	  npv50ns = PVI->getPU_NumInteractions();
	}
	
      }
      puWeight = 1; //LumiWeights_.weight(PupInfo->begin()->getTrueNumInteractions());
    }else
      puWeight = 1.0;
    
    return puWeight;
}

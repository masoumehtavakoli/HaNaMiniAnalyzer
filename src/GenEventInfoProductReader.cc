#include "../interface/GenEventInfoProductReader.h"

GenEventInfoProductReader::GenEventInfoProductReader( edm::ParameterSet const& iPS, edm::ConsumesCollector && iC) :
  BaseEventReader< GenEventInfoProduct >( iPS , &iC )
{
  
}

double GenEventInfoProductReader::Read( const edm::Event& iEvent ){
  BaseEventReader< GenEventInfoProduct >::Read( iEvent );
  Weight = handle->weight();
  WeightSign = (handle->weight() > 0) ? 1.0 : -1.0 ; 
  return WeightSign;
}


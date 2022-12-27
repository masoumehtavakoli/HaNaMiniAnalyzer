#include "Haamm/HaNaMiniAnalyzer/interface/LHEEventReader.h"

LHEEventReader::LHEEventReader( edm::ParameterSet const& iPS, edm::ConsumesCollector && iC) :
  BaseEventReader< LHEEventProduct >( iPS , &iC )
{
  
}

double LHEEventReader::Read( const edm::Event& iEvent ){
  BaseEventReader< LHEEventProduct >::Read( iEvent );
  WeightSign = (handle->hepeup().XWGTUP > 0) ? 1.0 : -1.0 ; 
  return WeightSign;
}


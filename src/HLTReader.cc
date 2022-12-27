#include "Haamm/HaNaMiniAnalyzer/interface/HLTReader.h"

using namespace edm;
using namespace std;

HLTReader::HLTReader( edm::ParameterSet const& iPS, edm::ConsumesCollector && iC) :
  BaseEventReader< TriggerResults >( iPS , &iC ),
  HLT_To_Or ( iPS.getParameter< vector<string> >("HLT_To_Or" ) )
{
  
}

double HLTReader::Read( const edm::Event& iEvent ){
    BaseEventReader< TriggerResults >::Read( iEvent );
    const edm::TriggerNames& trigNames = iEvent.triggerNames(*handle);
    passTrig = (HLT_To_Or.size() == 0);
    for(auto hlt : HLT_To_Or){
      uint hltindex = trigNames.triggerIndex(hlt);
      if( hltindex < trigNames.size() )
	passTrig |= handle->accept(hltindex);
    }
    if( !passTrig )
      return -1.0;
    else
      return 1.0;
  }

#ifndef HLTReader_H
#define HLTReader_H

#include "BaseEventReader.h"

#include "DataFormats/Common/interface/TriggerResults.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include <vector>

using namespace edm;
using namespace std;

class HLTReader : public BaseEventReader< TriggerResults > {
public:
  HLTReader( edm::ParameterSet const& iPS, edm::ConsumesCollector && iC);

  double Read( const edm::Event& iEvent ) override;
  bool passTrig;
private :
  std::vector<std::string> HLT_To_Or;
};

#endif

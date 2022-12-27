#ifndef GenEventInfoProductReader_H
#define GenEventInfoProductReader_H


#include "BaseEventReader.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

using namespace edm;
//using namespace reco;

class GenEventInfoProductReader : public BaseEventReader< GenEventInfoProduct > {
public:
  GenEventInfoProductReader( edm::ParameterSet const& iPS, edm::ConsumesCollector && iC);
  double Read( const edm::Event& iEvent ) override;
  double WeightSign;
  double Weight;
private :

};

#endif

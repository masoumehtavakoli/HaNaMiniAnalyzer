#ifndef TtGenEvent_h
#define TtGenEvent_h

#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include <vector>
#include <TMath.h>
#include <Math/VectorUtil.h>
#include "TVector2.h"
#include "TLorentzVector.h"
using namespace std;
class TopDecayChain {
public:
  TopDecayChain(){};
  void Set(const reco::GenParticle* _Top,
		const reco::GenParticle* _W,
		const reco::GenParticle* _b,
		const reco::GenParticle* _Lepton,
		const reco::GenParticle* _Neutrino ){
    Top = _Top;
    W = _W;
    b = _b;
    Lepton = _Lepton;
    Neutrino = _Neutrino;
  }

  const reco::GenParticle* Top;
  const reco::GenParticle* W;
  const reco::GenParticle* b;  
  const reco::GenParticle* Lepton;
  const reco::GenParticle* Neutrino;
  TLorentzVector TopP4(){
	TLorentzVector ret(Top->px(),Top->py(), Top->pz(), Top->energy());
	return ret;
  }
};

class ZDecayChain{
public:
  ZDecayChain(){};
  void Set(const reco::GenParticle* _Z, const reco::GenParticle* _dplus, const reco::GenParticle* _dminus){
   Z = _Z;
   dplus = _dplus;
   dminus = _dminus;
  };
  const reco::GenParticle* Z;
  const reco::GenParticle* dplus;
  const reco::GenParticle* dminus;
  TLorentzVector ZP4(){
	TLorentzVector ret(Z->px(),Z->py(), Z->pz(), Z->energy());
	return ret;
  }
};

class TtZ {
public:
  TtZ( const TtZ* ttbar , bool JustTransverse );
  TtZ( const std::vector<reco::GenParticle>* );
  ~TtZ();
  int getLastCopy( const std::vector<reco::GenParticle>* gens, int pdgId , int parentId=0 , bool beforeFSR = false , bool noCheckLastCopy = false );


  

  TopDecayChain Top;
  TopDecayChain TopBar;
  ZDecayChain Z;
  bool isSet;

  TLorentzVector ttZP4(){
     TLorentzVector ret(0,0,0,0);
     ret.SetX(Top.Top->px()+TopBar.Top->px()+Z.Z->px());
     ret.SetY(Top.Top->py()+TopBar.Top->py()+Z.Z->py());
     ret.SetZ(Top.Top->pz()+TopBar.Top->pz()+Z.Z->pz());
     ret.SetT(Top.Top->energy()+TopBar.Top->energy()+Z.Z->energy());
     return ret;
  }

  TLorentzVector InttZ(const reco::GenParticle* input){
     TLorentzVector ret(input->px(), input->py(), input->pz(), input->energy());
     ret.Boost(-this->ttZP4().BoostVector());     
     return ret;
  }

  //http://arxiv.org/pdf/0907.2191v2.pdf
  //Not clear what is the boost convention. The way I understand it is to boost all to ttZ and then boost leptons to top!
  //Optimal frame  
  double CosTheta(int sign, bool optimal = true){
    if(sign == 0) return -100;
    TLorentzVector topInttZ = InttZ(Top.Top);
    TLorentzVector ltopInttZ = InttZ(Top.Lepton);
    TLorentzVector lZInttZ = InttZ(Z.dminus);
    if(sign < 0){
	topInttZ = InttZ(TopBar.Top);
        ltopInttZ = InttZ(TopBar.Lepton);
    }
    ltopInttZ.Boost(-topInttZ.BoostVector());
    lZInttZ.Boost(-topInttZ.BoostVector());
    double ret = -100;
    if(optimal){
       ret = ROOT::Math::VectorUtil::CosTheta(ltopInttZ,lZInttZ);
    } else {
       ret = ROOT::Math::VectorUtil::CosTheta(ltopInttZ,topInttZ);
    }
    return ret;
  }
};


/*class TZ : {
public:
  TZ( const TZ* ttbar , bool JustTransverse );
  TZ( const std::vector<reco::GenParticle>* );
  ~TZ();
  int getLastCopy( const std::vector<reco::GenParticle>* gens, int pdgId , int parentId=0 , bool beforeFSR = false , bool noCheckLastCopy = false );
}*/
#endif


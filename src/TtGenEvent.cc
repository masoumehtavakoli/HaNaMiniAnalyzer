#include "Haamm/HaNaMiniAnalyzer/interface/TtGenEvent.h"
#include <iostream>
using namespace std;
TtZ::~TtZ(){

}

TtZ::TtZ( const TtZ* ttbar , bool JustTransverse  ){
  isSet = ttbar->isSet;
  if( !isSet )
    return ;

  if( !JustTransverse ){
    Top = ttbar->Top;
    TopBar = ttbar->TopBar;
  }

}
TtZ::TtZ( const std::vector<reco::GenParticle>* gen  )
{
  //cout<< "New Event +++++++++++++++++++++++++ "<<endl;
  int top = getLastCopy( gen , 6 );
  int topbar = getLastCopy( gen , -6 );

  int z = getLastCopy( gen , 23 );
  //int mz2 = gen->at(mz2).motherId(0);
  
  //cout<<mz1<<"\t"<<mz2<<endl;

  int wm = getLastCopy( gen , -24 , -6 , true , true );
  int wp = getLastCopy( gen , 24 , 6 , true , true);

  int lm = getLastCopy( gen , 11 , -24 , false, true);
  int neutrinobar = getLastCopy( gen , -12 , -24, false, true );

  int lp = getLastCopy( gen , -11 , 24, false , true );
  int neutrino = getLastCopy( gen , 12 , 24, false , true );

  if(lm < 0){
    lm = getLastCopy( gen , 13 , -24, false, true );
    neutrinobar = getLastCopy( gen , -14 , -24, false , true );
  }
  if(lp < 0){
    lp = getLastCopy( gen , -13 , 24, false, true );
    neutrino = getLastCopy( gen , 14 , 24, false, true );
  }

  int b = getLastCopy( gen , 5 , 6 , false, true );

  int bbar = getLastCopy( gen , -5 , -6 , false, true );

  int lmz = getLastCopy( gen , 11 , 23 , false, true);
  int lpz = getLastCopy( gen , -11 , 23, false , true );

  if(lmz < 0){
    lmz = getLastCopy( gen , 13 , 23, false, true );
  }
  if(lpz < 0){
    lpz = getLastCopy( gen , -13 , 23, false, true );
  }


  if( lm < 0 || lp < 0 || lmz < 0 || lpz < 0){
    isSet = false;
    return;
  }
  
  //std::cout << top << "->" << b << "+(" << wm << "->" << lm << "," << neutrinobar << ") ,,,  " ;
  //std::cout << topbar << "->" << bbar << "+(" << wp << "->" << lp << "," << neutrino << ")" << std::endl ;

  TopBar.Set(
	     &(gen->at( topbar )),
	     &(gen->at( wp )),
	     &(gen->at(bbar)),
	     &(gen->at( lp )),
	     &(gen->at( neutrino )) );
 
  Top.Set(
	  &(gen->at( top )),
	  &(gen->at( wm )),
	  &(gen->at( b )),
	  &(gen->at( lm )),
	  &(gen->at( neutrinobar )) );

  Z.Set(
          &(gen->at( z )),
          &(gen->at( lpz )),
          &(gen->at( lmz ))	
  );

  isSet = true;
}

int TtZ::getLastCopy(const std::vector<reco::GenParticle>* gens, int pdgId , int parentId , bool beforeFSR , bool noCheckLastCopy ){
  int index=-1;
  for(auto genPart : *gens ){
    index ++ ;
    //cout<<genPart.status() <<"\t"<<genPart.pdgId()<<endl;
    //if(genPart.status() != 1 ) continue;

    int pdgid = genPart.pdgId();
    if( pdgid != pdgId )
      continue;
    /*if(fabs(pdgId) == 23){
        cout<< "New Z! ============ "<<endl;
	cout<< "\tDaughters: "<<genPart.numberOfDaughters()<<endl;
	for(unsigned int i = 0; i < genPart.numberOfDaughters(); i++)
		if(genPart.daughter(i) != NULL )
			cout<<"\t"<<genPart.daughter(i)->pdgId()<<endl;
    	cout<< "\tMothers: "<<genPart.numberOfMothers() <<endl;
	for(unsigned int i = 0; i < genPart.numberOfDaughters(); i++)
		if(genPart.mother(i) != NULL )
			cout<<"\t"<<genPart.mother(i)->pdgId()<<endl;
    }*/
    if( parentId != 0 )
      if( genPart.mother()->pdgId() != parentId )
	continue;
    if( noCheckLastCopy )
      return index;
    else if( beforeFSR ){
      if( genPart.isLastCopyBeforeFSR() )
	return index;
    }else if( genPart.isLastCopy() )
      return index;
  }
  return -1;
}

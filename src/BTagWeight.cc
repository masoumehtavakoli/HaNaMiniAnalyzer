#include "Haamm/HaNaMiniAnalyzer/interface/BTagWeight.h"


/*float BTagWeight::weight(pat::JetCollection jets){
    float pMC = 1;
    float pData = 1;
    for (auto j : jets){
	float eff = this->MCTagEfficiency(j,WPT);
	float sf= this->TagScaleFactor(j);
	if(j.bDiscriminator(algo)>bTagMapCSVv2[WPT] ){
		pMC*=eff;
		pData*=sf*eff;
	}else{
		pMC*=(1-eff);
		pData*=(1-sf*eff);
	}
    }
    return pData/pMC;
}*/

float BTagWeight::weight(pat::JetCollection jets/*, int ntag*/){
	//if (!filter(ntag)){
      		//   std::cout << "nThis event should not pass the selection, what is it doing here?" << std::endl;
        //	return 0;
	//}
	int njetTags = jets.size();
	int comb = 1 << njetTags;
	float pMC = 0;
	float pData = 0;
	for (int i = 0; i < comb; i++){
		float mc = 1.;
      		float data = 1.;
      		int ntagged = 0;
      		for (int j = 0; j < njetTags; j++){
	  		bool tagged = ((i >> j) & 0x1) == 1;
			float eff = this->MCTagEfficiency(jets[j],WPT);
			float sf = this->TagScaleFactor(jets[j]);
	  		if (tagged){
	      			ntagged++;
				mc *= eff;
				data *= (eff*sf);
				//mc *= jetTags[j].eff;
				//data *= jetTags[j].eff * jetTags[j].sf;
			} else {
			        mc*=(1-eff);
                		data*=(1-sf*eff);
				//mc *= (1. - jetTags[j].eff);
				//data *= (1. - jetTags[j].eff * jetTags[j].sf);
            		}
        	}

      		if (filter(ntagged)){
			//std::cout << mc << " " << data << endl;
			pMC += mc;
			pData += data;
	        }
	}
	if (pMC == 0) return 0;
	return pData / pMC;
}



//*************************************************************************
//DONT USE !!!!! METHOD INCOMPLETE ****************************************
//*************************************************************************
float BTagWeight::weightExclusive(pat::JetCollection jets){
//This function takes into account cases where you have n b-tags and m vetoes, but they have different thresholds.
    if(WPL == -1){
	std::cout<<"FATAL ERROR: Provide the second btag WP!!!!"<<std::endl;
	return 0;
    } 
    float pMC = 1;
    float pData = 1;
    for (auto j : jets){
	float effL = this->MCTagEfficiency(j,WPL);
	float sfL= this->TagScaleFactor(j,(WPL != -1));
	float effT = this->MCTagEfficiency(j,WPT);
	float sfT= this->TagScaleFactor(j);
	if(j.bDiscriminator(algo) > bTagMapCSVv2[WPT]){
		pMC*=effT;
		pData*=sfT*effT;
	}else if (j.bDiscriminator(algo) > bTagMapCSVv2[WPL]){
		pMC*=(effL-effT);
		pData*=fabs(sfL*effL - sfT*effT);
	} else {
		pMC*=(1-effL);
		pData*=(1-sfL*effL);
	}
    }
    
    return pData/pMC;
}
//*************************************************************************

float BTagWeight::MCTagEfficiency(pat::Jet jet, int WP){
  int flavor = fabs(jet.hadronFlavour());
  if(flavor == 5){
    if(WP==0) return 0.38; //L
    if(WP==1) return 0.58; //M
    if(WP==2) return 0.755;//T
  }
  if(flavor == 4){
    if(WP==0) return 0.015; //L
    if(WP==1) return 0.08; //M
    if(WP==2) return 0.28;//T
  }
  if(flavor != 4){
    if(WP==0) return 0.0008; //L
    if(WP==1) return 0.007; //M
    if(WP==2) return 0.079;//T
 }
  return 1.0;
}

float BTagWeight::TagScaleFactor(pat::Jet jet, bool LooseWP ){

	//	float MinJetPt = 20.;
	//	float MaxBJetPt = 670., MaxLJetPt = 1000.;
	//      float JetPt = jet.pt(); bool DoubleUncertainty = false;
	//	int flavour = fabs(jet.hadronFlavour());
	// if(flavour == 5) flavour = BTagEntry::FLAV_B;
	// else if(flavour == 4) flavour = BTagEntry::FLAV_C;
	// else flavour = BTagEntry::FLAV_UDSG;
	
	// if(flavour != BTagEntry::FLAV_UDSG){
	//    if (JetPt>MaxBJetPt)  { // use MaxLJetPt for  light jets
        // 	JetPt = MaxBJetPt; 
        // 	DoubleUncertainty = true;
      	//    }
	// } else {
	//    if (JetPt>MaxLJetPt)  { // use MaxLJetPt for  light jets
        //         JetPt = MaxBJetPt;
        //         DoubleUncertainty = true;
        //    }
	// }
	// if(JetPt<MinJetPt){
	//    JetPt = MinJetPt;
	//    DoubleUncertainty = true;
	// }

	float jet_scalefactor = 1;

	// if((BTagEntry::JetFlavor)flavour != BTagEntry::FLAV_UDSG){
	// 	jet_scalefactor = reader->eval((BTagEntry::JetFlavor)flavour, jet.eta(), JetPt); 
	// 	if(LooseWP)
	// 		jet_scalefactor = readerExc->eval((BTagEntry::JetFlavor)flavour, jet.eta(), JetPt);
	// } else {
	// 	jet_scalefactor = readerLight->eval((BTagEntry::JetFlavor)flavour, jet.eta(), JetPt);
	// 	if(LooseWP)
	// 		jet_scalefactor = readerExcLight->eval((BTagEntry::JetFlavor)flavour, jet.eta(), JetPt);
	// }


	// if(DoubleUncertainty && syst != 0){
	//         float jet_scalefactorCent = 1;
	// 	if((BTagEntry::JetFlavor)flavour != BTagEntry::FLAV_UDSG){
	// 		jet_scalefactorCent = readerCent->eval((BTagEntry::JetFlavor)flavour, jet.eta(), JetPt); 
	// 		if(LooseWP)
	// 			jet_scalefactorCent = readerCentExc->eval((BTagEntry::JetFlavor)flavour, jet.eta(), JetPt);
	// 	} else {
	// 		jet_scalefactorCent = readerCentLight->eval((BTagEntry::JetFlavor)flavour, jet.eta(), JetPt); 
	// 		if(LooseWP)
	// 			jet_scalefactorCent = readerCentExcLight->eval((BTagEntry::JetFlavor)flavour, jet.eta(), JetPt);
	// 	}
        //         jet_scalefactor = 2*(jet_scalefactor - jet_scalefactorCent) + jet_scalefactorCent; 
	// }
	return jet_scalefactor;
}


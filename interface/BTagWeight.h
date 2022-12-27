#ifndef BTagWeight_H
#define BTagWeight_H

//https://github.com/nfaltermann/ST_RunII_EA/blob/master/src/DMAnalysisTreeMaker.cc
//https://twiki.cern.ch/twiki/bin/view/CMS/BTagSFMethods    (method 1a)

#include <vector>
#include <iostream>
#include <string>

//#include "CondFormats/BTauObjects/interface/BTagCalibration.h"
//#include "CondFormats/BTauObjects/interface/BTagCalibrationReader.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
using namespace std;



/*
 *
 * enum OperatingPoint {
 *     OP_LOOSE=0,
 *     OP_MEDIUM=1,
 *     OP_TIGHT=2,
 *     OP_RESHAPING=3,
 *     };
 * enum JetFlavor {
 *     FLAV_B=0,
 *     FLAV_C=1,
 *     FLAV_UDSG=2,
 *     };
 *
 */



class BTagWeight
  {
  private:
    string algo;
    int WPT, WPL, minTag, maxTag;
    int syst;
    float bTagMapCSVv2[3];
  public:
    BTagWeight(string algorithm, int WPt, string setupDir, int mintag, int maxtag, double BLCut = 0.460, double BMCut = 0.800, 
	       double BTCut = 0.935, int WPl = -1, int systematics = 0): 
      algo(algorithm), WPT(WPt), WPL(WPl), minTag(mintag), maxTag(maxtag), syst(systematics) //,readerExc(0),readerCentExc(0)
    {
	bTagMapCSVv2[0] = BLCut;
	bTagMapCSVv2[1] = BMCut;
	bTagMapCSVv2[2] = BTCut;
	if(WPL != -1){
    		if (WPL > WPT){
		       	int tmp;
		       	tmp = WPL;
			WPL = WPT;
			WPT = tmp;
		}
	}
	Systs[0] = "central";
	Systs[-1] = "down";
	Systs[1] = "up";
	cout<< setupDir+"/"+algo+string(".csv")<<endl;
	// calib = new BTagCalibration(algo /*"CSVv2"*/, setupDir+"/"+algo+string(".csv"));
	// reader = new BTagCalibrationReader(calib,(BTagEntry::OperatingPoint)WPT,"mujets",Systs[syst]);
        // readerCent = new BTagCalibrationReader(calib,(BTagEntry::OperatingPoint)WPT,"mujets","central");  
	// readerLight = new BTagCalibrationReader(calib,(BTagEntry::OperatingPoint)WPT,"incl",Systs[syst]);
        // readerCentLight = new BTagCalibrationReader(calib,(BTagEntry::OperatingPoint)WPT,"incl","central");  
	// if(WPL != -1){
	// 	readerExc = new BTagCalibrationReader(calib,(BTagEntry::OperatingPoint)WPL,"mujets",Systs[syst]);
        // 	readerCentExc = new BTagCalibrationReader(calib,(BTagEntry::OperatingPoint) WPL,"mujets","central");  
	// 	readerExcLight = new BTagCalibrationReader(calib,(BTagEntry::OperatingPoint)WPL,"incl",Systs[syst]);
        // 	readerCentExcLight = new BTagCalibrationReader(calib,(BTagEntry::OperatingPoint) WPL,"incl","central");  
	// }

	/* Sanity checks
	 * std::cout<< "---- BTag WPs ----\n\t" <<bTagMapCSVv2[0] <<",\t"<<bTagMapCSVv2[1] <<",\t"<<bTagMapCSVv2[2]
	 *	 <<"\n---- WPs to select ----\n\t"<<bTagMapCSVv2[WPT]
	 *	 <<"\n---- WPs to veto ----\n\t";
	 *	 if(WPL != -1) std::cout << bTagMapCSVv2[WPL]<<std::endl;
	 *	 else std::cout << "No veto is requested" <<std::endl;
	 * End Sanity Checks
	 */
    };
    inline bool filter(int t){
	if(maxTag != -1)
		return (t >= minTag && t <= maxTag);
	else
		return (t >= minTag);
    }
    float weight(pat::JetCollection jets);
    float weight(pat::JetCollection jets, int);
    float weightExclusive(pat::JetCollection jetsTags);
    float TagScaleFactor(pat::Jet jet, bool LooseWP = false);
    float MCTagEfficiency(pat::Jet jet, int WP);
    std::map<int, string> Systs;
    // BTagCalibration * calib;
    // BTagCalibrationReader * reader;
    // BTagCalibrationReader * readerCent;
    // BTagCalibrationReader * readerExc;
    // BTagCalibrationReader * readerCentExc;
    // BTagCalibrationReader * readerLight;
    // BTagCalibrationReader * readerCentLight;
    // BTagCalibrationReader * readerExcLight;
    // BTagCalibrationReader * readerCentExcLight;
  };
#endif


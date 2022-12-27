from difflib import SequenceMatcher

class JSONFile:
    def __init__(self, bad, events , name , nevents , totEvents , weights ):
        self.bad = bad
        self.events = events
        self.name = name
        self.nevents = nevents
        self.totEvents = totEvents
        self.weights = weights

class JSONSample :
    def FindOldSample(self , oldsamples ):
        self.OldSample = None
        parts1 = self.Path.split("/")
        nametolook = parts1[1]
        nameparts = nametolook.split("_")
        if len(nameparts) < 2:
            self.ObjName = nameparts[0]
        else:
            self.ObjName = "{S[0]}_{S[1]}".format( S=nameparts )
        self.XSection = 0.
        self.AllMatchedOldSamples = {}
        highestsimilarity = 0.
        for s in oldsamples:
            parts2 = s.DSName.split("/")
            if parts2[1]  == nametolook :
                similarityOf2ndParts = SequenceMatcher(None, parts2[2] , parts1[2] ).ratio()
                self.AllMatchedOldSamples[similarityOf2ndParts] =  s
                if similarityOf2ndParts > highestsimilarity :
                    self.OldSample = s
                    self.ObjName = s.Name
                    self.XSection = s.XSection
                    highestsimilarity = similarityOf2ndParts
        self.ObjName = self.ObjName.replace( "-" , "_" )
        
    def __init__(self, path , allinfo , filename ):
        self.Path = str(path)
        self.Vetted = False
        self.Files = []
        self.Data = False
        self.JSONFileName = filename
        
        for j in allinfo:
            if j == "vetted":
                self.Vetted =  allinfo[j]
            if j == "files":
                #print allinfo[j]
                for file in allinfo[j]:
                    name = file["name"]
                    #print name
                    bad = file["bad"]
                    if not bad:
                        events = file["events"]
                        nevents = file["nevents"]
                        totEvents = file["totEvents"]
                        weights = file["weights"]
                        if "lumis" in file.keys():
                            self.hasLumi()
                        self.AddFile( bad , events , name , nevents , totEvents , weights )

        

    def ISamcatnlo(self):
        return "amcatnlo" in self.Path
    
    def AddFile(self,  bad, events , name , nevents , totEvents , weights ):
        self.Files.append( JSONFile(  bad, events , str(name) , nevents , totEvents , weights ) )

    def hasLumi(self):
        self.Data = True
        
    def nTotal(self , i = -1):
        ret = 0.
        if i == -1:
            ret = {}
            ret['events'] = self.nTotal(0)
            ret['nevents'] = self.nTotal(1)
            ret['totEvents'] = self.nTotal(2)
            ret['weights'] = self.nTotal(3)
            ret['jsonfile'] = self.JSONFileName
            return ret
        
        for f in self.Files:
            if i == 0 :
                ret += f.events
            elif i == 1:
                ret += f.nevents
            elif i == 2 :
                ret += f.totEvents
            elif i == 3:
                ret += f.weights
        return ret

    def Print(self):
        if not hasattr(self,"OldSample"):
            self.FindOldSample(_oldsamples)
        format_ = '{objName} = Sample( "{objName}" , {xsection:.3f} , {useLHE} , "{fullpath}" , info_from_json={jsoninfo} )'
        print (format_.format( objName=self.ObjName , xsection=self.XSection , useLHE=self.ISamcatnlo() , fullpath=self.Path , jsoninfo=self.nTotal(-1) ))

        print ("MicroAODSamples.append( {objName} )".format( objName=self.ObjName ))

import FWCore.ParameterSet.Config as cms


# Give the process a name
process = cms.Process("HaNa")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 10000
#process.MessageLogger.cerr.FwkReport.reportEvery = 1
#process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.TFileService = cms.Service("TFileService", fileName = cms.string("simepl_tree.root") )
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(20000))

# Tell the process which files to use as the source
process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
                            fileNames = cms.untracked.vstring()
)

# Tell the process what filename to use to save the output
#process.Out = cms.OutputModule("PoolOutputModule",
#         fileName = cms.untracked.string ("MyOutputFile.root")
#)


process.PUAnalyzer = cms.EDAnalyzer('SimplePUAnalyzer',
                                 Vertex = cms.PSet( Input = cms.InputTag( "offlineSlimmedPrimaryVertices" ),
                                                    pileupSrc = cms.InputTag("slimmedAddPileupInfo")
                                                ),

                                 Tracks = cms.PSet( Input = cms.InputTag("packedPFCandidates" ) ),
                                 LostTracks = cms.PSet( Input = cms.InputTag("lostTracks" ) ),

                                    
                                 sample = cms.string("WJetsMG"),
                                 isData = cms.bool( True ),  
                                 SetupDir = cms.string("PUStudies")
                             )


import FWCore.ParameterSet.VarParsing as opts
options = opts.VarParsing ('analysis') 
options.register('sample', 'SimMiniAOD22', opts.VarParsing.multiplicity.singleton, opts.VarParsing.varType.string, 'Sample to analyze')
options.register('job', 0, opts.VarParsing.multiplicity.singleton, opts.VarParsing.varType.int , "number of the job")
options.register('nFilesPerJob', 1, opts.VarParsing.multiplicity.singleton, opts.VarParsing.varType.int , "number of the files pre job") 
options.register('output', "out", opts.VarParsing.multiplicity.singleton, opts.VarParsing.varType.string , "could be root://eoscms//eos/cms/store/user/hbakhshi/out")

options.parseArguments()


theSample = None
from SamplesPU.Samples import MINIAOD22 as samples
for sample in samples:
    print( sample )
    if sample.Name == options.sample : 
        theSample = sample
    
import os
process.PUAnalyzer.sample = theSample.Name
#process.PUAnalyzer.LHE.useLHEW = theSample.LHEWeight
process.PUAnalyzer.isData = theSample.IsData
print('isdata ={0}'.format(theSample.IsData))
if not ( options.job < theSample.MakeJobs( options.nFilesPerJob ,  options.output ) ):
    raise NameError("Job %d is not in the list of the jobs of sample %s with %d files per run" % (options.job , options.sample , options.nFilesPerJob ) )

job = theSample.Jobs[options.job ]

process.source.fileNames.extend( job.Inputs )
process.TFileService.fileName = job.Output

process.maxEvents.input = 20000 #options.maxEvents

process.p = cms.Path( process.PUAnalyzer )


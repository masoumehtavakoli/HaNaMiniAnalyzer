#! /usr/bin/env python

import torch
import torch_geometric as tg
import ROOT
import h5py
from tqdm import tqdm
import argparse
import sys
import os
import numpy as np

def GetEdgeInfo(eta , phi ,max_distance):
    pi = ROOT.TMath.Pi()
    phi_diff = abs( phi.unsqueeze(1) - phi.unsqueeze(0) )
    #phi_diff = phi_diff.remainder(2 * pi)
    mask = phi_diff > pi
    delta_phi = phi_diff - mask*2*pi
    eta_diff = eta.unsqueeze(1) - eta.unsqueeze(0)
    distances = torch.sqrt(eta_diff ** 2 + delta_phi ** 2)
    
    torch.diagonal(distances).fill_(1000.0)
    distances[ torch.tril(torch.ones(distances.shape, dtype=torch.bool)) ] = 1000.0
    
    mask = distances < max_distance
    indices = mask.nonzero().t()
    edge_index = indices.flip(0)

    edge_attr = distances[mask]
    
    return edge_index , edge_attr


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument( '--input' , dest='input' , help='the input root file name' , type=str )
    parser.add_argument( '--maxDR' , dest='maxDR' , help='the cut on the dr to construct the graph' , type=float , default=0.2 )
    opt = parser.parse_args()
        
    file = ROOT.TFile(opt.input)
    tree = file.Get("PUAnalyzer/Trees/Events")

    out_file_name , _ = os.path.splitext( os.path.basename(opt.input) )
    hdf5_file = h5py.File( './{0}.h5'.format(out_file_name) , "w")
    
    pu_groups = {}
    pu_nevents = {}


    num_events = tree.GetEntries()
    for e in tqdm( range(num_events) ):
        tree.GetEntry(e)  
        # Collect features for particles
        phi = torch.tensor(tree.Phi, dtype=torch.float32)
        energy = torch.tensor(tree.Energy, dtype=torch.float32)
        p = torch.tensor(tree.P, dtype=torch.float32)
        pt = torch.tensor(tree.Pt, dtype=torch.float32)
        dz = torch.tensor(tree.dz, dtype=torch.float32)
        dxy = torch.tensor(tree.dxy, dtype=torch.float32)
        eta = torch.tensor(tree.Eta, dtype=torch.float32)
        Type = torch.tensor(tree.Type, dtype=torch.int32)
        charge = torch.tensor(tree.Charge, dtype=torch.int32)

        # Collect attributes for events
        nVertices = torch.tensor([tree.nVertices], dtype=torch.int32)
        nVGoodVertices = torch.tensor([tree.nVGoodVertices], dtype=torch.int32)

        # node_features = torch.stack((phi, charge, energy, p, pt, dz, dxy, eta, Type), dim=1)
        # graph_attr = torch.stack((nVertices, nVGoodVertices), dim=0)

        node_features = torch.stack((phi, pt, dz, dxy, eta, Type), dim=1)
        graph_attr = torch.stack((nVertices), dim=0)

        edge_index , edge_attr = GetEdgeInfo(eta , phi , opt.maxDR)

        data = tg.data.Data(
            x=node_features,
            edge_index=edge_index,
            edge_attr=edge_attr,
            graph_attr=graph_attr
        )

        graph_label = tree.nInt
        data.y = torch.tensor(graph_label, dtype=torch.int64)

        if graph_label not in pu_groups:
            label = "PU{}".format(graph_label)
            group = hdf5_file.create_group(label)
            pu_groups[graph_label] = group
            pu_nevents[graph_label] = 0

        current_type = np.dtype([ ("node_features",  np.dtype("({0},{1})f".format(*data.x.shape))) , 
                                  ("edge_attributes",np.dtype("({0},)f".format(*data.edge_attr.shape)))  ,
                                  ("edge_indecies",  np.dtype("(2,{0})i".format( len( data.edge_attr )))) , 
                                  ("graph_features", np.dtype("(2,1)i")),
                                  ("graph_labels",   np.dtype("(1,)i")) ] )

        arr = np.empty(shape=(1,), dtype=current_type)
        arr["node_features"] = data.x
        arr['edge_attributes'] = data.edge_attr
        arr['edge_indecies'] = data.edge_index
        arr['graph_features'] = data.graph_attr
        arr['graph_labels'] = data.y

        pu_groups[graph_label].create_dataset( 'E{0}'.format(pu_nevents[graph_label]) , shape=(1,), dtype=current_type, data=arr, compression="gzip", chunks=True )
        pu_nevents[graph_label] += 1

    hdf5_file.close()

    import json 
    with open('./{0}.json'.format(out_file_name), "w") as outfile:
        dict_out = {}
        for i,j in pu_nevents.items():
            dict_out[i] = { out_file_name : j }
        outfile.write(json.dumps(dict_out, indent=4))
        
if __name__ == "__main__":
    sys.exit( main() )

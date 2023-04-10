################################################# IMPORTING LIBRARIES #################################################

import numpy as np
import uproot as ur
import h5py
import traceback
import argparse
import sys
from tqdm import tqdm

np.seterr(divide = 'ignore') 

##################################################### Initiation #####################################################

# Initialize parser
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-R", "--ROOTFile",  help = "ROOT File; *.root",     required=True)
parser.add_argument("-T", "--Tree",      help = "Tree of ROOT File",     required=False)
parser.add_argument("-W", "--HDF5Name",  help = "HDF5 File Name; *.hd5", required=False)
parser.add_argument("-b", "--BatchSize", help = "Memory Batch Size",    required=False)

# Read arguments from command line
args = parser.parse_args()

source_file = args.ROOTFile

if args.BatchSize:
    batch_size = args.BatchSize
else:
    batch_size = None

if args.HDF5Name:
    destination = args.HDF5Name
else:
    destination = source_file[:-4] + "hd5"
    
if args.Tree:
    tree = args.Tree
else:
    tree = "PUAnalyzer/Trees/Events"

####################################################### CLASSES #######################################################
class Particle(object):
    DataKeys = ['Pt', 'P', 'Phi', 'Eta', 'Charge', '_dxy', '_dz', 'Energy']

    def __init__(self, particle_name:str, abbr:str, own_flag:dict):
        self.__name = particle_name
        self.__abbr = abbr
        self.__flag = own_flag
        return 
    
    @property
    def abbr(self):
        return self.__abbr
    
    def get_keys(self):
        return Particles.DataKeys
    
    def get_UKeys(self):
        return list(self.__flag.keys())
    
    def __call__(self, u_feature):
        try:
            return self.__flag[u_feature]
        except KeyError:
            return False
        
    def __iter__(self):
        return iter(["{}s{}".format(self.abbr, DataKey) for DataKey in Particle.DataKeys])
    
    def __str__(self):
        return self.__name
    
    def __repr__(self):
        return "{}-{}".format(self.__name, self.__abbr)

class PGraph(object):
    
    def __init__(self, num_nodes, num_node_features, num_edge_attrs, num_graph_features, graph_label, index, dR_telorance = 0.5, undirectd=True):
        assert len(graph_label) != 0, "At least 1 label is required"
        self.index           = index
        self.__num_nodes     = num_nodes
        self.__num_node_f    = num_node_features
        self.__node_features = np.zeros((num_nodes, num_node_features), dtype=np.float32) 
        self.__num_edge_attr = num_edge_attrs
        self.__isUndirected  = undirectd
        self.__num_graph_f   = num_graph_features
        self.__label         = graph_label
        self.__num_graph_l   = len(self.__label)
        self.__dR_telorance  = dR_telorance
        
        self.__graph_f    = dict()
        self.__num_edges  = 0
        self.__edge_index = None
        self.__edge_attrs = None
        return 
    
    @property
    def features(self):
        return self.__graph_f

    def get_num_graph_features(self):
        return self.__num_graph_f
    
    def get_num_graph_labels(self):
        return self.__num_graph_l
    
    def get_label(self):
        return self.__label
    
    def __iter__(self):
        self.__NITERATE = 0
        return self
    
    def __getitem__(self, node_ind):
        return self.__node_features[node_ind]
    
    def len(self):
        return self.__num_nodes, self.__num_edges * 2
    
    def __next__(self):
        if self.__NITERATE == self.__num_nodes:
            raise StopIteration
        node_ind, self.__NITERATE = self.__NITERATE, self.__NITERATE + 1
        return self.__node_features[node_ind]
    
    def add_edge(self, edge, features):
        assert len(edge) == 2, "Unsupported edge"
        assert isinstance(features, (list, tuple)), "Unsupported iterable or data type for features. Use tuple or list instead."
        assert len(features) == len(self.__edge_attr), "Node features are not compatible with this object"
        
        if  self.__isUndirected:
            self.__edge_index.append(edge)
            self.__edge_index.append(edge[::-1])
            
            for i in range(len(features)):
                self.__edge_attr[i].append(features[i])
                self.__edge_attr[i].append(features[i])
        else:
            self.__edge_index.append(edge)
            for i in range(len(features)):
                self.__edge_attr[i].append(features[i])
        
        return
    
    def add_graph_features(self, arr):
        self.__graph_f = arr
    
    def connect_with_index(self, eta_ind, phi_ind):
        dR_MAX = self.__dR_telorance
        N = 1/((1 + dR_MAX) * np.log(1 + dR_MAX) - dR_MAX)
        
        def R2(eta1, phi1, eta2, phi2):
            dphi = abs(phi1 - phi2)
            if dphi > np.pi:
                dphi -= 2*np.pi
                
            return (eta1 - eta2) ** 2 + dphi ** 2
        
        def W(dR):
            return  N * np.exp( np.log(dR_MAX - dR) - np.log(1 + dR) )
        
        edges = []
        attrs = []
        
        # Mapping Theta to Eta
        Eta = self.__node_features[:,eta_ind]
        
        Phi = self.__node_features[:,phi_ind]
        
        # DeltaR Matrix. dr[i][j] is DeltaR of node i and j
#         dr_matrix = np.zeros((self.__num_nodes, self.__num_nodes), dtype=np.float32)
#         np.fill_diagonal(dr_matrix, np.inf)  # Avoiding Self Connections

        for i in range(self.__num_nodes):
            u_eta, u_phi = Eta[i], Phi[i]
            
            for j in range(i + 1, self.__num_nodes):
                v_eta, v_phi = Eta[j], Phi[j]
                
                dr = np.sqrt(R2(u_eta, u_phi, v_eta, v_phi))
                if dr <= dR_MAX:
                    edges.append([i, j])
                    edges.append([j, i])
                    
                    attrs.append([W(dr)])
                    attrs.append([W(dr)])   
                    
                    self.__num_edges += 1
#         print(self.__num_edges, len(edges))
#         n_missed_inf  = np.isinf(dr_matrix).sum() - self.__num_nodes
#         n_missed_nan  = np.isnan(dr_matrix).sum()
#         total_missing = n_missed_inf + n_missed_nan
        
#         dr_matrix[np.isinf(dr_matrix)] = np.inf
#         dr_matrix[np.isnan(dr_matrix)] = np.inf
# #         print(total_missing)
#         if total_missing != 0:
#             print("Missing Value Encountered at event{}".format(self.index), file=sys.stderr)
        
#         mask     = dr_matrix < dR_MAX
#         edge_ind = np.argwhere(dr_matrix < dR_MAX)
        
#         self.__num_edges  = np.sum(mask)
        
#         self.__edge_index = np.insert(edge_ind, np.arange(self.__num_edges),np.flip(edge_ind, axis=1), axis=0).T

        
        
#         dr_s = dr_matrix[dr_matrix < dR_MAX]
        
#         p_matrix = N * np.exp( np.log(dR_MAX - dr_s) - np.log(1 + dr_s) )
        
        self.__edge_index = np.atleast_2d(edges).T
        self.__edge_attrs = np.atleast_2d(attrs)
        return 
    
    def get_graph_features_np(self):
        return np.array([*self.__graph_f.values()])
    
    def get_graph_features_tensor(self):
        return self.__graph_f(self.__graph_f, dtype=torch.float)
    
    def get_edge_index_tensor(self):
        return torch.tensor(self.__edge_index, dtype=torch.long)
    
    def get_edge_attr_tensor(self):
        return torch.tensor(self.__edge_attrs, dtype=torch.float)
    
    def get_node_features_tensor(self):
        return torch.tensor(self.__node_features, dtype=torch.float)
    
    def get_edge_index_np(self):
        return self.__edge_index
    
    def get_edge_attr_np(self):
        return self.__edge_attrs
    
    def get_node_features_np(self):
        return self.__node_features

    
class Event(object):
    DataKeys = ['nGoodVertices', 'nVertices', 'nVGoodVertices', 'nVVGoodVertices', #'ndof',
                'nEles', 'nMus', 'nChargedHadrons', 'nNeutralHadrons', 'nPhotons']
    
    ParticleSummary = ['nEles', 'nMus', 'nChargedHadrons', 'nNeutralHadrons', 'nPhotons']
    
    def __init__(self, particle_queue_dict:dict):
        self.__particle_queue = particle_queue_dict
        self.__num_particle_a = np.cumsum(np.array(list(self.__particle_queue.values())))
        self.__n_particle     = self.__num_particle_a[-1]
#         print(self.__num_particle_a)
        
        # Iteration Variables
        self.__NITERATE  = 0
        self.__current_p = None
        return         
    
    def __len__(self, sub_particle=None):
        return n_particles 
    
    def __iter__(self):
        return self
    
    def node_index(self):
        if self.__current_p is None:
            raise RuntimeError("this method is available only in iterations block".capitalize())
            
        status = self.__num_particle_a - self.__NITERATE
        number = self.__particle_queue[self.__current_p]
#         print("There is {} {}(s)".format(number, self.__current_p.abbr))
#         print("Iteration number", self.__NITERATE)
        index  = number - status[status >= 0][0] - 1
        return index
    
    def __next__(self):
        for C_sum, particle in zip(self.__num_particle_a, self.__particle_queue):
            if  self.__NITERATE  < C_sum:
                self.__NITERATE += 1
                self.__current_p = particle
#                 print(particle.abbr)
                return particle
        
        self.__NITERATE  = 0
        self.__current_p = None
        raise StopIteration
                    

class EventsPGraph(object):
    def __init__(self, directory, key, particle_queue, n_edge_attrs, graph_label_num=1, memory_batch_size="100 MB"):
        self._open_key = "{}:{}".format(directory, key)
        self._PQ       = particle_queue 
        self._NEA      = n_edge_attrs     # Number of Edge Attributes
        self._MBSize   = memory_batch_size
        self._ur_file  = ur.open(self._open_key)
        self._n_event  = len(self._ur_file["nEles"].array())       
        self._n_labels = graph_label_num
        
        self._PN_key   = None
        self._p_keys   = None   # Particle Keys
        self._a_keys   = None   # Additional Keys
        self._n_event  = None   # Number of Events
        self._NEF      = None   # Number of Event Features
        self._NNF      = None   # Number of Node Features
        self._all_NP   = None   # All Number of Particles
        self._all_EFD  = None   # All Events Features data
        self._all_PFD  = None   # All Particles Features data
        self._TreeIter = None   # Tree Iterator
        self._NITERATE = None   # Event Iterator Counter Sentinel
        self._sub_coun = None
        
        self._current_batch = None
        
        return 
    
    def _process(self):
        # Initialize the Keys
        try:
            self._PN_key = ["n{}s".format(particle.abbr) for particle in self._PQ]
            self._a_keys = []
            self._p_keys = []
            for particle in self._PQ:
                additional_keys = particle.get_UKeys()

                for add_key in additional_keys:
                    if self._a_keys.count(add_key) <= 1:
                        self._a_keys.append(add_key)

                for data_key in particle:
                    self._p_keys.append(data_key)

            self._NNF     = len(Particle.DataKeys) + len(self._a_keys)
            self._NEF     = len(Event.DataKeys)

            return 1  # Successful initiation
        
        except Exception as e:
            print(e)
            traceback.print_exc()
            return 0

    def __iter__(self):
        self._NITERATE = 0
        self._sub_coun = 0
        
        self._TreeIter = self._ur_file.iterate(step_size=self._MBSize)
        
        if self._process():
            return self
        
        self._ur_file.close()
        raise ProcessLookupError("Processing Faild")
    
    def event_index(self):
        return self._NITERATE
    
#     def __len__(self):
#         return self._NITERATE % self._MBSize
    
    def __next__(self):
        if self._NITERATE == 0:
            self._current_batch = next(self._TreeIter)   # Contains StopIterationError
        
#         print(self._NITERATE, self._sub_coun)
        
        try:
            this_event_data = self._current_batch[self._sub_coun]
#             self._sub_coun += 1
        
        except ValueError:
            self._sub_coun      = 0
            self._current_batch = next(self._TreeIter)
            this_event_data     = self._current_batch[self._sub_coun]
        
        eventNum, self._NITERATE = self._NITERATE, self._NITERATE + 1
        
        self._sub_coun += 1
#         this_event_data   = self._current_batch[eventNum % self._MBSize]
        
        particle_summary  = [this_event_data[key] for key in self._PN_key]
        num_of_particles  = np.sum(particle_summary)
        
        num_PU = this_event_data["nInt"]
#         print(num_PU)
        this_event_PQD    = dict(zip(self._PQ, [this_event_data[key] for key in self._PN_key]))
        this_event        = Event(this_event_PQD)
        this_event_pgraph = PGraph(num_of_particles, self._NNF, self._NEA, self._NEF, index=self.event_index(), graph_label=[num_PU])
        
        for key in Event.DataKeys:
            this_event_pgraph.features[key] = this_event_data[key]

        for particle, node in zip(this_event, this_event_pgraph):
            particle_ind = this_event.node_index()
#             print("index:", particle_ind, '\n')
            
            for i, particle_key in zip(range(len(self._p_keys)), particle):
                node[i] = this_event_data[particle_key][particle_ind]
            
            for j, additional_feature in zip(range(len(self._p_keys), self._NNF), self._a_keys):
                node[j] = particle(additional_feature)
        
        theta_ind = Particle.DataKeys.index('Eta')
        phi_ind   = Particle.DataKeys.index('Phi')
        
        this_event_pgraph.connect_with_index(theta_ind, phi_ind)
        
        return this_event_pgraph
    
    def to_hd5(self, dest_name, ):
        
        with h5py.File(dest_name, "w") as h5_file:
            order = 5
            dset_group = h5_file.create_group("datasets")
#             count = 0
            for pgraph in tqdm (self, desc="Graph Generation Progress...", ascii=False, unit="event", total=self._n_event):
#                 count += 1
                nn, ne = pgraph.len()
                
                current_type = np.dtype([
                    ("node_features",  np.dtype(f"({nn},{self._NNF})f")),
                    ("edge_attributes", np.dtype(f"({ne},{self._NEA})f")),
                    ("edge_indecies",  np.dtype(f"(2,{ne})i")),
                    ("graph_features", np.dtype(f"({self._NEF},)i")),
                    ("graph_labels",   np.dtype(f"({self._n_labels},)i"))
                ])
                arr = np.empty(shape=(1,), dtype=current_type)
                arr["node_features"]   = [pgraph.get_node_features_np()]
                arr["edge_indecies"]   = [pgraph.get_edge_index_np()]
                arr["edge_attributes"] = [pgraph.get_edge_attr_np()]
                arr["graph_labels"]    = [pgraph.get_label()]
                arr["graph_features"]  = [pgraph.get_graph_features_np()]
                
                event_number = pgraph.index

                DS = dset_group.create_dataset(f"data{event_number: 0{order}}", shape=(1,), dtype=current_type, data=arr, compression="gzip", chunks=True)
                
#                 clear_output(wait=True)
#                 print("At event", event_number, flush=True)

#                 print(pgraph.get_graph_features_np())
#                 print(DS[0]["graph_features"])
        
    
#                 if count == 5:
#                     break
            h5_file["Keys/Particle/Features"] = [*Particle.DataKeys, *self._a_keys]
            h5_file["Keys/Event/Features"]    = [f"f{key}" for key in Event.DataKeys]
            h5_file["Keys/Event/Labels"]      = ["lPU"]
        
        print("Done.")

############################################## Defining The Particle Queue ##############################################      


electron       = Particle(particle_name="e" , abbr="Ele",           own_flag={"is_lep": True, "is_e" : True})
muon           = Particle(particle_name="mu", abbr="Mu",            own_flag={"is_lep": True, "is_mu": True})
charged_hadron = Particle(particle_name="ch", abbr="ChargedHadron", own_flag={"is_had": True})
neutral_hadron = Particle(particle_name="nh", abbr="NeutralHadron", own_flag={"is_had": True})
photon         = Particle(particle_name="ph", abbr="Photon",        own_flag={})

particle_queue = [electron, muon, photon, charged_hadron, neutral_hadron]


############################################### Creating The Event Object ############################################### 

if batch_size is not None:
    events = EventsPGraph(source_file, tree, particle_queue, 1, memory_batch_size=batch_size)
else:
    events = EventsPGraph(source_file, tree, particle_queue, 1)

############################################## Write Graphs into HDF5 File ############################################## 

events.to_hd5(destination)

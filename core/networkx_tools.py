import re
from itertools import product
from core.variable_template_regex import VariableTemplateRegex
import networkx as nx
from gfx.arrow import Arrow
from gfx.object import Object
from gfx.text import Text
from bidict import bidict
import time


def regex_node_match(data1, data2):
    """
    data1 corresponds to G1, which is the database graph.  
    G2 is the query graph and data2['labels'] holds its list of labels.
    """    
    labels1 = data1['labels']
    labels2 = data2['labels']        
    
    if len(labels1) != len(labels2):
        return False
    
    maps2to1 = product(labels1, repeat=len(labels2))
    
    for m in maps2to1:
        for i in range(len(m)):
            if not m[i].regex.fullmatch(labels2[i]):
                break
        else:
            return True
                
    return False


def regex_multiedge_match(datasets1, datasets2):
    #if len(datasets1) != len(datasets2):
        #return False
    
    #datasets2_list = datasets2.values()
    
    #dataset_maps2to1 = product(datasets1.values(), len(datasets2))
    
    #for m in dataset_maps2to1:
        #for i in range(len(m)):
            #data1 = m[i]
            #data2 = datasets2_list[i]
    
            #if not regex_node_match(data1, data2):
                #break
        #else:
            #return True
    
    # This works because our Arrows are represented as nodes in the graph and edges are two plain edges to connect respective nodes
    return True    
        
        
def build_networkx_graph(graph:nx.MultiDiGraph, items, var_index:bidict=None, labels_fun=None, node_id:int=None):               
    if var_index is None:
        var_index = bidict()
        
    if node_id is None:
        node_id = 0
        
    nodes = {}

    # Establish all the nodes first, including Arrows in order to support arrow-to-arrow connections
    for item in items:
        if isinstance(item, (Object, Arrow)):
            nodes[id(item)] = node_id
            attrs = networkx_attributes(item, var_index, labels_fun)
            graph.add_node(node_id, **attrs) 
            node_id += 1
        
    # Connect the "arrows" and finally add in orphan Text items
    for item in items:
        if isinstance(item, Arrow):
            if item.source:
                graph.add_edge(nodes[id(item.source)], nodes[id(item)])
            if item.destination:
                graph.add_edge(nodes[id(item)], nodes[id(item.destination)])
            
        elif isinstance(item, Text):
            if item.parentItem() is None:
                attrs = networkx_attributes(item, var_index, labels_fun)
                graph.add_node(node_id, **attrs) 
                node_id += 1
            
    return node_id
   

def networkx_attributes(item, var_index:bidict=None, labels_fun=None):
    if labels_fun is None:
        labels_fun = networkx_library_labels
        
    if isinstance(item, Object):
        return {
            'kind': 'object',
            'labels' : labels_fun(item, var_index),
            'gfxitem' : item,
        }
    
    elif isinstance(item, Arrow):
        return {
            'kind' : 'arrow',
            'labels' : labels_fun(item, var_index),
            'gfxitem' : item,
        }
    
    elif isinstance(item, Text):
        return {
            'kind' : 'remark',
            'gfxitem' : item,
            'labels' : [item.toHtml()],
        }

    
def networkx_library_labels(item, var_index:bidict=None):
    labels = [VariableTemplateRegex(t.toHtml(), var_index) for t in filter(lambda x: isinstance(x, Text), item.childItems())]
    return labels       

def networkx_query_labels(item, var_index:bidict=None):
    labels = [t.toHtml() for t in filter(lambda x: isinstance(x, Text), item.childItems())]
    return labels

def networkx_component_induced_by_node(G, node):
    nodes = nx.single_source_shortest_path(G,node).keys()
    return G.subgraph(nodes)
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
            if not re.match(m[i], labels2[i]):
                break
        else:
            return True
                
    return False


def regex_multiedge_match(datasets1, datasets2):
    if len(datasets1) != len(datasets2):
        return False
    
    datasets2_list = datasets2.values()
    
    dataset_maps2to1 = product(datasets1.values(), len(datasets2))
    
    for m in dataset_maps2to1:
        for i in range(len(m)):
            data1 = m[i]
            data2 = datasets2_list[i]
    
            if not regex_node_match(data1, data2):
                break
        else:
            return True
    
    return False
        
        
def networkx_graph(items, var_index:bidict=None):        
    if var_index is None:
        var_index = bidict()
    node_id = 0
    nodes = {}
    graph = nx.Graph()

    for item in items:
        if isinstance(item, Object):
            item.networkx_node_id = node_id
            nodes[id(item)] = item
            graph.add_node(node_id, **networkx_attributes(item, var_index)) 
            node_id += 1
        
    for item in items:
        if isinstance(item, Arrow):
            item.networkx_node_id = node_id
            nodes[id(item)] = item
            graph.add_node(node_id, **networkx_attributes(item, var_index)) 
            node_id += 1
            if item.source:
                graph.add_edge(item.source.networkx_node_id, node_id)
            if item.destination:
                graph.add_edge(node_id, item.destination.networkx_node_id)
            
        elif isinstance(item, Text):
            if item.parentItem() is None:
                item.networkx_node_id = node_id
                nodes[id(item)] = item
                graph.add_node(node_id, **networkx_attributes(item, var_index)) 
                node_id += 1
            
    print(var_index)
    return graph


def networkx_attributes(item, var_index:bidict):
    if isinstance(item, Object):
        return {
            'kind': 'ob',
            'labels' : networkx_labels(item, var_index),
            'canvas' : item.scene(),
        }
    
    elif isinstance(item, Arrow):
        return {
            'kind' : 'arrow',
            'labels' : networkx_labels(item, var_index),
            'canvas' : item.scene(),
        }
    
    return {
        'canvas' : item.scene(),
    }
    
    
def networkx_labels(item, var_index:bidict):
    assert isinstance(item, (Object, Arrow))
    labels = [VariableTemplateRegex(t.toHtml(), var_index) for t in filter(lambda c: isinstance(c, Text), item.childItems())]
    return labels        


class ParentArrow:
    def __init__(self, source, dest):
        self._source = source
        self._dest = dest
        
    @property
    def source(self):
        return self._source
    
    @property
    def destination(self):
        return self._dest
    
    def childItems(self):
        return []
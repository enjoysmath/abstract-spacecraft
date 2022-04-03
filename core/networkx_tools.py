import re
from itertools import product
from core.variable_template_regex import VariableTemplateRegex
import networkx as nx
from graphics.arrow import Arrow
from graphics.object import Object
from graphics.text import Text

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
        
        
def networkx_graph(items):        
    node_id = 0
    nodes = {}
    arrows = []
    graph = nx.Graph()
    
    for item in items:
        if isinstance(item, (Object, Arrow)):
            item.networkx_node_id = node_id
            nodes[id(item)] = item
            graph.add_node(node_id, **networkx_attributes(item))
            node_id += 1
            
            if item.parentItem() is not None:
                parent_arrow = ParentArrow(item, item.parentItem())
                arrows.append(parent_arrow)
            
            if isinstance(item, Arrow):
                arrows.append(item)
                
    for arrow in arrows:
        if isinstance(arrow, ParentArrow):
            graph.add_edge(nodes[id(arrow.source)], nodes[id(arrow.destination)], tofromparent='p')
        else:
            graph.add_edge(nodes[id(arrow)], nodes[id(arrow.destination)], tofromparent='t')
            graph.add_edge(nodes[id(arrow)], nodes[id(arrow.source)], tofromparent='f')
    
    return graph


def networkx_attributes(item):
    if isinstance(item, Object):
        kind = 0
    elif isinstance(item, Arrow):
        kind = 1
    return {
        'kind' : kind,
        'labels' : networkx_labels(item)
    }
    
    
def networkx_labels(item):
    assert isinstance(item, (Object, Arrow))
    labels = [VariableTemplateRegex(t.toHtml()) for t in \
              filter(lambda c: isinstance(c, Text), item.childItems())]
    #print(labels)
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
from collections import defaultdict


links_node_1 = [('E1', 'E1', 'node_2'), ('E11', 'E11', 'node_2'),
                ('E2', 'E1', 'node_3'), ('E3', 'E1', 'node_4'),
                ('P1', '', 'node_2')]
links_node_2 = [('E1', 'E1', 'node_1'), ('E11', 'E11', 'node_1'),
                ('E2', 'E2', 'node_3'), ('E3', 'E2', 'node_4'),
                ('P11', '', 'node_1')]
links_node_3 = [('E1', 'E2', 'node_1'), ('E2', 'E2', 'node_2')]
links_node_4 = [('E1', 'E3', 'node_1'), ('E2', 'E3', 'node_2'),
                ('E3', 'E1', 'node_5'), ('P1', '', 'node_5')]
links_node_5 = [('E1', 'E3', 'node_4'), ('P1', '', 'node_4')]

nodeinfo = {}

nodeinfo['node_1'] = links_node_1
nodeinfo['node_2'] = links_node_2
nodeinfo['node_3'] = links_node_3
nodeinfo['node_4'] = links_node_4
nodeinfo['node_5'] = links_node_5


def update_nodeinfo(nodeinfo):
    """
    remove port-channel member links and update remote port info
    for Port-channel interfaces
    """
    # Create adj list formed by port-channel links
    adj_list = defaultdict(list)
    for node in nodeinfo:
        for tuple_ in nodeinfo[node]:
            local_port = tuple_[0]
            remote_port = tuple_[1]
            remote_node = tuple_[2]
            if local_port.startswith('P'):
                adj_list[node].append(remote_node)

    # Create lookup dict for remote port-channel port and remove port-channel
    # member links from nodeinfo dict
    po_remote_port = defaultdict(dict)
    for adj_local_node in list(adj_list):
        for adj_remote_node in adj_list[adj_local_node]:
            for node in nodeinfo:
                for tuple_ in list(nodeinfo[node]):
                    local_port = tuple_[0]
                    remote_port = tuple_[1]
                    remote_node = tuple_[2]
                    if (not local_port.startswith('P') and
                            remote_node in adj_list[node]):
                        nodeinfo[node].remove(tuple_)
                    if (local_port.startswith('P') and
                            adj_local_node == remote_node):
                        po_remote_port[adj_local_node][node] = local_port

    # Add remote port info for Po interfaces
    for node in nodeinfo:
        for tuple_ in nodeinfo[node]:
            local_port = tuple_[0]
            remote_port = tuple_[1]
            remote_node = tuple_[2]
            if remote_port == '':
                remote_port = po_remote_port[node][remote_node]
                nodeinfo[node].remove(tuple_)
                nodeinfo[node].append((local_port, remote_port, remote_node))

    return nodeinfo


def check_if_nodeinfo_is_empty(nodeinfo):
    for node in nodeinfo:
        if nodeinfo[node] != []:
            return False
    return True


# Create link object with node information (node name and portindex)
# on each part of the link.
nodeinfo = update_nodeinfo(nodeinfo)
index = 1
link_obj = {}
nodeinfo_is_empty = False
while not nodeinfo_is_empty:
    for node in nodeinfo:
        for tuple_ in nodeinfo[node]:
            local_port = tuple_[0]
            remote_port = tuple_[1]
            remote_node = tuple_[2]
            for node2 in nodeinfo:
                if node == node2:
                    continue
                if (remote_port, local_port, node) in nodeinfo[node2]:
                    nodeinfo[node2].remove((remote_port, local_port, node))
                    break
            link_obj['link' + str(index)] = {node: local_port}
            link_obj['link' + str(index)].update({node2: remote_port})
            nodeinfo[node].remove(tuple_)
            index += 1
            break
    nodeinfo_is_empty = True if check_if_nodeinfo_is_empty(nodeinfo) else False


print(link_obj)
    

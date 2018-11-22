#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Tree_Manager():
    def __init__(self):
        self._to_name = {}
        self._all_nodes = {}
        self._to_parent = {}
        self._to_old = {}
        self._to_main_id = {}

    def change_main_bookid(self, book_id):
        id_str = str(book_id)
        new_id = '91' + id_str[2:]
        return new_id

    def is_main_id(self, know_id):
        id_str = str(know_id)
        if id_str[0 : 2] == '91':
            return True
        else :
            return False

    def add_node(self, parent_id, son_id, name, level, old_id):
        self._to_name[son_id] = name
        self._to_parent[son_id] = parent_id
        self._to_old[son_id] = old_id
        if level == 1:
            if not parent_id in self._all_nodes:
                self._all_nodes[parent_id] = {}
            self._all_nodes[parent_id][son_id] = {}
        if level == 2:
            book_id = self._to_parent[parent_id]
            if not book_id:
                print 'Error. no found book_id'
            if not parent_id in self._all_nodes[book_id]:
                self._all_nodes[book_id][parent_id] = {}
            self._all_nodes[book_id][parent_id][son_id] = 1
            # other book id need to transform to main id
            if self.is_main_id(book_id):
                main_ky_str = str(book_id) + '_' + old_id
                self._to_main_id[main_ky_str] = son_id
            else :
                m_book_id = self.change_main_bookid(book_id)
                main_ky_str = m_book_id + '_' + old_id
                ky_str = str(book_id) + '_' + old_id
                self._to_main_id[ky_str] = self._to_main_id[main_ky_str] if main_ky_str in self._to_main_id else son_id

    def short_book_id(self):
        pass

    def get_parent_id(self, id):
        return self._to_parent[id]

    def get_name(self, id):
        return self._to_name[id]

    def get_old_id(self, id):
        return self._to_old[id]

    def get_all_old_ids(self, book_id):
        all_olds = {}
        all_nodes = self.get_nodes_by_level(book_id, 2)
        for k_id in all_nodes:
            o_id = self.get_old_id(k_id)
            all_olds[o_id] = 1
        return all_olds

    def get_nodes_by_level(self, book_id, level):
        nodes = {}
        if book_id not in self._all_nodes:
            return nodes
        if level == 1:
            for k_id in self._all_nodes[book_id]:
                nodes[k_id] = 1

        if level == 2:
            for k_id in self._all_nodes[book_id]:
                for kk_id in self._all_nodes[book_id][k_id]:
                    nodes[kk_id] = 1
        return nodes

    def get_all_nodes(self, book_id):
        nodes_1 = self.get_nodes_by_level(book_id, 1)
        nodes_2 = self.get_nodes_by_level(book_id, 2)
        return dict(nodes_1, **nodes_2)

    def get_child_knows(self, book_id, know_id):
        return self._all_nodes[book_id][know_id]

    def get_main_id(self, book_id, old_id):
        k_str = str(book_id) + '_' + str(old_id)
        if k_str not in self._to_main_id:
            return None
        return self._to_main_id[k_str]

    def get_leaf_nodes(self, node_id, level):
        pass


if __name__ == '__main__':
    tree_m = Tree_Manager()
    tree_m.add_node('1', '11', 'NN', 1, 'C1')
    tree_m.add_node('1', '12', 'NN2', 1, 'C2')
    tree_m.add_node('11', '1101', 'NNN1', 2, 'C22')
    tree_m.add_node('11', '1102', 'NNN2', 2, 'C23')

    print ' get_nodes_by_level:', tree_m.get_nodes_by_level('1', 2)
    print 'get old_id:', tree_m.get_old_id('1102')


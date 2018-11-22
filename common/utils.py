#!/usr/bin/env python
# -*- coding: utf-8 -*-

Yt_Front_Str = '70'

def generate_quesiton_id(sub, grade_id, old_id, topic_id, term_id):
    new_sub = str(sub)
    grade_id += term_id
    new_grade = str(grade_id) if grade_id > 9 else '0' + str(grade_id)
    new_old_id = str(old_id) if old_id > 999 else '0' + str(old_id)
    new_top_id = str(topic_id) if topic_id > 999999 else '0' + str(topic_id)
    return new_sub + new_grade + new_old_id + new_top_id


def generate_yt_id(sub, tree_id, id):
    new_sub = str(sub)
    new_tree_id = str(tree_id) if tree_id > 999 else '0' + str(tree_id)
    new_id = str(id) if id > 999999999 else '0' + str(id)
    return Yt_Front_Str + new_sub + new_tree_id + new_id

def list_to_str(list):
    for i in range(0, len(list)):
        list[i] = str(list[i])
    return ','.join(list)
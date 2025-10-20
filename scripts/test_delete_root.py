#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# Ensure project root is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from controllers.tree_controller import TreeController

class MinimalView:
    def show_message(self, title, msg):
        print(f"{title}: {msg}")
    def update_visualization_with_animation(self, before_state, after_state, operation, value=None, **kwargs):
        before_size = before_state.get('size') if isinstance(before_state, dict) else 'NA'
        after_size = after_state.get('size') if isinstance(after_state, dict) else 'NA'
        print(f"Animation: {operation}, value={value}, before size={before_size}, after size={after_size}")
    def update_visualization(self, data, structure_type=None):
        print(f"Update visualization: type={data.get('type')}, size={data.get('size')}, structure_type={structure_type}")
    def show_avl_delete_animation(self, steps, deleted_value):
        print(f"AVL delete animation steps: {len(steps)} for value {deleted_value}")


def main():
    view = MinimalView()
    tc = TreeController(view)
    # Create empty binary tree
    tc.handle_action('create', {'structure_type': 'binary_tree', 'values': []})
    # Insert root at path []
    tc.handle_action('insert', {'value': 10, 'position': []})
    # Delete root at path []
    tc.handle_action('delete', {'position': []})

if __name__ == '__main__':
    main()
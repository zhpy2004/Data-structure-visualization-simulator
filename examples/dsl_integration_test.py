import sys
import os

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Minimal mock views for controller integration
class LinearMockView:
    def show_message(self, title, msg):
        print(f"[LinearView:{title}] {msg}")
    def show_result(self, title, msg):
        print(f"[LinearView:{title}] {msg}")
    def update_view(self, structure):
        print(f"[LinearView] update_view structure={structure}")
    def update_visualization(self, data, structure_type=None):
        print(f"[LinearView] visualization: type={structure_type}, data={data}")
    def update_visualization_with_animation(self, before_state, after_state, action, **kwargs):
        print(f"[LinearView] anim action={action}, before={before_state}, after={after_state}, extra={kwargs}")

class TreeMockView:
    def show_message(self, title, msg):
        print(f"[TreeView:{title}] {msg}")
    def update_view(self, structure):
        print(f"[TreeView] update_view structure={structure}")
    def update_visualization(self, data, structure_type=None):
        print(f"[TreeView] visualization: type={structure_type}, data={data}")
    def update_visualization_with_animation(self, before_state, after_state, action, value):
        print(f"[TreeView] anim action={action}, before={before_state}, after={after_state}, value={value}")
    def show_bst_build_animation(self, steps):
        print(f"[TreeView] BST build steps={len(steps)}")
    def show_avl_build_animation(self, steps):
        print(f"[TreeView] AVL build steps={len(steps)}")
    def highlight_traversal_path(self, result, traverse_type):
        print(f"[TreeView] traverse {traverse_type}: {result}")
    # Add search/insert/delete path highlights used by TreeController
    def highlight_search_path(self, path, found, value):
        print(f"[TreeView] search path={path}, found={found}, value={value}")
    def highlight_bst_insert_path(self, path, value):
        print(f"[TreeView] bst insert path={path}, value={value}")
    def highlight_bst_delete_path(self, path, value):
        print(f"[TreeView] bst delete path={path}, value={value}")

# Wire controllers
from controllers.linear_controller import LinearController
from controllers.tree_controller import TreeController
from controllers.dsl_controller import DSLController


def run_linear_tests(ctrl: DSLController):
    print("\n=== Linear Context Tests ===")
    ctrl.set_context_target('linear')
    # Create stack and push values (grammar: push <value> to <structure>)
    ctrl.process_command("create stack")
    ctrl.process_command("push 10 to stack")
    ctrl.process_command("push 20 to stack")
    # Peek top
    ctrl.process_command("peek stack")
    # Pop and peek again (grammar: pop from <structure>)
    ctrl.process_command("pop from stack")
    ctrl.process_command("peek stack")
    # Create arraylist and get/delete by value/position
    ctrl.process_command("create arraylist with 1,2,3,4")
    ctrl.process_command("get 3 from arraylist")
    ctrl.process_command("delete 2 from arraylist")
    # Clear
    ctrl.process_command("clear arraylist")


def run_tree_tests(ctrl: DSLController):
    print("\n=== Tree Context Tests ===")
    ctrl.set_context_target('tree')
    # Build BST and traverse inorder
    ctrl.process_command("build bst with 10,5,15,3,7,12,18")
    ctrl.process_command("traverse inorder")
    # Search and delete in BST (grammar: search <value> in <structure>, delete <value> from <structure>)
    ctrl.process_command("search 7 in bst")
    ctrl.process_command("delete 7 from bst")
    # Build AVL and traverse preorder
    ctrl.process_command("build avl with 10,20,30,40,50,25")
    ctrl.process_command("traverse preorder")
    # Create binary tree and insert by position (grammar: insert <value> at <pos> in <structure>)
    ctrl.process_command("create binarytree")
    ctrl.process_command("insert 1 in binarytree")
    ctrl.process_command("insert 2 at 1 in binarytree")
    ctrl.process_command("insert 3 at 0,0 in binarytree")
    ctrl.process_command("traverse levelorder")
    # Clear
    ctrl.process_command("clear bst")
    ctrl.process_command("clear avl")
    ctrl.process_command("clear binarytree")


def main():
    linear_view = LinearMockView()
    tree_view = TreeMockView()
    linear_ctrl = LinearController(linear_view)
    tree_ctrl = TreeController(tree_view)
    dsl_ctrl = DSLController(linear_ctrl, tree_ctrl)

    # Run both contexts
    run_linear_tests(dsl_ctrl)
    run_tree_tests(dsl_ctrl)


if __name__ == "__main__":
    sys.exit(main())
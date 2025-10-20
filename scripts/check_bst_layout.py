#!/usr/bin/env python
import os
import sys

# Ensure repository root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, REPO_ROOT)

from models.tree.bst import BST


def main():
    t = BST()
    for v in [10, 5, 15, 3, 7, 12, 18]:
        t.insert(v)
    data = t.get_visualization_data()
    print("type=", data.get("type"))
    print("nodes=")
    for n in sorted(data.get("nodes", []), key=lambda k: k.get("id")):
        x = n.get("x_pos", 0.0)
        print(
            "id=%s val=%s parent=%s level=%s x_pos=%.3f" % (
                n.get("id"), n.get("value"), n.get("parent_id"), n.get("level"), x
            )
        )


if __name__ == "__main__":
    main()
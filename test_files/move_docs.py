#!/usr/bin/env python3
"""
File operations script for document consolidation.
Moves AuthorityAndAlignment.md to archive and merges ScopeByPhase.md into PRD.md
"""

import os
import shutil

def main():
    base_path = r"c:\Users\AiDev\Documents\RevelHMIPatentCode-v2\docs"
    
    # Move ScopeByPhase.md to archive
    src_scope = os.path.join(base_path, "ScopeByPhase.md")
    dst_scope = os.path.join(base_path, "archive", "ScopeByPhase-Obsolete.md")
    
    if os.path.exists(src_scope):
        shutil.move(src_scope, dst_scope)
        print(f"Moved {src_scope} to {dst_scope}")
    else:
        print(f"File not found: {src_scope}")

if __name__ == "__main__":
    main()
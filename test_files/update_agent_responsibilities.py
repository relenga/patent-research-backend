#!/usr/bin/env python3
"""
Replace AgentResponsibilities.md with updated version
"""

import os
import shutil

def main():
    base_path = r"c:\Users\AiDev\Documents\RevelHMIPatentCode-v2\docs"
    
    # Move original to archive
    src_old = os.path.join(base_path, "AgentResponsibilities.md")
    dst_archive = os.path.join(base_path, "archive", "AgentResponsibilities-Obsolete.md")
    
    # Move updated version to main location
    src_updated = os.path.join(base_path, "AgentResponsibilities-Updated.md")
    dst_main = os.path.join(base_path, "AgentResponsibilities.md")
    
    if os.path.exists(src_old):
        shutil.move(src_old, dst_archive)
        print(f"Moved original to {dst_archive}")
    
    if os.path.exists(src_updated):
        shutil.move(src_updated, dst_main)
        print(f"Activated updated version at {dst_main}")

if __name__ == "__main__":
    main()
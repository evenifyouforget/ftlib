"""Data loading for Spacelight Tournament"""

import re
import sys
from pathlib import Path
from typing import List

# Add test directory to path for imports  
ftlib_root = Path(__file__).parent.parent  # Go up from spacelight/ to ftlib/
test_dir = ftlib_root / "test"
sys.path.insert(0, str(test_dir))

from get_design import retrieveDesign, designDomToStruct
from .core import EasyLevel


def extract_design_id(link_or_id):
    """Extract design ID from URL or direct ID"""
    matches = re.findall('(?:Id=)?(\\d+)', link_or_id)
    for match in matches:
        return int(match)
    return None


def int_or_none(value):
    """Convert string to int or None if empty"""
    if value == '':
        return None
    return int(value)


def load_easy_levels_from_tsv(max_levels: int = None) -> List[EasyLevel]:
    """Load easy levels from fc_data.tsv file with expected results"""
    print("📥 Loading levels from fc_data.tsv...")
    
    tsv_path = ftlib_root / "test" / "fc_data.tsv"
    
    levels = []
    level_count = 0
    solve_count = 0
    fail_count = 0
    
    with open(tsv_path, 'r') as file:
        for line_num, line in enumerate(file, 1):
            if max_levels and len(levels) >= max_levels:
                print(f"🛑 Reached max_levels limit ({max_levels})")
                break
                
            if line.strip() and not line.startswith('#'):
                try:
                    parts = line.strip().split('\t')
                    if len(parts) < 4:
                        continue
                        
                    url = parts[0]
                    solve_ticks_str = parts[1] if len(parts) > 1 else ''
                    design_max_ticks_str = parts[2] if len(parts) > 2 else ''
                    
                    # Determine expected result from TSV columns
                    solve_ticks = int_or_none(solve_ticks_str)
                    design_max_ticks = int_or_none(design_max_ticks_str)
                    
                    if solve_ticks is not None:
                        expected_result = True  # Design solves
                        solve_count += 1
                    elif design_max_ticks is not None:
                        expected_result = False  # Design fails
                        fail_count += 1
                    else:
                        continue  # Skip if no expected result
                    
                    design_id = extract_design_id(url)
                    if not design_id:
                        continue
                    
                    if level_count <= 3 or level_count % 10 == 0:  # Show first 3, then every 10th
                        print(f"📦 Processing {design_id} (expect: {'SOLVE' if expected_result else 'FAIL'})...")
                    level_count += 1
                    
                    try:
                        dom = retrieveDesign(design_id)
                        design_struct = designDomToStruct(dom)
                        
                        goal_area = design_struct.goal_area
                        goal_pieces = design_struct.goal_pieces
                        
                        # Skip if too complex (>1 goal piece or complex goal area)
                        if len(goal_pieces) > 1:
                            if level_count <= 2:  # Only show first couple skips
                                print(f"⏭️  Skipped complex level: {design_id}")
                            continue
                        if goal_area.w > 150 or goal_area.h > 150:
                            if level_count <= 2:  # Only show first couple skips
                                print(f"⏭️  Skipped complex level: {design_id}")
                            continue
                        
                        # Convert goal pieces to simple format
                        simple_goal_pieces = []
                        for piece in goal_pieces:
                            simple_goal_pieces.append({
                                'x': piece.x, 'y': piece.y, 'w': piece.w, 'h': piece.h, 'angle': piece.angle
                            })
                        
                        level = EasyLevel(
                            design_id=design_id,
                            url=url,
                            goal_area_x=goal_area.x,
                            goal_area_y=goal_area.y, 
                            goal_area_w=goal_area.w,
                            goal_area_h=goal_area.h,
                            goal_area_angle=goal_area.angle,
                            goal_pieces=simple_goal_pieces,
                            expected_result=expected_result
                        )
                        
                        levels.append(level)
                        if level_count <= 3 or level_count % 10 == 0:
                            print(f"✅ Added level {design_id}: {'SOLVE' if expected_result else 'FAIL'}")
                        
                    except Exception as e:
                        print(f"⏭️  Skipped level {design_id} due to error: {e}")
                        continue
                        
                except Exception as e:
                    print(f"⏭️  Skipped line {line_num} due to error: {e}")
                    continue
    
    print(f"🎯 Found {len(levels)} easy levels (processed {level_count} total)")
    print(f"📊 Dataset: {solve_count} SOLVE + {fail_count} FAIL cases = {solve_count + fail_count} expected results")
    
    return levels
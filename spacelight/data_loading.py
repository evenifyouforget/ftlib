"""Data loading for Spacelight Tournament"""

import csv
import itertools
import re
import sys
from collections import Counter
from pathlib import Path
from typing import List

# Add test directory to path for imports  
ftlib_root = Path(__file__).parent.parent  # Go up from spacelight/ to ftlib/
test_dir = ftlib_root / "test"
sys.path.insert(0, str(test_dir))

from get_design import retrieveDesign, retrieveLevel, designDomToStruct
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
    line_count = 0
    reject_reason_counts = Counter()
    
    with open(tsv_path, newline='') as file:
        reader = csv.reader(file, delimiter='\t')
        # tsv to 2D list
        fc_data = list(reader)
    
    if True:
        for row in fc_data:
            line_count += 1
            if max_levels and len(levels) >= max_levels:
                print(f"🛑 Reached max_levels limit ({max_levels})")
                break
                
            if True:
                try:
                    # parse row
                    level_id, design_id, solve_ticks, design_max_ticks, user_comment, spectre_override, cpu_name, p2_solve_ticks, *_ = itertools.chain(row, [None]*10)
                    level_id = extract_design_id(level_id)
                    design_id = extract_design_id(design_id)
                    solve_ticks = int_or_none(solve_ticks)
                    design_max_ticks = int_or_none(design_max_ticks)
                    if solve_ticks is None and design_max_ticks is None:
                        reject_reason_counts['no expected result'] += 1
                        continue  # Skip if no expected result
                    # generate basic data
                    design_uid = f'D{design_id}' if design_id else f'L{level_id}'
                    # placeholder
                    design_xml = retrieveDesign(design_id) if design_id else retrieveLevel(level_id)
                    design_struct = designDomToStruct(design_xml)
                    
                    expected_result = solve_ticks is not None
                    
                    if level_count <= 3 or level_count % 10 == 0:  # Show first 3, then every 10th
                        print(f"📦 Processing {design_id} (expect: {'SOLVE' if expected_result else 'FAIL'})...")
                    level_count += 1
                    
                    try:
                        goal_area = design_struct.goal_area
                        goal_pieces = design_struct.goal_pieces
                        
                        # Single goal rectangle and nothing else
                        reject_reason = None
                        reject_reason = reject_reason or len(design_struct.level_pieces) != 0 and 'has level pieces'
                        reject_reason = reject_reason or len(design_struct.design_pieces) != 0 and 'has design pieces'
                        
                        # Convert goal pieces to simple format
                        simple_goal_pieces = []
                        for piece in goal_pieces:
                            reject_reason = reject_reason or piece.type_id != 4 and 'non-rectangle goal piece'
                            simple_goal_pieces.append({
                                'x': piece.x, 'y': piece.y, 'w': piece.w, 'h': piece.h, 'angle': piece.angle
                            })
                        reject_reason = reject_reason or len(simple_goal_pieces) != 1 and 'not exactly 1 goal piece'
                        
                        if reject_reason:
                            reject_reason_counts[reject_reason] += 1
                            continue
                        
                        level = EasyLevel(
                            design_id=design_id,
                            url=None,
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
    
    print(f"🎯 Found {len(levels)} easy levels (processed {level_count} levels, {line_count} lines)")
    solve_count = sum(1 for level in levels if level.expected_result)
    fail_count = len(levels) - solve_count
    print(f"📊 Dataset: {solve_count} SOLVE + {fail_count} FAIL cases = {solve_count + fail_count} expected results")
    
    print('# Sample - first 10 levels')
    for level in levels[:10]:
        print(f"   - Level {level.design_id}: expects {'SOLVE' if level.expected_result else 'FAIL'}")
    
    print('# Rejection Reasons:')
    for reason, count in reject_reason_counts.items():
        print(f"   - {reason}: {count} levels")
    
    return levels
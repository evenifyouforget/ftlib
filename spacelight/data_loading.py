"""Data loading and ftlib integration for Spacelight Tournament"""

import math
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add test directory to path for imports
current_dir = Path(__file__).parent.parent
test_dir = current_dir / "test"
sys.path.insert(0, str(test_dir))

from get_design import retrieveDesign, designDomToStruct, fcsim_strtod
from .core import EasyLevel


def load_easy_levels_from_tsv(max_levels: int = None) -> List[EasyLevel]:
    """Load easy levels from fc_data.tsv file"""
    print("📥 Loading levels from fc_data.tsv...")
    
    tsv_path = current_dir / "test" / "fc_data.tsv"
    
    levels = []
    level_count = 0
    
    with open(tsv_path, 'r') as file:
        for line_num, line in enumerate(file, 1):
            if max_levels and len(levels) >= max_levels:
                print(f"🛑 Reached max_levels limit ({max_levels})")
                break
                
            if line.strip() and not line.startswith('#'):
                try:
                    parts = line.strip().split('\t')
                    url = parts[0]
                    
                    print(f"📦 Processing {url}...")
                    level_count += 1
                    
                    if "designId=" in url:
                        design_id = url.split("designId=")[1].split("&")[0]
                    elif "levelId=" in url:
                        design_id = url.split("levelId=")[1].split("&")[0]
                    else:
                        print(f"⏭️  Skipped: Cannot extract design ID from {url}")
                        continue
                    
                    try:
                        dom = retrieveDesign(design_id)
                        design_struct = designDomToStruct(dom)
                        
                        goal_area = design_struct.goal_area
                        goal_pieces = design_struct.goal_pieces
                        
                        # Skip if too complex (>1 goal piece or complex goal area)
                        if len(goal_pieces) > 1:
                            print(f"⏭️  Skipped complex level: {design_id}")
                            continue
                        if goal_area.w > 150 or goal_area.h > 150:
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
                            goal_pieces=simple_goal_pieces
                        )
                        
                        levels.append(level)
                        print(f"✅ Added easy level: {design_id}")
                        
                    except Exception as e:
                        print(f"⏭️  Skipped level {design_id} due to error: {e}")
                        continue
                        
                except Exception as e:
                    print(f"⏭️  Skipped line {line_num} due to error: {e}")
                    continue
    
    print(f"🎯 Found {len(levels)} easy levels")
    print(f"📊 Statistics:")
    print(f"   • Total levels processed: {level_count}")
    print(f"   • Goal rectangle levels found: {len(levels)}")
    if level_count > 0:
        print(f"   • Goal rectangle ratio: {len(levels)/level_count*100:.1f}%")
    
    return levels


def determine_expected_results_with_ftlib(easy_levels: List[EasyLevel]) -> List[EasyLevel]:
    """Determine expected results using ftlib's fcsim_in_area function"""
    print("🔍 Determining expected results with ftlib...")
    
    sys.path.insert(0, str(current_dir / "test"))
    from get_ftlib_dir import get_ftlib_dir
    
    ftlib_path = get_ftlib_dir()
    build_dir = ftlib_path / "build"
    sys.path.insert(0, str(build_dir))
    
    try:
        import ftlib
    except ImportError as e:
        print(f"❌ Could not import ftlib: {e}")
        print("   Make sure ftlib is built: cd ../ftlib && scons")
        return easy_levels
    
    solve_count = 0
    fail_count = 0
    
    for level in easy_levels:
        try:
            for piece in level.goal_pieces:
                result = ftlib.fcsim_in_area(
                    piece['x'], piece['y'], piece['w'], piece['h'], piece['angle'],
                    level.goal_area_x, level.goal_area_y, 
                    level.goal_area_w, level.goal_area_h, level.goal_area_angle
                )
                
                level.expected_result = bool(result)
                if result:
                    solve_count += 1
                    print(f"✅ Level {level.design_id}: SOLVES")
                else:
                    fail_count += 1
                    print(f"❌ Level {level.design_id}: FAILS")
                break  # Only check first goal piece for simple levels
                
        except Exception as e:
            print(f"⚠️  Could not determine result for {level.design_id}: {e}")
            level.expected_result = None
    
    print(f"📊 Expected results: {solve_count} solve, {fail_count} fail")
    
    return easy_levels
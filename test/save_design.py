from typing import Optional
from collections import namedtuple
import requests
from xml.dom import minidom
from get_design import FCDesignStruct, fcsim_piece_types

FCLoginResult = namedtuple('FCLoginResult', ['success', 'user_id', 'username', 'email', 'md5password', 'error'])

def fc_login(username: str, password: str) -> FCLoginResult:
    """
    Login to FC servers and return user credentials.
    
    Returns:
        FCLoginResult with success status and user info if successful
    """
    url = "http://www.fantasticcontraption.com/logIn.php"
    params = {'userName': username, 'password': password}

    try:
        response = requests.post(url, data=params)
        dom = minidom.parseString(response.text)
        
        try:
            # Check for error first
            error_nodes = dom.firstChild.getElementsByTagName('error')
            if error_nodes:
                error_msg = error_nodes[0].firstChild.toxml()
                return FCLoginResult(success=False, user_id=None, username=None, email=None, md5password=None, error=error_msg)
            
            # Parse successful login
            username_node = dom.firstChild.getElementsByTagName('userName')[0].firstChild.toxml()
            user_id_str = dom.firstChild.getElementsByTagName('userId')[0].firstChild.toxml()
            md5password_node = dom.firstChild.getElementsByTagName('password')[0].firstChild.toxml()
            email_node = dom.firstChild.getElementsByTagName('email')[0].firstChild.toxml()
            
            return FCLoginResult(
                success=True,
                user_id=int(user_id_str),
                username=username_node,
                email=email_node,
                md5password=md5password_node,
                error=None
            )
        except Exception as parse_error:
            return FCLoginResult(success=False, user_id=None, username=None, email=None, md5password=None, error=f"Parse error: {parse_error}")
            
    except Exception as e:
        return FCLoginResult(success=False, user_id=None, username=None, email=None, md5password=None, error=f"Network error: {e}")

def save_design(design_struct: FCDesignStruct, user_id: Optional[int] = None, name: str = "Test Design", description: str = "") -> Optional[int]:
    """
    Upload a design to the FC servers.
    If it is successful, it will return the new design ID.
    
    Args:
        design_struct: The design to save
        user_id: User ID from fc_login() - REQUIRED for saves to work
        name: Name for the design (default: "Test Design") 
        description: Description for the design (default: "")
    
    Returns:
        New design ID if successful, None if failed
    """
    if user_id is None:
        raise ValueError('user_id is required')
    
    # Convert FCDesignStruct to XML DOM
    dom = _struct_to_save_design_xml(design_struct, user_id, name, description)
    
    # Send POST request to FC servers
    url = "http://www.fantasticcontraption.com/saveDesign.php"
    params = {'xml': dom.toxml()}
    
    try:
        response = requests.post(url, data=params)
        result = response.text.strip()
        
        # Parse response - FC returns the new design ID as a number, or error message
        if result.isdigit():
            return int(result)
        else:
            return None
    except Exception as e:
        return None

def _struct_to_save_design_xml(design_struct: FCDesignStruct, user_id: Optional[int], name: str, description: str) -> minidom.Document:
    """Convert FCDesignStruct to FC saveDesign XML format"""
    dom = minidom.Document()
    
    # Root element
    save_design = dom.createElement("saveDesign")
    dom.appendChild(save_design)
    
    # Design metadata
    name_elem = dom.createElement("name")
    name_elem.appendChild(dom.createTextNode(name))
    save_design.appendChild(name_elem)
    
    description_elem = dom.createElement("description")
    description_elem.appendChild(dom.createTextNode(description))
    save_design.appendChild(description_elem)
    
    user_id_elem = dom.createElement("userId")
    if user_id is not None:
        user_id_elem.appendChild(dom.createTextNode(str(user_id)))
    save_design.appendChild(user_id_elem)
    
    level_id_elem = dom.createElement("levelId")
    if design_struct.base_level_id is not None:
        level_id_elem.appendChild(dom.createTextNode(str(design_struct.base_level_id)))
    save_design.appendChild(level_id_elem)
    
    is_solution_elem = dom.createElement("isSolution")
    is_solution_elem.appendChild(dom.createTextNode("0"))
    save_design.appendChild(is_solution_elem)
    
    # Level structure
    level = dom.createElement("level")
    save_design.appendChild(level)
    
    # Level blocks
    level_blocks = dom.createElement("levelBlocks")
    level.appendChild(level_blocks)
    for piece in design_struct.level_pieces:
        level_blocks.appendChild(_piece_struct_to_xml(piece, dom))
    
    # Player blocks (design pieces + goal pieces)
    player_blocks = dom.createElement("playerBlocks")
    level.appendChild(player_blocks)
    for piece in design_struct.goal_pieces + design_struct.design_pieces:
        player_blocks.appendChild(_piece_struct_to_xml(piece, dom))
    
    # Build area
    level.appendChild(_area_struct_to_xml(design_struct.build_area, "start", dom))
    
    # Goal area
    level.appendChild(_area_struct_to_xml(design_struct.goal_area, "end", dom))
    
    return dom

def _piece_struct_to_xml(piece, dom) -> minidom.Element:
    """Convert FCPieceStruct to XML element"""
    # Map fcsim piece type to XML piece type name
    type_mapping = {
        fcsim_piece_types.FCSIM_STATIC_RECT.value: "StaticRectangle",
        fcsim_piece_types.FCSIM_STATIC_CIRC.value: "StaticCircle", 
        fcsim_piece_types.FCSIM_DYNAMIC_RECT.value: "DynamicRectangle",
        fcsim_piece_types.FCSIM_DYNAMIC_CIRC.value: "DynamicCircle",
        fcsim_piece_types.FCSIM_GP_RECT.value: "JointedDynamicRectangle",
        fcsim_piece_types.FCSIM_GP_CIRC.value: "NoSpinWheel",
        fcsim_piece_types.FCSIM_UPW.value: "NoSpinWheel",
        fcsim_piece_types.FCSIM_CW.value: "ClockwiseWheel",
        fcsim_piece_types.FCSIM_CCW.value: "CounterClockwiseWheel",
        fcsim_piece_types.FCSIM_WATER.value: "HollowRod",
        fcsim_piece_types.FCSIM_WOOD.value: "SolidRod",
    }
    
    xml_type = type_mapping.get(piece.type_id, "StaticRectangle")
    node = dom.createElement(xml_type)
    
    # Add ID attribute for jointed pieces (before any child nodes)
    if piece.piece_id is not None and piece.piece_id != 65535:
        node.setAttribute("id", str(piece.piece_id))
    
    # Rotation (if angle != 0)
    if piece.angle != 0:
        rotation = dom.createElement("rotation")
        node.appendChild(rotation)
        rotation.appendChild(dom.createTextNode(str(piece.angle)))
    
    # Position
    position = dom.createElement("position")
    node.appendChild(position)
    
    x = dom.createElement("x")
    position.appendChild(x)
    
    y = dom.createElement("y")
    position.appendChild(y)
    
    # Width and height
    width = dom.createElement("width")
    node.appendChild(width)
    
    height = dom.createElement("height")
    node.appendChild(height)
    
    # Goal block marker 
    goal_block = dom.createElement("goalBlock")
    node.appendChild(goal_block)
    
    # Joints
    joints = dom.createElement("joints")
    node.appendChild(joints)
    
    # Fill in the actual values
    w, h = piece.w, piece.h
    if piece.type_id in (fcsim_piece_types.FCSIM_STATIC_CIRC.value, fcsim_piece_types.FCSIM_DYNAMIC_CIRC.value):
        # Circles use radius in XML, but our struct stores diameter
        w, h = w / 2, h / 2
    
    x.appendChild(dom.createTextNode(str(piece.x)))
    y.appendChild(dom.createTextNode(str(piece.y)))
    width.appendChild(dom.createTextNode(str(w)))
    height.appendChild(dom.createTextNode(str(h)))
    
    # Goal block
    is_goal = piece.type_id in (fcsim_piece_types.FCSIM_GP_RECT.value, fcsim_piece_types.FCSIM_GP_CIRC.value)
    goal_block.appendChild(dom.createTextNode("true" if is_goal else "false"))
    
    # Add joints
    for joint_id in piece.joints:
        if joint_id != 65535:  # Skip invalid joint IDs
            jointed_to = dom.createElement("jointedTo")
            joints.appendChild(jointed_to)
            jointed_to.appendChild(dom.createTextNode(str(joint_id)))
    
    return node

def _area_struct_to_xml(area, area_type, dom) -> minidom.Element:
    """Convert area struct (build or goal area) to XML"""
    node = dom.createElement(area_type)
    
    # Position
    position = dom.createElement("position")
    node.appendChild(position)
    
    x = dom.createElement("x")
    position.appendChild(x)
    
    y = dom.createElement("y")
    position.appendChild(y)
    
    # Width and height
    width = dom.createElement("width")
    node.appendChild(width)
    
    height = dom.createElement("height")
    node.appendChild(height)
    
    # Goal block (always false for areas)
    goal_block = dom.createElement("goalBlock")
    node.appendChild(goal_block)
    
    # Empty joints
    joints = dom.createElement("joints")
    node.appendChild(joints)
    
    # Fill in values
    x.appendChild(dom.createTextNode(str(area.x)))
    y.appendChild(dom.createTextNode(str(area.y)))
    width.appendChild(dom.createTextNode(str(area.w)))
    height.appendChild(dom.createTextNode(str(area.h)))
    goal_block.appendChild(dom.createTextNode("false"))
    
    return node
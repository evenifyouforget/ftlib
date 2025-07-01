from enum import Enum
from collections import namedtuple
import requests
from xml.dom import minidom
from pathlib import Path

DISABLE_CACHE = 'DISABLE_CACHE'

class fcsim_piece_types(Enum):
    FCSIM_STATIC_RECT = 0
    FCSIM_STATIC_CIRC = 1
    FCSIM_DYNAMIC_RECT = 2
    FCSIM_DYNAMIC_CIRC = 3
    FCSIM_GP_RECT = 4
    FCSIM_GP_CIRC = 5
    FCSIM_UPW = 6
    FCSIM_CW = 7
    FCSIM_CCW = 8
    FCSIM_WATER = 9
    FCSIM_WOOD = 10

class fcxml_piece_types(Enum):
    StaticRectangle = 0
    StaticCircle = 1
    DynamicRectangle = 2
    DynamicCircle = 3
    JointedDynamicRectangle = 4
    FCSIM_GP_CIRC__SPECIAL_CASE = 5
    NoSpinWheel = 6
    ClockwiseWheel = 7
    CounterClockwiseWheel = 8
    HollowRod = 9
    SolidRod = 10

FCPieceStruct = namedtuple('FCPieceStruct', ['type_id', 'piece_id', 'x', 'y', 'w', 'h', 'angle', 'joints'])
FCDesignStruct = namedtuple('FCDesignStruct', ['name', 'base_level_id', 'goal_pieces', 'design_pieces', 'level_pieces', 'build_area', 'goal_area'])

def retrieveLevel(levelId, is_design=False, cache=None):
    # try to get it from cache first
    raw_text = None
    if cache != DISABLE_CACHE:
        if cache:
            cache_dir = Path(cache)
        else:
            cache_dir = Path() / '.fc_design_cache'
        cache_dir.mkdir(parents=True, exist_ok=True)
        design_uid = f'D{levelId}' if is_design else f'L{levelId}'
        design_file_path = cache_dir / design_uid
        if design_file_path.is_file():
            with open(design_file_path) as file:
                raw_text = file.read()

    if not raw_text:
        URL = "http://www.fantasticcontraption.com/retrieveLevel.php"

        # defining a params dict for the parameters to be sent to the API
        PARAMS = {'id' : levelId}

        if is_design:
            PARAMS['loadDesign'] = '1'

        # sending POST request and saving the response as response object
        r = requests.post(URL, data = PARAMS)

        raw_text = r.text

        # save to cache
        if cache != DISABLE_CACHE:
            with open(design_file_path, 'w') as file:
                file.write(raw_text)

    dom = minidom.parseString(raw_text)

    return dom

def retrieveDesign(designId):
    return retrieveLevel(designId, is_design=True)

def pieceDomToStruct(dom):
    xml_type = dom.nodeName
    # get numerical piece type
    try:
        piece_type = getattr(fcxml_piece_types, xml_type)
    except AttributeError:
        piece_type = None
    if piece_type == fcxml_piece_types.NoSpinWheel and dom.getElementsByTagName("goalBlock")[0].firstChild.toxml() == "true":
        piece_type = fcxml_piece_types.FCSIM_GP_CIRC__SPECIAL_CASE
    if piece_type is not None:
        piece_type = piece_type.value
    # get joints
    joints = []
    if len(dom.getElementsByTagName("joints")) > 0:
        for joint in dom.getElementsByTagName("joints")[0].getElementsByTagName("jointedTo"):
            joints.append(int(joint.firstChild.nodeValue))
    # get xywhr
    x = float(dom.getElementsByTagName("position")[0].getElementsByTagName("x")[0].firstChild.nodeValue)
    y = float(dom.getElementsByTagName("position")[0].getElementsByTagName("y")[0].firstChild.nodeValue)
    w = float(dom.getElementsByTagName("width")[0].firstChild.nodeValue)
    h = float(dom.getElementsByTagName("height")[0].firstChild.nodeValue)
    angle = 0
    if(len(dom.getElementsByTagName("rotation")) > 0):
        angle = float(dom.getElementsByTagName("rotation")[0].firstChild.nodeValue)
    # static circles and dynamic circles use radius instead of diameter like every other piece. let's fix that
    use_radius = piece_type in (fcsim_piece_types.FCSIM_STATIC_CIRC.value, fcsim_piece_types.FCSIM_DYNAMIC_CIRC.value)
    if use_radius:
        w *= 2
        h *= 2
    # return struct
    return FCPieceStruct(
        type_id=piece_type,
        piece_id=None,
        x=x,
        y=y,
        w=w,
        h=h,
        angle=angle,
        joints=joints,
        )

def designDomToStruct(dom):
    retrievelevel = dom.firstChild
    level = retrievelevel.getElementsByTagName("level")[0]
    # get name
    try:
        name = retrievelevel.getElementsByTagName("name")[0].firstChild.toxml()
    except:
        name = None
    # get level id this design is based on
    try:
        base_level_id = int(retrievelevel.getElementsByTagName("levelId")[0].firstChild.toxml())
    except:
        base_level_id = None
    # get pieces
    level_pieces = []
    goal_pieces = []
    design_pieces = []
    for element in level.getElementsByTagName("levelBlocks")[0].childNodes:
        if element.nodeType == 1: #1 = ELEMENT_NODE
            level_pieces.append(pieceDomToStruct(element))
    for element in level.getElementsByTagName("playerBlocks")[0].childNodes:
        if element.nodeType == 1: #1 = ELEMENT_NODE
            if(element.getElementsByTagName("goalBlock")[0].firstChild.toxml() == "true"):
                goal_pieces.append(pieceDomToStruct(element))
            else:
                design_pieces.append(pieceDomToStruct(element))
    # get areas
    build_area = pieceDomToStruct(level.getElementsByTagName("start")[0])
    goal_area = pieceDomToStruct(level.getElementsByTagName("end")[0])
    # return struct
    return FCDesignStruct(
        name=name,
        base_level_id=base_level_id,
        level_pieces=level_pieces,
        goal_pieces=goal_pieces,
        design_pieces=design_pieces,
        build_area=build_area,
        goal_area=goal_area,
        )
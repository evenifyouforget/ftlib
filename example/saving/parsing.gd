class_name Parsing

#static func is_block(parser: XMLParser) -> bool:
	#if parser.get_node_type() != XMLParser.NODE_ELEMENT:
		#return false
	#return parser.get_node_name() in ["StaticRectangle", "StaticCircle", "DynamicRectangle", "DynamicCircle", 
		#"JointedDynamicRectangle", "NoSpinWheel", "ClockwiseWheel", "CounterClockwiseWheel", "HollowRod", "SolidRod"]

const level_block_node_names: Array[String] = ["StaticRectangle", "StaticCircle", "DynamicRectangle", "DynamicCircle"]
const player_block_node_names: Array[String] = ["JointedDynamicRectangle", "NoSpinWheel", "ClockwiseWheel", "CounterClockwiseWheel", "HollowRod", "SolidRod"]
const block_node_names: Array[String] = level_block_node_names + player_block_node_names

#steps the parser until it finds an element matching the params
#node type must be in node_types, node name or data must be in node_names_or_datas (if applicable)
#if node_names_or_datas is [], any node name or data is accepted
#returns if found
#max_reads is the max number of steps allowed to find the matching node. if negative, infinite.
static func read_until(parser: XMLParser, node_types: Array[XMLParser.NodeType], node_names_or_datas: Array[String], min_reads: int, max_reads: int) -> bool:
	var reads: int = 0
	var err: Error = OK
	while err == OK:
		if reads >= min_reads:
			var nt: XMLParser.NodeType = parser.get_node_type()
			if nt in node_types:
				if len(node_names_or_datas) == 0:
					return true
				match nt:
					XMLParser.NODE_ELEMENT, XMLParser.NODE_ELEMENT_END, XMLParser.NODE_COMMENT, XMLParser.NODE_CDATA:
						if parser.get_node_name() in node_names_or_datas:
							return true
					XMLParser.NODE_TEXT:
						if parser.get_node_data() in node_names_or_datas:
							return true
					XMLParser.NODE_NONE, XMLParser.NODE_UNKNOWN, _:
						return true
		
		if max_reads >= 0 and reads >= max_reads:
			return false
		
		err = parser.read()
		reads += 1
	return false
	
#array contains [pass/fail, rect/error code]
#expects parser to be on the "position" element node
static func parse_xywh(parser: XMLParser) -> Array:
	var x: float
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["x"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1):
		push_error(); return [false, ERR_INVALID_DATA]
	x = FTBackend.strtod(parser.get_node_data()) #TODO: handle strtod fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["x"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	var y: float
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["y"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1):
		push_error(); return [false, ERR_INVALID_DATA]
	y = FTBackend.strtod(parser.get_node_data()) #TODO: handle strtod fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["y"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["position"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	var width: float
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["width"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1):
		push_error(); return [false, ERR_INVALID_DATA]
	width = FTBackend.strtod(parser.get_node_data()) #TODO: handle strtod fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["width"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	var height: float
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["height"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1):
		push_error(); return [false, ERR_INVALID_DATA]
	height = FTBackend.strtod(parser.get_node_data()) #TODO: handle strtod fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["height"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	return [true, FTRect.init(x, y, width, height)]

#expects the parser to be on the block element node	
static func parse_block(parser: XMLParser) -> Array:
	var type_str: String
	var type: int
	#if !read_until(parser, [XMLParser.NODE_ELEMENT], block_node_names, 0, 0): #double check?
		#push_error(); return [false, ERR_INVALID_DATA]
	type_str = parser.get_node_name()
	match type_str:
		"StaticRectangle":
			type = FTRender.PieceType_STATIC_RECT
		"StaticCircle":
			type = FTRender.PieceType_STATIC_CIRC
		"DynamicRectangle":
			type = FTRender.PieceType_DYNAMIC_RECT
		"DynamicCircle":
			type = FTRender.PieceType_DYNAMIC_CIRC
		"JointedDynamicRectangle":
			type = FTRender.PieceType_GP_RECT
		"NoSpinWheel":
			type = FTRender.PieceType_UPW #can also be GP_CIRC, set later if so
		"ClockwiseWheel":
			type = FTRender.PieceType_CW
		"CounterClockwiseWheel":
			type = FTRender.PieceType_CCW
		"HollowRod":
			type = FTRender.PieceType_WATER
		"SolidRod":
			type = FTRender.PieceType_WOOD
		_:
			push_error(); return [false, ERR_INVALID_DATA]
	
	var id: int = FTBackend.FCSIM_NO_JOINT #TODO: is this the right default value?
	if FTBackend.type_is_player(type):
		var id_str: String = parser.get_named_attribute_value_safe("id")
		if id_str == "":
			push_error(); return [false, ERR_INVALID_DATA]
		id = int(id_str) #TODO: make sure int parsing can't fail
	
	var rotation: float
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["rotation"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1):
		push_error(); return [false, ERR_INVALID_DATA]
	rotation = FTBackend.strtod(parser.get_node_data()) #TODO: handle strtod fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["rotation"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["position"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	var x: float
	var y: float
	var width: float
	var height: float
	var xywh_parsed: Array = parse_xywh(parser)
	if !xywh_parsed[0]:
		push_error(); return [false, ERR_INVALID_DATA]
	x = xywh_parsed[1].x; y = xywh_parsed[1].y; width = xywh_parsed[1].w; height = xywh_parsed[1].h
	if type in [FTRender.PieceType_STATIC_CIRC, FTRender.PieceType_DYNAMIC_CIRC]: #TODO: ensure this is the exact correct behavior
		width *= 2; height *= 2
	
	var goalBlock_str: String
	var goalBlock: bool
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["goalBlock"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1):
		push_error(); return [false, ERR_INVALID_DATA]
	goalBlock_str = parser.get_node_data() #TODO: handle strtod fail
	if goalBlock_str != "true" and goalBlock_str != "false":
		push_error(); return [false, ERR_INVALID_DATA]
	goalBlock = goalBlock_str == "true"
	if type == FTRender.PieceType_UPW && goalBlock:
		type = FTRender.PieceType_GP_CIRC
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["goalBlock"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	var no_joints: bool
	var joint1: int = FTBackend.FCSIM_NO_JOINT
	var joint2: int = FTBackend.FCSIM_NO_JOINT
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["joints"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	no_joints = parser.is_empty()
	if !no_joints: #TODO: garbage logic
		if !read_until(parser, [XMLParser.NODE_ELEMENT], ["jointedTo"], 1, 2):
			push_error(); return [false, ERR_INVALID_DATA]
		if !read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1):
			push_error(); return [false, ERR_INVALID_DATA]
		joint1 = int(parser.get_node_data())
		if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["jointedTo"], 1, 2):
			push_error(); return [false, ERR_INVALID_DATA]
		
		if !read_until(parser, [XMLParser.NODE_ELEMENT, XMLParser.NODE_ELEMENT_END], ["jointedTo", "joints"], 1, 2):
			push_error(); return [false, ERR_INVALID_DATA]
		if parser.get_node_type() == XMLParser.NODE_ELEMENT and parser.get_node_name() == "jointedTo": #either there's another joint
			if !read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1):
				push_error(); return [false, ERR_INVALID_DATA]
			joint2 = int(parser.get_node_data())
			if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["jointedTo"], 1, 2):
				push_error(); return [false, ERR_INVALID_DATA]
			if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["joints"], 1, 2):
				push_error(); return [false, ERR_INVALID_DATA]
		elif !(parser.get_node_type() == XMLParser.NODE_ELEMENT_END and parser.get_node_name() == "joints"): #or the joints are done
			push_error(); return [false, ERR_INVALID_DATA]
	
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], [type_str], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	return [true, FTBlock.init(type, id, x, y, width, height, rotation, joint1, joint2)]

#array contains [pass/fail, [is_start, rect]/error code]
static func parse_area(parser: XMLParser, area_name: String) -> Array:
	var type_str: String
	var is_start: bool
	type_str = parser.get_node_name()
	if type_str == area_name:
		is_start = type_str == "start"
	else:
		push_error(); return [false, ERR_INVALID_DATA]
	
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["position"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	var xywh_parsed = parse_xywh(parser)
	if !xywh_parsed[0]:
		push_error(); return [false, ERR_INVALID_DATA]
	
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], [type_str], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	return [true, [is_start, xywh_parsed[1]]]

#array contains [pass/fail, [levelId, levelNumber, name, tickCount, pieceCount, design]/error code]
static func parse_design(xml_buffer: PackedByteArray) -> Array:
	var parser = XMLParser.new()
	parser.open_buffer(xml_buffer)
	
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["retrieveLevel"], 0, 5): #not sure what max_reads should be
		push_error(); return [false, ERR_INVALID_DATA]
	
	var levelId: int
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["levelId"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1):
		push_error(); return [false, ERR_INVALID_DATA]
	levelId = int(parser.get_node_data()) #TODO: handle int fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["levelId"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	var has_level: bool
	var levelNumber = null #int or null
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["levelNumber"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	has_level = read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1)
	if has_level:
		levelId = int(parser.get_node_data()) #TODO: handle int fail
	var levelNumber_end_steps = 1 if has_level else 0
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["levelNumber"], levelNumber_end_steps, levelNumber_end_steps):
		push_error(); return [false, ERR_INVALID_DATA]
	
	var name: String
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["name"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1):
		push_error(); return [false, ERR_INVALID_DATA]
	name = parser.get_node_data()
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["name"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["level"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
		
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["levelBlocks"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	var blocks: Array[FTBlock]
	while true:
		var node_names: Array[String] = level_block_node_names.duplicate(); node_names.append("levelBlocks")
		if !read_until(parser, [XMLParser.NODE_ELEMENT, XMLParser.NODE_ELEMENT_END], node_names, 1, 2):
			push_error(); return [false, ERR_INVALID_DATA]
		if parser.get_node_type() == XMLParser.NODE_ELEMENT_END and parser.get_node_name() == "levelBlocks":
			break
		elif !(parser.get_node_type() == XMLParser.NODE_ELEMENT and parser.get_node_name() in level_block_node_names):
			push_error(); return [false, ERR_INVALID_DATA]
		var block_parsed: Array = parse_block(parser)
		if !block_parsed[0]:
			push_error(); return block_parsed
		blocks.append(block_parsed[1])
	
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["playerBlocks"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	while true:
		var node_names: Array[String] = player_block_node_names.duplicate(); node_names.append("playerBlocks")
		if !read_until(parser, [XMLParser.NODE_ELEMENT, XMLParser.NODE_ELEMENT_END], node_names, 1, 2):
			push_error(); return [false, ERR_INVALID_DATA]
		if parser.get_node_type() == XMLParser.NODE_ELEMENT_END and parser.get_node_name() == "playerBlocks":
			break
		elif !(parser.get_node_type() == XMLParser.NODE_ELEMENT and parser.get_node_name() in player_block_node_names):
			push_error(); return [false, ERR_INVALID_DATA]
		var block_parsed: Array = parse_block(parser)
		if !block_parsed[0]:
			push_error(); return block_parsed
		blocks.append(block_parsed[1])
	
	var start: Array
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["start"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	var start_parsed: Array = parse_area(parser, "start")
	if !start_parsed[0]:
		push_error(); return start_parsed
	start = start_parsed[1]
	
	var end: Array
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["end"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	var end_parsed: Array = parse_area(parser, "end")
	if !end_parsed[0]:
		push_error(); return end_parsed
	end = end_parsed[1]
	
	var tickCount: int
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["tickCount"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1):
		push_error(); return [false, ERR_INVALID_DATA]
	tickCount = int(parser.get_node_data()) #TODO: handle int fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["tickCount"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	var pieceCount: int
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["pieceCount"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1, 1):
		push_error(); return [false, ERR_INVALID_DATA]
	pieceCount = int(parser.get_node_data()) #TODO: handle int fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["pieceCount"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["level"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["retrieveLevel"], 1, 2):
		push_error(); return [false, ERR_INVALID_DATA]
	
	var design: FTDesign = FTDesign.new()
	design.set_blocks(blocks)
	design.set_build(start[1])
	design.set_goal(end[1])
	return [true, [levelId, levelNumber, name, tickCount, pieceCount, design]]

static func parse_debug(xml_buffer: PackedByteArray) -> FTDesign:
	var parser = XMLParser.new()
	parser.open_buffer(xml_buffer)
	
	var err = OK
	while err == OK:
		var type = parser.get_node_type()
		match type:
			XMLParser.NODE_NONE:
				print("None")
			XMLParser.NODE_ELEMENT:
				print("Element ", parser.get_node_name(), " ", parser.is_empty())
				var attributes_dict = {}
				for idx in range(parser.get_attribute_count()):
					attributes_dict[parser.get_attribute_name(idx)] = parser.get_attribute_value(idx)
				print("\tAttributes ", attributes_dict)
			XMLParser.NODE_ELEMENT_END:
				print("Element End ", parser.get_node_name())
			XMLParser.NODE_TEXT:
				print("Text ", parser.get_node_data())
			XMLParser.NODE_COMMENT:
				print("Comment")
			XMLParser.NODE_CDATA:
				print("Cdata")
			XMLParser.NODE_UNKNOWN:
				print("Unknown")
		
		err = parser.read()
	
	return FTDesign.new()

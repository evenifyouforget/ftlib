class_name Parsing

#static func is_block(parser: XMLParser) -> bool:
	#if parser.get_node_type() != XMLParser.NODE_ELEMENT:
		#return false
	#return parser.get_node_name() in ["StaticRectangle", "StaticCircle", "DynamicRectangle", "DynamicCircle", 
		#"JointedDynamicRectangle", "NoSpinWheel", "ClockwiseWheel", "CounterClockwiseWheel", "HollowRod", "SolidRod"]

const block_node_names: Array[String] = ["StaticRectangle", "StaticCircle", "DynamicRectangle", "DynamicCircle", 
		"JointedDynamicRectangle", "NoSpinWheel", "ClockwiseWheel", "CounterClockwiseWheel", "HollowRod", "SolidRod"]

#steps the parser until it finds an element matching the params
#node type must be in node_types, node name or data must be in node_names_or_datas (if applicable)
#if node_names_or_datas is [], any node name or data is accepted
#returns if found
#max_reads is the max number of steps allowed to find the matching node. if negative, infinite.
static func read_until(parser: XMLParser, node_types: Array[XMLParser.NodeType], node_names_or_datas: Array[String], max_reads: int) -> bool:
	var reads: int = 0
	var err: Error = OK
	while err == OK and (max_reads < 0 or reads <= max_reads):
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
		parser.read()
		reads += 1
	return false

static func parse_block(parser: XMLParser) -> Array: #expects the parser to be on the block element node	
	var type_str: String
	var type: int
	if !read_until(parser, [XMLParser.NODE_ELEMENT], block_node_names, 0):
		push_error("HI"); return [false, ERR_INVALID_DATA]
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
			push_error("HI"); return [false, ERR_INVALID_DATA]
	
	var id: int = FTBackend.FCSIM_NO_JOINT #TODO: is this the right default value?
	if FTBackend.type_is_player(type):
		var id_str: String = parser.get_named_attribute_value_safe("id")
		if id_str == "":
			push_error("HI"); return [false, ERR_INVALID_DATA]
		id = int(id_str) #TODO: make sure int parsing can't fail
	
	var rotation: float
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["rotation"], 2):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	rotation = FTBackend.strtod(parser.get_node_data()) #TODO: handle strtod fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["rotation"], 1):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["position"], 2):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	
	var x: float
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["x"], 2):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	x = FTBackend.strtod(parser.get_node_data()) #TODO: handle strtod fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["x"], 1):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	
	var y: float
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["y"], 2):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	y = FTBackend.strtod(parser.get_node_data()) #TODO: handle strtod fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["y"], 1):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["position"], 2):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	
	var width: float
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["width"], 2):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	width = FTBackend.strtod(parser.get_node_data()) #TODO: handle strtod fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["width"], 1):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	
	var height: float
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["height"], 2):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	height = FTBackend.strtod(parser.get_node_data()) #TODO: handle strtod fail
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["height"], 1):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	
	var goalBlock_str: String
	var goalBlock: bool
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["goalBlock"], 2):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	if !read_until(parser, [XMLParser.NODE_TEXT], [], 1):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	goalBlock_str = parser.get_node_data() #TODO: handle strtod fail
	if goalBlock_str != "true" and goalBlock_str != "false":
		push_error("HI"); return [false, ERR_INVALID_DATA]
	goalBlock = goalBlock_str == "true"
	if type == FTRender.PieceType_UPW && goalBlock:
		type = FTRender.PieceType_GP_CIRC
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["goalBlock"], 1):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	
	var no_joints: bool
	var joint1: int = FTBackend.FCSIM_NO_JOINT
	var joint2: int = FTBackend.FCSIM_NO_JOINT
	if !read_until(parser, [XMLParser.NODE_ELEMENT], ["joints"], 2):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	no_joints = parser.is_empty()
	if !no_joints: #TODO: garbage logic
		if !read_until(parser, [XMLParser.NODE_ELEMENT], ["jointedTo"], 2):
			push_error("HI"); return [false, ERR_INVALID_DATA]
		if !read_until(parser, [XMLParser.NODE_TEXT], [], 1):
			push_error("HI"); return [false, ERR_INVALID_DATA]
		joint1 = int(parser.get_node_data())
		if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["jointedTo"], 1):
			push_error("HI"); return [false, ERR_INVALID_DATA]
		
		if !read_until(parser, [XMLParser.NODE_ELEMENT, XMLParser.NODE_ELEMENT_END], ["jointedTo", "joints"], 2):
			push_error("HI"); return [false, ERR_INVALID_DATA]
		if parser.get_node_type() == XMLParser.NODE_ELEMENT and parser.get_node_name() == "jointedTo": #either there's another joint
			if !read_until(parser, [XMLParser.NODE_TEXT], [], 1):
				push_error("HI"); return [false, ERR_INVALID_DATA]
			joint2 = int(parser.get_node_data())
			if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["jointedTo"], 1):
				push_error("HI"); return [false, ERR_INVALID_DATA]
			if !read_until(parser, [XMLParser.NODE_ELEMENT_END], ["joints"], 2):
				push_error("HI"); return [false, ERR_INVALID_DATA]
		elif !(parser.get_node_type() == XMLParser.NODE_ELEMENT_END and parser.get_node_name() == "joints"): #or the joints are done
			push_error("HI"); return [false, ERR_INVALID_DATA]
	
	if !read_until(parser, [XMLParser.NODE_ELEMENT_END], [type_str], 2):
		push_error("HI"); return [false, ERR_INVALID_DATA]
	
	push_error("HI"); return [true, FTBlock.init(type, id, x, y, width, height, rotation, joint1, joint2)]

static func parse_design(xml_buffer: PackedByteArray) -> FTDesign:
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
	
#static func parse_design(xml_buffer: PackedByteArray):
	#var parser = XMLParser.new()
	#parser.open_buffer(xml_buffer)
	#while parser.read() != ERR_FILE_EOF:
		#if parser.get_node_type() == XMLParser.NODE_ELEMENT:
			#var node_name = parser.get_node_name()
			#var attributes_dict = {}
			#for idx in range(parser.get_attribute_count()):
				#attributes_dict[parser.get_attribute_name(idx)] = parser.get_attribute_value(idx)
			#print("The ", node_name, " element has the following attributes: ", attributes_dict)

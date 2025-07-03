extends Node

func _ready() -> void:
	#var design = await Requests.retrieve_design(12708607, false)
	#print(design[1].get_string_from_utf8())
	#Parsing.parse_design(design[1])
	
	var xml: String = """
<StaticRectangle>
	<rotation>0</rotation>
	<position>
		<x>-519.05</x2>
		<y>-169.25</y>
	</position>
	<width>50</width>
	<height>50</height>
	<goalBlock>false</goalBlock>
	<joints/>
</StaticRectangle>
"""
	var buffer: PackedByteArray = xml.to_utf8_buffer()
	
	Parsing.parse_design(buffer)
	
	var parser = XMLParser.new()
	parser.open_buffer(buffer)
	Parsing.read_until(parser, [XMLParser.NODE_ELEMENT], [], -1)
	var read = Parsing.parse_block(parser)
	var block: FTBlock = read[1]
	print(read[0], " ", block.type, " ", block.id, " ", block.x, " ", block.y, " ", block.w, " ", block.h, " ", block.angle, " ", block.joint_1, " ", block.joint_2)

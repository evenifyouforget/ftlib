extends Node
class_name Test

const xml: String = """
<?xml version="1.0"?><retrieveLevel>
<levelId>688082</levelId>
<levelNumber></levelNumber>
<name>xml test</name>
<level>
	<levelBlocks>
	  <StaticRectangle>
		<rotation>0</rotation>
		<position>
		  <x>-519.05</x>
		  <y>-169.25</y>
		</position>
		<width>50</width>
		<height>50</height>
		<goalBlock>false</goalBlock>
		<joints/>
	  </StaticRectangle>
	  <StaticCircle>
		<rotation>0</rotation>
		<position>
		  <x>-430.2</x>
		  <y>-157.95000000000002</y>
		</position>
		<width>50</width>
		<height>50</height>
		<goalBlock>false</goalBlock>
		<joints/>
	  </StaticCircle>
	  <DynamicCircle>
		<rotation>0</rotation>
		<position>
		  <x>-176.3</x>
		  <y>-152.3</y>
		</position>
		<width>50</width>
		<height>50</height>
		<goalBlock>false</goalBlock>
		<joints/>
	  </DynamicCircle>
	  <DynamicRectangle>
		<rotation>0</rotation>
		<position>
		  <x>-62.05</x>
		  <y>-157.95</y>
		</position>
		<width>50</width>
		<height>50</height>
		<goalBlock>false</goalBlock>
		<joints/>
	  </DynamicRectangle>
	</levelBlocks>
	<playerBlocks>
	  <NoSpinWheel id="0">
		<rotation>0</rotation>
		<position>
		  <x>-341.3499999999999</x>
		  <y>-157.95000000000002</y>
		</position>
		<width>40</width>
		<height>40</height>
		<goalBlock>true</goalBlock>
		<joints/>
	  </NoSpinWheel>
	  <JointedDynamicRectangle id="1">
		<rotation>0</rotation>
		<position>
		  <x>-277.84999999999997</x>
		  <y>-155.15</y>
		</position>
		<width>50</width>
		<height>50</height>
		<goalBlock>true</goalBlock>
		<joints/>
	  </JointedDynamicRectangle>
	  <ClockwiseWheel id="2">
		<rotation>0</rotation>
		<position>
		  <x>-375</x>
		  <y>-66.7</y>
		</position>
		<width>40</width>
		<height>40</height>
		<goalBlock>false</goalBlock>
		<joints/>
	  </ClockwiseWheel>
	  <CounterClockwiseWheel id="3">
		<rotation>0</rotation>
		<position>
		  <x>-267.85</x>
		  <y>-63.65</y>
		</position>
		<width>40</width>
		<height>40</height>
		<goalBlock>false</goalBlock>
		<joints/>
	  </CounterClockwiseWheel>
	  <NoSpinWheel id="4">
		<rotation>0</rotation>
		<position>
		  <x>-163.75</x>
		  <y>-46.5</y>
		</position>
		<width>40</width>
		<height>40</height>
		<goalBlock>false</goalBlock>
		<joints/>
	  </NoSpinWheel>
	  <HollowRod id="5">
		<rotation>-1.1295690307569937</rotation>
		<position>
		  <x>-358.17499999999995</x>
		  <y>-102.32500000000002</y>
		</position>
		<width>78.79647834770287</width>
		<height>4</height>
		<goalBlock>false</goalBlock>
		<joints>
		  <jointedTo>2</jointedTo>
		  <jointedTo>0</jointedTo>
		</joints>
	  </HollowRod>
	  <SolidRod id="6">
		<rotation>1.431837559523214</rotation>
		<position>
		  <x>-272.85</x>
		  <y>-119.4</y>
		</position>
		<width>72.1959140118054</width>
		<height>8</height>
		<goalBlock>false</goalBlock>
		<joints>
		  <jointedTo>1</jointedTo>
		  <jointedTo>3</jointedTo>
		</joints>
	  </SolidRod>
	</playerBlocks>
	<start>
	  <position>
		<x>-191.85</x>
		<y>-69.1</y>
	  </position>
	  <width>947.9</width>
	  <height>411.9</height>
	</start>
	<end>
	  <position>
		<x>150</x>
		<y>50</y>
	  </position>
	  <width>200</width>
	  <height>200</height>
	</end>
	<tickCount>0</tickCount>
	<pieceCount>5</pieceCount>
  </level>
</retrieveLevel>
"""

#func _ready() -> void:
	#var xml = await Requests.retrieve_design(12708607, false)
	#print(xml)

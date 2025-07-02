extends Node

func _ready() -> void:
	var design = await Requests.retrieve_design(12707913)
	print(design[1])

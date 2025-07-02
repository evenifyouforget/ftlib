extends Node

const timeout = 5

func retrieve_design(design_id) -> Array:
	var http = HTTPRequest.new()
	http.timeout = timeout
	add_child(http)
	
	var ok: bool #if it's returning an error or the design
	var data #either an error code or design xml
	
	while true: #loop so cleanup only happens once
		var url: String = "http://www.fantasticcontraption.com/retrieveLevel.php"
		var design_id_str: String = "%d" % design_id

		var headers: Array = ["Content-Type: application/x-www-form-urlencoded"]
		var body: String = "id=%s&loadDesign=1" % design_id
		
		var error = http.request(url, headers, HTTPClient.METHOD_POST, body)
		if error != OK:
			ok = false
			data = error
			break
		
		var reply: Array = await http.request_completed
		var reply_result: int = reply[0]
		var reply_response_code: int = reply[1]
		var reply_headers: PackedStringArray = reply[2]
		var reply_body: PackedByteArray = reply[3]
		
		if reply_response_code != HTTPClient.RESPONSE_OK:
			ok = false
			data = ERR_CONNECTION_ERROR
			break
		
		var response_text = reply_body.get_string_from_utf8()
		ok = true
		data = response_text
		break
	
	http.queue_free()
	return [ok, data]

extends Node

const timeout = 5

#returns [pass/fail, design/error code]
func retrieve_design(design_id: int, as_string: bool) -> Array:
	var http = HTTPRequest.new()
	http.timeout = timeout
	add_child(http)
	
	var ok: bool #if it's returning an error or the design
	var data #either an error code or design xml
	
	while true: #loop so cleanup only happens once
		var url: String = "http://www.fantasticcontraption.com/retrieveLevel.php"

		var headers: Array = ["Content-Type: application/x-www-form-urlencoded"]
		var body: String = "id=%s&loadDesign=1" % design_id
		
		var error = http.request(url, headers, HTTPClient.METHOD_POST, body)
		if error != OK:
			push_error()
			ok = false
			data = error
			break
		
		var reply: Array = await http.request_completed
		#var reply_result: int = reply[0]
		var reply_response_code: int = reply[1]
		#var reply_headers: PackedStringArray = reply[2]
		var reply_body: PackedByteArray = reply[3]
		
		if reply_response_code != HTTPClient.RESPONSE_OK:
			push_error()
			ok = false
			data = ERR_CONNECTION_ERROR
			break
		
		ok = true
		data = reply_body
		if as_string:
			data = data.get_string_from_utf8()
		break
	
	http.queue_free()
	return [ok, data]

<!--
	Achtung das ist nur ein Minimalbeispiel wie man das mit PHP machen könnte
	Autor: Fliiiix https://twitter.com/l33tname, https://github.com/fliiiix/
	Require: Die php-curl extention
	Was ist nicht gemacht: Richtiges Error-handling, Schönes Layout
	First Steps: $username $password $prestUUID setzen

	Lizenz:
    DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
            Version 2, December 2004 

	 Copyright (C) 2004 Fliiiix <l33tname@outlook.com> 

	 Everyone is permitted to copy and distribute verbatim or modified 
	 copies of this license document, and changing it is allowed as long 
	 as the name is changed. 

	            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
	   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 

	  0. You just DO WHAT THE FUCK YOU WANT TO.
-->
<?php 
	$username = "";
	$password = "";
	$prestUUID = "";


	$error = "";
	$apiUrl = "https://auphonic.com/api/simple/productions.json";

	$error_types = array(
		1=>'The uploaded file exceeds the upload_max_filesize directive in php.ini.',
		'The uploaded file exceeds the MAX_FILE_SIZE directive that was specified in the HTML form.',
		'The uploaded file was only partially uploaded.',
		'No file was uploaded.',
		6=>'Missing a temporary folder.',
		'Failed to write file to disk.',
		'A PHP extension stopped the file upload.'
	); 

	if ($username == "" || $password == "" || $prestUUID == "") {
		$error .= "First Steps: username password prestUUID setzen";
	}

	if (isset($_FILES["file"]["tmp_name"]) && $_FILES["file"]["tmp_name"] != "" && $_FILES["file"]["error"] == 0) {
		move_uploaded_file($_FILES["file"]["tmp_name"], sys_get_temp_dir() . "/" . $_FILES["file"]["name"]);
		// Initializing curl
		$ch = curl_init();

		//Setup 
		$data = array(
			"preset" => $prestUUID, 
			"title" => explode("." , $_FILES["file"]["name"])[0],
			"input_file" => "@" . sys_get_temp_dir() . "/" . $_FILES["file"]["name"],
			"action" => "start"
		);

		// curl options & data
		$options = array(
			CURLOPT_URL => $apiUrl,
			CURLOPT_USERPWD => $username . ":" . $password,   // authentication
			CURLOPT_POST => true,
			CURLOPT_POSTFIELDS => $data
		);
		 
		// Setting curl options
		curl_setopt_array($ch, $options);
		 
		// Getting results
		if(curl_exec($ch) === false)
		{
		    $error .= "<br> Curl-Fehler: " . curl_error($ch);
		}

		//free memory
		curl_close($ch);

		//Delete file
		unlink(sys_get_temp_dir() . "/" . $_FILES["file"]["name"]);
	}
	if (isset($_FILES["file"]["error"]) && $_FILES["file"]["error"] > 0)
	{
		$error .= "<br> File Error: " . $error_types[$_FILES["file"]["error"]];
	}
 ?>
 <html>
 <head>
 	<title>Auphonic PHP</title>
 </head>
 <body>
 	<?php 
 		if ($error != "") {
 			echo($error);
 		}
 	 ?>
 	<form action="upload_auphonic.php" method="post" enctype="multipart/form-data">
 		<input type="file" name="file" id="file">
		<input type="submit" id="submit" name="submit" value="Submit">
 	</form>
 </body>
 </html>
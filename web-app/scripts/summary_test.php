<?php


$postdata = file_get_contents("php://input");

$request = json_decode($postdata);
$docs=$request->response->docs;
$full_text="";
for($i=0;$i<count($docs);$i++){
	if($docs[$i]->lang=="en"){

		$full_text=$full_text.$docs[$i]->text_en_modified."\n";

	}

}


$file = 'file.txt';
// Open the file to get existing content
$current = file_get_contents($file);
// Append a new person to the file
$current .= $full_text;
// Write the contents back to the file
file_put_contents($file, $current);


$cmd='ots file.txt';
$summary= exec($cmd);

echo $summary;


?>
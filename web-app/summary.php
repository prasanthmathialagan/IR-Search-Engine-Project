<?php
header('Content-Type: text/json; charset=utf-8');

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

if(isset($_GET['titles'])){
	$titles=$_GET['titles'];
	$titles='"'.$titles.'"';
	$summary = exec('python scripts/summary.py '.$titles);
	

	$summary=json_decode($summary);

	
	$response = array('summary' => $summary->summary ,'image' => $summary->image);

	echo json_encode($response);


}

?>

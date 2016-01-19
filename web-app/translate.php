<?php

header('Content-Type: text/json; charset=utf-8');

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
require_once __DIR__.'/vendor/autoload.php';

use Yandex\Translate\Translator;
use Yandex\Translate\Exception;

if(isset($_GET['text'])) {
	$text=$_GET['text'];

	$key="trnsl.1.1.20151128T201030Z.26dda6883a34f555.9f891613514d6b32abf4346be07fd229183f1429";
	try {
		$translator = new Translator($key);
		$en = $translator->translate($text, 'en')->getResultText();
		$de = $translator->translate($text, 'de')->getResultText();
		$ru = $translator->translate($text, 'ru')->getResultText();
		$fr = $translator->translate($text, 'fr')->getResultText();
		$ar = $translator->translate($text, 'ar')->getResultText();

		$language = file_get_contents('http://ws.detectlanguage.com/0.2/detect?key=4a34be079e10fe1aa3fd334e8de3434c&q='.urlencode($text));
		$language=json_decode($language);

		$language= json_encode($language->data->detections[0]->language);
		$language =trim($language, '"');
		$response = array('lang' => $language,'en' => $en , 'ru' => $ru , 'de' => $de , 'fr' => $fr , 'ar' => $ar);


		echo json_encode($response);



	} catch (Exception $e) {
  // handle exception
	}

}

?>

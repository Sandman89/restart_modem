<?php 
try		
{   
	if (empty($_GET['modem'])){
		echo "modem is empty";
		exit;
	}
	if (!empty($_GET['modem'])){
		if (empty($_GET['port'])){
			echo "port is empty";
			exit;	
		}
		else{
			$command = "python -W ignore /var/www/html/script_zte.py --ip ".$_GET['modem']." --port ".$_GET['port']." 2>&1"; 
			$pid = popen( $command,"r"); 
			while(!feof( $pid )) {
				echo fread($pid, 256); 
				flush(); 
				ob_flush(); 
				usleep(100000);
			}
			pclose($pid); 
		}
	}
}
catch (Exception $e)
{
	echo $e->getMessage();
}

?>
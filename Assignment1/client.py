import http.client,sys
ip = sys.argv[1]
port = sys.argv[2]
xCord = sys.argv[3]
yCord = sys.argv[4]
print("Sending fire command to " + ip + ":" + port + "with x coordinate" + xCord +" and y coordinate" + yCord)
h1 = http.client.HTTPConnection('localhost',9000)
h1.request('POST','/?x='+xCord+'&y='+yCord)
response = h1.getresponse()
print("Status: " + str(response.status))
print(response.headers)

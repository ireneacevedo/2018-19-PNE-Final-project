import http.server
import socketserver
import json
import requests
import http.client

from Seq import Seq

PORT = 8000

ensemblport = 80

SERVER = 'https://rest.ensembl.org'
headers = ({ "Content-Type" : "text/json"})
ENDPOINT = ["/info/species?","/overlap/region/human/{}:{}-{}?feature=gene;feature=transcript;feature=cds;feature=exon", '/info/assembly']

socketserver.TCPServer.allow_reuse_address = True

class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print("GET received")

        print("Request line:" + self.requestline)
        print("  Cmd: " + self.command)
        print("  Path: " + self.path)


        contents = ""
        try:
            if self.path == '/':
                with open('index.html', 'r') as f:
                    for i in f:
                        contents += i
                        contents = str(contents)
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
            else:
                end = self.path.split('?')[0]
                print("End =>", end)
                    if end == '/listSpecies':
                            contents = self.attend_info_species()
                            self.send_response(200)
                            self.send_header('Content-Type', 'text/html')
                    elif end == '/karyotype':
                        contents = self.handle_info_assembly()
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html')


                    elif self.path == '/overlap/region/human/{}:{}-{}?feature=gene;feature=transcript;feature=cds;feature=exon':
                        contents = self.handle_overlap_region()
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/plain')
                    else:
                        with open('error.html', 'r') as f:
                            for i in f:
                                contents += i
                                contents = str(contents)
                        self.send_response(404)
                        self.send_header('Content-Type', 'text/html')
        except Exception:
            self.send_response(404)
            with open('hugeerror.html', 'r') as f:
                contents = f.read()


        self.send_header("Content-Length", len(str.encode(str(contents))))
        self.end_headers()

        self.wfile.write(str.encode(contents))

        return



    def attend_info_species(self):
        r = requests.get(SERVER + ENDPOINT[0], headers = headers)
        print("Sending request:", request)
        data = r.json()
        print("CONTENT: ")
        print(data)


        limit = len(data['species'])

        print(data)

        contents = '<!DOCTYPE html><html lang="en"<head><meta charset="UTF-8"><title>Main</title></head><body><h1>Main page</h1>'
        for index in range(limit):
            contents += '<li>'
            contents += data['species'][index]['common name']
            contents += '</li>'
        contents += '</ol><body><html>'


        return contents
    def handle_info_assembly(self):

        r = requests.get(SERVER + ENDPOINT[2], headers=headers)
        data = r.json()
#http://rest.ensembl.org/info/assembly/homo_sapiens?
        specie = self.path.split("=")[1]
        specie = specie.replace("+", "_")
        #print("Specie=", specie)
        request = SERVER + ENDPOINT[2] + "/" + specie
        print ("Sending request:", request)

        r = requests.get(request, headers=headers)
        data = r.json()
        print("CONTENT: ")
        print(data)

        contents = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Karyotype of ' + specie + '</title></head>' \
                   '<body><h1>Karyotype of ' + specie + '</h1><ol>'

        for index, elem in enumerate(d['karyotype']):
            contents += "<li>"
            contents += elem #d['karyotype'][index]['common_name']
            contents += "</li>"

        contents += "</ol></body></html>"

        return contents

        return data


def handle_overlap_region(self):
    print("\nConnecting to server: {}:{}\n".format(SERVER, EPORT))

    # Connect with the server
    con = http.client.HTTPConnection(SERVER, EPORT)

    # Send the request message
    con.request("GET", "/overlap/region/human/{}:{}-{}?feature=gene;feature=transcript;feature=cds;feature=exon")

    # Read the response message from server
    r1 = con.getresponse()

    # Print the status line
    print("Response received: {} {}\n".format(r1.status, r1.reason))

    # Read the response's body
    data = r1.read().decode("utf-8")
    print("CONTENT: ")
    print(data)
    return data





Handler = TestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at PORT", PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Stop')
httpd.server_close()


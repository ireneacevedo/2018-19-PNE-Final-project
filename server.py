
import http.server
import socketserver
import json
import requests
import http.client


PORT = 8000


SERVER = 'https://rest.ensembl.org'
headers = ({ "Content-Type" : "application/json"})
ENDPOINT = ['/info/species?' , '/info/assembly']

ensemblport = 80

TEST = False

socketserver.TCPServer.allow_reuse_address = True

class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print("GET received")

        print("Request line:" + self.requestline)
        print("  Cmd: " + self.command)
        print("  Path: " + self.path)

        write_test('-----New request----------')
        write_test("Request line:" + self.requestline)
        write_test("  Cmd: " + self.command)
        write_test("  Path: " + self.path)

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
                write_test('Endpoint'+ end)
                print("End =>", end)
                if end == '/listSpecies':
                    contents = self.attend_info_species()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')

                elif end == '/karyotype':
                    write_test('Endpoint' + end)
                    contents = self.handle_info_assembly()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')

                elif end == '/chromosomeLength':
                    write_test('Endpoint' + end)
                    contents = self.handle_chromosome_length()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                else:
                    with open('error.html', 'r') as f:
                        for i in f:
                            contents += i
                            contents = str(contents)
                    self.send_response(404)
                    self.send_header('Content-Type', 'text/html')
        except Exception:
            self.send_response(404)
            with open('error.html', 'r') as f:
                for i in f:
                    contents += i
                    contents = str(contents)
            self.send_response(404)
            self.send_header('Content-Type', 'text/html')


        self.send_header("Content-Length", len(str.encode(str(contents))))
        self.end_headers()

        self.wfile.write(str.encode(contents))

        return

    def attend_info_species(self):
        request = SERVER + ENDPOINT[0]
        r = requests.get(request, headers=headers)
        print("Sending request:", request)
        write_test("request: " + request)
        data = r.json()
        write_test("Response: " + str(data))

        contents = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Species List</title></head>' \
                   '<body style="background-color: white;"><h1>List of species</h1><ol>'
        l = self.path.split('=')[1]

        if l == '':
            for index in range(len(data['species'])):
                contents += "<li>"
                contents += data['species'][index]['common_name']
                contents += "</li>"

            contents += "</ol></body></html>"
        else:
            for index in range(len(data['species'][:int(l)])):
                contents += "<li>"
                contents += data['species'][index]['common_name']
                contents += "</li>"

            contents += "</ol></body></html>"




        return contents

    def handle_info_assembly(self):
        specie = self.path.split("=")[1]
        specie = specie.replace("+", "_")

        request = SERVER + ENDPOINT[1] + "/" + specie
        print("Sending request:", request)

        write_test('Request' + request)

        r = requests.get(request, headers = headers)
        data = r.json()
        print("CONTENT: ")
        print(data)

        write_test('Parameters')
        write_test('Specie:' + str(specie))
        write_test('Response:' + str(data))

        #http://rest.ensembl.org/info/assembly/homo_sapiens?


        contents = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Karyotype of ' + specie + '</title></head>' \
                   '<body><h1>Karyotype of ' + specie + '</h1><ol>'

        for index, elem in enumerate(data['karyotype']):
            contents += "<li>"
            contents += elem #d['karyotype'][index]['common_name']
            contents += "</li>"

        contents += "</ol></body></html>"

        return contents


    def handle_chromosome_length(self):

        #http://localhost:8000/chromosomeLength?specie=cat&chromo=11

        a = self.path.split('?')[1]
        b = a.split('&')
        specie = b[0].split('=')[1]
        chromo = b[1].split('=')[1]

        specie = specie.replace("+", "_")

        print('specie = ', specie)
        print('chromo =', chromo)

        request = SERVER + ENDPOINT[1] + "/" + specie
        print("Sending request:", request)

        write_test('Request' + request)

        r = requests.get(request, headers=headers)
        data = r.json()
        print("CONTENT: ")
        print(data)

        write_test('Parameters')
        write_test('Specie:' + str(specie))
        write_test('Chromo' + str(chromo))
        write_test('Response' + str(data))


        lenchromo = ''
        for i in data['top_level_region']:
            if i['coord_system'] == 'chromosome' and i['name'] == chromo:
                if i['name'] == chromo:
                    lenchromo = i['length']
        if lenchromo == '':
            contents = '<!DOCTYPE html><html lang="en" dir="ltr"><head>' \
                       '<meta charset="UTF-8">' \
                       '<title>ERROR</title>' \
                       '</head>' \
                       '<body style="background-color: red">' \
                       '<h1>ERROR el nombre "' + chromo + '" no es válido.</h1>' \
                        '<p>Here there are the websites available: </p>' \
                        '<a href="/">[main server]</a></body></html>'
        else:
            contents = '<!DOCTYPE html> \
                                            <html lang="en"> \
                                            <head> \
                                                <meta charset="UTF-8"> \
                                                <title>LENGTH OF THE SELECTED CHROMOSOME</title> \
                                            </head> \
                                            <body style="background-color: lightblue;"> \
                                            <body> \
                                               The length of the chromosome is ' + str(lenchromo) + '. \
                                            </body> \
                                            </html>'
        return contents




#test
def write_test(cadena):
    if TEST == True:
        f = open('test_report.txt','a')
        f.write(cadena + '\n')
        f.close()

Handler = TestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at PORT", PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Stop')
httpd.server_close()





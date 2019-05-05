
import http.server
import socketserver
import requests
import http.client


PORT = 8000

SERVER = 'https://rest.ensembl.org'

headers = ({ "Content-Type" : "application/json"})

ENDPOINT = ['/info/species?' , '/info/assembly']

ensemblport = 80

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
                if end == '/listSpecies':
                    contents = self.attend_info_species()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')

                elif end == '/karyotype':
                    contents = self.handle_info_assembly()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')

                elif end == '/chromosomeLength':
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
        data = r.json()

        contents = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Species List</title></head>' \
                   '<body style="background-color: lime;"><h1>Species list:</h1><ol>'

        try:
            l = self.path.split('=')[1].split('&')[0]
        except IndexError:
            l = 199

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
        r = requests.get(request, headers = headers)
        data = r.json()

        contents = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Karyotype of ' + specie + '</title></head>' \
                   '<body style="background-color: aquamarine;"><h1>Karyotype of ' + specie + '</h1><ol>'

        for index, elem in enumerate(data['karyotype']):
            contents += "<li>"
            contents += elem
            contents += "</li>"

        contents += "</ol></body></html>"

        return contents


    def handle_chromosome_length(self):

        a = self.path.split('?')[1]
        b = a.split('&')
        specie = b[0].split('=')[1]
        chromo = b[1].split('=')[1]
        specie = specie.replace("+", "_")

        request = SERVER + ENDPOINT[1] + "/" + specie
        print("Sending request:", request)
        r = requests.get(request, headers=headers)
        data = r.json()

        lenchromo = ''
        for i in data['top_level_region']:
            if i['coord_system'] == 'chromosome' and i['name'] == chromo:
                if i['name'] == chromo:
                    lenchromo = i['length']
        if lenchromo == '':
            contents = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Error page</title></head>' \
                        '<body style="background-color: red;"><h1>ERROR</h1>' \
                        '<li> The name ' + chromo + ' is not valid or in the list.</li>' \
                        '<li> Main page to try again: <li>' \
                        '<a href = "http://localhost:8000">Link to the main page.</a></body></html>'
        else:
            contents = '<!DOCTYPE html><html lang="en" dir="ltr"><head>'  \
                       '<meta charset="UTF-8">' \
                       '<title>Chromosome length</title>' \
                       '<head>' \
                        '<body style="background-color: yellow;">'\
                       '<h1>Chromosome length</h1>'\
                        '<body> The length of the chromosome is ' + str(lenchromo) + '.' \
                        '</body></html>'
        return contents


Handler = TestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at PORT", PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Stop')
httpd.server_close()





import tkinter
class URL:
    def __init__(self,url):
        if "://" in url:
            self.scheme, url = url.split("://",1)
            assert self.scheme in ['http','https']
        if '/' not in url:
            url+='/'
        self.hostname, url = url.split("/",1) # setting the hostname
        self.path="/"+url
        if self.scheme=='https':
            self.port=443
        elif self.scheme=='http':
            self.port=80
        if ':' in self.hostname:
            self.hostname, port = self.hostname.split(":",1)
            self.port=int(port)
        print(f"scheme: {self.scheme}")
        print(f"hostname: {self.hostname}")
        print(f"port: {self.port}")
        print(f"path: {self.path}")
    def request(self): # does everything from establishing a socket connection, creating the request, sending it, processing the request and finally returns the contents
        # importing the libraries
        import socket
        import ssl
        
        # initialising the socket
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )
        
        # establishing the connection
        s.connect((self.hostname, self.port))
        
        # wrapping the socket around in a context in case of https
        if self.scheme=='https':
            ctx=ssl.create_default_context()
            s=ctx.wrap_socket(s, server_hostname=self.hostname)
        
        # now it's time to send the request
        request=f'GET {self.path} HTTP/1.0\r\n' # \r\n is just HTTP's way of a new line
        request+=f'Host: {self.hostname}\r\n' # passing the headers
        request+="\r\n" # an empty line so that HTTP knows that our request has finished
        s.send(request.encode('utf8')) # and request sent

        # now we need to parse the response
        response = s.makefile("r",encoding='utf8',newline='\r\n')
        # further, we need to divide the response into statusline, headers and content
        # getting the statusline
        statusline=response.readline() # the first line is the statusline (eg: HTTP/1.0 200 OK)
        version,status,explanation=statusline.split(" ",2)
        # getting the headers
        response_headers={} # will store the headers in a dictionary
        while True:
            line=response.readline()
            if line=="\r\n":
                break
            header, value = line.split(":",1)
            response_headers[header.casefold()]=value.strip()
        assert "transfer_encoding" not in response_headers
        assert "content_encoding" not in response_headers
        # getting the content
        content=response.read()

        # now that we have the content, we'll return it and close the connection
        s.close()
        return version,status,explanation,content

# def lex(content): # displays everything except the intags, ie, everything plaintext
#     text=''
#     in_tag=False
#     for char in content:
#         if char=='<':
#             in_tag=True
#         elif char==">":
#             in_tag=False
#         elif not in_tag:
#             text+=char
#     return text

# def load(self,url): # it loads the url, ie, gets the response and displays it
#     version,status,explanation,content=url.request()
#     print(version, status, explanation)
#     self.display(content)

WIDTH=1200
HEIGHT=800
SCROLL_STEP=100
H_STEP=8
V_STEP=18
class Browser:
    def __init__(self):
        self.window=tkinter.Tk() # creating the window
        self.canvas=tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT) # creating a canvas to draw stuff
        self.canvas.pack()
        self.display_layout=[]
        self.scroll=0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
    def layout(self,content):
        x=H_STEP
        y=V_STEP
        for char in content:
            if x>WIDTH-H_STEP:
                x=H_STEP
                y+=V_STEP
                self.display_layout.append((x,y,char))
            else:
                self.display_layout.append((x,y,char))
                x+=H_STEP
    def draw(self):
        # logic for drawing the characters
        self.canvas.delete("all")
        for x,y,char in self.display_layout:
            if y<self.scroll: continue
            elif y>self.scroll+HEIGHT: continue
            else: self.canvas.create_text(x,y-self.scroll,text=char)
    def load(self,url):
        version,status,explanation,content=url.request()
        self.layout(content)
        self.draw()
    def scrolldown(self,e):
        self.scroll+=SCROLL_STEP
        self.draw()
    def scrollup(self,e):
        self.scroll-=SCROLL_STEP
        self.draw()

    

if __name__=='__main__':
    import sys
    url=URL(sys.argv[1])
    # url.load(url)
    browser=Browser()
    browser.load(url)
    tkinter.mainloop()
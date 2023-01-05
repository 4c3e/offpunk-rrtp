import time
import RNS
import os
import urllib


class RRTPResponseObject:
    response: bytes
    status: str
    type: str
    meta: str
    body: bytes
    ok: bool

    def __init__(self):
        self.response = None
        self.status = ""
        self.type = ""
        self.meta = ""
        self.body = None
        self.ok = False


def parse_url(url):
    if "://" not in url:
        url = "rrtp://" + url
    t_url = url.replace("rrtp://", "http://")
    parsed = urllib.parse.urlparse(t_url)
    path = parsed.path
    if path == "":
        path = "/"
    return parsed.netloc, path


def request_failed(request_receipt):
    RNS.log("The request " + RNS.prettyhexrep(request_receipt.request_id) + " failed.")


def link_closed(link):
    if link.teardown_reason == RNS.Link.TIMEOUT:
        RNS.log("The link timed out, exiting now")
    elif link.teardown_reason == RNS.Link.DESTINATION_CLOSED:
        RNS.log("The link was closed by the server, exiting now")
    else:
        RNS.log("Link closed, exiting now")

    RNS.Reticulum.exit_handler()
    time.sleep(1.5)
    os._exit(0)


class RRTPRequest:
    def link_established(self, link):
        self.link = link
        RNS.log("Link established with server")

    def handle_response(self, request_receipt):
        raw_response = request_receipt.response
        self.responded = True
        self.response = RIPResponseObject()
        header = raw_response[0]
        header = header.split(" ", maxsplit=2)
        self.response.status = header[0]
        self.response.type = header[1]
        if len(header) > 2:
            self.response.meta = header[2]

        if raw_response[1]:
            self.response.body = raw_response[1]

        self.response.ok = True

    def blocking_request(self, path, data=None):
        self.responded = False
        self.response = None
        self.status = ""
        self.type = ""
        self.meta = ""
        self.ok = False
        try:
            RNS.log("Sending request to " + path)
            self.link.request(
                path,
                data=data,
                response_callback=self.handle_response,
                failed_callback=request_failed,
                timeout=5,
            )

        except Exception as e:
            RNS.log("Error while sending request over the link: " + str(e))
            self.curr_connected_dest = None
            self.link.teardown()

        while not self.responded:
            time.sleep(0.1)

        return

    def req(self, url, data=None):
        destination_hexhash, path = parse_url(url)

        try:
            if len(destination_hexhash) != 20:
                raise ValueError("Destination length is invalid, must be 20 hexadecimal characters (10 bytes)")
            destination_hash = bytes.fromhex(destination_hexhash)

        except:
            RNS.log("Invalid destination entered. Check your input!\n")
            exit()

        if not RNS.Transport.has_path(destination_hash):
            RNS.log("Destination is not yet known. Requesting path and waiting for announce to arrive...")
            RNS.Transport.request_path(destination_hash)
            while not RNS.Transport.has_path(destination_hash):
                time.sleep(0.1)

        if self.curr_connected_dest == destination_hash and self.link:
            self.blocking_request(path, data)
            return self.response

        server_identity = RNS.Identity.recall(destination_hash)

        RNS.log("Establishing link with server...")

        self.destination = RNS.Destination(
            server_identity,
            RNS.Destination.OUT,
            RNS.Destination.SINGLE,
            "rrtp",
            "server"
        )

        t_link = RNS.Link(self.destination)

        t_link.set_link_established_callback(self.link_established)
        t_link.set_link_closed_callback(self.destination)

        while not self.link:
            time.sleep(0.1)

        self.curr_connected_dest = destination_hash

        self.blocking_request(path, data)
        return self.response

    def get(self, url, params=None):
        return self.req(url)

    def post(self, url, data, params=None):
        return self.req(url, data)

    def __init__(self, identity=None):
        r = RNS.Reticulum()
        self.identity = None
        self.destination = None
        self.link = None
        self.curr_connected_dest = None
        self.responded = False
        # raw response
        self.response = None
        # response status code
        self.status = ""
        # mime type of response
        self.type = ""
        # value of meta field
        self.meta = ""
        # response body
        self.body = None
        # response health
        self.ok = False

        if identity:
            self.identity = identity
        else:
            self.identity = RNS.Identity()


if __name__ == "__main__":
    request = RRTPRequest()

class RunConfig(object):
    def __init__(self, api_key=None, api_secret=None, host_used=None,type = 0):
        # type: (str, str, str) -> None
        self.api_key = api_key
        self.api_secret = api_secret
        self.host_used = host_used
        if type == 0:
            self.use_test = "https://api-testnet.gateapi.io"
        else:
            self.use_test = "https://api.gateio.ws"
import json

class bencode_parser:
    def parse(self, src):
        self.src = src
        self.p = 0
        if len(self.src) > 0:
            return self._boss()

    def isok(self):
        return self.p == len(self.src)

    def _boss(self):
        if self.src[self.p] == 'i':
            self.p += 1
            return self._helper_int()
        elif self.src[self.p].isdigit():
            return self._helper_str()
        elif self.src[self.p] == 'l':
            self.p += 1
            return self._helper_list()
        elif self.src[self.p] == 'd':
            self.p += 1
            return self._helper_dict()

    def _helper_int(self):
        pp = self.src.find('e', self.p)
        val = int(self.src[self.p: pp])
        self.p = pp + 1
        return val

    def _helper_str(self):
        pp = self.src.find(':', self.p)
        l = int(self.src[self.p: pp])
        self.p = pp + 1 + l
        s = self.src[pp + 1: self.p]
        return s

    def _helper_list(self):
        lst = []
        while self.p < len(self.src) and self.src[self.p] != 'e':
            lst.append(self._boss())
        self.p += 1
        return lst

    def _helper_dict(self):
        d = {}
        while self.p < len(self.src) and self.src[self.p] != 'e':
            k = self._helper_str()
            v = self._boss()
            d[k] = v
        self.p += 1
        return d


def test():
    ps = bencode_parser()
    testdb = [
            ('i-42e', -42),
            ('4:spam', 'spam'),
            ('l4:spami42ee', ['spam', 42]),
            ('d3:bar4:spam3:fooi42ee', {'bar': 'spam', 'foo': 42}),
            ('lli555e6:123456deee', [[555, '123456', {}]]),
            ]
    for t in testdb:
        print 'testing ' + t[0]
        parsed = ps.parse(t[0])
        if json.dumps(parsed) != json.dumps(t[1]) or not ps.isok():
            print 'Test failed: your res {} != {}, when src = {}'.format(parsed, t[1], t[0])
            break
    else:
        print 'All test passed'

#test()

ps = bencode_parser()
res = ps.parse(open('123.torrent', 'r').read())
print res['info']['files']
print ps.isok()

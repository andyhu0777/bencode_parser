import json
import md5
import os


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



class bencode_unparser:
    def unparse(self, parsed):
        return self._boss(parsed)

    def _boss(self, parsed):
        if type(parsed) == int:
            return 'i{}e'.format(str(parsed))
        elif type(parsed) == str:
            return '{}:{}'.format(len(parsed), parsed)
        elif type(parsed) == list:
            s = 'l'
            for item in parsed:
                s += self._boss(item)
            s += 'e'
            return s
        elif type(parsed) == dict:
            s = 'd'
            for k, v in parsed.items():
                s += self._boss(k)
                s += self._boss(v)
            s += 'e'
            return s


def test():
    ps = bencode_parser()
    ups = bencode_unparser()
    testdb = [
            ('i-42e', -42),
            ('4:spam', 'spam'),
            ('l4:spami42ee', ['spam', 42]),
            ('d3:bar4:spam3:fooi42ee', {'bar': 'spam', 'foo': 42}),
            ('lli555e6:123456deee', [[555, '123456', {}]]),
            ]
    for t in testdb:
        print 'testing ' + json.dumps(t[0]), json.dumps(t[1])
        parsed = ps.parse(t[0])
        unparsed = ups.unparse(t[1])
        if json.dumps(parsed) != json.dumps(t[1]) or not ps.isok():
            print 'Test Parser failed: your result {} != {}'.format(parsed, t[1])
            break
        if json.dumps(unparsed) != json.dumps(t[0]):
            print 'Test Unparser failed: your result {} != {}'.format(unparsed, t[0])
            break
    else:
        print 'All test passed'

def test2():
    ps = bencode_parser()
    res = ps.parse(open('123.torrent', 'r').read())
    print res['info']['files']
    print ps.isok()


def xizhongzi(parsed):
    parsed['info']['name'] = md5.md5(parsed['info']['name']).hexdigest()
    for file in parsed['info']['files']:
        for key in file:
            if key == 'path' or key == 'path.utf-8':
                for i in range(len(file[key])):
                    left, right = os.path.splitext(file[key][i])
                    file[key][i] = md5.md5(left).hexdigest() + right
    return parsed

ps = bencode_parser()
ups = bencode_unparser()
parsed_clean = xizhongzi(ps.parse(open('123.torrent', 'r').read()))
print parsed_clean['info']['name']
print parsed_clean['info']['files']
open(parsed_clean['info']['name'] + '.torrent', 'w').write(ups.unparse(parsed_clean))

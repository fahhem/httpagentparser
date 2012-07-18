"""
Extract client information from http user agent
The module does not try to detect all capabilities of browser in current form (it can easily be extended though).
Aim is
    * fast
    * very easy to extend
    * reliable enough for practical purposes
    * and assist python web apps to detect clients.
"""
from collections import defaultdict

import sys

class DetectorBase(object):
    def __init__(self):
        self.name = "" # "to perform match in DetectorsHub object"
        self.info_type = "override me"
        self.result_key = "override me"
        self.order = 10 # 0 is highest
        self.look_for = "string to look for"
        self.skip_if_found = [""]
        self.skip_if_found = [] # strings if present stop processin
        self.prefs = {'':['']}
        self.prefs = {} # dict(info_type = [name1, name2], ..)
        self.version_splitters = ["/", " "]
        self._suggested_detectors = None

    def detect(self, agent, result):
        # -> True/None
        if self.checkWords(agent):
            #result[self.info_type] = defaultdict(str)
            result[self.info_type]['name'] = self.name
            version = self.getVersion(agent)
            if version:
                result[self.info_type]['version'] = version
            return True

    def checkWords(self, agent):
        # -> True/None
        for w in self.skip_if_found:
            if w in agent:
                return False
        if self.look_for in agent:
            return True

    def getVersion(self, agent):
        # -> version string /None
        return agent.split(self.look_for + self.version_splitters[0])[-1].split(self.version_splitters[1])[0].strip()


class OS(DetectorBase):
    def __init__(self):
        DetectorBase.__init__(self)
        self.name = "OS"
        self.info_type = "os"
        self.version_splitters = [";", " "]


class Dist(DetectorBase):
    def __init__(self):
        DetectorBase.__init__(self)
        self.name = "Dist"
        self.info_type = "dist"


class Flavor(DetectorBase):
    def __init__(self):
        DetectorBase.__init__(self)
        self.name = "Flavor"
        self.info_type = "flavor"


class Browser(DetectorBase):
    def __init__(self):
        DetectorBase.__init__(self)
        self.name = "Browser"
        self.info_type = "browser"


class Firefox(Browser):
    def __init__(self):
        Browser.__init__(self)
        self.name = "Firefox"
        self.look_for = "Firefox"


class Konqueror(Browser):
    def __init__(self):
        Browser.__init__(self)
        self.name = "Konquerer"
        self.look_for = "Konqueror"
        self.version_splitters = ["/", ";"]

class OperaMobile(Browser):
    def __init__(self):
        Browser.__init__(self)
        self.look_for = "Opera Mobi"
        self.name = "Opera Mobile"
    def getVersion(self, agent):
        try:
            look_for = "Version"
            return agent.split(look_for)[1][1:].split(' ')[0]
        except:
            look_for = "Opera"
            return agent.split(look_for)[1][1:].split(' ')[0]

class Opera(Browser):
    def __init__(self):
        Browser.__init__(self)
        self.name = "OS"
        self.look_for = "Opera"
    def getVersion(self, agent):
        try:
            look_for = "Version"
            return agent.split(look_for)[1][1:].split(' ')[0]
        except:
            look_for = "Opera"
            return agent.split(look_for)[1][1:].split(' ')[0]

class Netscape(Browser):
    def __init__(self):
        Browser.__init__(self)
        self.name = "OS"
        self.look_for = "Netscape"

class MSIE(Browser):
    def __init__(self):
        Browser.__init__(self)
        self.look_for = "MSIE"
        self.skip_if_found = ["Opera"]
        self.name = "Microsoft Internet Explorer"
        self.version_splitters = [" ", ";"]


class Galeon(Browser):
    def __init__(self):
        Browser.__init__(self)
        self.name = "Galeon"
        self.look_for = "Galeon"

class WOSBrowser(Browser):
    def __init__(self):
        Browser.__init__(self)
        self.name = "WOSBrowser"
        self.look_for = "wOSBrowser"

    def getVersion(self, agent):
        return ''

class Safari(Browser):
    def __init__(self):
        Browser.__init__(self)
        self.name = "Safari"
        self.look_for = "Safari"

    def checkWords(self, agent):
        unless_list = ["Chrome", "OmniWeb", "wOSBrowser"]
        if self.look_for in agent:
            for word in unless_list:
                if word in agent:
                    return False
            return True

    def getVersion(self, agent):
        if "Version/" in agent:
            return agent.split('Version/')[-1].split(' ')[0].strip()
        else:
            return agent.split('Safari ')[-1].split(' ')[0].strip() # Mobile Safari


class Linux(OS):
    def __init__(self):
        OS.__init__(self)
        self.name = "Linux"
        self.look_for = 'Linux'
        self.prefs = {'browser':["Firefox"], 'dist':["Ubuntu", "Android"], 'flavor':None}

    def getVersion(self, agent):
        return ''

class Blackberry(OS):
    def __init__(self):
        OS.__init__(self)
        self.name = "Blackberry"
        self.look_for = 'BlackBerry'
        self.prefs = {'dist':["BlackberryPlaybook"], 'flavor':None}
    def getVersion(self, agent):
        return ''

class BlackberryPlaybook(Dist):
    def __init__(self):
        Dist.__init__(self)
        self.name = "BlackberryPlaybook"
        self.look_for = 'PlayBook'
    def getVersion(self, agent):
        return ''

class Macintosh(OS):
    def __init__(self):
        OS.__init__(self)
        self.name = "Macintosh"
        self.look_for = 'Macintosh'
        self.prefs = {'dist':None, 'flavor':['MacOS']}

    def getVersion(self, agent):
        return ''


class MacOS(Flavor):
    def __init__(self):
        Flavor.__init__(self)
        self.name = "MacOS"
        self.look_for = 'Mac OS'
        self.prefs = {'browser':['Firefox', 'Opera', "Microsoft Internet Explorer"]}

    def getVersion(self, agent):
        version_end_chars = [';', ')']
        part = agent.split('Mac OS')[-1].strip()
        for c in version_end_chars:
            if c in part:
                version = part.split(c)[0]
                return version.replace('_', '.')
        return ''


class Windows(OS):
    def __init__(self):
        OS.__init__(self)
        self.name = "Windows"
        self.look_for = 'Windows'
        self.prefs = {'browser':["Microsoft Internet Explorer", 'Firefox'], 'dict':None, 'flavor':None}
        self.win_versions = {

            "NT 6.1": "7",
            "NT 6.0": "Vista",
            "NT 5.2": "Server 2003 / XP x64",
            "NT 5.1": "XP",
            "NT 5.01": "2000 SP1",
            "NT 5.0": "2000",
            "98; Win 9x 4.90": "Me"
        }

    def getVersion(self, agent):
        v = agent.split('Windows')[-1].split(';')[0].strip()
        if ')' in v:
            v = v.split(')')[0]
        v = self.win_versions.get(v, v)
        return v


class Ubuntu(Dist):
    def __init__(self):
        Dist.__init__(self)
        self.name = "Ubuntu"
        self.look_for = 'Ubuntu'
        self.version_splitters = ["/", " "]
        self.prefs = {'browser':['Firefox']}


class Debian(Dist):
    def __init__(self):
        Dist.__init__(self)
        self.name = "Debian"
        self.look_for = 'Debian'
        self.version_splitters = ["/", " "]
        self.prefs = {'browser':['Firefox']}


class Chrome(Browser):
    def __init__(self):
        Browser.__init__(self)
        self.name = "Chrome"
        self.look_for = "Chrome"
        self.version_splitters = ["/", " "]

class ChromeiOS(Browser):
    def __init__(self):
        Browser.__init__(self)
        self.name = "ChromeiOS"
        self.look_for = "CriOS"
        self.version_splitters = ["/", " "]

class ChromeOS(OS):
    def __init__(self):
        OS.__init__(self)
        self.name = "ChromeOS"
        self.look_for = "CrOS"
        self.version_splitters = [" ", " "]
        self.prefs = {'browser':['Chrome']}
    def getVersion(self, agent):
        return agent.split(self.look_for + self.version_splitters[0])[-1].split(self.version_splitters[1])[1].strip()[:-1]

class Android(Dist):
    def __init__(self):
        Dist.__init__(self)
        self.name = "Android"
        self.look_for = 'Android'
        self.prefs = {'browser':['Safari']}

    def getVersion(self, agent):
        return agent.split(self.look_for)[-1].split(';')[0].strip()

class WebOS(Dist):
    def __init__(self):
        Dist.__init__(self)
        self.name = "WebOS"
        self.look_for = 'hpwOS'

    def getVersion(self, agent):
        return agent.split('hpwOS/')[-1].split(';')[0].strip()


class IPhone(Dist):
    def __init__(self):
        Dist.__init__(self)
        self.name = "IPhone"
        self.look_for = 'iPhone'
        self.prefs = {'browser':['Safari']}

    def getVersion(self, agent):
        version_end_chars = [';', ')']
        part = agent.split('Mac OS')[-1].strip()
        for c in version_end_chars:
            if c in part:
                version = part.split(c)[0]
                return version.replace('_', '.')
        return ''

class IPad(Dist):
    def __init__(self):
        Dist.__init__(self)
        self.name = "IPad"
        self.look_for = 'iPad'
        self.prefs = {'browser':['Safari']}

    def getVersion(self, agent):
        version_end_chars = [';', ')']
        part = agent.split('Mac OS')[-1].strip()
        for c in version_end_chars:
            if c in part:
                version = part.split(c)[0]
                return version.replace('_', '.')
        return ''

detectorshub = defaultdict(list)

detector_classes = [
    Firefox(),
    Konqueror(),
    OperaMobile(),
    Opera(),
    Netscape(),
    MSIE(),
    Galeon(),
    WOSBrowser(),
    Safari(),
    Linux(),
    Blackberry(),
    BlackberryPlaybook(),
    Macintosh(),
    MacOS(),
    Windows(),
    Ubuntu(),
    Debian(),
    Chrome(),
    ChromeiOS(),
    ChromeOS(),
    Android(),
    WebOS(),
    IPhone(),
    IPad(),
]

sort_prefs = ['']
def sort_lambda(detector):
    if detector.name in sort_prefs:
        return sort_prefs.index(detector.name)
    return sys.maxsize

class DetectorsHub(object):
    known_types = ['os', 'dist', 'flavor', 'browser']

    def __init__(self):
        for d in detector_classes:
            self.register(d)

    def register(self, detector):
        detectorshub[detector.info_type].append(detector)
        if detector.info_type not in DetectorsHub.known_types:
            DetectorsHub.known_types.insert(detector.order, detector.info_type)

    @staticmethod
    def reorderByPrefs(detectors, prefs):
        global sort_prefs
        sort_prefs = prefs

        if prefs is None:
            return []
        elif prefs == []:
            return detectors
        else:
            prefs.insert(0, '')
            return sorted(detectors, key=sort_lambda)
                #key=lambda d: prefs.index(d.name) if d.name in prefs else sys.maxsize)

DetectorsHub()


def detect(agent):
    result = defaultdict(lambda: defaultdict(str))
    _suggested_detectors = [Firefox()]
    _suggested_detectors = []
    for info_type in DetectorsHub.known_types:
        detectors = _suggested_detectors or detectorshub[info_type]
        for detector in detectors:
            if detector.detect(agent, result):
                if detector.prefs and not detector._suggested_detectors:
                    _suggested_detectors = DetectorsHub.reorderByPrefs(detectors, detector.prefs.get(info_type))
                    detector._suggested_detectors = _suggested_detectors
                    break
    return result


def simple_detect(agent):
    """
    -> (os, browser) # tuple of strings
    """
    result = detect(agent)
    os_list = []
    if 'flavor' in result: os_list.append(result['flavor']['name'])
    if 'dist' in result: os_list.append(result['dist']['name'])
    if 'os' in result: os_list.append(result['os']['name'])

    os = " ".join(os_list) if os_list else "Unknown OS"
    os_version = ""
    if os_list:
        if result.get('flavor'):
            os_version = result['flavor'].get('version')
        elif result.get('dist'):
            os_version = result['dist'].get('version')
        elif result.get('os'):
            os_version = result['os'].get('version')

    browser = result['browser'].get('name') if 'browser' in result else 'Unknown Browser'
    browser_version = result['browser'].get('version') if 'browser' in result else ""
    if browser_version:
        browser = " ".join((browser, browser_version))
    if os_version:
        os = " ".join((os, os_version))
    return os, browser

if __name__ == '__main__':
    agents = [
        "Not a real agent",
        "Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.307.11 Safari/532.9",
        "Mozilla/5.0 (Linux; U; Android 2.3.5; en-in; HTC_DesireS_S510e Build/GRJ90) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    ]
    for user_agent in agents:
        print detect(user_agent)
        print simple_detect(user_agent)


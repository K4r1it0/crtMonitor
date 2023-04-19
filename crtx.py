import schedule
import telegram
import requests
import time
import json



def bot(msg):
    text = msg
    bot_token = "Token"
    chat_id = "ID"
    bot = telepot.Bot(bot_token)
    bot.sendMessage(chat_id, 'New CERT=' + text)


class crtshAPI(object):
    """crtshAPI main handler."""

    def search(self, domain, wildcard=True, expired=True):
        """
        Search crt.sh for the given domain.

        domain -- Domain to search for
        wildcard -- Whether or not to prepend a wildcard to the domain
                    (default: True)
        expired -- Whether or not to include expired certificates
                    (default: True)

        Return a list of objects, like so:

        {
            "issuer_ca_id": 16418,
            "issuer_name": "C=US, O=Let's Encrypt, CN=Let's Encrypt Authority X3",
            "name_value": "hatch.uber.com",
            "min_cert_id": 325717795,
            "min_entry_timestamp": "2018-02-08T16:47:39.089",
            "not_before": "2018-02-08T15:47:39"
        }
        """
        base_url = "https://crt.sh/?q={}&output=json"
        if not expired:
            base_url = base_url + "&exclude=expired"
        if wildcard and "%" not in domain:
            domain = "%.{}".format(domain)
        url = base_url.format(domain)

        ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
        while True:

            req = requests.get(url, headers={'User-Agent': ua})

            if req.ok:
                try:
                    content = req.content.decode('utf-8')
                    data = json.loads(content)
                    return data
                except ValueError:
                    data = json.loads("[{}]".format(content.replace('}{', '},{')))
                    return data
                except Exception as err:
                    print("Error retrieving information.")
            else:
                print(f"Request Status is {req.status_code} trying again after 10 seconds")
                time.sleep(10)
                continue

        return None


def monitor(query):
    print("Monitor Task Started")
    for cert in crtshAPI().search(query):
        if cert['serial_number'] not in certs:
            certs.add(cert['serial_number'])
            bot(str(cert))
            print(cert)


status = "Store"
query = "Fidelity National Information Services, Inc"
certs = set()


if status == "Store":
    print("Entreing Storing Mode")
    for cert in crtshAPI().search(query):
        certs.add(cert['serial_number'])
        status = "Monitor"
        print("Exiting Storing Mode")
        schedule.every(6).hours.do(monitor,query)
        while True:
            schedule.run_pending()
            time.sleep(1)


import requests
import threading
import argparse
import os
from colorama import Fore, Style, init
import time

# Initialize colorama
init(autoreset=True)

class Rabbit:
    def __init__(self, url, wordlist, threads, method, output_file):
        self.url = url
        self.wordlist = wordlist
        self.threads = threads
        self.method = method
        self.output_file = output_file
        self.lock = threading.Lock()
        self.results = []

    def request(self, word):
        try:
            full_url = self.url.replace("FUZZ", word)
            start_time = time.time()
            if self.method.upper() == "POST":
                response = requests.post(full_url)
            else:
                response = requests.get(full_url)
            response_time = time.time() - start_time

            if response.status_code == 200:
                with self.lock:
                    print(f"{Fore.GREEN}[+] Found: {full_url} | Status: {response.status_code} | Time: {response_time:.2f}s{Style.RESET_ALL}")
                    self.results.append(f"{full_url} | Status: {response.status_code} | Time: {response_time:.2f}s")
            elif response.status_code == 404:
                pass  # Not found, ignore
            else:
                with self.lock:
                    print(f"{Fore.YELLOW}[-] {full_url} | Status: {response.status_code}{Style.RESET_ALL}")

        except requests.exceptions.RequestException as e:
            with self.lock:
                print(f"{Fore.RED}[-] Error: {e}{Style.RESET_ALL}")

    def run(self):
        with open(self.wordlist, 'r') as f:
            words = f.read().splitlines()

        threads = []
        for word in words:
            t = threading.Thread(target=self.request, args=(word,))
            threads.append(t)
            t.start()

            if len(threads) >= self.threads:
                for t in threads:
                    t.join()
                threads = []

        # Join remaining threads
        for t in threads:
            t.join()

        # Save results to a file
        with open(self.output_file, "w") as result_file:
            for result in self.results:
                result_file.write(result + "\n")
        print(f"{Fore.CYAN}[+] Results saved to {self.output_file}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description="Rabbit - Directory Brute Forcing Tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL with FUZZ placeholder")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads to use")
    parser.add_argument("-m", "--method", choices=['GET', 'POST'], default='GET', help="HTTP method to use (default: GET)")
    parser.add_argument("-o", "--output", default="results.txt", help="Output file name (default: results.txt)")
    
    args = parser.parse_args()

    if not os.path.isfile(args.wordlist):
        print(f"{Fore.RED}[-] Wordlist file does not exist.{Style.RESET_ALL}")
        return

    rabbit = Rabbit(args.url, args.wordlist, args.threads, args.method, args.output)
    rabbit.run()

if __name__ == "__main__":
    main()
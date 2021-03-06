import json
import os
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
from country import const_countries


class Human_test(Exception):

    def __init__(self, text):
        self.txt = text


class Similar:
    """ Class for working with API Similarweb. """

    def __init__(self, headless=True):
        """ Parameters needed for operation. """
        try:
            if headless:
                self.options = webdriver.ChromeOptions()
                self.options.add_argument('headless')
                self.driver = webdriver.Chrome(options=self.options)
            else:
                self.driver = webdriver.Chrome()
        except WebDriverException:
            print('chromedriver.exe needed, please put it in the script folder')
            print("If you don't have one download it from the link below")
            print('https://chromedriver.storage.googleapis.com/84.0.4147.30/chromedriver_win32.zip')
            print('or download the latest version from here https://chromedriver.chromium.org/downloads')
            input('To exit the program, click - Enter!')
            quit()

        self.file_input = 'input.txt'
        self.file_output = 'output.txt'
        self.bad_file = 'bad_links.txt'
        self.all_months = 'all_months.txt'
        self.domain = []
        self.monthly_visits = []
        self.count = 0
        self.file_domain_count = 0
        self.path = os.getcwd()

    def __create_list_of_domains(self):
        """ Creating a clean list of domains from a file. """
        try:
            with open(file=self.file_input, mode='r', encoding='utf-8') as file:
                for url in file:
                    url = url.replace('\n', '')
                    if '//' in url:
                        need_url = url.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
                        self.domain.append(need_url)
                    else:
                        need_url = url.replace('www.', '')
                        self.domain.append(need_url)
        except FileNotFoundError:
            print('Please create a file input.txt and put data there')
            input('To exit the program, click - Enter!')
            quit()

    def __create_files_to_write(self):
        with open(file=self.file_output, mode='w', encoding='utf-8') as file_out:
            file_out.write('Domain' + '\t' + 'Country' + '\t' + 'Amount of traffic' + '\t' + 'Comment' + '\n')
        with open(file=self.bad_file, mode='w', encoding='utf-8') as bad_file:
            bad_file.write('These links must be checked manually:\n')
        with open(file=self.all_months, mode='w', encoding='utf-8') as all_months:
            all_months.write('Domain' + '\t' + 'Date' + '\t' + 'Amount of traffic' + '\n')

    def __write_to_file(self, file_name, str_to_write):
        with open(file=file_name, mode='a', encoding='utf-8') as file:
            file.write(str_to_write)

    def __count_of_links(self):
        """ Counting the number of domains in a file. """
        with open(self.file_input, 'r', encoding='utf-8') as file:
            for _ in file:
                self.file_domain_count += 1

    def __rounding(self, number_to_round):
        """ Rounding traffic by type similarweb. """
        number = str(number_to_round)
        if len(number) >= 7:
            h = number[:3] + '.' + number[3:]
            j = round(float(h))
            g = str(j) + '0' * (len(number) - 3)
            return g
        elif 5 <= len(number) <= 6:
            h = number[:2] + '.' + number[2:]
            j = round(float(h))
            g = str(j) + '0' * (len(number) - 2)
            return g
        elif 1 <= len(number) <= 4:
            h = number[:1] + '.' + number[1:]
            j = round(float(h))
            g = str(j) + '0' * (len(number) - 1)
            return g

    def __preparing_data(self, soup):
        """ Preparing data for further use. """
        if 'HTTP ERROR 429' in str(soup) or '<html><head></head><body></body></html>' in str(soup):
            print('---> Banned. We need to wait!')
            time.sleep(61)
            self.count -= 1
        elif '{}' in str(soup):
            need_write = 'https://www.similarweb.com/website/' + str(self.domain[self.count - 1]) + '\n'
            self.__write_to_file(file_name=self.bad_file, str_to_write=need_write)
        elif 'invalid payload' in str(soup):
            print('---> This is not a domain! Check - ' + str(self.domain[self.count - 1]))
        elif 'Please verify you are a human' in str(soup):
            raise Human_test('---> Please verify you are a human! - ')

        else:
            find_json = soup.find('pre').text
            _json = json.loads(find_json)
            monthly_visits_top5 = _json['EstimatedMonthlyVisits']
            top_country = _json['TopCountryShares']
            site_name = _json['SiteName']

            if self.domain[self.count - 1] == site_name:
                for date in monthly_visits_top5:
                    self.monthly_visits.append(monthly_visits_top5[date])
                    need_write = str(site_name) + '\t' + str(date) + '\t' + str(self.__rounding(monthly_visits_top5[date])) + '\n'
                    self.__write_to_file(file_name=self.all_months, str_to_write=need_write)

                need_write_ = str(site_name) + '\t' + 'Total Traffic' + '\t' + str(self.__rounding(self.monthly_visits[-1]) + '\t' + 'Total Traffic' + '\n')
                self.__write_to_file(file_name=self.file_output, str_to_write=need_write_)

                number_top_list = 1
                for country in top_country:
                    country_name = const_countries[str(country['Country'])]
                    top5_traffic = self.__rounding(round(self.monthly_visits[-1] * country['Value']))
                    _need_write = str(site_name) + '\t' + str(country_name) + '\t' + str(top5_traffic) + '\t' + 'TOP-' + str(number_top_list) + '\n'
                    self.__write_to_file(file_name=self.file_output, str_to_write=_need_write)
                    number_top_list += 1
            else:
                need_write = 'https://www.similarweb.com/website/' + str(self.domain[self.count - 1]) + '\n'
                self.__write_to_file(file_name=self.bad_file, str_to_write=need_write)

    def run(self):
        """ Main function. """
        self.__create_files_to_write()
        self.__create_list_of_domains()
        self.__count_of_links()
        while True:
            if self.count == len(self.domain):
                self.driver.quit()
                break
            self.count += 1
            print('---> Passed domains: ' + str(self.count) + ' from ' + str(self.file_domain_count) +
                             ' domain - ' + str(self.domain[self.count - 1]))
            self.driver.get(f'https://data.similarweb.com/api/v1/data?domain={self.domain[self.count - 1]}')
            source = self.driver.page_source
            soup = BeautifulSoup(source, 'html.parser')
            self.__preparing_data(soup=soup)


if __name__ == '__main__':
    start_time = time.time()
    similar = Similar(headless=False)  # if False - the browser will be visible, if True - will not be
    print('---> Starting data collection')
    similar.run()
    finish_time = time.time()
    print('---> Done!\n')
    print('---> See the positive result in the file - output.txt')
    print('---> For raw links, see the file - bad_links.txt')
    print('---> Traffic for all months see the file - all_months.txt')
    print(f'---> Time spent on data collection - {round(finish_time - start_time, 2)} second')
    input('---> To exit the program, click - Enter!')

import os
import statistics
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv


def fetch_vacancy_hh(language):
    url_hh = 'https://api.hh.ru/vacancies'
    moscow_region_id = 1
    params = {
        'text': f"Программист {language}",
        'area': moscow_region_id,
        'only_with_salary': 'true',
        'currency': 'RUR'
    }
    response_hh = requests.get(url_hh, params=params)
    response_json_hh = response_hh.json()
    pages_hh = response_json_hh['pages']

    for page in range(1, pages_hh):
        params['page'] = page
        vacancies_response = requests.get(url_hh, params=params)
        vacancies_json = vacancies_response.json()
        for vacancy in vacancies_json['items']:
            response_json_hh['items'].append(vacancy)

    return response_json_hh


def fetch_vacancy_sj(language):
    url_sj = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': os.getenv('key')}
    work_sector_development_and_programming_id = 48
    results_per_page = 100
    params = {
        'keyword': f"Программист {language}",
        'town': 'Москва',
        'currency': 'rub',
        'count': results_per_page,
        'catalogues': work_sector_development_and_programming_id}
    response_sj = requests.get(url_sj, headers=headers, params=params)
    response_json_sj = response_sj.json()
    return response_json_sj


def result_for_hh(response_json_hh):
    all_salaries_hh = []

    for vacancy in response_json_hh['items']:
        all_salaries_hh.append(predict_salary(vacancy['salary']['from'], vacancy['salary']['to']))

    results_hh = response_json_hh['found'], len(all_salaries_hh), int(statistics.mean(all_salaries_hh))
    return results_hh


def result_for_sj(response_json_sj):
    all_salaries_sj = []

    if response_json_sj['total'] == 0:
        results_sj = response_json_sj['total'], len(all_salaries_sj), 'unknown'
    else:
        for vacancy in response_json_sj['objects']:
            if vacancy['payment'] is None:
                continue
            else:
                all_salaries_sj.append(predict_salary(vacancy['payment_from'], vacancy['payment_to']))

        results_sj = response_json_sj['total'], len(all_salaries_sj), int(statistics.mean(all_salaries_sj))

    return results_sj


def predict_salary(salary_from, salary_to):
    if salary_from is None or salary_from == 0:
        predict_salary = salary_to * 0.8
    elif salary_to is None or salary_to == 0:
        predict_salary = salary_from * 1.2
    elif (salary_from is not None and salary_to is not None) or (salary_from != 0 and salary_to != 0):
        predict_salary = int((salary_from + salary_to) / 2)

    return predict_salary


def main():
    load_dotenv()
    languages_list = ['C', 'JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'Go', 'Objective-C', 'TypeScript', '1С', 'Scala', 'Swift']
    table_data_hh = table_data_sj = (('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'), )

    for language in languages_list:
        salary_hh = result_for_hh(fetch_vacancy_hh(language))
        print(f"{language} vacancies from HH loaded")

        salary_sj = result_for_sj(fetch_vacancy_sj(language))
        print(f"{language} vacancies from SJ loaded")

        table_data_hh = table_data_hh + ((language,) + salary_hh,)
        table_data_sj = table_data_sj + ((language,) + salary_sj,)

    table_header_hh = 'HeadHunter'
    table_header_sj = 'SuperJob'
    table_hh = AsciiTable(table_data_hh, table_header_hh)
    table_sj = AsciiTable(table_data_sj, table_header_sj)

    print(table_hh.table)
    print(table_sj.table)


if __name__ == '__main__':
    main()

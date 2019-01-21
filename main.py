import os
import statistics
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv


def fetch_vacancy_hh(language):
    url_hh = 'https://api.hh.ru/vacancies'
    params = {'text': f"Программист {language}", 'area': 1, 'period': 30, 'only_with_salary': 'true', 'currency': 'RUR'}
    response_hh = requests.get(url_hh, params=params)
    response_json_hh = response_hh.json()
    pages_hh = response_json_hh['pages']

    for page in range(1, pages_hh):
        params['page'] = page
        vacancies_response = requests.get(url_hh, params=params)
        print(f"{language} page {page} loaded")
        vacancies_json = vacancies_response.json()
        for vacancy in vacancies_json['items']:
            response_json_hh['items'].append(vacancy)

    return response_json_hh


def fetch_vacancy_sj(language):
    url_sj = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': os.getenv('key')}
    params = {'keyword': f"Программист {language}", 'town': 4, 'currency': 'rub', 'count': 100, 'catalogues': 48}
    response_sj = requests.get(url_sj, headers=headers, params=params)
    response_sj_json = response_sj.json()
    return response_sj_json


def predict_rub_salary_for_hh(response_json_hh):
    all_salaries_hh = []

    for vacancy in response_json_hh['items']:
        if vacancy['salary']['from'] is None:
            all_salaries_hh.append(vacancy['salary']['to'] * 0.8)
        elif vacancy['salary']['to'] is None:
            all_salaries_hh.append((vacancy['salary']['from'] * 1.2))
        elif vacancy['salary']['from'] is not None and vacancy['salary']['to'] is not None:
            all_salaries_hh.append(int(vacancy['salary']['from'] + (vacancy['salary']['to']) / 2))

    results_hh = response_json_hh['found'], len(all_salaries_hh), int(statistics.mean(all_salaries_hh))
    return results_hh


def predict_rub_salary_for_sj(response_sj_json):
    all_salaries_sj = []

    if response_sj_json['total'] == 0:
        results_sj = response_sj_json['total'], len(all_salaries_sj), 'unknown'
        pass
    else:
        for vacancy in response_sj_json['objects']:
            if vacancy['payment'] is None:
                continue
            elif vacancy['payment_from'] == 0:
                all_salaries_sj.append(vacancy['payment_to'] * 0.8)
            elif vacancy['payment_to'] == 0:
                all_salaries_sj.append((vacancy['payment_from'] * 1.2))
            elif vacancy['payment_from'] != 0 and vacancy['payment_to'] != 0:
                all_salaries_sj.append(int((vacancy['payment_from'] + vacancy['payment_to']) / 2))
        results_sj = response_sj_json['total'], len(all_salaries_sj), int(statistics.mean(all_salaries_sj))

    return results_sj


def main():
    load_dotenv()
    languages_list = ['C', 'JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'Go', 'Objective-C', 'TypeScript', '1С', 'Scala', 'Swift']
    table_data_hh = table_data_sj = (('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'), )

    for language in languages_list:
        salary_hh = predict_rub_salary_for_hh(fetch_vacancy_hh(language))
        salary_sj = predict_rub_salary_for_sj(fetch_vacancy_sj(language))
        table_data_hh = table_data_hh + ((language, salary_hh[0], salary_hh[1], salary_hh[2]), )
        table_data_sj = table_data_sj + ((language, salary_sj[0], salary_sj[1], salary_sj[2]), )

    table_header_hh = 'HeadHunter'
    table_header_sj = 'SuperJob'
    table_hh = AsciiTable(table_data_hh, table_header_hh)
    table_sj = AsciiTable(table_data_sj, table_header_sj)

    print(table_hh.table)
    print(table_sj.table)


if __name__ == '__main__':
    main()

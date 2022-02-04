#-*- coding: utf-8 -*-
import requests as re #Библиотека необходимая для подключения к сайту
from bs4 import BeautifulSoup as bs #Библиотека необходимая для парсинга
from xlsxwriter import Workbook  #Библиотека для записи результатов в excel-файл
#lxml библиотека для работы с lxml (прирост производительности в сравнении с html-аналогом на 30%, из личного опыт)
wb = Workbook('Результаты парсинга.xlsx') #Создание рабочей книги для записи результатов

#Функция для внесения записей в лист 'Общая информация'
def pars_info():
    #Создание хедеров листа
    ws_info = wb.add_worksheet('Общая информация')
    ws_info.write(0, 0, 'Заголовок сайта')
    ws_info.write(0, 1, 'Ссылка на первоисточник цитат')
    ws_info.write(2, 1, 'CMS Сайта')
    ws_info.write(0, 2, 'Топ теги')
    #Подключение к сайту
    URL = 'https://quotes.toscrape.com/'
    session = re.session()
    request = session.get(URL)
    #Проверка на подключение
    if request.status_code == 200:
        #Загрузка контента сайта
        soup = bs(request.content, 'lxml')
        #Выгрузка заголовка сайта
        title_body = soup.find('title').get_text()
        ws_info.write(1, 0, title_body)
        #Выгрузка сайта-источника с цитатами
        source_quotes_body = soup.find('p', attrs={'class': 'text-muted'})
        source_quotes_body_link = source_quotes_body.a['href']
        ws_info.write(1, 1, source_quotes_body_link)

        #Выгрузка CMS-сайта
        source_cms_body = soup.find('p', attrs={'class': 'copyright'})
        source_cms_body_link = source_cms_body.a['href']
        ws_info.write(3, 1, source_cms_body_link)

        #Выгрузка самых популярных тегов на сайте
        top_teg_body = soup.find_all('span', attrs={'tag-item'})
        top_teg = []
        for teg in top_teg_body:
            top_teg_body_all = teg.a.text
            top_teg.append(top_teg_body_all)
        for i in range(len(top_teg)):
            temp = top_teg[i]
            ws_info.write(i + 1, 2, temp)

#Функция для внесения записей в лист 'Цитаты'
def pars_quotes():
    #Создание пустых массивов (Цитаты, автор, тэг), которые затем будут заполнены
    quotes = []
    authors = []
    tags = []
    #Указание кол-ва страиц парсинг. При желани можно спарсить с мэппинга сайта, но в данном случае я задал вручную.
    num_of_page = 10
    #Создание хедеров
    ws_quotes = wb.add_worksheet('Цитаты')
    ws_quotes.write(0, 0, 'Цитата')
    ws_quotes.write(0, 1, 'Автор')
    ws_quotes.write(0, 2, 'Тэги')
    #Проходим циклом по всем страницам
    for i in range(num_of_page):
        URL = 'https://quotes.toscrape.com/page/' + str(i + 1)
        session = re.session()
        request = session.get(URL)

        if request.status_code == 200:
            #Парсим на всех страницах цитаты, их авторов и закрепленные за ними тэги.
            soup = bs(request.content, 'lxml')
            quotes_text_body = soup.find_all('span', attrs={'class':'text'})
            quotes_author_body = soup.find_all('small', attrs={'class': 'author'})
            quotes_tags_body = soup.find_all('div', attrs={'class': 'tags'})
            #Заполняем пустые массивы спаршенной информацией
            for text in quotes_text_body:
                quotes_all = text.text
                quotes.append(quotes_all)
            for author in quotes_author_body:
                author_all = author.text
                authors.append(author_all)
            for tag in quotes_tags_body:
                tags_all = tag.text
                tags.append(tags_all)
    #Заполняем excel-лист полученной информацией
    for i in range(len(quotes)):
        temp = quotes[i]
        ws_quotes.write(i + 1, 0, temp)
    for i in range(len(authors)):
        temp = authors[i]
        ws_quotes.write(i + 1, 1, temp)
    for i in range(len(tags)):
        temp = tags[i]
        temp_str = str(temp)
        temp_split = temp_str.split('\n')[3:]
        temp_str_split = str(temp_split)
        ws_quotes.write(i + 1, 2, temp_str_split)
    return authors

#Функция для внесения записей в лист 'Биографии авторов'
def pars_authors(authors):
    # Создание пустых массивов (Автор, дата рождения, город, биография), которые затем будут заполнены
    Name = []
    Date = []
    City = []
    Description = []
    #Отдельно создадим пустой массив, в который положим только уникальные значения
    Unique_Authors = []
    #Создание листов
    ws_authors = wb.add_worksheet('Биографии авторов')
    ws_authors.write(0, 0, 'Автор')
    ws_authors.write(0, 1, 'Год рождения')
    ws_authors.write(0, 2, 'Место рождения')
    ws_authors.write(0, 3, 'Биография')
    #Проверка уникальности
    set_authors = set(authors)
    #Заполнения массива с уникальными именами
    for i in set_authors:
        Unique_Authors.append(i)
    #Преобразование имён в элемент ссылки
    Unique_Authors_str = str(Unique_Authors)
    Unique_Authors_str_replace_1 = Unique_Authors_str.replace('.','-')
    Unique_Authors_str_replace_2 = Unique_Authors_str_replace_1.replace(' ','-')
    Unique_Authors_str_replace_3 = Unique_Authors_str_replace_2.replace('--','-')
    Unique_Authors_str_replace_4 = Unique_Authors_str_replace_3.replace(',-', ',')
    Unique_Authors_str_replace_5 = Unique_Authors_str_replace_4.replace("-'", "'")
    Unique_Authors_str_replace_6 = Unique_Authors_str_replace_5.replace("'", "")
    Unique_Authors_str_replace_7 = Unique_Authors_str_replace_6.replace('"','')
    Unique_Authors_str_replace_8 = Unique_Authors_str_replace_7.replace('é','e')
    Unique_Authors = Unique_Authors_str_replace_8[1:-1].split(',')
    #Проходим циклом по всем авторам
    for i in Unique_Authors:
        URL = 'https://quotes.toscrape.com/author/' + str(i)
        session = re.session()
        request = session.get(URL)
        if request.status_code == 200:
            soup = bs(request.content, 'lxml')
        #Парсим все имена авторов, их дату рождения, место рождения и биографию
            #Записываем эту информацию в excel-лист
            author_name = soup.find_all('h3', attrs={'class':'author-title'})
            for name in author_name:
                name_all = name.text
                Name.append(name_all)
            for i in range(len(Name)):
                temp = Name[i]
                ws_authors.write(i + 1, 0, temp)
            author_date = soup.find_all('span', attrs={'class':'author-born-date'})
            for date in author_date:
                date_all = date.text
                Date.append(date_all)
            for i in range(len(Date)):
                temp = Date[i]
                ws_authors.write(i + 1, 1, temp)
            author_city = soup.find_all('span', attrs={'class':'author-born-location'})
            for city in author_city:
                city_all = city.text
                City.append(city_all)
            for i in range(len(City)):
                temp = City[i]
                ws_authors.write(i + 1, 2, temp)
            author_desc = soup.find_all('div', attrs={'class':'author-description'})
            for desc in author_desc:
                disc_all = desc.text
                Description.append(disc_all)
            for i in range(len(Description)):
                temp = Description[i]
                ws_authors.write(i + 1, 3, temp)



pars_info()
authors = pars_quotes()
pars_authors(authors)
wb.close()
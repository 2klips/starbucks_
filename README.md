# **Streamlit을 사용한 starbucks 매장 및 메뉴 정보 웹사이트 ( 크롤링 )**

<br>

<div align="center">
  
![image](https://github.com/user-attachments/assets/1f835a12-3808-4548-8df1-78b58e1e99f3)

</div>

<br>

## **스타벅스 매장 위치 및 메뉴 크롤링**

Selenium과 BeatifulSoup를 사용하여 스타벅스 홈페이지 크롤링


### **매장 위치 크롤링 함수**

```
def starbucks_sejung_stores(region_xpath):
    driver = webdriver.Chrome()
    url = 'https://www.starbucks.co.kr:7643/store/store_map.do?disp=locale'

    driver.get(url)
    time.sleep(3)

    driver.find_element('xpath', region_xpath).click()
    time.sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    stores = soup.select('li.quickResultLstCon')
    data = []

    for store in stores:
        name = store.select('strong')[0].text
        lat = store['data-lat']
        lng = store['data-long']
        address = str(store.select('p.result_details')[0]).split('<br/>')[0].split('>')[1]
        tel = str(store.select('p.result_details')[0]).split('<br/>')[1].split('<')[0]

        data.append([name, lat, lng, address, tel])

    columns = ['매장명', '위도', '경도', '주소', '전화번호']
    df = pd.DataFrame(data, columns=columns)
    
    driver.quit()
    
    return df
```

스타벅스 홈페이지의 경우, [ 매장찾기 ] 메뉴에서 지역을 선택하여 출력하기에,
해당 지역에 대한 Xpath만 있을 경우, 간단하게 크롤링이 가능

크롤링을 통해, ['매장명', '위도', '경도', '주소', '전화번호'] 정보를 가져온 후, 
MongoDB에 저장
시각화를 위해 Pandas DataFrame으로 변환


### **메뉴 크롤링**

```
url = "https://www.starbucks.co.kr/menu/drink_list.do"

browser = webdriver.Chrome()
browser.get(url)

browser.implicitly_wait(5)
html = browser.page_source
bs = BeautifulSoup(html, 'html.parser')

# 메뉴 정보를 찾아서 이미지 URL과 음료 이름을 리스트에 저장
drinks_data = []
drinks_wrapper = bs.findAll("li", {"class": re.compile("menuDataSet")})
for row in drinks_wrapper:
    img_tag = row.find("img")
    img_url = img_tag['src']
    title = img_tag['alt']
    # drinks_data.append({'title': title, 'img_url': img_url})

    a_tag = row.find("a")
    a_prod = a_tag['prod']

    drinks_data.append({'title': title, 'img_url': img_url, 'a_prod': a_prod})

df = pd.DataFrame(drinks_data)
print(df)

browser.quit()
```

[ 메뉴 ] 페이지에서, 메뉴에 대한 정보들을 크롤링 

---

이후 가져온 정보들을 MongoDB를 사용해 저장한 후,
Streamlit을 사용하여 제작한 간단한 웹페이지를 통해 매장 지도 및 메뉴목록 구현


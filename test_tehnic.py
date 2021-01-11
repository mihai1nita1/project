from selenium import webdriver
from selenium.webdriver import ActionChains
import re
import time
import requests
import json

web = webdriver.Chrome("D:\\chrome\\Chromedriver.exe")
actions = ActionChains(web)

#1. Navigate to https://www.deindeal.ch/fr/
web.get('https://www.deindeal.ch/fr/')

#2. Select the FOOD DELIVERY channel from the channels list
web.find_element_by_xpath('//*[@id="channel-navigation"]/dl/dd[3]/a').click()

#3.  Assert that the url ends with "restaurant/"
url = web.current_url
print(url)
    
if re.findall("restaurant/$", url):
    print('Page ends with restaurant/')
else:
    print('Page doesn\'t end with restaurant/')

#4. Click on a food city and save its id from the URL (eg: restaurant/geneve => "geneve")
page_loaded = True
web.find_element_by_xpath('//*[@id="__next"]/div[2]/div/div[2]/ul/li[1]/a/img').click()

while page_loaded:
    url = web.current_url
    if (re.findall("restaurant/", url) and not(re.findall("restaurant/$", url))): #check if restaurant/ is in the link and it is not the last word

        id_restaurant = re.split("restaurant/", url)[1] #the link was splitted in a list containing two strings: before restaurant/ and  after it; using [1] we get the 2nd string
        print(id_restaurant)
        page_loaded = False
    else:
        time.sleep(1)
        page_loaded = True

#5. Assert that the button to display the restaurant is disabled
print('Button is enabled: ', web.find_element_by_xpath('//*[@id="__next"]/div[2]/div[1]/div/div/button').is_enabled())

#6 Input the following address in the search input: "Rue Emma-Kammacher 9"
text = 'Rue Emma-Kammacher 9'
element = web.find_element_by_xpath('//*[@id="__next"]/div[2]/div[1]/div/div/div/input')
element.send_keys(text)

# 7. Select the suggestion that appears
time.sleep(2)
suggestion_loaded = True
while suggestion_loaded:
    try:
        web.find_element_by_xpath('//*[@id="food-prediction-undefined"]').click()
        suggestion_loaded = False
    except:
        suggestion_loaded = True

# 8. Assert that the button to display the restaurant is enabled
button_enabled = True
while button_enabled:
    if web.find_element_by_xpath('//*[@id="__next"]/div[2]/div[1]/div/div/button').is_enabled():
        button_enabled = False
        print('Button is enabled: True')

# 9. Click on the button to display the restaurants
web.find_element_by_xpath('//*[@id="__next"]/div[2]/div[1]/div/div/button').click()

#11. Wait for the marketing pop-up to appear
pop_up = True
while pop_up:
    try:
        web.switch_to.frame('ju_iframe_335872')
        pop_up = False
        print("Pop-up appeared")
    except:
        pop_up = True

#12. Close the marketing pop-up
close_button = True

time.sleep(2)
while close_button:
    try:
        web.find_element_by_xpath('//*[@id="justuno_form"]/div/div[2]/div[7]/div/div/div/span/span/span').click()
        close_button = False
        print ('Add closed')
    except:
        close_button = True
        
web.switch_to.default_content()

#10. Push the arrows to display the food filters
web.find_element_by_xpath('//*[@id="__next"]/div[2]/div[2]/div[1]/button').click()

#13. Select a popular filter (eg on german: "Gesund")
time.sleep(2)
choice = web.find_element_by_xpath('//*[@id="__next"]/div[2]/div[2]/div[1]/div[1]/div/ul/li[5]/div/label/span')
actions.move_to_element(choice).click().perform()
print('Pressed Healthy')

#14. Assert that the filter is also selected in the list with all filters
culoare = web.find_element_by_xpath('//*[@id="__next"]/div[2]/div[2]/div[1]/div[1]/ul/li[5]/div/label/span').value_of_css_property('color')
if culoare == 'rgba(255, 177, 9, 1)': # found the rgb value for #ffb109 on google
    print('filter is also selected in the list with all filters')
else:
    print('filter is not selected in the list with all filters')

#15. Save the value of the filter by retrieving it from the URL (eg: ?sortBy=fd_healthy => "fd_healthy")
url = web.current_url
value_filter = re.split("sortBy=", url)[1] 
print('value filter: ',value_filter)

#16. Save the ids of the displayed collections from the html
elem = web.find_elements_by_class_name('ClassicSale')
lista = []
for i in elem:  #getting the code value and storring it in a list variable
    to_split = i.get_attribute('id')
    value = re.split("-", to_split)[2]
    lista.append(value)

for i in lista:
    print('Collection: ',i)
web.close()
print('closwing chromedriver instance')

#17. Make an API call using GET to https://testfoodios.herokuapp.com/food_city/{{food_city}} (replace "{{food_city}}" with the channel id saved in step 4.)
api = 'https://testfoodios.herokuapp.com/food_city/'
link_resp = api + id_restaurant
response = (requests.get(link_resp))
print(response)

#18. Assert that the status code is 200 and save the response
#   a. The number of collection ids saved in step 16. must match the number of items from the response
if re.findall('200',str(response)):
    status = True
else:
    status = False

print(status)

#   b. The ids of collections saved in step 16. must match with the ids of the items from the response
data = response.json() 
collections = data.get('items')

all_data = json.dumps(data)
test_16 = 0

for i in lista:
    if re.search(i,str(collections) +','):
        test_16 = test_16 + 1

if test_16 == len(lista):
    print('All collections found at 16 were present in the response')
else:
    print('We have failed 16')

#   c. The filters of each item (you can find them under "myThemes" key) must contain the food filter saved in step 15. (eg: "fd_healthy")
if re.search(value_filter,str(data)):
    print('Food filter found at 15 was present in the response')
else:
    print('We have failed 15')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
import cv2
import geopandas as gp


############################### IDEA FOR HEAT MAP PREDICTIONS ###################################

# image = cv2.imread('testimage.png', 0)
# colormap = plt.get_cmap('inferno')
# heatmap = (colormap(image) * 2**16).astype(np.uint16)[:,:,:3]
# heatmap = cv2.cvtColor(heatmap, cv2.COLOR_RGB2BGR)

# cv2.imshow('image', image)
# cv2.imshow('heatmap', heatmap)

##################################################################################################


# # Instantiate Driver and import necessary libraries for web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
url= 'https://waterwatch.usgs.gov/index.php?id=flood&sid=w__table&r=us'
driver = webdriver.Chrome()
driver.get(url)

#Get the table elements for the already flooded data
flooded_rows = driver.find_elements(By.XPATH, "//tr")

#List of the flood indicated USGS sites
list_flooded = []
for i in range(len(flooded_rows)):
    list_flooded.append(flooded_rows[i].text)

df = pd.DataFrame(list1[5:])

# df

df = pd.DataFrame(pd.read_csv('pa01d_oh.txt'))
print(df)

import re
import requests
from bs4 import BeautifulSoup

def snow_report():
  r = requests.get("http://winter.kirkwood.com/site/mountain/snow-report")
  data = r.text
  soup = BeautifulSoup(data)
  
  r = requests.get(soup.find("meta")['content'].split('=')[1])
  data = r.text
  soup = BeautifulSoup(data)
  
  headline = soup.find(id="titleHeader").get_text()
  timestamp = soup.find(id="snowReport").find("h1").get_text()
  
  weather = soup.find(id="snowReport").find(attrs={"class": "srCol"}).find("h2").get_text()
  tempF = int(soup.find(id="snowReport").find(attrs={"class": "temp"}).get_text())
  windmph = int(soup.find(id="snowReport").find(attrs={"class": "wind"}).get_text())
  winddir = soup.find(id="snowReport").find(attrs={"class": "dir"}).get_text()
  
  forecast_today = soup.find(id="snowReport").find(text=re.compile("Today's Forecast")).parent.next_sibling.next_sibling.get_text()
  forecast_short_term = soup.find(id="snowReport").find(text=re.compile("Short-Term Weather Outlook")).parent.next_sibling.next_sibling.get_text()
  
  snow_base_24hr    = int(soup.find(id="snowReport").find("table").find_all("tr")[0].find_all("td")[1].get_text().split("\"")[0])
  snow_summit_24hr  = int(soup.find(id="snowReport").find("table").find_all("tr")[0].find_all("td")[2].get_text().split("\"")[0])
  snow_base_48hr    = int(soup.find(id="snowReport").find("table").find_all("tr")[1].find_all("td")[1].get_text().split("\"")[0])
  snow_summit_48hr  = int(soup.find(id="snowReport").find("table").find_all("tr")[1].find_all("td")[2].get_text().split("\"")[0])
  snow_base_storm   = int(soup.find(id="snowReport").find("table").find_all("tr")[2].find_all("td")[1].get_text().split("\"")[0])
  snow_summit_storm = int(soup.find(id="snowReport").find("table").find_all("tr")[2].find_all("td")[2].get_text().split("\"")[0])
  snow_7day         = soup.find(id="snowReport").find("table").find_all("tr")[0].find_all("td")[4].get_text()
  snow_total        = soup.find(id="snowReport").find("table").find_all("tr")[1].find_all("td")[4].get_text()
  snow_base         = int(soup.find(id="snowReport").find("table").find_all("tr")[2].find_all("td")[2].get_text().split("\"")[0])
  
  snow_conditions   = soup.find(id="snowReport").find(text=re.compile("Surface Conditions")).parent.next_sibling.next_sibling.get_text().strip()
  
  road_conditions   = soup.find(id="snowReport").find(text=re.compile("Road Conditions")).next_sibling.get_text()
  
  roads = \
    { \
      road.find_all("td")[0].get_text().split(":")[0]:\
        road.find_all("td")[1].get_text().strip() \
      for road in soup.find(id="snowReport").find(text=re.compile("Road Conditions")).parent.next_sibling.next_sibling.find_all("tr") \
    }
  
  def text_to_status(s):
    if s == "Open": return True
    if s == "Scheduled": return True
    if s == "Closed": return False
    return s
  
  def img_to_terrain(s):
    if s['src'] == "/site/images/run_circle.png": return "green circle"
    if s['src'] == "/site/images/run_square.png": return "blue square"
    if s['src'] == "/site/images/run_diamond.png": return "black diamond"
    if s['src'] == "/site/images/run_dbl_diamond.png": return "double black diamond"
    return s['src']
  
  lifts = \
    { \
      lift.find_all("td")[0].get_text().strip(): \
        { "open": text_to_status(lift.find_all("td")[2].get_text().strip()), \
          "groomed_runs": lift.find_all("td")[3].get_text().strip(), \
          "terrain": [img_to_terrain(i) for i in lift.find_all("td")[1].find_all("img")] \
        } \
      for lift in soup.find(id="snowReport").find(text=re.compile("Lift Operations")).parent.next_sibling.next_sibling.find_all("tr")[1:] \
    }

  # XXX: parks and pipes
  # XXX: high angle grooming
  # XXX: bowls
  
  r = requests.get("http://www.snow.com/VailResorts/HttpHandlers/GenericProxy.ashx?url=http://cache.snow.com/httphandlers/genericproxy.ashx?name=SnowReportFeed")
  data = r.text
  soup = BeautifulSoup(data)
  
  lifts_total = int(soup.find("resort", description=re.compile("Kirkwood"))['totallifts'])
  lifts_open = int(soup.find("resort", description=re.compile("Kirkwood")).find("snowreport")['liftsopen'])
  # validity flag on this one is set to false ...
  #runs_open = int(soup.find("resort", description=re.compile("Kirkwood"))['runsopen'])
  acres_total = int(soup.find("resort", description=re.compile("Kirkwood"))['totalacres'])
  runs_total = int(soup.find("resort", description=re.compile("Kirkwood"))['totalruns'])
  percent_open = int(soup.find("resort", description=re.compile("Kirkwood")).find("terrainopen")['percent'])
  acres_open = int(soup.find("resort", description=re.compile("Kirkwood")).find("terrainopen")['hectares']) * 2.5

  return { \
    "time": timestamp, \
    "description": headline, \
    "weather": { "skies": weather, "temp": tempF, "wind": { "mph": windmph, "direction": winddir }, "forecast": { "today": forecast_today, "short_term": forecast_short_term } }, \
    "snow_stakes": { \
      "base": { \
        "elevation": 7840, \
        # overnight \
        "hours_24": snow_base_24hr, \
        "hours_48": snow_base_48hr, \
        "storm_total": snow_base_storm, \
        "days_7": snow_7day, \
        "conditions": snow_conditions, \
        "base": snow_base, \
        "season_total": snow_total, \
      }, \
      "summit": { \
        "elevation": 9800, \
        # overnight \
        "hours_24": snow_summit_24hr, \
        "hours_48": snow_summit_48hr, \
        "storm_total": snow_base_storm, \
        "days_7": snow_7day, \
        "conditions": snow_conditions, \
        "base": snow_base, \
        "season_total": snow_total, \
      }, \
    }, \
    "lifts": lifts, \
    "runs": {}, \
    "roads": roads, \
    "stats": { \
      "road_conditions": road_conditions, \
      "runs": { "total": runs_total }, \
      "acres": { "open": acres_open, "total": acres_total }, \
      "percent": percent_open, \
      "lifts": { "open": lifts_open, "total": lifts_total }, \
    }, \
  }

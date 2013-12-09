import re
import requests
from bs4 import BeautifulSoup

def snow_report():
  r = requests.get("http://www.northstarcalifornia.com/snowreport.asp")
  data = r.text
  soup = BeautifulSoup(data)

  content = soup.find(id="cmtContent")
  timestamp = unicode(content.find(text=re.compile("Snow report last updated")))
  
  snowtab = content.find(text=re.compile("New Snow")).parent.parent.next_sibling.next_sibling
  # midmountain 6800'
  snow_midmtn_24hr = int(snowtab.find_all("strong")[1].get_text().split("\"")[0])
  snow_midmtn_48hr = int(snowtab.find_all("strong")[2].get_text().split("\"")[0])
  snow_midmtn_7day = int(snowtab.find_all("strong")[3].get_text().split("\"")[0])
  snow_midmtn_base = int(snowtab.find_all("strong")[4].get_text().split("\"")[0])
  # summit 8610'
  snow_summit_24hr = int(snowtab.find_all("strong")[6].get_text().split("\"")[0])
  snow_summit_48hr = int(snowtab.find_all("strong")[7].get_text().split("\"")[0])
  snow_summit_7day = int(snowtab.find_all("strong")[8].get_text().split("\"")[0])
  snow_summit_base = int(snowtab.find_all("strong")[9].get_text().split("\"")[0])
  
  # Season snowfall totals can come from
  # http://www.northstarcalifornia.com/info/ski/the-mountain/snowfall.asp ,
  # but I grab it from Vail's site later.
  
  # XXX: could parse full weather page -- http://www.northstarcalifornia.com/winter/forecast.asp
  # Using Vail's stuff later helps, too.
  
  tempF_low = re.match(r"([-\d]+)", content.find(text=re.compile("Weather Forecast")).parent.parent.next_sibling.next_sibling.find_all("strong")[0].get_text()).group(0)
  tempF_high = re.match(r"([-\d]+)", content.find(text=re.compile("Weather Forecast")).parent.parent.next_sibling.next_sibling.find_all("strong")[1].get_text()).group(0)
  forecast_today = content.find(text=re.compile("Weather Forecast")).parent.parent.next_sibling.next_sibling.next_sibling.next_sibling.get_text()
  
  trails_open    = int(content.find(text=re.compile("Trails Open")).parent.find("strong").get_text().strip())
  trails_groomed = int(content.find(text=re.compile("Trails Groomed")).parent.find("strong").get_text().strip())
  lifts_open     = int(content.find(text=re.compile("Lifts Running")).parent.find("strong").get_text().strip())
  
  r = requests.get("http://www.northstarcalifornia.com/groomingreport.asp?sort=area")
  data = r.text
  soup = BeautifulSoup(data)
  
  runs  = soup.find_all("table", attrs={"class": "snowreport"})[0]
  areas = soup.find_all("table", attrs={"class": "snowreport"})[1]
  lifts = soup.find_all("table", attrs={"class": "snowreport"})[2]
  
  # Sigh.  The way they have it set up, we need more than just a
  # comprehension.  Oh, well.
  region = None
  runs = {}
  for run in soup.find_all("table", attrs={"class": "snowreport"})[0].find_all("tr"):
    tds = run.find_all("td")
    # name, difficulty, open, region
    if tds[0].has_attr('colspan') and tds[0]['colspan'] == "4":
      region = run.get_text().strip()
      continue
    if tds[0]['align'] == "center":
      continue
    
    def img_to_difficulty(s):
      if s['src'] == "/nsbase/images/green.gif": return "green circle"
      if s['src'] == "/nsbase/images/blue.gif": return "blue square"
      if s['src'] == "/nsbase/images/black.gif": return "black diamond"
      return s['src']
    
    runs[tds[0].get_text().strip()] = { \
      "difficulty": img_to_difficulty(tds[0].find("img")), \
      "open": tds[1].get_text() != "N", \
      "groomed": tds[2].get_text() != "N", \
      "snow_making": tds[3].get_text() != "N", \
      "region": region \
    }
  
  # XXX: Could parse areas -- table[1] -- but I don't care
  
  region = None
  lifts = {}
  for lift in soup.find_all("table", attrs={"class": "snowreport"})[2].find_all('tr'):
    tds = lift.find_all("td")
    # type, open
    if tds[0].has_attr('colspan') and tds[0]['colspan'] == "8":
      region = lift.get_text().strip()
      continue
    if tds[0].get_text().strip() == "LIFT":
      continue
    
    lifts[tds[0].get_text().strip()] = {
      "open": tds[2].get_text().strip() != "N",
      "type": tds[3].get_text().strip(),
      "region": region
    }

    if tds[4].get_text().strip() != "":
      lifts[tds[4].get_text().strip()] = {
        "open": tds[6].get_text().strip() != "N",
        "type": tds[7].get_text().strip(),
        "region": region
      }
  
  r = requests.get("http://www.snow.com/VailResorts/HttpHandlers/GenericProxy.ashx?url=http://cache.snow.com/httphandlers/genericproxy.ashx?name=SnowReportFeed")
  data = r.text
  soup = BeautifulSoup(data)
  
  resort = soup.find("resort", description=re.compile("Northstar"))
  
  lifts_total = int(resort['totallifts'])
  acres_total = int(resort['totalacres'])
  runs_total = int(resort['totalruns'])
  percent_open = int(resort.find("terrainopen")['percent'])
  acres_open = int(resort.find("terrainopen")['hectares'])
  snow_midmtn_total = int(resort.find("seasonsnowfall")['inches'])
  snow_midmtn_overnight = int(resort.find("sincemtnclosed")['inches'])
  snow_summit_total = int(resort.find("seasonsnowfallsummit")['inches'])  
  snow_summit_overnight = int(resort.find("sincemtnclosed12hourssummit")['inches'])
  snow_conditions = resort.find("snowreport")['snowconditions']
  tempF = int(resort.find("temperature")['fahrenheit'])
  
  # Quoth the XML:
  #
  #   <terrainopen percent="5" hectares="405" acres="164" displayPercentOpen="true" displayAcresOpen="true" displayAllOpen="true" allOpenMessage=""/>
  #
  # You have: 405 acres
  # You want: hectares
  #         * 163.89769
  #
  # You idiots.
          
  return {
    "time": timestamp,
    # no description
    "weather": { "temp": tempF, "forecast": { "temp": { "low": tempF_low, "high": tempF_high }, "today": forecast_today } },
    "snow_stakes": {
      "midmountain": {
        "elevation": 6800,
        "overnight": snow_midmtn_overnight,
        "hours_24": snow_midmtn_24hr,
        "hours_48": snow_midmtn_48hr,
        "days_7": snow_midmtn_7day,
        "base": snow_midmtn_base,
        "season_total": snow_midmtn_total,
        "conditions": snow_conditions,
      },
      "summit": {
        "elevation": 8610,
        "overnight": snow_summit_overnight,
        "hours_24": snow_summit_24hr,
        "hours_48": snow_summit_48hr,
        "days_7": snow_summit_7day,
        "base": snow_summit_base,
        "season_total": snow_summit_total,
        "conditions": snow_conditions,
      },
    },
    "lifts": lifts,
    "runs": runs,
    "stats": {
      "runs": { "open": trails_open, "groomed": trails_groomed, "total": runs_total },
      "lifts": { "open": lifts_open, "total": lifts_total },
      "acres": { "open": acres_open, "total": acres_total },
      "percent": percent_open,
    }
  }

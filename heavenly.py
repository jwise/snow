import requests
from bs4 import BeautifulSoup

def snow_report():
  r = requests.get("http://www.skiheavenly.com/the-mountain/snow-report/snow-report.aspx")
  data = r.text
  soup = BeautifulSoup(data)
  
  snow_24hr      = int(soup.find(attrs={"class": "newSnow"}).find_all("td")[0].get_text().split(" ")[0])
  snow_overnight = int(soup.find(attrs={"class": "newSnow"}).find_all("td")[1].get_text().split(" ")[0])
  snow_48hr      = int(soup.find(attrs={"class": "newSnow"}).find_all("td")[2].get_text().split(" ")[0])
  snow_7day      = int(soup.find(attrs={"class": "newSnow"}).find_all("td")[3].get_text().split(" ")[0])
  
  snow_type         =     soup.find(attrs={"class": "snowConditions"}).find_all("th")[1].get_text()
  snow_base         = int(soup.find(attrs={"class": "snowConditions"}).find_all("td")[0].get_text().split(" ")[0])
  snow_season_total = int(soup.find(attrs={"class": "snowConditions"}).find_all("td")[1].get_text().split(" ")[0])
  
  r = requests.get("http://www.skiheavenly.com/the-mountain/terrain-and-lift-status.aspx")
  data = r.text
  soup = BeautifulSoup(data)
  
  lifts_open  = int(soup.find(id="columnRight_ctl00_liLiftsOpen").find_all("span")[0].get_text())
  lifts_total = int(soup.find(id="columnRight_ctl00_liLiftsOpen").find_all("span")[1].get_text())
  
  runs_open  = int(soup.find(id="columnRight_ctl00_liRunsOpen").find_all("span")[0].get_text())
  runs_total = int(soup.find(id="columnRight_ctl00_liRunsOpen").find_all("span")[1].get_text())
  
  acres_open  = int(soup.find(id="columnRight_ctl00_liAcresOpen").find_all("span")[0].get_text())
  acres_total = int(soup.find(id="columnRight_ctl00_liAcresOpen").find_all("span")[1].get_text())
  
  percent_open = int(soup.find(id="columnRight_ctl00_liOpenPercent").find_all("span")[0].get_text().split("%")[0])
  
  # Okay, here comes the fun bit.
  regions = soup.find(id="ScheduledRuns").find_all("div", recursive=False)
  
  def text_to_status(s):
    if s == 'Yes': return True
    if s == 'No': return False
    return s
  
  runs = \
    { run.find_all("td")[1].get_text():
      { "difficulty": run.find_all("img")[0]['alt'],
        "open": text_to_status(run.find_all("img")[1]['alt']),
        "region": r.find_all("h2")[0].get_text().split(" - ")[0]
      }
      for r in regions
      for tab in r.find("tr").find_all("table")
      for run in tab.find_all("tr")[1:]
    }
  
  lifts = \
    {lift.find_all("td")[0].get_text().strip():
      { "type": lift.find_all("td")[1].get_text().strip(),
        "open": text_to_status(lift.find_all("td")[2].find("img")['alt'])
      }
      for lift in soup.find(id="Lifts").find("table").find_all("tr")[1:]
    }
  
  words = soup.find(attrs={"class": "introText"}).get_text()
  
  # From http://www.snow.com/faqdetail/Snow-Stake-Cams/Where-do-you-measure.axd:
  #   The official snow stake at Heavenly is located near Dipper Express at
  #   9,800 feet.  Two additional snow stakes are the Mott Canyon snow stake,
  #   located at 8,900 feet and the Sky Deck snow stake, located at 8,550
  #   feet.  The snow stake at Dipper Express is our official snow stake
  #   camera and the one we use to record our historical snowfall totals.
  
  return {
    "description": words,
    "snow_stakes": {
      "dipper_express": {
        "elevation": 9800,
        "overnight": snow_overnight,
        "hours_24": snow_24hr,
        "hours_48": snow_48hr,
        "days_7": snow_7day,
        "conditions": snow_type,
        "base": snow_base,
        "season_total": snow_season_total
      },
    },
    "lifts": lifts,
    "runs": runs,
    "stats": {
      "runs": {"open": runs_open, "total": runs_total},
      "acres": {"open": acres_open, "total": acres_total},
      "percent": percent_open
    }
  }

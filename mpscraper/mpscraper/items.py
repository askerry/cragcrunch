
from scrapy.item import Item, Field


class Climb(Item):
    url = Field()
    name = Field()
    description = Field()
    locationdescrip = Field()
    protection = Field()
    grade = Field()
    style = Field()
    fa = Field()
    submittedby = Field()
    length = Field()
    pitch = Field()
    area = Field()
    areaurl = Field()
    region = Field()
    avgstars = Field()
    pageviews = Field()
    submittedby = Field()
    

class Area(Item):
    url = Field()
    name = Field()
    area = Field()
    areaurl = Field()
    description = Field()
    elevation = Field()
    directions = Field()
    maplocation = Field()
    mapref = Field()
    region = Field()
    country = Field()
    pageviews = Field()

    
class SubArea(Item):
    url = Field()
    name = Field()
    description = Field()
    area = Field()
    
class Climber(Item):
    url = Field()
    name = Field()
    personal = Field()
    gender = Field()
    age = Field()
    favclimbs = Field()
    interests = Field()
    climbstyles = Field()
    selfreportgrades = Field()
    moreinfo = Field()
    trad_l = Field()
    trad_f = Field()
    sport_l = Field()
    sport_f = Field()
    ice_l = Field()
    ice_f = Field()
    boulders = Field()
    aid_l = Field()
    aid_f = Field()
    mixed_l = Field()
    mixed_f = Field()
    
class Photo(Item):
    url = Field()
    name = Field()
    poster = Field()
    climb = Field()
    area = Field()
    
class Rating(Item):
    url = Field()
    name = Field()
    climb = Field()
    climblink = Field()
    climber = Field()
    
class Stars(Rating):
    starsscore = Field()
    
class Comments(Rating):
    comment= Field()
    date = Field()

class Grades(Rating):
    grade = Field()

class Ticks(Rating):
    note = Field()
    date = Field()
    
class ToDos(Rating):
    pass

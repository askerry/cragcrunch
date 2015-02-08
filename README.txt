#CragCrunch
###Insight Data Science Project
As a rock climber, I love traveling to new climbing areas around the United States and abroad. But a given climbing area or national park often contains hundreds or thousands of individual rock routes, and I can only tackle a handful of them in a single day. I often spend hours reading descriptions of climbs in a local guide book in order to find climbs I'm likely to enjoy. CragCrunch aims to solve this problem by providing an efficient platform for discovering new rock climbing routes.

The primary goal of CragCrunch is personalization. Every climber is unique and comes to the crag with their own skills, preferences, and goals. Similarly, every climb is different (e.g. different types of holds and faces) and demands its own blend of mental and physical skills. CragCrunch aims to learn about its individual users to create a personalized system for finding climbs that are right for YOU. The key feature of this system is a recommendation engine that makes personalized suggestions based on predictions of a user-specific model. Users who have not built up an extensive climbing history can answer few questions about their climbing preferences and receive personalized recommendations right away. CragCrunch also provides a list of similar climbs on each climb page. So look up a route you love and CragCrunch will suggest other climbs to add to your tick list. The climbing community has built a rich [data source](www.MountainProject.com), and I want us to have the freedom to interact with the data to meet our individual goals and needs.

###Project Steps
- Scrape, parse, and wrangle user-entered data from [www.MountainProject.com](www.MountainProject.com)
- Rapid, iterative data exploration/visualization to assess data quality and identify necessary preprocessing steps
- Pilot/exploratory analyses to sanity check extraction and analyses, make model decisions, perform feature selection, etc.
- Use random forest classifer trained on individual users (separate data from exploratory phase) to predict each user's 4 star rating of individual climbs. Model performance validated using leave-one-out cross validation.
- User-specific models loaded online to generate rankings of candidate climbs based on user-specified constraints
- Feature space also used to construct a similarity space (cosine similarity of same feature vectors used for classification) that supports "Similar Climb" suggestions

###Tools
CragCrunch relied heavily on the following python libraries:
- [Scrapy](http://scrapy.org/) for web scraping
- [Sqlalchemy](http://www.sqlalchemy.org/) for converting scraped data classes into a set of relational database schemas (MySQL)
- [Pandas](http://pandas.pydata.org/) for data processing and transformation
- [Scipy](http://www.scipy.org/scipylib/index.html) and [Statsmodels](http://statsmodels.sourceforge.net/) for inferential statistics
- [Sci-kit learn](http://scikit-learn.org/stable/) for building models (constructing cross-validation procedures, performing feature selection, fitting model parameters, testing trained models)
- [Matplotlib](http://matplotlib.org/) and [Seaborn](http://stanford.edu/~mwaskom/software/seaborn/) for visualization
- Front-end webapp built on [Flask](flask.pocoo.org/) and [Bootstrap](getbootstrap.com/2.3.2/)



***NOTE: CragCrunch is a work in progress. Additional regions and features will be added as time allows. I welcome feature requests, bug reports, and feedback on the recommendations. Please do not circulate widely (e.g. Reddit) as I'm not ready for high traffic.***

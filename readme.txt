twitter chatter bot source: hama, donsuke, yuka_
needs:simplejson, sqlalchemy, mysql5, Tweepy(new!)

1. Install above library.
2. Modify config.json.sample for your enviroment, save config.json.
   (You need OAuth consumer token/secret)
3. Change exec_path for youe enviroment: 
     crawler/crawler.py,
	 analyzer/(quick)analyzer.py,
	 generator/(quick)generator.py
4. Set up stored procedure: mysql -u hoge -p db < analyzer/replace_malkov.sql
5. Start quick.py, analyzer/analyzer.py, and generator/generator.py.
   First tell you OAuth access. 
     You copy and paste url to browser.
     (You should login twitter for bot user).
     You allow OAuth access.
     And display numbers, enter console.

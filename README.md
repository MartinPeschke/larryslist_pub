LarrysList
==========


How to start server locally
---------------------------

Load environment and start server.

	. ~/Development/virtualenv/Larryslist/bin/activate
	cd ~/Development/projects/LarrysList/webapp
	pserver local.ini


How to deploy
-------------

Commit changes to github and call deploy script.

	cd ~/Development/projects/LarrysList/
	git commit -a
	git push
	cd deploy
	./deploy.live


How to edit documentation
-------------------------

github uses Markdown as markup language.

* [Markdown Home](http://daringfireball.net/projects/markdown/syntax)
* [github flavored markdown](https://help.github.com/articles/github-flavored-markdown)

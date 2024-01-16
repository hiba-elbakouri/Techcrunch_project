run:
	docker build -t scrapping-app .
	docker run -v ./output:/app/db -p 8087:5000 -it scrapping-app
docker build -f "Dockerfile" -t cpd:latest ./
docker run -p 5000:5000 -p 80:80/tcp -p 80:80/udp -p 430:430/tcp -d --name master cpd:latest
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' master
PAUSE
Usage with K8s:
 - with local registry:
   Start up a local resistry in a docker container:
   docker run -d -p 5000:5000 --restart=always --name registry registry:2
   
   Enable the access to the insecure local registry on all k8s nodes:
   echo '{ "insecure-registries":["<IP of local registry>:5000"] }' >> /etc/docker/daemon.json
   sudo service docker restart
 
   Push the image after building it to the registry:
   docker push <IP of local registry>:5000/<tag-of-image>
 
   Use it form k8s, e.g.:
   kubectl run test-js-nginx –image=<IP of local registry>:5000/<tag-of-image> –port=80

Issues:
 - Testing a forwarded port form the docker container the URL was not working for /hello with 'localhost', only with 127.0.0.1 

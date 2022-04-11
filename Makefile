build:
	docker build -t otus_05_img .

run:
	docker run -ti --rm --name otus_05 otus_05_img

stop:
	docker stop otus_05

rmi:
	-docker stop otus_05
	-docker rm otus_05
	-docker rmi otus_05_img

rbr:
	-docker stop otus_05
	-docker rm otus_05
	-docker rmi otus_05_img
	docker build -t otus_05_img .
	docker run -ti --rm --name otus_05 otus_05_img

save:
	docker save -o m2k_img.tar m2k_img
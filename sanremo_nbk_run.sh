echo 'Removing existing container'
docker rm -f sanremo_nbk_cnt

echo 'Spin up container'
docker build -t sanremo_nbk_img ./ -f nbk.Dockerfile 
docker run -v $(pwd)/src:/APP --name sanremo_nbk_cnt sanremo_nbk_img 

# get id of running container with image name
container_id=$(sudo docker ps | grep gpt_plugin_sample_file_sever | awk '{print $1}')
echo "container id: $container_id"
# connect bash
sudo docker exec -it $container_id bash
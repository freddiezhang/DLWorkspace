# Known issues. 

1. 'docker pull' fails with error "layers from manifest don't match image configuration". 
   Please check the docker version of the 'pull' machine, the 'push' machine, and the docker register. It seems that this is caused by incompatible docker version. [See](https://github.com/docker/distribution/issues/1439)
   
2. We are still prototyping the platform. Please report issues to the author, so that we can complete the document. 